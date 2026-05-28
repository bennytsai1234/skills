# Architecture Reasoning

Cross-cutting reference — applies whenever a high-cost decision arises,
not only at specific steps. Common trigger points: Step 1.6
(architecture-changing constraints), Step 1.7 (module plan), Stage 2 tech
stack discussion, any "we can change this later" statement. The goal is to
derive the correct system abstraction from product behavior, not to pick
popular libraries too early.

The internal "Stage 1-8" headings below describe the reasoning workflow
within this analysis, not Project Genius's overall stages. Apply the
relevant sections whenever irreversible architecture decisions arise.

## Stage 1: Intent Interpretation

Understand what the user actually wants to build. Users often describe the
surface feature, not the system problem.

Ask internally:
- What experience are they trying to deliver?
- What would make the product feel right to the end user?
- What would make the first useful version obviously fail?

## Stage 2: Product Essence

Identify the one or two aspects where quality determines whether the product
has value.

Examples:

| Surface request | Product essence |
|---|---|
| Novel reader | Stable, continuous, fast reading across long content |
| Whiteboard | Object management in infinite space with zoom and selection |
| Chat app | Message synchronization, ordering, read state, offline resilience |
| AI workflow editor | Execution graph, task context, tool dispatch, recoverable runs |
| Note app | Block model, document structure, editing operations |
| Spreadsheet | Grid engine, formula evaluation, dependencies |
| Search system | Indexing, ranking, relevance scoring |
| Task management | Workflow state model and status transitions |

## Stage 3: Architecture-Changing Constraints

Ask only questions whose answers change technical decisions.

Good architecture-changing questions:
- Must data work offline and sync later?
- How large can the primary content or dataset become?
- Does the product require realtime collaboration?
- Does the user need undo/redo across complex operations?
- Are roles, permissions, audit logs, or compliance requirements present?
- Does the UI require infinite canvas, precise coordinates, media timelines, or
  high-frequency interactions?

Avoid low-value early questions:
- What color do you prefer?
- How many signups do you expect in month one?
- Which icon set should we use?

## Stage 4: Hidden Complexity Detection

Flag these red signals when they appear:

- very large data volumes
- 60fps or continuous interaction
- infinite or unbounded space
- realtime collaboration
- offline-first with sync
- precise positional accuracy
- complex undo / redo
- cross-device state synchronization
- WYSIWYG, canvas, diagram, timeline, or editor surfaces
- drag-and-drop ordering
- deeply nested structures
- plugin or extension systems
- workflow orchestration
- long-running tasks
- recoverable execution
- multi-step AI agent orchestration
- regulated, sensitive, financial, healthcare, or high-value data

When a red flag appears, explain the hidden complexity and why standard CRUD,
standard UI components, or default library behavior may fail.

## Stage 5: Solution Pattern Matching

Choose the domain abstraction before the library.

| Product area | Surface solution | Deeper abstraction |
|---|---|---|
| Novel reader | Scroll view | Virtual reading surface |
| Whiteboard | Canvas | Infinite object space |
| Note app | Rich text editor | Block/document engine |
| Chat | Message list | Realtime sync model |
| AI workflow | Prompt chain | Execution graph / state machine |
| Task manager | CRUD table | Workflow state model |
| Spreadsheet | HTML table | Grid/formula engine |
| Search | SQL LIKE | Indexing and ranking engine |
| Collaborative editing | API updates | CRDT / OT / conflict resolution |
| Video editor | Timeline UI | Media timeline engine |

## Stage 6: Failure Boundary Analysis

For each candidate approach, analyze where it starts to fail.

Use this shape:

```markdown
### Failure Boundary: [Simple Solution]

**Works well for:**
- [scenarios where it succeeds]

**Starts to strain at:**
- [trigger conditions]

**Patches needed:**
- [workaround 1]
- [workaround 2]

**End state of patching:**
[Does patching converge toward reimplementing the advanced solution?]

**Verdict:**
[Is this a viable path, or does it create architecture-level debt?]
```

## Stage 7: Decision Engine

Compare solutions across:

- short-term cost
- long-term cost
- rewrite risk
- product differentiation
- core experience quality
- maintainability
- testability

Classify decisions:

- Reversible: low-cost to change later, such as icon set or color palette.
- Semi-reversible: changeable but expensive, such as state management or API
  style.
- High-cost: foundation-level changes, such as rendering model, data model,
  sync protocol, permission model, workflow engine, or storage model.

Spend the most time on high-cost decisions.

## Stage 8: Minimum Viable Architecture

Do not confuse MVP with MVA.

- MVP = smallest feature set worth shipping.
- MVA = smallest foundation that supports the correct abstraction without a
  predictable rewrite.

Choose the right foundation, then cut scope above it. Do not choose a weak
foundation and plan to replace it later.
