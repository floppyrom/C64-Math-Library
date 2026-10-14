#!/usr/bin/env python3
"""Diff source-built DIST8 candidate against shipped reference PRGs.

Do not promote a full generated PRG if unrelated code/data diverges. Report
every difference outside the intended same-address DIST8 swap first.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
P=("v1_balanced","v2_pareto_fast","v3_reu_512k",
   "v4_reu_16m","v5_hybrid_lowzp")
OFFSET={"v1_balanced":(0xCAED,14),"v2_pareto_fast":(0xCA06,10),
        "v3_reu_512k":(0xCA11,10),"v4_reu_16m":(0xC8D0,10),
        "v5_hybrid_lowzp":(0xCAED,14)}
def h(b):return hashlib.sha256(b).hexdigest()
def image(prg):
    load=int.from_bytes(prg[:2],"little")
    return load,prg[2:]
out={"profiles":{}}
for p in P:
    oldpath=R/p/"resident"/("math_"+p+"_game_math.prg")
    d=(R/"build_hybrid/reference" if p=="v5_hybrid_lowzp" else R/"build_source/reference")/p
    man=json.loads((d/"source_build_manifest.json").read_text())
    newpath=d/man["output_prg"]
    old=oldpath.read_bytes();new=newpath.read_bytes()
    old_load,old_data=image(old);new_load,new_data=image(new)
    offset,length=OFFSET[p]
    difference=[old_load+i for i,(a,b) in enumerate(zip(old_data,new_data)) if a!=b]
    in_window=[a for a in difference if offset<=a<offset+length]
    extra=[a for a in difference if not offset<=a<offset+length]
    row={"baseline_sha256":h(old),"source_sha256":h(new),
         "same_load":old_load==new_load,"same_length":len(old)==len(new),
         "total_diff_bytes":len(difference)+abs(len(old)-len(new)),
         "swap_window_changed_bytes":len(in_window),
         "outside_swap_changed_bytes":len(extra),
         "outside_swap_first_32":list(map(lambda n:f"${n:04X}",extra[:32])),
         "old_length":len(old),"source_length":len(new),
         "original_load":f"${old_load:04X}","source_load":f"${new_load:04X}"}
    out["profiles"][p]=row
    print(p,json.dumps(row),flush=True)
Path("/tmp/issue39_dist8_binary_diff.json").write_text(json.dumps(out,indent=2)+"\n")
