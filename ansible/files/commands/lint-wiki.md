# /lint-wiki

Health-Check des Wikis. **Nur Report, keine Auto-Fixes.**

Prüfe:

1. **Kaputte/rote Links:** `[[Ziele]]` ohne existierende Seite (Code-Blöcke und Inline-Code ignorieren). Erwünschte Lücken-Marker von Tippfehlern unterscheiden.
2. **Waisen:** Seiten ohne eingehenden Link (außer `00_Index`).
3. **Schema-Verstöße:** fehlende Frontmatter-Felder (`type`, `created`, `updated`, `sources`, `tags`); ungültige `type`-Werte; `sources`-Einträge, deren raw-Datei fehlt; nachträglich geänderte raw-Dateien (via `git diff`/`git log` gegen `raw/`); vault-weit doppelte Seitentitel.
4. **Inhalt:** Widersprüche zwischen Seiten, veraltete Stände (Quelle neuer als `updated`), Content-Lücken.

Ausgabe als priorisierter Report: **P1** kaputt (Links, fehlende sources), **P2** Schema (Frontmatter, Waisen, Duplikate, raw-Mutationen), **P3** Lücken/Inhalt. Pro Finding: Datei, Problem, Fix-Vorschlag.
