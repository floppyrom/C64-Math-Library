#!/usr/bin/env python3
"""Source geometry and exact ABI test for the research-only D=$00010000 path."""
from __future__ import annotations

import unittest

import selective_hybrid_u3232 as original_unsigned
import selective_signed_hybrid_u3232 as original_signed
import research_d65536_hybrid as candidate


class D65536ResearchTests(unittest.TestCase):
    def test_two_qualified_ram_and_zp_maps_preserve_entry_geometry(self):
        for code,io,zp in candidate.PLACEMENTS:
            with self.subTest(map=hex(code)):
                u,ue,ue_end=candidate.assemble_unsigned(code,io,zp)
                s,se,se_end=candidate.assemble_signed(code,io,zp)
                self.assertEqual(ue[original_unsigned.API_DIV],code+0x9a0)
                self.assertEqual(ue[original_unsigned.API_MOD],code+0x9a0)
                self.assertEqual(se[original_signed.PUBLIC_MOD],code+0xa20)
                self.assertEqual(se[original_signed.PUBLIC_DIV],code+0xa20)
                self.assertEqual(len(u),candidate.IMAGE_BYTES)
                self.assertEqual(len(s),candidate.SIGNED_IMAGE_BYTES)
                self.assertEqual(ue_end,code+candidate.IMAGE_BYTES)
                self.assertEqual(se_end,code+candidate.SIGNED_IMAGE_BYTES)

    def test_full_qr_c_inputs_and_source_immutability_across_boundary(self):
        cases=(
            (0x80000001,0x00010000),
            (0xffffffff,0x00010000),
            (0x80000000,0x00010000),
            (0x80000001,0xffff0000),
            (0x10000,0x10000),
            (0x10001,0x10000),
            (0x0000ffff,0x10000),
            (0,0x10000),
            (0xffffffff,0),
            (0xffffffff,1),
            (0xffffffff,0xffff),
            (0x10000001,0x10001),
            (0x80000001,0x80000000),
        )
        for code,io,zp in candidate.PLACEMENTS:
            for signed_mode in (False,True):
                with self.subTest(code=hex(code),signed=signed_mode):
                    if signed_mode:
                        image,entries,_=candidate.assemble_signed(code,io,zp)
                        old,old_entries,_,_=original_signed.assemble(code,io,zp)
                        label=original_signed.PUBLIC_MOD
                    else:
                        image,entries,_=candidate.assemble_unsigned(code,io,zp)
                        old,old_entries,_,_=original_unsigned.assemble(code,io,zp)
                        label=original_unsigned.API_MOD
                    measured=candidate.qualify_one(
                        image,entries[label],code,io,cases,signed_mode,name='candidate')
                    baseline=candidate.qualify_one(
                        old,old_entries[label],code,io,cases,signed_mode,name='old')
                    self.assertLess(measured[0],baseline[0])
                    self.assertEqual(len(measured),len(cases))
                    self.assertGreater(len(image),len(old))

    def test_only_12_zp_source_research_and_existing_donors_untouched(self):
        self.assertEqual(candidate.ZP_BYTES,12)
        self.assertEqual(candidate.IMAGE_BYTES-original_unsigned.IMAGE_BYTES,96)
        self.assertEqual(candidate.SIGNED_IMAGE_BYTES-original_signed.IMAGE_BYTES,96)
        self.assertEqual(candidate.FRAME8_SMOD,(0x80000001,0x10000))


if __name__ == '__main__':
    unittest.main()
