#!/usr/bin/env python3
"""SHA-pinned undo of the V1 323-byte Q2 code-layout microoptimization.

Only for reproducing pre-PR68 historical V1 benchmark certificates. Never
change the shipped resident during normal public API calls.
"""
import hashlib
BEFORE='9afa30ffd24c1ce9566e7ef21e4032396fbdea7d4c3da5b68e137fc12ec41b62'
AFTER='cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f'
BEFORE_V5='26981cc03b06d1a797917ae34a5d8969db466435fff496a758a262bac75b254b'
AFTER_V5='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
OLD_CORE='f60d4ec80e4285e8bb3b243b3e7f93ae908989c0818ba2e543750d33ed8909eb'
NEW_CORE='7a1dfb987c2f9f1386cdbf7c4096c1a20cd9f143bce9907550cee209dacc2bc6'
# Only the 57 modified bytes, at zero-based offsets from REG_KERNEL+$0200.
OLD_BYTES=[[101,37],[110,27],[138,138],[139,174],[140,21],[141,192],[142,208],[143,5],[144,174],[145,20],[146,192],[147,240],[148,161],[149,168],[150,173],[151,28],[152,192],[153,237],[154,20],[156,141],[157,28],[159,152],[160,237],[161,21],[162,192],[163,141],[164,29],[166,205],[167,21],[169,176],[170,3],[171,76],[172,56],[173,67],[292,4],[298,5],[299,109],[302,141],[303,24],[304,192],[305,144],[306,4],[307,238],[308,25],[309,192],[310,24],[311,96],[312,169],[313,2],[314,141],[315,24],[316,192],[317,11],[318,0],[319,141],[320,25],[321,192]]
def sha(b):return hashlib.sha256(b).hexdigest()
def restore_u16_q2_parent(prg:bytes,profile:str)->bytes:
    assert profile in ('v1_balanced','v5_hybrid_lowzp')
    before,after=(BEFORE,AFTER) if profile=='v1_balanced' else (BEFORE_V5,AFTER_V5)
    lo=int.from_bytes(prg[:2],'little')
    assert lo==0x1000,'unsupported V1 origin'
    off=2+0x4200-lo
    core=prg[off:off+323]
    digest=sha(core)
    if digest==OLD_CORE:return prg
    assert digest==NEW_CORE,('unexpected V1 16bit core',digest)
    assert sha(prg)==after,('unknown live 16bit parent',profile,sha(prg))
    b=bytearray(prg)
    for i,previous in OLD_BYTES:b[off+i]=previous
    assert sha(b[off:off+323])==OLD_CORE
    restored=bytes(b)
    assert sha(restored)==before
    return restored

def restore_v1_q2_parent(prg:bytes)->bytes:
    return restore_u16_q2_parent(prg,'v1_balanced')

def restore_v5_q2_parent(prg:bytes)->bytes:
    from issue39_v5_umod32_parent import restore_v5_umod32_parent
    return restore_u16_q2_parent(restore_v5_umod32_parent(prg),'v5_hybrid_lowzp')
