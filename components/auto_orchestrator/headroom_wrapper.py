#!/usr/bin/env python3
"""Headroom Wrapper - Wraps all model inputs with context compression."""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CompressionConfig:
    enabled: bool = True
    level: str = "aggressive"  # aggressive, moderate, light
    preserve_code: bool = True
    preserve_numbers: bool = True
    min_compression_ratio: float = 0.3


class HeadroomWrapper:
    """Wraps model inputs with Headroom context compression."""

    def __init__(self, headroom_client=None, config: CompressionConfig = None):
        self.headroom = headroom_client
        self.config = config or CompressionConfig()

    async def wrap_messages(self, messages: List[Dict]) -> List[Dict]:
        """Wrap messages with context compression."""
        if not self.config.enabled or not self.headroom:
            return messages

        try:
            compressed = await self.headroom.compress(messages)
            return compressed
        except Exception as e:
            logger.warning(f"Compression failed, using original: {e}")
            return messages

    async def wrap_prompt(
        self,
        system_prompt: str,
        user_message: str,
        context: str = None,
    ) -> List[Dict]:
        """Wrap a prompt with context compression."""
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            compressed_context = await self._compress_context(context)
            messages.append({"role": "user", "content": compressed_context})

        messages.append({"role": "user", "content": user_message})
        return messages

    async def _compress_context(self, context: str) -> str:
        """Compress context using Headroom."""
        if not self.headroom or not self.config.enabled:
            return context

        try:
            messages = [{"role": "user", "content": context}]
            compressed = await self.headroom.compress(messages)
            return compressed[0]["content"] if compressed else context
        except Exception as e:
            logger.warning(f"Context compression failed: {e}")
            return context

    async def compress_for_agent(
        self, agent_type: str, messages: List[Dict]
    ) -> List[Dict]:
        """Compress messages optimized for a specific agent type."""
        # Adjust compression based on agent type
        if agent_type in ["coder", "debugger"]:
            # Less compression for code-heavy tasks
            original_level = self.config.level
            self.config.level = "moderate"
            result = await self.wrap_messages(messages)
            self.config.level = original_level
            return result
        elif agent_type == "documenter":
            # More compression for documentation
            original_level = self.config.level
            self.config.level = "aggressive"
            result = await self.wrap_messages(messages)
            self.config.level = original_level
            return result
        else:
            return await self.wrap_messages(messages)

    def get_compression_stats(self) -> Dict:
        """Get compression statistics."""
        return {
            "enabled": self.config.enabled,
            "level": self.config.level,
            "preserve_code": self.config.preserve_code,
            "preserve_numbers": self.config.preserve_numbers,
        }
