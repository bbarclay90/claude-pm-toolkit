You are processing meeting notes for the user, a product manager. Read `pdm.config.yaml` first: `user.name` and `user.aliases` identify the user in transcripts, and `vault.path` is `{vault}`. Your job is to extract key insights and, most importantly, identify action items the user is responsible for, then persist everything to the vault.

---

## Step 1: Identify the project

Before anything else, determine which project this meeting belongs to. Look for project names in the transcript. If unclear, ask the user to confirm before proceeding.

The vault is organized as: `{vault}/[Project Name]/`

Known projects can be found by listing subdirectories of the vault root.

---

## Step 2: Get the raw content

Argument received: `$ARGUMENTS`

- If `$ARGUMENTS` is a file path ending in `.docx`: run `python scripts/parse_doc.py "$ARGUMENTS"` to extract the text, then use that output as the transcript.
- If `$ARGUMENTS` is a file path ending in `.txt` or `.md`: read the file directly.
- If `$ARGUMENTS` is long text (a pasted transcript): use it directly.
- If `$ARGUMENTS` is empty: look for a transcript pasted earlier in this conversation. If none is found, ask the user to paste the transcript now and wait for their response before continuing.

---

## Step 3: Extract structured information

Analyze the transcript and identify:

1. **Meeting title** - infer from context if not explicit (e.g. "Q2 Roadmap Review", "Design Sync")
2. **Meeting date** - use the date in the transcript if present; otherwise use today's date
3. **Attendees** - list everyone mentioned as present
4. **Key decisions & insights** - 3-7 concise bullet points capturing what was decided or learned
5. **The user's action items** - the critical output. Look for:
   - Direct assignments to `user.name` or any of `user.aliases` ("Jane will...", "action: Jane")
   - First-person commitments in the user's voice ("I'll...", "I can take that", "I'll follow up")
   - Actions assigned to the user's role (for example "the PM") when the transcript makes clear that is the user
   - Follow-ups and open questions the user raised that need tracking
   - Deadlines or due dates if mentioned

---

## Step 4: Write the meeting note to Obsidian

Create the file at:
`{vault}/[Project Name]/Meetings/YYYY-MM-DD - [Meeting Title].md`

Use this exact format:

```markdown
---
date: YYYY-MM-DD
attendees: [Name, Name, ...]
tags: [meeting, project-name]
---

# [Meeting Title] - YYYY-MM-DD

## Key Decisions & Insights
- 
- 

## Action Items - {user}
- [ ] 
- [ ] 

## All Action Items
| Owner | Action | Due |
|-------|--------|-----|
|       |        |     |

## Notes
[Any additional context worth preserving verbatim]
```

If the `[Project Name]/Meetings/` directory doesn't exist in the vault, create it first.

---

## Step 5: Update the running to-do list

Read `{vault}/Tasks/To-Do.md` if it exists. If it doesn't exist, create it with this header:

```markdown
# To-Do

Items are added automatically by /new-notes. Check them off as you complete them.

---
```

Append each of the user's action items as a new unchecked task under a heading for today's meeting:

```markdown
## YYYY-MM-DD - [Meeting Title]
- [ ] [action item text] - *[[Project Name/Meetings/YYYY-MM-DD - Meeting Title]]*
```

Do not remove or modify existing items. Only append.

---

## Step 6: Confirm

Report back with:
- The meeting note file path created
- How many action items were added to To-Do.md
- A bulleted list of the user's action items so they can review them immediately
