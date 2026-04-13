#!/usr/bin/env python3
"""Build bounded curated inputs for writing skills from hourly raw RSS data."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SOURCES_FILE = ROOT / "rss_sources.json"

INTEREST_KEYWORDS = {
    "agent": 3, "agents": 3, "agentic": 3, "multi-agent": 3,
    "mcp": 3, "model context protocol": 3,
    "skill": 3, "skills": 3,
    "openclaw": 3, "claude code": 3, "codex": 3, "cursor": 3,
    "workflow": 3, "orchestration": 3,
    "rag": 2, "retrieval": 2, "embedding": 2, "vector": 2,
    "memory": 2, "knowledge graph": 2, "ontology": 2,
    "langchain": 2, "llamaindex": 2, "crewai": 2, "autogen": 2,
    "tool use": 2, "function calling": 2,
    "prompt engineering": 2, "prompt": 2,
    "fine-tuning": 2, "fine tuning": 2,
    "deployment": 2, "production": 2, "observability": 2,
    "evaluation": 2, "benchmark": 2,
    "llm": 1, "gpt": 1, "claude": 1, "gemini": 1,
    "transformer": 1, "diffusion": 1,
    "quantitative": 1, "trading": 1, "finance": 1,
    "open source": 1, "open-source": 1, "github": 1,
}

PROFILE_CONFIG: dict[str, dict[str, Any]] = {
    "morning": {
        "max_total": 28,
        "per_source": 2,
        "category_boost": {"company": 3, "community": 2, "media": 2, "ai-agent": 3, "cn_media": 1, "newsletter": 1, "papers": 0},
        "include_categories": {"company", "community", "media", "ai-agent", "cn_media", "newsletter", "papers"},
        "purpose": "rss-morning-report shortlist",
    },
    "digest": {
        "max_total": 18,
        "per_source": 1,
        "category_boost": {"papers": 4, "newsletter": 3, "ai-agent": 3, "company": 2, "media": 1, "community": 1, "cn_media": 1},
        "include_categories": {"papers", "newsletter", "ai-agent", "company", "media", "community", "cn_media"},
        "purpose": "daily-tech-digest shortlist",
    },
    "noon": {
        "max_total": 24,
        "per_source": 2,
        "category_boost": {"company": 4, "media": 2, "community": 2, "ai-agent": 2, "cn_media": 1, "newsletter": 1, "papers": 1},
        "include_categories": {"company", "media", "community", "ai-agent", "cn_media", "newsletter", "papers"},
        "purpose": "midday writing shortlist",
    },
}


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    iso = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def load_source_categories() -> dict[str, str]:
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources = json.load(f)
    return {src.get("name", ""): src.get("category", "unknown") for src in sources}


def score_interest(text: str) -> int:
    lowered = text.lower()
    return sum(weight for keyword, weight in INTEREST_KEYWORDS.items() if keyword in lowered)


def recency_score(ts: float, now_ts: float) -> int:
    if ts <= 0:
        return 0
    age_hours = max(0.0, (now_ts - ts) / 3600)
    if age_hours <= 6:
        return 4
    if age_hours <= 12:
        return 3
    if age_hours <= 24:
        return 2
    if age_hours <= 48:
        return 1
    return 0


def clean_items(items: list[dict[str, Any]], source_to_category: dict[str, str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for it in items:
        title = (it.get("title") or "").strip()
        url = (it.get("url") or "").strip()
        if not title or not url or not url.startswith("http") or url in seen:
            continue
        source = (it.get("source") or "").strip() or "unknown"
        category = source_to_category.get(source, "unknown")
        desc = (it.get("desc") or "").strip()
        date = (it.get("date") or "").strip()
        dt = parse_dt(date)
        cleaned.append({"title": title, "url": url, "source": source, "category": category, "desc": desc, "date": date, "ts": dt.timestamp() if dt else 0})
        seen.add(url)
    return cleaned


def select_candidates(items: list[dict[str, Any]], profile: str) -> list[dict[str, Any]]:
    cfg = PROFILE_CONFIG[profile]
    include_categories = cfg["include_categories"]
    now_ts = datetime.now(timezone.utc).timestamp()

    ranked: list[dict[str, Any]] = []
    for it in items:
        category = it.get("category", "unknown")
        if category not in include_categories:
            continue
        row = dict(it)
        row["score"] = score_interest(f"{it.get('title', '')} {it.get('desc', '')}")
        row["score"] += cfg["category_boost"].get(category, 0)
        row["score"] += recency_score(it.get("ts", 0), now_ts)
        ranked.append(row)

    ranked.sort(key=lambda x: (-x.get("score", 0), -x.get("ts", 0), x.get("source", "")))

    by_source: dict[str, int] = defaultdict(int)
    result: list[dict[str, Any]] = []
    for it in ranked:
        source = it.get("source", "unknown")
        if by_source[source] >= cfg["per_source"]:
            continue
        result.append(it)
        by_source[source] += 1
        if len(result) >= cfg["max_total"]:
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build curated writing inputs from hourly raw JSON")
    parser.add_argument("--input", required=True)
    parser.add_argument("--profile", required=True, choices=sorted(PROFILE_CONFIG))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(json.dumps({"ok": False, "error": f"missing input: {in_path}"}, ensure_ascii=False))
        return 1

    with open(in_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        print(json.dumps({"ok": False, "error": "raw input must be a JSON list"}, ensure_ascii=False))
        return 1

    source_to_category = load_source_categories()
    cleaned = clean_items(raw, source_to_category)
    candidates = select_candidates(cleaned, args.profile)
    stats = Counter(it.get("category", "unknown") for it in candidates)
    payload = {
        "ok": True,
        "profile": args.profile,
        "purpose": PROFILE_CONFIG[args.profile]["purpose"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFile": str(in_path),
        "stats": {"rawItems": len(raw), "cleanItems": len(cleaned), "candidateItems": len(candidates), "byCategoryCandidates": dict(stats)},
        "candidates": [
            {"title": it["title"], "url": it["url"], "source": it["source"], "category": it["category"], "date": it["date"], "desc": it["desc"], "score": it["score"]}
            for it in candidates
        ],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "out": str(out_path), "stats": payload["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
