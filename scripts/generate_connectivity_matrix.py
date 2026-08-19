#!/usr/bin/env python3
"""Sinh ma trận kết nối từ compose + policy."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose" / "docker-compose.yml"
POLICY = ROOT / "config" / "policy" / "default-deny.yaml"
OUTPUT = ROOT / "evidence" / "connectivity-matrix.json"

NODES = ["dmz-web", "gateway-dmz-app", "app-api", "gateway-app-data", "data-db"]


def main():
    with open(POLICY) as f:
        policy = yaml.safe_load(f)

    allowed = {}
    for exc in policy.get("exceptions", []):
        key = f"{exc['from']}->{exc['to']}"
        allowed[key] = {"port": exc["port"], "reason": exc["reason"]}

    matrix = {}
    for src in NODES:
        matrix[src] = {}
        for dst in NODES:
            if src == dst:
                matrix[src][dst] = "SELF"
            else:
                key = f"{src}->{dst}"
                if key in allowed:
                    matrix[src][dst] = "ALLOW"
                else:
                    matrix[src][dst] = "DENY"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump({"matrix": matrix, "exceptions": policy.get("exceptions", [])}, f, indent=2)
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()
