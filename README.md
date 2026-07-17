# Fully Autonomous, 100 % Local LLM Wiki — Works Without an Internet Connection

**Self-maintaining knowledge wiki following the Karpathy pattern: Obsidian as the viewer, an LLM agent as a disciplined wiki maintainer. Everything lives in plain Markdown on your own disk — and with local models (llama.cpp / Ollama / Hermes), ingest, query, and retrieval run entirely offline. Your data never leaves your machine.**

For **Debian** and **macOS**, as a manual runbook and as an Ansible playbook.

## Concept

Three layers, three operations:

| | |
|---|---|
| `raw/` | immutable sources (`YYYY-MM-DD_<slug>.md`) |
| `wiki/` | LLM-generated, cross-linked pages with mandatory frontmatter |
| `CLAUDE.md` | governing schema — turns the LLM into a maintainer instead of a chatbot |

**Ingest** (one source updates 5–15 *existing* pages instead of creating a dump page) · **Query** (cited synthesis from the wiki only) · **Lint** (health check, report without auto-fixes). Obsidian ingests nothing — it only renders the `.md` files live.

Details, pitfalls, and the manual steps: **[SETUP-OBSIDIAN-LLM-WIKI.md](SETUP-OBSIDIAN-LLM-WIKI.md)** (runbook, tested on Debian 13 and macOS).

## Offline / air-gapped operation

- **At runtime, no cloud service is required.** The vault is plain Markdown + Git on local disk; Obsidian renders locally.
- **Retrieval/chat inside Obsidian:** plugins (Copilot, Smart Connections) connect to any OpenAI-compatible *local* endpoint — a llama.cpp server on your machine or LAN is enough; embeddings included.
- **The maintainer agent itself can be local too:** instead of the cloud-based reference agent (Claude Code), a locally connected agent such as **Hermes** with `model.provider llamacpp` maintains the vault. A 30B-class model handles ingest discipline; verify it with the deterministic lint (`python3 scripts/lint_wiki.py` — no LLM involved).
- Internet is only needed **once, during installation** (downloading Obsidian/packages) — and not even then if you mirror the installers.

## Quick start with Ansible

Automates the deterministic parts of the runbook: vault skeleton, `CLAUDE.md`, slash commands, lint script, git init, plus Obsidian installation and vault registration (Debian: AppImage + desktop entry; macOS: Homebrew cask). The playbook detects the OS by itself.

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
```

### Variables (`ansible/group_vars/all.yml`, override with `-e`)

| Variable | Default | Meaning |
|---|---|---|
| `vault_path` | `~/llm-wiki` | target path of the vault |
| `wiki_language` | `Deutsch` | target language written into the governing schema |
| `install_obsidian` | `true` | install the app + register the vault (`false` = vault only) |
| `launch_obsidian` | `false` | launch Obsidian at the end (macOS only) |

The playbook is idempotent and **never overwrites an existing vault**: all vault files are copied with `force: false`; the Obsidian registry is only extended if the entry is missing (on macOS the app is quit cleanly first — see the pitfall in the runbook).

### Requirements

- Ansible ≥ 2.14, Python 3, Git (with a configured commit identity)
- Debian: FUSE (`fusermount3`) for AppImages
- macOS: [Homebrew](https://brew.sh) (only if Obsidian is not installed yet)

## Afterwards: bootstrap ingest (LLM work, not automatable)

```bash
cd ~/llm-wiki && claude        # or your local agent, e.g. hermes
# then: /ingest <first source>  ·  /query <question>  ·  /lint-wiki
```

Deterministic verification at any time, without an LLM:

```bash
cd ~/llm-wiki && python3 scripts/lint_wiki.py
```

## Repository layout

```
SETUP-OBSIDIAN-LLM-WIKI.md      runbook (Debian & macOS, manual steps + pitfalls)
ansible/
├── playbook.yml                entry point, OS switch
├── inventory.ini               default: localhost
├── group_vars/all.yml          variables
├── tasks/{common,debian,macos}.yml
├── templates/                  CLAUDE.md.j2, obsidian.desktop.j2
└── files/                      slash commands, lint_wiki.py, register_vault.py, gitignore
```

No credentials or API keys are required or stored anywhere in this setup.

## License

[MIT](LICENSE)
