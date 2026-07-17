# SETUP: Obsidian + LLM-Wiki (Karpathy-Muster) — Debian & macOS

Reproduzierbares Runbook, um auf einem frischen System ein LLM-Wiki mit Obsidian als Viewer und **Claude Code als Wiki-Maintainer** aufzusetzen. Getestet auf **Debian 13** (2026-07-08/09) und **macOS / Apple Silicon** (2026-07-17).

**An Claude:** Arbeite die Schritte der Reihe nach ab. Erkenne das Betriebssystem selbst (`uname`) und nutze den passenden OS-Teil (B = Debian, C = macOS). Frage vorab per AskUserQuestion: (1) Vault-Pfad (Default `~/llm-wiki`), (2) Wiki-Sprache (Default Deutsch), (3) Obsidian-App installieren oder nur Vault anlegen.

> **Automatisierung:** Die OS-unabhängigen Schritte 1–3 und 6 sowie die App-Installation/Vault-Registrierung (Teil B/C) gibt es auch als Ansible-Playbook unter `ansible/` (Repo `setup-obsidian-llm-wiki`). Bootstrap-Ingest (Schritt 4) und Lint-Bewertung bleiben LLM-Arbeit.

---

## Konzept in einem Absatz

Drei Schichten: `raw/` (unveränderliche Quellen), `wiki/` (LLM-generierte, quervernetzte Seiten), `CLAUDE.md` (governing schema — macht aus Claude einen disziplinierten Maintainer). Drei Operationen: **Ingest** (eine Quelle aktualisiert 5–15 *bestehende* Seiten statt Sammel-Eintrag), **Query** (zitierte Synthese nur aus dem Wiki), **Lint** (Health-Check). Obsidian ingestiert nichts — es rendert nur die `.md`-Dateien live.

---

## Teil A — Gemeinsame Schritte (Debian & macOS identisch)

### Schritt 1 — Vault-Gerüst

```bash
mkdir -p ~/llm-wiki/raw ~/llm-wiki/wiki ~/llm-wiki/.claude/commands
```

### Schritt 2 — `CLAUDE.md` (Governing Schema, wichtigste Datei)

Nach `~/llm-wiki/CLAUDE.md` schreiben — Kernregeln (Formulierung darf variieren, Inhalte nicht):

