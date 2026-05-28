# Analytics Module

Cross-cutting reference — consulted at Stage 1 Step 1.7 (module activation).
Analytics events must be defined before the coding agent builds screens,
because retrofitting tracking after the fact requires touching every
instrumented component and risks losing early production data.

## Activation Criteria

Activate the Analytics module when any of these apply:

- The user mentions conversion, funnel, retention, DAU, engagement, or
  any product metric.
- The product has a CTA, sign-up, purchase, or upgrade flow.
- The user mentions a specific analytics tool (GA4, PostHog, Mixpanel,
  Amplitude, Plausible, Fathom, Segment).
- The product has a marketing site with a primary CTA.
- The product needs to demonstrate value to stakeholders via data.

Skip when: prototype-only mode and the user has confirmed no analytics needed.

Output: `11-analytics.md`

---

## Question Tree

### Tool Selection

- Analytics tool: PostHog (recommended, open-source, product + web) /
  GA4 (free, web-focused) / Mixpanel / Amplitude / Plausible (privacy-first,
  no events) / Segment (multi-destination router) / custom.
- If Segment: which downstream destinations?
- Privacy / cookie consent required? (EU users → yes by default.)
- Self-hosted or cloud?

### Metric Goals

Before defining events, lock the 2-3 metrics that determine whether the
product is succeeding. These drive which events matter most.

Ask: "In 3 months, which numbers will you look at every week to know if the
product is working?"

Common examples:
- Activation rate (% users who complete the core action in first session).
- Retention (7-day, 30-day).
- Conversion (visitor → signup, trial → paid).
- Feature adoption (% users who used feature X in last 30 days).
- Task completion rate.

Lock 2-3 primary metrics before defining events. Events that do not feed
these metrics are deprioritized.

### Page View / Screen View Events

- Auto-tracked (most tools) or manual page_view calls?
- Identify authenticated users on page view? (user_id, plan, role.)
- UTM parameter capture on landing?

### Funnel Events

For each conversion funnel identified:

1. Name every step.
2. Name the event at each step.
3. Define properties on each event (what dimensions matter for analysis).

Example: Sign-up funnel
```
signup_started       { source: 'hero_cta' | 'pricing_cta' | 'nav' }
signup_email_entered { email_domain: string }
signup_completed     { plan: 'free' | 'pro', method: 'google' | 'email' }
```

### Core Feature Events

For each v1 feature in MVP scope, define the primary action event:

| Feature | Event name | Key properties |
|---------|-----------|----------------|
| [feature] | [event] | [prop list] |

Rule: one event per meaningful user action. Do not track everything; track
what feeds the locked metrics.

### Error and Dead-End Events

- Track failed form submissions with error type.
- Track empty states (user hits empty search, empty list).
- Track rage clicks or error pages if the tool supports it.

### Identity and User Properties

- Anonymous → identified: when does the user get a stable ID?
- User properties to set at signup (plan, role, org_id, etc.).
- Group analytics needed (org-level metrics in addition to user-level)?

### Event Naming Convention

Pick one and lock it:
- `snake_case_verb_noun` (e.g. `task_created`) — recommended.
- `Object Verbed` (e.g. `Task Created`) — Mixpanel convention.
- `category:action` (e.g. `task:create`).

All events in `11-analytics.md` must follow the chosen convention.
No mixing.

### Privacy and Consent

- Cookie banner / consent manager required? (OneTrust / Cookiebot / custom.)
- Analytics loaded only after consent? (Yes = slightly harder to implement.)
- PII in event properties? (Email, name, etc. must be hashed or excluded.)
- Data retention period in the analytics tool.

---

## Scope Guard

Only track events for v1 features. v1.5/v2 feature events are out of scope
and must not be added until those features are promoted.

---

## Output Format

See `output-templates.md` § 11-analytics.md.
