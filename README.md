# Skills

Canonical home for reusable Codex and agent skills.

## Atlas development workflow

- `atlas-fast` — default path for ordinary development: navigate with the atlas when available, then investigate/implement directly with proportional verification.
- `atlas-planner` — formal planning path: investigate and discuss with the human until problem/root cause/target/solution are explicitly confirmed, then write detailed `atlas/v4` packages and one dispatch plan.
- `atlas-relay` — execute a confirmed dispatch plan sequentially, route workers, independently accept results, record completion, and deliver the batch.
- `atlas-worker` — implement one detailed worker package and return real verification evidence.
- `codebase-atlas` — explicitly build/refresh/rebuild the engineering navigation map only.

## Repository foundation and environments

- `project-foundation` — initialize or standardize `AGENTS.md`, `README.md`, `DEVELOPMENT.md`, optional `DESIGN.md`, optional `docs/architecture.md`, then initialize/refresh Codebase Atlas when real source structure exists.
- `gpu-hosts` — load RTX 4090 / H200 host facts and operating guidance only for host-specific tasks.
- `dev-flow` — explicitly diagnose whether a company project has drifted from the intended local/AA/company-integration development path.
- `cota` — Cota platform-specific guidance.

## Other skills

- `blueprint` — 把已確認內容整理成可執行方案
- `bro` — 把上一則訊息改寫成白話
- `codebase-memory`
- `codex-update`
- `codex-wsl-terminal-repair`
- `compass` — 把偏掉的對話拉回正確方向
- `hermes-ops`
- `mmx-cli`
- `openclaw-ops`
- `project-genius` — production code 前的產品需求與視覺原型收斂
- `summarize-project-work`
- `video-to-text`
- `windows-cjk-font-substitution`

## Structure

Each skill lives in its own directory with `SKILL.md`. Keep reusable references, scripts, assets, and `agents/openai.yaml` inside the owning skill. Prefer concise `SKILL.md` control planes and load detailed references only when the task needs them.
