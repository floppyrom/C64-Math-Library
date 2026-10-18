# Follow-up: shared biased quarter-square SMUL24 fast entry

This draft experiment adds a signed full-public X24/Y24-to-Z48 entry to
the **same physical V2 $CA-biased UMUL24 source image**, rather than copying
any V1–V5 resident binary, table plane, or second 24-byte ZP allocation.

For 24-bit inputs x,y, signed and unsigned products relate by:

    SMUL24(x,y) mod 2^48 =
       UMUL24(x,y)
       - ((x & $800000) ? (y << 24) : 0)
       - ((y & $800000) ? (x << 24) : 0)  (mod 2^48)

Only the **upper three Z48 output bytes** require signed correction; the
lower half is exactly the original unsigned result. Correct in particular
for x=y=$800000 and the sign-boundary quadrants.

The current source experiment appends a public SMUL24 adapter after the
historical V2 native arithmetic rows. Both entries refer to one wrapper,
one native V2 carry-neutral source, four pre-biased 511-entry table planes,
one 24-byte contiguous ZP pointer bank and one writable code island. The
first test interleaves unsigned/signed calls, checks all six output bytes,
carry, X/Y preservation, output sentinels, and stack balance at $8000 and
$7123. It **must fit within the original 512-byte code slot** before it
is considered source-layout compatible.

Follow-on required: promote SMUL24 as an independently selectable
multi-entry producer in the builder, preserve the 227-byte/zero-ZP compact
kernel, compare both on one identical corpus, enforce once-only physical
source/table/ZP sharing when UMUL24+SMUL24 are installed, and qualify with
native VICE plus busiest-frame CPU-model tests. Do not count this research
stage as 31/56 qualified APIs; the speed installer currently has only the
UMUL24 production fast donor.
