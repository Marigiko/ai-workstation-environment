#!/usr/bin/env bash

if curl -sf http://localhost:8000/health &>/dev/null; then
    exit 0
fi
exit 1
