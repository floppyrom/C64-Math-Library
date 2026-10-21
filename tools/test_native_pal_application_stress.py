#!/usr/bin/env python3
"""Fail-closed source, table, RAM map and output-oracle tests for Issue #367."""
from __future__ import annotations

import hashlib
import unittest

import mixed_seven_frame_parity as seven
import native_pal_consecutive_application as previous
import native_pal_application_stress as stress


class NativeRealWorkTests(unittest.TestCase):
    def setUp(self):
        self.entries={api:0x4123+0x20*i for i,api in enumerate(seven.OPS)}

    def test_sid_player_has_twelve_distinct_real_register_and_shadow_stores(self):
        self.assertEqual(len(stress.STREAMS),12)
        self.assertLess(stress.HANDLER+len(stress.PLAYER),stress.RENDER)
        self.assertEqual(len({stream["sid_register"] for stream in stress.STREAMS}),12)
        self.assertTrue(stress.PLAYER.startswith(bytes((0x48,0x8a,0x48,0x98,0x48))))
        self.assertIn(bytes((0x68,0xa8,0x68,0xaa,0x68,0x40)),stress.PLAYER)
        sound_registers={0xd400,0xd401,0xd404,0xd407,0xd408,0xd40b,
                         0xd40e,0xd40f,0xd412,0xd416,0xd417,0xd418}
        self.assertEqual({row["sid_register"] for row in stress.STREAMS},
                         sound_registers)
        for i,stream in enumerate(stress.STREAMS):
            self.assertEqual(stream["shadow_address"],stress.PLAYER_SHADOW+i)
            self.assertEqual(len(stream["values"]),8)
            self.assertGreater(len(set(stream["values"])),1)
            ptr=stream["table_address"]-stress.HANDLER
            self.assertEqual(stress.PLAYER[ptr:ptr+8],bytes(stream["values"]))
            self.assertIn(
                bytes((0x8d,))+stress.word(stream["sid_register"])+
                bytes((0x8d,))+stress.word(stream["shadow_address"]),
                stress.PLAYER)

    def test_renderer_writes_and_reads_actual_screen_colour_cells(self):
        for rows in stress.LEVELS:
            with self.subTest(rows=rows):
                render=stress.render_rows(rows)
                self.assertLess(stress.RENDER+len(render),previous.SUB)
                self.assertEqual(render[:2],bytes((0xa2,0x0f)))
                self.assertTrue(render.endswith(bytes((0xee,0x01,0x3a,0x60))))
                for row in range(rows):
                    self.assertIn(bytes((0x9d,))+
                                  stress.word(0x0400+40*row),render)
                for row in range(0,rows,2):
                    self.assertIn(bytes((0x9d,))+
                                  stress.word(0xd800+40*row),render)

    def test_source_call_bodies_original_oracle_and_ram_regions_unchanged(self):
        for display in (False,True):
            original,old_halt,old_output,old_geo=previous.build_harness(
                self.entries,display=display)
            for rows in stress.LEVELS:
                with self.subTest(display=display,rows=rows):
                    blob,halt,outputs,geo=stress.build_harness(
                        self.entries,display=display,rows=rows)
                    self.assertEqual(outputs,old_output)
                    self.assertEqual(halt,stress.HALT)
                    self.assertEqual(geo["original_halt"],old_halt)
                    self.assertEqual(geo["source_public_calls"],150)
                    self.assertEqual(geo["source_frames"],24)
                    self.assertEqual(geo["rendered_character_cells_per_frame"],
                                     rows*16)
                    self.assertEqual(geo["rendered_color_cells_per_frame"],
                                     ((rows+1)//2)*16)
                    self.assertEqual(geo["sid_shadow_cells_verified_at_exit"],12)
                    self.assertEqual(
                        blob[old_halt-stress.MAIN:old_halt-stress.MAIN+3],
                        bytes((0x4c,))+stress.word(stress.VERIFY))
                    self.assertEqual(
                        blob[halt-stress.MAIN:halt-stress.MAIN+3],
                        bytes((0x4c,))+stress.word(halt))
                    self.assertLess(stress.VERIFY+geo["native_readback_oracle_bytes"],
                                    halt)
                    self.assertEqual(blob[stress.HANDLER-stress.MAIN:
                                          stress.HANDLER-stress.MAIN+
                                          len(stress.PLAYER)],stress.PLAYER)
                    self.assertEqual(blob[stress.RENDER-stress.MAIN:
                                          stress.RENDER-stress.MAIN+
                                          len(stress.render_rows(rows))],
                                     stress.render_rows(rows))
                    # Retain each original frame's exact staged operands,
                    # full public JSR/carry captures and benchmark SHA.
                    self.assertEqual(
                        geo["body_sha256_by_frame"],
                        old_geo["body_sha256_by_frame"])
                    for frame,addr in enumerate(geo["body_addresses"]):
                        original_source=previous.extract_frame(
                            self.entries,frame,display)[3]
                        offset=addr-stress.MAIN
                        self.assertEqual(
                            blob[offset:offset+len(original_source)],
                            original_source)
                    self.assertEqual(
                        geo["oracle_sha256"],old_geo["oracle_sha256"])

    def test_no_nops_no_unregistered_load_no_invalid_inputs(self):
        for reserve in (2,-1,False,True,"0",None,0.0):
            with self.subTest(reserve=reserve),self.assertRaises(ValueError):
                stress.build_harness(
                    self.entries,display=True,reserve_cpu_cycles=reserve)
        for rows in (0,1,3,5,6,24,-4,4.0,True,"4"):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                stress.build_harness(self.entries,display=True,rows=rows)
        for rows in ((),(8,4),(4,4),(4,5),(4,True)):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                stress.run("not-a-file",rows)

    def test_native_final_oracle_contains_shadow_and_live_screen_checks(self):
        blob,halt,_,geo=stress.build_harness(
            self.entries,display=True,rows=16)
        begin=stress.VERIFY-stress.MAIN
        end=begin+geo["native_readback_oracle_bytes"]
        code=blob[begin:end]
        for source in stress.STREAMS:
            self.assertIn(bytes((0xbd,))+
                          stress.word(source["table_address"]),code)
            self.assertIn(bytes((0xcd,))+
                          stress.word(source["shadow_address"]),code)
        for addr in (0x0400,0x040f,0x0400+40*15+15,
                     0xd800,0xd80f,0xd800+40*14+15):
            self.assertIn(bytes((0xcd,))+stress.word(addr),code)
        self.assertEqual(code[-3:],bytes((0x4c,))+stress.word(halt))
        self.assertIn(bytes((0xee,))+stress.word(previous.ERRORS_ADDR),code)


if __name__=="__main__":
    unittest.main()
