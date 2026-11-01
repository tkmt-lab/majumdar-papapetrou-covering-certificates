# Verification record

## Mathematical and computational scope

This package concerns five specified strips, one first upward return map,
and an entropy lower bound per return. The interval propagation and the
closed-chain/compactness argument are not Lean-verified: the level is L0.
The named author is responsible for the work. AI tools assisted with design,
implementation, calculations, literature checks and drafting. No human expert
peer review is recorded. Preparation of this package used a single Codex
worker; it is integration and rechecking of existing evidence.

## Input exposure and implementation diversity

The binary64 verifier read the model specification, supplied box geometry,
and an earlier interval-method example. During extraction it also saw
unintended design sections containing nonrigorous numerical results and
candidate strips. That exposure was reported. The record states that those
numbers were not used as proved constants or search starting values. This
was not blind verification; the original exposure record is retained under
`evidence/hset-check/READ-LOG.md`, with routing identifiers removed.

The CAPD implementation used the frozen model, claims, boxes and strips.
Its recorded plan excluded the binary64 verifier's source, outputs and
report. The plan and source-input manifest are retained under
`evidence/independent-capd/`. The recorded separation is the basis for the
manuscript's construction statement; it is not a formally enforced proof
of every historical exposure. CAPD supplies interval propagation and the
oriented Poincare map. Project code separately specifies the field, graph,
chart, tube audit and acceptance predicates.

Both routes share the equations, box/strip choice, external topological
result and machine environment. They establish agreement on a fixed claim
through different implementations, not independent selection of the model.
The source solver hashes are bound by provenance.json and the evidence index.

## Existing calculations and saved-record audits

The binary64 certificate has 15 covering conditions, 768 successful leaves
and 1,521 exact tree nodes. The CAPD certificate has 2,381 accepted affine
return records (2,114 C1, 131 L, 136 R); M1 contributes zero. The unresolved
adaptive ancestors are not accepted as certificates. Overlap between accepted
CAPD cells is handled by an exact rational union.

Original numerical runs and controls are retained as historical evidence.
The v1 and v1.1 paper-stage audits reran the saved-record coverage checkers,
checked exact input alignment and CAPD row/margin provenance; they performed
no new ODE integration. The publication entrypoint repeats those bounded
checks in temporary directories, adds exact geometry and correspondence
checks, and checks the aggregate time-range containment stated in the paper.
Default checks trust the integrators' validated enclosures and native CAPD
predicates. Printed MPFR endpoints are diagnostics, not directed certificates.
No pointwise return-image intersection audit is claimed.

## Supplied manuscript readings

Two supplied reports identified their reader as Antigravity / Claude Opus
5.5, the same reader on both occasions, and both recommended MINOR. The
reader read source text and selected certificate/code files and made hand
checks, including the optical-core curvature inequalities and table values.
The reader could not execute the scripts or inspect the PDF and did not
read the primary external theorem papers. These readings are not executed
reproductions, human peer review, or two different independent readers.

The first response table contains 25 numbered items. The second report's
summary describes 27 judgments; its count is not adopted as a count of
distinct original item IDs. The publication revision addresses its seven
concrete minor wording/source items. Its optional suggestion to compare
pointwise return-image intersections was not undertaken.

The revision checked the Hénon/Rössler/Lorenz overview in the author PDF of
Zgliczyński–Gidea (introduction, PDF page 2), located `-std=c++17` in the
recorded binary64 command arrays, clarified the continuous-time scope of
Bolotin–Kozlov, and shortened the Pantig comparison to its abstract. Earlier
paper preparation checked the closed-chain theorem and compact-core theorem
in the primary sources. Pantig full-text comparison remains pending.

## Publication transformations and remaining steps

The paper version is 1.0.0, currently a local release candidate. There is
no public archive URL or DOI yet. The publication coordinator must assign
those after release and update README/citation metadata. The planned date
is 31 October 2026; preparation does not assert publication on that date.

Update, 1 November 2026: version 1.0.0 was released from commit
`5849fdd83b801cd65659a88ad70805c4ec54bd76` with version DOI 10.5281/zenodo.23850841
(all versions 10.5281/zenodo.23850840). The evidence and checks are unchanged.

Machine-local paths and internal routing identifiers were replaced in
exported metadata, with before/after SHA-256 values in provenance.json.
Three contributing CAPD result files change only their `authorization`
field; all numerical JSON fields compare exactly to the original. Earlier-input
digests embedded in a later result and dependent indexes were rebound; reversing
those documented digest substitutions restores all non-authorization fields. Both solver sources, both original
coverage checkers and the binary64 JSONL remain byte-identical. Historical
embedded manifests keep their historical role; MANIFEST.sha256 alone is
the complete distribution manifest. No external libraries or papers are
redistributed. No new numerical calculation, external publication, author
contact or paid full-text access was performed to prepare this package.

## Publication-candidate validation

The bounded saved-record checks passed on 26 October 2026: 15 conditions,
768 binary64 leaves, 1,521 tree nodes, 2,381 accepted CAPD records, five
aggregate time-range containments and the complete 15-condition row mapping.
Five corrupt-input controls were rejected: a missing binary64 leaf, a false
return flag, zero transverse velocity, a missing CAPD edge and a wrong source
hash. Distribution membership, exported hashes, claim references and PDF
text/metadata passed. Tectonic 0.17.0 produced no final warnings; all ten
rendered pages were visually inspected. The publication wrapper initially
exposed an omitted internal-job reference and an incomplete metadata-digest
rebinding; both were corrected without changing numerical data. A clean-clone
run of the same command is required before any push. GitHub-hosted CI has not
run while this package remains local.
