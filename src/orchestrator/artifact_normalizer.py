"""Synthetic provider adapters. No upstream raw schema is assumed or implemented."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import json
from .contracts import Derivation
from .evidence_store import canonical


@dataclass(frozen=True)
class Provenance:
    origin_provider: str
    evidence_id: str
    derivation: Derivation
    limitations: tuple[str,...]


@dataclass(frozen=True)
class NormalizedArtifact:
    provenance: Provenance
    raw_blob: str
    unrepresented_fields: Mapping[str,Any]


@dataclass(frozen=True)
class FunctionArtifact(NormalizedArtifact):
    name: str
    address: str | None
    signature: str | None
    body_kind: str
    body: str


@dataclass(frozen=True)
class CallGraphArtifact(NormalizedArtifact):
    nodes: tuple
    edges: tuple
    unknown_edges: tuple


@dataclass(frozen=True)
class StringRecord:
    value: str
    encoding: str | None
    address: str | None
    derivation: str


@dataclass(frozen=True)
class StringTableArtifact(NormalizedArtifact):
    strings: tuple[StringRecord,...]


@dataclass(frozen=True)
class NetworkCaptureArtifact(NormalizedArtifact):
    requests: tuple
    responses: tuple
    protocol: str
    decoded: bool


@dataclass(frozen=True)
class SchemaField:
    name: str | None
    type: str
    confidence: float


@dataclass(frozen=True)
class SchemaArtifact(NormalizedArtifact):
    fields: tuple[SchemaField,...]


def _extras(raw, consumed, prefix=""):
    return {prefix+str(k):v for k,v in raw.items() if k not in consumed}


def _base(raw, evidence_id, derivation, extras):
    if not evidence_id:
        raise ValueError("Evidence reference required")
    return (Provenance("synthetic-fixture",evidence_id,derivation,
                       ("normalized projection; inspect raw blob and unrepresented fields",)),
            canonical(raw),extras)


def _rows(raw,key):
    value=raw[key]
    if not isinstance(value,list):
        raise ValueError(key+" must be a list")
    return value


def normalize_fixture(kind: str, raw: Mapping[str,Any], evidence_id: str,
                      derivation: Derivation) -> NormalizedArtifact:
    """Normalize the checked-in fixture dialect only, retaining the entire JSON blob."""
    # Snapshot caller data, validate JSON, preserve values before projecting.
    raw=json.loads(canonical(raw))
    if not isinstance(raw,dict):
        raise ValueError("Expected object")
    if kind=="function":
        bodies=[k for k in ("pseudocode","assembly","bytecode","ir") if k in raw]
        if not bodies:
            raise ValueError("No function body representation")
        body=bodies[0]
        extra=_extras(raw,{"symbol","address","signature",body})
        return FunctionArtifact(*_base(raw,evidence_id,derivation,extra),raw["symbol"],
                                raw.get("address"),raw.get("signature"),body,raw[body])
    if kind=="call_graph":
        return CallGraphArtifact(*_base(raw,evidence_id,derivation,_extras(raw,{"nodes","edges","unknown_edges"})),
                                 tuple(_rows(raw,"nodes")),tuple(_rows(raw,"edges")),tuple(_rows(raw,"unknown_edges")))
    if kind=="strings":
        extra=_extras(raw,{"entries"}); strings=[]
        for i,row in enumerate(_rows(raw,"entries")):
            if row["derivation"] not in {"observed","decrypted","inferred"}:
                raise ValueError("Unknown string derivation")
            strings.append(StringRecord(row["value"],row.get("encoding"),row.get("address"),row["derivation"]))
            extra.update(_extras(row,{"value","encoding","address","derivation"},f"entries/{i}/"))
        return StringTableArtifact(*_base(raw,evidence_id,derivation,extra),tuple(strings))
    if kind=="network":
        if not isinstance(raw["decoded"],bool):
            raise ValueError("decoded must be boolean")
        return NetworkCaptureArtifact(*_base(raw,evidence_id,derivation,_extras(raw,{"requests","responses","protocol","decoded"})),
                                      tuple(_rows(raw,"requests")),tuple(_rows(raw,"responses")),raw["protocol"],raw["decoded"])
    if kind=="schema":
        extra=_extras(raw,{"fields"}); fields=[]
        for i,row in enumerate(_rows(raw,"fields")):
            c=row["confidence"]
            if isinstance(c,bool) or not isinstance(c,(int,float)) or not 0<=c<=1:
                raise ValueError("Invalid field confidence")
            fields.append(SchemaField(row.get("name"),row["type"],c))
            extra.update(_extras(row,{"name","type","confidence"},f"fields/{i}/"))
        return SchemaArtifact(*_base(raw,evidence_id,derivation,extra),tuple(fields))
    raise ValueError("No reviewed normalizer for "+kind)
