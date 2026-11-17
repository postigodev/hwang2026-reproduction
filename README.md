# Hwang et al. (2026) reproduction and covariate audit

An independent check of the observed network motifs and household ordering in the released multilayer ERGM for *Reciprocal exchanges across multilayered networks show an emerging patron–client system led by salaried households*. [Article](https://doi.org/10.1017/ehs.2026.10061) · [Pinned author release](https://github.com/JoonHwang-psu/MatlabMultinetwork/tree/054263ef3b75eb6550019e1168788c185f00b6b8)

- [Technical report (PDF)](verification/TECHNICAL_REPORT.pdf) · [HTML-rendered text](verification/TECHNICAL_REPORT.md)
- [Reviewer guide](REVIEW.md) with runnable checks for all 27 observed motif counts and the distance and kinship assignments
- [Audit results](AUDIT.md) with aggregate fit and simulation evidence

The observed counts reproduce. In the tested Statnet environment, the released code reads the distance and kinship matrices by position. Only 12 of 78 household IDs occupy the same positions in each matrix as in the support networks. Aligning both matrix axes by household ID recovers the covariates for the intended pairs.

The original fitting and simulation records are needed to establish whether the published analysis used that same ordering and to explain the reported Monte Carlo p-value of 0.062 for salaried financial reciprocity.

The reviewer guide downloads the original scripts and data directly from the authors’ pinned revision and checks their Git blob IDs. The public repository contains independent verification code, the report, and aggregate outputs. Keep the downloaded inputs and the generated pair-level results in the ignored local directories.
