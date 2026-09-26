#!/usr/bin/env python3
"""Fixed-string lookup against the evidence-db index.

Hunt-time query for huntboard. Prints HIT/MISS plus at most one entity
brief. Never opens case notes, loot, or kit files. Path layout is parsed
from the evidence-db skill table; this script does not embed a vault path.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAX_LINES_PER_QUERY = 20
MAX_ENTITIES_DEFAULT = 1
MIN_QUERY_LEN = 3
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
TABLE_KEY_RE = re.compile(
    r"^\|\s*(vault|資料庫根|總索引|實體目錄)\s*\|\s*(.*?)\s*\|"
)
DEFAULT_INDEX_NAME = "證據資料庫.md"
DEFAULT_ENTITY_DIR = "實體"


@dataclass
class LookupResult:
    status: str
    reason: str = ""
    queries: int = 0
    hits: int = 0
    misses: int = 0
    entities: int = 0
    lines: list[str] = field(default_factory=list)

    def render(self) -> str:
        header = f"IOC_LOOKUP status={self.status}"
        if self.reason:
            header += f" reason={self.reason}"
        if self.status == "ok":
            header += (
                f" queries={self.queries} hits={self.hits} "
                f"misses={self.misses} entities={self.entities}"
            )
        body = [header, *self.lines]
        return "\n".join(body) + "\n"


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _strip_cell(raw: str) -> str:
    value = raw.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1].strip()
    return value


def parse_evidence_db_defaults(skill_text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in skill_text.splitlines():
        match = TABLE_KEY_RE.match(line)
        if not match:
            continue
        found[match.group(1)] = _strip_cell(match.group(2))
    return found


def evidence_db_skill_candidates() -> list[Path]:
    ordered: list[Path] = []
    env = os.environ.get("EVIDENCE_DB_SKILL", "").strip()
    if env:
        path = Path(env).expanduser()
        ordered.append(path if path.name == "SKILL.md" else path / "SKILL.md")
    here = Path(__file__).resolve()
    huntboard_root = here.parent.parent
    for parent in (
        huntboard_root.parent,
        Path.home() / ".grok" / "skills",
        Path.home() / ".claude" / "skills",
    ):
        ordered.append(parent / "evidence-db" / "SKILL.md")
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in ordered:
        key = path
        try:
            key = path.resolve()
        except OSError:
            pass
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _load_defaults() -> dict[str, str]:
    for candidate in evidence_db_skill_candidates():
        if candidate.is_file():
            return parse_evidence_db_defaults(
                candidate.read_text(encoding="utf-8")
            )
    return {}


def resolve_index(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit.expanduser()
    defaults = _load_defaults()
    vault = os.environ.get("OBSIDIAN_VAULT", "").strip() or defaults.get("vault")
    db_rel = defaults.get("資料庫根")
    index_name = defaults.get("總索引") or DEFAULT_INDEX_NAME
    if not vault or not db_rel:
        return None
    return Path(vault).expanduser() / db_rel / index_name


def resolve_entity_dir(index: Path, explicit_index: bool) -> Path:
    if explicit_index:
        return index.parent / DEFAULT_ENTITY_DIR
    defaults = _load_defaults()
    vault = os.environ.get("OBSIDIAN_VAULT", "").strip() or defaults.get("vault")
    db_rel = defaults.get("資料庫根")
    entity_rel = defaults.get("實體目錄") or DEFAULT_ENTITY_DIR
    if vault and db_rel:
        return Path(vault).expanduser() / db_rel / entity_rel
    return index.parent / DEFAULT_ENTITY_DIR


def _is_table_rule(line: str) -> bool:
    core = (
        line.strip()
        .strip("|")
        .replace("|", "")
        .replace("-", "")
        .replace(":", "")
        .replace(" ", "")
    )
    return core == ""


def match_index_lines(index_text: str, query: str) -> list[str]:
    needle = query.casefold()
    hits: list[str] = []
    for line in index_text.splitlines():
        if _is_table_rule(line):
            continue
        if needle not in line.casefold():
            continue
        hits.append(line.rstrip())
        if len(hits) >= MAX_LINES_PER_QUERY:
            break
    return hits


def _section_items(text: str, heading: str) -> list[str]:
    items: list[str] = []
    capturing = False
    for line in text.splitlines():
        if line.startswith("## "):
            capturing = line[3:].strip() == heading
            continue
        if not capturing:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def entity_brief(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    title = path.stem
    for line in text.splitlines():
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip() or title
            break
        if line.startswith("# "):
            title = line[2:].strip() or title
            break
    lines = [f"ENTITY {title}"]
    cases = _section_items(text, "出現案件")
    related = _section_items(text, "關聯實體")
    if cases:
        lines.append("- cases: " + "; ".join(cases))
    if related:
        lines.append("- related: " + "; ".join(related))
    return lines


def _wikilinks(line: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(line)]


def split_queries(queries: list[str]) -> tuple[list[str], list[str]]:
    usable: list[str] = []
    skipped: list[str] = []
    for raw in queries:
        value = raw.strip()
        if not value:
            continue
        if len(value) < MIN_QUERY_LEN:
            skipped.append(value)
            continue
        usable.append(value)
    return usable, skipped


def skip_result(skipped: list[str]) -> LookupResult:
    result = LookupResult(status="skip", reason="no_query")
    for value in skipped:
        result.lines.append(f"SKIP {value} reason=too_short")
    return result


def lookup(
    index_text: str,
    queries: list[str],
    entity_dir: Path | None = None,
    max_entities: int = MAX_ENTITIES_DEFAULT,
) -> LookupResult:
    usable, skipped = split_queries(queries)
    if not usable:
        return skip_result(skipped)

    result = LookupResult(status="ok", queries=len(usable))
    for value in skipped:
        result.lines.append(f"SKIP {value} reason=too_short")

    emitted = 0
    entity_root = entity_dir.resolve() if entity_dir is not None else None
    for query in usable:
        rows = match_index_lines(index_text, query)
        if not rows:
            result.misses += 1
            result.lines.append(f"MISS {query}")
            continue
        result.hits += 1
        result.lines.append(f"HIT {query}")
        for row in rows:
            result.lines.append(f"INDEX {row}")
            if (
                emitted >= max_entities
                or entity_root is None
                or not entity_root.is_dir()
            ):
                continue
            for link in _wikilinks(row):
                candidate = (entity_root / f"{link}.md").resolve()
                if not candidate.is_file():
                    continue
                if not _is_within(candidate, entity_root):
                    continue
                result.lines.extend(entity_brief(candidate))
                result.entities += 1
                emitted += 1
                break
    return result


def run_lookup(
    queries: list[str],
    index_path: Path | None = None,
    max_entities: int = MAX_ENTITIES_DEFAULT,
) -> LookupResult:
    usable, skipped = split_queries(queries)
    if not usable:
        return skip_result(skipped)
    explicit = index_path is not None
    resolved = resolve_index(index_path)
    if resolved is None:
        return LookupResult(status="unavailable", reason="no_index")
    try:
        text = resolved.read_text(encoding="utf-8")
    except OSError:
        return LookupResult(status="unavailable", reason="index_unreadable")
    entity_dir = resolve_entity_dir(resolved, explicit_index=explicit)
    return lookup(
        text,
        queries,
        entity_dir=entity_dir,
        max_entities=max_entities,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Search the evidence-db index with fixed strings. "
            "Prints HIT/MISS; emits at most one entity brief. "
            "Never opens case notes."
        )
    )
    parser.add_argument("values", nargs="*", help="IOC values to look up")
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="index markdown path (default: evidence-db layout)",
    )
    parser.add_argument(
        "--max-entities",
        type=int,
        default=MAX_ENTITIES_DEFAULT,
        help="max entity briefs to emit (default: 1)",
    )
    args = parser.parse_args(argv)
    max_entities = max(0, args.max_entities)
    result = run_lookup(
        args.values,
        index_path=args.index,
        max_entities=max_entities,
    )
    sys.stdout.write(result.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
