"""Font Preview Tool — Style models layer."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class FontModels:
    """Style models for the Font Preview Tool application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._size_pt = self._cfg.get("size_pt", None)
        logger.debug("%s initialised", self.__class__.__name__)

    def compare_style(
        self, size_pt: Any, format: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Style record."""
        now = datetime.now(timezone.utc).isoformat()
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "size_pt": size_pt,
            "format": format,
            "status":     "active",
            "created_at": now,
            **extra,
        }
        saved = self._store.put(record)
        logger.info("compare_style: created %s", saved["id"])
        return saved

    def get_style(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Style by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_style: %s not found", record_id)
        return record

    def filter_style(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Style."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Style {record_id!r} not found")
        record.update(changes)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._store.put(record)

    def export_style(self, record_id: str) -> bool:
        """Remove a Style; returns True on success."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("export_style: removed %s", record_id)
        return True

    def list_styles(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return paginated Style records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_styles: %d results", len(results))
        return results

    def iter_styles(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Style records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_styles(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size
