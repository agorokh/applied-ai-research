# Assumptions And Unknowns

Every entry is an explicit hypothesis with the evidence that motivated it, per the
skill's operating rule ("treat missing paper details as explicit hypotheses").

## Scope decision (deliberate, not a paper unknown)

- **Example 3 (cylinder wake, arxiv.tex:937-1197) is not planned.** The claim family
  requires DNS-derived POD-mode data; this replication ran laptop-only. The release
  bundle's own runs cover it. Consequence: our `validate-completion` covers the planned
  11-target set, not the full paper -- coverage is planner-relative by the workflow's design.

## Setup values not stated in the paper (hypotheses)

1. **Ex1 integration/noise**: trajectory length T=25 (Fig:Ex1 axis), dt=0.01 (assumed),
   x0=(2,0) (Fig:Ex1 phase portraits start near (2,0)), derivative noise eta=0.05 (assumed
   small; appendix deviations from truth are ~0.002-0.003), lambda=0.05 (assumed; recovers
   the published support at this data volume). Resolution test: run at these values and
   check support + coefficient deviations against the appendix tables.
2. **3D linear system**: T=50 (Fig:Ex1_3d axis), x0=(2,0,1) (assumed from figure scale),
   poly order 3 (text says "second or third order", arxiv.tex:618).
3. **Lorenz**: dt=0.001, T=100 (assumed; long-attractor sampling), lambda=0.025 (common
   published SINDy practice for Lorenz), eta=1.0 (appendix table caption states eta=1.0).
   x0=(-8,7,27) from FIG00BIG caption.
4. **Logistic**: 1000 iterations per mu with 100-step transient discard, five initial
   conditions x0 in {0.1,...,0.9} per mu (resolved -- see log), clipping to [0,1] under
   forcing (assumed; keeps the stochastic map in its domain), lambda=0.08 (assumed;
   below the unit coefficients, above the noise floor).
5. **Hopf**: mu grid {-0.2,-0.1,0.05,...,0.55} spanning Fig:HopfTraining's range (assumed);
   outer IC r=1.2, inner IC r=0.05; T=50, dt=0.025 (250 samples per limit-cycle period;
   revised from dt=0.0025 because the dense TV antidifferentiation operator scales O(m^2)
   in memory -- resolution recorded below); sensor noise sd 0.002 on x,y states
   (assumed "added to simulate sensor noise", arxiv.tex:1303); TV-derivative alpha=0.01,
   12 lagged-diffusivity iterations (Chartrand 2011 parameters not stated); 50-sample
   edge trim after differentiation (assumed; removes boundary artifacts); lambda=0.35
   (assumed; must sit below the ~0.92 cubic coefficients and above library cross-terms).
6. **Hopf omega sign**: displayed equation leaves omega unstated; Tab:Hopf signs imply
   the omega=-1 rotation sense. We match the table (see spec/targets.md).

## Known deviations

- The Hopf table acceptance is anchored to truth with tolerance 0.12, justified by the
  paper's own statement that its cubic terms are "off by almost 8%" (arxiv.tex:1305);
  our noise realization differs from theirs, so exact-value matching is not meaningful.
- Random seeds differ from the original MATLAB study by construction; all numeric
  tolerances were pre-registered in configs before the first run.

## Resolution log

Values chosen above are recorded in `configs/targets/*.json`; post-run metrics JSONs
next to each artifact record whether each hypothesis survived (support match + tolerances).

- **tab_ex1_3d, attempt 1 (superseded run):** poly order 3 at eta=0.05 produced spurious
  z/zz/zzz/xxz/yyz terms -- the exponential-rate degeneracy the paper itself warns about
  (arxiv.tex:618: higher-order powers of e^{lambda t} alias other exponential rates).
  Resolved to poly order 2 (paper: "second or third order"). Additionally, the displayed
  3D equation (arxiv.tex:612-616) and Tab:Ex1_3d disagree in off-diagonal sign convention;
  the appendix table (the claim anchor) matches the 2D example's rotation sense, so the
  simulated system follows the table. Both issues surfaced by the metrics gate refusing
  the comparison -- the run stays in the ledger as superseded evidence.
- **tab_logistic_coefficients, attempt 1 (superseded run):** a single initial condition
  per mu produced a dense, ill-conditioned fit (spurious r-polynomial terms with
  coefficients up to +/-14; the degree-5 r-monomials on the narrow grid [2.5, 3.95] are
  nearly collinear and absorb forcing noise). Resolved: five initial conditions per mu
  (x0 in {0.1,0.3,0.5,0.7,0.9}); recovery is then exact-support with max coefficient error
  ~0.0007 vs the paper table. Transient discard is immaterial once multiple ICs are used
  (tested both ways). The paper does not state its sampling protocol; multiple ICs is the
  minimal hypothesis that reproduces Tab:Logistic.
- **tab_logistic_coefficients, attempt 2 (superseded run):** multiple ICs alone were
  seed-fragile (2/5 seeds recovered support). Root cause: recording the *clipped*
  next-state as the regression target biases the residual at the domain edges, and the
  bias loads onto x-monomials (the spurious terms observed). Resolved: record the raw
  forced next-state as the target, clip only the continuing iterate; lambda=0.15 (chosen
  by a sweep -- the paper itself selects lambda by cross-validation on the Pareto front,
  arxiv.tex "Cross-validation to determine parsimonious sparse solution"). Robustness after
  fix: 5/5 seeds exact support, max coefficient error 0.0014 vs Tab:Logistic. Column
  normalization for STLS was also implemented and recorded as an available method option
  (authors' later published practice), but was not needed after the target fix.
- **tab_hopf_coefficients, attempt 1 (superseded run):** tv_alpha=0.01 over-regularized the
  TV derivative at sensor-noise sd 0.002, biasing the derivative estimates and producing a
  dense fit in u-cross terms. Isolation test: clean (noise-free, exact) derivatives recover
  the support with deviation 0.0000, proving the method core; tv_alpha=1e-4 with noise
  recovers exact support at max deviation 0.0049-0.0084 from truth across seeds 1509/7/42
  (well inside the paper's own ~8%). Resolved: tv_alpha=1e-4.
- **Shared-code provenance invalidation (workflow observation):** fixing src/targets.py for
  the logistic target invalidated the recorded code_sha256 of every previously matched
  target registered against that file; all targets were re-driven (fresh run + registration
  + comparison) against the settled code before completion. This is the harness working as
  designed -- shared-module edits force re-registration of downstream evidence.
