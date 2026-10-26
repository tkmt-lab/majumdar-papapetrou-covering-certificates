# CAPD certificate: method, accepted evidence, and trust boundary

This English description accompanies the original Japanese `METHOD.md`. It identifies the final 2,381 accepted records used by the paper; exploratory methods mentioned in the historical Japanese document are distinguished below. It describes the saved calculation and does not report a new integration.

## Accepted method and identifiers

All 2,381 accepted records use `return_check.cpp`: 2,114 C1 cells, 131 left-edge cells and 136 right-edge cells. **No M1 record from `return_mvt.cpp` is used.** The mean-value variant described at the end of the historical Japanese method was exploratory. It is not a premise of this paper's covering certificate and its source is not needed to reproduce the accepted record audit.

The `source_sha256` field in `ab-extension/expected-coverage-check.json` identifies the numerical source `return_check.cpp`, SHA-256 `1cafbf1b8dad5580a5bd9d45c49247ef8d8dcaba8b97f2e23eae342e30fc411f`. It does **not** identify the coverage-checking Python script. The latter is `ab-extension/check_coverage.py`, SHA-256 `e62eed123fc363954541ba7369a9786406ff4c832951dd7d020894ac853b15c1`. Both are listed in `certificate-index.json` and the paper's claims index. `review-audit.json` traces every accepted source family and the margin witnesses.

The frozen claim and input provenance are in `PLAN.md`, `input-manifest.json`, `CLAIMS.json`, `SPEC.input.md` and `DESIGN.4.1.1-4.1.2.input.md`. The last file is the originally permitted excerpt; its exploratory diagnostic numbers are not certificates. The final accepted coverage is established by the saved result files, not by an exploratory input claim or historical progress note.

## Arithmetic, model and initial set

The calculation uses CAPD at commit `37057e5899bccaa6cd5701057b7e6ea5e232ef8b`, 160-bit MPFR intervals, `MpITaylor` of order 24 and `MpC1Rect2Set`. Decimal inputs are parsed directly with `RoundDown` and `RoundUp`; they are not first rounded to binary64. The recorded environment, exact compiler/link argument arrays and library flags are in `environment-record.json` and its referenced files. The step-selection tolerance is the double argument `1e-20`, with maximum step `0.2`. These are step-selection settings, not certified global error bounds; interval Taylor remainder bounds provide the enclosures.

The independently written field expression uses

`U = 1 + 1/r+ + 1/r-`,

`grad U = (-x/r+^3-x/r-^3, -(z-1)/r+^3-(z+1)/r-^3)`,

`v' = 2/U * (grad U - v*(grad U dot v))`.

The state is `(x,z,vx,vz)`, and the null initial graph is `(q,0,w,sqrt(1-w^2))`. The two parameters determine q and w affinely. For `g(w)=sqrt(1-w^2)`, the enclosure uses

`g(w0+dw) in g(w0) + g'(w0)*dw + g''(W)*dw^2/2`,

with `g''(W)=-1/(1-W^2)^(3/2)`. The linear parameter correlation is retained in the doubleton's `C*r0`; quadratic remainders and coefficient rounding enter the interval part of the set. The original source inspection established that this constructor and the first propagation preserve interval uncertainty in x and C. An enclosing set may contain non-null points; propagation by the smooth extended field still contains the true null family.

## First upward return and tube audit

The calculation uses the interval class `MpIPoincareMap`, the coordinate section `z=0`, and orientation `MinusPlus`. In the pinned CAPD source, the crossing routine leaves the initial section, reaches the negative side, and finds the first subsequent upward crossing. Its transversality check rejects a section-intersecting tube if the normal velocity contains zero, rather than silently skipping a possible crossing inside a step.

An additional audit is embedded in integration: it wraps both `move` overloads and inspects every `getLastEnclosure`, including trial and return-time-refinement steps. It requires `r±-1/5>0` and `64-x^2-z^2>0`. Every tube containing `z=0` must exclude zero from `vz`. The bounds of 20,000 moves and affine time 100 are operational stopping conditions, not proofs of nonreturn.

The initial normal velocity is positive. Each accepted result additionally requires positive return time, positive return velocity, and an audited downward crossing. CAPD's affine-coordinate overload encloses `A*(P-c)` at the interval-enclosed variable hitting time. A fixed-time image is not substituted for the return map. The first two returned coordinates are target U and S; the fourth retains vz. A is an interval enclosure of the inverse target chart.

