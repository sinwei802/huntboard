# Huntboard

Thin **Huntboard** method / evidence-gate skill for authorized hunting — **not** an attack cookbook.

This repository is the open methodology layer: local sense, thin method cards (evidence gates, handoffs, dead paths), and a mechanical `sense_gate`. It does **not** ship payloads, PoCs, or step-by-step exploit recipes.

## Install

### Clone

```bash
git clone https://github.com/sinwei802/huntboard.git
```

### Grok Bot

```bash
ln -sfn /path/to/huntboard /home/box/agent-data/workflows/huntboard
```

Then select `huntboard` in chat (`/` or `@`), or trigger via its skill description.

### Generic / Claude

Set `$SKILL_ROOT` to the clone root (must contain `SKILL.md`, `references/`, `scripts/`), then load `SKILL.md`. Prefer a symlink into your harness; do not fork the tree.

```bash
export SKILL_ROOT="$(pwd)/huntboard"
```

### Verify

```bash
cd scripts && python3 -m unittest discover -p 'test_*.py'
```

## Start here

| Path | Role |
|------|------|
| [`SKILL.md`](SKILL.md) | Agent skill entry + progressive disclosure |
| [`references/sense-cards/`](references/sense-cards/) | Thin method / evidence-gate cards |
| [`scripts/sense_gate.py`](scripts/sense_gate.py) | Mechanical proposal gate (methodology only) |
| [`USER.md`](USER.md) | Operator load notes (not combat gates) |
| [`CHANGELOG.md`](CHANGELOG.md) | Rolling changes |

## Layout

```
SKILL.md              # agent skill entry
USER.md               # operator notes
CHANGELOG.md
DELIVERABLE-*.md      # delivery notes (optional)
references/           # contracts, local-sense, sense-cards, indexes
scripts/              # hunt_plan, sense_gate, helpers, tests
```

## License

[MIT](LICENSE) — Copyright (c) 2026 sinwei802.

## Related

Extracted from [`sinwei802/kali_cc_skills`](https://github.com/sinwei802/kali_cc_skills) (that repo’s `huntboard/` path is now a stub pointing here).
