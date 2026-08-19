#!/usr/bin/env python3
"""Sinh sơ đồ luồng Mermaid từ docker-compose.yml."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose" / "docker-compose.yml"
OUTPUT = ROOT / "evidence" / "flow-diagram.mmd"


def main():
    with open(COMPOSE) as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    networks = data.get("networks", {})

    lines = ["flowchart LR"]
    lines.append('  subgraph DMZ["Miền DMZ (net_dmz)"]')
    for name, svc in services.items():
        nets = svc.get("networks", {})
        if "net_dmz" in (nets if isinstance(nets, dict) else nets):
            if "gateway" not in name and name != "probe":
                lines.append(f"    {name}[{name}]")
    lines.append("  end")

    lines.append('  subgraph GW1["Cổng DMZ↔APP"]')
    lines.append("    gateway-dmz-app[gateway-dmz-app]")
    lines.append("  end")

    lines.append('  subgraph APP["Miền APP (net_app)"]')
    for name, svc in services.items():
        nets = svc.get("networks", {})
        if "net_app" in (nets if isinstance(nets, dict) else nets):
            if "gateway" not in name and name != "probe":
                lines.append(f"    {name}[{name}]")
    lines.append("  end")

    lines.append('  subgraph GW2["Cổng APP↔DATA"]')
    lines.append("    gateway-app-data[gateway-app-data]")
    lines.append("  end")

    lines.append('  subgraph DATA["Miền DATA (net_data)"]')
    for name, svc in services.items():
        nets = svc.get("networks", {})
        if "net_data" in (nets if isinstance(nets, dict) else nets):
            if "gateway" not in name and name != "probe":
                lines.append(f"    {name}[{name}]")
    lines.append("  end")

    lines += [
        "  dmz-web -->|HTTP :8000| gateway-dmz-app",
        "  gateway-dmz-app -->|HTTP :5000| app-api",
        "  app-api -->|TCP :5432| gateway-app-data",
        "  gateway-app-data -->|TCP :5432| data-db",
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()
