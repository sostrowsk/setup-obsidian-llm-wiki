# setup-obsidian-llm-wiki

Reproduzierbares Setup für ein **LLM-Wiki nach dem Karpathy-Muster**: Obsidian als Viewer, ein LLM-Agent (Referenz: Claude Code) als disziplinierter Wiki-Maintainer. Für **Debian** und **macOS**.

## Konzept

Drei Schichten, drei Operationen:

| | |
|---|---|
| `raw/` | unveränderliche Quellen (`YYYY-MM-DD_<slug>.md`) |
| `wiki/` | LLM-generierte, quervernetzte Seiten mit Pflicht-Frontmatter |
| `CLAUDE.md` | Governing Schema — macht aus dem LLM einen Maintainer statt Chatbot |

**Ingest** (eine Quelle aktualisiert 5–15 *bestehende* Seiten statt Sammel-Eintrag) · **Query** (zitierte Synthese nur aus dem Wiki) · **Lint** (Health-Check, Report ohne Auto-Fixes). Obsidian ingestiert nichts — es rendert die `.md`-Dateien nur live.

Details, Pitfalls und die manuellen Schritte: **[SETUP-OBSIDIAN-LLM-WIKI.md](SETUP-OBSIDIAN-LLM-WIKI.md)** (Runbook, getestet auf Debian 13 und macOS).

## Schnellstart mit Ansible

Automatisiert die deterministischen Teile des Runbooks: Vault-Gerüst, `CLAUDE.md`, Slash-Commands, Lint-Skript, Git-Init sowie Obsidian-Installation und Vault-Registrierung (Debian: AppImage + Desktop-Eintrag; macOS: Homebrew-Cask). Das Playbook erkennt das OS selbst.

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
```

### Variablen (`ansible/group_vars/all.yml`, per `-e` überschreibbar)

| Variable | Default | Bedeutung |
|---|---|---|
| `vault_path` | `~/llm-wiki` | Zielpfad des Vaults |
| `wiki_language` | `Deutsch` | Zielsprache im Governing Schema |
| `install_obsidian` | `true` | App installieren + Vault registrieren (`false` = nur Vault) |
| `launch_obsidian` | `false` | Obsidian am Ende starten (nur macOS) |

Das Playbook ist idempotent und **überschreibt nie ein bestehendes Vault**: Alle Vault-Dateien werden mit `force: false` kopiert; die Obsidian-Registry wird nur ergänzt, wenn der Eintrag fehlt (auf macOS wird die App dafür vorher sauber beendet — Pitfall siehe Runbook).

### Voraussetzungen

- Ansible ≥ 2.14, Python 3, Git (mit konfigurierter Commit-Identität)
- Debian: FUSE (`fusermount3`) für AppImages
- macOS: [Homebrew](https://brew.sh) (nur falls Obsidian noch fehlt)

## Danach: Bootstrap-Ingest (LLM-Arbeit, nicht automatisierbar)

```bash
cd ~/llm-wiki && claude
# dann: /ingest <erste Quelle>  ·  /query <frage>  ·  /lint-wiki
```

Verifikation jederzeit deterministisch ohne LLM:

```bash
cd ~/llm-wiki && python3 scripts/lint_wiki.py
```

## Repo-Layout

```
SETUP-OBSIDIAN-LLM-WIKI.md      Runbook (Debian & macOS, manuelle Schritte + Pitfalls)
ansible/
├── playbook.yml                Einstieg, OS-Weiche
├── inventory.ini               Default: localhost
├── group_vars/all.yml          Variablen
├── tasks/{common,debian,macos}.yml
├── templates/                  CLAUDE.md.j2, obsidian.desktop.j2
└── files/                      Slash-Commands, lint_wiki.py, register_vault.py, gitignore
```

Es werden keinerlei Zugangsdaten oder API-Keys benötigt oder abgelegt.

## Lizenz

[MIT](LICENSE)
