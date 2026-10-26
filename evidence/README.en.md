# Evidence map and audit filenames

The packet contains two saved interval certificates for the same exact five-strip claim. Start with `hset-check/METHOD.en.md` and `independent-capd/METHOD.en.md`. The original Japanese method documents are retained unchanged.

| Program | Frozen expected output | Fresh output written by the program |
|---|---|---|
| `hset-check/check_coverage.py` | `hset-check/expected-coverage-audit.json` | `hset-check/coverage-audit.json` |
| `independent-capd/ab-extension/check_coverage.py` | `independent-capd/ab-extension/expected-coverage-check.json` | `independent-capd/ab-extension/coverage-check.json` |

The expected files were copied under an `expected-` prefix by the paper packet preparer. The generated names retain the original checker conventions. Compare semantic results and provenance hashes, not wall times or timestamps. Both forms are indexed; no alternative numerical claim is implied by the prefix.

To rerun both checkers without overwriting either baseline or the packet's previous generated outputs, run from `paper-v1/`:

```sh
python3 -B evidence/independent-capd/audit_review_fixes.py --out /tmp/r029-review-audit.json
```

The wrapper uses temporary copies, invokes neither numerical solver nor compiler, and checks the CAPD source rows and Table 5 margins. It leaves all frozen inputs untouched.

The CAPD coverage output's `source_sha256` identifies `return_check.cpp`. The distinct Python checker hash and the exact accepted input list are given in `independent-capd/certificate-index.json`. All 2,381 accepted tasks are C1, L or R; none is an exploratory M1 task. Table 5's CAPD witnesses, with zero-based result rows and complete output lines, are in `independent-capd/review-audit.json`. Their margins describe printed diagnostics, while native MPFR interval comparisons supplied the original PASS decisions.

The original source/build version record is `independent-capd/final-artifact-manifest.json`; its paths refer to the original research directory and it is not the manifest of this portable packet. `independent-capd/environment-record.json` extracts the recorded versions and compile/link arguments. `capd-library-flags.make` and `capd-build-CMakeCache.txt` preserve the existing local build configuration, with original paths. Relocate paths for a separately authorized numerical rebuild; do not execute the operational build or run scripts during a saved-record audit.

The claims index now names the method, plan, frozen input specification and exposure records. The final paper package's top-level input inventory and hash manifest must be refreshed when these evidence additions and the subsequent manuscript edits are integrated.
