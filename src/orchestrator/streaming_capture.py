"""Bounded CDP IO.read fixture transport; content-addressed, no inline large bodies."""
from __future__ import annotations
import base64
import hashlib
import os
import tempfile
from dataclasses import asdict,dataclass,replace
from pathlib import Path
from .evidence_store import canonical,digest

@dataclass(frozen=True)
class CaptureReference:
    sha256:str
    size_bytes:int
    relative_path:str

def capture_stream(reader,handle:str,directory:Path,*,chunk_bytes:int=1024,max_bytes:int=16384)->CaptureReference:
    if not isinstance(handle,str) or not handle or not 1<=chunk_bytes<=max_bytes:
        raise ValueError("Invalid stream configuration")
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix=".capture-",dir=directory)
    size=0;h=hashlib.sha256()
    try:
        try:
            with os.fdopen(fd,"wb") as file:
                # Each non-EOF response must make progress, bounding calls.
                while True:
                    response=reader("IO.read",{"handle":handle,"size":chunk_bytes})
                    data=response["data"]
                    if not isinstance(data,str) or type(response.get("eof")) is not bool:
                        raise ValueError("Malformed IO.read result")
                    flag=response.get("base64Encoded",False)
                    if type(flag) is not bool:raise ValueError("Invalid base64Encoded")
                    if len(data)>4*chunk_bytes+4:raise ValueError("Oversized IO.read response")
                    chunk=base64.b64decode(data,validate=True) if flag else data.encode("utf-8")
                    if len(chunk)>chunk_bytes or size+len(chunk)>max_bytes:
                        raise ValueError("Capture budget exceeded")
                    if not chunk and not response["eof"]:raise ValueError("Empty non-EOF stream chunk")
                    size+=len(chunk);h.update(chunk);file.write(chunk)
                    if response["eof"]:break
                file.flush();os.fsync(file.fileno())
        finally:
            reader("IO.close",{"handle":handle})
        hexdigest=h.hexdigest();name=hexdigest+".blob";dest=directory/name
        if dest.exists():
            existing=hashlib.sha256()
            with dest.open("rb") as f:
                for chunk in iter(lambda:f.read(65536),b""):existing.update(chunk)
            if existing.hexdigest()!=hexdigest or dest.stat().st_size!=size:
                raise ValueError("Existing capture blob is corrupt")
        else:
            os.replace(temp,dest)
        return CaptureReference(hexdigest,size,name)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def normalize_capture_result(result,spec,reader,directory):
    """Streaming contract: provider supplies a handle and declared byte length;
    reference metadata is hashed separately from captured bytes. Large inline
    data is rejected rather than copied to the evidence ledger.
    """
    threshold=spec["threshold_bytes"];out=[]
    for artifact in result.artifacts:
        if artifact.artifact_type!="network-capture":
            out.append(artifact);continue
        if not isinstance(artifact.payload,dict):raise ValueError("Capture payload missing")
        payload=dict(artifact.payload)
        declared=payload.get("payload_size")
        if declared is not None and (type(declared) is not int or declared<0):
            raise ValueError("Invalid capture size")
        if len(canonical(payload).encode("utf-8"))>threshold:
            raise ValueError("Capture inline metadata exceeds threshold; return a stream handle")
        handle=payload.pop("stream_handle",None)
        if handle is not None:
            if reader is None or directory is None:raise ValueError("Streaming backend not configured")
            if declared is None:raise ValueError("Stream size declaration required")
            if declared>spec["max_bytes"]:raise ValueError("Declared capture exceeds budget")
            ref=capture_stream(reader,handle,directory,chunk_bytes=spec["chunk_bytes"],max_bytes=spec["max_bytes"])
            if declared!=ref.size_bytes:raise ValueError("Stream length mismatch")
            payload["payload_ref"]=asdict(ref)
            payload["payload_size"]=ref.size_bytes
            out.append(replace(artifact,reference="blob:"+ref.sha256,sha256=digest(payload),payload=payload,
                limitations=(*artifact.limitations,"Artifact SHA-256 identifies metadata; payload_ref SHA-256 identifies captured bytes")))
        else:
            if declared is not None and declared>threshold:raise ValueError("Large capture requires IO.read handle")
            if "payload_ref" in payload:raise ValueError("Unvalidated external capture reference")
            out.append(artifact)
    return replace(result,artifacts=tuple(out))
