"""Versioned orchestration contracts; no independent verification harness.

All providers operate at authorized boundaries. Status describes provider outcome,
not gate closure. A failed result may carry useful observed evidence. No provider
is healthy by virtue of registration. Preserve canonical upstream evidence IDs
without fabricating them; namespace external evidence separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
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
    INCOMPLETE = "INCOMPLETE"


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
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    RATE_LIMITED = "RATE_LIMITED"
    AUTH_MISSING = "AUTH_MISSING"
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
    payload: Mapping[str, object] | None = None


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
class ArtifactContract:
    artifact_type: str
    required_fields: Mapping[str, object]  # null = present and non-null; otherwise exact value


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
    input_contract: tuple[ArtifactContract, ...] = ()
    output_contract: tuple[ArtifactContract, ...] = ()


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
class ObservationScope:
    question_asked: str
    artifact_observed: str

    def __post_init__(self):
        if not all(isinstance(v,str) and v.strip() for v in (self.question_asked,self.artifact_observed)):
            raise ValueError("Observation scope requires question and artifact identity")


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
    status: ResultStatus
    observation_scope: ObservationScope | None = None  # legacy rows only; explicit scope for new scheduling

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError('Evidence timestamp must be timezone-aware')
        if not isinstance(self.status, ResultStatus) or not isinstance(self.derivation, Derivation) or not isinstance(self.failure_signature, FailureSignature):
            raise ValueError('Evidence status, derivation and signature must be enums')
        for digest in (self.input_artifact_hash, self.output_artifact_hash):
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)):
                raise ValueError('Invalid SHA-256 digest')
        if self.status is ResultStatus.PASS and (self.input_artifact_hash is None or self.output_artifact_hash is None):
            raise ValueError('PASS requires input and output hashes')
        if (self.input_artifact_hash is None or self.output_artifact_hash is None) and not self.limitations:
            raise ValueError('Missing artifact hashes require limitations')


@dataclass(frozen=True)
class GateAssessment:
    """Separate future gate receipt; only GREEN supports verified closure."""
    color: GateColor
    evidence_ids: tuple[str, ...]
    verification_method: str | None
    residual_uncertainty: tuple[str, ...]

    def acceptable_for(self, fingerprint: TargetFingerprint) -> bool:
        """Admissibility only, not execution or correctness verification."""
        if self.color is GateColor.GREEN:
            return bool(self.evidence_ids and self.verification_method in
                        {"byte_match", "oracle_harness", "behavioral_equivalence"})
        return (self.color is GateColor.YELLOW and not fingerprint.verification_feasibility
                and bool(self.evidence_ids) and bool(self.residual_uncertainty)
                and all(isinstance(x, str) and x.strip() for x in self.residual_uncertainty))


class DiscoveryKind(str, Enum):
    GITHUB_SEARCH = "github_search"
    BROWSER_RESEARCH = "browser_research"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"


@dataclass(frozen=True)
class DiscoveryQuery:
    capability: str
    language: str | None
    archetype: Archetype
    failure_signature: FailureSignature
    license_allowlist: tuple[str, ...]
    authorization_ref: str
    observable_behavior: str
    undetermined_mechanism: str
    trigger_receipts: tuple[str, ...]
    artifact_types_attempted: tuple[str, ...] = ()
    failure_signatures: tuple[str, ...] = ()

    def __post_init__(self):
        if (not isinstance(self.capability,str) or not self.capability.strip()
                or len(self.capability)>240 or re.search(r"(?i)\bclone\b|https?://|\b(?:repo|user|org):",self.capability)):
            raise ValueError("Use a bounded capability description, not an app clone, URL or repository selector")
        if self.language is not None and not re.fullmatch(r"[A-Za-z0-9+#. -]{1,40}",self.language):
            raise ValueError("Invalid language/framework qualifier")
        if self.authorization_ref not in {"synthetic-fixture","public-research"}:
            raise ValueError("Discovery authorization required")


@dataclass(frozen=True)
class MaintenanceSignal:
    last_commit_date: str | None
    open_issues_count: int | None
    archived: bool | None


@dataclass(frozen=True)
class DiscoveryCandidate:
    canonical_path: str
    capability_match: str
    license: str
    maintenance_signal: MaintenanceSignal
    stars: int | None
    verification_required: str
    derivation: Derivation
    license_risk: str
    eligible: bool
    source_quote: str = ""
    provenance_tier: int = 4


@dataclass(frozen=True)
class DiscoveryResult:
    status: ResultStatus
    failure_signature: FailureSignature
    candidates: tuple[DiscoveryCandidate, ...]
    evidence_ids: tuple[str, ...]
    derivation: Derivation
    limitations: tuple[str, ...]
    rejections: tuple[str, ...]

    def __post_init__(self):
        if self.status not in {ResultStatus.PASS,ResultStatus.FAIL,ResultStatus.TIMEOUT,ResultStatus.EMPTY}:
            raise ValueError("Invalid discovery status")
        if self.status is ResultStatus.PASS and not self.candidates:
            raise ValueError("Discovery PASS requires candidates")


class DiscoveryProvider(Protocol):
    name: str
    kind: DiscoveryKind
    def health_check(self) -> bool: ...
    def invoke(self, query: DiscoveryQuery) -> DiscoveryResult: ...


class SupervisorAction(str, Enum):
    CONTINUE="CONTINUE"
    REPAIR="REPAIR"
    DISCOVER="DISCOVER"
    VERIFY="VERIFY"
    ABSTAIN="ABSTAIN"
    ESCALATE="ESCALATE"


@dataclass(frozen=True)
class SupervisorDecision:
    action: SupervisorAction
    reason: str
    target: str
    evidence_ids: tuple[str,...]


@dataclass(frozen=True)
class AbstentionRecord:
    archetype: Archetype
    failure_signatures: tuple[str,...]
    stages_attempted: tuple[str,...]
    rungs_attempted: tuple[int,...]
    providers_attempted: tuple[Mapping[str,object],...]
    discovery_queries_issued: tuple[Mapping[str,object],...]
    construction_brief_id: str | None
    no_brief_reason: str | None
    required_to_proceed: tuple[str,...]

    def __post_init__(self):
        if bool(self.construction_brief_id)==bool(self.no_brief_reason):
            raise ValueError("Exactly one brief ID or reason required")
        if not self.required_to_proceed or not all(isinstance(x,str) and x.strip() for x in self.required_to_proceed):
            raise ValueError("Required evidence or input must be named")
