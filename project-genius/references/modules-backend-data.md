# Backend, Data, and API Blueprint Rules

Deep reference used during Stage 2 Step 2.6 (data model and domain). The
new flow produces `04-data-model.md` from these rules, after the user has
locked each entity, endpoint, and permission decision via the convergence
loop.

Backend and data plans must respect the architecture reasoning output. The
data model, auth model, API shape, and storage strategy are high-cost decisions
when other modules depend on them.

## Backend blueprint

Define:
- domain areas.
- business rules.
- services or modules.
- background jobs.
- external integrations.
- emails or notifications.
- error handling.
- security concerns.

## Data model

For each entity define:
- name.
- purpose.
- fields.
- relationships.
- indexes or lookup patterns.
- validation.
- ownership and permissions.
- lifecycle states.

## API contract

For each endpoint or server action define:
- method and path or action name.
- purpose.
- auth requirement.
- request shape.
- response shape.
- error cases.
- frontend consumers.

When the project is full-stack, each frontend flow that reads or writes data
must map to either an API endpoint, server action, background job, or explicit
mock-only placeholder.

## Auth and permissions

Define:
- login methods.
- user roles.
- protected routes.
- role matrix.
- server-side checks.
- client-side visibility rules.

## Storage

For file or media storage define:
- storage provider.
- bucket or folder strategy.
- file naming.
- upload limits.
- access control.
- transformation or optimization pipeline.

## Security and privacy

Define when relevant:
- data classification.
- sensitive fields.
- retention rules.
- audit events.
- permission checks.
- rate limits.
- abuse cases.
- backup and recovery expectations.
