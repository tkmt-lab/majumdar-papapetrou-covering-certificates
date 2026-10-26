# Reproduction

## Default: saved records only

Python 3.11+ and Poppler are required. No pip packages, network or numerical
libraries are needed. Run `python3 -B check_all.py`. The command refuses
optimized Python, because historical checkers use assertions. Subprocesses
also have `PYTHONOPTIMIZE` removed and bounded timeouts. Every generated
coverage report is written in a temporary copy. The delivered files are
checked again at the end.

The individual entrypoints are `check_packet.py`, `verify.py` and
`negative_controls.py`. The first checks distribution integrity and PDF
metadata/text. The second reruns exact geometry, the two historical coverage
checks, fixed-input alignment and the CAPD row/margin audit. It also checks
that the aggregate CAPD return-time ranges lie within the displayed coarse
binary64 time intervals. This is not a pointwise return-image comparison.
The negative controls remove or corrupt certificate data and require rejection.

Expected successful counts are 15 conditions, 768 successful binary64 leaves,
1,521 tree nodes and 2,381 accepted CAPD rows, with zero M1 rows and zero new
ODE integrations. A checker PASS is conditional on the recorded interval
propagation, not a new proof of the ODE enclosures.

## Typesetting

The delivered PDF was built with Tectonic 0.17.0. A local compatible TeX
installation may also work. In a separate copy:

```sh
tectonic --untrusted --keep-logs paper.tex
pdftoppm -r 110 -png paper.pdf page
```

Tectonic may download standard TeX resources on its first use; use
`--only-cached` when already available. The delivered layout has 10 A4 pages.
PDF bytes can vary with the engine, fonts and creation metadata. CI inspects
the delivered PDF; it does not build TeX or fetch resources.

## Optional numerical reproduction

This is a separate, resource-bounded computation, never part of default CI.
The package contains frozen numerical sources and historical operational
scripts for inspection. Those drivers use original workspace assumptions;
do not run them unchanged in an arbitrary checkout. Set an isolated output
directory and explicit time/memory limits, and retain all failures and logs.

Binary64 uses `evidence/hset-check/solver.cpp`, `boxes.dat` and `strips.dat`.
The recorded Apple clang 21.0.0 command in `trials.json` includes:

```sh
clang++ -std=c++17 -O2 -ffp-contract=off -fno-fast-math solver.cpp -o solver
./solver "$PWD/boxes.dat" cover "$PWD/new-coverage.jsonl" 1500 0.0625
```

Use a fresh directory containing the exact inputs. Rename/copy the new log
only in that directory to the checker's expected `coverage.jsonl` and run
`check_coverage.py`. The internal time limit is not an external resource cap.
Read `evidence/hset-check/METHOD.en.md` for arithmetic assumptions.

CAPD uses source commit `37057e5899bccaa6cd5701057b7e6ea5e232ef8b`, with
source archive SHA-256
`960768c4aabfcf55799ca85f0dc2bcf449ed6e0355f46ba19dad8413c4d09024`.
The recorded configuration is macOS arm64, GCC 16.2.0, MPFR 4.2.2, GMP 6.3.0,
`CAPD_ENABLE_MULTIPRECISION=ON`, `CAPD_INTERVAL_TYPE=NATIVE`; the solver
itself uses 160-bit `MpInterval`, Taylor order 24, maximum step 0.2 and
step-selection tolerance 1e-20. See `environment-record.json`, `build-result.json`
and `controls-result.json` under `evidence/independent-capd/` for the original
build/link arguments. Replace the marked local paths with isolated locations.
Obtain CAPD from its upstream source, not from this package. Its source is
not vendored. Respect each dependency's license.

Compile `return_check.cpp` and `geometry_generated.h` against that build.
Run its `controls` mode first, then the tuples in `correspondence.json`:
`return_check EDGE KIND IU NU IS NS reserved`. Edges 0..4 are OO, OA, AB,
BO, BA; kinds are C1, L, R. The four integer parameters encode normalized
rational cells. Retain complete stdout/stderr, return code, task tuple,
source hash and executable hash. Audit new results using the same schema;
do not combine failures with old successful records to call a new run a
success. No numerical replay was performed to prepare this publication packet.
