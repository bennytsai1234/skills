# {{PROJECT_NAME}} Codebase Atlas

This is the Codebase Atlas agent entrypoint for this project. Follow these
steps for every operation in this project.

## Usage

1. Preserve the user's original request.
1. Open `{{MAIN_WORKFLOW_FILE}}` and follow it.
1. Do not begin any operation before reading the atlas index.
1. Use plain language for all user-facing reports. Do not mention module names,
   file paths, or code snippets to the user.
1. For any operation that edits files, provide Before / After and wait for user
   confirmation before editing.
1. Finish according to this delivery policy: {{DELIVERY_POLICY}}

## Do Not Do

- Do not rerun Codebase Atlas initialization unless the user explicitly asks
  for a full rebuild.
- Do not skip reading the atlas index.
- Do not edit files before the user confirms Before / After.
