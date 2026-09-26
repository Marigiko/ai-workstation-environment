#!/usr/bin/env bash

if curl -fsS -o /dev/null http://127.0.0.1:5678/healthz 2>/dev/null; then
    exit 0
fi
exit 1
