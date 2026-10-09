# Document Standards

All documents follow a two-stage workflow:
1. Draft - written to the vault at `{vault}/[Project]/[Doc Type]/[filename].md`
2. Final - exported to the appropriate format when the user approves the draft

Vault path: `{vault}/`

---

## General Rules

- No emojis in any document or output
- No em-dashes (-- or the em-dash character). Use hyphens (-) or colons (:) for separation
- All documents use YAML frontmatter for metadata
- Dates use ISO format: `YYYY-MM-DD`
- Status values: `Draft`, `In Review`, `Approved`
- Tone: direct and concise - written for practitioners, not for performance
- Avoid filler phrases ("in order to", "it should be noted that", "as mentioned above")
- Tables preferred over nested bullets for comparisons, requirements, and structured data
- Every document includes a TL;DR or one-line summary at the top

---

## Document Types

### PRD (Product Requirements Document)
- **Audience**: Engineering team, cross-functional stakeholders
- **Vault location**: `[Project]/PRDs/[YYYY-MM-DD] [Feature Name].md`
- **Final format**: Word document (`.docx`), exported via `scripts/export_word.py`
- **Template**: `templates/prd.md`
- **Key sections**: TL;DR, Problem Statement, Goals & Metrics, Non-Goals, Requirements (MoSCoW), Risks, Open Questions

### User Story Map (USM)
- **Audience**: Engineering team
- **Vault location**: `[Project]/Story Maps/[YYYY-MM-DD] [Epic Name].md`
- **Final format**: Structured text exported via `scripts/export_figjam.py` - optimized for bulk copy-paste into FigJam as sticky notes organized by swim lane
- **Template**: `templates/user-story-map.md`
- **Hierarchy**: Activity -> Task -> Story (release rows optional)
- **Key rule**: Activities are the backbone (swim lane headers); Tasks sit under Activities; Stories sit under Tasks

### User Stories + Acceptance Criteria
- **Audience**: Engineering team, QA
- **Vault location**: `[Project]/Stories/[YYYY-MM-DD] [Epic or Feature Name].md`
- **Final format**: CSV uploaded to Jira, exported via `scripts/export_jira_csv.py`
- **Template**: `templates/user-story.md`
- **Story format**: As a [persona], I want to [action] so that [benefit]
- **AC format**: Given [context], when [action], then [expected result] - one criterion per line

**Jira CSV columns**: `Project`, `Issue Type`, `Summary`, `Description`
- Project: the Jira project key (from `tracker.projects` in config or passed to the export script)
- Issue Type is always `Story`
- Summary: 7 words max, derived from the user story (imperative, action-focused)
- Description: single formatted block containing all of the following in order:

```
[Value statement - what's being built, what problem it solves, why it matters. Elevator pitch, not spec doc.]

User Story:
As a [persona], I want to [action], so that [benefit].

Tasks:
- [task]

Acceptance Criteria:
- Given [context], when [action], then [expected result]

Non-Functional Requirements:
[BU, privacy, or security constraints the team needs to design around]

Technical/Architecture Signoff:
[Whether tech/arch has reviewed for feasibility. Flag if review is pending.]

Dependencies:
[Other teams, services, or work items this story is blocked by or blocks]

Risks:
| Risk | Likelihood | Impact | Mitigation |
```

### Decision Document
- **Audience**: Leadership, stakeholders
- **Vault location**: `[Project]/Decisions/[YYYY-MM-DD] [Decision Title].md`
- **Final format**: Word document (`.docx`), exported via `scripts/export_word.py`
- **Template**: `templates/decision-doc.md`
- **Structure**: Objective - The Problem - Context - Options - The Ask
- **Key rules**: Lead with what decision is needed; quantify the problem; present 2-3 options with pros/cons/risks; bold the recommendation so it is not buried; end with a named decision owner, DRI, and deadline

### Status Update
- **Audience**: Leadership (clarity-first) or Team (detail-first) - tailor for the reader
- **Vault location**: `[Project]/Status Updates/[YYYY-MM-DD] [Project] Status.md`
- **Final format**: Slack message. Use `*bold*` for section labels (renders in Slack). No `##` headers. No em-dashes. No Metrics table. Copy the body below the YAML frontmatter directly into Slack.
- **Template**: `templates/status-update.md`
- **Status values**: `Green` (on track), `Yellow` (at risk of missing targets), `Red` (goals will not be met without significant intervention)
- **Structure**: Headline - What Happened - What's Next - What's Blocked - Risks
- **Key rules**: No "Headline:" label - just write it. No separate Metrics section - embed numbers in bullets instead (e.g. "X of Y stories complete", "Z% coverage"). Risks include owner and mitigation inline. Use `*Section*` not `## Section`.
- **Jira data**: When a Jira MCP is available, query the relevant epic for story counts (total stories, stories complete, stories targeting current release) and embed those numbers in the What Happened bullets. If no Jira MCP is configured, note this and skip.

---

## Vault Folder Structure per Project

```
[Project Name]/
├── _context/
├── Meetings/
├── PRDs/
├── Story Maps/
├── Stories/
├── Decisions/
├── Status Updates/
└── Knowledge Graph/
    ├── graph.json
    ├── _index.md
    ├── _log.md
    ├── graph-view.md
    ├── pending/
    ├── approved/
    └── nodes/
```

---

## Export Scripts

| Script | Input | Output | Use for |
|--------|-------|--------|---------|
| `scripts/export_word.py` | Vault markdown file path | `.docx` in `docs/output/` | PRDs, Decision Docs |
| `scripts/export_jira_csv.py` | Vault markdown file path | `.csv` in `docs/output/` | User Stories |
| `scripts/export_figjam.py` | Vault markdown file path | `.txt` in `docs/output/` | User Story Maps |
