# Type-Specific Question Trees

Different product types require different questions in Stage 1 anchor
capture, Stage 2 surface mapping, Stage 2 interaction spec, and Stage 2
asset pinning. This file lists the type-specific questions and the
first-pass prototype skeleton for each recognized type.

When a product is mixed (e.g. SaaS with a marketing site), combine the
relevant trees but separate them by surface (the app surface uses the SaaS
tree, the marketing surface uses the marketing tree).

---

## Web app / SaaS dashboard

### Anchor questions (additional to standard)
- Single-user app or team / multi-tenant?
- What's the primary user job-to-be-done in one session? (e.g. "respond to
  customer tickets", "build a workflow", "review analytics")
- Authenticated only or has public surface too?

### Surface map questions
- What screens exist? List every named view.
- What's the default landing screen after login?
- What's the global navigation (sidebar / topbar / both)?
- Is there a settings area? An admin area?
- Is there a search? Where does it live?
- Are there modals / slide-overs / drawers? When does each appear?

### Interaction questions
- Keyboard shortcuts (cmd-K palette, j/k navigation, esc-close)?
- Bulk selection and bulk actions on lists?
- Inline edit vs modal edit pattern?
- Optimistic updates vs always-confirm?
- Empty state copy and call-to-action?
- Notification surface (toast / inbox / both)?
- Real-time updates (websocket? polling? manual refresh?)

### Data questions
- Per-tenant data isolation?
- Audit log requirements?
- Soft delete vs hard delete?
- Export formats (CSV, JSON, PDF)?
- Search infrastructure (DB-side, dedicated search engine)?

### Asset questions
- Brand logo and favicon?
- Empty state illustrations?
- Loading skeletons custom or generic?
- Icon set (Lucide, Heroicons, custom)?

### Prototype skeleton
```
prototype/
├── index.html              # redirects to login or dashboard
├── login.html
├── dashboard.html          # main landing
├── [primary-resource].html # e.g. tickets.html, projects.html
├── [resource]-detail.html
├── settings.html
├── _vibe-test.html
├── _locks.md
└── assets/
    ├── tokens.css          # locked vibe tokens
    └── chrome.css          # locked layout archetype
```

---

## Mobile app

### Anchor questions
- iOS / Android / both? Native or hybrid (React Native, Flutter,
  Capacitor)?
- Online-required or offline-capable?
- Push notifications central or peripheral?
- Native OS integrations (camera, location, contacts, calendar,
  biometrics)?

### Surface map questions
- Tab bar / drawer / stack-only navigation?
- How many tabs?
- Onboarding flow on first launch?
- Login required at launch or browse-then-sign-up?
- Modal sheets vs full-screen modals?

### Interaction questions
- Gestures (swipe to delete, pull to refresh, long press, swipe between
  tabs)?
- Haptic feedback?
- Keyboard behavior (avoid covering inputs, dismiss on scroll)?
- Loading patterns (skeleton, spinner, optimistic)?
- Pull to refresh per list?
- Infinite scroll vs pagination?
- Native components (action sheet vs custom bottom sheet)?
- Deep linking and URL scheme?

### Data questions
- Local cache strategy (SQLite, Realm, MMKV)?
- Sync conflict resolution?
- Offline writes queued?

### Asset questions
- App icon (1024x1024 master + per-size).
- Splash screen.
- Push notification icon.
- Store screenshots (per device size, per locale).
- In-app illustrations (light/dark variants).

### Native Behavior Questions (Mobile)

The HTML prototype captures layout. `03b-native-behaviors.md` captures the
behaviors the prototype cannot show. Ask these during Step 2.5b.

**Navigation transitions** — for every screen-to-screen move, confirm:
push / modal full / sheet / fade. Swipe-back available on push transitions?

**Gesture inventory** — per screen:
- Swipe left/right on a row?
- Pull-to-refresh?
- Long press?
- Pinch to zoom?
- Swipe between tabs?
- Any gesture conflict with system scroll or navigation swipe?

**Haptic feedback** — for each:
- Primary action button tap: impact level (light / medium / heavy)?
- Destructive confirmation: notification.warning?
- Task / form success: notification.success?
- Error: notification.error?
- Toggle on/off: selection?

**Native vs custom component** — decide for each:
- Bottom sheet: native sheet or custom drawer?
- Alerts and confirmations: native UIAlertController / AlertDialog or
  custom modal?
- Action sheets: native or custom?
- Date/time pickers: native or custom (often custom to match design)?
- Context menus: native long-press menu or custom popup?

**Keyboard behavior** — per form:
- Avoidance: scroll form view up / KeyboardAwareScrollView / fixed layout?
- Return key per field: next field / submit / done / search?
- Dismiss keyboard: tap outside / swipe down / explicit done button?
- Any numeric-only, email, URL, or search keyboard types needed?

**OS integrations** — for each v1 feature that touches the OS:
- Camera / photo library: PHPickerViewController / CameraX?
- Share: UIActivityViewController / ShareCompat?
- Files: document picker?
- Location: always / when in use / never?
- Biometrics: Face ID / fingerprint — which flows use it?
- Deep links: URL scheme + Universal Links / App Links?

