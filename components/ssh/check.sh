#!/usr/bin/env bash

if command -v ssh &>/dev/null; then
    exit 0
fi
exit 1
