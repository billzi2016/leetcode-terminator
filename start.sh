#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "未找到 .venv，请先运行: python -m venv .venv && pip install -r requirements.txt"
  exit 1
fi

echo "启动 LeetCode Terminator..."
echo "访问: http://localhost:8000"
echo "停止: Ctrl+C  或  kill \$(lsof -ti:8000)"
echo ""

python manage.py runserver
