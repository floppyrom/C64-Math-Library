#!/usr/bin/env python3
"""Source-locked *historical* self-modifying V1-V5 signed 8x8 tables.

511 bytes in each of four pages with one unused byte between consecutive
512-byte regions. Original source V1: $9C00/$9E00/$8800/$8A00.
V2-V4 use equivalent complement pages $6400/$6600; all bytes match.
Do not regenerate using floating point or silently compact/rearrange pages.
The companion kernel modifies ONLY its four abs,X operand low bytes in RAM.
"""
from __future__ import annotations

ENTRIES = 511
PAGE_STRIDE = 512
TABLE_COUNT = 4
ALIGNED_SPAN = PAGE_STRIDE * TABLE_COUNT
NAMES = ("LOW_SUM", "HIGH_SUM", "LOW_COMPLEMENT", "HIGH_COMPLEMENT")
TABLE_HEX = {
    "LOW_SUM": (
        "004a014c04500956105e196824743182409251a464b879ce90e6a900c41ce13a"
        "005a217c44a069c690eeb918e444117240a271d4a408d93e107649b084ecc12a"
        "006a41ac84f0c936107e59c8a414f16240b29104e45839ae9006e96044bca11a"
        "007a61dcc44029a6900ef97864e4d15240c2b13424a8991e10968910048c810a"
        "008a810c04908916109e992824b4b14240d2d16464f8f98e902629c0c45c61fa"
        "009aa13c44e0e986902e39d8e484913240e2f194a44859fe10b6c970842c41ea"
        "00aac16c843049f610bed988a454712240f211c4e498b96e9046692044fc21da"
        "00bae19cc480a966904e793864245112400231f424e819de10d609d004cc01ca"
        "00ca01cc04d009d610de19e824f43102401251246438794e9066a980c49ce1ba"
        "00da21fc44206946906eb998e4c411f240227154a488d9be10f64930846cc1aa"
        "00ea412c8470c9b610fe5948a494f1e240329184e4d8392e9086e9e0443ca19a"
        "00fa615cc4c02926908ef9f86464d1d24042b1b42428999e10168990040c818a"
        "000a818c04108996101e99a82434b1c24052d1e46478f90e90a62940c4dc617a"
        "001aa1bc4460e90690ae3958e40491b24062f114a4c8597e1036c9f084ac416a"
        "002ac1ec84b04976103ed908a4d471a240721144e418b9ee90c669a0447c215a"
        "003ae11cc400a9e690ce79b864a45192408231742468195e10560950044c01"
    ),
    "HIGH_SUM": (
        "40403f3f3e3e3d3d3c3c3b3b3a3a393938383737363635353434333432333132"
        "313130302f2f2e2e2d2d2c2d2b2c2b2b2a2a2929282927282727262625252425"
        "2424232322222122212120201f201e1f1e1e1d1e1c1d1c1c1b1c1a1b1a1a191a"
        "1919181817181717161715161515141514141314131312131212111211111011"
        "10100f100f0f0e0f0e0e0d0e0d0d0c0d0c0c0b0c0b0b0a0b0a0b0a0a090a0909"
        "0909080908080708070807070607060706060506050605050505040504050404"
        "0404030403040303030302030203020302020202010201020102010201010101"
        "0101000100010001000100010001000100010000000000000000000000000000"
        "0000000000000000000000000000000100010001000100010001000100010001"
        "0101010101020102010201020102020202030203020302030303030403040304"
        "0404040504050405050505060506050606070607060707080708070808090809"
        "0909090a090a0a0b0a0b0a0b0b0c0b0c0c0d0c0d0d0e0d0e0e0f0e0f0f100f10"
        "1011101111121112121312131314131414151415151615171617171817181819"
        "191a191a1a1b1a1c1b1c1c1d1c1e1d1e1e1f1e201f2020212122212222232324"
        "2425242525262627272827292829292a2a2b2b2c2b2d2c2d2d2e2e2f2f303031"
        "313231333234333434353536363737383839393a3a3b3b3c3c3d3d3e3e3f3f"
    ),
    "LOW_COMPLEMENT": (
        "b5feb3fbaff6a9efa1e697db8bce7dbf6dae5b9b4786316f1956ff3be31ec5ff"
        "a5de83bb5f96396f1146e71bbbee8dbf5d8e2b5bf726c1ef89b64f7b133ed5ff"
        "95be537b0f36c9ef81a6375beb0e9dbf4d6efb1ba7c6516ff9169fbb435ee5ff"
        "859e233bbfd6596ff106879b1b2eadbf3d4ecbdb5766e1ef6976effb737ef5ff"
        "757ef3fb6f76e9ef6166d7db4b4ebdbf2d2e9b9b0706716fd9d63f3ba39e05ff"
        "655ec3bb1f16796fd1c6271b7b6ecdbf1d0e6b5bb7a601ef49368f7bd3be15ff"
        "553e937bcfb609ef4126775bab8eddbf0dee3b1b6746916fb996dfbb03de25ff"
        "451e633b7f56996fb186c79bdbaeedbffdce0bdb17e621ef29f62ffb33fe35ff"
        "35fe33fb2ff629ef21e617db0bcefdbfedaedb9bc786b16f99567f3b631e45ff"
        "25de03bbdf96b96f9146671b3bee0dbfdd8eab5b772641ef09b6cf7b933e55ff"
        "15bed37b8f3649ef01a6b75b6b0e1dbfcd6e7b1b27c6d16f79161fbbc35e65ff"
        "059ea33b3fd6d96f7106079b9b2e2dbfbd4e4bdbd76661efe9766ffbf37e75ff"
        "f57e73fbef7669efe16657dbcb4e3dbfad2e1b9b8706f16f59d6bf3b239e85ff"
        "e55e43bb9f16f96f51c6a71bfb6e4dbf9d0eeb5b37a681efc9360f7b53be95ff"
        "d53e137b4fb689efc126f75b2b8e5dbf8deebb1be746116f39965fbb83dea5ff"
        "c51ee33bff56196f3186479b5bae6dbf7dce8bdb97e6a1efa9f6affbb3feb5"
    ),
    "HIGH_COMPLEMENT": (
        "bfc0c0c1c1c2c2c3c3c4c4c5c5c6c6c7c7c8c8c9c9cacacbcbcccbcdcccecdce"
        "cecfcfd0d0d1d1d2d2d3d2d4d3d4d4d5d5d6d6d7d6d8d7d8d8d9d9dadadbdadb"
        "dbdcdcdddddedddededfdfe0dfe1e0e1e1e2e1e3e2e3e3e4e3e5e4e5e5e6e5e6"
        "e6e7e7e8e7e8e8e9e8eae9eaeaebeaebebecebececedecededeeedeeeeefeeef"
        "eff0eff0f0f1f0f1f1f2f1f2f2f3f2f3f3f4f3f4f4f5f4f5f4f5f5f6f5f6f6f6"
        "f6f7f6f7f7f8f7f8f7f8f8f9f8f9f8f9f9faf9faf9fafafafafbfafbfafbfbfb"
        "fbfcfbfcfbfcfcfcfcfdfcfdfcfdfcfdfdfdfdfefdfefdfefdfefdfefefefefe"
        "fefffefffefffefffefffefffefffefffeffffffffffffffffffffffffffffff"
        "fffffffffffffffffffffffffffffefffefffefffefffefffefffefffefffefe"
        "fefefefefdfefdfefdfefdfefdfdfdfdfcfdfcfdfcfdfcfcfcfcfbfcfbfcfbfb"
        "fbfbfafbfafbfafafafaf9faf9faf9f9f8f9f8f9f8f8f7f8f7f8f7f7f6f7f6f6"
        "f6f6f5f6f5f5f4f5f4f5f4f4f3f4f3f3f2f3f2f2f1f2f1f1f0f1f0f0eff0efef"
        "eeefeeeeedeeededecedececebecebebeaebeaeae9eae8e9e8e8e7e8e7e7e6e6"
        "e5e6e5e5e4e5e3e4e3e3e2e3e1e2e1e1e0e1dfe0dfdfdededddedddddcdcdbdb"
        "dadbdadad9d9d8d8d7d8d6d7d6d6d5d5d4d4d3d4d2d3d2d2d1d1d0d0cfcfcece"
        "cdcecccdcbcccbcbcacac9c9c8c8c7c7c6c6c5c5c4c4c3c3c2c2c1c1c0c0bf"
    ),
}
TABLES = {name: bytes.fromhex("".join(TABLE_HEX[name])) for name in NAMES}
assert all(len(TABLES[name]) == ENTRIES for name in NAMES)


