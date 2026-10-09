Switch the active product context to $ARGUMENTS.

Steps:

1. Read `pdm.config.yaml` to get `{vault}`. Verify that `{vault}/$ARGUMENTS/_context/` exists. If it does not, list the folders in `{vault}` so the user can pick the correct name, and tell them they can create a new product with `python scripts/setup.py add-product "$ARGUMENTS"`.

2. Update `active_product` in `pdm.config.yaml` to `$ARGUMENTS`. Change only that line.

3. Read all files in `{vault}/$ARGUMENTS/_context/`:
   - overview.md
   - stakeholders.md
   - goals.md
   - roadmap-status.md
   - constraints.md
   - glossary.md

4. Confirm the switch and provide a brief summary of the loaded context so the user can verify the right product is active:
   - Product name
   - One sentence on what the product is (from overview.md)
   - Current status / top priority (from goals.md or roadmap-status.md)
   - Any immediate risks or blockers
