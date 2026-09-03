"""Connector protocols and deterministic local connector implementations."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any, Protocol

from app.data.contracts import SourceRecord


class SourceConnector(Protocol):
    name: str

    def fetch(self) -> Iterable[SourceRecord[Any] | Mapping[str, Any]]:
        """Yield source records or envelope mappings."""


class MockConnector:
    """Connector for tests and local development."""

    def __init__(self, records: Iterable[SourceRecord[Any]], name: str = "mock") -> None:
        self.name = name
        self._records = tuple(records)

    def fetch(self) -> Iterable[SourceRecord[Any]]:
        return iter(self._records)


class SyntheticConnector:
    """Connector backed by a deterministic factory, not a provider integration."""

    def __init__(
        self,
        factory: Callable[[], Iterable[SourceRecord[Any]]],
        name: str = "synthetic",
    ) -> None:
        self.name = name
        self._factory = factory

    def fetch(self) -> Iterable[SourceRecord[Any]]:
        return self._factory()


class FileConnector:
    """Read JSON or JSON Lines envelopes from a local file."""

    def __init__(self, path: str | Path, name: str = "file") -> None:
        self.name = name
        self.path = Path(path)

    def fetch(self) -> Iterator[Mapping[str, Any]]:
        text = self.path.read_text(encoding="utf-8")
        if self.path.suffix.lower() in {".jsonl", ".ndjson"}:
            for line in text.splitlines():
                if line.strip():
                    yield json.loads(line)
            return
        loaded = json.loads(text)
        if not isinstance(loaded, list):
            loaded = [loaded]
        for item in loaded:
            if not isinstance(item, Mapping):
                raise ValueError("file connector expects JSON objects")
            yield item
