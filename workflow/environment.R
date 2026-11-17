required_packages <- c("igraph", "sna", "statnet", "intergraph", "stargazer",
                       "latticeExtra", "ergm.multi", "network")
if (any(c("--install", "--install-binary") %in% commandArgs(TRUE))) {
  dir.create(Sys.getenv("R_LIBS_USER"), recursive = TRUE, showWarnings = FALSE)
  .libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))
  type <- if ("--install-binary" %in% commandArgs(TRUE)) "binary" else getOption("pkgType")
  install.packages(required_packages, repos = "https://cloud.r-project.org", type = type)
}
if ("--restore-windows" %in% commandArgs(TRUE)) {
  stopifnot(.Platform$OS.type == "windows", as.character(getRversion()) %in% c("4.6.2", "4.3.2"))
  library_path <- Sys.getenv("R_LIBS_USER")
  stopifnot(nzchar(library_path))
  dir.create(library_path, recursive = TRUE, showWarnings = FALSE)
  .libPaths(c(library_path, .libPaths()))
  run <- if (getRversion() == "4.3.2") "patched-r43" else "patched"
  minor <- paste(R.version$major, strsplit(R.version$minor, ".", fixed = TRUE)[[1]][1], sep = ".")
  lock <- read.csv(file.path("evidence", run, "packages.csv"))
  lock <- lock[!lock$Package %in% installed.packages(lib.loc = .Library)[, "Package"], ]
  installed <- installed.packages(lib.loc = library_path)
  needed <- !paste(lock$Package, lock$Version) %in% paste(installed[, "Package"], installed[, "Version"])
  urls <- sprintf("https://cloud.r-project.org/bin/windows/contrib/%s/%s_%s.zip",
                  minor, lock$Package[needed], lock$Version[needed])
  if (length(urls)) install.packages(urls, repos = NULL, type = "win.binary", lib = library_path)
  active <- vapply(lock$Package, function(pkg) packageDescription(pkg, fields = "Version"), character(1))
  stopifnot(identical(unname(active), lock$Version))
}
available <- vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
print(available)
versions <- as.data.frame(installed.packages()[, c("Package", "Version", "Built")])
print(versions[order(versions$Package), ], row.names = FALSE)
print(sessionInfo())
if (!all(available)) quit(status = 1)
