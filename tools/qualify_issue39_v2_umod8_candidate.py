#!/usr/bin/env python3
"""Issue #39 experimental V2-only D>=24 UMOD8 qualification.

Must be run AFTER source regeneration, reference/alternate V2 assembly and
reference V5 hybrid build. This does not publish a release or update benchmarks.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from issue39_root_historical_parent import undo_root_release

NAME='v2_pareto_fast'
ENTRY=0x3200
HELPER=0x5323
END=HELPER+101
PARENT=ROOT/NAME/'resident'/f'math_{NAME}_game_math.prg'
NEW=ROOT/'build_source/reference'/NAME/f'math_{NAME}_source_built.prg'
ALT=ROOT/'build_source/alternate'/NAME/f'math_{NAME}_source_built.prg'
V5=ROOT/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
V5_NEW=ROOT/'build_hybrid/reference/v5_hybrid_lowzp/math_v5_hybrid_lowzp_game_math.prg'
OUT=ROOT/'validation/review/ISSUE39_V2_UMOD8_D24_CANDIDATE.json'

def sha(data):return hashlib.sha256(data).hexdigest()
def memof(blob):
    lo=int.from_bytes(blob[:2],'little')
    m=bytearray(65536)
    m[lo:lo+len(blob)-2]=blob[2:]
    return m,lo

def cpubuild(blob):
    mem,_=memof(blob)
    cpu=CPU(mem)
    cpu.d=0
    cpu.call(0x3280,2_000_000)
    return cpu

def main():
    parentbytes=PARENT.read_bytes()
    newbytes=NEW.read_bytes()
    # This is a historical UMOD8 A/B proof. The independent root-only
    # source replacement must be reversed in BOTH source-built residents,
    # preserving exactly the original candidate/control arithmetic bytes.
    parentbytes=undo_root_release(NAME,parentbytes)
    newbytes=undo_root_release(NAME,newbytes)
    # Before publication the resident is the historical old image. After
    # publication reconstruct that *exact* historical image from the
    # SHA-certified 104 changed addresses, without altering the new code.
    if sha(parentbytes)== 'e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd':
        oldbytes=parentbytes
    elif sha(parentbytes)=='28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6':
        lo=int.from_bytes(parentbytes[:2],'little')
        old=bytearray(parentbytes)
        old[2+ENTRY-lo:2+ENTRY-lo+3]=bytes((0xAD,0x10,0xC0))
        old[2+HELPER-lo:2+END-lo]=bytes(101)
        oldbytes=bytes(old)
    elif sha(parentbytes)=='0510d469e1ff3bf136395e49b2e5055b9ab485fd87c4741ab5d0cbfc8fdf013d':
        # PR70's published resident relocates only the independent 32/32
        # modulo gate. Audit the pre-UMOD8 101-byte helper against *this*
        # SHA-qualified parent, without pretending it is the 2026-10-11 PRG.
        lo=int.from_bytes(parentbytes[:2],'little')
        old=bytearray(parentbytes)
        assert old[2+ENTRY-lo:2+ENTRY-lo+3]==bytes((0x4C,0x23,0x53))
        old[2+ENTRY-lo:2+ENTRY-lo+3]=bytes((0xAD,0x10,0xC0))
        old[2+HELPER-lo:2+END-lo]=bytes(101)
        oldbytes=bytes(old)
        assert sha(oldbytes)=='2a5f17aa3eabff7c53d75f46335dcbec1aa34d2343bf36d53f909bf109eec0a3'
    elif sha(parentbytes)=='c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84':
        # Current PR100 V2 remains a SHA-pinned 56-entry source-built image.
        # Reconstruct ONLY the retired UMOD8 guard for this historical A/B;
        # other divisions changed since PR70 and must remain identical.
        assert sha(newbytes)==sha(parentbytes), 'current V2 source-build drift'
        lo=int.from_bytes(parentbytes[:2],'little')
        old=bytearray(parentbytes)
        assert old[2+ENTRY-lo:2+ENTRY-lo+3]==bytes.fromhex('4c2353')
        assert sha(old[2+HELPER-lo:2+END-lo])=='6a733be6ca05992b46585c8443ae6ce7b21a075bfdfdfe34cf844e748b8f6f29'
        old[2+ENTRY-lo:2+ENTRY-lo+3]=bytes.fromhex('ad10c0')
        old[2+HELPER-lo:2+END-lo]=bytes(101)
        oldbytes=bytes(old)
    else:
        raise AssertionError('unrecognized V2 historical/release resident SHA')
    assert sha(oldbytes) in (
        'e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd',
        '2a5f17aa3eabff7c53d75f46335dcbec1aa34d2343bf36d53f909bf109eec0a3') or (
            sha(parentbytes)=='c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84'
            and oldbytes != parentbytes)
    assert oldbytes[:2]==newbytes[:2], 'load address changed'
    assert len(oldbytes)==len(newbytes), 'resident length changed'
    oldmem,lo=memof(oldbytes)
    newmem,_=memof(newbytes)
    assert lo==0x1000
    assert oldmem[ENTRY:ENTRY+3]==bytes((0xAD,0x10,0xC0))
    assert newmem[ENTRY:ENTRY+3]==bytes((0x4C,0x23,0x53))
    assert not any(oldmem[HELPER:END]), 'helper not exclusively empty in parent'
    assert len(newmem[HELPER:END])==101
    assert sha(newmem[HELPER:END])=='6a733be6ca05992b46585c8443ae6ce7b21a075bfdfdfe34cf844e748b8f6f29'
    diffs=[a for a in range(lo,lo+len(newbytes)-2) if oldmem[a]!=newmem[a]]
    assert diffs and all((ENTRY<=a<=ENTRY+2) or (HELPER<=a<END) for a in diffs), \
        f'unexpected changes outside V2 guard: {[hex(a) for a in diffs[:20]]}'
    alt=ALT.read_bytes()
    altmem,_=memof(alt)
    assert altmem[0xB200:0xB203]==bytes((0x4C,0x23,0x33))
    assert altmem[0x3323:0x3328]==bytes((0xAD,0x14,0xC8,0xC9,0x18))
    # PR71 intentionally changes only V5's Q-preserving UMOD32/32 gate.
    # Verify the source-built V5 against either its published pre-PR71
    # resident (after SHA-qualified reversal) or the promoted candidate.
    from issue39_v5_umod32_parent import restore_v5_umod32_parent
    v5_live=V5.read_bytes()
    v5_source=V5_NEW.read_bytes()
    if v5_live!=v5_source:
        assert v5_live==restore_v5_umod32_parent(v5_source), \
            'V5 contains changes outside SHA-certified PR71 UMOD32/32 frontend'

    before=cpubuild(oldbytes)
    after=cpubuild(newbytes)
    cycles_old=cycles_new=0
    hashes=[hashlib.sha256(),hashlib.sha256()]
    faster=slower=equal=0
    slowmax=0
    for n in range(256):
        for d in range(256):
            results=[]
            for ci,cpu in enumerate((before,after)):
                m=cpu.mem
                m[0xC010:0xC012]=bytes((n,0xB5))
                m[0xC014:0xC016]=bytes((d,0xA9))
                m[0xC018:0xC01C]=bytes((0xC3,0x5C,0x2B,0x97))
                m[0xC01C:0xC020]=bytes((0xD2,0x52,0x76,0x19))
                cycle=cpu.call(ENTRY,100000)
                hashes[ci].update(cycle.to_bytes(2,'little'))
                state=(m[0xC01C],cpu.c,bytes(m[0xC018:0xC01C]),\
                       bytes(m[0xC01D:0xC020]),\
                       bytes(m[0xC010:0xC012]),bytes(m[0xC014:0xC016]))
                expected=(n%d if d else 0,int(d==0),\
                          bytes((0xC3,0x5C,0x2B,0x97)),bytes((0x52,0x76,0x19)),\
                          bytes((n,0xB5)),bytes((d,0xA9)))
                assert state==expected,(ci,n,d,state,expected)
                results.append(cycle)
            delta=results[1]-results[0]
            faster+=delta<0;slower+=delta>0;equal+=delta==0
            slowmax=max(slowmax,delta)
            cycles_old+=results[0];cycles_new+=results[1]
    oldmean=cycles_old/65536
    newmean=cycles_new/65536
    assert (cycles_old,cycles_new)==(4247988,3421271),(cycles_old,cycles_new)
    assert slowmax==15,(slowmax,faster,slower,equal)
    report={'status':'PASS','qualification':'candidate only, not published release',
        'profile':'v2_pareto_fast','threshold_divisor':24,'guard_bytes':101,
        'all_input_pairs':65536,'paired_calls':131072,
        'old_mean_cycles':oldmean,'new_mean_cycles':newmean,
        'faster':faster,'equal':equal,'slower':slower,'maximum_regression_cycles':slowmax,
        'source_candidate_sha256':sha(newmem[HELPER:END]),
        'old_resident_sha256':sha(oldbytes),'new_resident_sha256':sha(newbytes),
        'old_cycle_stream_sha256':hashes[0].hexdigest(),
        'new_cycle_stream_sha256':hashes[1].hexdigest(),
        'delta_addresses':len(diffs),
        'v5_resident_byte_identical':v5_live==v5_source,
        'v5_source_diff_is_sha_certified_pr71_gate':True,
        'reference_and_alternate_relocation_validated':True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 V2 UMOD8 D24 CANDIDATE PASS',oldmean,newmean,faster,equal,slower,flush=True)

if __name__=='__main__':
    main()
