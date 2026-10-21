#!/usr/bin/env python3
"""Guard current operation-first performance charts against numeric/source drift.

The assertions check verbatim source rows and arithmetic; they do NOT pretend
to rerun native VICE or infer cycles for otherwise unbenchmarked applications.
"""
from __future__ import annotations

import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "PERFORMANCE.md"
ARCHIVE = ROOT / "docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md"
SOURCES = (
    ("docs/SEVEN_CROSS_FRAME_PRODUCTION.md",
     "The particularly useful new alternatives are:", 4),
    ("docs/D65536_FRAME_CHOICES.md", "## Workload-specific result", 3),
    ("docs/NATIVE_INSTALLED_D65536_PAL.md",
     "## Verified pinned native results", 3),
)


def source_table(path: str, marker: str) -> list[str]:
    content = (ROOT / path).read_text(encoding="utf-8")
    if marker not in content:
        raise AssertionError(f"Source marker absent: {path}: {marker}")
    lines = content.split(marker, 1)[1].splitlines()
    first = next((i for i, line in enumerate(lines) if line.startswith("|")), None)
    if first is None:
        raise AssertionError(f"No Markdown table in {path}")
    result = []
    for line in lines[first:]:
        if not line.startswith("|"):
            break
        result.append(line)
    return result


def number(value: str) -> int:
    return int(re.sub(r"[^\d-]", "", value.replace("\N{MINUS SIGN}", "-")))


def cells(line: str) -> list[str]:
    return [entry.strip().replace("**", "") for entry in line.strip().strip("|").split("|")]


class OperationFirstPerformanceCharts(unittest.TestCase):
    def test_tables_are_verbatim_verified_source_rows(self):
        current = CURRENT.read_text(encoding="utf-8")
        for path, marker, count in SOURCES:
            with self.subTest(source=path):
                source = source_table(path, marker)
                self.assertEqual(len(source), count + 2)
                self.assertEqual(current.count("\n".join(source)), 1)

    def test_native_pal_margins_and_public_claims(self):
        current = CURRENT.read_text(encoding="utf-8")
        rows = source_table(*SOURCES[2][:2])[2:]
        measured = [cells(row) for row in rows]
        self.assertEqual(len(measured), 3)
        for row in measured:
            self.assertEqual(19656 - number(row[1]), number(row[2]))
        self.assertEqual(number(measured[0][1]) - number(measured[2][1]), 2303)
        self.assertEqual(number(measured[1][1]) - number(measured[2][1]), 38)
        self.assertEqual(number(measured[0][3]), number(measured[2][3]))
        self.assertIn("**2,303 native slots**", current)

    def test_source_model_peak_and_memory_differences(self):
        rows = [cells(row) for row in source_table(*SOURCES[1][:2])[2:]]
        self.assertEqual(number(rows[0][1]) - number(rows[2][1]), 2323)
        self.assertEqual(number(rows[1][1]) - number(rows[2][1]), 48)
        self.assertEqual(number(rows[1][2]) - number(rows[2][2]), 221)
        self.assertEqual(number(rows[0][2]), number(rows[2][2]))
        self.assertEqual(number(rows[0][3]), 31)

    def test_historical_tables_are_archived_not_current(self):
        self.assertIn("## Shipped profile means", ARCHIVE.read_text(encoding="utf-8"))
        current = CURRENT.read_text(encoding="utf-8")
        self.assertNotIn("## Shipped profile means", current)
        self.assertIn("cycle_model_benchmark", current)
        self.assertIn("not directly interchangeable", current)


if __name__ == "__main__":
    unittest.main()
