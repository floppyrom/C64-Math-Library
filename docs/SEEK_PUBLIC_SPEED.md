# Authenticated public-call speed for the eight original SEEK APIs

The original generated RAM-operand SEEK8 (651 code bytes + 160 persistent
state bytes) and SEEK16 (898 code bytes + 248 persistent state bytes) are now
eligible for the operation-first installer's `speed` objective. **No kernel is
replaced.** Each family still owns one shared four-entry code image and uses
19 bytes of INIT scratch, zero new ZP, and eight independent slots.

The benchmark `tools/selective_speed_seek.py` uses 80 deterministic moves per
API at two independently relocated code/I/O/state origins. Positions cover
zero-length routes, single-pixel moves, horizontal/vertical/diagonal cases,
all eight indexed sprite slots, integer and fractional speeds, Euclidean path
speed, and subsequent arrival/post-arrival calls. Original generated source
SHA-256, exact geometry, public C/X/SP/input preservation, untouched other
sprite slots and immutable code are checked. INIT and each STEP variant are
**benchmarked separately**, because a frame normally calls INIT once per move,
but calls a stepper many times. STEP timing excludes initialization, while
including arrival handling and one post-arrival call per route.

The output records complete public entry-through-RTS **CPU-model** cycles
(mean, p95 and worst), fixed-corpus SHA-256, source/generator hashes, and
exact scratch/persistent-state geometry. These are NOT physical PAL/VIC-II
badline, IRQ, REU or loader timings. Source qualifications run under the
same two placements as the existing native VICE state and carry checks.
The installer weights INIT versus per-frame STEP calls using explicit
`workload_calls`. There is only one source-qualified variant per API, so
this measurement authenticates the original speed without claiming a new
faster kernel.

For game loops, provide realistic call frequency for each operation, e.g.
two INIT calls and 120 STEP1 calls in a representative workload, instead
of comparing INIT and STEP as equally frequent. SRAM and shared-code
selection remain subject to strict RAM/ZP budgets and separate hardware
parity gates. All historical V1–V5 resident images stay unchanged.
