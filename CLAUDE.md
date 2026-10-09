# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A product management toolkit for Claude Code. It centralizes product context, reusable templates, and Python-based analysis and export scripts. Product knowledge lives in a markdown vault (Obsidian or any folder) outside the repo, so the repo itself holds no product data.

## Loading Context (Do This First on Every Task)

### Step 0: Load config

Read `pdm.config.yaml` in the repo root. If it does not exist, stop and tell the user to run `python scripts/setup.py init`.

Use these placeholders everywhere in this file and in `.claude/commands/`:

- `{vault}`: `vault.path`, resolved relative to the repo root (`~` expands to the home folder)
- `{product}`: `active_product`
- `{user}`: `user.name`

Also read `context/about-me.md` if it exists.

### Step 1: Product context

1. The active product is `{product}` from Step 0
2. Read all files under `{vault}/{product}/_context/`:
   - `overview.md` - what the product is, users, current state
   - `stakeholders.md` - key people, roles, and how to engage them
   - `goals.md` - current OKRs and success metrics
   - `roadmap-status.md` - what is in flight, next, and at risk
   - `constraints.md` - legal, technical, and business constraints
   - `glossary.md` - product-specific terminology

### Step 1b: Active features tracker (for roadmap and status tasks)

If `{vault}/{product}/Tracker/active-features.md` exists, read it for any task involving feature status, roadmap planning, or in-flight work:
- This file is the PM-layer view of the roadmap: epics, story counts, stalled items, and PM notes
- It may be sourced from a tracker such as Jira but can contain PM context the tracker does not capture

### Step 2: Knowledge graph

3. Read `{vault}/{product}/Knowledge Graph/graph.json`
4. Read `{vault}/{product}/Knowledge Graph/_index.md`
5. Based on the task, load relevant node files from `{vault}/{product}/Knowledge Graph/nodes/`:
   - For any task involving a person: load their stakeholder node
   - For any task involving a feature or deliverable: load related commitment and milestone nodes
   - For PRDs, user stories, or decisions: load all constraint and decision nodes for the active product
   - For status updates: load all milestone and metric nodes for the active product
   - When uncertain which nodes are relevant, read the full index and load anything that overlaps with the task subject

### Step 3: Apply what you loaded

Use both the product context files and the knowledge graph when generating any output. The knowledge graph contains confirmed facts - commitments, decisions, constraints, and metrics - that must be reflected accurately. Do not contradict anything in the graph without flagging it explicitly.

To switch products: run `/switch-product [Product Name]` or edit `active_product` in `pdm.config.yaml`.

## Writing Standards

- No emojis in any output
- No em-dashes (-- or the em-dash character). Use hyphens (-) or colons (:) instead
- Tone: direct and concise
- See `context/document-standards.md` for full formatting rules per document type

## Environment Setup

```bash
python -m venv venv
venv/Scripts/activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python scripts/setup.py init
```

## Project Structure

- `pdm.config.yaml` - local config: user, vault path, active product, tracker (gitignored)
- `context/about-me.md` - the user's role and working context (gitignored)
- `context/document-standards.md` - formatting rules for all document types
- `context/knowledge-graph-schema.md` - node and edge types for the knowledge graph
- `context/git-commit-best-practices.md` - commit message conventions for this repo
- `templates/` - starter markdown for PRDs, user stories, user story maps, decision docs, status updates, and retros
- `templates/vault/` - stub files copied into the vault when a product is added
- `scripts/` - Python utilities:
  - `config.py` - load `pdm.config.yaml` and resolve vault and product paths
  - `setup.py` - `init` creates the config and first product; `add-product` scaffolds a product in the vault
  - `check_clean.py` - leak check: fails if tracked files contain absolute paths or personal terms
  - `analyze.py` - load and summarize Excel files from `data/`
  - `visualize.py` - Plotly charts saved to `docs/output/`
  - `export_word.py` - convert markdown drafts to Word documents
  - `export_jira_csv.py` - convert user stories markdown to Jira CSV
  - `export_figjam.py` - convert user story maps to FigJam-ready text
  - `parse_doc.py` - extract text from Word documents for ingestion
  - `knowledge_graph.py` - graph engine: query nodes, visualize DOT, rebuild index
- `data/` - Excel files for analysis (gitignored)
- `docs/output/` - generated exports (gitignored)

## Slash Commands

### `/new-notes [optional: file path]`
Ingestion pipeline for meeting notes. Identifies the project from the transcript, extracts key insights and the user's action items, writes a structured note to `{vault}/[Project]/Meetings/`, and appends the user's action items to `{vault}/Tasks/To-Do.md`.

- No argument: Claude looks for a pasted transcript in the conversation
- File path argument: reads `.docx` via `parse_doc.py` or `.txt`/`.md` directly

### `/switch-product [Product Name]`
Switches the active product context. Updates `active_product` in `pdm.config.yaml` and loads the new product's `_context/` files from the vault.

### `/new-doc [doc type]`
Drafts a PRD, user stories, user story map, decision doc, or status update from the templates and the loaded product context, and writes it to the vault.

### `/ingest-context [optional: file path]`
Reads a document or pasted text, extracts candidate nodes and edges that meet the fact quality rules, and writes a pending review file to `Knowledge Graph/pending/`. Nothing enters the graph until the user approves it.

### `/approve-context [file path]`
Reads a reviewed pending file, processes all checked items, writes node files, updates `graph.json`, rebuilds `_index.md`, appends to `_log.md`, regenerates the DOT visualization, and moves the file to `Knowledge Graph/approved/`.

### `/brief`
Competitive research brief for the active product. Searches the web for the last 48 hours of news across named competitors, broad product category, and emerging technology. Deduplicates against the prior brief. Writes a prioritized, categorized findings file to `{vault}/{product}/Research/YYYY-MM-DD Daily Brief.md`. Each finding is tagged: `[competitive-update]`, `[emerging-tech]`, or `[market-signal]`, with a secondary label of `closely related` or `exploratory` where applicable.

Personal commands that should not be shared go in `.claude/commands/local/` (gitignored).

## Running Scripts

```python
import sys; sys.path.insert(0, 'scripts')
import analyze, visualize

df = analyze.load("metrics.xlsx")
analyze.summarize(df)
visualize.bar(df, x="month", y="revenue", title="Monthly Revenue", save_as="revenue.html")
```

## MCP Configuration

Claude Code reads and writes the vault directly; no filesystem MCP server is needed. Optional MCP servers (for example Jira via `mcp-atlassian`) go in `.mcp.json`, which is gitignored. Start from `.mcp.example.json`.
