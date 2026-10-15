#!/usr/bin/env python3
"""Issue144 D: fail-closed ownership audit for V1/V5 in-resident SEEK16.

The apparent 427-byte contiguous code window starts at SEEK16_INIT but is NOT
a private allocation. The independently generated SEEK8 plane writer begins
at REG_API+$085B, before the old SEEK16 helper at +$08CE. This script prevents
false promotion based on isolated INIT/STEP measurements.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_seek16_v15_normal_resident_feasibility import candidate,BEGIN,LIMIT
from issue144_seek16_v15_source_relocation_screen import source_pair
from assemble_sources import parse_config
from generate_seek_sources import LAYOUTS

PRIVATE_END=0x385B
def main():
    assert LAYOUTS["v1_balanced"]["seek16_init"]=="REG_API+$0723"
    assert LAYOUTS["v1_balanced"]["seek8_planes"]=="REG_API+$085B"
    assert LAYOUTS["v1_balanced"]["seek16_helpers"]=="REG_API+$08CE"
    result={}
    for profile in ("v1_balanced","v5_hybrid_lowzp"):
        facts,mem=candidate(profile)
        assert mem is not None
        conflicts=sorted(a for a in mem if PRIVATE_END<=a<LIMIT)
        main=[a for a in mem if BEGIN<=a<PRIVATE_END]
        assert conflicts and min(conflicts)==PRIVATE_END,(profile,conflicts[:10])
        assert len(mem)==399 and facts["source_bytes"]==399
        # Native public ABI would execute SEEK8 plane writer through this
        # overwritten code. The previous isolated test never exercised SEEK8.
        result[profile]={
           "status":"REJECT_NOT_EXCLUSIVE_NORMAL_RESIDENT_FOOTPRINT",
           "candidate_bytes":len(mem),"actual_private_INIT_bytes":PRIVATE_END-BEGIN,
           "source_bytes_outside_private_INIT":len(conflicts),
           "interfering_owner":"SEEK8 plane writer",
           "interfering_region_reference":[hex(PRIVATE_END),hex(LIMIT)],
           "first_conflict":hex(conflicts[0]),"last_conflict":hex(conflicts[-1]),
           "native_vice_was_not_attempted":True,
           "source_promotion_unsafe":True,
           "caller_ram_option_remains_research_only":True}
    assert all(item["source_bytes_outside_private_INIT"]>0 for item in result.values())
    print(json.dumps({"status":"PASS_SAFETY_REJECTION", "candidate_not_promotable":True,
         "decision":"Do not install this 399-byte candidate in V1/V5 normal resident.",
         "profiles":result},indent=2,sort_keys=True))
if __name__=="__main__":main()