def align_page(n: int) -> int:
    return (n + 255) & ~255


def emit(base: int):
    """Emit exact shared immutable pages; leave four 1-byte holes unowned."""
    if base & 255 or base < 0 or base + ALIGNED_SPAN > 65536:
        raise ValueError("SMUL8 tables require aligned four-page pairs in RAM")
    return {base + block*PAGE_STRIDE + i: value
            for block, name in enumerate(NAMES)
            for i, value in enumerate(TABLES[name])}


def digest_data():
    return b"".join(TABLES[name] for name in NAMES)


def signed_reference(x: int, y: int) -> int:
    xx = x if x < 128 else x-256
    yy = y if y < 128 else y-256
    return (xx*yy) & 0xffff


def original_table_math(x: int, y: int) -> int:
    """Exact original V1 ADC-with-carry pipeline, used to audit data parity."""
    left = (x ^ 0x80) + (y ^ 0x80)
    right = ((x ^ 0x80) ^ 0xff) + (y ^ 0x80)
    lo = TABLES["LOW_SUM"][left] + TABLES["LOW_COMPLEMENT"][right] + 1
    hi = TABLES["HIGH_SUM"][left] + TABLES["HIGH_COMPLEMENT"][right] + (lo >> 8)
    return (lo & 255) | ((hi & 255) << 8)