- **Rolle:** Claude ist Maintainer, kein Chatbot; das Wiki ist ein kumulierendes Artefakt (verdichten beim Schreiben).
- **Schichten:** `raw/` immutable, Dateiname `YYYY-MM-DD_<slug>.md`, URL-Quellen mit `url:` im Frontmatter; `wiki/` gehört dem LLM, flach (max. 1 Unterordner-Ebene); `CLAUDE.md` nur auf Anweisung ändern.
- **Seitentypen** (`type` im Frontmatter): `concept | entity | synthesis | comparison | moc`.
- **Frontmatter-Pflicht** auf jeder Wiki-Seite: `type, created, updated, sources (Liste von raw-Pfaden), tags`.
- **Verlinkung:** `[[Seitentitel]]`, Titel vault-weit eindeutig (defensive Konvention — Obsidian selbst verlangt keine Voll-Pfade, „shortest path" reicht bei Eindeutigkeit). Rote Links = erwünschte Lücken-Marker. Jede Seite außer dem Index braucht ≥ 1 eingehenden Link.
- **Operationen:** Ingest (5–15 Berührungen, bestehende Seiten zuerst, `00_Index` pflegen), Query (nur aus `wiki/`, Lücken benennen statt Weltwissen), Lint (Report, keine Auto-Fixes).
- **Stil:** Zielsprache festlegen; verdichten statt sammeln; Fakt von Einschätzung trennen.

### Schritt 3 — Slash-Commands

Drei Dateien unter `~/llm-wiki/.claude/commands/` (wirken, wenn Claude Code im Vault gestartet wird):

- **`ingest.md`** — `/ingest <url|pfad>`: Quelle datiert nach `raw/` (URL per WebFetch spiegeln), `wiki/` nach berührten Seiten durchsuchen und **aktualisieren** (Ziel 5–15), neue Seiten nur ohne passendes Ziel, quervernetzen, `00_Index` + `sources`/`updated` pflegen, Abschlussbericht (neu vs. aktualisiert, rote Links).
- **`query.md`** — `/query <frage>`: Antwort ausschließlich aus `wiki/`, Belege als `[[Links]]`, Lücken explizit + als Ingest-Kandidat.
- **`lint-wiki.md`** — `/lint-wiki`: kaputte/rote Links, Waisen, Schema-Verstöße (Frontmatter, nachträglich geänderte raw-Dateien via git diff, Titel-Duplikate), Widersprüche/veraltete Stände, Content-Lücken → priorisierter Report (P1 kaputt, P2 Schema, P3 Lücken).

### Schritt 4 — Bootstrap-Ingest

Erste Quelle nach `raw/` legen (z. B. einen Research-Report; bei lokalen Dateien Herkunft/Methode/Verifikationsstand ins Frontmatter), daraus 6–9 Wiki-Seiten generieren + `wiki/00_Index.md` als Root-MOC (type `moc`; Rubriken z. B. Kernkonzepte / Tools / Ingest-Kandidaten). Alles quervernetzt, Frontmatter nach Schema.

### Schritt 5 — Lint-Verifikation (deterministisch, kein LLM)

```bash
cd ~/llm-wiki && python3 - <<'EOF'
import re, pathlib
pages = {p.stem: p.read_text() for p in pathlib.Path('wiki').glob('*.md')}
errors = []
def strip_code(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)   # Code-Blöcke
    return re.sub(r'`[^`]*`', '', t)              # Inline-Code
links = {n: set(re.findall(r'\[\[([^\]|#]+)', strip_code(t))) for n, t in pages.items()}
for n, ts in links.items():
    errors += [f"KAPUTT: [[{t}]] in {n}" for t in ts if t not in pages]
incoming = {t: [s for s, ts in links.items() if t in ts and s != t] for t in pages}
errors += [f"VERWAIST: {t}" for t, inc in incoming.items() if t != '00_Index' and not inc]
for n, t in pages.items():
    fm = t.split('---')[1]
    errors += [f"FRONTMATTER: {f} fehlt in {n}" for f in ('type:','created:','updated:','sources:','tags:') if f not in fm]
    for s in re.findall(r'raw/\S+\.md', fm):
        if not pathlib.Path(s).exists(): errors.append(f"SOURCES: {s} fehlt ({n})")
print(f"{len(pages)} Seiten:", "LINT CLEAN" if not errors else "\n".join(errors))
EOF
```

Erwartung: „LINT CLEAN" **oder** ausschließlich KAPUTT-Meldungen zu den absichtlichen roten Links (Ingest-Kandidaten aus dem Index) — alles andere ist ein echter Fehler.

> **Pitfall:** Meta-Erwähnungen der Link-Syntax (z. B. „nutze `[[Titel]]`") IMMER in Backticks setzen — sonst rendert Obsidian sie als rote Links; der Lint oben ignoriert Code-Spans korrekt.

### Schritt 6 — Git

```bash
cd ~/llm-wiki && printf '.obsidian/workspace*\n.trash/\n.DS_Store\n' > .gitignore && git init -q && git add -A && git commit -m "Initial LLM-Wiki-Vault nach Karpathy-Muster"
```

(`.DS_Store` schadet auf Debian nicht und erspart auf macOS Rauschen.)

---

## Teil B — Debian: Obsidian-App (optional, ohne root)

```bash
mkdir -p ~/Applications
URL=$(curl -s https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | grep -o 'https://[^"]*Obsidian-[0-9.]*\.AppImage' | grep -v arm64 | head -1)
curl -sL -o ~/Applications/Obsidian.AppImage "$URL" && chmod +x ~/Applications/Obsidian.AppImage
```

**Vault vorregistrieren** (kein Vault-Picker beim ersten Start) — Registry liegt unter `~/.config/obsidian/obsidian.json`:

```bash
mkdir -p ~/.config/obsidian
printf '{"vaults":{"%s":{"path":"%s","ts":%s,"open":true}}}' "$(head -c8 /dev/urandom | od -An -tx1 | tr -d ' \n')" "$HOME/llm-wiki" "$(date +%s%3N)" > ~/.config/obsidian/obsidian.json
```

Desktop-Eintrag: `~/.local/share/applications/obsidian.desktop` mit `Exec=$HOME/Applications/Obsidian.AppImage %u`, `MimeType=x-scheme-handler/obsidian;`. Voraussetzung FUSE (`fusermount3`). Bei xrdp/Remote-Desktop ist ein „Exiting GPU process"-Log-Fehler normal (Software-Rendering).

---

## Teil C — macOS: Obsidian-App

**Installation** (falls nicht schon unter `/Applications/Obsidian.app`):

```bash
brew install --cask obsidian        # oder Download von obsidian.md
```

**Vault registrieren** — Registry liegt unter `~/Library/Application Support/obsidian/obsidian.json` (gleiches JSON-Format wie auf Debian):

```bash
osascript -e 'quit app "Obsidian"' 2>/dev/null; sleep 2   # WICHTIG, falls Obsidian läuft — s. Pitfalls
python3 - "$HOME/llm-wiki" <<'EOF'
import json, pathlib, secrets, sys, time
vault = sys.argv[1]
p = pathlib.Path.home()/'Library/Application Support/obsidian/obsidian.json'
p.parent.mkdir(parents=True, exist_ok=True)
d = json.loads(p.read_text()) if p.exists() else {"vaults": {}}
if any(v.get('path') == vault for v in d['vaults'].values()):
    print("schon registriert:", vault)
else:
    d['vaults'][secrets.token_hex(8)] = {"path": vault, "ts": int(time.time()*1000), "open": True}
    p.write_text(json.dumps(d))
    print("registriert:", vault)
EOF
open -a Obsidian
```

**Pitfalls (macOS, erlebt 2026-07-17):**

- **Registry nie unter laufender App editieren** — Obsidian schreibt `obsidian.json` beim Beenden neu und überschreibt Fremd-Änderungen. Erst `osascript -e 'quit app "Obsidian"'`, dann editieren, dann neu starten.
- **`open "obsidian://open?path=…"` registriert keinen neuen Vault-Ordner** — für noch nicht registrierte Pfade passiert nichts Automatisierbares (ggf. wartet ein Dialog). Für Skripte immer den Registry-Weg oben nehmen.
- **Obsidian räumt selbst auf:** Registry-Einträge, deren Pfad nicht mehr existiert (z. B. nach Verschieben eines Vault-Ordners), werden beim nächsten Start automatisch entfernt. Verschobene Vaults müssen einmal neu registriert bzw. per „Open folder as vault" geöffnet werden.

---

## Betrieb

- Claude Code **im Vault starten** (`cd ~/llm-wiki && claude`), dann `/ingest`, `/query`, `/lint-wiki`.
- Es gibt **keinen Automatismus**: Dateien in `raw/` bleiben unverarbeitet bis zum `/ingest`-Aufruf (Cron-Automation ist eine spätere Option).
- Arbeitsteilung: **Heuristik** = alles, was sich über Dateinamen/Links/Frontmatter regeln lässt (Lint!); **KI** = verstehen, zuordnen, verdichten, verlinken.
- Deep-Research-Reports eignen sich ideal als raw-Quellen; im Frontmatter der raw-Datei Methode + Verifikationsstand notieren.

## Optional: Obsidian mit lokalem LLM

Ja, das Wiki läuft komplett mit lokalen Modellen — auf zwei Ebenen:

**Ebene 1 — In-Vault-Plugins (Retrieval/Chat in der Obsidian-UI):**
- **Copilot** (logancyang): verbindet sich mit jedem OpenAI-kompatiblen Endpoint — also direkt mit einem llama.cpp-Server (z. B. `http://LLMHOST:8084/v1`, Modellname = Server-Alias) oder Ollama (CORS-Toggle in den Settings). Für zuverlässiges Vault-RAG Embeddings aktivieren — auch die kann ein llama.cpp-Embedding-Server (`--embeddings`, Port 8085) liefern.
- **Smart Connections**: nutzt ein eigenes lokales Embedding-Modell (zero-setup, kein Endpoint nötig) für „Relevant Notes"; für Chat auf lokale Endpoints umkonfigurierbar (`http://localhost:11434` o. ä.).
- **LLM-Wiki-Plugin** (Obsidian-Forum): läuft standardmäßig über Ollama, re-indexiert beim Speichern, Hybrid-Suche — reiner *Retriever*.

**Ebene 2 — der Maintainer-Agent selbst:** Das Karpathy-Muster ist agent-agnostisch. Statt Claude Code kann auch ein lokal angebundener Agent (z. B. **Hermes** mit `model.provider llamacpp`, siehe `SETUP-HERMES-HONCHO.md`) den Vault pflegen — `CLAUDE.md` als Schema gilt sinngemäß (Hermes liest Projektregeln analog). Qualitäts-Hinweis: Ingest-Disziplin (5–15 Berührungen, Dedup, saubere Links) ist die anspruchsvollste Aufgabe im System — mit einem 30B-Klasse-Modell funktioniert sie, sollte aber anfangs per `/lint-wiki` engmaschig kontrolliert werden.

Faustregel: **Embeddings + Retrieval lokal ist unkritisch** (kleine Modelle reichen), **Ingest-Autorschaft lokal ist möglich**, verdient aber Kontrolle; die Rohdaten verlassen in beiden Fällen nie das eigene Netz.
