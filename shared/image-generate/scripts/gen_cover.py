#!/usr/bin/env python3
"""
Generate a blog post cover image based on article title and tags.

Usage:
  python3 gen_cover.py --title "文章標題" --tags "AI,LLM" --slug "2026-04-06-my-post" [--output path.png]

Output (stdout, one line):
  SAVED:/path/to/image.png
  or
  FAILED:reason
"""
import argparse
import subprocess
import sys
import os
import re

BLOG_ASSETS = os.path.expanduser(
    "~/projects/openclaw-blog/src/assets/post-covers"
)

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


def build_visual_prompt(title: str, tags: list[str]) -> str:
    """Convert Chinese article title + tags into an English visual prompt."""
    # Tag-to-visual mapping
    tag_visuals = {
        "ai": "neural network, glowing data streams",
        "llm": "large language model, text tokens floating in space",
        "rust": "gear mechanism, orange metallic",
        "python": "snake, blue and yellow",
        "frontend": "browser, colorful UI components",
        "astro": "space, stars, rocket",
        "database": "server racks, data cylinders",
        "security": "padlock, shield, cybersecurity",
        "cloud": "cloud infrastructure, kubernetes",
        "算法": "mathematical formulas, abstract graph",
        "deep learning": "layered neural network visualization",
        "transformer": "attention mechanism, matrix grids",
        "agent": "robot arm, autonomous decision tree",
    }

    visual_hints = []
    for tag in tags:
        t = tag.lower()
        for key, visual in tag_visuals.items():
            if key in t:
                visual_hints.append(visual)
                break

    # Build prompt
    hints = ", ".join(visual_hints[:2]) if visual_hints else "technology, abstract digital art"
    prompt = (
        f"blog post cover image, {hints}, "
        "wide 16:9 aspect ratio, dark background with subtle gradient, "
        "minimalist tech aesthetic, high quality digital illustration, "
        "no text, no watermark"
    )
    return prompt


def generate(title: str, tags: list[str], slug: str, output: str | None) -> str:
    os.makedirs(BLOG_ASSETS, exist_ok=True)

    if not output:
        output = os.path.join(BLOG_ASSETS, f"{slug}.png")

    prompt = build_visual_prompt(title, tags)

    gemini_script = os.path.join(SKILL_DIR, "gemini_generate.py")
    result = subprocess.run(
        ["python3", gemini_script, "--prompt", prompt, "--output", output],
        capture_output=True, text=True, timeout=210
    )
    if result.returncode == 0 and os.path.exists(output):
        return output

    return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate blog post cover image")
    parser.add_argument("--title", required=True, help="Article title (Chinese OK)")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--slug", required=True, help="Post slug (used as filename)")
    parser.add_argument("--output", default=None, help="Override output path")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    path = generate(title=args.title, tags=tags, slug=args.slug, output=args.output)

    if path:
        print(f"SAVED:{path}")
    else:
        print("FAILED:image generation failed")
        sys.exit(1)
