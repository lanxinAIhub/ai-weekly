#!/bin/bash
# AI开源周报 - 发布脚本
# 用法: ./scripts/publish.sh [issue_dir]
# 例如: ./scripts/publish.sh issues/2026-W17

set -e

REPO_DIR="/tmp/ai-weekly"
TOKEN_FILE="/home/lanxin/.github_token"
ISSUE_DIR="${1:-}"

if [ -z "$ISSUE_DIR" ]; then
    ISSUE_DIR=$(ls -d $REPO_DIR/issues/2* | sort | tail -1)
    echo "未指定期号，自动选择最新: $ISSUE_DIR"
fi

if [ ! -d "$ISSUE_DIR" ]; then
    echo "❌ 目录不存在: $ISSUE_DIR"
    exit 1
fi

cd "$REPO_DIR"

# 复制周报到根目录 README
if [ -f "$ISSUE_DIR/README.md" ]; then
    cp "$ISSUE_DIR/README.md" "$REPO_DIR/README.md"
    echo "✅ README.md 已更新"
fi

# 配置 git 身份（若未配置）
git config user.email "ai-weekly@openclaw.ai" 2>/dev/null || true
git config user.name "AI开源周报 Bot" 2>/dev/null || true

# 提交
git add -A
git commit -m "📖 第 $(basename $ISSUE_DIR) 期周报更新 - $(date '+%Y-%m-%d')" || echo "没有新变更"

# 推送
TOKEN=$(cat "$TOKEN_FILE")
git remote set-url origin "https://x-access-token:${TOKEN}@github.com/lanxinAIhub/ai-weekly.git"
git push origin main

echo "✅ 发布完成: https://github.com/lanxinAIhub/ai-weekly"
