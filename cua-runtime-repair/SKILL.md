---
name: cua-runtime-repair
description: Repair and verify Windows Codex CUA runtime package-resolution failures, especially missing @oai/cua/tinyskyAlt caused by URL-encoded package paths.
---

# CUA Runtime Repair

Use this skill when the Computer Use runtime fails before initialization with errors such as 'Cannot find package @oai/cua', 'Cannot find module @oai/cua/tinyskyAlt', or when the configured cua_node runtime contains packages under names such as %40oai instead of @oai.

The desired result is a working CUA session whose cua.getState() returns the current desktop/browser state. This skill repairs only the local Codex CUA runtime; it does not modify the active repository, application source code, database settings, or credentials.

## Workflow

1. Run the bundled repair script at scripts/repair_cua_runtime.ps1 with PowerShell. It reads the configured runtime manifest under the Codex installation, discovers existing percent-encoded filesystem names, and creates only missing aliases: directory junctions for directories and hardlinks for files. Existing files are never overwritten or deleted.

   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\repair_cua_runtime.ps1

   When the runtime is installed elsewhere, pass its exact cua_node root with -RuntimeRoot. Use -VerifyOnly for a read-only preflight.

2. The script must verify all of these with the same runtime Node executable:

   - @oai/cua/tinyskyAlt resolves. It is not imported here: since runtime 0.0.27 it reads CUA_REPL_ENABLED_SURFACES from node_repl's globalThis.nodeRepl, so a plain Node import always fails with "CUA_REPL_ENABLED_SURFACES is required"; step 3 covers it.
   - @oai/sky and @oai/sky/service import successfully.
   - The runtime's own setup.ps1 validation passes.

3. After the shell checks pass, reset the persistent CUA JavaScript session and make the first call exactly await cua.getState();. Confirm that the returned state visibly contains the available apps or browsers before doing any UI work.

## Boundaries

- Do not install @oai/cua from public npm; this is an internal bundled package. If the package is genuinely absent rather than URL-encoded, stop and report that the official Codex runtime must be restored or updated.
- Do not delete or rebuild the whole runtime. The repair is intentionally additive and reversible; a future Codex update may replace the runtime with a clean copy.
- Do not use Computer Use to open a terminal or execute repair commands. Run the PowerShell script through the normal command tool, then use CUA only for the final runtime/UI verification.
- Do not print or persist passwords, tokens, or other sensitive values while testing.

Report the exact runtime root, the number of aliases created or skipped, the three package check results, the setup.ps1 result, and whether cua.getState() succeeded. If final CUA verification is unavailable, distinguish that from a failed package repair.
