You are helping the user create a product management document. Follow each step in order. Do not skip steps or combine them.

Argument received: `$ARGUMENTS`

---

## Step 1: Determine the document type

Parse `$ARGUMENTS` for one of the following doc types:

| Keyword(s) | Doc Type |
|------------|----------|
| `prd` | PRD (Product Requirements Document) |
| `stories`, `user-stories` | User Stories |
| `usm`, `user-story-map`, `story-map` | User Story Map |
| `decision`, `decision-doc` | Decision Document |
| `status`, `status-update` | Status Update |

If the doc type is unambiguous, confirm it and proceed. If `$ARGUMENTS` is empty or the type is unclear, present the list above and ask the user to choose before continuing.

---

## Step 2: Load product context

1. Read `pdm.config.yaml` to get `{vault}` and the active product `{product}`.
2. Read all files in `{vault}/{product}/_context/`:
   - `overview.md`
   - `stakeholders.md`
   - `goals.md`
   - `roadmap-status.md`
   - `constraints.md`
   - `glossary.md`
3. Read `{vault}/{product}/Knowledge Graph/graph.json` and `_index.md`.
4. Load graph nodes relevant to this doc type:
   - **PRD**: all constraint, decision, feature, and milestone nodes
   - **User Stories**: all feature and milestone nodes
   - **User Story Map**: all feature nodes
   - **Decision Doc**: all constraint and decision nodes; load stakeholder nodes for anyone mentioned in `$ARGUMENTS`
   - **Status Update**: all milestone and metric nodes

---

## Step 3: Evaluate the input and identify gaps

Analyze `$ARGUMENTS` and the loaded context to assess what is already known. Then follow the doc-type-specific rules below.

### PRD

Check whether each of the following is clearly addressed in `$ARGUMENTS` or derivable from the loaded context:

| Component | Check |
|-----------|-------|
| Feature | Is the feature or capability named and described? |
| Target user | Is the target persona or user segment identified? |
| Problem | Is the problem being solved stated clearly? |
| Solution approach | Is there a sense of how the feature addresses the problem? |
| Constraints or unknowns | Are there known limitations, risks, or open questions? |

For any component that is missing or ambiguous, add it to the clarifying questions in Step 4. If constraints and unknowns are not mentioned at all, always ask about them even if everything else is clear.

### User Stories

Ask:
1. What is the epic or feature name?
2. Which personas are involved? (check stakeholders.md and glossary.md for defined personas)
3. Which milestone does this map to?
4. Are there any must-have acceptance criteria you already know?

### User Story Map

Ask:
1. What is the epic or user journey name?
2. Are there multiple releases or phases? If so, how many and what are their goals?
3. Which persona is the primary user walking this journey?

### Decision Document

Ask:
1. What decision needs to be made?
2. What options are being considered?
3. Who owns this decision and who are the key stakeholders?
4. Is there a deadline or forcing function?

### Status Update

Ask:
1. What period does this cover (e.g., week of MM-DD)?
2. Who is the audience - leadership or team?
3. What is the overall status: Green (on track), Yellow (at risk), or Red (off track)?
4. Are there specific risks or blockers to call out?

---

## Step 4: Ask clarifying questions

Present only the questions that are needed based on the gap analysis in Step 3. Do not ask about things already clear from `$ARGUMENTS` or the loaded context.

Number each question. State at the top which doc type you are creating and which product it is for, so the user can confirm before answering.

Wait for the user's responses before proceeding.

---

## Step 4b: Query Jira for story data (Status Update only)

If the doc type is Status Update, attempt to pull story counts from Jira to embed in the document:

1. Check `tracker` in `pdm.config.yaml` and whether a Jira MCP tool is available in the current session. If either is missing, skip this step and note it in the confirmation step.
2. If available: query the relevant epic(s) mentioned in the input for:
   - Total stories in the epic
   - Stories marked complete or done
   - Stories targeting the current release (e.g. the next release)
   - Any stories flagged as blocked
   Embed these numbers directly in the What Happened bullets (e.g. "Checkout redesign: 4 of 12 release stories complete").
3. If no Jira MCP is available: note this in the confirmation step and skip. Do not leave placeholder text for Jira data - write the bullets based on what the user provided.

---

## Step 5: Write the document

Using the template, the loaded product context, and the user's answers, generate the full document draft. Do not leave placeholder text. Every section should be populated based on what is known - if something is genuinely unknown, state that explicitly rather than leaving a blank.

Apply all rules from `context/document-standards.md`:
- No emojis
- No em-dashes
- Direct and concise tone
- Tables preferred over nested bullets for comparisons and structured data
- YAML frontmatter with today's date and `status: Draft`

Write the file to the vault at:

| Doc Type | Vault Path |
|----------|------------|
| PRD | `{vault}/{product}/PRDs/[YYYY-MM-DD] [Feature Name].md` |
| User Stories | `{vault}/{product}/Stories/[YYYY-MM-DD] [Epic Name].md` |
| User Story Map | `{vault}/{product}/Story Maps/[YYYY-MM-DD] [Epic Name].md` |
| Decision Doc | `{vault}/{product}/Decisions/[YYYY-MM-DD] [Decision Title].md` |
| Status Update | `{vault}/{product}/Status Updates/[YYYY-MM-DD] {product} Status.md` |

If the target directory does not exist, create it before writing the file.

---

## Step 6: Offer graph ingestion

After writing the file, check whether the document contains any of the following that are not already in the knowledge graph:

- A named commitment (owner + deliverable + date or trigger)
- A confirmed decision
- A new constraint
- A new milestone or metric

If any are found, tell the user:

> "This document contains [N] candidate(s) for the knowledge graph: [list them briefly]. Run `/ingest-context [file path]` to extract and review them."

If nothing new is found, skip this step.

---

## Step 7: Confirm

Report:
- The file path written
- The doc type and product
- A one-line summary of the document (the TL;DR if it is a PRD or Decision Doc, otherwise a plain summary)
