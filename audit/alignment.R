alignment_audit <- function(design, out) {
  env <- design$env
  layers <- c("cash", "material", "help")
  n <- env$multi_network
  layer <- network::get.vertex.attribute(n, ".LayerName")
  model_ids <- network::network.vertex.names(n)
  ids <- model_ids[layer == "cash"]
  stopifnot(length(ids) == 78L, !anyDuplicated(ids))
  ids_of <- network::network.vertex.names
  vertex <- data.frame(position = seq_along(ids), model = ids)
  for (key in layers) {
    vertex[[paste0(key, "_graph")]] <- igraph::V(env[[paste0(key, "_graph")]])$name
    vertex[[paste0(key, "_view")]] <- ids_of(env[[paste0(key, "_network")]])
    vertex[[paste0(key, "_model")]] <- model_ids[layer == key]
    stopifnot(identical(ids, vertex[[paste0(key, "_view")]]),
              identical(ids, vertex[[paste0(key, "_model")]]))
  }
  vertex$distance <- ids_of(env$distance_network)
  vertex$kinship <- ids_of(env$kin_network)
  write.csv(vertex, file.path(out, "vertex-order.csv"), row.names = FALSE)

  distance <- as.matrix(env$distance_network, attrname = "distance")
  kinship <- as.matrix(env$kin_network)
  for (matrix in list(distance, kinship)) {
    stopifnot(setequal(rownames(matrix), ids), identical(rownames(matrix), colnames(matrix)))
  }
  env$distance_by_id <- distance[ids, ids]
  env$kinship_by_id <- kinship[ids, ids]
  dyads <- expand.grid(i = seq_along(ids), j = seq_along(ids))
  ij <- as.matrix(dyads[dyads$i != dyads$j, ])
  detail <- data.frame(tail = ids[ij[, 1]], head = ids[ij[, 2]],
                       distance_released = distance[ij], distance_aligned = env$distance_by_id[ij],
                       kinship_released = kinship[ij], kinship_aligned = env$kinship_by_id[ij],
                       distance_tail_used = vertex$distance[ij[, 1]], distance_head_used = vertex$distance[ij[, 2]],
                       kinship_tail_used = vertex$kinship[ij[, 1]], kinship_head_used = vertex$kinship[ij[, 2]])
  checks <- lapply(layers, function(key) {
    edges <- igraph::as_edgelist(env[[paste0(key, "_graph")]])
    adjacency <- matrix(FALSE, length(ids), length(ids), dimnames = list(ids, ids))
    adjacency[edges] <- TRUE
    detail[[key]] <<- adjacency[ij]
    actual <- summary(as.formula(sprintf(
      "multi_network ~ L(~edgecov(distance_network, 'distance') + edgecov(kin_network), ~%s)", key), env = env))
    corrected <- summary(as.formula(sprintf(
      "multi_network ~ L(~edgecov(distance_by_id) + edgecov(kinship_by_id), ~%s)", key), env = env))
    expected <- c(sum(distance[adjacency]), sum(kinship[adjacency]))
    aligned <- c(sum(env$distance_by_id[adjacency]), sum(env$kinship_by_id[adjacency]))
    stopifnot(isTRUE(all.equal(unname(actual), expected)),
              isTRUE(all.equal(unname(corrected), aligned)))
    data.frame(layer = key, covariate = c("distance", "kinship"),
               released = expected, aligned = aligned,
               wrong_tie_values = c(sum(abs(distance[adjacency] - env$distance_by_id[adjacency]) > 1e-8),
                                    sum(kinship[adjacency] != env$kinship_by_id[adjacency])),
               ties = sum(adjacency))
  })
  write.csv(detail, file.path(out, "dyad-assignments.csv"), row.names = FALSE)
  write.csv(do.call(rbind, checks), file.path(out, "alignment-statistics.csv"), row.names = FALSE)
  aligned <- design$released
  aligned[[3]] <- str2lang(sub("edgecov\\(distance_network, \"distance\"\\) \\+ edgecov\\(kin_network\\)",
                             "edgecov(distance_by_id) + edgecov(kinship_by_id)",
                             deparse1(aligned[[3]])))
  stopifnot(!identical(aligned, design$released), identical(environment(aligned), env))
  aligned
}
