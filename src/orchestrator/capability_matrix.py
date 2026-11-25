"""Conservative host capability discovery; version probes are not target analysis."""
from __future__ import annotations
import argparse
import ctypes
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable


class CapabilityStatus(str, Enum):
    UNAVAILABLE="UNAVAILABLE"
    AVAILABLE_UNVERIFIED="AVAILABLE_UNVERIFIED"
    AVAILABLE_VERIFIED="AVAILABLE_VERIFIED"


@dataclass(frozen=True)
class HostSnapshot:
    os: str
    architecture: str
    jdk_version: str | None
    python_version: str
    ptrace_seize: bool
    docker_reachable: bool
    display_present: bool


@dataclass(frozen=True)
class ProbeSpec:
    binary: str
    args: tuple[str,...]
    expected: str
    requirements: tuple[str,...]


@dataclass(frozen=True)
class CapabilityRecord:
    status: CapabilityStatus
    binary_path: str | None
    reason: str


# Explicitly reviewed, read-only command shapes. No catalog URL is executable.
# Unlisted source/SDK/hosted/reference candidates need reviewed probe specs.
DEFAULT_SPECS={
    "rea":ProbeSpec("rea",("--version",),r"\b(?:rea\s+)?v?\d+\.\d+",()),
    "ghidra":ProbeSpec("analyzeHeadless",("-help",),r"(?i)ghidra|analyzeheadless",("jdk",)),
    "playwright":ProbeSpec("playwright",("--version",),r"(?i)version\s+\d+\.\d+",()),
    "github":ProbeSpec("gh",("--version",),r"(?i)gh version \d+",()),
    "mitmproxy":ProbeSpec("mitmdump",("--version",),r"(?i)mitmproxy",()),
    "jadx":ProbeSpec("jadx",("--version",),r"\d+\.\d+\.\d+",("jdk",)),
    "apktool":ProbeSpec("apktool",("--version",),r"\d+\.\d+\.\d+",("jdk",)),
    "ilspy":ProbeSpec("ilspycmd",("--version",),r"\d+\.\d+",()),
    "tree-sitter":ProbeSpec("tree-sitter",("--version",),r"(?i)tree-sitter \d+",()),
    "semgrep":ProbeSpec("semgrep",("--version",),r"\d+\.\d+",()),
    "k6":ProbeSpec("k6",("version",),r"(?i)k6 v?\d+",()),
    "locust":ProbeSpec("locust",("--version",),r"(?i)locust",()),
    "z3":ProbeSpec("z3",("--version",),r"(?i)z3 version",()),
    "wireshark":ProbeSpec("tshark",("--version",),r"(?i)tshark",()),
    "rr":ProbeSpec("rr",("--version",),r"(?i)rr version",("linux","ptrace_seize")),
    "webcrack":ProbeSpec("webcrack",("--version",),r"\d+\.\d+",()),
    "ipsw":ProbeSpec("ipsw",("version",),r"(?i)version|ipsw",()),
    "bubblewrap":ProbeSpec("bwrap",("--version",),r"(?i)bubblewrap",("linux",)),
    "nsjail":ProbeSpec("nsjail",("--help",),r"(?i)nsjail",("linux",)),
    "firecracker":ProbeSpec("firecracker",("--version",),r"(?i)firecracker",("linux","kvm")),
    "spirv-tools":ProbeSpec("spirv-val",("--version",),r"(?i)spirv-tools",()),
    "qemu":ProbeSpec("qemu-system-x86_64",("--version",),r"(?i)qemu emulator version",("x86_64",)),
    "postgres":ProbeSpec("postgres",("--version",),r"(?i)postgres",()),
    "ollama":ProbeSpec("ollama",("--version",),r"(?i)ollama",()),
}


def run_probe(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=5, check=False)


def _output(result):
    return (result.stdout or "")+"\n"+(result.stderr or "")


def _ptrace_probe() -> bool:
    """Probe only a disposable child we create, never a real target."""
    if platform.system()!="Linux":
        return False
    child=None
    try:
        libc=ctypes.CDLL(None,use_errno=True)
        ptrace=libc.ptrace
        ptrace.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
        ptrace.restype=ctypes.c_long
        child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"],
                               stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return ptrace(0x4206,child.pid,None,None)==0  # Linux PTRACE_SEIZE
    except (OSError,AttributeError):
        return False
    finally:
        if child is not None:
            try:
                child.kill()
            except ProcessLookupError:
                pass
            child.wait(timeout=5)


