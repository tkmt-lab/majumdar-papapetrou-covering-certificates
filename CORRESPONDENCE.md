# Correspondence of the two interval validations

The shared claim is the first positive upward return of the specified planar null initial graph, with fixed masses 1, centres at z = ±1 and p_t = −1. The exact box and strip data agree. The agreement is between separately implemented numerical enclosures of the same frozen claim; it is not independent selection of the claim.

| Feature | Binary64 certificate (`hset-check`) | CAPD certificate (`independent-capd`) |
|---|---|---|
| Arithmetic | Outward expansion with `nextafter`, including square root; exact binary endpoints recovered by `Fraction(float)` | MPFR intervals at 160 bits; exact decimal strings parsed with directed rounding |
| Integrator | Custom Taylor method, order 10; strict Picard tube and variational remainder checks | CAPD 6.1, pinned source `37057e5899bccaa6cd5701057b7e6ea5e232ef8b`, order 24 `MpITaylor` |
| Set representation | Two correlated parameters and a moving 4D error box; interval inverse of the stored QR basis | `MpC1Rect2Set`, preserving the two initial parameters and enclosing the graph curvature |
| Step choice | Dyadic subdivisions of 1/16; validated local remainder criteria | Maximum step 0.2, step-selection tolerances 1e−20; tolerances are not the certified error bounds |
| Return | Explicit phase tracking and full transverse crossing window; correlated correction using z as integration variable | Interval `MpIPoincareMap`, `MinusPlus`, affine target coordinates at an interval-enclosed hitting time |
| Domain and first return | Every tube stays in D; one downward window and the first subsequent upward window; opposite endpoint signs and positive normal velocity | Audit of both `move` overloads and all tubes; section-intersecting tubes must exclude zero normal velocity; positive return time/velocity and a downward crossing |
| Coverage checker | Exact dyadic binary trees; 1521 nodes and 768 successful leaves | Exact rational union of finite closed rectangles and edges; 2381 accepted cells, allowing overlap |
| Original validation controls | Rounding, known variational/short-flow examples, null initial graph and return prerequisites | Rounding, known harmonic first return, model acceleration and rejection of a nontransverse tube |
| Mathematical conclusion | All 15 C1/C2L/C2R conditions pass | The same 15 conditions pass |

| Edge | Binary64 C1 / left / right | CAPD C1 / left / right | Whole strip and both edges |
|---|---:|---:|---|
| O→O | 64 / 16 / 16 | 128 / 16 / 16 | PASS / PASS |
| O→A | 64 / 16 / 16 | 256 / 16 / 16 | PASS / PASS |
| A→B | 256 / 64 / 64 | 1330 / 67 / 72 | PASS / PASS |
| B→O | 64 / 16 / 16 | 272 / 16 / 16 | PASS / PASS |
| B→A | 64 / 16 / 16 | 128 / 16 / 16 | PASS / PASS |
| Total | 768 | 2381 | All five coverings |

The two counts describe different subdivisions and enclosure methods. They are not a timing or precision benchmark. The final CAPD A→B union retains five distinct successful older edge cells in addition to 1464 successful extension cells (1330 C1, 64 left, 70 right). Thus its final A→B count is 1469. The 312 unresolved extension parent cells are excluded; their successful descendants provide coverage. A finite union of closed cells that has full area in the closed parameter rectangle covers the entire rectangle: a nonempty relative-open complement would have positive area. The same argument applies to edge lengths.

`correspondence.json` gives every one-based binary64 JSONL leaf and summary line, and every zero-based CAPD result row with its task and `CELL` prefix, for each of the fifteen conditions. `evidence-inputs.json` fixes the source bytes and hashes. The original unmodified checkers and the completed paper-stage audit are in `evidence/` and `audit-result.json`.

The approximate CAPD margins in the paper are diagnostics from printed MPFR endpoints. Native interval predicates in `return_check.cpp` decide PASS. The binary64 endpoints are interpreted as exact binary values, not as exact decimal endpoint strings. No rounding convention is silently shared between the two checkers.

The numerical evidence does not establish hyperbolicity, a conjugacy or a whole-parent-box C1 assertion. The topological deduction uses the five disjoint strips and the external closed-chain covering theorem, followed by compactness and symbolic coding. The proposed formalization stage is L0; no Lean proof is included.
