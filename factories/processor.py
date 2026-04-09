"""Font Preview Tool — Font service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FontProcessor:
    """Business-logic service for Font operations in Font Preview Tool."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("FontProcessor started")

    def load(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the load workflow for a new Font."""
        if "family" not in payload:
            raise ValueError("Missing required field: family")
        record = self._repo.insert(
            payload["family"], payload.get("size_pt"),
            **{k: v for k, v in payload.items()
              if k not in ("family", "size_pt")}
        )
        if self._events:
            self._events.emit("font.loadd", record)
        return record

    def filter(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Font and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Font {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("font.filterd", updated)
        return updated

    def compare(self, rec_id: str) -> None:
        """Remove a Font and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Font {rec_id!r} not found")
        if self._events:
            self._events.emit("font.compared", {"id": rec_id})

    def search(
        self,
        family: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search fonts by *family* and/or *status*."""
        filters: Dict[str, Any] = {}
        if family is not None:
            filters["family"] = family
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search fonts: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Font counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
