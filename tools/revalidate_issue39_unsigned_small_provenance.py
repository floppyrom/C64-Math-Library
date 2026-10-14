#!/usr/bin/env python3
"""Re-qualify archived small-width unsigned workload records after DIST8-only PRG swap.

All 53,760 calls are recomputed. Every numerical result, cycle-vector digest,
input corpus and text output field must match the frozen audit; only the
SHA256 of the entire host PRG may change. Fail closed if anything else differs.
"""
from pathlib import Path
import sys,json,csv,hashlib,subprocess
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue39_dist8_provenance import pre_dist8_bytes
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
REPORT=R/"validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json"
TABLE=R/"benchmarks/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.csv"
STATUS=R/"RELEASE_STATUS.json"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))
def main():
    before=json.loads(REPORT.read_text()); csv_before=rows(TABLE)
    st=json.loads(STATUS.read_text())
    cert=st["issue39_dist8_shared_register_swap_2026_10_14"]
    assert cert["public_diffs_only_in_DIST8_swap"] and cert["resource_memory_growth_bytes"]==0
    for p in P:
        prg=R/p/"resident"/("math_"+p+"_game_math.prg")
        assert sha(prg)==st["reference_prg_sha256"][p]==cert["new_production_prgs"][p]
        parent=pre_dist8_bytes(p,prg.read_bytes())
        assert hashlib.sha256(parent).hexdigest()==before["resident_sha256"][p]==cert["old_production_prgs"][p]
    subprocess.run([sys.executable,str(R/"tools/audit_issue39_unsigned_small_workloads.py")],cwd=R,check=True)
    after=json.loads(REPORT.read_text());csv_after=rows(TABLE)
    for key in before:
        if key!="resident_sha256":assert before[key]==after[key],("numerical proof changed",key)
    assert len(csv_before)==len(csv_after) and len(csv_before)>100
    for i,(old,new) in enumerate(zip(csv_before,csv_after)):
        assert old["resident_sha256"]==cert["old_production_prgs"][old["profile"]],(i,"old CSV provenance")
        assert new["resident_sha256"]==cert["new_production_prgs"][new["profile"]],(i,"new CSV provenance")
        assert {k:v for k,v in old.items() if k!="resident_sha256"}=={k:v for k,v in new.items() if k!="resident_sha256"},(i,"small-width metrics differ")
    assert after["total_calls"]==before["total_calls"]==53760
    if isinstance(st.get("issue39_unsigned_small_width_workloads_2026_10_11"),dict):
        st["issue39_unsigned_small_width_workloads_2026_10_11"]["data_sha256"]=sha(REPORT)
    STATUS.write_text(json.dumps(st,indent=2)+"\n")
    print("DIST8: unsigned small-width audit all 53,760 numerical calls unchanged; only resident SHA updated")
if __name__=="__main__":main()
