# SETUP: Obsidian + LLM Wiki (Karpathy pattern) — Debian & macOS

Reproducible runbook for setting up an LLM wiki on a fresh system, with Obsidian as the viewer and **an LLM agent (reference: Claude Code) as the wiki maintainer**. Tested on **Debian 13** (2026-07-08/09) and **macOS / Apple Silicon** (2026-07-17). The wiki itself is fully local (plain Markdown + Git); with local models it also runs entirely offline — see "Optional: Obsidian with a local LLM" below.

**To Claude:** Work through the steps in order. Detect the operating system yourself (`uname`) and use the matching OS part (B = Debian, C = macOS). First ask via AskUserQuestion: (1) vault path (default `~/llm-wiki`), (2) wiki language (default German), (3) install the Obsidian app or create the vault only.

> **Automation:** The OS-independent steps 1–3 and 6, plus app installation / vault registration (parts B/C), are also available as an Ansible playbook under `ansible/` (repository `setup-obsidian-llm-wiki`). Bootstrap ingest (step 4) and lint assessment remain LLM work.

---

## The concept in one paragraph

Three layers: `raw/` (immutable sources), `wiki/` (LLM-generated, cross-linked pages), `CLAUDE.md` (governing schema — turns Claude into a disciplined maintainer). Three operations: **Ingest** (one source updates 5–15 *existing* pages instead of creating a dump page), **Query** (cited synthesis from the wiki only), **Lint** (health check). Obsidian ingests nothing — it only renders the `.md` files live.

---

## Part A — Common steps (identical on Debian & macOS)

### Step 1 — Vault skeleton

```bash
mkdir -p ~/llm-wiki/raw ~/llm-wiki/wiki ~/llm-wiki/.claude/commands
```

### Step 2 — `CLAUDE.md` (governing schema, the most important file)

Write to `~/llm-wiki/CLAUDE.md` — core rules (wording may vary, content must not):

- **Role:** Claude is a maintainer, not a chatbot; the wiki is a cumulative artifact (condense while writing).
- **Layers:** `raw/` is immutable, file name `YYYY-MM-DD_<slug>.md`, URL sources get `url:` in the frontmatter; `wiki/` belongs to the LLM, flat (max. 1 subfolder level); change `CLAUDE.md` only when instructed.
- **Page types** (`type` in the frontmatter): `concept | entity | synthesis | comparison | moc`.
- **Mandatory frontmatter** on every wiki page: `type, created, updated, sources (list of raw paths), tags`.
- **Linking:** `[[Page Title]]`, titles unique vault-wide (defensive convention — Obsidian itself does not require full paths, "shortest path" suffices when unique). Red links = desired gap markers. Every page except the index needs ≥ 1 incoming link.
- **Operations:** Ingest (5–15 touches, existing pages first, maintain `00_Index`), Query (from `wiki/` only, name gaps instead of using world knowledge), Lint (report, no auto-fixes).
- **Style:** define the target language; condense instead of collect; separate fact from assessment.

### Step 3 — Slash commands

Three files under `~/llm-wiki/.claude/commands/` (they take effect when Claude Code is started inside the vault):

- **`ingest.md`** — `/ingest <url|path>`: place the source, dated, into `raw/` (mirror URLs via WebFetch), search `wiki/` for touched pages and **update** them (target 5–15), new pages only when no suitable target exists, cross-link, maintain `00_Index` + `sources`/`updated`, closing report (new vs. updated, red links).
- **`query.md`** — `/query <question>`: answer exclusively from `wiki/`, evidence as `[[links]]`, gaps stated explicitly + as ingest candidates.
- **`lint-wiki.md`** — `/lint-wiki`: broken/red links, orphans, schema violations (frontmatter, retroactively modified raw files via git diff, duplicate titles), contradictions/stale content, content gaps → prioritized report (P1 broken, P2 schema, P3 gaps).

### Step 4 — Bootstrap ingest

Place a first source into `raw/` (e.g. a research report; for local files, note origin/method/verification status in the frontmatter), generate 6–9 wiki pages from it + `wiki/00_Index.md` as the root MOC (type `moc`; sections e.g. Core Concepts / Tools / Ingest Candidates). Everything cross-linked, frontmatter per schema.

### Step 5 — Lint verification (deterministic, no LLM)

