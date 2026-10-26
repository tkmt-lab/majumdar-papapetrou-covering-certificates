# Binary64 certificate: method and interpretation

This is the English companion to the original `METHOD.md`. It describes the saved certificate and its trust assumptions. The immutable packet baseline is `expected-coverage-audit.json`; the checker writes a fresh `coverage-audit.json`. The coverage decisions, exact trees and source hashes must match, while timing fields may differ. A method description alone does not declare a successful computation.

## Model and fixed inputs

The four-dimensional autonomous ODE in `inputs/SPEC.md` has state `(x,z,vx,vz)`, section `z=0, vz>0`, and initial graph `iota(q,w)=(q,0,w,sqrt(1-w^2))`. Decimal strings in `boxes.json` are exact rational inputs. The three original A-1 boxes, including their centres, bases and radii, are fixed. Exact rational vertex/projection calculations in `geometry-pilot.json` separate different boxes in q.

A box is written `c+u_vec*u+s_vec*s`. Each of the five strips in `strips.dat` restricts u to its specified rational interval and retains the full s interval `[-1,1]`. Exploratory point calculations selected these strip endpoints; their sampled trajectories are not whole-strip certificates. Strips in the same parent box have disjoint u intervals. `READ-LOG.md` records input provenance and prior exposure to exploratory numerical results. This was not verification by an unexposed third party.

## Arithmetic and initial enclosure

The interval type in `solver.cpp` expands the binary64 result of each basic arithmetic operation and square root outward by one ULP using `nextafter`. Identities are used for operations with exact zero. Finite values, denominators excluding zero, and nonnegative square-root arguments are checked. The decimal parser checks that integer numerators and denominators are below `2^53` before enclosing the rational input.

The recorded compilation flags are `-O2 -ffp-contract=off -fno-fast-math`. The trusted base includes IEEE-754 round-to-nearest basic operations and correctly rounded square root and `nextafter`; this is not a formally verified interval library. `environment.txt` records the original compiler and platform.

The 17-digit JSON endpoints round-trip to the original binary64 values. The audit converts those same binary64 values to exact rationals with `Fraction(float)`. It does not interpret their printed decimal strings as exact outward enclosure endpoints. Short displayed bounds in the paper are coarsened outward separately.

Each initial cell is enclosed as

`X = c + C*xi + B*eta`, with `xi in [-1,1]^2` and `|eta_j|<=r_j`.

The affine q,w coordinates are enclosed directly. The vz component uses the first-order Taylor expression at the central w and remainder bound

`|delta_w|^2 / [2*(1-w_range^2)^(3/2)]`.

Rounding errors in the centre and matrices also enter r. This contains every point of the true null initial graph. The enclosing four-dimensional set may contain non-null points; propagation by the smooth extended ODE still contains the null family.

## One-step existence and Taylor enclosures

For each positive step h, a Cartesian tube B0 must satisfy the strict Picard inclusion

`X + [0,h]*f(B0) subset int(B0)`.

The field is smooth where its denominators do not vanish. Continuation and continuous dependence give existence of every initial trajectory throughout the step in B0. Two subsequent intersections `B <- B intersect (X+[0,h]*f(B))` retain the true tube.

Every tube must satisfy `r±>1/5` and `x^2+z^2<64`. If a step cannot be certified, h is halved; failure to certify a cell is unresolved, not a physical horizon-crossing conclusion.

Let a_k denote the time Taylor coefficients of the flow and N=10. Interval power-series recurrences evaluate these coefficients. The central solution satisfies

`Phi_h(c) in sum(k=0..N) a_k(c)*h^k + a_(N+1)(B)*h^(N+1)`.

For the variational equation `V'=Df(Phi_t(x))*V`, `V(0)=I`, let `L>=sup_B ||Df||_infinity` and require `a=hL<1/2`. Then

`||V-I||_infinity <= exp(a)-1 <= a/(1-a) = e`,

so `V_tube=I+[-e,e]` componentwise contains the variation. The Taylor enclosure is

`D Phi_h(X) subset sum(k=0..N) Da_k(X)*h^k + Da_(N+1)(B)*V_tube*h^(N+1)`.

This follows from `d^k V/dt^k = k! Da_k(Phi_t(x))*V(t)` and the variational Taylor remainder. It is not obtained by differentiating an unknown intermediate-time remainder in the position formula. Automatic differentiation in four variables and interval power-series arithmetic enclose Da_k. The step requires central remainder at most `1e-13` and variational infinity-norm remainder at most `1e-11`.

Steps are dyadic subdivisions of 1/16. In the recorded run, sums of these times up to the operational limit 60 are exactly representable in binary64. Powers of h in remainder bounds are enclosed with interval arithmetic.

## Enclosure update preserving correlations

