#!/usr/bin/env bash

if command -v python3 &>/dev/null; then
    exit 0
fi
if command -v python &>/dev/null; then
    exit 0
fi
exit 1
