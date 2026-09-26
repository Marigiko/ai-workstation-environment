#!/usr/bin/env python3
"""
AI Proxy Server — Terax → MiMo/Claude with Headroom compression.

All requests are compressed by Headroom before reaching the LLM backend,
saving 60-90% of tokens. No API keys needed — uses MiMo Auto (free) and
Claude Max (login).
"""

import asyncio
import os
import re
import subprocess
import time
import uuid
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from headroom import CompressionConfig, HeadroomContextCompressor
from pydantic import BaseModel

app = FastAPI(title="AI Proxy Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Data Models
# ============================================

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    headroom: Optional[bool] = True  # Enable/disable compression per request


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    original_tokens: int = 0
    compressed_tokens: int = 0
    compression_ratio: float = 1.0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


# ============================================
# Global compressor
# ============================================

_compressor = HeadroomContextCompressor(CompressionConfig(
    enabled=True,
    max_tokens=4096,
    aggressive=True,
    preserve_code=True,
    strip_comments=True,
    normalize_whitespace=True,
    dedup_lines=True,
))


# ============================================
# Backend Handlers
# ============================================

class MiMoHandler:
    """Handle requests via MiMo CLI (`mimo run`)."""

    def __init__(self):
        self.binary = self._find_binary()

    def _find_binary(self) -> str:
        """Find the mimo binary path."""
        # Check common locations
        candidates = [
            "mimo",
            os.path.expanduser("~/.nvm/versions/node/v24.18.0/bin/mimo"),
            "/usr/local/bin/mimo",
        ]
        for path in candidates:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
            # Try which
            try:
                result = subprocess.run(
                    ["which", path], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
        return "mimo"

    async def complete(self, messages: List[Message], max_tokens: int = 1024) -> str:
        """Send messages to MiMo and get response."""
        prompt = self._build_prompt(messages)

        try:
            process = await asyncio.create_subprocess_exec(
                self.binary,
                "run",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120,
            )

            output = stdout.decode().strip()
            error_output = stderr.decode().strip()

            # Clean up MiMo output
            output = self._clean_output(output)

            if output:
                return output

            # If stdout empty, check stderr for useful info
            if error_output and "error" in error_output.lower():
                raise RuntimeError(f"MiMo error: {error_output[:200]}")

            raise RuntimeError("MiMo returned empty response")

        except asyncio.TimeoutError:
            raise RuntimeError("MiMo timeout after 120s")
        except FileNotFoundError:
            raise RuntimeError(f"MiMo binary not found at: {self.binary}")

    def _build_prompt(self, messages: List[Message]) -> str:
        """Build a single prompt from message list."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"[System]: {msg.content}")
            elif msg.role == "user":
                parts.append(msg.content)
            elif msg.role == "assistant":
                parts.append(f"[Assistant]: {msg.content}")
        return "\n\n".join(parts)

    def _clean_output(self, output: str) -> str:
        """Clean MiMo output by removing ANSI codes, banners, and noise."""
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)

        lines = output.split('\n')
        cleaned = []
        skip_patterns = [
            'build ·',
            'mimo-auto',
            'mimo-code',
            'mimo-v',
            '█▀▄▀█',
            '█ ▀ █',
            '▀   ▀',
            '>mimo',
            '> build',
            '───',
            '═══',
            'Commands:',
            'Positionals:',
            'Options:',
        ]

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            skip = False
            for pattern in skip_patterns:
                if pattern in stripped:
                    skip = True
                    break

            # Skip lines that look like CLI help
            if stripped.startswith('-') and '  ' in stripped:
                skip = True

            if not skip:
                cleaned.append(stripped)

        result = '\n'.join(cleaned)

        # If we stripped everything, return the original minus ANSI
        if not result.strip() and output.strip():
            return output.strip()

        return result


class ClaudeHandler:
    """Handle requests via Claude CLI (`claude -p`)."""

    def __init__(self):
        self.binary = self._find_binary()

    def _find_binary(self) -> str:
        """Find the claude binary path."""
        candidates = [
            "claude",
            os.path.expanduser("~/.local/bin/claude"),
            "/usr/local/bin/claude",
        ]
        for path in candidates:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
            try:
                result = subprocess.run(
                    ["which", path], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
        return "claude"

    async def complete(self, messages: List[Message], max_tokens: int = 1024) -> str:
        """Send messages to Claude and get response."""
        prompt = self._build_prompt(messages)

        try:
            process = await asyncio.create_subprocess_exec(
                self.binary,
                "-p",  # --print for non-interactive
                "--dangerously-skip-permissions",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=180,
            )

            output = stdout.decode().strip()

            if output:
                return output

            error = stderr.decode().strip()
            raise RuntimeError(f"Claude returned empty response: {error[:200]}")

        except asyncio.TimeoutError:
            raise RuntimeError("Claude timeout after 120s")
        except FileNotFoundError:
            raise RuntimeError(f"Claude binary not found at: {self.binary}")

    def _build_prompt(self, messages: List[Message]) -> str:
        """Build a single prompt from message list."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"[System]: {msg.content}")
            elif msg.role == "user":
                parts.append(msg.content)
            elif msg.role == "assistant":
                parts.append(f"[Assistant]: {msg.content}")
        return "\n\n".join(parts)


class OmniRouteHandler:
    """Handle requests via OmniRoute gateway (OpenAI-compatible)."""

    def __init__(self, model: str):
        self.model = model
        self.base_url = os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
        self.api_key = os.environ.get("OMNIROUTE_API_KEY", "")

    async def complete(self, messages: List[Message], max_tokens: int = 1024) -> str:
        """Send messages to OmniRoute chat completions."""
        messages_dict = [{"role": m.role, "content": m.content} for m in messages]

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages_dict,
                        "max_tokens": max_tokens,
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            raise RuntimeError("OmniRoute timeout after 60s")
        except Exception as e:
            raise RuntimeError(f"OmniRoute error: {str(e)[:200]}")


class OllamaHandler:
    """Handle requests via Ollama local API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: Optional[str] = None,
    ):
        self.base_url = base_url
        self.model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

    async def complete(self, messages: List[Message], max_tokens: int = 1024) -> str:
        """Send messages to Ollama and get response."""
        prompt = self._build_prompt(messages)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7,
                        },
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            raise RuntimeError("Ollama timeout after 120s")
        except Exception as e:
            raise RuntimeError(f"Ollama error: {str(e)[:200]}")

    def _build_prompt(self, messages: List[Message]) -> str:
        """Build a single prompt from message list."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"[System]: {msg.content}")
            elif msg.role == "user":
                parts.append(msg.content)
            elif msg.role == "assistant":
                parts.append(f"[Assistant]: {msg.content}")
        return "\n\n".join(parts)


# ============================================
# Model Registry
# ============================================

MODEL_REGISTRY = {
    "mimo": MiMoHandler(),
    "mimo-auto": MiMoHandler(),
    "mimo-fast": MiMoHandler(),
    "claude": ClaudeHandler(),
    "claude-code": ClaudeHandler(),
    "omniroute": OmniRouteHandler("liviano"),
    "liviano": OmniRouteHandler("liviano"),
    "gemini": OmniRouteHandler("liviano"),
    "gemini-flash": OmniRouteHandler("liviano"),
    "agente": OmniRouteHandler("agente"),
    "smart": OmniRouteHandler("agente"),
    "local": OllamaHandler(),
    "ollama": OllamaHandler(),
}


def get_handler(model: str):
    """Get the appropriate handler for a model."""
    if model in MODEL_REGISTRY:
        return MODEL_REGISTRY[model]
    for key, handler in MODEL_REGISTRY.items():
        if model.startswith(key):
            return handler
    return MODEL_REGISTRY["mimo"]


# ============================================
# API Endpoints
# ============================================

@app.get("/health")
async def health():
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                ollama_status = "connected"
            else:
                ollama_status = "error"
    except Exception:
        ollama_status = "disconnected"

    return {
        "status": "ok",
        "version": "2.0.0",
        "headroom": "enabled",
        "backends": {
            "mimo": MiMoHandler().binary,
            "claude": ClaudeHandler().binary,
            "ollama": ollama_status,
        },
    }


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "omniroute",
                "object": "model",
                "owned_by": "omniroute",
                "description": "OmniRoute gateway (liviano, cheap/free)",
            },
            {
                "id": "liviano",
                "object": "model",
                "owned_by": "omniroute",
                "description": "OmniRoute liviano combo (light work)",
            },
            {
                "id": "agente",
                "object": "model",
                "owned_by": "omniroute",
                "description": "OmniRoute agente combo (hard/coding work)",
            },
            {
                "id": "gemini",
                "object": "model",
                "owned_by": "omniroute",
                "description": "OmniRoute liviano combo (legacy alias)",
            },
            {
                "id": "gemini-flash",
                "object": "model",
                "owned_by": "omniroute",
                "description": "OmniRoute liviano combo (legacy alias)",
            },
            {"id": "mimo", "object": "model", "owned_by": "xiaomi"},
            {"id": "mimo-auto", "object": "model", "owned_by": "xiaomi"},
            {"id": "mimo-fast", "object": "model", "owned_by": "xiaomi"},
            {"id": "claude", "object": "model", "owned_by": "anthropic"},
            {"id": "claude-code", "object": "model", "owned_by": "anthropic"},
            {
                "id": "local",
                "object": "model",
                "owned_by": "ollama",
                "description": "Local Ollama (qwen2.5-coder:7b)",
            },
            {
                "id": "ollama",
                "object": "model",
                "owned_by": "ollama",
                "description": "Ollama local models",
            },
            {"id": "smart", "object": "model", "owned_by": "omniroute"},
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle OpenAI-compatible chat completion requests.

    All requests are compressed by Headroom before forwarding to the backend.
    """
    try:
        handler = get_handler(request.model)

        # Convert to dict format for compression
        messages_dict = [{"role": m.role, "content": m.content} for m in request.messages]

        # Original token estimate
        original_tokens = _compressor.estimate_tokens(
            " ".join(m.content for m in request.messages)
        )

        # Apply Headroom compression unless disabled
        if request.headroom and _compressor.config.enabled:
            compressed = _compressor.compress(messages_dict)
            compressed_tokens = _compressor.estimate_tokens(
                " ".join(m.get("content", "") for m in compressed)
            )
            # Convert back to Message objects
            compressed_messages = [
                Message(role=m["role"], content=m["content"])
                for m in compressed
            ]
        else:
            compressed_messages = request.messages
            compressed_tokens = original_tokens

        # Forward to backend
        response_text = await handler.complete(
            compressed_messages,
            request.max_tokens or 1024,
        )

        # Calculate compression stats
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(role="assistant", content=response_text),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=original_tokens,
                completion_tokens=_compressor.estimate_tokens(response_text),
                total_tokens=original_tokens + _compressor.estimate_tokens(response_text),
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=ratio,
            ),
        )

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/v1/compress")
async def compress_endpoint(request: ChatCompletionRequest):
    """Standalone compression endpoint — returns compressed messages without LLM call."""
    messages_dict = [{"role": m.role, "content": m.content} for m in request.messages]

    original_tokens = _compressor.estimate_tokens(
        " ".join(m.content for m in request.messages)
    )

    compressed = _compressor.compress(messages_dict)

    compressed_tokens = _compressor.estimate_tokens(
        " ".join(m.get("content", "") for m in compressed)
    )

    ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

    return {
        "original": messages_dict,
        "compressed": compressed,
        "stats": {
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "ratio": ratio,
            "savings_percent": round((1 - ratio) * 100, 1),
        },
    }


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
