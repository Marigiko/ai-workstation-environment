#!/usr/bin/env bash
# Healthy only if the omniroute container is running+healthy AND the
# gateway answers on /v1/models. Never prints OMNIROUTE_API_KEY.
set -euo pipefail

GATEWAY_URL="http://127.0.0.1:20128/v1/models"

health="$(docker inspect -f '{{.State.Health.Status}}' omniroute 2>/dev/null || true)"
if [ "$health" != "healthy" ]; then
    exit 1
fi

if [ -n "${OMNIROUTE_API_KEY:-}" ]; then
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 \
        -H "Authorization: Bearer ${OMNIROUTE_API_KEY}" "$GATEWAY_URL" || true)"
    [ "$code" = "200" ] || exit 1
else
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$GATEWAY_URL" || true)"
    { [ "$code" = "200" ] || [ "$code" = "401" ]; } || exit 1
fi

exit 0
