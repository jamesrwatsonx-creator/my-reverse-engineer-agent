"""Phase 1 interface declarations only; no execution or verification logic.

All providers operate at authorized boundaries. Status describes provider outcome,
not gate closure. A failed result may carry useful observed evidence. No provider
is healthy by virtue of registration. Preserve canonical upstream evidence IDs
without fabricating them; namespace external evidence separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Mapping, Protocol, TypeAlias


class Layer(str, Enum):
    STATIC = "static"
    DYNAMIC_DISPATCH = "dynamic-dispatch"
    CROSS_BOUNDARY = "cross-boundary"
    TRANSPORT = "transport"
    PERSISTENT_STATE = "persistent-state"


class ProviderKind(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    EMULATION = "emulation"
    SYMBOLIC = "symbolic"
    CAPTURE = "capture"
    VERIFY = "verify"
    RESEARCH = "research"


class ResultStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    EMPTY = "EMPTY"
    CONTRADICTED = "CONTRADICTED"


class FailureSignature(str, Enum):
    PACKED = "PACKED"
    ENCRYPTED_STRINGS = "ENCRYPTED_STRINGS"
    DISPATCHER_LOOP = "DISPATCHER_LOOP"
    UNRESOLVED_INDIRECT = "UNRESOLVED_INDIRECT"
    PINNED = "PINNED"
    UNKNOWN_PROTOCOL = "UNKNOWN_PROTOCOL"
    HOST_UNSUPPORTED = "HOST_UNSUPPORTED"
    TIMEOUT_ADVERSARIAL = "TIMEOUT_ADVERSARIAL"
    SHADER_OPAQUE = "SHADER_OPAQUE"
    MODEL_GRAPH_UNKNOWN = "MODEL_GRAPH_UNKNOWN"
    NONE = "NONE"


class Derivation(str, Enum):
    OBSERVED = "observed"
    DERIVED = "derived"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class Archetype(str, Enum):
    NATIVE_DESKTOP = "native-desktop"
    ELECTRON = "electron"
    ANDROID_APK = "android-apk"
    WEB_SPA = "web-spa"
    CLOUD_API = "cloud-api"
    PACKED_BINARY = "packed-binary"
    FIRMWARE = "firmware"
    BROWSER_EXTENSION = "browser-extension"
    VIDEO_DRM = "video-drm"
    GAME_REALTIME = "game-realtime"
    IOS = "ios"
    DOTNET = "dotnet"
    WASM = "wasm"
    EVM = "evm"
    SQLITE = "sqlite"


class ObfuscationSignature(str, Enum):
    CONTROL_FLOW_FLATTENING = "control-flow-flattening"
    STRING_ENCRYPTION = "string-encryption"
    VM_PROTECTION = "vm-protection"
    INDIRECT_BRANCH_DENSITY_HIGH = "indirect-branch-density-high"


class TransportProtocol(str, Enum):
    HTTP_JSON = "http-json"
    GRPC = "grpc"
    QUIC = "quic"
    WEBSOCKET_BINARY = "websocket-binary"
    SSE = "sse"


class GateColor(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


SHA256: TypeAlias = str  # lowercase 64 hexadecimal characters; validated later
JSONSchema: TypeAlias = Mapping[str, object]


@dataclass(frozen=True)
class ArtifactSchema:
    """Versioned normalized type and shape; no adapter-specific payload guessing."""
    artifact_type: str
    schema_version: str
    schema: JSONSchema


@dataclass(frozen=True)
class Artifact:
    artifact_type: str
    reference: str
    sha256: SHA256
    evidence_id: str
    origin_provider: str
    derivation: Derivation
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ProviderCapabilities:
    consumes: tuple[ArtifactSchema, ...]
    emits: tuple[ArtifactSchema, ...]


@dataclass(frozen=True)
class HostRequirement:
    """Host-dependent predicate expressed as data; checked at runtime later."""
    name: str
    requirement: str


@dataclass(frozen=True)
class ProviderInput:
    stage_id: str
    artifacts: tuple[Artifact, ...]
    parameters: Mapping[str, object]
    authorization_ref: str


@dataclass(frozen=True)
class ProviderResult:
    """All fields required; NONE is a signature, not a success assertion.

    verification_method=None means unverified, even if status is PASS.
    Empty/failed results still require evidence IDs and explicit limitations.
    Normalized schemas describe the emitted artifact types, including an empty
    tuple where there is no artifact. Verification is independent of derivation.
    """
    status: ResultStatus
    failure_signature: FailureSignature
    artifacts: tuple[Artifact, ...]
    evidence_ids: tuple[str, ...]
    derivation: Derivation
    limitations: tuple[str, ...]
    normalized_artifact_schema: tuple[ArtifactSchema, ...]
    satisfies_upstream_requirement: str | None
    verification_method: str | None


class Provider(Protocol):
    name: str
    kind: ProviderKind
    capabilities: ProviderCapabilities
    host_requirements: tuple[HostRequirement, ...]

    def health_check(self) -> bool:
        """True only following a successful functional health probe."""
        ...

    def invoke(self, input: ProviderInput) -> ProviderResult:
        ...


GatePredicate: TypeAlias = Callable[[ProviderResult], bool]


@dataclass(frozen=True)
class RepairRoute:
    failure_signature: FailureSignature
    stage_ids: tuple[str, ...]  # ordered, bounded by future policy


@dataclass(frozen=True)
class Stage:
    """Preconditions require gate-verified PASS, not merely provider PASS.

    on_fail is ordered and signature-specific; NONE must not imply retry.
    A missing local gate does not waive the global verification requirement.
    """
    id: str
    layer: Layer
    preconditions: tuple[str, ...]
    providers: tuple[str, ...]
    gate: GatePredicate | None
    on_fail: tuple[RepairRoute, ...]


@dataclass(frozen=True)
class TargetFingerprint:
    """Confidence in [0,1]; choose a cheap probe when below policy threshold.

    If verification_feasibility is false, YELLOW may express named uncertainty;
    it is not a GREEN closure or permission to bypass a protected boundary.
    """
    archetype: Archetype
    format: str | None
    arch: str | None
    packer: str | None
    obfuscation_signatures: tuple[ObfuscationSignature, ...]
    transport_protocols: tuple[TransportProtocol, ...]
    platform: str | None
    confidence: float
    timeout_sensitivity: bool
    verification_feasibility: bool


@dataclass(frozen=True)
class EvidenceEntry:
    """UTC timestamp; null digest explicitly means no corresponding artifact.

    Missing hashes require stated limitations, never fabricated digest values.
    Contradictions reference evidence IDs, not mutable paths. Failed attempts
    carry a signature even when no artifact was produced.
    """
    evidence_id: str
    origin_provider: str
    derivation: Derivation
    timestamp: datetime
    input_artifact_hash: SHA256 | None
    output_artifact_hash: SHA256 | None
    limitations: tuple[str, ...]
    contradicts: tuple[str, ...]
    verification_method: str | None
    failure_signature: FailureSignature


@dataclass(frozen=True)
class GateAssessment:
    """Separate future gate receipt; only GREEN supports verified closure."""
    color: GateColor
    evidence_ids: tuple[str, ...]
    verification_method: str | None
    residual_uncertainty: tuple[str, ...]
