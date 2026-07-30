#!/usr/bin/env bash
set -euo pipefail

# Check if key security tools are installed
found=0
for tool in nmap hashcat john hydra sqlmap nikto; do
    if command -v "$tool" &>/dev/null; then
        found=$((found + 1))
    fi
done

[ "$found" -ge 3 ]
