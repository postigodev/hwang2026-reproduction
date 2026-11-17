"""Fetch and verify the released files against the pinned Git tree manifest."""
import argparse
import hashlib
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_URL = "https://raw.githubusercontent.com/JoonHwang-psu/MatlabMultinetwork/054263ef3b75eb6550019e1168788c185f00b6b8/"


def blob_id(data):
    blob = f"blob {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(blob).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fetch missing or mismatched inputs")
    args = parser.parse_args()
    upstream = ROOT / "upstream"
    if args.download:
        upstream.mkdir(exist_ok=True)
    manifest = (ROOT / "upstream-tree.txt").read_text(encoding="ascii").splitlines()
    for line in manifest:
        metadata, name = line.split("\t")
        _, _, expected = metadata.split()
        path = upstream / name
        if path.is_file() and blob_id(path.read_bytes()) == expected:
            continue
        if not args.download:
            parser.exit(1, f"Missing or mismatched input: {name}. Run again with --download.\n")
        with urlopen(UPSTREAM_URL + name, timeout=30) as response:
            data = response.read()
        if blob_id(data) != expected:
            parser.exit(1, f"Downloaded input has an unexpected Git blob ID: {name}\n")
        path.write_bytes(data)
    print(f"Verified {len(manifest)} pinned upstream Git blobs.")


if __name__ == "__main__":
    main()
