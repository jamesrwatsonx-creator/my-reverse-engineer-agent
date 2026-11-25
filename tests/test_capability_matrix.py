import tempfile, unittest
from pathlib import Path
from datetime import datetime, timezone
from subprocess import CompletedProcess
from src.orchestrator.capability_matrix import CapabilityMatrix, CapabilityStatus, ProbeSpec, HostSnapshot

NOW=datetime(2026,1,1,tzinfo=timezone.utc)
HOST=HostSnapshot("Linux","x86_64",None,"3.11",False,False,False)
CAT={"entries":[{"id":"fixture"}]}
SPEC={"fixture":ProbeSpec("fixture",("--version",),r"fixture [0-9]+",())}
class CapabilityTests(unittest.TestCase):
    def test_missing_failed_success_and_unverified(self):
        for path,code,out,check,expected in [
            (None,0,"fixture 1",True,CapabilityStatus.UNAVAILABLE),
            ("/fixture",1,"fixture 1",True,CapabilityStatus.UNAVAILABLE),
            ("/fixture",0,"unrelated",True,CapabilityStatus.UNAVAILABLE),
            ("/fixture",0,"fixture 1",False,CapabilityStatus.AVAILABLE_UNVERIFIED),
            ("/fixture",0,"fixture 1",True,CapabilityStatus.AVAILABLE_VERIFIED),
        ]:
            calls=[]
            def run(args):
                calls.append(args)
                return CompletedProcess(args,code,out,"")
            m=CapabilityMatrix.discover(CAT, specs=SPEC, host=HOST, which=lambda _:path, run=run, check=check, timestamp=NOW)
            self.assertEqual(m.records["fixture"].status,expected)
            self.assertEqual(m.is_available("fixture"),expected==CapabilityStatus.AVAILABLE_VERIFIED)
            if not m.is_available("fixture"): self.assertTrue(m.why_unavailable("fixture"))
            self.assertEqual(len(calls),int(bool(path) and check))
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/"snapshot.json"; m.persist(p); self.assertTrue(p.is_file())