def probe_host(which=shutil.which, run=run_probe) -> HostSnapshot:
    java=which("java"); jdk=None
    if java and which("javac"):
        try:
            r=run([java,"-version"])
            if r.returncode==0:
                jdk=_output(r).strip().splitlines()[0] or None
        except (OSError,subprocess.TimeoutExpired,IndexError):
            pass
    docker=which("docker"); reachable=False
    # Do not contact a remotely configured Docker endpoint during local preflight.
    if docker and not os.environ.get("DOCKER_HOST","").startswith(("tcp:","ssh:","http:","https:")):
        try:
            r=run([docker,"version","--format","{{.Server.Version}}"])
            reachable=r.returncode==0 and bool(re.search(r"\d+\.\d+",_output(r)))
        except (OSError,subprocess.TimeoutExpired):
            pass
    return HostSnapshot(platform.system(),platform.machine(),jdk,platform.python_version(),
                        _ptrace_probe(),reachable,bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
                        or platform.system() in {"Darwin","Windows"}))


def _missing(requirements,host):
    facts={"linux":host.os=="Linux","windows":host.os=="Windows","darwin":host.os=="Darwin",
           "jdk":bool(host.jdk_version),"ptrace_seize":host.ptrace_seize,
           "docker":host.docker_reachable,"display":host.display_present,
           "x86_64":host.architecture in {"x86_64","AMD64"},
           "kvm":os.access("/dev/kvm",os.R_OK|os.W_OK)}
    return [r for r in requirements if not facts.get(r,False)]


@dataclass(frozen=True)
class CapabilityMatrix:
    host: HostSnapshot
    records: dict[str,CapabilityRecord]
    timestamp: datetime

    @classmethod
    def discover(cls,catalog,*,specs=None,host=None,which=shutil.which,run=run_probe,
                 check=True,timestamp=None):
        specs=DEFAULT_SPECS if specs is None else specs
        host=probe_host(which,run) if host is None else host
        records={}
        for entry in catalog["entries"]:
            name=entry["id"]
            if name in records:
                raise ValueError("Duplicate provider ID: "+name)
            spec=specs.get(name)
            path=which(spec.binary if spec else name)
            if spec is None:
                rec=CapabilityRecord(CapabilityStatus.UNAVAILABLE,path,
                                     "No approved provider-specific CLI/host probe; catalog entry only")
            elif not path:
                rec=CapabilityRecord(CapabilityStatus.UNAVAILABLE,None,"Binary not on PATH: "+spec.binary)
            elif missing:=_missing(spec.requirements,host):
                rec=CapabilityRecord(CapabilityStatus.UNAVAILABLE,path,"Host requirements not met: "+", ".join(missing))
            elif not check:
                rec=CapabilityRecord(CapabilityStatus.AVAILABLE_UNVERIFIED,path,"Health invocation not performed")
            else:
                try:
                    result=run([path,*spec.args])
                    good=result.returncode==0 and bool(re.search(spec.expected,_output(result)))
                    rec=CapabilityRecord(CapabilityStatus.AVAILABLE_VERIFIED if good else CapabilityStatus.UNAVAILABLE,
                                         path,"Version/help shape verified; analysis compatibility untested" if good else
                                         f"Health probe failed: exit={result.returncode}; expected output shape required")
                except (OSError,subprocess.TimeoutExpired) as exc:
                    rec=CapabilityRecord(CapabilityStatus.UNAVAILABLE,path,"Health probe failed: "+type(exc).__name__)
            records[name]=rec
        return cls(host,records,timestamp or datetime.now(timezone.utc))

    def is_available(self,name):
        # Fail closed for execution: discovered but not health-checked is not usable.
        return name in self.records and self.records[name].status is CapabilityStatus.AVAILABLE_VERIFIED

    def why_unavailable(self,name):
        if self.is_available(name):
            return ""
        return self.records[name].reason if name in self.records else "Unknown provider"

    def persist(self,path):
        path=Path(path)
        snapshot={"timestamp":self.timestamp.isoformat(),"host":asdict(self.host),
                  "records":{k:asdict(v) for k,v in self.records.items()}}
        # Caller selects a new path per snapshot; retain history.
        with path.open("x",encoding="utf-8") as f:
            json.dump(snapshot,f,indent=2,sort_keys=True); f.write("\n")

    @staticmethod
    def changed_since(previous,current):
        return previous.get("host")!=current.get("host") or previous.get("records")!=current.get("records")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    matrix=CapabilityMatrix.discover(json.loads(args.catalog.read_text(encoding="utf-8")))
    matrix.persist(args.output)
    print(json.dumps({"host":asdict(matrix.host),"counts":{s.value:sum(r.status is s for r in matrix.records.values()) for s in CapabilityStatus},"records":{k:asdict(v) for k,v in matrix.records.items()}},indent=2))

if __name__=="__main__":
    main()
