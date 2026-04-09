"""Font Preview Tool — utility helpers for glyph operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def load_glyph(data: Dict[str, Any]) -> Dict[str, Any]:
    """Glyph load — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "family" not in result:
        raise ValueError(f"Glyph must include 'family'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["family"]).encode()).hexdigest()[:12]
    return result


def filter_glyphs(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Glyph records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("filter_glyphs: %d items after filter", len(out))
    return out[:limit]


def render_glyph(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "loaded_at" in updated and not isinstance(updated["loaded_at"], (int, float)):
        try:
            updated["loaded_at"] = float(updated["loaded_at"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_glyph(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Glyph invariants."""
    required = ["family", "loaded_at", "size_pt"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_glyph: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def favourite_glyph_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk favourite."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
