# Audit results

## Covariate alignment

The R test verifies that reindexing the two matrices preserves all other formula terms and the other 21 observed model statistics. The independent CSV check covers all 6,006 eligible directed pairs, including 546 observed directed support ties across the three layers. [Layer statistics](audit/evidence/alignment-statistics.csv) · [Independent mismatch counts](audit/evidence/dyad-summary.csv) · [Runnable checks](REVIEW.md#verify-the-covariate-assignments)

## Fitted sensitivity analysis

The matched Hummel fits used the released model terms with the original positional or ID-aligned distance and kinship covariates. The kinship odds ratio changed from 1.207 (95% Wald CI 1.071–1.361) to 35.990 (24.805–52.219). The conditional pseudolikelihood screen found no evidence of separation in the aligned design. The saved chain diagnostics leave global mixing uncertain. [Coefficient comparison](audit/evidence/coefficient-comparison.csv) · [Fit diagnostics](audit/evidence/fit-diagnostics.csv) · [Estimation-chain diagnostics](audit/evidence/estimation-chain-diagnostics.csv) · [Separation screen](verification/results/separation-screen.csv)

## Monte Carlo comparisons

The reported p-value of 0.062 for salaried financial reciprocity remains unexplained. Using the released inclusive rule, six runs from the reproduced default fit gave p-values from 0.002 to 0.260. Four wider-spaced runs from that fit gave 0.136 to 0.274. Median effective sample size for the motif increased from 24 to 65 of 1,000 draws. In four wider-spaced chains from the aligned fit, all three highlighted cross-layer panels gave p-values above 0.05 under the strict-tail rule. The reported ranges describe the runs performed. [Simulation summaries](audit/evidence/replicate-summary.csv) · [Paired simulation comparison](audit/evidence/paired-simulation-comparison.csv)

The downloadable data and runnable checks support the positional-assignment finding. The audit tables summarize earlier fitted runs. The original publication fit and simulation records remain necessary to determine whether the paper used the same ordering and to trace its reported p-value.
