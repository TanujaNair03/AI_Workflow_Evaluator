from __future__ import annotations

from pathlib import Path

from loguru import logger

from .base import BaseTranscriptParser, TranscriptMessage, TranscriptPayload


class RawTextTranscriptParser(BaseTranscriptParser):
    """Parser that treats a file as a single raw transcript block."""

    def parse(self, path: Path) -> TranscriptPayload:
        self._ensure_file(path)
        try:
            raw_content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            logger.exception("Failed to decode text transcript %s: %s", path, exc)
            raise

        if not raw_content.strip():
            logger.warning("Transcript %s is empty or contains only whitespace", path)

        message_text = raw_content or ""
        message = TranscriptMessage(role="transcript", text=message_text)

        metadata = {
            "source": "raw_text",
            "path": str(path),
            "extension": path.suffix.lower(),
        }

        return TranscriptPayload(
            transcript_id=path.stem,
            messages=[message],
            metadata=metadata,
        )
