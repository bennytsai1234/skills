# Sources and Confidence

Use this reference when generating blueprint documents from user-provided
materials or inferred decisions.

## Required Block

Include this block near the top of generated documents when relevant:

```markdown
## Sources & Confidence

- Materials used:
- Inferred values to verify:
- Confirmed decisions:
- Open questions:
```

## Confidence Rules

- Mark screenshot-derived colors, fonts, spacing, layouts, and content as
  inferred unless the user provided source values.
- Mark database fields from sample records as inferred unless a schema was
  provided.
- Mark API shapes from observed requests as inferred unless an API contract was
  provided.
- Mark reference-site observations as inspiration, not permission to copy.
- Mark user-confirmed choices as confirmed only after the user explicitly
  accepts them.

## Discussion Modes

Use the lightest useful mode:

- Materials-driven: draft from supplied files, screenshots, schemas, or APIs;
  ask only about uncertain extractions.
- Discussion-driven: infer from the user's idea, then ask about gaps one at a
  time.
- Recommendation-driven: propose a default based on product type and
  architecture reasoning; discuss alternatives when the decision is costly.
- Accumulation-driven: collect risks, open questions, and assumptions as the
  session proceeds.

For high-stakes decisions (vibe, layout, navigation, data model, API
contract, permission model), use the **convergence loop** from
`convergence-protocol.md` instead of a single discussion mode — propose 2-3
candidates, iterate until lock.

## Downstream Meaning

For AI coding agents, inferred values are soft defaults. Confirmed values are
requirements. Open questions are stop points when implementation would otherwise
invent behavior.
