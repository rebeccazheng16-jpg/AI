#!/bin/bash
# Video Clip Assembler — 一键启动
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$HOME/.claude/skills/xhs-video-downloader/.venv"
PORT="${1:-8765}"

echo "=== Video Clip Assembler ==="

# 1. Activate venv
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo "[OK] venv activated"
else
    echo "[ERROR] venv not found at $VENV_DIR"
    exit 1
fi

# 2. Check API keys (only Gemini needed — handles both transcription and translation)
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -n "$GOOGLE_API_KEY" ]; then
        export GEMINI_API_KEY="$GOOGLE_API_KEY"
        echo "[OK] Using GOOGLE_API_KEY as GEMINI_API_KEY"
    else
        echo "[WARN] GEMINI_API_KEY not set — transcription and translation will fail"
    fi
else
    echo "[OK] GEMINI_API_KEY set"
fi

# 3. Ensure temp dirs
mkdir -p "$SKILL_DIR/temp/clips"
mkdir -p "$SKILL_DIR/temp/build"

# 4. Start server
echo "[START] http://localhost:$PORT"
echo ""

# Open browser after short delay
(sleep 1 && open "http://localhost:$PORT") &

python "$SKILL_DIR/scripts/server.py" "$PORT"
