#!/usr/bin/env bash
# Topic Deep Research → Blog
# 入口腳本：協調多源搜尋、彙整，輸出研究摘要由 AI 直接寫文章

set -e

TOPIC="$1"
WORKDIR="$HOME/.openclaw/workspace/~/skills/shared/topic-deep-research"
OUTPUT_DIR="$HOME/projects/openclaw-blog/src/content/post"
SECRETS_DIR="$HOME/.openclaw/workspace/.secrets"
TIMESTAMP=$(date +%Y-%m-%d)
SLUG=$(echo "$TOPIC" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]' | sed 's/^-+|-+$//g')
OUTPUT_FILE="${OUTPUT_DIR}/${TIMESTAMP}-${SLUG}.md"
RESEARCH_FILE="${OUTPUT_DIR}/${TIMESTAMP}-${SLUG}-research.json"
TEMP_DIR=$(mktemp -d)
GIT_DIR="$HOME/projects/openclaw-blog"

echo "[topic-deep-research] 開始研究：$TOPIC"

# 清理退出（但保留 research file）
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 讀取 Tavily API Key
TAVILY_KEY=""
if [ -f "$SECRETS_DIR/tavily.key" ]; then
    TAVILY_KEY=$(cat "$SECRETS_DIR/tavily.key" | tr -d '\n')
fi

# Step 1: 多源搜尋
echo "[1/4] 多源搜尋中..."

TAVILY_OUTPUT="${TEMP_DIR}/tavily.json"
if [ -n "$TAVILY_KEY" ]; then
    echo "  → Tavily 搜尋..."
    python3 "$WORKDIR/scripts/tavily_search.py" "$TOPIC" "$TAVILY_KEY" > "$TAVILY_OUTPUT" 2>&1 || true
    if [ -s "$TAVILY_OUTPUT" ]; then
        echo "  ✓ Tavily 完成"
    else
        echo "  ✗ Tavily 無輸出，改用 DuckDuckGo fallback"
        echo "[]" > "$TAVILY_OUTPUT"
    fi
else
    echo "  ⚠ 無 Tavily API Key，跳過"
    echo "[]" > "$TAVILY_OUTPUT"
fi

DDG_OUTPUT="${TEMP_DIR}/ddg.json"
echo "  → DuckDuckGo 搜尋..."
python3 "$WORKDIR/scripts/duckduckgo_search.py" "$TOPIC" > "$DDG_OUTPUT" 2>&1 || true
echo "  ✓ DuckDuckGo 完成"

GITHUB_OUTPUT="${TEMP_DIR}/github.json"
echo "  → GitHub 搜尋..."
python3 "$WORKDIR/scripts/github_search.py" "$TOPIC" > "$GITHUB_OUTPUT" 2>&1 || true
echo "  ✓ GitHub 完成"

RSS_OUTPUT="${TEMP_DIR}/rss.json"
echo "  → RSS 內容抓取..."
python3 "$WORKDIR/scripts/rss_search.py" "$TOPIC" > "$RSS_OUTPUT" 2>&1 || true
echo "  ✓ RSS 完成"

# Step 2: 去重與彙整
echo "[2/4] 去重與彙整..."
python3 "$WORKDIR/scripts/dedupe_summarize.py" \
    "$TEMP_DIR/tavily.json" \
    "$TEMP_DIR/ddg.json" \
    "$TEMP_DIR/github.json" \
    "$TEMP_DIR/rss.json" \
    > "${TEMP_DIR}/consolidated.json" 2>&1

echo "[3/4] 生成研究摘要..."
RESEARCH_SUMMARY=$(python3 "$WORKDIR/scripts/write_blog.py" "$TOPIC" "${TEMP_DIR}/consolidated.json")

# Step 3: 儲存研究資料（供 AI 寫文章用）
echo "[4/4] 研究資料已就緒..."
mkdir -p "$OUTPUT_DIR"
cp "${TEMP_DIR}/consolidated.json" "$RESEARCH_FILE"

# 輸出研究摘要供 AI 讀取
echo ""
echo "=== RESEARCH_SUMMARY_START ==="
echo "$RESEARCH_SUMMARY"
echo "=== RESEARCH_SUMMARY_END ==="
echo ""
echo "研究 JSON 已儲存：$RESEARCH_FILE"
echo ""
echo "========================================"
echo "請根據以上研究摘要，生成 12 章結構化部落格文章，"
echo "並寫入：$OUTPUT_FILE"
echo "最後 git add + commit + push 到 openclaw-blog"
echo "========================================"
