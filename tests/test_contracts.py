import unittest
from datetime import datetime, timezone
from dataclasses import fields, MISSING
from src.orchestrator.contracts import *

class ContractTests(unittest.TestCase):
    def test_enums(self):
        expected = {
            Layer: "static dynamic-dispatch cross-boundary transport persistent-state",
            ProviderKind: "static dynamic emulation symbolic capture verify research",
            ResultStatus: "PASS FAIL TIMEOUT EMPTY CONTRADICTED",
            FailureSignature: "PACKED ENCRYPTED_STRINGS DISPATCHER_LOOP UNRESOLVED_INDIRECT PINNED UNKNOWN_PROTOCOL HOST_UNSUPPORTED TIMEOUT_ADVERSARIAL SHADER_OPAQUE MODEL_GRAPH_UNKNOWN RATE_LIMITED AUTH_MISSING NONE",
            Derivation: "observed derived inferred unknown",
            Archetype: "native-desktop electron android-apk web-spa cloud-api packed-binary firmware browser-extension video-drm game-realtime ios dotnet wasm evm sqlite",
            ObfuscationSignature: "control-flow-flattening string-encryption vm-protection indirect-branch-density-high",
            TransportProtocol: "http-json grpc quic websocket-binary sse",
            GateColor: "GREEN YELLOW RED",
            DiscoveryKind: "github_search browser_research knowledge_retrieval",
        }
        for enum, values in expected.items():
            self.assertEqual({x.value for x in enum}, set(values.split()))
    def test_mandatory_and_construction(self):
        schema = ArtifactSchema("function", "1", {})
        artifact = Artifact("function", "fixture", "a"*64, "source-id", "fixture", Derivation.OBSERVED, ())
        capabilities = ProviderCapabilities((schema,), (schema,))
        host = HostRequirement("os", "fixture")
        inp = ProviderInput("s", (artifact,), {}, "synthetic-fixture")
        result = ProviderResult(ResultStatus.PASS, FailureSignature.NONE, (artifact,), ("source-id",), Derivation.OBSERVED, (), (schema,), None, None)
        repair = RepairRoute(FailureSignature.PACKED, ("repair",))
        stage = Stage("s", Layer.STATIC, (), ("fixture",), None, (repair,))
        fp = TargetFingerprint(Archetype.NATIVE_DESKTOP, "fixture", None, None, (), (), None, 1, False, False)
        entry = EvidenceEntry("", "fixture", Derivation.OBSERVED, datetime(2026,1,1,tzinfo=timezone.utc), "a"*64, "b"*64, (), (), None, FailureSignature.NONE, ResultStatus.PASS)
        gate = GateAssessment(GateColor.YELLOW, ("source-id",), None, ("interface: response timing",))
        for obj in (schema,artifact,capabilities,host,inp,result,repair,stage,fp,entry,gate):
            self.assertTrue(all(f.default is MISSING and f.default_factory is MISSING for f in fields(obj) if f.name not in {'payload','input_contract','output_contract','observation_scope'}))
        self.assertTrue(gate.acceptable_for(fp))
        self.assertFalse(gate.acceptable_for(TargetFingerprint(Archetype.NATIVE_DESKTOP,None,None,None,(),(),None,1,False,True)))
        with self.assertRaises(TypeError):
            ProviderResult(status=ResultStatus.FAIL, failure_signature=FailureSignature.NONE, artifacts=(), evidence_ids=(), limitations=(), normalized_artifact_schema=(), satisfies_upstream_requirement=None, verification_method=None)
    def test_evidence_hashes(self):
        args = ("", "fixture", Derivation.OBSERVED, datetime(2026,1,1,tzinfo=timezone.utc), None, None, ("no artifact",), (), None, FailureSignature.NONE)
        with self.assertRaises(ValueError):
            EvidenceEntry(*args, ResultStatus.PASS)
        self.assertIsNone(EvidenceEntry(*args, ResultStatus.FAIL).output_artifact_hash)
