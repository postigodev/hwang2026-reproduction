import csv
from collections import defaultdict
from math import isclose
from pathlib import Path
import sys


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def pair(tail, head):
    return tuple(sorted((tail, head)))


def main(out):
    dyads = rows(out / "dyad-assignments.csv")
    ids = {r["model"] for r in rows(out / "vertex-order.csv")}
    expected_keys = {(i, j) for i in ids for j in ids if i != j}
    assert len(dyads) == len(expected_keys) == 78 * 77
    assert {(r["tail"], r["head"]) for r in dyads} == expected_keys
    distance = defaultdict(list)
    kin = set()
    for row in rows(Path("upstream/BD_Distance_NHB.csv")):
        if (row["ui"], row["uj"]) in expected_keys:
            distance[pair(row["ui"], row["uj"])].append(float(row["distance"]))
    for row in rows(Path("upstream/BD_Edgelist_kinship_NHB.csv")):
        kin.add(pair(row["Source"], row["Target"]))
    support = {}
    for layer, suffix in zip(("cash", "material", "help"), ("Q1Q2", "Q3Q4", "Q5Q6")):
        edges = {(r["Source"], r["Target"]) for r in rows(Path(f"upstream/BD_Edgelist_{suffix}_NHB.csv"))}
        support[layer] = {(j, i) if layer == "help" else (i, j)
                          for i, j in edges if (i, j) in expected_keys}
    totals = defaultdict(int)
    for dyad in dyads:
        endpoints = dyad["tail"], dyad["head"]
        key = pair(*endpoints)
        for name in ("distance", "kinship"):
            positional = dyad[f"{name}_tail_used"], dyad[f"{name}_head_used"]
            totals[f"{name}_ordered_ID_mismatch"] += endpoints != positional
            totals[f"{name}_unordered_ID_mismatch"] += key != pair(*positional)
            for version, lookup in (("released", pair(*positional)), ("aligned", key)):
                values = distance[lookup] if name == "distance" else [int(lookup in kin)]
                assert values and isclose(float(dyad[f"{name}_{version}"]),
                                          sum(values) / len(values), abs_tol=1e-8)
            wrong = not isclose(float(dyad[f"{name}_released"]), float(dyad[f"{name}_aligned"]),
                                rel_tol=0, abs_tol=1e-8)
            totals[f"{name}_value_mismatch_all"] += wrong
            totals[f"{name}_value_mismatch_observed_tie_incidences"] += wrong * sum(
                endpoints in edges for edges in support.values())
        for layer, edges in support.items():
            assert (dyad[layer] == "TRUE") == (endpoints in edges)
    recorded = rows(Path("audit/evidence/dyad-summary.csv"))
    expected_totals = {row["metric"]: int(row["count"]) for row in recorded}
    assert totals == expected_totals
    with (out / "dyad-summary.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("metric", "count"))
        writer.writerows(totals.items())
    print(f"Verified all {len(dyads)} dyads and {sum(map(len, support.values()))} support tie incidences.")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