Let J enclose the one-step variation and M be its componentwise midpoint. Set `C_new=mid(M*C)`. Choose B_new from a floating-point QR calculation on `mid(J*B)`. Exact orthogonality of this computed basis is not assumed. Interval Gaussian elimination encloses the inverse of the actual stored binary64 B_new; a pivot containing zero causes failure.

The new error is enclosed by

`B_new^-1 * [(Phi_h(c)-c_new) + ((J-M)*C + M*C-C_new)*xi + J*B*eta]`.

Its componentwise absolute upper bounds define the new r. The two parameter correlations are retained. A poor basis may produce a wide enclosure but does not invalidate this inclusion formula. The segment from the centre to each represented point lies in the outer Cartesian box used to bound J.

## First subsequent upward crossing

The first step requires positive vz throughout its tube and positive z at its endpoint. While on the positive side, the algorithm excludes a zero either because the entire tube has positive z or because vz is positive and z increases from the known positive start. A downward-crossing window requires negative vz throughout and ends with negative z. On the negative side, analogous zero-free or monotone downward steps preserve the sign until the upward window.

The upward window has negative z at its start, positive z at its end, and `vz>=nu>0` throughout, for all initial values. Every trajectory has a unique return time in that window. The preceding sign/monotonicity checks make it the first subsequent upward return. Saved successful cells record the window, endpoint signs, nu, exactly one downward window and strict spatial-domain margins. A timeout or unresolved window is not a proof of nonexistence.

At a common fixed time before this window, let X0 be the enclosing set with `z0<0`. Let K enclose `(vx/vz, f_vx/vz)` throughout the window. Using z as the integration variable gives

`(x,vx)_return = (x,vx)_0 - K_avg*z0`, with `K_avg in K`.

For a chosen point k0, evaluation uses

`(x,vx)_0-k0*z0 + (k0-K)*z0`.

The first linear part preserves the doubleton correlations and applies the target inverse-chart rows directly. This encloses the image at the different hitting times of all initial points; it is not a fixed-time image substituted for P.

## Finite coverage and saved-record checking

C1 covers each entire source parameter rectangle; C2L and C2R cover the full left and right s edges. Dyadic child cells share only their closed boundary and exactly cover their parent. Each accepted leaf proves the return prerequisites and one strict condition:

- C1: `-1<S_lower<=S_upper<1`;
- C2L: `U_upper<-1`;
- C2R: `U_lower>1`.

`check_coverage.py` traverses every tree node independently of the producer's traversal. It compares endpoints with `Fraction`, associates successful records to all leaves, and checks their recorded bounds and strict inequalities. An unprocessed, timed-out or unproved cell prevents acceptance. The saved certificate contains 768 accepted leaves over fifteen conditions and 1,521 checked tree nodes.

The checker does not reintegrate the ODE or reprove the numerical enclosure implementation. Its default output is `coverage-audit.json`. The packet's `expected-coverage-audit.json` is the saved expected output. Their shared `coverage_sha256` and `checker_sha256` bind the data and checking code; the fresh output is compared semantically with the expected baseline. The combined review audit in `../independent-capd/audit_review_fixes.py` runs this checker in a temporary copy, leaving both baseline and original numerical records untouched.

## Conditional dynamical consequence and limits

After all five source-to-target C1/C2 conditions pass, the target box N_j can be restricted to each listed successor strip K_jk without changing its s radius. For a successor u interval `[a,b]`, its coordinate is `(U_j-(a+b)/2)/((b-a)/2)`. The original left and right inequalities outside -1 and 1 also cross the successor's exit boundaries. Thus every listed source strip covers each allowed successor strip.

The five disjoint strips give the edge-state adjacency matrix B. The homotopy reducing S to zero and taking U to 2u avoids the entrance and exit obstructions and has exit degree one. The adopted closed-chain covering theorem, compactness and the continuous coding on disjoint strips provide the symbolic dynamical conclusion. The topological argument and its external theorem remain mathematical premises outside the executable interval checker.

For the three-box matrix `A=[[1,1,0],[0,0,1],[1,1,0]]`, the exact integer characteristic polynomials are `lambda*(lambda^2-lambda-1)` and `lambda^3*(lambda^2-lambda-1)` for A and B. Their spectral radius is phi. The logarithm is enclosed by rational bounds for sqrt(5), substituted into the positive series `2*sum(k>=0)(sqrt(5)-2)^(2k+1)/(2k+1)` with a rational tail bound. The reported entropy is per return, conditional on the covering and topological premises.

The certificate does not establish a strong whole-parent-box C1 claim to several incompatible targets, a unique orbit per symbolic sequence, conjugacy, hyperbolicity, an entropy rate per unit physical or affine time, or novelty. Model correspondence adopts the provided specification; this implementation task did not re-audit the original physics literature.
