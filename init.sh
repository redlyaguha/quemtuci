#!/usr/bin/env bash
# Заглушка: скачивает тестовые PDF и грузит их через API (DO-03).
# TODO: реализовать в рамках issue [DO-03].
set -euo pipefail
API="${API:-http://localhost:8000/api/v1}"
echo "init.sh — заглушка. Реализация в issue [DO-03]."
echo "API endpoint: $API/documents/upload"