The trust boundary includes the pinned CAPD interval integrator and Poincare implementation, MPFR/GMP, the compiler and execution environment. This project's code supplies the model, initial-set construction, chart, audit and predicates. It does not independently reimplement CAPD's integrator or formally verify that library.

## Acceptance and exact coverage

For C1 the full cell's S enclosure must lie strictly inside `(-1,1)`. For a left boundary cell, the upper endpoint of U must be below -1; for a right boundary cell, its lower endpoint must exceed 1. PASS is decided by native interval comparisons. A wide or failed enclosure is unresolved, not a mathematical counterexample. A CONTRARY label is reserved for an interval enclosure putting the entire nonempty cell image outside the required region; no such record is accepted here.

The coverage checker reads six frozen result files listed under `inputs` in `ab-extension/expected-coverage-check.json`. It checks their numerical-source hash, process return code, printed task identity and verdict, and keys records by the complete rational task tuple. The later occurrence replaces an identical earlier task after a verdict-consistency check. The final list contains distinct task cells, but those cells can overlap geometrically.

The normalized intervals are `[iu/nu,(iu+1)/nu]` and `[is/ns,(is+1)/ns]`. Index validation requires `0<=iu<nu` and `0<=is<ns`, so every cell already lies in `[0,1]^2`; no clipping is necessary or performed. For area, the checker sorts all distinct rational u endpoints, sweeps each resulting slab, computes the union length of the s intervals spanning that slab by sorting and merging overlaps, then sums width times union length. All arithmetic uses `Fraction`. Left and right boundary covers use the same exact interval-union routine. Overlaps are counted once.

A finite union of closed cells inside the square is closed. If its complement were nonempty, that relatively open complement would have positive area; thus area exactly one establishes coverage of the entire closed square, including its boundary. The analogous length argument applies to the exit edges. All five areas and ten boundary lengths equal one. This is a finite coverage audit of saved solver claims, not a new ODE proof or an integration rerun.

## Margins and adaptive subdivision

`ab-extension/proof-summary.json` contains the original approximate summaries. `review-audit.json` gives, for every Table 5 CAPD minimum, the source JSON file, zero-based row, task tuple, complete CELL line, input-file hash and exact rational value calculated from the printed decimal endpoints. The ten values reproduce Table 5. The printed MPFR endpoints are diagnostics, not directed-output interval certificates; the original native MPFR predicates remain the acceptance basis.

The adaptive drivers (`run_coverage.py` and `ab-extension/run_full.py`) retain a cell once the strict predicate succeeds and subdivide unresolved cells within the prescribed resolution and resource bounds. They do not require a predetermined positive margin. Older accepted overlapping cells are retained in the final union. A small minimum over these enclosures is therefore allowed and depends on both enclosure width and retained subdivision history; it is not a perturbation-robustness radius or a discrepancy measure between implementations.

The other implementation uses different cells and enclosures. The saved audits establish agreement on the same exact geometry and all fifteen covering conditions. **No pointwise intersection test between the two implementations' return enclosures was performed in this task**, and no such result is claimed from their different aggregate margins.

## Controls and historical settings

The original controls check directed decimal parsing, division and square-root containment; a harmonic oscillator's upward first return contains 2*pi and its known return point, with time strictly between 6 and 7, and records both upward and downward crossings. A negative control requires rejection of a tube containing zero normal velocity. A model control compares the acceleration at `(2,0,0,1)` with `-8/[5*(sqrt(5)+2)]`. These controls support implementation checks; they are not themselves covering certificates.

Early exploratory runs used tolerance `1e-35` and maximum step `0.1` and encountered time limits or unresolved transversality. The accepted-source version uses `1e-20` and `0.2`, retaining 160-bit precision and order 24. The six contributing run records contain their original elapsed times. Their wall times include unresolved adaptive ancestors and cannot be read as a like-for-like performance comparison.

## Expected and generated audit names

`ab-extension/expected-coverage-check.json` is the immutable baseline copied into the paper packet. Running the original checker writes `ab-extension/coverage-check.json`. Their coverage decisions and accepted record lists must agree; timestamps need not. These are intentional baseline/output roles, not alternative names for different claims.

For a non-destructive combined recheck, run from the paper directory:

```sh
python3 -B evidence/independent-capd/audit_review_fixes.py --out /tmp/r029-review-audit.json
```

This runs the original CAPD and binary64 saved-record checkers in temporary copies and checks the 2,381 source rows and Table 5 witnesses. It invokes no numerical solver or compiler. `return_check.cpp`, the original result files and the expected audit outputs remain unchanged.
