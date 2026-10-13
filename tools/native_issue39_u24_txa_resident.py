#!/usr/bin/env python3
"""Independent actual VICE x64sc correctness of old/new UDIV24/UMOD24 residents.

Uses Git's immutable parent SHA to reconstruct shipped PRGs; binary PRGs are
then loaded into a real Commodore 64 emulator (not our Python CPU model).
48 paired operands x 2 APIs x 5 profiles x 2 images = 960 native calls.
No claim about physical cycle times, REU transport speed, or alternate-map
native runs. Normal-ZP and size are tested by separate CI validators.
"""
from pathlib import Path
import argparse,hashlib,json,os,random,socket,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OPS=('MATH_UDIV24','MATH_UMOD24')
API={'MATH_UDIV24':0x3170,'MATH_UMOD24':0x3223}
PARENT='c88416430737bfb84903b9af5acba96e71a7605b'
H=0x0b00
INPUT=0x0400
OUTPUT=0x0600
COUNT=48
STRIDE=64
MAPIO=0xc000
FIELDS=[MAPIO+0x18+i for i in range(4)]+[MAPIO+0x1c+i for i in range(4)]+[MAPIO+0x10+i for i in range(3)]+[MAPIO+0x14+i for i in range(3)]+[0xc030]
def sha(b):return hashlib.sha256(b).hexdigest()
def inputs():
 e=[(0,0),(0,1),(1,0),(1,1),(2,1),(3,2),(0xffffff,0),
    (0xffffff,1),(0xffffff,2),(0xffffff,255),(0xffffff,256),
    (0xffffff,65535),(0xffffff,0xffffff),(0xfffffe,0xffffff),
    (65536,1),(65536,2),(65536,65536),(65536,65535),(0x10000,0xff),
    (0x123456,0x101010),(0x123456,0x222222),(0x876543,0x123456),
    (0x876543,0x87ffff),(0x801234,0x012345),(0xfedcba,0xabcdef),
    (0x800000,0x7fffff),(0x7fffff,0x800000),(0x012345,0x012345),
    (0x012346,0x012345),(0x012344,0x012345),(0x654321,0x654321),
    (0x001234,0x000001),(0x9abcde,0x000111)]
 rng=random.Random(0xC639247A)
 while len(e)<COUNT:
  d=rng.getrandbits(24)
  n=rng.getrandbits(24)
  e.append((n,d))
 assert len(e)==COUNT
 return e
def machine_bytes(prg):
 load=int.from_bytes(prg[:2],'little')
 assert load==0x1000
 m=bytearray(65536);m[load:load+len(prg)-2]=prg[2:]
 return m
def harness(entry):
 b=bytearray()
 def emit(*xs):b.extend(xs)
 def op(code,address):emit(code,address&255,address>>8)
 emit(0x78,0xd8,0xa9,0x34,0x85,0x01)   # SEI CLD; RAM under both ROMs visible
 op(0x20,0x3280)                     # actual MATH_INIT
 emit(0xa2,0x00)                     # LDX #0
 loop=H+len(b)
 for j in range(3):
  op(0xbd,INPUT+j*STRIDE)
  op(0x8d,MAPIO+0x10+j)
  op(0xbd,INPUT+(j+3)*STRIDE)
  op(0x8d,MAPIO+0x14+j)
 # Precondition hygiene; output sentinels and the true values must be checked.
 emit(0xa9,0x91)
 for j in range(4):op(0x8d,MAPIO+0x18+j)
 emit(0xa9,0x82)
 for j in range(4):op(0x8d,MAPIO+0x1c+j)
 emit(0x8a,0x48,0x38)                # TXA PHA SEC, caller X retained
 op(0x20,entry)
 emit(0x08,0x68)
 op(0x8d,0xc030)                    # saved P status including carry
 emit(0x68,0xaa)                    # PLA TAX restores loop index
 for i,a in enumerate(FIELDS):
  op(0xad,a)
  op(0x9d,OUTPUT+i*STRIDE)
 emit(0xe8,0xe0,COUNT,0xf0,0x03)
 op(0x4c,loop)
 stop=H+len(b)
 op(0x4c,stop)
 assert len(b)<0x300
 return bytes(b),stop
def command(sock,line,needle):
 sock.sendall((line+'\n').encode())
 data=b''
 for _ in range(160):
  try:
   part=sock.recv(16384)
   if not part:break
   data+=part
   if needle.encode() in data and data.endswith(b') '):return data
  except socket.timeout:continue
 raise RuntimeError((line,needle,data[-1100:].decode(errors='replace')))
