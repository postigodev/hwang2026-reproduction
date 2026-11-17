for (pkg in c("ergm", "ergm.multi", "network")) {
  cat(pkg, as.character(packageVersion(pkg)), "\n")
}
for (item in list(c("network", "as.matrix.network.adjacency"),
                  c("ergm", "ergm_edgecov_args"), c("ergm", "InitErgmTerm.edgecov"))) {
  cat("\n", item[1], ":::", item[2], "\n", sep = "")
  code <- deparse(getFromNamespace(item[2], item[1]))
  print_lines <- grep("as.matrix|dim|vertex.names|network.size|as.double|inputs|xm|matrix.type", code)
  cat(code[print_lines], sep = "\n")
}