```bash
cd ~/llm-wiki && python3 - <<'EOF'
import re, pathlib
pages = {p.stem: p.read_text() for p in pathlib.Path('wiki').glob('*.md')}
errors = []
def strip_code(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)   # code blocks
    return re.sub(r'`[^`]*`', '', t)              # inline code
links = {n: set(re.findall(r'\[\[([^\]|#]+)', strip_code(t))) for n, t in pages.items()}
for n, ts in links.items():
    errors += [f"BROKEN: [[{t}]] in {n}" for t in ts if t not in pages]
incoming = {t: [s for s, ts in links.items() if t in ts and s != t] for t in pages}
errors += [f"ORPHAN: {t}" for t, inc in incoming.items() if t != '00_Index' and not inc]
for n, t in pages.items():
    fm = t.split('---')[1]
    errors += [f"FRONTMATTER: {f} missing in {n}" for f in ('type:','created:','updated:','sources:','tags:') if f not in fm]
    for s in re.findall(r'raw/\S+\.md', fm):
        if not pathlib.Path(s).exists(): errors.append(f"SOURCES: {s} missing ({n})")
print(f"{len(pages)} pages:", "LINT CLEAN" if not errors else "\n".join(errors))
EOF
```

Expectation: "LINT CLEAN" **or** exclusively BROKEN findings for the intentional red links (ingest candidates from the index) — anything else is a real error. The same check ships as `scripts/lint_wiki.py` (installed by the Ansible playbook).

> **Pitfall:** ALWAYS put meta-mentions of the link syntax (e.g. "use `[[Title]]`") in backticks — otherwise Obsidian renders them as red links; the lint above correctly ignores code spans.

### Step 6 — Git

```bash
cd ~/llm-wiki && printf '.obsidian/workspace*\n.trash/\n.DS_Store\n' > .gitignore && git init -q && git add -A && git commit -m "Initial LLM wiki vault (Karpathy pattern)"
```

(`.DS_Store` does no harm on Debian and avoids noise on macOS.)

---

## Part B — Debian: Obsidian app (optional, no root required)

```bash
mkdir -p ~/Applications
URL=$(curl -s https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | grep -o 'https://[^"]*Obsidian-[0-9.]*\.AppImage' | grep -v arm64 | head -1)
curl -sL -o ~/Applications/Obsidian.AppImage "$URL" && chmod +x ~/Applications/Obsidian.AppImage
```

**Pre-register the vault** (no vault picker on first start) — the registry lives at `~/.config/obsidian/obsidian.json`:

```bash
mkdir -p ~/.config/obsidian
printf '{"vaults":{"%s":{"path":"%s","ts":%s,"open":true}}}' "$(head -c8 /dev/urandom | od -An -tx1 | tr -d ' \n')" "$HOME/llm-wiki" "$(date +%s%3N)" > ~/.config/obsidian/obsidian.json
```

Desktop entry: `~/.local/share/applications/obsidian.desktop` with `Exec=$HOME/Applications/Obsidian.AppImage %u`, `MimeType=x-scheme-handler/obsidian;`. Requires FUSE (`fusermount3`). With xrdp/remote desktop, an "Exiting GPU process" log error is normal (software rendering).

---

## Part C — macOS: Obsidian app

**Installation** (unless already present at `/Applications/Obsidian.app`):

```bash
brew install --cask obsidian        # or download from obsidian.md
```

**Register the vault** — the registry lives at `~/Library/Application Support/obsidian/obsidian.json` (same JSON format as on Debian):

```bash
osascript -e 'quit app "Obsidian"' 2>/dev/null; sleep 2   # IMPORTANT if Obsidian is running — see pitfalls
python3 - "$HOME/llm-wiki" <<'EOF'
import json, pathlib, secrets, sys, time
vault = sys.argv[1]
p = pathlib.Path.home()/'Library/Application Support/obsidian/obsidian.json'
p.parent.mkdir(parents=True, exist_ok=True)
d = json.loads(p.read_text()) if p.exists() else {"vaults": {}}
if any(v.get('path') == vault for v in d['vaults'].values()):
    print("already registered:", vault)
else:
    d['vaults'][secrets.token_hex(8)] = {"path": vault, "ts": int(time.time()*1000), "open": True}
    p.write_text(json.dumps(d))
    print("registered:", vault)
EOF
open -a Obsidian
```

**Pitfalls (macOS, experienced 2026-07-17):**

- **Never edit the registry while the app is running** — Obsidian rewrites `obsidian.json` on quit and overwrites external changes. First `osascript -e 'quit app "Obsidian"'`, then edit, then relaunch.
- **`open "obsidian://open?path=…"` does not register a new vault folder** — for not-yet-registered paths nothing scriptable happens (a dialog may be waiting). For scripts, always use the registry approach above.
- **Obsidian cleans up after itself:** registry entries whose path no longer exists (e.g. after moving a vault folder) are removed automatically on the next start. Moved vaults must be re-registered once, or opened via "Open folder as vault".

---

## Operation

- Start Claude Code **inside the vault** (`cd ~/llm-wiki && claude`), then `/ingest`, `/query`, `/lint-wiki`.
- There is **no automatism**: files in `raw/` remain unprocessed until `/ingest` is invoked (cron automation is a later option).
- Division of labor: **heuristics** = everything that can be governed via file names/links/frontmatter (lint!); **AI** = understanding, assigning, condensing, linking.
- Deep-research reports are ideal raw sources; note method + verification status in the raw file's frontmatter.

## Optional: Obsidian with a local LLM

Yes — the wiki runs entirely on local models, on two levels:

**Level 1 — in-vault plugins (retrieval/chat in the Obsidian UI):**
- **Copilot** (logancyang): connects to any OpenAI-compatible endpoint — i.e. directly to a llama.cpp server (e.g. `http://LLMHOST:8084/v1`, model name = server alias) or Ollama (CORS toggle in the settings). For reliable vault RAG, enable embeddings — these too can be served by a llama.cpp embedding server (`--embeddings`, port 8085).
- **Smart Connections**: uses its own local embedding model (zero setup, no endpoint needed) for "Relevant Notes"; chat can be reconfigured to local endpoints (`http://localhost:11434` or similar).
- **LLM-Wiki plugin** (Obsidian forum): runs on Ollama by default, re-indexes on save, hybrid search — a pure *retriever*.

**Level 2 — the maintainer agent itself:** The Karpathy pattern is agent-agnostic. Instead of Claude Code, a locally connected agent (e.g. **Hermes** with `model.provider llamacpp`) can maintain the vault — `CLAUDE.md` applies as the schema analogously (Hermes reads project rules the same way). Quality note: ingest discipline (5–15 touches, dedup, clean links) is the most demanding task in the system — a 30B-class model can handle it, but should initially be monitored closely via `/lint-wiki`.

Rule of thumb: **local embeddings + retrieval is uncritical** (small models suffice), **local ingest authorship is feasible** but deserves oversight; in both cases the raw data never leaves your own network.
