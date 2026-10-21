#!/usr/bin/env python3
"""Package boundary and DMA handshake tests; native VICE runs separately."""
import unittest
from mini6502 import CPU
import reu_turbo16_standalone_package as p

class StandaloneREUTests(unittest.TestCase):
    def test_512_and_16m_package_and_source_cpu_execution(self):
        for kb, bank in ((512,4),(16384,200)):
            with self.subTest(kb=kb,bank=bank):
                manifest, raw = p.build(kb,bank)
                self.assertEqual(raw[:2],bytes((0,0x30)))
                self.assertEqual(len(raw),p.LIMIT-p.BASE+2)
                self.assertFalse(manifest["reu_mode_selectable_in_operation_first_builder"])
                self.assertEqual(manifest["claimed_resources"]["reu_bank_exclusive"][0],bank*65536)
                self.assertEqual(manifest["claimed_resources"]["alias_guard_one_byte"],
                                 None if bank<8 else 65535)
                mem=bytearray(65536)
                mem[p.BASE:p.LIMIT]=raw[2:]
                mem[1]=0x35
                initial=bytes((i*73+19)&255 for i in range(122))
                mem[p.ZP:p.ZP+122]=initial
                cpu=CPU(mem,reu=bytearray(kb*1024))
                addr={k:int(v[1:],16) for k,v in manifest["public_exports"].items()}
                cpu.call(addr["T16_REU_CALL"])
                self.assertEqual(cpu.c,1)
                cpu.call(addr["T16_REU_BEGIN"])
                self.assertEqual(cpu.c,1)
                cpu.call(addr["T16_REU_INSTALL"],100000)
                self.assertEqual(cpu.c,0)
                self.assertEqual(cpu.mem[p.STATE+1],1)
                self.assertEqual(bytes(cpu.mem[p.ZP:p.ZP+122]),initial)
                for batch in range(2):
                    cpu.call(addr["T16_REU_BEGIN"],100000)
                    self.assertEqual(cpu.c,0)
                    for x,y in ((0x1234,0x5678),(0xffff,0xffff),(0,0)):
                        for offset in range(2):
                            cpu.mem[p.IO+offset]=x>>(8*offset)&255
                            cpu.mem[p.IO+4+offset]=y>>(8*offset)&255
                        cpu.call(addr["T16_REU_CALL"],100000)
                        result=sum(cpu.mem[p.IO+8+j]<<(8*j) for j in range(4))
                        self.assertEqual(result,x*y)
                        self.assertEqual(cpu.c,0)
                    cpu.call(addr["T16_REU_END"],100000)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(bytes(cpu.mem[p.ZP:p.ZP+122]),initial)

    def test_absent_reu_fails_closed_without_zp_damage(self):
        manifest,raw=p.build()
        mem=bytearray(65536)
        mem[p.BASE:p.LIMIT]=raw[2:]
        mem[1]=0x35
        initial=bytes(range(122))
        mem[p.ZP:p.ZP+122]=initial
        cpu=CPU(mem)
        addr={k:int(v[1:],16) for k,v in manifest["public_exports"].items()}
        cpu.call(addr["T16_REU_INSTALL"])
        self.assertEqual(cpu.c,1)
        self.assertEqual(cpu.mem[p.STATE+1],0)
        cpu.call(addr["T16_REU_BEGIN"])
        self.assertEqual(cpu.c,1)
        self.assertEqual(bytes(cpu.mem[p.ZP:p.ZP+122]),initial)

    def test_fail_closed_user_reservations(self):
        for kw in (dict(reserved_zp=[(0x40,0x41)]),
                   dict(reserved_ram=[(0x7200,0x7500)]),
                   dict(reserved_ram=[(0xc010,0xc010)]),
                   dict(reserved_reu_banks=[4]),
                   dict(reu_kib=512,bank=8),
                   dict(reu_kib=1024)):
            with self.subTest(kw=kw), self.assertRaises(p.PackageError):
                p.build(**kw)
        with self.assertRaisesRegex(p.PackageError,"mirror probe"):
            p.build(16384,200,reserved_reu_banks=[0])
        with self.assertRaisesRegex(p.PackageError,"overlay collision"):
            p.build(reserved_zp=[(0x00,0xff)])

    def test_source_package_deterministic(self):
        a,p1=p.build()
        b,p2=p.build()
        self.assertEqual(p1,p2)
        self.assertEqual(a,b)

if __name__=="__main__":
    unittest.main()
