#!/usr/bin/env python3
"""Fast CPU-side assembly, contract and timing-pair regressions for PAL REU."""
from __future__ import annotations
import unittest
from unittest.mock import patch

import native_reu_pal_irq_dma as pal
import reu_turbo16_standalone_package as package


class NativePALREUContracts(unittest.TestCase):
    def test_eight_real_source_assembled_segregated_irq_variants(self):
        for tier,bank in ((512,4),(16384,200)):
            manifest,_=package.build(tier,bank)
            for display in (False,True):
                for irq in (False,True):
                    with self.subTest(tier=tier,display=display,irq=irq):
                        # Address 0x8000 stands for an actual qualified stock
                        # public entry; runtime checks resolve the exact export.
                        memory,halt,seed=pal.assemble(
                            manifest["public_exports"],0x8000,0xc040,
                            display=display,irq=irq)
                        self.assertLess(halt,pal.IRQ)
                        self.assertIn(pal.IRQ,memory)
                        self.assertIn(pal.NMI_GUARD,memory)
                        self.assertTrue(all(pal.HARNESS<=addr<pal.IRQ or
                                            pal.IRQ<=addr<pal.IRQ+256 or
                                            pal.NMI_GUARD<=addr<pal.NMI_GUARD+256
                                            for addr in memory))
                        self.assertEqual(len(seed),122)
                        # Hardware handler saves/restores registers and
                        # never reads/writes the executable $3E-$B7 ZP.
                        op=bytes(memory[p] for p in range(pal.IRQ,
                            max(k for k in memory if pal.IRQ<=k<pal.NMI_GUARD)+1))
                        self.assertTrue(op.startswith(bytes((0x48,0x8a,0x48,0x98,0x48))))
                        self.assertTrue(op.endswith(bytes((0x68,0xa8,0x68,0xaa,0x68,0x40))))
                        self.assertNotIn(bytes((0x85,0x3e)),op)
                        # CIA2 timeout handler is a diagnostic bailout only.
                        nmi=bytes(memory[p] for p in range(pal.NMI_GUARD,
                            max(k for k in memory if k>=pal.NMI_GUARD)+1))
                        self.assertIn(bytes((0xa9,0xdd,0x8d,0x07,0x1a)),nmi)
                        self.assertTrue(nmi.endswith(bytes((0x4c,
                            halt&255,(halt>>8)&255))))

    def test_unqualified_emulator_modes_cannot_pass_full_matrix(self):
        for args in (["--warp"],["--monitor-start","goto"],
                     ["--warp","--monitor-start","goto"]):
            with self.subTest(args=args),patch(
                    "sys.argv",["native_reu_pal_irq_dma.py","--out","discard.json"]+args):
                with self.assertRaises(SystemExit) as raised:
                    pal.main()
                self.assertEqual(raised.exception.code,2)

    def test_experimental_basic_matrix_remains_distinct_from_release_gate(self):
        from unittest.mock import patch
        invalid=[
            ["--basic-matrix"],
            ["--basic-matrix","--launch-mode","monitor"],
            ["--basic-matrix","--launch-mode","basic-autostart","--warp"],
            ["--basic-matrix","--launch-mode","basic-autostart","--only-case","reu_16384_display0_irq1"],
            ["--basic-matrix","--launch-mode","basic-autostart","--monitor-start","goto"],
        ]
        for args in invalid:
            with self.subTest(args=args),patch(
                    "sys.argv",["native_reu_pal_irq_dma.py","--out","ignore.json"]+args):
                with self.assertRaises(SystemExit) as err:
                    pal.main()
                self.assertEqual(err.exception.code,2)

    def test_paired_matrix_fails_closed(self):
        with self.assertRaises(AssertionError):
            pal.summarize([])
        base={
            "source_stock_prg_sha256":"stock","source_reu_prg_sha256":"reu",
            "raster_interrupts_serviced":1
        }
        rows=[]
        for tier in (512,16384):
            for display in (False,True):
                for irq in (False,True):
                    rows.append({**base,"tier_kib":tier,
                        "display_enabled":display,"raster_irq_enabled":irq,
                        "native_cia_phi2_slots":10000+(500 if irq else 0)})
        self.assertEqual(set(pal.summarize(rows)),{"512","16384"})
        for row in rows:
            if row["raster_irq_enabled"]:
                row["native_cia_phi2_slots"]=999
                break
        with self.assertRaises(AssertionError):
            pal.summarize(rows)


if __name__=="__main__":unittest.main()
