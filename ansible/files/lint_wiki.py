#!/usr/bin/env python3
"""Deterministischer Lint für das LLM-Wiki (Runbook Schritt 5) — kein LLM.

Prüft aus dem Vault-Root heraus (python3 scripts/lint_wiki.py):
  - KAPUTT:      [[Links]] ohne Zielseite (rote Links; absichtliche
                 Ingest-Kandidaten aus dem Index sind hier erwartbar)
  - VERWAIST:    Seiten ohne eingehenden Link (außer 00_Index)
  - FRONTMATTER: fehlende Pflichtfelder (type, created, updated, sources, tags)
  - SOURCES:     sources-Einträge, deren raw-Datei fehlt

Exit-Code 0 = LINT CLEAN, 1 = Findings vorhanden.
"""
import pathlib
import re
import sys

pages = {p.stem: p.read_text() for p in pathlib.Path("wiki").glob("*.md")}
errors = []


def strip_code(t: str) -> str:
    t = re.sub(r"```.*?```", "", t, flags=re.S)  # Code-Blöcke
    return re.sub(r"`[^`]*`", "", t)             # Inline-Code


links = {n: set(re.findall(r"\[\[([^\]|#]+)", strip_code(t))) for n, t in pages.items()}
for n, ts in links.items():
    errors += [f"KAPUTT: [[{t}]] in {n}" for t in ts if t not in pages]
incoming = {t: [s for s, ts in links.items() if t in ts and s != t] for t in pages}
errors += [f"VERWAIST: {t}" for t, inc in incoming.items() if t != "00_Index" and not inc]
for n, t in pages.items():
    fm = t.split("---")[1]
    errors += [f"FRONTMATTER: {f} fehlt in {n}"
               for f in ("type:", "created:", "updated:", "sources:", "tags:") if f not in fm]
    for s in re.findall(r"raw/\S+\.md", fm):
        if not pathlib.Path(s).exists():
            errors.append(f"SOURCES: {s} fehlt ({n})")

print(f"{len(pages)} Seiten:", "LINT CLEAN" if not errors else "\n".join(errors))
sys.exit(1 if errors else 0)
