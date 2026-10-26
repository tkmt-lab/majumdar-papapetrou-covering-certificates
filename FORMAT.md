# Certificate formats and trust boundary

`coverage.jsonl` records binary64 dyadic tree nodes, leaf certificates and
one summary per edge/condition. Decimal JSON numbers are decoded by Python
as binary64 and recovered as exact binary rationals by `Fraction(float)`.
The checker reconstructs every split from the root, requires every leaf,
checks first-return/domain/transversality fields and exact target inequalities,
and computes the adjacency characteristic polynomial and rational log bound.
A stored boolean is not a substitute for those finite checks. The interval
propagation that produced each bound remains part of the trust base.

CAPD result files contain task arrays, return codes and stdout. `CELL` lines
encode edge, kind, rational normalized-cell coordinates and verdict. The
coverage checker rejects contradictory duplicate verdicts, excludes
unresolved attempts, and checks exact unions of closed cells/edge segments.
Its accepted tasks can overlap; the union calculation does not double-count.

The independent audit of the saved rows recomputes positive margins from
printed diagnostics. Decimal text is parsed as rational values; those
printed endpoints are not certified directed-output enclosures. Native MPFR
interval inequalities in the numerical source supplied the original PASS.
M1 is excluded by the accepted source hash and task kinds.

`correspondence.json` links one-based binary64 leaf lines to zero-based CAPD
result rows for each of the 15 conditions. `verify.py` checks this mapping
against the newly regenerated coverage reports as well as its counts.
The rational input comparison checks centres, basis vectors, radii and
strip endpoints. Exact geometry checks nonsingularity, parent-box separation,
strip separation and the positive eigenvector identity over Q(phi).

The supplied paper uses an external closed-chain theorem and a prose
compactness argument. This package has no proof-assistant verification and
no pointwise comparison of the two implementations' return images. All
independence and input-exposure limits are in VERIFICATION-RECORD.md.
