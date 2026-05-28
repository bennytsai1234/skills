# Convergence Protocol

This file defines the three core mechanisms that close the gap between
the user's mental image and the final product:

1. **Reference Pinning Protocol** — replace adjective descriptions with
   concrete reference products.
2. **Convergence Loop** — iterate proposals until the user explicitly
   agrees.
3. **Pilot-Per-Lock** — every locked decision generates a tangible
   artifact in HTML/CSS the user can see.

These are not optional. Every Stage 1 anchor question with visual /
interaction / voice content, and every Stage 2 step, MUST use these
mechanisms. Skipping them is the most common failure mode of weak models.

---

## 1. Reference Pinning Protocol

### The Forbidden Words List

For any decision about visual style, layout, interaction feel, copy
voice, or product personality, **the agent MUST NOT accept these words as
final answers**:

- "simple", "clean", "minimal", "minimalist"
- "modern", "fresh", "contemporary"
- "professional", "enterprise", "serious"
- "friendly", "warm", "approachable"
- "elegant", "sophisticated", "premium"
- "intuitive", "user-friendly", "easy to use"
- "beautiful", "nice", "good-looking"

These words mean different things to different people. "Minimalist" can
mean Linear, Notion, Stripe, Apple, Dieter Rams, Japanese MUJI, or
Brutalist. None of these look alike.

### What to do when the user uses a forbidden word

1. Acknowledge their direction.
2. Ask them to pin a reference: "Can you name a product that already
   feels the way you're describing?"
3. If they name one, ask which specific aspect (color / spacing / type /
   density / motion / copy / chrome).
4. If they cannot name one, **propose 3 candidate references** based on
   product type and the rest of Stage 1 context. Show 1-line
   characterizations. User picks one or says "closer to A but X".

### Reference Pin Format

When the user pins a reference, record it as:

```
Reference: Linear
What to learn from it:
  - Cold, dense information layout
  - Sidebar + canvas chrome
  - Cmd-K palette interaction pattern
What NOT to copy:
  - The exact icon set
  - The brand color (we want warmer)
  - The specific copy tone
```

This separates inspiration (allowed) from copying (not allowed).

### Reference Pinning is Required for

- Visual mood / vibe.
- Layout archetype.
- Per-component visual style.
- Interaction patterns (e.g. "the way Notion handles nested blocks").
- Copy voice ("the way Stripe writes error messages").
- Onboarding feel ("the way Linear's first-run experience flows").

### Reference Pinning is NOT required for

- Pure feature decisions (does the product have feature X yes/no).
- Data model decisions (these are about correctness, not feel).
- Tech stack decisions (these are about constraints, not feel).
- Pricing or business model.

---

## 2. Convergence Loop

For any high-stakes decision, use this loop:

```
1. Agent proposes 2-3 candidates.
   Each candidate must be:
     - Concrete (not abstract).
     - Differentiated from the others.
     - Brief (1-3 lines per candidate).
   When possible, attach a pilot artifact (see § 3).

2. User responds:
   - "A" → propose to lock A; go to step 5.
   - "B but X is wrong" → record the delta; go to step 3.
   - "None of these" → ask for direction, go to step 1.
   - Adjective-only feedback ("more polished", "less corporate") →
     refuse silently; ask for a reference pin per § 1.

3. Agent revises:
   - Apply the user's delta to the closest candidate.
   - Propose 1-2 new variants if useful.

4. Go back to step 2.

5. Lock with rationale:
   - Write the locked decision into the relevant lock file.
   - Quote the user's confirmation if possible ("matches my mental
     image", "yes, exactly this").
   - Note the rejected alternatives briefly so future stages
     understand context.
```

### Single-Round Acceptance Is Forbidden for High-Stakes Items

If the user accepts the very first proposal for a high-stakes decision
(vibe, layout archetype, navigation pattern, data model shape), the
agent MUST verify before locking:

```
"You accepted A immediately. Want me to also show alternatives B and C
before locking? Some decisions look obvious until you see the
alternatives."
```

If they confirm "yes, lock A", proceed. This is the only allowed
single-round path and only after explicit double-check.

### Low-Stakes Decisions Can Skip the Loop

For reversible / low-stakes decisions, a single proposal is fine:
- Icon set choice
- Specific shade within a confirmed color family
- Border radius value
- Microcopy phrasing for non-critical strings
- Stack provider when product shape is locked (which Postgres host)

If unsure whether a decision is high-stakes, default to running the
loop.

### The Lock File

Each stage maintains lock records:

- **Stage 1**: `00-requirements.md` § Confirmed decisions.
- **Stage 2 vibe / layout / archetype**: `01-design-system.md` § Locks.
- **Stage 2 per-screen**: `prototype/_locks.md`.
- **Stage 2 per-interaction**: `03-interactions.md` § Confirmed.
- **Stage 2 data model**: `04-data-model.md` § Confirmed entities and
  endpoints.
- **Stage 2 asset / voice**: `05-assets-and-content.md` § Voice lock,
  Asset source decisions.
- **Stage 2 stack**: `06-tech-stack.md`.

---

## 3. Pilot-Per-Lock

Every lock that affects what the product LOOKS or FEELS like generates a
tangible artifact the user can view before the lock is final.

### Artifact Format Priority

In order of preference:

