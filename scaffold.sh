#!/usr/bin/env bash
# 用法: scaffold.sh <目标目录> <项目名> <项目一句话> [YYYY-MM-DD]
set -euo pipefail
exec python3 "$(dirname "${BASH_SOURCE[0]}")/scaffold.py" "$@"
