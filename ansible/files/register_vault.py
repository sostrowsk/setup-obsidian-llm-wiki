#!/usr/bin/env python3
"""Vault idempotent in Obsidians Vault-Registry (obsidian.json) eintragen.

Funktioniert für Debian (~/.config/obsidian/obsidian.json) und
macOS (~/Library/Application Support/obsidian/obsidian.json) —
das JSON-Format ist identisch.

Aufruf:
    register_vault.py --registry <pfad/obsidian.json> --vault <vault-pfad> [--check]

Exit-Codes:
    0  Vault ist registriert (bzw. wurde soeben eingetragen)
    3  nur mit --check: Vault ist NICHT registriert (Änderung nötig)

WICHTIG (macOS): Obsidian vor dem Schreiben beenden — die App schreibt
die Registry beim Beenden neu und überschreibt Fremd-Änderungen.
"""
import argparse
import json
import pathlib
import secrets
import sys
import time


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--check", action="store_true",
                    help="nur prüfen, nichts schreiben (Exit 3 = Eintrag fehlt)")
    args = ap.parse_args()

    registry = pathlib.Path(args.registry).expanduser()
    vault = str(pathlib.Path(args.vault).expanduser())

    data = json.loads(registry.read_text()) if registry.exists() else {"vaults": {}}
    data.setdefault("vaults", {})

    if any(v.get("path") == vault for v in data["vaults"].values()):
        print(f"PRESENT {vault}")
        return 0

    if args.check:
        print(f"MISSING {vault}")
        return 3

    data["vaults"][secrets.token_hex(8)] = {
        "path": vault,
        "ts": int(time.time() * 1000),
        "open": True,
    }
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(json.dumps(data))
    print(f"ADDED {vault}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
