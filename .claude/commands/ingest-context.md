You are extracting structured knowledge from a source document for the user's product management knowledge graph.

The knowledge graph only accepts facts - not ideas, brainstorms, open questions, or speculation. Your job is to identify candidates that meet the fact quality rules and present them for the user's review. Nothing enters the graph until the user approves it.

---

## Step 1: Get the source content

Argument received: `$ARGUMENTS`

- If `$ARGUMENTS` is a file path ending in `.docx`: run `python scripts/parse_doc.py "$ARGUMENTS"` to extract the text.
- If `$ARGUMENTS` is a file path ending in `.txt` or `.md`: read the file directly.
- If `$ARGUMENTS` is text (a pasted document): use it directly.
- If `$ARGUMENTS` is empty: ask the user to provide a file path or paste the content to ingest. Do not look for content in the conversation. Wait for their response before continuing.

Also read `pdm.config.yaml` to get `{vault}` and the active product `{product}`. All knowledge graph files are scoped to that product at:
`{vault}/{product}/Knowledge Graph/`

Read `{vault}/{product}/Knowledge Graph/graph.json` to understand what is already in the graph and avoid proposing duplicates.

---

## Step 2: Extract candidates

Read the source carefully. For each candidate, apply the fact quality rules before including it:

**Include only if it is one of:**
1. A named entity - a person, team, or product with a confirmed role
2. A hard commitment - explicit owner + stated deliverable + date or trigger
3. A confirmed decision - was decided (not discussed or proposed), has a clear outcome
4. An active constraint - a real current limitation (legal, technical, or business)
5. A tracked metric - has a name, a value, and a measurement date

**Exclude:**
- Ideas, brainstorms, or proposals without a decision
- Open questions
- Opinions without a decision attached
- Speculative future plans without a commitment

For each candidate also determine:
- Its node type: Product, Stakeholder, Team, Feature, Decision, Commitment, Constraint, Metric, or Milestone
- A stable ID (lowercase-hyphenated, e.g. `stakeholder-jane`, `commitment-pricing-api-apr30`)
- Any relationships (edges) to nodes already in the graph or to other candidates in this batch

---

## Step 3: Write the pending review file

Create `{vault}/{product}/Knowledge Graph/pending/YYYY-MM-DD-[source-slug]-review.md`

Use this exact format:

```markdown
---
source: [filename or short description of pasted content]
date: YYYY-MM-DD
status: Pending Review
---

# Knowledge Graph Review: [Source]

Review each candidate below. This file enforces the fact quality rules - only check items that are confirmed facts, hard commitments, made decisions, active constraints, or tracked metrics. Reject anything speculative, proposed, or uncertain.

Check [x] to approve. Leave [ ] or delete the line to reject.
Edit the text of any item before approving if the wording needs to be more precise.

---

## Candidate Nodes

### Stakeholders
- [ ] **id**: `stakeholder-[name]` | **name**: [Full Name] | **description**: [Role and context] | **source**: [quote or reference]

### Products
- [ ] **id**: `product-[name]` | **name**: [Name] | **description**: [What it is] | **source**: [quote]

### Teams
- [ ] **id**: `team-[name]` | **name**: [Team Name] | **description**: [What they own] | **source**: [quote]

### Commitments
- [ ] **id**: `commitment-[slug]` | **owner**: [Name] | **deliverable**: [What exactly] | **due**: [Date or trigger] | **source**: [quote]

### Decisions
- [ ] **id**: `decision-[slug]` | **decision**: [What was decided] | **decided_by**: [Who] | **date**: [Date] | **source**: [quote]

### Constraints
- [ ] **id**: `constraint-[slug]` | **description**: [The constraint] | **applies_to**: [What it limits] | **source**: [quote]

### Metrics
- [ ] **id**: `metric-[slug]` | **name**: [Metric name] | **value**: [Value] | **date**: [Measurement date] | **source**: [quote]

### Milestones
- [ ] **id**: `milestone-[slug]` | **name**: [Milestone name] | **date**: [Target date] | **status**: [On Track/At Risk/Blocked] | **source**: [quote]

---

## Candidate Edges

- [ ] `[from-id]` -[edge-type]-> `[to-id]` | **label**: [short description] | **source**: [quote]

---

## Rejected Candidates

List items found in the source that were excluded because they did not meet the fact quality rules. This gives the user visibility into what was filtered out.

- [Item] - Reason: [speculative / open question / no owner / not yet decided]
```

---

## Step 4: Confirm

Tell the user:
- The pending review file path
- How many candidates were found (by type)
- How many were excluded and why
- Next step: open the file in Obsidian, review and check approved items, then run `/approve-context [file path]`
