#!/usr/bin/env python3
"""Issue144 B: first-pass source-owned V5 placement feasibility, not an importer.

Build unchanged V5 hybrid from canonical source on both relocation maps. Find
461-byte zero-valued resident windows that are zero after ALL current overlays.
Report symbol-relative intersection for both maps, and exact candidate SHA,
without interpreting zero bytes as sufficient ownership or execution proof.

No code patch, OptiSearch source, imported V2 dualtail, binary publication,
or claim of IRQ/NMI/reentrancy safety.
"""
from __future__ import annotations
import hashlib,json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from build_hybrid import build
from assemble_sources import parse_config
from source_relocation import REGIONS
from validate_source_build import validate
TAIL_BYTES=461
PROFILE="v5_hybrid_lowzp"
# Source-defined regions are inspected separately; no candidate crosses
# a region boundary even when two successive bytes happen to be zero.
SCAN=tuple(row[0] for row in REGIONS)
def windows(mem,base,length):
    # Return ALL maximal zero runs, not merely the impossible 461-byte option.
    out=[];i=0
    while i<length:
        if mem[base+i]!=0:i+=1;continue
        start=i
        while i<length and mem[base+i]==0:i+=1
        out.append((start,i-start))
    return out

def region_length(name):
    exact=[(start,end) for region,start,end in REGIONS if region==name]
    assert len(exact)==1,(name,exact)
    start,end=exact[0]
    return end-start+1

def main():
    rows={};corpus_by_map={}
    with tempfile.TemporaryDirectory(prefix="issue144_b_v5_island_") as td:
        for layout in ("reference","alternate"):
            cfg=ROOT/"relocatable_source"/PROFILE/("math_config_"+layout+".inc")
            vals=parse_config(cfg)
            out=Path(td)/layout/PROFILE
            man=build(cfg,out)
            assert man["normal_zp_bytes"]==31
            prg=(out/man["output_prg"]).read_bytes()
            at=int.from_bytes(prg[:2],"little")
            mem=bytearray(65536)
            assert at+len(prg)-2<=65536
            mem[at:at+len(prg)-2]=prg[2:]
            result={}
            for name in SCAN:
                start=vals[name]
                length=region_length(name)
                assert start>=at and start+length<=at+len(prg)-2,(layout,name,
                       hex(start),hex(at+len(prg)-2))
                runs=windows(mem,start,length)
                top=sorted(runs,key=lambda a:(-a[1],a[0]))[:12]
                large=[(a,sz) for a,sz in runs if sz>=TAIL_BYTES]
                result[name]={"region_base":hex(start),"length":length,
                     "hole_count":len(large),
                     "max_zero_run_bytes":max((sz for _,sz in runs),default=0),
                     "runs_at_least_32":sum(sz>=32 for _,sz in runs),
                     "runs_at_least_64":sum(sz>=64 for _,sz in runs),
                     "runs_at_least_128":sum(sz>=128 for _,sz in runs),
                     "runs_at_least_232":sum(sz>=232 for _,sz in runs),
                     "total_zero_bytes_in_runs_32plus":sum(sz for _,sz in runs if sz>=32),
                     "longest_12_unclaimed_candidates":[{"offset":hex(a),"bytes":sz}
                                                          for a,sz in top],
                     "candidates_offset":[{"offset":hex(a),"bytes":sz}
                                          for a,sz in large[:16]],
                     "all_offsets":[a for a,sz in large for a in range(a,a+sz-TAIL_BYTES+1)]}
            check=validate(PROFILE,Path(td)/layout)
            assert check["public_entries_executed"]==56 and check["machine_calls"]==21678
            rows[layout]={"normal_zp":31,"public_entries":56,"public_calls":check["machine_calls"],
                          "unchanged_source_prg_sha256":hashlib.sha256(prg).hexdigest(),
                          "regions":{k:{kk:vv for kk,vv in v.items() if kk!="all_offsets"} for k,v in result.items()}}
            corpus_by_map[layout]=result
            print("V5 DUALTAIL HOLE FEASIBILITY",layout,"PASS",flush=True)
    common={}
    for name in SCAN:
        ref=set(corpus_by_map["reference"][name]["all_offsets"])
        alt=set(corpus_by_map["alternate"][name]["all_offsets"])
        both=sorted(ref&alt)
        common[name]={"intersecting_461byte_symbol_relative_offsets":len(both),
                      "first_16_offsets":[hex(a) for a in both[:16]],
                      "possible":bool(both)}
    report={"status":"PASS_V5_RELOCATION_HOLE_SURVEY_NOT_PROOF_OF_OWNERSHIP",
        "tail_bytes":TAIL_BYTES,"default_source_unchanged":True,
        "imported_auxiliary_tail":False,"native_vice_executed":False,
        "zero_filled_region_is_not_code_ownership_proof":True,
        "V5_ordinary_source_all_56_entries_pass":True,
        "layout_results":rows,"matching_offsets":common,
        "next_required_gates":["source ownership, labels, data relocation and all future generated overlays",
          "relocate all reachable V2 donor JMP/JSR/zero page operands",
          "56-entry regression and executed-program write guard",
          "sign/mixed/interrupt interleaving and 31-byte ZP bound",
          "actual VICE and physical VIC/REU bus tests"]}
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
