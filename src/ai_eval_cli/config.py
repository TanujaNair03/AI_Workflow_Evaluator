from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional, List

# Tiered defaults: Move from most capable/modern to most stable fallback
DEFAULT_MODEL_PRIORITY = [
    "gemini-3-flash",      # 2026 Flagship (if available)
    "gemini-2.5-flash",    # Your current target
    "gemini-1.5-flash",    # Legacy fallback
]

@dataclass(frozen=True)
class CLIConfig:
    api_key: str
    # We store the user's choice OR our tiered list
    model_priority: List[str] = field(default_factory=lambda: DEFAULT_MODEL_PRIORITY)

    @classmethod
    def from_env(cls, api_key: Optional[str] = None, model: Optional[str] = None) -> "CLIConfig":
        key = api_key or os.environ.get("GENAI_API_KEY")
        if not key:
            raise EnvironmentError("GENAI_API_KEY must be set.")
        
        # If a user provides a specific model via CLI/Env, it becomes the sole priority
        env_model = model or os.environ.get("GENAI_MODEL")
        priority = [env_model] if env_model else DEFAULT_MODEL_PRIORITY
        
        return cls(api_key=key, model_priority=priority)