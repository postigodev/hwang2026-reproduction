# Household ordering in the multilayer ERGM

Hwang et al. (2026) · Independent technical review

The released R code assigns some distances and kinship indicators to the wrong household pairs. Each covariate matrix shares the same 78 household IDs as the support networks, but only 12 IDs occupy the same positions. The observed motif counts reproduce independently. Whether the published fit used the same covariate ordering remains unknown. [Article](https://doi.org/10.1017/ehs.2026.10061) · [Released source revision](https://github.com/JoonHwang-psu/MatlabMultinetwork/tree/054263ef3b75eb6550019e1168788c185f00b6b8)

## How the assignment was checked

The three support layers use the same vertex order. In `network` 1.19.0, converting a covariate network to a matrix retains that network’s own order. In `ergm` 4.8.1, `edgecov()` checks the dimensions and passes numeric values to the model by position. The household IDs attached to the matrix never reach the term. [Versioned implementation](https://github.com/statnet/ergm/blob/4.8.1/R/InitErgmTerm.R)

The R demonstration runs the released network construction against the pinned CSVs and stops before fitting. It keeps the 78 vertices in model order and evaluates one observed financial tie at a time. After reindexing both matrix axes by household ID, the contributions agree with direct CSV lookups. Distance lookups average records for an undirected pair, following the released code.

Table 1. Covariate assignments for two observed financial ties

| Financial tie | Covariate | Pair used by released code | Released | ID-aligned |
|---|---|---|---:|---:|
| BDSU049 to BDSU001 | Distance | BDSU045 / BDSU001 | 37.779337 | 43.079279 |
| BDSU049 to BDSU001 | Kinship | BDSU046 / BDSU001 | 0 | 1 |
| BDSU024 to BDSU002 | Distance | BDSU023 / BDSU002 | 259.406463 | 87.059777 |
| BDSU024 to BDSU002 | Kinship | BDSU023 / BDSU002 | 0 | 1 |

An independent check covered all 6,006 ordered pairs. Among 546 observed ties across the three layers, alignment changes the distance value for 504 ties and the kinship value for 394. The distance sum across observed ties moves from 55,628.83 to 30,189.12. The kinship sum moves from 114 to 506. [Dyad summary](https://github.com/postigodev/hwang2026-reproduction/blob/main/audit/evidence/dyad-summary.csv)

<!-- page -->

## What changes in the fitted model

The sensitivity analysis changes the two covariate arguments. Tests reconstruct every directed support edge from the CSVs, verify the exclusion of BDSU019 and the reversal of labor ties, and check that both 78 × 78 covariate matrices are finite, symmetric, and keyed by household ID on both axes. Reversing the two substitutions recovers the released formula exactly. The other 21 observed model statistics and all 27 observed motif counts agree across specifications.

Table 2. Matched fits using the released and ID-aligned covariates

| Quantity | Released construction | ID-aligned |
|---|---:|---:|
| Kinship coefficient (log odds) | 0.18844 | 3.58325 |
| Kinship standard error | 0.06124 | 0.18990 |
| Kinship 95% Wald CI (log odds) | 0.06841–0.30846 | 3.21106–3.95544 |
| Kinship odds ratio (95% Wald CI) | 1.207 (1.071–1.361) | 35.990 (24.805–52.219) |
| Distance odds ratio per 100 recorded units | 0.820 | 0.647 |

The odds ratio compares kin and non-kin pairs at the same values of the other change statistics. In the aligned data, 506 of 1,752 kin dyads and 40 of 16,266 non-kin dyads have a tie, counting eligible directed pairs separately in each layer. The conditional pseudolikelihood design has full rank (23 of 23) across those 18,018 observations. A linear program testing for complete or quasi-complete separation returned an optimum of zero at a tolerance of 0.0000001. This screen addresses the conditional pseudolikelihood. Existence and global stability of the ERGM maximum-likelihood estimate remain open. [Separation screen](https://github.com/postigodev/hwang2026-reproduction/blob/main/verification/results/separation-screen.csv)

Both fits used seed 890716 and Hummel stopping. The aligned fit reported `failure = FALSE` after four iterations and two unit steps. The saved estimation chain has 2,098 draws, an effective sample size of 148 for kinship, and a Geweke z of 1.19. Two saved post-fit chains averaged 507.55 and 504.09 kin ties, compared with 506 observed. Their mean edge counts in each layer were within 1.35 of the observed counts. Those chains stayed near the observed densities, while distant modes could remain undetected. [Fit comparison and diagnostics](https://github.com/postigodev/hwang2026-reproduction/blob/main/AUDIT.md#fitted-sensitivity-analysis)

<!-- page -->

## What remains unresolved

The published Monte Carlo p-value of 0.062 for salaried financial reciprocity remains unexplained. Using the released inclusive two-tail rule on the same reproduced fit, one seed yielded one draw equal to the observed count of 27 and none above it (p = 0.002). Another yielded 21 equal and 52 above (p = 0.146). The estimates ranged from 0.002 to 0.260 across six runs and from 0.136 to 0.274 across four runs with wider spacing. Median motif effective sample size increased from 24 to 65 of 1,000 draws. The original fit and simulation records would help establish how the published value was obtained.

In four wider-spaced chains from the aligned fit, all three highlighted cross-layer panels gave p-values above 0.05 under the released strict-tail rule. These results are conditional on the aligned fit and come from a small number of chains with serial dependence. Global mixing remains uncertain. The study’s cross-sectional reports of potential support allow an associational interpretation. [Simulation comparisons](https://github.com/postigodev/hwang2026-reproduction/blob/main/AUDIT.md#monte-carlo-comparisons)

## Reproduce the checks

The recorded environment was Windows x64 with R 4.3.2, `ergm` 4.8.1, `ergm.multi` 0.2.1.1, `network` 1.19.0, and `igraph` 2.1.4. Both matched fits used lpSolveAPI after a GLPK fallback. The public checks reconstruct the observed motifs and covariate assignments. Aggregate results from the fitted runs and the separation screen are linked above.

Fetch and verify the pinned inputs, restore the recorded packages using the reviewer guide, and run these commands from the repository root. [Reviewer guide](https://github.com/postigodev/hwang2026-reproduction/blob/main/REVIEW.md) · [Public audit evidence](https://github.com/postigodev/hwang2026-reproduction/blob/main/AUDIT.md)

```
python workflow/verify_upstream.py --download
Rscript --vanilla verification/edgecov_demo.R
Rscript --vanilla verification/test_alignment.R runs/review-alignment
Rscript --vanilla verification/package_implementation.R
python audit/verify_alignment.py runs/review-alignment
```
