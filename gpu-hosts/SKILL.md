---
name: gpu-hosts
description: "Operate the user's known RTX 4090 and H200 Linux GPU hosts. Use when the human explicitly asks to connect to, inspect, run, test, deploy, transfer files to/from, or troubleshoot the RTX 4090/H200 machines, or asks about their SSH account/network constraints. Load host facts from references/hosts.md only for these host-specific tasks; do not inject them into ordinary development work."
---

# GPU Hosts

Use the known GPU machines only when the task actually involves them. Read `references/hosts.md` before connecting or planning host-specific operations.

## Workflow

1. Resolve which host the human means.
2. Read its current facts and network constraints from `references/hosts.md`.
3. Inspect the local SSH configuration/key directory when the exact identity file is needed; do not guess a private-key filename.
4. Connect using the documented account/host and existing local key material.
5. Verify the target host and relevant service/process state before making changes.
6. Perform only the host operation the human requested.
7. Report concrete commands/results and any host-specific limitation.

## Network-aware behavior

- On a host documented as having no public Internet access, do not waste time repeatedly attempting public package/model downloads. Use already-present resources, internal mirrors, or stage files through an allowed connected machine when that is part of the requested workflow.
- On an Internet-capable host, normal external downloads are possible but still follow project/version requirements.

## Secrets

The reference contains non-secret connection metadata only. Never write private key bytes, passwords, tokens, passphrases, or other secrets into this skill/repository or user-visible logs.

## Scope

This skill owns reusable machine facts and host-operation guidance. Project-specific deployment architecture and application runbooks still belong to that project, not here.