1. **Working HTML/CSS file** in `prototype/` that the user opens in a
   browser. This is the only format that gives true visual fidelity.
2. **Inline HTML/CSS snippet** in chat (when chat-only or for very small
   demos).
3. **ASCII wireframe** (only acceptable for layout archetype
   visualization, never for vibe or visual style).
4. **Detailed prose description** (only acceptable when no other format
   is possible — e.g. describing animation timing).

### What Each Lock Produces

| Lock | Pilot artifact |
|------|----------------|
| Vibe | `prototype/_vibe-test.html` — one button + one card + one input with locked tokens |
| Layout archetype | `prototype/_archetype-test.html` — empty chrome (sidebar / topbar / etc.) with one fake screen |
| Per-screen | `prototype/<screen>.html` — full screen with locked vibe + archetype + locked content |
| Per-button (complex) | An inline JS demo showing click → loading → success/error sequence |
| Form validation | A form with the validation behavior wired (inline errors, async checks if relevant) |
| Empty / loading / error states | The relevant component rendered in each state on one demo page |
| Data entity lifecycle | A walkthrough page showing create / read / update / delete with sample data |
| Voice | 3 candidate sentences for the same message; user picks one |
| Asset feel | One screen with REAL assets and REAL copy (no Lorem Ipsum) |
| Stack choice | Justification document referencing locked constraints (no artifact required) |

### Pilot ≠ Production

Pilot artifacts are throwaway. They:
- Do not need to be accessible, performant, or cross-browser.
- May use inline styles, single-file HTML, no framework.
- Use placeholder data unless asset pinning has happened.
- Should be obviously labeled as prototype (e.g. yellow banner at top).

### When User Cannot Open HTML

If the user is in a chat-only context with no browser access:
- Use inline HTML/CSS snippets in the chat.
- Describe what the rendered output looks like in detail.
- Offer to paste the full HTML for the user to open elsewhere.

### Pilot Iteration

Pilots are part of the convergence loop, not separate from it. After
proposing candidates, the agent generates pilot artifacts for the top
1-2 candidates so the user can see-not-just-read.

---

## 4. The Stage 2 Iterative Prototype Loop (Special Case)

Stage 2 is the most intensive use of these mechanisms. The full
iteration:

### Phase A: First-pass prototype

After Stage 1 locks, the agent generates a rough first-pass prototype
covering all screens. This first pass:
- Uses the locked vibe tokens.
- Uses the locked layout archetype as chrome.
- Has placeholder data and stub interactions (clicks toast "stub").
- Is intentionally rough — the goal is to give the user something to
  react to, not to be polished.

The agent says: "Open `prototype/dashboard.html` in your browser. This
is the first rough pass. Tell me what's wrong, in any order."

### Phase B: Reactive feedback

The user opens the prototype and gives feedback. The feedback may be:
- Direct visual ("the sidebar is too wide").
- Functional ("there should be a search bar at the top").
- Conceptual ("this feels too dense, I want more breathing room").
- Pin-referenced ("more like Notion's left sidebar").

The agent's job is to:
- Ask one targeted question per ambiguous piece of feedback.
- Apply unambiguous feedback directly.
- Resist the urge to "fix everything in one pass" — small revisions per
  round produce better convergence.

### Phase C: Per-screen lock

When the user says "this screen matches my image" or equivalent, mark
the screen locked in `prototype/_locks.md` with:
- Timestamp.
- The user's confirmation quote.
- Any noted out-of-scope items still pending.

A screen is not locked until the user uses confirming language. Silent
acceptance ("looks fine", "I guess") is not a lock. Ask:

```
"Should I lock this screen? It will be treated as the spec for that
view from here on. If something needs to change later, we'll need to
explicitly revise."
```

### Phase D: Move on, return on conflicts

After locking a screen, move to the next unlocked one. If a later
decision invalidates a locked screen (e.g. data model change affects
what the dashboard shows), surface the conflict immediately:

```
"You just changed the permission model so non-admins can't see
the team list. This affects the dashboard you locked earlier. Want me
to revise the dashboard now?"
```

### Phase E: Stage 2 completion

Stage 2 completes when:
- `prototype/_locks.md` shows every screen locked.
- Interaction details for every locked screen are captured.
- Data model (if applicable) is locked.
- Voice and assets are locked.
- Tech stack is locked.

Only then does the agent extract documents from the locked prototype.

---

## 5. Anti-Patterns to Refuse

The agent MUST refuse these shortcuts:

| Anti-pattern | Why refused |
|--------------|-------------|
| Accept "minimalist" as a vibe answer | Word is ambiguous. Force reference pin. |
| Lock a screen because the user said "ok" | "Ok" is not "this matches my image". Confirm explicitly. |
| Produce all Stage 2 documents in one pass | Stage 2 docs come from the locked prototype, not from inference. |
| Treat one round of feedback as convergence | High-stakes locks need at least one back-and-forth. |
| Mark a value as "inferred" and move on | Inferred values must be read back to the user before locking. |
| Skip the pilot artifact "to save tokens" | Without the artifact, the user cannot calibrate against their mental image. |
| Build the prototype in framework-specific code without confirming the stack | If stack is unknown, use plain HTML/CSS. Framework choice happens late. |

When the agent notices itself drifting toward any of these, it must
stop and revert to the correct protocol.
