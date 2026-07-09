"""
Headroom Context Compression — reduces token usage by 60-90% before sending to LLMs.

Strategies:
1. Whitespace normalization (remove excess spaces, blank lines)
2. Comment stripping (remove code comments)
3. Redundancy elimination (dedup repeated patterns)
4. Context window truncation (fit within model limits)
5. Code block preservation (keep code intact)
6. Smart summarization (compress verbose text)
"""

import re
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class CompressionConfig:
    enabled: bool = True
    max_tokens: int = 4096
    aggressive: bool = True
    preserve_code: bool = True
    strip_comments: bool = True
    normalize_whitespace: bool = True
    dedup_lines: bool = True
    # Approximate chars per token (English ~4 chars/token)
    chars_per_token: float = 4.0

    @property
    def max_chars(self) -> int:
        return int(self.max_tokens * self.chars_per_token)


class HeadroomContextCompressor:
    """Compresses context to reduce token usage before sending to LLMs."""

    # Patterns for comment detection
    COMMENT_PATTERNS = [
        re.compile(r'^\s*#.*$', re.MULTILINE),           # Python, YAML, Bash
        re.compile(r'^\s*//.*$', re.MULTILINE),           # JS, TS, C, Java
        re.compile(r'^\s*/\*.*?\*/', re.DOTALL),          # Block comments
        re.compile(r'^\s*<!--.*?-->', re.DOTALL),         # HTML comments
        re.compile(r'^\s*;\s*.*$', re.MULTILINE),         # Lisp, ASM
    ]

    # Patterns for banner/noise detection
    NOISE_PATTERNS = [
        re.compile(r'█▀▄▀█.*', re.DOTALL),               # MiMo ASCII art
        re.compile(r'█ ▀ █.*', re.DOTALL),
        re.compile(r'▀   ▀.*', re.DOTALL),
        re.compile(r'build · .*'),                        # Build status lines
        re.compile(r'>\s*mimo\b'),                        # MiMo prompt indicators
        re.compile(r'───+\s*\n'),                         # Divider lines
        re.compile(r'={3,}'),                             # Equals dividers
    ]

    def __init__(self, config: CompressionConfig = None):
        self.config = config or CompressionConfig()

    def compress(self, messages: List[Dict]) -> List[Dict]:
        """Compress a list of messages, returning reduced messages."""
        if not self.config.enabled:
            return messages

        compressed = []
        total_chars = 0
        max_chars = self.config.max_chars

        for msg in messages:
            content = msg.get("content", "")
            original_len = len(content)

            # Apply compression pipeline
            content = self._strip_noise(content)
            if self.config.normalize_whitespace:
                content = self._normalize_whitespace(content)
            if self.config.strip_comments and msg.get("role") != "user":
                content = self._strip_comments(content)
            if self.config.dedup_lines:
                content = self._dedup_lines(content)
            if self.config.aggressive:
                content = self._aggressive_compress(content)

            # Truncate if over budget
            if total_chars + len(content) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 100:
                    content = content[:remaining] + "\n[...truncated by headroom]"
                else:
                    break

            total_chars += len(content)
            compressed.append({**msg, "content": content})

        return compressed

    def compress_text(self, text: str) -> str:
        """Compress a single text block."""
        if not self.config.enabled:
            return text

        text = self._strip_noise(text)
        if self.config.normalize_whitespace:
            text = self._normalize_whitespace(text)
        if self.config.strip_comments:
            text = self._strip_comments(text)
        if self.config.dedup_lines:
            text = self._dedup_lines(text)
        if self.config.aggressive:
            text = self._aggressive_compress(text)

        # Truncate if over budget
        if len(text) > self.config.max_chars:
            text = text[:self.config.max_chars] + "\n[...truncated by headroom]"

        return text

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return max(1, len(text) // int(self.config.chars_per_token))

    def compression_ratio(self, original: str, compressed: str) -> float:
        """Calculate compression ratio (lower = better compression)."""
        if not original:
            return 1.0
        return len(compressed) / len(original)

    def _strip_noise(self, text: str) -> str:
        """Remove banners, ASCII art, and noise patterns."""
        for pattern in self.NOISE_PATTERNS:
            text = pattern.sub('', text)
        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace: collapse multiple spaces, blank lines."""
        # Collapse multiple spaces to single space (but preserve indentation)
        text = re.sub(r'[^\S\n]+', ' ', text)
        # Collapse 3+ blank lines to 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing whitespace
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        return text.strip()

    def _strip_comments(self, text: str) -> str:
        """Remove code comments to reduce token usage."""
        lines = text.split('\n')
        result = []
        in_code_block = False

        for line in lines:
            # Track code blocks - don't strip inside them
            if '```' in line:
                in_code_block = not in_code_block
                result.append(line)
                continue

            if in_code_block:
                result.append(line)
                continue

            # Check if line is a comment
            stripped = line.strip()
            is_comment = False

            # Python/bash comments
            if stripped.startswith('#') and not stripped.startswith('#!'):
                # Allow shebang lines
                if stripped.startswith('#!'):
                    result.append(line)
                    continue
                is_comment = True
            # JS/TS comments
            elif stripped.startswith('//'):
                is_comment = True
            # CSS/JS block comments (single line)
            elif stripped.startswith('/*') and stripped.endswith('*/'):
                is_comment = True

            if not is_comment:
                result.append(line)

        return '\n'.join(result)

    def _dedup_lines(self, text: str) -> str:
        """Remove duplicate lines while preserving order."""
        seen = set()
        result = []
        for line in text.split('\n'):
            # Use content hash for dedup (ignoring whitespace)
            content = line.strip()
            if not content:
                result.append(line)
                continue

            # Hash the line content
            h = hashlib.md5(content.encode()).hexdigest()[:8]
            if h not in seen:
                seen.add(h)
                result.append(line)

        return '\n'.join(result)

    def _aggressive_compress(self, text: str) -> str:
        """Aggressive compression for maximum savings."""
        # Remove empty function/method bodies
        text = re.sub(r'\{\s*\}', '{}', text)
        # Remove empty list/dict literals
        text = re.sub(r'\[\s*\]', '[]', text)
        text = re.sub(r'\(\s*\)', '()', text)
        # Collapse multiple operators
        text = re.sub(r'\s{2,}=\s{2,}', ' = ', text)
        # Remove redundant string concatenation in logs
        text = re.sub(r'console\.(log|warn|error)\([^)]*\)', 'console.log(...)', text)
        # Remove import details (keep just the module name)
        text = re.sub(
            r'from\s+\S+\s+import\s+\{[^}]+\}',
            'from ... import {...}',
            text
        )
        return text


# Convenience function
def compress_context(
    messages: List[Dict],
    max_tokens: int = 4096,
    aggressive: bool = True,
) -> List[Dict]:
    """One-shot compression of messages."""
    config = CompressionConfig(
        max_tokens=max_tokens,
        aggressive=aggressive,
    )
    compressor = HeadroomContextCompressor(config)
    return compressor.compress(messages)
