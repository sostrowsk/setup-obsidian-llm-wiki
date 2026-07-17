# /ingest <url|pfad>

Ingestiere die Quelle `$ARGUMENTS` ins Wiki. Arbeite nach dem Schema in `CLAUDE.md`.

1. **Quelle nach `raw/` legen:** Datei kopieren bzw. URL per WebFetch spiegeln. Dateiname `YYYY-MM-DD_<slug>.md` (heutiges Datum). Bei URLs `url:` ins Frontmatter; Methode/Verifikationsstand der Quelle notieren. `raw/` ist immutable — existierende Dateien niemals ändern.
2. **Wiki durchsuchen:** Welche bestehenden Seiten berührt der Inhalt? Ziel: **5–15 Berührungen**, bestehende Seiten zuerst **aktualisieren** (verdichten, nicht anhängen). Neue Seiten nur anlegen, wenn kein passendes Ziel existiert.
3. **Quervernetzen:** Neue/geänderte Inhalte per `[[Links]]` verweben. Rote Links für bewusste Lücken sind erwünscht. Jede Seite (außer `00_Index`) braucht ≥ 1 eingehenden Link.
4. **Pflege:** Auf allen berührten Seiten `sources` (raw-Pfad ergänzen) und `updated` aktualisieren. `wiki/00_Index.md` aktualisieren (neue Seiten einsortieren, Ingest-Kandidaten pflegen).
5. **Abschlussbericht:** Was wurde neu angelegt vs. aktualisiert (mit Ein-Satz-Begründung), welche roten Links / Lücken entstanden sind.
