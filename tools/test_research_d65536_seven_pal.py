#!/usr/bin/env python3
"""Keep the research-only seven-API source injection isolated from stock modules."""
from __future__ import annotations

import copy
import hashlib
import tempfile
from pathlib import Path
import unittest

import selective_linker as linker
import research_d65536_seven_pal as research


class ResearchSevenPALTests(unittest.TestCase):
    def test_optin_source_assembles_correct_geometry_and_restores_registry(self):
        before={api:copy.deepcopy(linker.MODULES[api][variant])
                for api,variant in research.PAIRED.items()}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            old=root/"stock"
            new=root/"research"
            old.mkdir()
            new.mkdir()
            baseline, original_entries, baseproof=research.research_source_image(
                old,use_candidate=False)
            image, entries, proof=research.research_source_image(new)
        self.assertEqual(baseproof["zero_page_bytes"],proof["zero_page_bytes"])
        producer_extra=2*(research.research.IMAGE_BYTES-
                          research.research.OLD_UNSIGNED_BYTES)
        linked_extra=proof["main_ram_bytes"]-baseproof["main_ram_bytes"]
        self.assertEqual(producer_extra,192)
        self.assertEqual(linked_extra,len(image)-len(baseline))
        self.assertGreaterEqual(linked_extra,producer_extra)
        self.assertLess(linked_extra,producer_extra+256)
        self.assertEqual(set(entries),set(original_entries))
        self.assertFalse(baseproof["research_only_with_temporarily_injected_source_emitters"])
        after={api:copy.deepcopy(linker.MODULES[api][variant])
               for api,variant in research.PAIRED.items()}
        self.assertEqual(before,after)
        self.assertEqual(set(entries),set(research.OPS))
        self.assertEqual(image[:2],research.CODE.to_bytes(2,"little"))
        self.assertLess(research.CODE+len(image)-2,research.cia.HARNESS)
        self.assertEqual(proof["zero_page_bytes"],31)
        self.assertFalse(proof["production_builder_source_qualified"])
        self.assertTrue(proof["research_only_with_temporarily_injected_source_emitters"])
        self.assertEqual(proof["research_linked_prg_sha256"],hashlib.sha256(image).hexdigest())

    def test_research_frame_selection_does_not_accept_unqualified_index(self):
        with self.assertRaises(ValueError):
            research.run("",(24,))
        with self.assertRaises(ValueError):
            research.run("",(True,))


if __name__=="__main__":
    unittest.main()
