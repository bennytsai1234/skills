# Atlas Quality Checklist

Run before reporting initialization, refresh, or rebuild complete.

## Shape

- Output is only the atlas index and module docs.
- Index has purpose, provenance, module links, and routing summaries.
- Index has no delivery/reporting/language settings, copied project rules, architecture decisions, workflow instructions, or file inventories.
- Every module link resolves.
- Every path/link is relative and uses forward slashes.
- No initialization placeholder remains.
- No unrelated file was rewritten only for line-ending normalization.

## Grounding

- Module ownership and boundaries are supported by committed repository facts or persistent docs.
- Module summaries tell future work when to start there.
- Each module names representative scope, dependencies/impact, key flows, change routes, and real risks/boundaries.
- Search-answerable call-site/symbol/file inventories stay out of the map.
- Generic engineering advice is not presented as a repository-specific risk.

## Refresh

- Existing provenance was usable or the human explicitly selected a hand-scoped refresh.
- Changed source paths were filtered through scan exclusions.
- Only stale/new/removed routing areas were rewritten.
- Untouched module docs are byte-identical.
- Unmapped files were assigned through a real boundary decision rather than silently dropped.
- Provenance was updated last, after validation.

## Rebuild

- Only confirmed Atlas-generated map/legacy artifacts were replaced or removed.
- `docs/changes/**` and unrelated project docs were left alone.

## Final report

Report created/updated/removed atlas files, validation result, and any real `TODO` uncertainty. Follow higher-priority project/user delivery instructions; the atlas itself stores no delivery policy.
