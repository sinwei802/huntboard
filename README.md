# Huntboard

Open methodology skill for authorized security engagements: **local sense**, thin method cards (evidence gates / handoffs / dead paths), and a mechanical `sense_gate`—**not** an exploit cookbook.

Red line: no payload / PoC / step-by-step attack recipes in this repository.

## Layout

```
SKILL.md              # agent skill entry + progressive disclosure
USER.md               # operator load notes (not combat gates)
CHANGELOG.md          # rolling changes
references/           # contracts, local-sense, sense-cards, indexes
scripts/              # hunt_plan, sense_gate, tests, helpers
```

## Install

### Generic / Claude / local harness

```bash
git clone https://github.com/sinwei802/huntboard.git
export SKILL_ROOT="$(pwd)/huntboard"   # or your clone path
# Point your harness at $SKILL_ROOT (symlink preferred; do not fork the tree)
```

### Grok Bot (shared workflows)

```bash
git clone https://github.com/sinwei802/huntboard.git /path/to/huntboard
ln -sfn /path/to/huntboard /home/box/agent-data/workflows/huntboard
```

Then select `huntboard` in chat (`/` or `@`), or trigger via its skill description.

## Tests

```bash
cd /path/to/huntboard
python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Related

This skill was extracted from `sinwei802/kali_cc_skills` (see stub under that repo’s `huntboard/`).
