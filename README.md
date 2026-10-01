# Skills

Canonical home for reusable Codex and agent skills.

## Atlas development workflow

- `atlas-planner` — formal planning path: investigate and discuss with the human until problem/root cause/target/solution are explicitly confirmed, then write detailed `atlas/v4` packages and one dispatch plan.
- `atlas-relay` — execute a confirmed dispatch plan sequentially, route workers, independently accept results, record completion, and deliver the batch.
- `atlas-worker` — implement one detailed worker package and return real verification evidence.

## Repository foundation and environments

- `project-foundation` — initialize or standardize the minimal project docs: `AGENTS.md`, `README.md`, and `DESIGN.md` only for UI projects.
- `gpu-hosts` — load RTX 4090 / H200 host facts and operating guidance only for host-specific tasks.
- `dev-flow` — explicitly diagnose whether a company project has drifted from the intended local/AA/company-integration development path.
- `cota` — Cota platform-specific guidance.

## Other skills

- `blueprint` — 把已確認內容整理成可執行方案
- `bro` — 把上一則訊息改寫成白話
- `codex-update`
- `codex-wsl-terminal-repair`
- `compass` — 把偏掉的對話拉回正確方向
- `engineering-judgment` — 教你身為工程師如何做技術取捨與判斷
- `hermes-ops`
- `handoff` — 整理目前對話成已遮蔽敏感資料的代理交接文件
- `mmx-cli`
- `openclaw-ops`
- `summarize-project-work`
- `video-to-text`
- `windows-cjk-font-substitution`

## Structure

Each skill lives in its own directory with `SKILL.md`. Keep reusable references, scripts, assets, and `agents/openai.yaml` inside the owning skill. Prefer concise `SKILL.md` control planes and load detailed references only when the task needs them.
