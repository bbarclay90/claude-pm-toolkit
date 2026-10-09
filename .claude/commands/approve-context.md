Process a reviewed knowledge graph pending file and write approved items to the graph.

Argument received: `$ARGUMENTS`

This should be the full path to a pending review file in the active product's knowledge graph:
`{vault}/{product}/Knowledge Graph/pending/`

Read `pdm.config.yaml` to get `{vault}` and the active product `{product}` before processing.

If no argument is provided, list all files currently in the pending folder and ask the user which one to process.

---

## Step 1: Read the review file

Read the file at `$ARGUMENTS`. Parse all checked items `- [x]` as approved. Ignore all unchecked items `- [ ]`.

---

## Step 2: Load the current graph

Read `{vault}/{product}/Knowledge Graph/graph.json` to get the current state of nodes and edges.

---

## Step 3: Process approved nodes

For each approved node candidate:

1. Parse its fields: `id`, `type`, `name`, `description`, `source`, and any type-specific fields (owner, due, value, etc.)
2. Check if a node with that `id` already exists in `graph.json`:
   - If new: add it to the nodes array with `created` and `updated` set to today's date
   - If existing: update the description and append the new source to its sources array, set `updated` to today
3. Write or update its markdown node file at:
   `{vault}/{product}/Knowledge Graph/nodes/[type-folder]/[id].md`
   using the node file format defined in `context/knowledge-graph-schema.md`

---

## Step 4: Process approved edges

For each approved edge candidate:

1. Parse: `from-id`, `to-id`, `edge-type`, `label`, `source`
2. Verify both `from` and `to` nodes exist in the graph. If either is missing, skip the edge and note it in the confirmation report.
3. Generate an edge `id` as `edge-[from-id]-[type]-[to-id]`
4. Add or update the edge in `graph.json`

---

## Step 5: Update graph.json

Write the updated graph back to:
`{vault}/{product}/Knowledge Graph/graph.json`

---

## Step 6: Rebuild _index.md

Rewrite `{vault}/{product}/Knowledge Graph/_index.md` with all current nodes grouped by type.
Each entry format: `- [[nodes/[type-dir]/[id]|Name]] - [description truncated to 80 chars]`

---

## Step 7: Append to _log.md

Append an entry to `{vault}/{product}/Knowledge Graph/_log.md`:

```
## [YYYY-MM-DD] approve-context | source: [source name] | nodes added: N | nodes updated: N | edges added: N
```

---

## Step 8: Regenerate graph visualization

Run: `python scripts/knowledge_graph.py --visualize`

This updates `Knowledge Graph/graph-view.md` with a fresh DOT diagram.

---

## Step 9: Move the review file to approved

Move (copy then delete) the processed review file from:
`{vault}/{product}/Knowledge Graph/pending/[filename]`
to:
`{vault}/{product}/Knowledge Graph/approved/[filename]`

---

## Step 10: Confirm

Report to the user:
- Nodes added (list with types)
- Nodes updated (list)
- Edges added (list)
- Any skipped edges (missing nodes)
- Current graph totals: X nodes, Y edges
- Reminder to open `{vault}/{product}/Knowledge Graph/graph-view.md` in Obsidian preview to see the updated visualization
