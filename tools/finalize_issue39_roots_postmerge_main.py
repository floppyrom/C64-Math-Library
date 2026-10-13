#!/usr/bin/env python3
"""Metadata-only final issue39 integer-root release status after PR102 main CI.

The recorded merge + workflow checks are immutable identifiers. Verify all
published binaries and the native certificate before changing documentation.
Do not rebuild/change production arithmetic or close the larger issue #39.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
MAIN="b179436082933d4edd80bca0256c11fc09d143be"
KEY="issue39_integer_roots_source_release_2026_10_13"
DOC="docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md"
MARKER="2026-10-13 ISSUE39 INTEGER ROOTS POSTMERGE MAIN VALIDATION"

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    st_path=ROOT/"RELEASE_STATUS.json"
    state=json.loads(st_path.read_text())
    row=state[KEY]
    assert row["status"]=="PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING"
    assert row["native_vice_calls"]==768 and row["issue39_complete"] is False
    assert row["v4_PRG_unchanged"] is True
    for profile,digest in row["reference_sha256"].items():
        path=ROOT/profile/"resident"/f"math_{profile}_game_math.prg"
        assert sha(path.read_bytes())==digest,(profile,"unexpected resident drift")
    native=ROOT/row["native_vice_evidence"]
    proof=json.loads(native.read_text())
    assert proof["status"]=="PASS_NATIVE_VICE_SOURCE_INSTALLED_ROOTS"
    assert proof["native_calls"]==768
    assert set(proof["profiles"])=={"v1_balanced","v2_pareto_fast","v3_reu_512k","v5_hybrid_lowzp"}
    row.update({
      "status":"PASS_MERGED_POSTMERGE_MAIN_CI",
      "integer_roots_family_complete":True,
      "issue39_complete":False,
      "source_pr_number":102,
      "source_pr_merge_sha":MAIN,
      "post_merge_workflow_runs":{
         "Validate library":{"id":38389399637,"conclusion":"success"},
         "Comparable unsigned performance":{"id":38389399688,"conclusion":"success"},
         "Turbo32 integration proof":{"id":38389399617,"conclusion":"success"}},
      "native_vice_evidence_sha256":sha(native.read_bytes())})
    s=(ROOT/DOC).read_text()
    old="Source installed and native VICE old/new checked (768 full-resident calls); PR/main CI not yet qualified."
    new=("Released in PR #102 (main "+MAIN+"); 768 native VICE old/new calls"
         " and three independent post-merge main workflows all passed.")
    assert old in s
    s=s.replace(old,new)
    pending="**Pending:** independent PR tests and post-merge main CI."
    assert pending in s
    s=s.replace(pending,"**Release complete:** independent PR checks and post-merge main validation passed. The broader issue #39 remains open.")
    if "Worst-case caveat" not in s:
        s+="\n**Worst-case caveat:** Although exhaustive-domain mean ISQRT16 cycles fell by about 72–74%, the new correction loop can take **471 cycles** on rare inputs. Raster-critical callers should benchmark worst-case latency, not only averages.\n"
    (ROOT/DOC).write_text(s)
    old="independent PR/main CI pending"
    new="PR #102 merged; PR/main CI green"
    for name in ("README.md","USER_MANUAL.md"):
        p=ROOT/name
        t=p.read_text()
        assert old in t,name
        p.write_text(t.replace(old,new))
    note=(MARKER+"\n"
      "- Integer roots PR #102 merged; main workflows Validate library"
      " #38389399637, Comparable unsigned #38389399688 and Turbo32"
      " #38389399617 all SUCCESS on "+MAIN+". No resident arithmetic,"
      " ABI, resource, size or cycles changed by this metadata closeout."
      " Source/native checksums preserved; release status and user documentation"
      " synchronized, issue #39 still OPEN. "+DOC+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=ROOT/name
        if MARKER not in f.read_text():f.write_text(note+f.read_text())
    d=state.get("documentation")
    if isinstance(d,dict):
        p=ROOT/"USER_MANUAL.md"
        d.update(user_manual_bytes=p.stat().st_size,
           user_manual_lines=len(p.read_text().splitlines()),
           user_manual_sha256=sha(p.read_bytes()))
    st_path.write_text(json.dumps(state,indent=2)+"\n")
    for i in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],cwd=ROOT,check=True)
    print("ROOT POSTMERGE SOURCE STATUS SEALED; NO BINARIES CHANGED; ISSUE39 OPEN",flush=True)
if __name__=="__main__": main()
