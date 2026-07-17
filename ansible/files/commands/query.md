# /query <frage>

Beantworte die Frage: `$ARGUMENTS`

Regeln (siehe `CLAUDE.md`):

1. **Nur aus `wiki/` antworten.** Kein Weltwissen einmischen — das Wiki ist die einzige Quelle.
2. **Belege als `[[Links]]`:** Jede wesentliche Aussage mit der Wiki-Seite belegen, aus der sie stammt.
3. **Lücken explizit machen:** Was das Wiki nicht abdeckt, klar benennen — und als Ingest-Kandidat vorschlagen (was müsste ingestiert werden, um die Lücke zu schließen?).
4. Fakt von Einschätzung trennen; Antwort auf Deutsch.
