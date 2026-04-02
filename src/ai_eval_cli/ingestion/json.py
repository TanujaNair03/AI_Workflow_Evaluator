from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from .base import BaseTranscriptParser, TranscriptMessage, TranscriptPayload


class JSONTranscriptParser(BaseTranscriptParser):
    """Parser for JSON-based chat exports."""

    def parse(self, path: Path) -> TranscriptPayload:
        self._ensure_file(path)
        try:
            payload = json.loads(path.read_bytes())
        except json.JSONDecodeError as exc:
            logger.exception("Invalid JSON transcript %s: %s", path, exc)
            raise

        metadata = self._extract_metadata(payload, path)
        transcript_id = self._infer_transcript_id(payload, path)

        messages_source = self._find_message_source(payload)
        if messages_source:
            metadata.setdefault("structure", "conversation")
            messages = [self._normalize_entry(entry) for entry in messages_source]
        else:
            logger.warning(
                "JSON transcript %s does not expose a message sequence; sending raw dump", path
            )
            metadata["structure"] = "raw_dump"
            messages = [
                TranscriptMessage(
                    role="transcript",
                    text=self._format_payload_dump(payload),
                )
            ]

        return TranscriptPayload(
            transcript_id=transcript_id,
            messages=messages,
            metadata=metadata,
        )

    def _find_message_source(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return [self._coerce_entry(entry) for entry in payload]

        if not isinstance(payload, dict):
            return []

        for candidate in ("messages", "dialogue", "conversation", "entries"):
            collection = payload.get(candidate)
            if isinstance(collection, list):
                return [self._coerce_entry(entry) for entry in collection]

        choices = payload.get("choices")
        if isinstance(choices, list):
            extracted = []
            for choice in choices:
                if isinstance(choice, dict):
                    message = choice.get("message") or choice.get("text") or choice.get("content")
                    if message:
                        extracted.append(self._coerce_entry(message))
            if extracted:
                return extracted

        return []

    def _coerce_entry(self, entry: Any) -> Dict[str, Any]:
        if isinstance(entry, dict):
            return entry
        return {"role": "assistant", "content": str(entry)}

    def _normalize_entry(self, entry: Dict[str, Any]) -> TranscriptMessage:
        role = self._extract_role(entry)
        text = self._extract_text(entry)
        return TranscriptMessage(role=role, text=text or "")

    def _extract_role(self, entry: Dict[str, Any]) -> str:
        for key in ("role", "sender", "author", "speaker", "from"):
            raw_value = entry.get(key)
            if isinstance(raw_value, str) and raw_value.strip():
                return raw_value.strip()
        return "assistant"

    def _extract_text(self, entry: Dict[str, Any]) -> str:
        for key in ("content", "text", "message", "value"):
            value = entry.get(key)
            if value:
                return self._coalesce_text(value)

        extras = entry.get("content", {})
        if isinstance(extras, dict):
            for sub_key in ("text", "value"):
                if sub_key in extras:
                    return self._coalesce_text(extras[sub_key])

        return ""

    def _coalesce_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts = []
            for chunk in value:
                if isinstance(chunk, dict):
                    text = chunk.get("text") or chunk.get("value")
                    if text:
                        parts.append(str(text).strip())
                else:
                    parts.append(str(chunk).strip())
            return "\n".join(part for part in parts if part)
        if isinstance(value, dict):
            nested = value.get("text") or value.get("value")
            if nested:
                return self._coalesce_text(nested)
        return str(value).strip()

    def _extract_metadata(self, payload: Any, path: Path) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {"source": "json", "path": str(path)}
        if isinstance(payload, dict):
            for key in ("metadata", "meta", "context"):
                data = payload.get(key)
                if isinstance(data, dict):
                    metadata.update(data)
        return metadata

    def _infer_transcript_id(self, payload: Any, path: Path) -> str:
        if isinstance(payload, dict):
            for key in ("transcript_id", "id", "name", "title"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return path.stem

    def _format_payload_dump(self, payload: Any) -> str:
        try:
            return json.dumps(payload, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(payload)
