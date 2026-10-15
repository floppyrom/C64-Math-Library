#!/usr/bin/env python3
"""Issue144 all-profile SEEK16_INIT accumulator-call overhead screen.

Create independently relocated, source-assembled SEEK16_INIT V1–V5 by
replacing repeated JSR/RTS accumulator helper transitions with either
inline code or symmetrical JMP/JMP (no return-stack pressure). Ordinary
SEEK16_STEP and original resident helpers remain unchanged. Does NOT
alter any shipped PRGs or claim interrupt reentrancy.
"""
from __future__ import annotations
import argparse,hashlib,json,re,statistics,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
from benchmark_seek_profiles import load,corpus,PROFILES
CONF={
 'v1_balanced': {'start':'3723','next':'38CE','helper':'38CE','helper_end':'38F8','loop':'37EA','once':'3809','ret':'380C','method':'inline'},
 'v2_pareto_fast':{'start':'18E2','next':'3D23','helper':'3EE3','helper_end':'3F01','loop':'198E','once':'19AB','ret':'19AE','method':'inline'},
 'v3_reu_512k':{'start':'3600','next':'3D23','helper':'5E54','helper_end':'5E72','loop':'36AC','once':'36C9','ret':'36CC','method':'inline'},
 'v4_reu_16m':{'start':'3600','next':'3D23','helper':'5E54','helper_end':'5E72','loop':'36AC','once':'36C9','ret':'36CC','method':'inline'},
 'v5_hybrid_lowzp': {'start':'3723','next':'38CE','helper':'38CE','helper_end':'38F8','loop':'37EA','once':'3809','ret':'380C','method':'inline'},
}
SPEEDS=(0x0080,0x0100,0x0180,0x0200,0x0300,0x0400,0x8100,0x8200,0x8300,0x8400)

def make(profile):
 conf=CONF[profile]
 s=(R/profile/'standalone/seek_u16_u8_init.asm').read_text()
 start='; ---- executable island $'+conf['start']+' ----'
 end='; ---- executable island $'+conf['next']+' ----'
 segment=s[s.index(start):s.index(end)]
 # Explicit labels for original unlabelled addresses needed by trampolines.
 for addr in (conf['once'],conf['ret']):
  label='L'+addr
  if not re.search(r'(?m)^'+label+':',segment):
   match=re.search(r'(?m)^    [^\n]+; @'+addr+r' ',segment)
   assert match,(profile,addr)
   segment=segment[:match.start()]+label+':\n'+segment[match.start():]
 labels=set(re.findall(r'(?m)^\s*(L[0-9A-Fa-f]{4}):',segment))
 # Local labels relocate; all external symbols keep exact numeric resident address.
 segment=re.sub(r'(?<!\w)L([0-9A-Fa-f]{4})\b',
    lambda m:m.group(0) if m.group(0) in labels else '$'+m.group(1),segment)
 segment=segment.replace('* = $'+conf['start'],'* = $0D00')
 # V1/V5 have longer absolute $C0xx accesses: the source-backed inline
 # expansion places two early conditional branches >127 bytes away.
 # Preserve both decisions exactly through complemented short branches
 # plus unconditional long jumps, without overwriting live $19F0/$1A00.
 if profile in ('v1_balanced','v5_hybrid_lowzp'):
  assert segment.count('bcc L3827')==1 and segment.count('bmi L382A')==1
  segment=segment.replace('bcc L3827','bcs seek_skip_empty\n    jmp L3827\nseek_skip_empty:',1)
  segment=segment.replace('bmi L382A','bpl seek_skip_euclid\n    jmp L382A\nseek_skip_euclid:',1)
 helper=s[s.index('L'+conf['helper']+':'):s.index('L'+conf['helper_end']+':')]
 assert re.search(r'(?m)^    rts\b',helper)
 def clone(tag,return_label,inline):
  text=helper
  labellist=set(re.findall(r'(?m)^\s*(L[0-9A-Fa-f]{4}):',text))
  text=re.sub(r'(?<!\w)L[0-9A-Fa-f]{4}\b',lambda m:tag+'_'+m.group(0) if m.group(0) in labellist else '$'+m.group(0)[1:],text)
  text=re.sub(r'(?m)[ \t]*;[^\n]*','',text)
  assert text.rstrip().endswith('rts')
  return text.rstrip()[:-3]+('' if inline else 'jmp '+return_label)+'\n'
 needle='jsr $'+conf['helper'];assert segment.count(needle)==2,(profile,needle,segment.count(needle))
 if conf['method']=='inline':
  segment=segment.replace(needle,clone('INLINE','',True),1)
 else:segment=segment.replace(needle,'jmp SEEK_ACCUM_LOOP',1)
 segment=segment.replace(needle,'jmp SEEK_ACCUM_ONCE',1)
 if conf['method']=='jump':
  segment+='\n* = $0F00\nSEEK_ACCUM_LOOP:\n'+clone('LOOP','L'+hex(int(conf['loop'],16)+3)[2:].upper().zfill(4),False)
 segment+='\n* = $0F60\nSEEK_ACCUM_ONCE:\n'+clone('ONCE','L'+conf['ret'],False)
 # For JMP loop, original DEY @loop+3 was not a named label; insert label there.
 if conf['method']=='jump':
  ret='L'+hex(int(conf['loop'],16)+3)[2:].upper().zfill(4)
  segment=segment.replace('jmp '+ret+'\n', 'jmp '+ret+'\n')
  # Insert label at original annotated DEY before removing stale annotations.
  original=f'@{int(conf["loop"],16)+3:04X}'
  match=re.search(r'(?m)^    [^\n]+; '+original+r' ',segment)
  assert match,(profile,original)
  segment=segment[:match.start()]+ret+':\n'+segment[match.start():]
 segment=re.sub(r'(?m)[ \t]*; @[^\n]*','',segment)
 src='!cpu 6510\n'+segment
 mem,labels,_=Assembler().assemble(src)
 assert min(mem)==0x0D00 and max(mem)<0x1000
 assert labels['SEEK_ACCUM_ONCE']==0x0F60
 assert all(0<=v<=255 for v in mem.values())
 return src,mem,labels

