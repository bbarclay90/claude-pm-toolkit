# claude-pm-toolkit

A product management workspace for Claude Code: slash commands for meeting notes, product documents, competitive briefs, and a per-product knowledge graph. Your product knowledge lives in your own markdown vault (Obsidian or any folder), so this repo holds the framework and nothing about your products.

---

## Requirements

- Python 3.11+
- [Claude Code](https://claude.com/claude-code)

Optional:
- [Obsidian](https://obsidian.md) to browse and edit the vault
- [Graphviz](https://graphviz.org/download/) and the [obsidian-graphviz](https://github.com/QAMichaelPeng/obsidian-graphviz) plugin to render the knowledge graph view
- `uvx` and [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) for Jira integration

---

## Setup

```bash
git clone https://github.com/bbarclay90/claude-pm-toolkit.git
cd claude-pm-toolkit
python -m venv venv
venv/Scripts/activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python scripts/setup.py init
```

`init` asks for:
- **Your name and aliases** - used to find your action items in meeting transcripts
- **Vault path** - where product knowledge lives. The default `./vault` creates a folder inside the repo (gitignored). To use an existing Obsidian vault, give its path, for example `~/Obsidian/My Vault`.
- **First product name** - creates `{vault}/{product}/` with stub context files and an empty knowledge graph

If the vault is outside the repo, `init` adds it to `.claude/settings.local.json` so Claude Code can read and write it.

After setup, fill in the six files under `{vault}/{product}/_context/`. Every command reads them.

---

## Configuration

`pdm.config.yaml` (created by `init`, gitignored):

```yaml
user:
  name: Jane Doe
  role: Product Manager
  aliases: [Jane]

vault:
  path: ./vault              # relative to this file, ~ allowed, or an absolute path

active_product: Acme

# Optional: remove if you do not use Jira
tracker:
  type: jira
  url: https://jira.example.com
  username: jdoe
  projects: [ABC]

# Optional: extra terms the leak check blocks from commits
leak_check:
  deny: []
```

Local files that are never committed:

| File | Purpose |
|------|---------|
| `pdm.config.yaml` | Your config |
| `context/about-me.md` | Your role and working style, read on every task |
| `.mcp.json` | MCP servers and their credentials (start from `.mcp.example.json`) |
| `.claude/settings.local.json` | Local Claude Code permissions, including the vault path |
| `.claude/commands/local/` | Personal slash commands you do not want to share |

---

## Slash Commands

Run these inside Claude Code. Restart Claude Code after changing command files.

### `/new-notes [optional: file path]`
Processes a meeting transcript. Identifies the project, extracts key decisions and insights, finds your action items, writes a note to `{vault}/[Project]/Meetings/`, and appends your action items to `{vault}/Tasks/To-Do.md`. With no argument it uses a transcript pasted into the conversation; with a path it reads `.docx`, `.txt`, or `.md`.

### `/switch-product [Product Name]`
Sets `active_product` in `pdm.config.yaml` and loads that product's context.

### `/new-doc [doc type]`
Drafts a PRD, user stories, user story map, decision doc, or status update from the templates and the product context, and writes it to the vault. Status updates pull story counts from Jira when a tracker is configured.

### `/ingest-context [optional: file path]`
Extracts candidate facts (people, commitments, decisions, constraints, metrics) from a document and writes a review file to `Knowledge Graph/pending/`. Nothing enters the graph until you approve it.

### `/approve-context [file path]`
Processes a reviewed pending file: writes node files, updates `graph.json`, rebuilds the index and log, and regenerates the graph view.

### `/brief`
Competitive research brief for the active product covering the last 48 hours. Writes a prioritized, tagged findings file to `{vault}/{product}/Research/`.

---

## Adding a product

```bash
python scripts/setup.py add-product "Product Name"
```

Existing files are never overwritten, so this is safe to run on a product that already exists.

---

## Scheduling the daily brief

**Windows:** create a Task Scheduler task that runs:

```
powershell -File scripts/run-brief.ps1
```

with the repo folder as the working directory. Logs go to `logs/`. Headless runs cannot ask for permission, so the script allows the tools `/brief` needs (web search and fetch, and file read and write).

**macOS / Linux:** add a cron line:

```
0 8 * * * cd /path/to/claude-pm-toolkit && mkdir -p logs && claude --print "/brief" --allowedTools "WebSearch,WebFetch,Read,Write,Edit,Glob" >> logs/brief.log 2>&1
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `config.py` | Loads `pdm.config.yaml` and resolves vault and product paths |
| `setup.py` | `init` and `add-product` |
| `knowledge_graph.py` | Query the graph, print stats, regenerate the DOT view |
| `export_word.py` | Markdown draft to Word |
| `export_jira_csv.py` | User stories markdown to Jira CSV (project key defaults to the first `tracker.projects` entry) |
| `export_figjam.py` | User story map to FigJam-ready text |
| `parse_doc.py` | Extract text from Word documents |
| `analyze.py`, `visualize.py` | Excel analysis and Plotly charts |
| `check_clean.py` | Leak check for absolute paths and personal terms |

---

## Contributing

Before pushing:

```bash
python -m pytest
python scripts/check_clean.py
```

`check_clean.py` fails if any tracked file contains an absolute path or a term from your config (your name, aliases, and `leak_check.deny`).
