"""Font Preview Tool — Preview service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FontHandler:
    """Business-logic service for Preview operations in Font Preview Tool."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("FontHandler started")

    def export(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the export workflow for a new Preview."""
        if "weight" not in payload:
            raise ValueError("Missing required field: weight")
        record = self._repo.insert(
            payload["weight"], payload.get("family"),
            **{k: v for k, v in payload.items()
              if k not in ("weight", "family")}
        )
        if self._events:
            self._events.emit("preview.exportd", record)
        return record

    def load(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Preview and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Preview {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("preview.loadd", updated)
        return updated

    def filter(self, rec_id: str) -> None:
        """Remove a Preview and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Preview {rec_id!r} not found")
        if self._events:
            self._events.emit("preview.filterd", {"id": rec_id})

    def search(
        self,
        weight: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search previews by *weight* and/or *status*."""
        filters: Dict[str, Any] = {}
        if weight is not None:
            filters["weight"] = weight
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search previews: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Preview counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
