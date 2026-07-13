"""Gateway client and Headroom context compression for ai-workstation platform.

Headroom compresses context before sending to LLMs, saving 60-90% of tokens.
Uses the HeadroomContextCompressor for local compression without external services.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GatewayConfig:
    base_url: str = "http://localhost:8000"
    api_key: str = ""
    timeout: int = 30


class GatewayClient:
    """HTTP client for ai-workstation gateway API."""

    def __init__(self, config: GatewayConfig = None):
        self.config = config or GatewayConfig()
        self.headers = {}
        if self.config.api_key:
            self.headers["X-API-Key"] = self.config.api_key

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.config.base_url}/health",
                    headers=self.headers,
                    timeout=5,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def chat(self, messages: List[Dict], model: str = "local", **kwargs) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.base_url}/chat",
                json={"messages": messages, "model": model, **kwargs},
                headers=self.headers,
                timeout=self.config.timeout,
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_completions(self, messages: List[Dict], model: str = "local", **kwargs) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.base_url}/v1/chat/completions",
                json={"messages": messages, "model": model, **kwargs},
                headers=self.headers,
                timeout=self.config.timeout,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_models(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.config.base_url}/v1/models",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def create_session(self, project_path: str = None) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.base_url}/sessions",
                json={"project_path": project_path},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def execute_skill(self, skill_name: str, params: Dict = None) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.base_url}/skills/{skill_name}/execute",
                json=params or {},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def recall_memory(self, query: str, scope: str = "global") -> List[Dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.base_url}/memory/recall",
                json={"query": query, "scope": scope},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json().get("memories", [])


@dataclass
class HeadroomConfig:
    # Compression settings
    enabled: bool = True
    max_tokens: int = 4096
    aggressive: bool = True
    preserve_code: bool = True
    strip_comments: bool = True
    normalize_whitespace: bool = True
    dedup_lines: bool = True
    chars_per_token: float = 4.0

    # Proxy settings (for AI Proxy Server integration)
    proxy_url: str = "http://localhost:8090"
    use_proxy: bool = True

    # Legacy settings (for direct LiteLLM integration)
    litellm_url: str = "http://localhost:4000"
    api_key: str = ""


class HeadroomClient:
    """Wraps model inputs with Headroom context compression.

    Usage:
        client = HeadroomClient()
        compressed = await client.compress(messages, model="mimo-auto")
        # or
        response = await client.complete(messages, model="mimo-auto")
    """

    def __init__(self, config: HeadroomConfig = None):
        self.config = config or HeadroomConfig()
        self._compressor = None

    def _get_compressor(self):
        """Lazy-load the HeadroomContextCompressor."""
        if self._compressor is None:
            try:
                from components.ai_proxy.headroom import (
                    HeadroomContextCompressor,
                    CompressionConfig,
                )
                self._compressor = HeadroomContextCompressor(CompressionConfig(
                    enabled=self.config.enabled,
                    max_tokens=self.config.max_tokens,
                    aggressive=self.config.aggressive,
                    preserve_code=self.config.preserve_code,
                    strip_comments=self.config.strip_comments,
                    normalize_whitespace=self.config.normalize_whitespace,
                    dedup_lines=self.config.dedup_lines,
                    chars_per_token=self.config.chars_per_token,
                ))
            except ImportError:
                # Fallback: use simple compression
                self._compressor = _SimpleCompressor(self.config)
        return self._compressor

    async def compress(self, messages: List[Dict], model: str = None) -> List[Dict]:
        """Compress messages using Headroom context compression."""
        if not self.config.enabled:
            return messages

        compressor = self._get_compressor()
        try:
            return compressor.compress(messages)
        except Exception as e:
            logger.warning(f"Headroom compression failed: {e}")
            return messages

    async def compress_text(self, text: str) -> str:
        """Compress a single text block."""
        if not self.config.enabled:
            return text

        compressor = self._get_compressor()
        try:
            return compressor.compress_text(text)
        except Exception as e:
            logger.warning(f"Headroom compression failed: {e}")
            return text

    async def wrap_context(self, system_prompt: str, user_message: str, context: str = None) -> List[Dict]:
        """Wrap inputs with context compression."""
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            compressed_context = await self.compress(
                [{"role": "user", "content": context}]
            )
            messages.append({"role": "user", "content": compressed_context[0]["content"]})

        messages.append({"role": "user", "content": user_message})
        return messages

    async def complete(self, messages: List[Dict], model: str = "mimo-auto", **kwargs) -> Dict:
        """Compress and forward to AI Proxy Server."""
        if self.config.use_proxy:
            return await self._complete_via_proxy(messages, model, **kwargs)
        else:
            return await self._complete_via_litellm(messages, model, **kwargs)

    async def _complete_via_proxy(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """Forward to AI Proxy Server (which handles Headroom compression)."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.config.proxy_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "headroom": self.config.enabled,
                        **kwargs,
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"AI Proxy request failed: {e}")
            raise

    async def _complete_via_litellm(self, messages: List[Dict], model: str, **kwargs) -> Dict:
        """Forward to LiteLLM with Headroom compression."""
        compressed = await self.compress(messages, model)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.config.litellm_url}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": compressed,
                        **kwargs,
                    },
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"LiteLLM request failed: {e}")
            raise

    async def health(self) -> bool:
        """Check if Headroom is available."""
        if self.config.use_proxy:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self.config.proxy_url}/health",
                        timeout=5,
                    )
                    return resp.status_code == 200
            except Exception:
                return False
        else:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self.config.litellm_url}/health",
                        headers={"Authorization": f"Bearer {self.config.api_key}"},
                        timeout=5,
                    )
                    return resp.status_code == 200
            except Exception:
                return False

    def stats(self, original: List[Dict], compressed: List[Dict]) -> Dict:
        """Calculate compression statistics."""
        original_tokens = sum(
            len(m.get("content", "").split()) for m in original
        )
        compressed_tokens = sum(
            len(m.get("content", "").split()) for m in compressed
        )
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        return {
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "ratio": ratio,
            "savings_percent": round((1 - ratio) * 100, 1),
        }


class _SimpleCompressor:
    """Fallback compressor when HeadroomContextCompressor is not available."""

    def __init__(self, config: HeadroomConfig):
        self.config = config

    def compress(self, messages: List[Dict]) -> List[Dict]:
        """Simple whitespace normalization."""
        result = []
        for msg in messages:
            content = msg.get("content", "")
            # Basic normalization
            import re
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r'[ \t]+', ' ', content)
            content = re.sub(r' +\n', '\n', content)
            result.append({**msg, "content": content.strip()})
        return result

    def compress_text(self, text: str) -> str:
        """Simple text compression."""
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' +\n', '\n', text)
        return text.strip()
