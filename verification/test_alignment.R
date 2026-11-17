source("verification/edgecov_demo.R")
source("audit/alignment.R")
stopifnot(nrow(edgecov_demo()) == 4L)
design <- released_inputs()
e <- design$inputs
n <- e$multi_network
layer <- get.vertex.attribute(n, ".LayerName")
names_in_model <- network.vertex.names(n)
ids <- names_in_model[layer == "cash"]
raw_ids <- read.csv("upstream/BD_SharingUnit_NHB.csv", fileEncoding = "UTF-8-BOM")[[1L]]
stopifnot(length(raw_ids) == 79L, "BDSU019" %in% raw_ids,
          setequal(ids, setdiff(raw_ids, "BDSU019")), network.size(n) == 234L)
edges <- as.edgelist(n)
stopifnot(all(layer[edges[, 1]] == layer[edges[, 2]]))
keys <- c(cash = "Q1Q2", material = "Q3Q4", help = "Q5Q6")
encode <- function(tail, head) paste(tail, head, sep = ">")
for (key in names(keys)) {
  raw <- read.csv(sprintf("upstream/BD_Edgelist_%s_NHB.csv", keys[key]))
  raw <- subset(raw, Source %in% ids & Target %in% ids & Source != Target)
  expected <- if (key == "help") encode(raw$Target, raw$Source) else encode(raw$Source, raw$Target)
  ix <- edges[layer[edges[, 1]] == key, , drop = FALSE]
  actual <- encode(names_in_model[ix[, 1]], names_in_model[ix[, 2]])
  stopifnot(identical(names_in_model[layer == key], ids),
            identical(network.vertex.names(e[[paste0(key, "_network")]]), ids),
            setequal(actual, expected), !anyDuplicated(actual))
  if (key == "help") stopifnot(!setequal(actual, encode(raw$Source, raw$Target)))
}
args <- commandArgs(TRUE)
stopifnot(length(args) == 1L)
work <- args[1L]
dir.create(work, recursive = TRUE, showWarnings = FALSE)
aligned <- alignment_audit(list(env = e, released = design$formula), work)
for (name in c("distance_network", "kin_network")) {
  stopifnot(sum(ids == network.vertex.names(e[[name]])) == 12L)
}
for (m in list(e$distance_by_id, e$kinship_by_id)) {
  stopifnot(identical(dim(m), c(78L, 78L)), identical(rownames(m), ids),
            identical(colnames(m), ids), isSymmetric(m), all(is.finite(m)), all(diag(m) == 0))
}
restore <- function(expr) {
  if (!is.call(expr)) return(expr)
  if (identical(expr, quote(edgecov(distance_by_id)))) return(quote(edgecov(distance_network, "distance")))
  if (identical(expr, quote(edgecov(kinship_by_id)))) return(quote(edgecov(kin_network)))
  as.call(lapply(as.list(expr), restore))
}
stopifnot(identical(restore(aligned[[3]]), design$formula[[3]]),
          identical(aligned[[2]], design$formula[[2]]),
          identical(environment(aligned), environment(design$formula)),
          identical(unname(tail(summary(aligned), 21L)), unname(tail(summary(design$formula), 21L))))
cat("PASS: targeted edgecov tests, all directed support edges, ordering, exclusion, dimensions, and formula invariance.\n")
