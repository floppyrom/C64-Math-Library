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
SCAN=("REG_LOW","REG_KERNEL","REG_TABLE")
def windows(mem,base,length):
    out=[];i=0
    while i<length:
        if mem[base+i]!=0:i+=1;continue
        start=i
        while i<length and mem[base+i]==0:i+=1
        if i-start>=TAIL_BYTES:out.append((start,i-start))
    return out

def region_length(name):
    if name=="REG_LOW":return 0x2000
    if name=="REG_KERNEL":return 0x1e00
    if name=="REG_TABLE":return 0x3c00
    raise ValueError(name)

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
                result[name]={"region_base":hex(start),"length":length,
                     "hole_count":len(runs),
                     "candidates_offset":[{"offset":hex(a),"bytes":sz}
                                          for a,sz in runs[:16]],
                     "all_offsets":[a for a,sz in runs for a in range(a,a+sz-TAIL_BYTES+1)]}
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
