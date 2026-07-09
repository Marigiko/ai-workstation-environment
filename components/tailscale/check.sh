#!/usr/bin/env bash

if command -v tailscale &>/dev/null; then
    exit 0
fi
exit 1
