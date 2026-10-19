#!/usr/bin/env python3
"""Native-pinned config preparatory checks without needing local VICE."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from native_frame_qualified_config import (
    CHOICES, LOCATIONS, ORACLES, N, build_native_cases, check_cli_exact_image,
)


class NativeFrameInstallerContractTests(unittest.TestCase):
    def test_all_four_qualified_configs_rebuild_exact_prgs(self):
        result = list(build_native_cases())
        self.assertEqual(len(result), len(CHOICES)*len(LOCATIONS))
        hashes = set()
        for i, cfg, proof in result:
            with self.subTest(code=hex(cfg["memory"]["code_base"]),
                              choice=proof["selection"]["objective"]), \
                 tempfile.TemporaryDirectory() as td:
                image, entries, digest = check_cli_exact_image(cfg, proof, Path(td))
                self.assertEqual(digest, hashlib.sha256(image).hexdigest())
                self.assertEqual(set(entries), {api for api,_ in ORACLES})
                self.assertEqual(cfg["memory"]["scratch_base"],
                                 cfg["memory"]["math_io"]+0x40)
                self.assertFalse(proof["physical_pal_feasibility_claim"])
                hashes.add(digest)
        self.assertEqual(len(hashes), 4)

    def test_native_oracle_contract(self):
        self.assertEqual(N, 96)
        self.assertEqual(len(ORACLES), 3)
        self.assertEqual({x[0] for x in ORACLES},
                         {"MATH_UMUL32","MATH_SMUL32","MATH_ISQRT16"})


if __name__ == "__main__":
    unittest.main()
