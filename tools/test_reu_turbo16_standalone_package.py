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
                self.assertEqual(manifest["claimed_resources"]["alias_guard_bytes"],
                                 [] if bank<8 else [65535, 8*65536+65535, 72*65536+65535])
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
                   dict(reu_kib=1024),
                   dict(reserved_zp=[(0x100,0x120)]),
                   dict(reserved_zp=[(-1,0x10)]),
                   dict(reserved_ram=[(0xf000,0x10000)]),
                   dict(reserved_reu_banks=[8])):
            with self.subTest(kw=kw), self.assertRaises(p.PackageError):
                p.build(**kw)
        for mirror_bank in (0,8,72):
            with self.subTest(mirror_bank=mirror_bank), self.assertRaisesRegex(
                    p.PackageError,"mirror probe"):
                p.build(16384,200,reserved_reu_banks=[mirror_bank])
        with self.assertRaisesRegex(p.PackageError,"overlay collision"):
            p.build(reserved_zp=[(0x00,0xff)])


    def test_import_stock_builder_physical_occupancy_and_fail_closed(self):
        # A successful operation-first build can only coexist if its public
        # IO, ZP, scratch and source-built occupied code do not collide.
        stock = {
            "target":"c64", "operations":[{"api":"MATH_UMUL8"}],
            "resource_use":{
                "public_io_bytes":32, "private_ram_scratch_bytes":16,
                "zero_page_bytes":8
            },
            "memory_map":{
                "code_start":"$8000","code_end":"$8400",
                "math_io_start":"$C040","scratch_start":"$C060",
                "zp_start":"$C0","persistent_state":{},
                "user_reserved":[{"name":"game","start":"$9000","end":"$91FF"}],
                "user_zp_reserved":[{"name":"irq","start":"$02","end":"$1F"}]
            }
        }
        out, blob = p.build(stock_manifest=stock)
        self.assertEqual(out["stock_manifest_collision_check"],
                         "PASSED_FOR_REPORTED_RESOURCES")
        self.assertEqual(out["stock_selected_operations_checked"],1)
        self.assertTrue(blob)
        # Default stock public IO ($C000) always collides with standalone IO.
        import copy
        io_conflict=copy.deepcopy(stock)
        io_conflict["memory_map"]["math_io_start"]="$C000"
        with self.assertRaisesRegex(p.PackageError,"collision"):
            p.build(stock_manifest=io_conflict)
        zp_conflict=copy.deepcopy(stock)
        zp_conflict["memory_map"]["zp_start"]="$70"
        with self.assertRaisesRegex(p.PackageError,"overlay collision"):
            p.build(stock_manifest=zp_conflict)
        ram_conflict=copy.deepcopy(stock)
        ram_conflict["memory_map"]["code_start"]="$7100"
        ram_conflict["memory_map"]["code_end"]="$7300"
        with self.assertRaisesRegex(p.PackageError,"collision"):
            p.build(stock_manifest=ram_conflict)
        state_unqualified=copy.deepcopy(stock)
        state_unqualified["memory_map"]["persistent_state"]={"seek":"$A000"}
        with self.assertRaisesRegex(p.PackageError,"persistent state"):
            p.build(stock_manifest=state_unqualified)
        missing=copy.deepcopy(stock)
        del missing["memory_map"]["code_end"]
        with self.assertRaisesRegex(p.PackageError,"Incomplete"):
            p.build(stock_manifest=missing)
        with self.assertRaisesRegex(p.PackageError,"Expected"):
            p.build(stock_manifest={"target":"1541"})

    def test_source_package_deterministic(self):
        a,p1=p.build()
        b,p2=p.build()
        self.assertEqual(p1,p2)
        self.assertEqual(a,b)

if __name__=="__main__":
    unittest.main()
