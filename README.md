# A five-strip covering certificate for planar null geodesics in an equal-mass Majumdar–Papapetrou spacetime

Five explicit strips in a planar light-ray return section satisfy covering
relations. Together with a closed-chain covering theorem, they give a compact
invariant set whose return dynamics has topological entropy at least
**log((1+sqrt(5))/2) ≥ 0.481211825059603 per return**. The units are natural
logarithms per return, not entropy per unit physical time.

Read the [article](paper.pdf), its [TeX source](paper.tex), and the precise
[claims](claims.json). Version **1.0.0** was released on 1 November 2026
(version DOI [10.5281/zenodo.23850841](https://doi.org/10.5281/zenodo.23850841);
all versions [10.5281/zenodo.23850840](https://doi.org/10.5281/zenodo.23850840)).

## Check the saved evidence

Use Python 3.11 or newer and Poppler (`pdftotext`, `pdfinfo`). There are no
Python package dependencies. From the repository root, run the same command
as CI and the clean-clone preflight:

```sh
python3 -B check_all.py
```

The command checks file membership/hashes, exported provenance, PDF text and
metadata, exact geometry, both original coverage checkers, agreement of the
fixed rational inputs, CAPD row provenance and printed margin diagnostics,
and deliberately corrupted-input controls. It copies evidence to temporary
folders and leaves this repository unchanged. It invokes no integrator,
compiler, network request or optional operational driver. Success is exit
code 0 and a final `status: PASS`.

The binary64 certificate has **15 conditions, 1,521 tree nodes and 768
successful leaves**. The CAPD/MPFR certificate has **2,381 accepted records**:
2,114 C1 cells, 131 left-edge cells and 136 right-edge cells. All use the
accepted affine-return source; zero use the exploratory M1 variant.
[REPRODUCE.md](REPRODUCE.md) distinguishes this audit from a new numerical
integration. [FORMAT.md](FORMAT.md) describes the record formats and trust.

## Scope

The saved-record checks are conditional on the integrators' validated
flow/return enclosures. CAPD's printed decimal endpoints are diagnostics;
its original native MPFR predicates decide acceptance. The topological
argument and the integrators are not formally verified. **Lean level L0**:
no Lean theorem is included. There has been no human expert peer review.

The implementations share equations, boxes, strips and the geometric claim.
Their agreement supplies implementation diversity, not an independently
chosen physical model. No hyperbolicity, conjugacy, least-period result,
whole-parent-box covering, or exhaustive novelty claim is made. Qualitative
positive entropy of the optical geodesic flow also follows from our stated
application of Bolotin–Kozlov's general theorem. Comparison with Pantig's
2026 paper is limited to its accessible abstract; its full text remains
unreviewed. [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md) records the input
exposure and the limits of the two supplied AI readings.

## Certificate storage and provenance

All certificate data needed for the default checks are bundled in
[evidence/](evidence/README.en.md). No external large-certificate download is
required. The per-file **location, byte size and SHA-256** are in
[evidence-inputs.json](evidence-inputs.json); the whole distribution is fixed
by [MANIFEST.sha256](MANIFEST.sha256). The two principal records are
`evidence/hset-check/coverage.jsonl` and the six CAPD result files named in
`evidence/independent-capd/ab-extension/expected-coverage-check.json`.

[provenance.json](provenance.json) binds original and exported hashes.
Machine-local path prefixes and internal routing identifiers were replaced
in metadata only. Three CAPD result files have a routing-only `authorization`
field replacement, with dependent result-file digests rebound (including
embedded earlier-input digests in later result metadata). Their
numerical records, task coordinates, stdout and verdicts are identical to
the source; both solver and coverage-checker sources are byte-identical.
Historical embedded manifests describe their original source trees and are
not this distribution's inventory. Local executable binaries, CAPD libraries,
full external source archives and build caches are not included. A numerical
rebuild obtains the pinned dependencies separately.

## Attribution and license

Tatsuhiko Takimoto is responsible for this work. Codex and Claude assisted
with implementation, computation, mathematical discussion and writing.
[The verification record](VERIFICATION-RECORD.md) separates executed checks
from source reading. Building this package is not a fresh independent review.

Contopoulos, Dettmann–Frankel–Cornish, Cornish–Gibbons and Shipley–Dolan
provide earlier work on black-hole scattering and symbolic dynamics.
Bolotin–Kozlov supply the compact-core theorem; Zgliczyński–Gidea supply
the covering-relation framework. Kapela, Mrozek, Wilczak and Zgliczyński's
CAPD, with MPFR/GMP, supports the second interval implementation. I thank
the authors and developers for these foundations and hope this work adds
something to the field they developed. This does not imply endorsement.
References and access limits are in [SOURCES.md](SOURCES.md) and the article.

Project code is Apache-2.0; original text and generated data are CC BY 4.0.
Third-party libraries are not redistributed. See [LICENSE](LICENSE) and
[CITATION.cff](CITATION.cff).

## Representative certificate files

All are bundled; the full list is in evidence-inputs.json.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `evidence/hset-check/coverage.jsonl` | 941937 | `b7de0a0d3204bd218e81619a945b5ca4303cbfc7b75c899201ac5b30dcdf2b0b` |
| `evidence/independent-capd/coverage-result.json` | 852892 | `4e76e73db78fb32766c5ebf34cf875be88e583e2f10824a2bd29ef99f18a4189` |
| `evidence/independent-capd/ab-extension/full-result.json` | 2147015 | `e27e8634ed56408bd53c90e22ce0b20d1ff83585421c02baebb1a31648238e50` |