def native(prg,p,op,tag,port,folder,exe):
 mem=machine_bytes(prg)
 code,stop=harness(API[op])
 mem[H:H+len(code)]=code
 operands=inputs()
 for i,(n,d) in enumerate(operands):
  for k in range(3):
   mem[INPUT+k*STRIDE+i]=(n>>(8*k))&255
   mem[INPUT+(3+k)*STRIDE+i]=(d>>(8*k))&255
 prog=folder/(tag+'.prg')
 dump=folder/(tag+'.dump')
 # Do not write into VIC registers at $D000: only RAM $0400..$CFFF.
 prog.write_bytes(bytes((INPUT&255,INPUT>>8))+mem[INPUT:0xd000])
 args=[str(exe),'-console','-silent','-sounddev','dummy','-warp',
   '-remotemonitor','-remotemonitoraddress',f'127.0.0.1:{port}',
   '-initbreak','reset']
 logfile=folder/(tag+'.log')
 with logfile.open('w') as log:
  proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
  try:
   sock=None
   for _ in range(180):
    try:
     sock=socket.create_connection(('127.0.0.1',port),timeout=0.15)
     break
    except (ConnectionRefusedError,TimeoutError):time.sleep(0.07)
   if sock is None:raise RuntimeError(('VICE monitor connection timeout',tag,logfile.read_text()[-1200:]))
   sock.settimeout(0.3)
   try:
    command(sock,'load "'+str(prog)+'" 0','Loading')
    command(sock,'break '+format(stop,'04x'),'BREAK:')
    command(sock,'g '+format(H,'04x'),'Stop on  exec')
    command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,'04x')+' '+
        format(OUTPUT+len(FIELDS)*STRIDE-1,'04x'),'Saving')
    sock.sendall(b'quit\n')
   finally:sock.close()
  finally:
   proc.terminate()
   try:proc.wait(timeout=3)
   except subprocess.TimeoutExpired:proc.kill()
 if not dump.exists():raise RuntimeError((tag,'no dump',logfile.read_text()[-1500:]))
 data=dump.read_bytes()
 assert len(data)==len(FIELDS)*STRIDE,(tag,len(data))
 results=[]
 for i,(n,d) in enumerate(operands):
  columns=[data[k*STRIDE+i] for k in range(len(FIELDS))]
  q=sum(columns[k]<<(8*k) for k in range(3))
  r=sum(columns[4+k]<<(8*k) for k in range(3))
  q3,r3=columns[3],columns[7]
  out_n=sum(columns[8+k]<<(8*k) for k in range(3))
  out_d=sum(columns[11+k]<<(8*k) for k in range(3))
  carry=columns[14]&1
  wantq=0 if d==0 else n//d
  wantr=0 if d==0 else n%d
  check_q=op=='MATH_UDIV24' or p=='v1_balanced'
  assert (r,carry,out_n,out_d,r3)==(wantr,int(d==0),n,d,0x82),(tag,i,hex(n),hex(d),'R/C/N/D/R3',columns)
  if check_q:assert q==wantq,(tag,i,'Q',q,wantq)
  results.append((q,r,carry,out_n,out_d,r3))
 return {'source':tag,'operand_count':COUNT,'input_sha256':sha(json.dumps(operands,separators=(',',':')).encode()),
 'outputs_sha256':sha(data),'results':results,'uncontracted_Q3_observed':True}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--out',type=Path)
 ap.add_argument('--smoke-profile',choices=PROFILES)
 ap.add_argument('--smoke-operation',choices=OPS)
 a=ap.parse_args()
 binary=os.environ.get('VICE_WRAPPER')
 assert binary and Path(binary).is_file(),('Set VICE_WRAPPER to a native x64sc binary/wrapper',binary)
 rawstatus=json.loads((ROOT/'RELEASE_STATUS.json').read_text())['issue39_u24_txa_production_source_2026_10_13']
 rows=[]
 with tempfile.TemporaryDirectory(prefix='issue39_u24_vice_') as scratch:
  folder=Path(scratch)
  index=0
  for profile in ([a.smoke_profile] if a.smoke_profile else PROFILES):
   path=f'{profile}/resident/math_{profile}_game_math.prg'
   current=(ROOT/path).read_bytes()
   old=subprocess.run(['git','show',PARENT+':'+path],cwd=ROOT,check=True,capture_output=True).stdout
   assert sha(old)==rawstatus['before_reference_sha256'][profile]
   assert sha(current)==rawstatus['after_reference_sha256'][profile]
   for op in ([a.smoke_operation] if a.smoke_operation else OPS):
    # Both baseline and candidate are executed in actual x64sc; compare promised
    # public Q (if applicable), R, carry, N/D, upper R and clean exit.
    oldrow=native(old,profile,op,'old_'+profile+'_'+op,7600+index*2,folder,binary)
    newrow=native(current,profile,op,'new_'+profile+'_'+op,7601+index*2,folder,binary)
    check_q=(op==OPS[0] or profile==PROFILES[0])
    differences=0
    for before,after in zip(oldrow['results'],newrow['results']):
     assert before[1:]==after[1:],(profile,op,'R/C/owned ABI diff',before,after)
     if check_q:assert before[0]==after[0],(profile,op,'Q diff',before,after)
     differences+=before[0]!=after[0]
    rows.append({'profile':profile,'operation':op,'native_old_calls':COUNT,
        'native_new_calls':COUNT,'native_total_calls':COUNT*2,
        'unpromised_quotient_side_effect_differences':differences,
        'old_output_sha256':oldrow['outputs_sha256'],
        'new_output_sha256':newrow['outputs_sha256'],
        'operand_sha256':newrow['input_sha256'],
        'old_resident_sha256':sha(old),'new_resident_sha256':sha(current)})
    print('NATIVE VICE PUBLIC RESIDENT PASS',profile,op,COUNT*2,'old+new',flush=True)
    index+=1
 assert len(rows)==(1 if a.smoke_profile else len(PROFILES))*(1 if a.smoke_operation else len(OPS))
 report={'status':'PASS_NATIVE_VICE_OLD_NEW_FULL_RESIDENT','tested_utc':'2026-10-13',
   'backend':'native VICE x64sc; actual 6510/VIC execution, not Python mini6502',
   'native_cycles_claimed':False,
   'native_full_resident_calls':sum(x['native_total_calls'] for x in rows),
   'cases_per_image_per_api':COUNT,'rows':rows,
   'parent_commit':PARENT,
   'running_vice_path':str(binary),
   'note':'No physical cycle/performance measurement. REU transport timing not exercised: UDIV24/UMOD24 are CPU kernels.'}
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 NATIVE VICE SOURCE-INTEGRATED U24 SUCCESS',report['native_full_resident_calls'],flush=True)
if __name__=='__main__':main()
