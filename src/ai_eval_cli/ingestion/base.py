from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass(frozen=True)
class TranscriptMessage:
    role: str
    text: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscriptPayload:
    transcript_id: str
    messages: List[TranscriptMessage]
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTranscriptParser(ABC):
    """Base interface for transcript parsers."""

    @abstractmethod
    def parse(self, path: Path) -> TranscriptPayload:
        """Parse the transcript located at `path`. Must return a normalized payload."""

    def _ensure_file(self, path: Path) -> None:
        if not path.exists():
            logger.error("Transcript file not found: {}", path)
            raise FileNotFoundError(f"Transcript file not found: {path}")

