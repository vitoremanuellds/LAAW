"""Core orchestrator: `laaw file check <path>`. Read-only — no state, no save."""

from pathlib import Path

from ..constants import EXEMPT_FILE_SUFFIX, FILE_WORD_THRESHOLD
from .base import Refuse


def check(path: str) -> tuple[str, int]:
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise Refuse(f"no such file: {path}")
    if not target.is_file():
        raise Refuse(f"not a file: {path}")

    words = len(target.read_text(encoding="utf-8", errors="replace").split())
    name = target.name

    if _is_exempt(target):
        return f"{name}: exempt (session entry point, always read in full)", 0
    if words > FILE_WORD_THRESHOLD:
        return f"{name}: {words} words > {FILE_WORD_THRESHOLD} (threshold) — split it", 1
    return f"{name}: {words} words \u2264 {FILE_WORD_THRESHOLD} — ok", 0


def _is_exempt(target: Path) -> bool:
    parts = target.parts
    return len(parts) >= 2 and "/".join(parts[-2:]) == EXEMPT_FILE_SUFFIX
