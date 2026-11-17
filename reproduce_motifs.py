#!/usr/bin/env python3
"""Independent, dependency-free reproduction of the *observed* network motifs.

Source: Hwang et al. (2026), public anonymized MatlabMultinetwork data.
This is NOT a reproduction of the original ergm.multi model or Monte Carlo tests.
Downloads only published CSVs from a pinned GitHub commit, or reads local CSVs.

Usage:
  python reproduce_motifs.py --download --output results.json
  python reproduce_motifs.py --data-dir ./csv --output results.json
"""
import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

COMMIT = "054263ef3b75eb6550019e1168788c185f00b6b8"
BASE = f"https://raw.githubusercontent.com/JoonHwang-psu/MatlabMultinetwork/{COMMIT}/"
FILES = {
    "nodes": "BD_SharingUnit_NHB.csv",
    "financial": "BD_Edgelist_Q1Q2_NHB.csv",
    "material": "BD_Edgelist_Q3Q4_NHB.csv",
    "labor": "BD_Edgelist_Q5Q6_NHB.csv",
}
ATTRS = ("salaried", "land", "status")
LAYERS = ("financial", "material", "labor")
# Published Figure 3: observed *directed, status-marked* mutual ties.
EXPECTED_WITHIN = {
    "financial": {"salaried": 27, "land": 31, "status": 9},
    "material": {"salaried": 42, "land": 67, "status": 21},
    "labor": {"salaried": 11, "land": 11, "status": 6},
}
# Published Figure 4: observed, directional cross-layer, status-marked ties.
EXPECTED_CROSS = {
    "financial->material": {"salaried": 30, "land": 32, "status": 12},
    "material->financial": {"salaried": 27, "land": 36, "status": 9},
    "financial->labor": {"salaried": 20, "land": 18, "status": 9},
    "labor->financial": {"salaried": 18, "land": 20, "status": 9},
    "material->labor": {"salaried": 25, "land": 24, "status": 12},
    "labor->material": {"salaried": 19, "land": 27, "status": 11},
}


def read_rows(filename, data_dir, allow_download):
    local = data_dir / filename
    if local.exists():
        text = local.read_text(encoding="utf-8-sig")
    elif allow_download:
        with urlopen(BASE + filename, timeout=30) as response:
            text = response.read().decode("utf-8-sig")
        data_dir.mkdir(parents=True, exist_ok=True)
        local.write_text(text, encoding="utf-8")
    else:
        raise FileNotFoundError(f"Missing {local}; use --download for public research data")
    return list(csv.DictReader(io.StringIO(text)))


def construct(data_dir, download):
    raw_nodes = read_rows(FILES["nodes"], data_dir, download)
    attrs = {r["name"]: {k: int(r[k]) for k in ATTRS} for r in raw_nodes}
    # The authors' R source explicitly excludes BDSU019 from each graph.
    attrs.pop("BDSU019", None)
    edges = {}
    raw_stats = {}
    for layer in LAYERS:
        rows = read_rows(FILES[layer], data_dir, download)
        valid = [(r["Source"], r["Target"]) for r in rows
                 if r["Source"] != "BDSU019" and r["Target"] != "BDSU019"
                 and r["Source"] != r["Target"]]
        if layer == "labor":  # R script: reverse_edges(inv_help_graph)
            valid = [(b, a) for a, b in valid]
        pairs = set(valid)  # R script: simplify(..., remove.multiple=TRUE)
        unknown = {x for e in pairs for x in e if x not in attrs}
        if unknown:
            raise ValueError(f"Unknown node IDs in {layer}: {sorted(unknown)}")
        edges[layer] = pairs
        raw_stats[layer] = {
            "raw_rows": len(rows),
            "excluded_self_loops": sum(r["Source"] == r["Target"] for r in rows),
            "unique_directed_edges": len(pairs),
        }
    return len(raw_nodes), attrs, edges, raw_stats


def within_layer(edges, attrs):
    out = {}
    for layer, layer_edges in edges.items():
        out[layer] = {
            attr: sum(1 for a, b in layer_edges if (b, a) in layer_edges
                      and attrs[a][attr] == 1)
            for attr in ATTRS
        }
    return out


def cross_layer(edges, attrs):
    out = {}
    for source in LAYERS:
        for target in LAYERS:
            if source == target:
                continue
            out[f"{source}->{target}"] = {
                attr: sum(1 for a, b in edges[source]
                          if (b, a) in edges[target] and attrs[a][attr] == 1)
                for attr in ATTRS
            }
    return out


def degree_summary(edges, attrs):
    """A descriptive exploration, NOT adjusted estimates of a status effect."""
    out = {}
    for layer, layer_edges in edges.items():
        records = {}
        for attr in ATTRS:
            records[attr] = {}
            for value in (0, 1):
                group = {n for n in attrs if attrs[n][attr] == value}
                records[attr][str(value)] = {
                    "n": len(group),
                    "mean_out_degree": round(sum(a in group for a, b in layer_edges) / len(group), 4),
                    "mean_in_degree": round(sum(b in group for a, b in layer_edges) / len(group), 4),
                }
        out[layer] = records
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download pinned public CSVs")
    parser.add_argument("--data-dir", type=Path, default=Path("./hwang_data"))
    parser.add_argument("--output", type=Path, default=Path("./results.json"))
    args = parser.parse_args()
    original_n, attrs, edges, stats = construct(args.data_dir, args.download)
    within = within_layer(edges, attrs)
    cross = cross_layer(edges, attrs)
    matches = within == EXPECTED_WITHIN and cross == EXPECTED_CROSS
    payload = {
        "status": "INDEPENDENT OBSERVED MOTIF RECONSTRUCTION; ERGM NOT EXECUTED",
        "source_commit": COMMIT,
        "original_households": original_n,
        "analytical_nodes_after_exclusion": len(attrs),
        "status_group_sizes": {a: sum(v[a] == 1 for v in attrs.values()) for a in ATTRS},
        "layers": stats,
        "within_layer_status_reciprocity": within,
        "cross_layer_status_reciprocity": cross,
        "descriptive_degree_comparisons": degree_summary(edges, attrs),
        "matches_published_figure_3_and_figure_4_observed_values": matches,
        "limitations": [
            "No ergm.multi model fitted and no 1,000-network Monte Carlo simulation performed.",
            "Associations and counts do not identify causal effects or long-term persistence.",
            "Networks are primarily reported potential sources of support, not complete transaction histories.",
            "Binary status categories overlap, so group counts are not independent.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Raw households:", original_n, "| Analytic nodes:", len(attrs))
    print("Unique directed edges:", {k: len(v) for k, v in edges.items()})
    print("Published observed motif counts reproduced:", matches)
    print("Results:", args.output)
    if not matches:
        raise SystemExit("WARNING: Observed motif counts differ from the published values")


if __name__ == "__main__":
    main()
