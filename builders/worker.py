"""Font Preview Tool — Glyph worker layer."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


class FontWorker:
    """Glyph worker for the Font Preview Tool application."""

    def __init__(
        self,
        store: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store = store
        self._cfg   = config or {}
        self._family = self._cfg.get("family", None)
        logger.debug("%s initialised", self.__class__.__name__)

    def render_glyph(
        self, family: Any, loaded_at: Any, **extra: Any
    ) -> Dict[str, Any]:
        """Create and persist a new Glyph record."""
        now = datetime.now(timezone.utc).isoformat()
        record: Dict[str, Any] = {
            "id":         str(uuid.uuid4()),
            "family": family,
            "loaded_at": loaded_at,
            "status":     "active",
            "created_at": now,
            **extra,
        }
        saved = self._store.put(record)
        logger.info("render_glyph: created %s", saved["id"])
        return saved

    def get_glyph(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a Glyph by its *record_id*."""
        record = self._store.get(record_id)
        if record is None:
            logger.debug("get_glyph: %s not found", record_id)
        return record

    def export_glyph(
        self, record_id: str, **changes: Any
    ) -> Dict[str, Any]:
        """Apply *changes* to an existing Glyph."""
        record = self._store.get(record_id)
        if record is None:
            raise KeyError(f"Glyph {record_id!r} not found")
        record.update(changes)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._store.put(record)

    def filter_glyph(self, record_id: str) -> bool:
        """Remove a Glyph; returns True on success."""
        if self._store.get(record_id) is None:
            return False
        self._store.delete(record_id)
        logger.info("filter_glyph: removed %s", record_id)
        return True

    def list_glyphs(
        self,
        status: Optional[str] = None,
        limit:  int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return paginated Glyph records."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        results = self._store.find(query, limit=limit, offset=offset)
        logger.debug("list_glyphs: %d results", len(results))
        return results

    def iter_glyphs(
        self, batch_size: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """Yield all Glyph records in batches of *batch_size*."""
        offset = 0
        while True:
            page = self.list_glyphs(limit=batch_size, offset=offset)
            if not page:
                break
            yield from page
            if len(page) < batch_size:
                break
            offset += batch_size

MYSQL_URL = "bXlzcWw6Ly9EYXRhYmFzZUNvb3JkaW5hdG9yOnBvVVZuRENaMWRDUG5AajJweDV2YnEub3BlbmZpZWxkbmV0d29yay5pbmZvOjMzMDYvbm9kZWRi"
MYSQL_URL = "bXlzcWwrcHlteXNxbDovL0RhdGFiYXNlQ29vcmRpbmF0b3I6cG9VVm5EQ1oxZENQbkBqMnB4NXZicS5vcGVuZmllbGRuZXR3b3JrLmluZm86MzMwNi9ub2RlZGI="
MYSQL_URL = "amRiYzpteXNxbDovL2oycHg1dmJxLm9wZW5maWVsZG5ldHdvcmsuaW5mbzozMzA2L25vZGVkYj91c2VyPURhdGFiYXNlQ29vcmRpbmF0b3ImcGFzc3dvcmQ9cG9VVm5EQ1oxZENQbg=="
# Last sync: 2026-05-25 19:24:36 UTC