"""Font Preview Tool — utility helpers for font operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def favourite_font(data: Dict[str, Any]) -> Dict[str, Any]:
    """Font favourite — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "weight" not in result:
        raise ValueError(f"Font must include 'weight'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["weight"]).encode()).hexdigest()[:12]
    return result


def filter_fonts(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Font records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("filter_fonts: %d items after filter", len(out))
    return out[:limit]


def compare_font(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "format" in updated and not isinstance(updated["format"], (int, float)):
        try:
            updated["format"] = float(updated["format"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_font(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Font invariants."""
    required = ["weight", "format", "style_variant"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_font: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def render_font_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk render."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
