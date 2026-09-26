# Operator notes (preferences, not combat gates)

## How to load

- Treat this directory as `$SKILL_ROOT` (must contain `SKILL.md`, `references/`, `scripts/`).
- Symlink the same tree into your agent harness; do not fork copies.
- Opening hot path:
  1. `python3 "$SKILL_ROOT/scripts/hunt_plan.py" opening "…"`
  2. `python3 "$SKILL_ROOT/scripts/load_state_bundle.py"`
  3. Then touch the target
- Before proposing the next action: read `references/local-sense.md` if not already loaded this session; if fields are missing run `python3 "$SKILL_ROOT/scripts/sense_gate.py" --check <proposal.json>` (fail = do not emit exploit-class options).

## Warboard console (optional)

- If you run a local warboard console, point it at your engagement SQLite (`./pentest-state/warboard.sqlite` or your harness path).
- Schema / interaction contract: `references/warboard-schema.md`, `references/interaction-truth-contract.md` (not required every turn).

## Offline cracking preference (optional)

- If the attack host has no GPU, do not run hashcat/john there.
- Copy offline hashes to your GPU box share using your own path convention; keep a copy under `./pentest-state/loot/` as well.
- Give the human only filenames and relative hints—never assume another machine’s absolute mount path.
