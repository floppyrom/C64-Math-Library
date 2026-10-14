#!/usr/bin/env python3
"""Issue #39 trig/angle: exhaustive 8-bit SIN/COS/SINCOS public ABI audit.

All 256 phases per profile and source map; compare the independent SIN8,
COS8 and combined SINCOS8 outputs on identical inputs. Also pin the
pre-existing exhaustive 655,360-call signed ATAN2_8 dispatcher certificate.
No unqualified OptiSearch candidate or private source is incorporated.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_smul24_directout import PROFILES,KINDS,load

OPS=("MATH_SIN8","MATH_COS8","MATH_SINCOS8")
def sha(data):return hashlib.sha256(data).hexdigest()

def bench(profile,kind):
    cpu,api=load(profile,kind)
    A=api["MATH_X"];B=api["MATH_Y"];C=api["MATH_Z"]
    results={key:bytearray() for key in OPS}
    cycles={key:[] for key in OPS}
    carry_vector={}
    for phase in range(256):
        outputs={}
        for i,op in enumerate(OPS):
            cpu.mem[A]=phase
            cpu.mem[B]=(phase*37+83)&255
            cpu.mem[C]=0xa5;cpu.mem[C+1]=0x5a
            cpu.c=(phase+i)&1
            cpu.d=0
            elapsed=cpu.call(api[op],2_000_000)
            got=bytes(cpu.mem[C:C+(2 if op=="MATH_SINCOS8" else 1)])
            assert cpu.mem[A]==phase and cpu.mem[B]==((phase*37+83)&255),(
                profile,kind,op,phase,"input clobber")
            assert cpu.c==0 and cpu.sp==0xfd,(profile,kind,op,phase,"carry/stack")
            if op!="MATH_SINCOS8":
                assert cpu.mem[C+1]==0x5a,(profile,kind,op,phase,"out-of-contract write")
            outputs[op]=got
            results[op].extend(got)
            cycles[op].append(elapsed)
        assert outputs["MATH_SINCOS8"]==outputs["MATH_SIN8"]+outputs["MATH_COS8"],(
            profile,kind,phase,"combined output mismatch",outputs)
    report={}
    for op in OPS:
        seq=cycles[op]
        report[op]={"cases":256,
            "mean_cycles":sum(seq)/256,"min_cycles":min(seq),"max_cycles":max(seq),
            "output_sha256":sha(results[op]),
            "cycle_vector_sha256":sha(b"".join(c.to_bytes(2,"little") for c in seq)),
            "inputs_preserved":True,"carry_clear":True,"stack_stable":True}
    total=[a+b-c for a,b,c in zip(cycles["MATH_SIN8"],cycles["MATH_COS8"],cycles["MATH_SINCOS8"])]
    report["paired_combined_vs_two_separate"]={
      "cases":256,"mean_saving_public_entry_cycles":sum(total)/256,
      "min_saving_cycles":min(total),"max_saving_cycles":max(total),
      "cycle_delta_sha256":sha(b"".join(c.to_bytes(2,"little",signed=True) for c in total)),
      "output_identity_all_256_phases":True}
    print(profile,kind,"SIN COS SINCOS PASS",
          "SINCOS",report["MATH_SINCOS8"]["mean_cycles"],
          "paired saving",report["paired_combined_vs_two_separate"]["mean_saving_public_entry_cycles"],
          flush=True)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    prior=json.loads((ROOT/"validation/ATAN2_DISPATCH_VALIDATION.json").read_text())
    assert prior["status"]=="PASS" and prior["machine_calls"]==655360
    data={"status":"PASS_PUBLIC_TRIG_ANGLE_EXHAUSTIVE",
      "scope":"SIN8 COS8 SINCOS8 per 256 phase plus already-qualified full signed atan2",
      "source_maps":list(KINDS),"profiles":{},
      "new_public_trig_calls":0,"already_qualified_public_atan2_calls":655360,
      "native_cycle_timing_measured":False,"private_optisearch_source_published":False,
      "no_production_binary_or_ABI_changes":True}
    for profile in PROFILES:
        data["profiles"][profile]={}
        for kind in KINDS:
            row=bench(profile,kind)
            data["profiles"][profile][kind]=row
            data["new_public_trig_calls"]+=256*3
            legacy=prior["results"][profile][kind]
            assert legacy["cases"]==65536 and legacy["input_or_carry_or_stack_failures"]==0
            assert legacy["max_phase_error"] <= (0 if profile=="v4_reu_16m" else 1)
        reference,alternate=(data["profiles"][profile][kind] for kind in KINDS)
        for op in OPS:
            assert reference[op]["output_sha256"]==alternate[op]["output_sha256"],(profile,op,"relocation output")
            assert reference[op]["cycle_vector_sha256"]==alternate[op]["cycle_vector_sha256"],(
                 profile,op,"relocation timing")
    assert data["new_public_trig_calls"]==7680
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 TRIG ANGLE FAMILY EXHAUSTIVE PASS",data["new_public_trig_calls"],flush=True)
if __name__=="__main__":main()
