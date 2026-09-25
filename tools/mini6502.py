#!/usr/bin/env python3
"""Self-contained legal-NMOS-6502 assembler/emulator used by the game-math extension.
Supports the documented opcodes/addressing modes exercised by the extension and
cycle-accurate branch/page-cross penalties. Decimal ADC/SBC is intentionally
implemented because public API requires D=0 but the emulator should be faithful.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

OPS = {
'brk':{'imp':0x00},
'ora':{'indx':0x01,'zp':0x05,'imm':0x09,'abs':0x0D,'indy':0x11,'zpx':0x15,'absy':0x19,'absx':0x1D},
'asl':{'zp':0x06,'acc':0x0A,'abs':0x0E,'zpx':0x16,'absx':0x1E},
'php':{'imp':0x08}, 'bpl':{'rel':0x10}, 'clc':{'imp':0x18},
'jsr':{'abs':0x20},
'and':{'indx':0x21,'zp':0x25,'imm':0x29,'abs':0x2D,'indy':0x31,'zpx':0x35,'absy':0x39,'absx':0x3D},
'bit':{'zp':0x24,'abs':0x2C}, 'rol':{'zp':0x26,'acc':0x2A,'abs':0x2E,'zpx':0x36,'absx':0x3E},
'plp':{'imp':0x28}, 'bmi':{'rel':0x30}, 'sec':{'imp':0x38},
'rti':{'imp':0x40},
'eor':{'indx':0x41,'zp':0x45,'imm':0x49,'abs':0x4D,'indy':0x51,'zpx':0x55,'absy':0x59,'absx':0x5D},
'lsr':{'zp':0x46,'acc':0x4A,'abs':0x4E,'zpx':0x56,'absx':0x5E},
'pha':{'imp':0x48}, 'jmp':{'abs':0x4C,'ind':0x6C}, 'bvc':{'rel':0x50}, 'cli':{'imp':0x58},
'rts':{'imp':0x60},
'adc':{'indx':0x61,'zp':0x65,'imm':0x69,'abs':0x6D,'indy':0x71,'zpx':0x75,'absy':0x79,'absx':0x7D},
'ror':{'zp':0x66,'acc':0x6A,'abs':0x6E,'zpx':0x76,'absx':0x7E},
'pla':{'imp':0x68}, 'bvs':{'rel':0x70}, 'sei':{'imp':0x78},
'sta':{'indx':0x81,'zp':0x85,'abs':0x8D,'indy':0x91,'zpx':0x95,'absy':0x99,'absx':0x9D},
'sty':{'zp':0x84,'abs':0x8C,'zpx':0x94}, 'stx':{'zp':0x86,'abs':0x8E,'zpy':0x96},
'dey':{'imp':0x88}, 'txa':{'imp':0x8A}, 'bcc':{'rel':0x90}, 'tya':{'imp':0x98}, 'txs':{'imp':0x9A},
'ldy':{'imm':0xA0,'zp':0xA4,'abs':0xAC,'zpx':0xB4,'absx':0xBC},
'lda':{'indx':0xA1,'zp':0xA5,'imm':0xA9,'abs':0xAD,'indy':0xB1,'zpx':0xB5,'absy':0xB9,'absx':0xBD},
'ldx':{'imm':0xA2,'zp':0xA6,'abs':0xAE,'zpy':0xB6,'absy':0xBE},
'tay':{'imp':0xA8}, 'tax':{'imp':0xAA}, 'bcs':{'rel':0xB0}, 'clv':{'imp':0xB8}, 'tsx':{'imp':0xBA},
'cpy':{'imm':0xC0,'zp':0xC4,'abs':0xCC},
'cmp':{'indx':0xC1,'zp':0xC5,'imm':0xC9,'abs':0xCD,'indy':0xD1,'zpx':0xD5,'absy':0xD9,'absx':0xDD},
'dec':{'zp':0xC6,'abs':0xCE,'zpx':0xD6,'absx':0xDE},
'iny':{'imp':0xC8}, 'dex':{'imp':0xCA}, 'bne':{'rel':0xD0}, 'cld':{'imp':0xD8},
'cpx':{'imm':0xE0,'zp':0xE4,'abs':0xEC},
'sbc':{'indx':0xE1,'zp':0xE5,'imm':0xE9,'abs':0xED,'indy':0xF1,'zpx':0xF5,'absy':0xF9,'absx':0xFD},
'inc':{'zp':0xE6,'abs':0xEE,'zpx':0xF6,'absx':0xFE},
'inx':{'imp':0xE8}, 'nop':{'imp':0xEA}, 'beq':{'rel':0xF0}, 'sed':{'imp':0xF8},
}
# Stable NMOS unintended opcodes (names as in ACME's !cpu 6510; ALR is also
# accepted as ASR). Timings/semantics follow "No More Secrets" (NMOS 6510
# Unintended Opcodes). The unstable SHA/SHX/SHY/TAS/ANE/LAX#imm are omitted.
ILLEGAL = {
'slo':{'zp':0x07,'zpx':0x17,'indx':0x03,'indy':0x13,'abs':0x0F,'absx':0x1F,'absy':0x1B},
'rla':{'zp':0x27,'zpx':0x37,'indx':0x23,'indy':0x33,'abs':0x2F,'absx':0x3F,'absy':0x3B},
'sre':{'zp':0x47,'zpx':0x57,'indx':0x43,'indy':0x53,'abs':0x4F,'absx':0x5F,'absy':0x5B},
'rra':{'zp':0x67,'zpx':0x77,'indx':0x63,'indy':0x73,'abs':0x6F,'absx':0x7F,'absy':0x7B},
'sax':{'zp':0x87,'zpy':0x97,'indx':0x83,'abs':0x8F},
'lax':{'zp':0xA7,'zpy':0xB7,'indx':0xA3,'indy':0xB3,'abs':0xAF,'absy':0xBF},
'dcp':{'zp':0xC7,'zpx':0xD7,'indx':0xC3,'indy':0xD3,'abs':0xCF,'absx':0xDF,'absy':0xDB},
'isc':{'zp':0xE7,'zpx':0xF7,'indx':0xE3,'indy':0xF3,'abs':0xEF,'absx':0xFF,'absy':0xFB},
'anc':{'imm':0x0B},
'alr':{'imm':0x4B}, 'asr':{'imm':0x4B},
'arr':{'imm':0x6B},
'sbx':{'imm':0xCB},
}
OPS.update(ILLEGAL)
BR={'bpl','bmi','bvc','bvs','bcc','bcs','bne','beq'}
SIZE={'imp':1,'acc':1,'imm':2,'zp':2,'zpx':2,'zpy':2,'indx':2,'indy':2,'rel':2,'abs':3,'absx':3,'absy':3,'ind':3}

REV={}
for op,modes in OPS.items():
    for mode,code in modes.items(): REV[code]=(op,mode)
# Stable NMOS undocumented subset intentionally used by the selected DIV kernels.
REV[0xA7]=('lax','zp')   # LAX zp: A=X=M, 3 cycles
REV[0xAF]=('lax','abs')  # LAX abs: A=X=M, 4 cycles
REV[0xBF]=('lax','absy') # LAX abs,Y: A=X=M, 4 cycles (+ page cross)
REV[0x0B]=('anc','imm')  # ANC #imm: A&=imm, C=N, 2 cycles
REV[0x2B]=('anc','imm')
REV[0x4B]=('alr','imm')
REV[0xEB]=('sbc','imm')  # SBC #imm duplicate

BASE_CYCLES={
'imp':2,'acc':2,'imm':2,'zp':3,'zpx':4,'zpy':4,'abs':4,'absx':4,'absy':4,'indx':6,'indy':5,'ind':5,'rel':2
}
# opcode-specific overrides
FIXED={0x00:7,0x08:3,0x20:6,0x28:4,0x40:6,0x48:3,0x4C:3,0x60:6,0x68:4,0x6C:5}
RMW=set([0x06,0x0E,0x16,0x1E,0x26,0x2E,0x36,0x3E,0x46,0x4E,0x56,0x5E,0x66,0x6E,0x76,0x7E,
         0xC6,0xCE,0xD6,0xDE,0xE6,0xEE,0xF6,0xFE])
STORE=set([0x81,0x85,0x8D,0x91,0x95,0x99,0x9D,0x84,0x8C,0x94,0x86,0x8E,0x96])
for _op in ('slo','rla','sre','rra','dcp','isc'): RMW.update(ILLEGAL[_op].values())
STORE.update(ILLEGAL['sax'].values())

class Assembler:
    def __init__(self): self.const={}; self.labels={}; self.items=[]
    def _clean(self,text):
        out=[]
        for raw in text.splitlines():
            s=raw.split(';',1)[0].strip()
            if s.lower().startswith('!cpu'): continue  # ACME CPU selection
            if s: out.append(s)
        return out
    def expr(self,s,labels=None):
        labels = self.labels if labels is None else labels
        s=s.strip()
        if s.startswith('<'): return self.expr(s[1:],labels)&255
        if s.startswith('>'): return (self.expr(s[1:],labels)>>8)&255
        # simple + / - expression
        m=re.fullmatch(r'(.+?)\s*([+-])\s*(\$[0-9A-Fa-f]+|%[01]+|\d+)',s)
        if m:
            v=self.expr(m.group(1),labels); d=self.expr(m.group(3),labels)
            return v+d if m.group(2)=='+' else v-d
        if s in labels: return labels[s]
        if s in self.const: return self.const[s]
        if s.startswith('$'): return int(s[1:],16)
        if s.startswith('%'): return int(s[1:],2)
        return int(s,0)
    def _mode(self,op,arg,labels,zp_hint=False):
        if op in BR: return 'rel',arg
        if arg is None or arg=='':
            if 'acc' in OPS.get(op,{}) and 'imp' not in OPS.get(op,{}): return 'acc',None
            return 'imp',None
        if arg.lower()=='a': return 'acc',None
        if arg.startswith('#'): return 'imm',arg[1:].strip()
        if arg.startswith('(') and arg.lower().endswith(',x)'): return 'indx',arg[1:-3].strip()
        if arg.startswith('(') and arg.lower().endswith('),y'): return 'indy',arg[1:-3].strip()
        if arg.startswith('(') and arg.endswith(')'): return 'ind',arg[1:-1].strip()
        suffix=None; base=arg
        if arg.lower().endswith(',x'): suffix='x'; base=arg[:-2].strip()
        elif arg.lower().endswith(',y'): suffix='y'; base=arg[:-2].strip()
        try: v=self.expr(base,labels); iszp=(0<=v<256)
        except: iszp=zp_hint
        if op in ('jmp','jsr'): return 'abs',base
        if suffix=='x': return ('zpx' if iszp and 'zpx' in OPS[op] else 'absx'),base
        if suffix=='y':
            if iszp and 'zpy' in OPS[op]: return 'zpy',base
            return 'absy',base
        return ('zp' if iszp and 'zp' in OPS[op] else 'abs'),base
    def assemble(self,text):
        lines=self._clean(text); self.const={}; self.labels={}; self.items=[]
        # Constants pass before code; allow NAME = expr with prior constants.
        code=[]
        for s in lines:
            m=re.fullmatch(r'([A-Za-z_.][\w.]*)\s*=\s*(.+)',s)
            if m and not s.startswith('*='):
                try:self.const[m.group(1)]=self.expr(m.group(2),{})
                except: code.append(s)
            else: code.append(s)
        # iterative layout because forward labels default absolute; explicit low numeric scratch avoids ambiguity.
        pc=0; labels={}; layout=[]
        for _ in range(3):
            pc=0; labels2={}; layout=[]
            for s0 in code:
                s=s0
                # ACME-style layout-time self-modifying aliases, e.g. x0 = *+1.
                meq=re.fullmatch(r'([A-Za-z_.][\w.]*)\s*=\s*\*\s*([+-])\s*(\d+|\$[0-9A-Fa-f]+)',s)
                if meq:
                    delta=self.expr(meq.group(3),labels|labels2)
                    labels2[meq.group(1)]=pc + (delta if meq.group(2)=='+' else -delta)
                    continue
                mo=re.fullmatch(r'(?:\*|\.org)\s*=*\s*(.+)',s,re.I)
                if mo: pc=self.expr(mo.group(1),labels|labels2); layout.append(('org',pc)); continue
                # label prefix
                if ':' in s:
                    left,right=s.split(':',1)
                    if re.fullmatch(r'[A-Za-z_.][\w.]*',left.strip()):
                        labels2[left.strip()]=pc; s=right.strip()
                        if not s: continue
                elif re.fullmatch(r'[A-Za-z_.][\w.]*',s) and s.lower() not in OPS:
                    labels2[s]=pc; continue
                if s.lower().startswith(('!byte','.byte')):
                    vals=s.split(None,1)[1].split(','); layout.append(('byte',pc,[v.strip() for v in vals])); pc+=len(vals); continue
                parts=s.split(None,1); op=parts[0].lower(); op=op[:-2] if op.endswith('+1') else op; arg=parts[1].strip() if len(parts)>1 else None
                mode,_=self._mode(op,arg,labels|labels2)
                layout.append(('ins',pc,op,arg,mode)); pc+=SIZE[mode]
            if labels2==labels: break
            labels=labels2
        self.labels=labels
        mem={}
        for it in layout:
            if it[0]=='org': continue
            if it[0]=='byte':
                _,pc,vals=it
                for v in vals: mem[pc]=self.expr(v)&255; pc+=1
                continue
            _,pc,op,arg,mode=it; mode,arg2=self._mode(op,arg,self.labels)
            codeop=OPS[op][mode]; bs=[codeop]
            if mode=='rel':
                target=self.expr(arg2); d=target-(pc+2)
                if not -128<=d<=127: raise ValueError(f'branch out of range {hex(pc)} {op} {arg2} {d}')
                bs.append(d&255)
            elif mode=='imm': bs.append(self.expr(arg2)&255)
            elif mode in ('zp','zpx','zpy','indx','indy'): bs.append(self.expr(arg2)&255)
            elif mode in ('abs','absx','absy','ind'):
                v=self.expr(arg2); bs.extend((v&255,(v>>8)&255))
            for b in bs: mem[pc]=b; pc+=1
        return mem,dict(self.labels),dict(self.const)

@dataclass
class CPU:
    mem: bytearray
    a:int=0; x:int=0; y:int=0; sp:int=0xFD; pc:int=0
    c:int=0; z:int=0; i:int=0; d:int=0; v:int=0; n:int=0; cycles:int=0
    reu: bytearray|None=None
    def __post_init__(self):
        if len(self.mem)<65536: self.mem.extend(b'\0'*(65536-len(self.mem)))
    def status(self,b=0): return self.c|(self.z<<1)|(self.i<<2)|(self.d<<3)|(b<<4)|0x20|(self.v<<6)|(self.n<<7)
    def set_status(self,p): self.c=p&1; self.z=(p>>1)&1; self.i=(p>>2)&1; self.d=(p>>3)&1; self.v=(p>>6)&1; self.n=(p>>7)&1
    def nz(self,v): v&=255; self.z=int(v==0); self.n=(v>>7)&1; return v
    def rd(self,a): return self.mem[a&0xffff]
    def wr(self,a,v):
        a &= 0xffff; v &= 255; self.mem[a]=v
        if a==0xDF01 and (v&0x80) and self.reu is not None:
            typ=v&3
            c64=self.mem[0xDF02]|(self.mem[0xDF03]<<8)
            ra=self.mem[0xDF04]|(self.mem[0xDF05]<<8)|(self.mem[0xDF06]<<16)
            ln=self.mem[0xDF07]|(self.mem[0xDF08]<<8); ln=65536 if ln==0 else ln
            acr=self.mem[0xDF0A]; fix_c64=bool(acr&0x80); fix_reu=bool(acr&0x40)
            for j in range(ln):
                ca=c64 if fix_c64 else ((c64+j)&0xffff); rr=ra if fix_reu else ((ra+j)&0xffffff)
                if typ==1: self.mem[ca]=self.reu[rr]
                elif typ==0: self.reu[rr]=self.mem[ca]
                elif typ==2:
                    t=self.mem[ca]; self.mem[ca]=self.reu[rr]; self.reu[rr]=t
                else:
                    pass
            self.cycles += ln if typ in (0,1) else (2*ln if typ==2 else ln)
    def push(self,v): self.wr(0x100+self.sp,v); self.sp=(self.sp-1)&255
    def pop(self): self.sp=(self.sp+1)&255; return self.rd(0x100+self.sp)
    def fetch(self): v=self.rd(self.pc); self.pc=(self.pc+1)&0xffff; return v
    def addr(self,mode):
        cross=False
        if mode=='zp': return self.fetch(),False
        if mode=='zpx': return (self.fetch()+self.x)&255,False
        if mode=='zpy': return (self.fetch()+self.y)&255,False
        if mode=='abs': lo=self.fetch(); hi=self.fetch(); return lo|(hi<<8),False
        if mode=='absx':
            lo=self.fetch(); hi=self.fetch(); base=lo|(hi<<8); a=(base+self.x)&0xffff; return a,(base&0xff00)!=(a&0xff00)
        if mode=='absy':
            lo=self.fetch(); hi=self.fetch(); base=lo|(hi<<8); a=(base+self.y)&0xffff; return a,(base&0xff00)!=(a&0xff00)
        if mode=='indx':
            zp=(self.fetch()+self.x)&255; return self.rd(zp)|(self.rd((zp+1)&255)<<8),False
        if mode=='indy':
            zp=self.fetch(); base=self.rd(zp)|(self.rd((zp+1)&255)<<8); a=(base+self.y)&0xffff; return a,(base&0xff00)!=(a&0xff00)
        if mode=='ind':
            lo=self.fetch(); hi=self.fetch(); p=lo|(hi<<8); # NMOS page-wrap bug
            return self.rd(p)|(self.rd((p&0xff00)|((p+1)&255))<<8),False
        raise ValueError(mode)
    def _adc(self,val):
        a=self.a; c=self.c
        if not self.d:
            s=a+val+c; r=s&255; self.c=int(s>255); self.v=int((~(a^val)&(a^r)&0x80)!=0); self.a=self.nz(r); return
        # NMOS decimal approximation faithful for flags V/N/Z from binary result, C from BCD correction.
        b=a+val+c; r=b&255; self.v=int((~(a^val)&(a^r)&0x80)!=0); self.z=int(r==0); self.n=(r>>7)&1
        lo=(a&15)+(val&15)+c; hi=(a>>4)+(val>>4)
        if lo>9: lo+=6; hi+=1
        if hi>9: hi+=6
        self.c=int(hi>15); self.a=((hi<<4)|(lo&15))&255
    def _sbc(self,val): self._adc(val^255)
    def step(self):
        pc0=self.pc; oc=self.fetch()
        if oc not in REV: raise RuntimeError(f'unsupported opcode ${oc:02X} at ${pc0:04X}')
        op,mode=REV[oc]; extra=0
        if oc in FIXED: cyc=FIXED[oc]
        elif oc in RMW:
            cyc={'zp':5,'zpx':6,'abs':6,'absx':7,'absy':7,'indx':8,'indy':8,'acc':2}[mode]
        elif oc in STORE:
            cyc={'zp':3,'zpx':4,'zpy':4,'abs':4,'absx':5,'absy':5,'indx':6,'indy':6}[mode]
        else: cyc=BASE_CYCLES[mode]
        # branches
        if mode=='rel':
            off=self.fetch(); off=off-256 if off&128 else off
            cond={'bpl':not self.n,'bmi':self.n,'bvc':not self.v,'bvs':self.v,'bcc':not self.c,'bcs':self.c,'bne':not self.z,'beq':self.z}[op]
            if cond:
                old=self.pc; self.pc=(self.pc+off)&0xffff; cyc+=1+int((old&0xff00)!=(self.pc&0xff00))
            self.cycles+=cyc; return oc
        if op=='brk': self.pc=(self.pc+1)&0xffff; self.push(self.pc>>8); self.push(self.pc&255); self.push(self.status(1)); self.i=1; self.pc=self.rd(0xfffe)|(self.rd(0xffff)<<8)
        elif op=='rts': lo=self.pop(); hi=self.pop(); self.pc=((lo|(hi<<8))+1)&0xffff
        elif op=='rti': self.set_status(self.pop()); lo=self.pop(); hi=self.pop(); self.pc=lo|(hi<<8)
        elif op=='jsr': lo=self.fetch(); hi=self.fetch(); ret=(self.pc-1)&0xffff; self.push(ret>>8); self.push(ret&255); self.pc=lo|(hi<<8)
        elif op=='jmp': self.pc=self.addr(mode)[0]
        elif op in ('clc','sec','cli','sei','cld','sed','clv'):
            if op=='clc':self.c=0
            elif op=='sec':self.c=1
            elif op=='cli':self.i=0
            elif op=='sei':self.i=1
            elif op=='cld':self.d=0
            elif op=='sed':self.d=1
            else:self.v=0
        elif op in ('pha','php','pla','plp'):
            if op=='pha':self.push(self.a)
            elif op=='php':self.push(self.status(1))
            elif op=='pla':self.a=self.nz(self.pop())
            else:self.set_status(self.pop())
        elif op in ('tax','txa','tay','tya','tsx','txs','inx','iny','dex','dey','nop'):
            if op=='tax':self.x=self.nz(self.a)
            elif op=='txa':self.a=self.nz(self.x)
            elif op=='tay':self.y=self.nz(self.a)
            elif op=='tya':self.a=self.nz(self.y)
            elif op=='tsx':self.x=self.nz(self.sp)
            elif op=='txs':self.sp=self.x
            elif op=='inx':self.x=self.nz(self.x+1)
            elif op=='iny':self.y=self.nz(self.y+1)
            elif op=='dex':self.x=self.nz(self.x-1)
            elif op=='dey':self.y=self.nz(self.y-1)
        else:
            if mode=='imm': val=self.fetch(); addr=None; cross=False
            elif mode=='acc': val=self.a; addr=None; cross=False
            else: addr,cross=self.addr(mode); val=self.rd(addr)
            if cross and mode in ('absx','absy','indy') and oc not in STORE and oc not in RMW: cyc+=1
            if op=='lda': self.a=self.nz(val)
            elif op=='lax': self.a=self.nz(val); self.x=self.a
            elif op=='anc': self.a=self.nz(self.a&val); self.c=self.n
            elif op=='ldx': self.x=self.nz(val)
            elif op=='ldy': self.y=self.nz(val)
            elif op=='sta': self.wr(addr,self.a)
            elif op=='stx': self.wr(addr,self.x)
            elif op=='sty': self.wr(addr,self.y)
            elif op=='adc': self._adc(val)
            elif op=='sbc': self._sbc(val)
            elif op=='and': self.a=self.nz(self.a&val)
            elif op=='ora': self.a=self.nz(self.a|val)
            elif op=='eor': self.a=self.nz(self.a^val)
            elif op in ('cmp','cpx','cpy'):
                reg=self.a if op=='cmp' else self.x if op=='cpx' else self.y; t=(reg-val)&0x1ff; self.c=int(reg>=val); self.z=int((t&255)==0); self.n=(t>>7)&1
            elif op=='bit': self.z=int((self.a&val)==0); self.n=(val>>7)&1; self.v=(val>>6)&1
            elif op in ('asl','lsr','rol','ror'):
                if op=='asl': self.c=(val>>7)&1; r=(val<<1)&255
                elif op=='lsr': self.c=val&1; r=val>>1
                elif op=='rol': c=self.c; self.c=(val>>7)&1; r=((val<<1)|c)&255
                else: c=self.c; self.c=val&1; r=((val>>1)|(c<<7))&255
                r=self.nz(r)
                if mode=='acc': self.a=r
                else:self.wr(addr,r)
            elif op=='inc': self.wr(addr,self.nz(val+1))
            elif op=='dec': self.wr(addr,self.nz(val-1))
            elif op=='sax': self.wr(addr,self.a&self.x)
            elif op=='slo': self.c=(val>>7)&1; r=(val<<1)&255; self.wr(addr,r); self.a=self.nz(self.a|r)
            elif op=='rla': c=self.c; self.c=(val>>7)&1; r=((val<<1)|c)&255; self.wr(addr,r); self.a=self.nz(self.a&r)
            elif op=='sre': self.c=val&1; r=val>>1; self.wr(addr,r); self.a=self.nz(self.a^r)
            elif op=='rra': c=self.c; self.c=val&1; r=(val>>1)|(c<<7); self.wr(addr,r); self._adc(r)
            elif op=='dcp':
                r=(val-1)&255; self.wr(addr,r); t=(self.a-r)&0x1ff; self.c=int(self.a>=r); self.z=int((t&255)==0); self.n=(t>>7)&1
            elif op=='isc': r=(val+1)&255; self.wr(addr,r); self._sbc(r)
            elif op=='alr': t=self.a&val; self.c=t&1; self.a=self.nz(t>>1)
            elif op=='arr':
                t=self.a&val; r=((t>>1)|(self.c<<7))&255; self.a=self.nz(r)
                if self.d: raise RuntimeError('ARR in decimal mode is not modelled')
                self.c=(r>>6)&1; self.v=((r>>6)^(r>>5))&1
            elif op=='sbx':
                t=self.a&self.x; self.c=int(t>=val); self.x=self.nz(t-val)
            else: raise RuntimeError((op,mode,hex(pc0)))
        self.cycles+=cyc; return oc
    def call(self,addr,max_steps=100000):
        sentinel=0xFF00; ret=(sentinel-1)&0xffff; self.push(ret>>8); self.push(ret&255); self.pc=addr; start=self.cycles
        for _ in range(max_steps):
            self.step()
            if self.pc==sentinel: return self.cycles-start
        raise RuntimeError('step limit')

def load_sparse(memdict):
    m=bytearray(65536)
    for a,b in memdict.items(): m[a]=b
    return m

def segments(memdict):
    if not memdict:return []
    ks=sorted(memdict); out=[]; s=p=ks[0]
    for k in ks[1:]:
        if k!=p+1: out.append((s,p+1)); s=k
        p=k
    out.append((s,p+1)); return out

if __name__=='__main__':
    src='''\n.org $2000\nstart: lda #1\n       adc #2\n       rts\n'''
    a=Assembler(); mem,l,c=a.assemble(src); cpu=CPU(load_sparse(mem)); cpu.c=0; cy=cpu.call(l['start']); assert cpu.a==3 and cy==10
    print('mini6502 self-test PASS',cy)
