from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

from loguru import logger

from .base import BaseTranscriptParser, TranscriptMessage, TranscriptPayload


class MarkdownTranscriptParser(BaseTranscriptParser):
    """Parser for Markdown chat transcripts."""

    _ROLE_PATTERN = re.compile(r"^(?P<role>[^:]{1,40}):\s*(?P<content>.*)$")
    _HEADING_PATTERN = re.compile(r"^#{1,6}\s*(?P<role>.+)$")
    _ROLE_KEYWORDS = {
        "user": {"user", "human", "client", "developer", "me"},
        "assistant": {"assistant", "ai", "agent", "bot", "system"},
    }

    def parse(self, path: Path) -> TranscriptPayload:
        self._ensure_file(path)
        try:
            raw_lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            logger.exception("Failed to decode Markdown transcript {}: {}", path, exc)
            raise

        messages: List[TranscriptMessage] = []
        current_role: Optional[str] = None
        current_lines: List[str] = []
        prelude: List[str] = []

        def flush_current() -> None:
            nonlocal current_role, current_lines
            if not current_role:
                return
            payload = "\n".join(line.strip() for line in current_lines if line.strip())
            if not payload:
                payload = ""
            messages.append(TranscriptMessage(role=current_role, text=payload))
            current_lines = []

        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                if current_role and current_lines:
                    current_lines.append("")  # preserve paragraph breaks
                continue

            role_detection = self._extract_role(stripped)
            if role_detection:
                flush_current()
                current_role, initial_text = role_detection
                if initial_text:
                    current_lines = [initial_text]
                else:
                    current_lines = []
                continue

            if current_role:
                current_lines.append(stripped)
            else:
                prelude.append(stripped)

        flush_current()

        metadata = {"source": "markdown", "path": str(path)}
        if prelude and not messages:
            metadata["prelude"] = "\n".join(prelude)
        elif prelude:
            metadata["prelude"] = "\n".join(prelude)

        if not messages:
            logger.warning("No role/message pairs detected in Markdown transcript {}", path)

        transcript_id = path.stem
        return TranscriptPayload(
            transcript_id=transcript_id,
            messages=messages,
            metadata=metadata,
        )

    def _extract_role(self, line: str) -> Optional[Tuple[str, str]]:
        line = line.lstrip("> ").strip()
        match = self._ROLE_PATTERN.match(line)
        if match:
            raw_role = match.group("role").strip().strip("`*")
            normalized = self._normalize_role(raw_role)
            if normalized:
                return normalized, match.group("content").strip()

        heading = self._HEADING_PATTERN.match(line)
        if heading:
            raw_role = heading.group("role").strip().strip("`*")
            normalized = self._normalize_role(raw_role)
            if normalized:
                return normalized, ""

        return None

    def _normalize_role(self, raw_role: str) -> Optional[str]:
        normalized = raw_role.lower()
        for canonical, keywords in self._ROLE_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                return canonical
        return None
