#!/usr/bin/env python3
"""Native VICE A/B for a V2-only *exclusive* direct-slice multiply overlay.

CPU cycles are NOT measured natively. The patched PRG is generated only in
memory; published resident binaries and GitHub release files are untouched.
"""
from pathlib import Path
import hashlib,json,os,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_shr16_direct_slice_overlay_research import PATCH,SITES
from native_issue39_fixed_shr16_tail import run_native,sha,STRIDE,FIELDS,COUNT

PROFILE="v2_pareto_fast"
ENTRY="MATH_UMUL32_SHR16"
def patch_prg(source):
    v=bytearray(source)
    start=int.from_bytes(v[:2],"little")
    assert start==0x1000 and len(v)==49042
    def read(addr,n):
        p=addr-start+2
        assert 2<=p and p+n<=len(v)
        return bytes(v[p:p+n])
    assert read(0x586E,3)==b"\x8d\x09\xc0"
    assert read(0x58C7,3)==b"\x8d\x08\xc0"
    assert read(0xC4E3,1)==b"\x20"
    for pc,addr in SITES:
        assert read(pc,3)==bytes((0x8d,addr&255,0xC0))
    for pc,new in PATCH.items():
        p=pc-start+2
        v[p:p+len(new)]=new
    return bytes(v)
def main():
    release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    source=(ROOT/PROFILE/"resident"/("math_"+PROFILE+"_game_math.prg")).read_bytes()
    assert sha(source)==release["reference_prg_sha256"][PROFILE]
    candidate=patch_prg(source)
    assert len(candidate)==len(source)
    changed=[i for i,(a,b) in enumerate(zip(source,candidate)) if a!=b]
    assert len(changed)>5
    native=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="issue144_slice_vice_") as name:
        tmp=Path(name)
        a=run_native(PROFILE,source,ENTRY,15790,tmp,native)
        b=run_native(PROFILE,candidate,ENTRY,15791,tmp,native)
    old=a["dump"];new=b["dump"]
    assert len(old)==len(new)==STRIDE*len(FIELDS)
    # PHP captures all NZVC status flags, but the public ABI only
    # requires carry clear; the adapter legitimately changes NZV.
    for j in list(range(6))+list(range(8,len(FIELDS))):
        if j==16:
            assert all((old[j*STRIDE+i]&1)==(new[j*STRIDE+i]&1)==0
                       for i in range(COUNT)),("carry divergence",j)
            continue
        assert old[j*STRIDE:(j+1)*STRIDE]==new[j*STRIDE:(j+1)*STRIDE],(
           j,"native result/inputs/stack divergence")
    report={
      "status":"PASS_NATIVE_VICE_EXCLUSIVE_OVERLAY_ONLY",
      "profile":PROFILE,"entry":ENTRY,
      "baseline_sha256":sha(source),"research_candidate_sha256":sha(candidate),
      "changed_memory_byte_indices":changed,
      "native_vice_calls":COUNT*2,
      "native_cycle_timing_measured":False,
      "native_candidate_expected_output_correct":True,
      "first_six_output_bytes_carry_inputs_and_stack_match":True,
      "last_two_output_bytes_outside_public_shr16_contract":True,
      "baseline_dump_sha256":a["dump_sha256"],
      "candidate_dump_sha256":b["dump_sha256"],
      "no_public_prg_binary_changed":True,
      "mixed_normal_UMUL32_calls_permitted_with_overlay":False,
      "native_reentry_and_patch_setup_cost_qualified":False,
    }
    dest=ROOT/"validation/review/ISSUE144_SHR16_OVERLAY_NATIVE_VICE_RESEARCH.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 EXCLUSIVE DIRECT-SLICE NATIVE VICE",COUNT*2,"PASS",flush=True)

if __name__=="__main__":main()
