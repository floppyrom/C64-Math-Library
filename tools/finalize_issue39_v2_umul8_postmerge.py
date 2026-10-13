#!/usr/bin/env python3
"""Metadata-only V2 UMUL8 post-merge closeout after all PR104 main checks.

No arithmetic binary rebuild/update, no issue #39 closure and no broader
unsigned multiply campaign completion. Fail on any changed resident SHA,
missing native proof, or stale public performance / checksum provenance.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
KEY="issue39_v2_umul8_directout_2026_10_13"
MERGE="b50b4fe60bc7a0640ce36473f12ddead28e07848"
PROOF="validation/review/ISSUE39_V2_UMUL8_DIRECTOUT_NATIVE.json"
DOC="docs/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_2026-10-13.md"
MARK="2026-10-13 ISSUE39 V2 UMUL8 POSTMERGE MAIN VALIDATION"
MAIN_RUNS={
 "Validate library":{"id":38397621683,"conclusion":"success"},
 "Comparable unsigned performance":{"id":38397621692,"conclusion":"success"},
 "Turbo32 integration proof":{"id":38397621687,"conclusion":"success"},
}
EXPECTED_V2="71648ececccba3186a1b186144dbace5e345a9a0967d397ec1db0655cef31c04"
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 statefile=ROOT/"RELEASE_STATUS.json"
 status=json.loads(statefile.read_text())
 meta=status[KEY]
 assert meta["status"]=="PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING"
 assert meta["native_vice_calls"]==128
 assert meta["volatile_status_differences"]==46
 assert meta["issue39_complete"] is False
 assert meta["normal_zp_growth"]==0 and meta["resident_size_growth"]==0
 assert meta["V5_changed"] is False
 assert meta["new_sha256"]==EXPECTED_V2
 for profile,expected in status["reference_prg_sha256"].items():
  path=ROOT/profile/"resident"/f"math_{profile}_game_math.prg"
  assert sha(path.read_bytes())==expected,(profile,"production binary changed")
 assert status["reference_prg_sha256"]["v2_pareto_fast"]==EXPECTED_V2
 assert status["reference_prg_sha256"]["v5_hybrid_lowzp"]=="b27e0885c7241dd7bdc3b2e25be6b2c616685cb426436a3c2b8260eff7a21ebb"
 native=ROOT/PROOF
 evidence=json.loads(native.read_text())
 assert evidence["status"]=="PASS_NATIVE_VICE_V2_UMUL8_PUBLIC_DIRECT_OUTPUT"
 assert evidence["native_calls"]==128 and evidence["paired_operands"]==64
 assert evidence["all_guaranteed_public_results_identical"] is True
 assert evidence["noncarry_status_flag_differences"]==46
 assert evidence["noncarry_flags_volatile_per_USER_MANUAL"] is True
 assert evidence["native_cycles_measured"] is False
 assert evidence["new_sha256"]==EXPECTED_V2
 assert meta["native_evidence_sha256"]==sha(native.read_bytes())
 meta.update({
  "status":"PASS_MERGED_POSTMERGE_MAIN_CI",
  "v2_umul8_substep_complete":True,
  "unsigned_multiply_family_complete":False,
  "issue39_complete":False,
  "source_pr_number":104,
  "source_pr_merge_sha":MERGE,
  "post_merge_workflow_runs":MAIN_RUNS})
 doc=ROOT/DOC
 value=doc.read_text()
 heading="13 October 2026. This is a **native-qualified source release; independent PR/main CI pending**."
 assert heading in value
 value=value.replace(heading,("13 October 2026. **Released in PR #104** (merge commit "+MERGE+
  "). Native VICE old/new public ABI passed and three post-merge main CI"
  " workflows all succeeded."))
 tail="**Pending:** independent PR and post-merge main CI."
 assert tail in value
 value=value.replace(tail,
   "**Release complete:** PR-head CI and post-merge main workflows succeeded. "
   "This validates only V2 UMUL8; the rest of unsigned multiplication and issue #39 remain open.")
 doc.write_text(value)
 for name in ("README.md","USER_MANUAL.md"):
  f=ROOT/name
  s=f.read_text()
  old="(native x64sc 128 old/new public calls PASS; independent PR/main CI pending)."
  new="(PR #104 merged; native x64sc 128 old/new calls and PR/main CI PASS)."
  assert old in s,name
  f.write_text(s.replace(old,new))
 note=(MARK+"\n"
  "- V2 UMUL8 PR #104 merged to main "+MERGE+". Post-merge Validate library"
  " #38397621683, Comparable unsigned #38397621692, Turbo32 #38397621687"
  " all SUCCESS. Exact native x64sc 128 old/new calls PASS guaranteed ABI,"
  " with 46/64 volatile N/Z/V differences disclosed. V2 public UMUL8"
  " 78.494141 -> 72.494141 cycles on 65,536 paired operands (6 saved)."
  " Source resident, ABI addresses, normal ZP, other profiles unchanged by"
  " this METADATA closeout. Issue #39 and remaining unsigned multiply"
  " campaign OPEN. "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=ROOT/name
  if MARK not in f.read_text():f.write_text(note+f.read_text())
 if isinstance(status.get("documentation"),dict):
  f=ROOT/"USER_MANUAL.md"
  status["documentation"].update(
   user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),
   user_manual_sha256=sha(f.read_bytes()))
 statefile.write_text(json.dumps(status,indent=2)+"\n")
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],
                 cwd=ROOT,check=True)
 print("ISSUE39 V2 UMUL8 PR104 MAIN GREEN; RELEASE STATUS SEALED; BINARIES UNCHANGED; ISSUE39 OPEN",flush=True)
if __name__=="__main__":main()
