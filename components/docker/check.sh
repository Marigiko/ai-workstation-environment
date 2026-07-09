#!/usr/bin/env bash

if command -v docker &>/dev/null && docker info &>/dev/null; then
    exit 0
fi
exit 1
