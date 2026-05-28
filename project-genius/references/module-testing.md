# Testing Module

Cross-cutting reference — consulted at Stage 1 Step 1.7 (module activation)
and again at Stage 2 Step 2.8 (tech stack), where CI gate and tooling
decisions become concrete.

## Activation Criteria

Activate the Testing module when any of these apply:

- The product handles money, health data, or regulated information.
- The team has more than one developer.
- The user mentions CI/CD, automated tests, coverage, or QA.
- The product has complex business rules (permission model, pricing logic,
  multi-step workflows, state machines).
- The downstream coding agent is Claude Code, Codex, or similar autonomous
  agent — automated tests are the primary guard against agent regressions.

Skip when: prototype-only mode is active and the user has explicitly said no
backend is needed.

Output: `10-testing.md`

---

## Question Tree

Ask only questions whose answers change tooling, architecture, or delivery
order. One at a time.

### Philosophy and Risk Tolerance

- What breaks if a bug reaches production? (Data loss / wrong charges /
  embarrassment / nothing critical.)
- Does the team have a testing culture, or is this being set up from scratch?
- Is there a minimum coverage threshold, or is coverage aspirational?

### Test Layer Priorities

Ask the user to rank in order of value (not all need to be high):

- **End-to-end tests** — simulate a real user browser session. High
  confidence, slow, brittle.
- **Integration tests** — test a vertical slice (API → DB → response).
  Catches contract and query bugs.
- **Unit tests** — test a pure function or isolated module. Fast, narrow.
- **Visual regression tests** — screenshot comparison against the locked
  prototype. Catches UI drift.
- **Accessibility tests** — automated axe / pa11y scans. Catches ARIA and
  contrast violations.

For most web apps, default recommendation: integration > E2E > unit.
Read this recommendation back and require confirmation or revision.

### E2E Testing (if activated)

- Framework: Playwright (recommended) / Cypress / Puppeteer.
- Which user journeys MUST have E2E coverage? (e.g. sign-up, primary
  task completion, payment.)
- Run on CI on every PR, or only on merge to main?
- Browser targets: Chromium only / cross-browser.
- Authenticated flows: seed user account or use real auth?

### Integration Testing

- Test against a real database (recommended) or mocked DB?
- Test data strategy: fixtures seeded before each test / factory functions /
  shared persistent seed.
- External API calls: real sandbox / recorded cassettes (VCR) / mocked.

### Unit Testing

- Framework: Vitest / Jest / pytest / Go test / other.
- Coverage threshold gate on CI? (If yes, what %?)
- Pure functions only, or also component render tests?

### Visual Regression (if activated)

- Baseline from locked prototype HTML or from first build screenshots?
- Threshold for acceptable pixel diff.
- Which screens are regression-guarded?

### Accessibility Testing

- Automated scan (axe-core / pa11y) in CI: yes / no.
- Manual screen-reader audit in scope for v1?
- WCAG level target: AA (default) / AAA / none.

### CI Gate Design

- What must pass before a PR can merge?
  - Linting (always recommend yes).
  - Type checking (always recommend yes if typed language).
  - Unit tests (recommend yes).
  - Integration tests (recommend yes if backend in scope).
  - E2E tests (recommend subset — full suite too slow for every PR).
  - Visual regression (recommend main-branch only).
- Estimated CI run time target (fast feedback loop < 5 min is the goal).

### Test Data and Seed Strategy

- Who creates and maintains test fixtures?
- Shared seed database or per-test isolation?
- How to handle test data for payment flows (use Stripe test mode / mock).
- PII in test data: anonymized / synthetic / none.

---

## Scope Guard

Testing scope follows the v1 feature list from `00-requirements.md`. Tests
for v1.5 or v2 features are out of scope and must not be written until those
features are promoted.

---

## Output Format

See `output-templates.md` § 10-testing.md.
