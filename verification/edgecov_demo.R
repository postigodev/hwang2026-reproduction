# Run from the repository root. Evaluate only the released data construction.
released_inputs <- function() {
  inputs <- new.env()
  inputs$read.csv <- function(file, ...) utils::read.csv(file.path("upstream", basename(file)), ...)
  for (expr in parse("upstream/MatlabMultinet.R")) {
    if (is.call(expr) && identical(expr[[1]], quote(`<-`)) &&
        identical(expr[[2]], quote(fundamental))) {
      return(list(inputs = inputs, formula = eval(expr[[3]][[2]], inputs)))
    }
    invisible(eval(expr, inputs))
  }
  stop("Released fit expression is missing")
}

edgecov_demo <- function() {
  x <- released_inputs()$inputs
  ids <- network.vertex.names(x$cash_network)
  d <- as.matrix(x$distance_network, attrname = "distance")
  k <- as.matrix(x$kin_network)
  raw_d <- read.csv("upstream/BD_Distance_NHB.csv")
  raw_k <- read.csv("upstream/BD_Edgelist_kinship_NHB.csv")
  pair_rows <- function(a, b, i, j) (a == i & b == j) | (a == j & b == i)
  expected <- function(i, j) {
    c(distance = mean(raw_d$distance[pair_rows(raw_d$ui, raw_d$uj, i, j)]),
      kinship = as.integer(any(pair_rows(raw_k$Source, raw_k$Target, i, j))))
  }
  stopifnot(length(ids) == 78L, !anyDuplicated(ids))
  results <- lapply(c("BDSU049:BDSU001", "BDSU024:BDSU002"), function(pair) {
    hh <- strsplit(pair, ":", fixed = TRUE)[[1L]]
    ij <- match(hh, ids)
    stopifnot(any(apply(as.edgelist(x$cash_network), 1L, function(e) all(e == ij))))
    one_tie <- network.initialize(length(ids), directed = TRUE)
    network.vertex.names(one_tie) <- ids
    add.edge(one_tie, ij[1], ij[2])
    released <- summary(one_tie ~ edgecov(x$distance_network, "distance") + edgecov(x$kin_network))
    aligned <- summary(one_tie ~ edgecov(d[ids, ids]) + edgecov(k[ids, ids]))
    from_csv <- expected(hh[1], hh[2])
    d_pair <- rownames(d)[ij]
    k_pair <- rownames(k)[ij]
    stopifnot(isTRUE(all.equal(unname(aligned), unname(from_csv))),
              isTRUE(all.equal(unname(released),
                               unname(c(expected(d_pair[1], d_pair[2])[1], expected(k_pair[1], k_pair[2])[2])))),
              all(released != aligned))
    data.frame(tail = hh[1], head = hh[2], covariate = names(from_csv),
               released_lookup = c(paste(d_pair, collapse = " / "), paste(k_pair, collapse = " / ")),
               released_value = unname(released), id_aligned_value = unname(aligned),
               raw_csv_value = unname(from_csv))
  })
  do.call(rbind, results)
}

if (sys.nframe() == 0L) {
  out <- edgecov_demo()
  print(out, row.names = FALSE, digits = 11)
  if (length(commandArgs(TRUE))) write.csv(out, commandArgs(TRUE)[1L], row.names = FALSE)
}