def feed(cpu,api,move,speed,slot):
 x0,y0,x1,y1=move
 for k,v in [('MATH_SEEK16_POS_XL',x0&255),('MATH_SEEK16_POS_XH',x0>>8),('MATH_SEEK16_POS_Y',y0)]:cpu.mem[api[k]+slot]=v
 for addr,value in [(api['MATH_X'],x1&255),(api['MATH_X']+1,x1>>8),(api['MATH_Y'],y1),(api['MATH_N'],speed&255),(api['MATH_N']+1,speed>>8)]:cpu.mem[addr]=value
 cpu.x=slot

def test(profile,moves,write=False):
 source,code,labels=make(profile)
 stock,api=load(profile);opt,_=load(profile)
 for addr,value in code.items():
  assert opt.mem[addr]==0,(profile,hex(addr),'caller-owned RAM occupied')
  opt.mem[addr]=value
 jmp=api['MATH_SEEK16_INIT'];assert opt.mem[jmp]==0x4C
 old_target=opt.mem[jmp+1]|(opt.mem[jmp+2]<<8)
 assert old_target==int(CONF[profile]['start'],16)
 opt.mem[jmp+1:jmp+3]=(0x0D00).to_bytes(2,'little')
 if profile in ('v1_balanced','v5_hybrid_lowzp'):state_start,state_end=0x1980,0x1B00
 else:state_start,state_end=0x90E0,0x9200
 # Assert relocation leaves all original executable and table bytes intact.
 assert bytes(stock.mem[old_target:old_target+32])==bytes(opt.mem[old_target:old_target+32])
 assert stock.mem[0x19F0:0x1B00]==opt.mem[0x19F0:0x1B00]
 gs={speed:[] for speed in SPEEDS};samples=0;errors=[];orig=[];new=[]
 for i,move in enumerate(corpus(320)[:moves]):
  for si,speed in enumerate(SPEEDS):
   slot=(i*7+si)&7
   feed(stock,api,move,speed,slot);feed(opt,api,move,speed,slot)
   a=stock.call(jmp,4_000_000);b=opt.call(jmp,4_000_000)
   if stock.mem[state_start:state_end]!=opt.mem[state_start:state_end] or stock.c!=opt.c or stock.x!=opt.x or stock.sp!=opt.sp:
    errors.append((profile,i,hex(speed),'init'))
    if len(errors)>4:raise AssertionError(errors)
   orig.append(a);new.append(b);gs[speed].append(a-b);samples+=1
   for cpu in (stock,opt):cpu.x=slot
   stock.call(api['MATH_SEEK16_STEP'],4_000_000);opt.call(api['MATH_SEEK16_STEP'],4_000_000)
   if stock.mem[state_start:state_end]!=opt.mem[state_start:state_end] or stock.c!=opt.c:errors.append((profile,i,hex(speed),'step'))
 assert not errors,errors
 gains=[a-b for a,b in zip(orig,new)]
 assert min(gains)>=-2,(profile,min(gains))
 result={'status':'PASS_SOURCE_ASSEMBLED_6510_PUBLIC_ABI_STATE_STEP','model_profiles':profile,'cases':samples,
 'public_mean_before':statistics.fmean(orig),'public_mean_after':statistics.fmean(new),'mean_saving':statistics.fmean(gains),'minimum_saving':min(gains),'maximum_saving':max(gains),
 'code_bytes':len(code),'max_code_address':hex(max(code)),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
 'return_stack_balanced':True,'original_resident_bytes_and_tables_untouched':True,
 'reference_reu_unchanged':True,'native_vice_tested':False,'method':CONF[profile]['method'],
 'by_speed':{f'${k:04X}':{'mean_saved':statistics.fmean(v),'min_saved':min(v),'max_saved':max(v)} for k,v in gs.items()}}
 if write:
  path=R/f'optional/issue144_seek16_accum_inline_all/{profile}.asm';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(source)
 print(profile,'moves',samples,'gain',round(result['mean_saving'],3),'range',min(gains),max(gains),'bytes',len(code),flush=True)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--moves',type=int,default=30);ap.add_argument('--profile',choices=PROFILES+['all'],default='all');ap.add_argument('--write',action='store_true');args=ap.parse_args()
 ps=PROFILES if args.profile=='all' else [args.profile]
 results={p:test(p,args.moves,args.write) for p in ps}
 if args.write:
  out=R/'validation/review/ISSUE144_SEEK16_ACCUM_INLINE_ALL_MODEL.json';out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(json.dumps({'status':'PASS_SOURCE_ASSEMBLED_PUBLIC_ABI','profiles':results},indent=2)+'\n')
 print('ISSUE144 SEEK16 ALL PROFILE MODEL PASS',sum(q['cases'] for q in results.values()))
if __name__=='__main__':main()