### Prototype skeleton
Use HTML with mobile viewport meta, frame each "screen" at 390x844 (iPhone
14) in a side-by-side grid for review.
```
prototype/
├── index.html              # screen index, side-by-side mobile frames
├── onboarding-01.html
├── onboarding-02.html
├── home-tab.html
├── search-tab.html
├── profile-tab.html
├── modal-sheet-example.html
├── _vibe-test.html
└── _locks.md
```

Additional output: `03b-native-behaviors.md` — gesture map, haptics,
native component decisions, OS integrations. See `modules-native-behaviors.md`.

---

## Marketing site / Landing page

### Anchor questions
- Single page or multi-page?
- Primary CTA target (signup / book demo / download / buy)?
- Persuasion arc (problem-solution / before-after / social-proof-led /
  feature-led)?
- Voice (corporate / friendly / technical / playful)?

### Surface map questions
- Section order: hero / social proof / problem / solution / features /
  pricing / testimonials / FAQ / CTA?
- Sticky nav or static?
- Footer content (links, contact, legal)?
- Cookie banner / GDPR consent?

### Interaction questions
- Scroll animations (fade-in, parallax, scroll-triggered videos)?
- Anchor link scroll behavior (smooth, instant)?
- Form behavior (modal, inline, redirect to dedicated page)?
- Mobile menu (drawer, full-screen)?
- Live chat widget?

### Data questions (usually minimal)
- Form submission destination (email, CRM, webhook, API)?
- Newsletter subscription target?
- Analytics tooling (GA4, Plausible, PostHog)?

### Asset questions (critical for marketing)
- Hero visual (photo / illustration / product screenshot / video / 3D
  render)?
- Social proof logos (real partners or placeholder)?
- Testimonial photos (real people or stock)?
- Feature illustrations style (matched set required)?
- OG image for social sharing?

### Prototype skeleton
```
prototype/
├── index.html              # the full landing page, all sections
├── pricing.html            # if multi-page
├── about.html
├── thank-you.html          # form submission landing
├── _vibe-test.html
└── _locks.md
```
Section-level lock (not screen-level) — each section locked
independently.

---

## Content site / Blog / Documentation

### Anchor questions
- Content frequency (daily, weekly, monthly, one-time)?
- Author count (single voice vs multiple authors)?
- Categories / tags / both / neither?
- Comment system needed?
- Newsletter integration?
- Translations / multi-locale?

### Surface map questions
- List templates (latest, by category, by tag, by author)?
- Detail template variations (long-form, short, with TOC, with code)?
- Sidebar content (related posts, ads, author bio, TOC)?
- Search (full-text DB / Algolia / Pagefind / none)?
- RSS / Atom feed?
- OG / Twitter card per post?

### Interaction questions
- Reading time estimate?
- Progress bar?
- Sticky TOC?
- Code copy button?
- Share buttons (which platforms)?
- Subscribe CTA placement?

### Data questions
- CMS (headless: Sanity / Strapi / Contentful; flat-file: Markdown in
  repo; WordPress)?
- Image hosting / processing?
- Content schema (frontmatter fields)?

### Asset questions
- Cover image per post (required, optional, sometimes)?
- Author avatars?
- OG image generation (manual or automated template)?

### Prototype skeleton
```
prototype/
├── index.html              # homepage / latest posts
├── post.html               # single post template
├── category.html
├── author.html
├── search.html
├── _vibe-test.html
└── _locks.md
```

---

## API service / Backend

### Anchor questions
- Public API or internal-only?
- API style (REST / GraphQL / RPC / gRPC / event-driven)?
- Versioning strategy?
- Customer types (developers, machines, internal services)?
- SLA expectations?

### Surface map questions (= endpoint map)
- List every endpoint / operation.
- Group by resource or capability.
- Auth model (API key / OAuth / JWT / mTLS / signed requests)?
- Rate limiting per key / per IP / per route?
- Webhook events to deliver?
- Idempotency key support?

### Interaction questions (= protocol details)
- Request format (JSON / form / multipart)?
- Response envelope (raw / wrapped with status)?
- Error format (problem+json / custom)?
- Pagination style (cursor / offset / page)?
- Retry / backoff guidance for clients?
- Webhook signature scheme?

### Data questions
- Data model with entity relationships.
- Per-endpoint request and response schemas.
- Validation rules.
- Filtering / sorting / search params.

### Asset questions (often N/A, but)
- API docs assets (architecture diagrams, sequence diagrams).
- SDK code samples per language.
- Postman / Insomnia / OpenAPI collection.

### Prototype skeleton
```
prototype/
├── index.html              # API overview, like Stripe docs landing
├── api-reference.html      # endpoint index
├── endpoint-detail.html    # one fully-spec'd endpoint as template
├── authentication.html
├── errors.html
├── webhooks.html           # if applicable
├── _vibe-test.html
└── _locks.md
```

