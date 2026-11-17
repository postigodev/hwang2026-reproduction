# Reviewer guide

Run these commands from the repository root. Python 3.9 or newer is sufficient for the first check and the independent dyad verifier. The download requires internet access and stores the pinned inputs under the ignored `upstream/` directory.

## Verify the observed motifs

```text
python workflow/verify_upstream.py --download
python reproduce_motifs.py --data-dir upstream --output runs/review-observed.json
python -c "import json; from pathlib import Path; assert json.loads(Path('runs/review-observed.json').read_bytes()) == json.loads(Path('observed.json').read_bytes()); print('Saved observed results match')"
```

Expect 12 verified Git blobs, 78 analytical households, and 176 financial, 236 material, and 134 labor ties. A successful run reproduces all 27 observed motif counts in Figures 3 and 4. [Saved counts](observed.json)

## Verify the covariate assignments

The tested environment was Windows x64 with R 4.3.2, `ergm` 4.8.1, `ergm.multi` 0.2.1.1, and `network` 1.19.0. Use the R 4.3.2 executable in the PowerShell commands below. The restore requires access to the recorded CRAN binaries. R may emit warnings for packages built under R 4.3.3 and deprecated `igraph` calls in the released code.

```powershell
python workflow/verify_upstream.py --download
if ($LASTEXITCODE -ne 0) { throw 'Input verification failed.' }
$r = 'Rscript'
$env:R_LIBS_USER = Join-Path $PWD '.runtime/review-library-r43'
Remove-Item Env:LC_ALL,Env:LC_CTYPE -ErrorAction SilentlyContinue
& $r --vanilla workflow/environment.R --restore-windows
if ($LASTEXITCODE -ne 0) { throw 'Package restore failed.' }
& $r --vanilla verification/edgecov_demo.R
if ($LASTEXITCODE -ne 0) { throw 'Dyad demonstration failed.' }
& $r --vanilla verification/test_alignment.R runs/review-alignment
if ($LASTEXITCODE -ne 0) { throw 'Alignment test failed.' }
python audit/verify_alignment.py runs/review-alignment
```

For the directed financial tie from `BDSU049` to `BDSU001`, the released distance is 37.779337 and the aligned distance is 43.079279 (rounded). The kinship indicator changes from 0 to 1. The aligned values agree with direct CSV lookups. The R test should print `PASS` and the independent Python check should report 6,006 verified dyads and 546 support tie incidences. [Aggregate cross-check](audit/evidence/dyad-summary.csv)

These checks stop before fitting the model. The [audit results](AUDIT.md) provide aggregate evidence from the earlier fitted runs and the Monte Carlo comparisons.
