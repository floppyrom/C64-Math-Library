#!/usr/bin/env python3
"""Issue144 V4 ISQRT32 masked-three-rotate: paired 6510 and real 16MiB REU VICE qualification."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json, math, os, random, shutil, socket, statistics, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,Assembler
P='v4_reu_16m'
MODULE='relocatable_source/v4_reu_16m/isqrt32_reu_prefix.asm'
OPT='optional/issue144_v4_reu_isqrt_maskshift/v4_reu_16m.asm'
BASELINE='optional/issue144_v4_reu_isqrt_maskshift/prepromotion_fastfour_v4_reu.asm'
REU='v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'
E=[0,1,2,3,4,7,15,16,17,255,256,257,32767,65535,65536,65537,0x12345678,0x7fffffff,0x80000000,0x80000001,0xbaddcafe,0xfffffffd,0xfffffffe,0xffffffff]

def build(r,layout,dst):
    args=[sys.executable,str(r/'tools/assemble_sources.py'),'--profile',P,'--config-kind',layout,'--out',str(dst)]
    subprocess.run(args,cwd=r,capture_output=True,text=True,check=True)
    path=dst/layout/P/('math_'+P+'_source_built.prg')
    assert path.is_file(),path
    return path

def machine(prg,reu):
    raw=prg.read_bytes()
    assert int.from_bytes(raw[:2],'little')==0x1000
    mem=bytearray(65536)
    mem[0x1000:0x1000+len(raw)-2]=raw[2:]
    cpu=CPU(mem,reu=bytearray(reu))
    cpu.d=0
    cpu.call(0x3280,2000000)
    return cpu

def call(c,n):
    for i in range(4):c.mem[0xc010+i]=(n>>(8*i))&255
    inp=bytes(c.mem[0xc010:0xc014]);sp=c.sp
    cycles=c.call(0x5e30,2000000)
    assert bytes(c.mem[0xc010:0xc014])==inp and c.sp==sp
    return (int.from_bytes(c.mem[0xc008:0xc00a],'little'),cycles,
            (c.c,c.n,c.z,c.v,c.a,c.x,c.y,c.d,c.sp),bytes(c.mem[0x54:0x5c]))

def model(a,b,reu):
    base=machine(a,reu);cand=machine(b,reu)
    nums=list(E)
    for n in (0,1,2,3,31,63,127,255,256,511,1023,1024,8191,16383,32767,65535):
        for j in (n*n-1,n*n,n*n+1):
            if 0<=j<=0xffffffff:nums.append(j)
    rnd=random.Random(0x1444a66)
    nums+= [rnd.getrandbits(32) for _ in range(2048)]
    nums=list(dict.fromkeys(nums))
    gains=[];vdiff=0
    for n in nums:
        old=call(base,n);new=call(cand,n)
        assert old[0]==new[0]==math.isqrt(n),(hex(n),old[0],new[0])
        assert old[2][:3]==new[2][:3] and old[2][4:]==new[2][4:] and old[3]==new[3],hex(n)
        vdiff+=old[2][3]!=new[2][3]
        gains.append(old[1]-new[1])
    assert gains and min(gains)>0
    return {'status':'PASS','calls':len(nums),'mean_saved':statistics.mean(gains),
            'min_saved':min(gains),'p95_saved':sorted(gains)[int(.95*(len(gains)-1))],
            'slower_calls':sum(x<0 for x in gains),'volatile_V_differences':vdiff,
            'input_sha256':hashlib.sha256(b''.join(n.to_bytes(4,'little') for n in nums)).hexdigest()}

def command(s,msg,marker):
    s.sendall((msg+'\n').encode());data=b''
    for _ in range(160):
        try:
            part=s.recv(16384)
            if not part:break
            data+=part
            if marker.encode() in data and data.endswith(b') '):return
        except socket.timeout:pass
    raise RuntimeError((msg,data[-500:]))

def native(vice,prg,reu,port,temp):
    raw=prg.read_bytes();mem=bytearray(65536)
    mem[0x1000:0x1000+len(raw)-2]=raw[2:]
    asm=['!cpu 6510','* = $0B00','sei','cld','ldx #$FF','txs','lda #$35','sta $01',
         'jsr $3280','ldx #$00','loop:']
    for k in range(4):
        asm+=['lda $'+format(0x0400+k*64,'04X')+',x',
              'sta $'+format(0xC010+k,'04X')]
    asm+=['txa','pha','jsr $5E30','php','pla','sta $C030','pla','tax','lda $C030','sta $0780,x']
    for k in range(2):asm+=['lda $'+format(0xc008+k,'04X'),'sta $'+format(0x0700+k*64,'04X')+',x']
    asm+=['inx','cpx #$18','beq done','jmp loop','done: jmp done']
    code,labels,_=Assembler().assemble('\n'.join(asm)+'\n')
    assert max(code)<0x0C00
    for addr,value in code.items():mem[addr]=value
    for i,n in enumerate(E):
        for k in range(4):mem[0x0400+i+k*64]=(n>>(8*k))&255
    img=temp/('v4_%d.prg'%port);dump=temp/('v4_%d.dump'%port)
    img.write_bytes(bytes((0,4))+mem[0x0400:0xd000])
    cmd=[vice,'-default','-console','-silent','-sounddev','dummy','-warp','-remotemonitor',
         '-remotemonitoraddress','127.0.0.1:'+str(port),'-initbreak','reset',
         '-reu','-reusize','16384','-reuimage',str(reu)]
    with (temp/('v4_%d.log'%port)).open('w') as log:
        process=subprocess.Popen(cmd,cwd=temp,stdout=log,stderr=log)
        try:
            conn=None
            for _ in range(160):
                try:conn=socket.create_connection(('127.0.0.1',port),timeout=.25);break
                except OSError:time.sleep(.08)
            if conn is None:raise RuntimeError('VICE monitor unavailable')
            conn.settimeout(1)
            try:
                command(conn,'load "'+str(img)+'" 0','Loading')
                command(conn,'break '+format(labels['done'],'04x'),'BREAK:')
                command(conn,'g 0b00','Stop on  exec')
                command(conn,'bsave "'+str(dump)+'" 0 0700 07bf','Saving')
                conn.sendall(b'quit\n')
            finally:conn.close()
        finally:
            process.terminate()
            try:process.wait(timeout=4)
            except subprocess.TimeoutExpired:process.kill()
    output=dump.read_bytes()
    assert len(output)==192
    for i,n in enumerate(E):
        assert output[i]+256*output[64+i]==math.isqrt(n),(i,hex(n),output[i],output[64+i])
        assert output[128+i]&1==0
    return output

def main():
    assert (ROOT/REU).stat().st_size==16777216
    with TemporaryDirectory(prefix='issue144_v4_fast4_') as name:
        temp=Path(name);clone=temp/'checkout'
        shutil.copytree(ROOT,clone,ignore=shutil.ignore_patterns('.git','__pycache__','build_source'))
        file=clone/MODULE;integrated=file.read_text();optimized=(clone/OPT).read_text()
        baseline=(clone/BASELINE).read_text()
        old_shifts='    and #$03\n' + '    asl\n'*6
        new_shifts='    and #$03\n    lsr\n    ror\n    ror\n    and #$C0\n'
        assert baseline.count(old_shifts)==2, 'expected two original six-ASL sites'
        assert optimized==baseline.replace(old_shifts,new_shifts), 'only the two exact masked-shift sites may change'
        assert (clone/'optional/issue144_v4_isqrt32_direct_reu_zp/prepromotion_v4_reu.asm').read_text() == optimized, 'independent historical maskshift source changed'
        assert integrated == (clone/'optional/issue144_v4_isqrt32_direct_reu_zp/v4_reu_16m.asm').read_text(), 'canonical V4 differs from qualified direct-ZP promotion'
        assert 'lda #$91\n    sta $DF01' in baseline and 'lda #$91\n    sta $DF01' in integrated
        file.write_text(baseline)
        b_ref=build(clone,'reference',temp/'baseline')
        b_alt=build(clone,'alternate',temp/'baseline')
        # The historical maskshift proof must assemble its own independently
        # pinned candidate, not whichever newer root occupies canonical V4.
        file.write_text(optimized)
        c_ref=build(clone,'reference',temp/'candidate')
        c_alt=build(clone,'alternate',temp/'candidate')
        assert b_ref.stat().st_size==c_ref.stat().st_size
        assert b_alt.stat().st_size==c_alt.stat().st_size
        report={'status':'PASS','source_reference':True,'source_alternate':True,
                'model':model(b_ref,c_ref,(ROOT/REU).read_bytes()),
                'normal_prgs_and_reu_unchanged':True,'native':'not requested'}
        vice=os.environ.get('VICE_WRAPPER')
        if vice:
            a=native(vice,b_ref,ROOT/REU,20204,temp)
            b=native(vice,c_ref,ROOT/REU,20205,temp)
            assert a==b, 'native root and captured 8-bit status must be exactly equal'
            report['native']={'status':'PASS','calls':2*len(E),
                              'output_sha256':hashlib.sha256(a[:128]).hexdigest()}
        print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
