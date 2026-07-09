#!/usr/bin/env bash
set -euo pipefail

# AI Proxy Client — quick CLI for testing the proxy server

PROXY_URL="${PROXY_URL:-http://localhost:8090}"

usage() {
    echo "Usage: $0 <model> <prompt>"
    echo ""
    echo "Models: mimo, mimo-auto, mimo-fast, claude, claude-code, local, smart"
    echo ""
    echo "Examples:"
    echo "  $0 mimo-auto 'hello world'"
    echo "  $0 claude 'write a python function'"
    echo "  $0 local 'explain this code' < code.py"
    exit 1
}

if [ $# -lt 2 ]; then
    usage
fi

MODEL="$1"
shift
PROMPT="$*"

# Read from stdin if no prompt args
if [ -z "$PROMPT" ]; then
    PROMPT=$(cat)
fi

# Build JSON payload using python for proper escaping
PAYLOAD=$(python3 -c "
import json
prompt = '''$PROMPT'''
payload = {
    'model': '$MODEL',
    'messages': [{'role': 'user', 'content': prompt}],
    'max_tokens': 1024,
    'headroom': True
}
print(json.dumps(payload))
")

# Call proxy and save response
RESPONSE=$(curl -s -X POST "$PROXY_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Parse response using python
python3 -c "
import json, sys

try:
    data = json.loads(sys.stdin.read())
except json.JSONDecodeError as e:
    print(f'JSON decode error: {e}', file=sys.stderr)
    sys.exit(1)

if 'detail' in data:
    print(f'Error: {data[\"detail\"]}', file=sys.stderr)
    sys.exit(1)

content = data['choices'][0]['message']['content']
usage = data.get('usage', {})

print(content)

if usage:
    orig = usage.get('original_tokens', 0)
    comp = usage.get('compressed_tokens', 0)
    ratio = usage.get('compression_ratio', 1.0)
    savings = (1 - ratio) * 100 if ratio < 1 else 0
    print(f'\n---\nTokens: {orig} → {comp} (savings: {savings:.1f}%)', file=sys.stderr)
" <<< "$RESPONSE"
