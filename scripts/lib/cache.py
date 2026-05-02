"""JSONL append/read with atomic write semantics.

Caching essential per pre-reg operational discipline: pull once, store as JSONL,
never re-pull. Writes go to a tempfile then atomically rename to avoid corrupted
output on interruption.

Read functions transparently support gzip-compressed JSONL: if the requested path
does not exist, a sibling `.gz` is tried. Used for committing large pulls (S2
citations) compressed.
"""

from __future__ import annotations

import gzip
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    """Atomically write an iterable of dicts as JSONL. Returns count written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent, suffix=".tmp")
    n = 0
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
                n += 1
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    return n


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Read JSONL, transparently falling back to <path>.gz if the plain file is absent."""
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return
    gz_path = path.with_suffix(path.suffix + ".gz")
    if gz_path.exists():
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


def append_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    """Append records to an existing JSONL (or create). Not atomic; use for incremental pulls."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            n += 1
    return n


def existing_ids(path: Path, id_field: str) -> set[str]:
    """Read an existing JSONL and return the set of values at id_field. For dedupe on resume."""
    return {rec[id_field] for rec in read_jsonl(path) if id_field in rec}