Plus OpenAPI YAML draft in `prototype/openapi.yaml`.

---

## Browser extension

### Anchor questions
- Chrome only / Firefox only / cross-browser?
- Manifest V2 or V3?
- Active on all sites / specific sites / user-toggle?
- Requires login to a backend?
- Free or paid?

### Surface map questions
- Popup (clicked from toolbar)?
- Sidebar / side panel?
- Options page?
- Content script overlays (injected into host pages)?
- Devtools panel?
- New tab page replacement?
- Context menu items?

### Interaction questions
- Toolbar icon states (active / inactive / count badge / loading)?
- Popup size and behavior on click outside?
- Content script injection timing (document_start / idle / load)?
- Cross-origin requests (declared permissions)?
- Storage (chrome.storage.local / sync / IndexedDB)?
- Communication between scripts (message passing pattern)?
- Update notification UX?

### Data questions
- What's stored locally vs synced via account?
- Sensitive data handling?
- Permissions audit (request only what's needed)?

### Asset questions
- 16x16, 48x48, 128x128 icons.
- Toolbar icon variants (light / dark).
- Store screenshots (1280x800).
- Promo tile.
- Demo GIF/video.

### Prototype skeleton
```
prototype/
├── index.html              # extension overview
├── popup.html              # actual popup HTML
├── sidebar.html
├── options.html
├── content-script-demo.html # mock of injected UI on a fake host page
├── _vibe-test.html
└── _locks.md
```

---

## Desktop app

### Anchor questions
- macOS / Windows / Linux / cross-platform?
- Framework (Electron / Tauri / native Swift / native C# / Qt)?
- Online-required or offline-capable?
- Multi-window or single-window?
- File-format ownership (does the app own a file type)?

### Surface map questions
- Main window layout (sidebar / tabs / panels)?
- Tray / menu bar presence?
- System menu items?
- Settings / preferences window?
- About window?
- Onboarding window on first launch?

### Interaction questions
- Global shortcuts (registered system-wide)?
- File drop targets?
- Drag between windows / apps?
- Native menus (File / Edit / View / Help)?
- Notification surface (native vs in-app)?
- Auto-updater UX?

### Data questions
- Local storage location (per platform conventions)?
- Cloud sync (optional / required)?
- Conflict resolution?

### Asset questions
- App icon (per platform sizes).
- Tray icon (active / idle / alert variants).
- Splash / launch.
- Installer assets.

### Native Behavior Questions (Desktop)

The HTML prototype captures layout. `03b-native-behaviors.md` captures OS
integration behaviors that the prototype cannot represent. Ask during Step 2.5b.

**Window management**:
- Single window or multi-window? If multi: do windows share state?
- Minimum window size (width × height)?
- Resizable, maximizable, full-screen mode?
- Save window position and size between launches?

**Native menu structure** — list every item the user expects:
- File menu items and keyboard shortcuts (New, Open, Save, Export, Close)?
- Edit menu (Undo/Redo, Cut/Copy/Paste, Find)?
- View menu items?
- App-specific menus?
  For each item: shortcut, action, enabled condition.

**Global keyboard shortcuts** (active system-wide):
- Show/hide window shortcut?
- Any other global shortcuts?
  Flag conflicts with common OS shortcuts (⌘Space, ⌘Tab, etc.).

**Tray / menu bar icon** (if applicable):
- Icon variants: idle / active / alert / loading?
- Click behavior: show window / toggle / show menu?
- Right-click menu items (list each with action)?
- Tooltip text?

**File associations** (if applicable):
- Does the app own a file type (extension)?
- Open-with behavior?
- Drag-and-drop into the window: which types, what action?

**Auto-updater**:
- Framework (Squirrel / Sparkle / NSIS / other)?
- Update check timing: launch / schedule / manual?
- Notification UX: silent / in-app prompt / mandatory restart dialog?

**OS notifications**:
- Notification types in v1 (list each with trigger)?
- Click action per notification?
- Auto-clear after N seconds or persist until dismissed?

### Prototype skeleton
```
prototype/
├── index.html              # window mockup
├── main-window.html
├── settings.html
├── tray-menu-demo.html
├── _vibe-test.html
└── _locks.md
```

Additional output: `03b-native-behaviors.md` — window management, menu
structure with shortcuts, tray states, file associations, auto-updater UX.
See `modules-native-behaviors.md`.

---

## Mixed products

When the user combines types:

1. Split surfaces. E.g. SaaS + marketing = two surface sets, two
   prototypes (`prototype/app/` and `prototype/marketing/`).
2. Decide shared design system or two separate ones.
3. Lock each surface independently.
4. Handoff package mentions which downstream phase implements which
   surface first.

---

## Type-Agnostic Topics

Some questions apply regardless of type and are covered in
`core-workflow.md` directly:
- vibe and tokens
- accessibility baseline
- internationalization
- analytics events
- error tracking
- legal pages (privacy, terms)

These are not repeated per type but should be raised when relevant.
