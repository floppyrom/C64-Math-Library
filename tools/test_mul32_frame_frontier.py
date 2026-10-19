#!/usr/bin/env python3
"""Project-level frame RAM/ZP/peak selection, including relocation conservatism."""
import copy
import unittest
from mul32_frame_frontier import EvidenceError, summarize, frontier, select

def evidence():
    raw=[
        ("$8000","$C000",{"compact-pair":(541,0,97621,94759,596847),
         "unified375":(419,0,97621,94759,596847),
         "fast31-independent":(5152,31,19429,19277,119426),
         "fast31-shared":(2592,31,19524,19382,120169)}),
        ("$7123","$C040",{"compact-pair":(541,0,97994,95133,598989),
         "unified375":(419,0,97622,94761,596848),
         "fast31-independent":(5373,31,19356,19214,119077),
         "fast31-shared":(2813,31,19638,19488,120881)})]
    places=[]
    for code,io,variants in raw:
        rows={}
        for name,(ram,zp,peak,p95,total) in variants.items():
            rows[name]={"main_ram_total_bytes":ram,"zero_page_bytes":zp,
                "peak_frame_math_cycles":peak,"p95_frame_math_cycles":p95,
                "total_math_cycles":total,
                "linked_source_count":1 if name in ("unified375","fast31-shared") else 2,
                "variant_map":{"MATH_UMUL32":name,"MATH_SMUL32":name},
                "source_sha256":{"MATH_UMUL32":"a"*64,"MATH_SMUL32":"b"*64}}
        places.append({"code":code,"io":io,"paired_calls":150,"frames":24,
            "cpu_model_only":True,"native_pal_timing":False,
            "input_corpus_sha256":"c"*64,"per_option":rows})
    return {"placements":places}

class FrontierTests(unittest.TestCase):
    def test_all_two_map_pareto_evidence(self):
        s=summarize(evidence())
        self.assertEqual(s["per_option"]["fast31-shared"]["main_ram_total_bytes"],2813)
        self.assertEqual(s["per_option"]["fast31-shared"]["peak_frame_math_cycles"],19638)
        self.assertEqual(s["per_option"]["fast31-independent"]["main_ram_total_bytes"],5373)
        self.assertEqual(frontier(s),["fast31-independent","fast31-shared","unified375"])
        self.assertFalse(s["physical_pal_feasibility_claim"])

    def test_budgeted_selection(self):
        s=summarize(evidence())
        self.assertEqual(select(s,6000,31)["choice"],"fast31-independent")
        self.assertEqual(select(s,3000,31)["choice"],"fast31-shared")
        self.assertEqual(select(s,3000,0)["choice"],"unified375")
        self.assertEqual(select(s,6000,31,objective="ram")["choice"],"unified375")
        self.assertFalse(select(s,3000,31)["physical_pal_feasibility_claim"])

    def test_hard_frame_budget(self):
        s=summarize(evidence())
        self.assertEqual(select(s,6000,31,19500)["choice"],"fast31-independent")
        with self.assertRaises(EvidenceError):select(s,3000,31,19500)
        with self.assertRaises(EvidenceError):select(s,2600,31,20000)

    def test_reject_incompatible_or_incomplete_evidence(self):
        for mutation in (
            lambda d:d["placements"].pop(),
            lambda d:d["placements"][1].__setitem__("frames",25),
            lambda d:d["placements"][1].__setitem__("input_corpus_sha256","d"*64),
            lambda d:d["placements"][1].__setitem__("cpu_model_only",False),
            lambda d:d["placements"][1]["per_option"].pop("fast31-shared"),
            lambda d:d["placements"][1]["per_option"]["fast31-shared"]["source_sha256"].__setitem__("MATH_SMUL32","e"*64),
            lambda d:d["placements"][0]["per_option"]["unified375"].__setitem__("peak_frame_math_cycles",-1)):
            obj=copy.deepcopy(evidence());mutation(obj)
            with self.assertRaises(EvidenceError):summarize(obj)
        with self.assertRaises(EvidenceError):select(summarize(evidence()),True,31)

if __name__=="__main__":unittest.main()
