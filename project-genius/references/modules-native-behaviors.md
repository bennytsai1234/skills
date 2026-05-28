# Native Behaviors Module

Applies to **Mobile app** and **Desktop app** product types.

The HTML prototype produced in Stage 2 captures visual layout and rough
information architecture, but it cannot represent:
- Touch gestures and gesture conflicts.
- Haptic feedback timing and intensity.
- Platform-specific navigation transitions (push / modal / sheet / dismiss).
- Native component behavior (action sheet vs bottom sheet vs dialog).
- OS-level integration (share sheet, biometrics, file picker, notifications).
- Keyboard avoidance and input management on mobile.
- Menu bar, tray, dock, and window management on desktop.

This module fills that gap with a dedicated `03b-native-behaviors.md` that
the downstream coding agent consults alongside the visual prototype.

## Activation Criteria

Always activate for Mobile app and Desktop app product types. Skip for all
other types.

Output: `03b-native-behaviors.md`

---

## Mobile Question Tree

Run this tree during Stage 2 alongside per-screen iteration (Step 2.4 and
2.5). Capture behaviors per screen or per interaction pattern, not globally.

### Navigation Transitions

For each navigation event, define the transition:

| From | To | Transition | Dismiss gesture |
|------|----|------------|----------------|
| [screen] | [screen] | push / modal full / sheet / fade | back / swipe-down / swipe-right |

- Push (drill-down): adds a screen to the stack; back arrow dismisses.
- Modal full: covers the entire screen; swipe-down dismisses.
- Sheet (partial): slides up partially; swipe-down or tap-outside dismisses.
- Fade/replace: no back; used for auth → app root swap.

### Gesture Map

For each screen, list every non-tap gesture and its action:

| Screen | Gesture | Action | Conflict? |
|--------|---------|--------|-----------|
| [screen] | swipe left on row | reveal delete | no |
| [screen] | pull down | refresh | no |
| [screen] | long press | context menu | no |
| [screen] | pinch | zoom content | no |

Conflict: does this gesture conflict with the system scroll gesture or the
navigation swipe-back gesture? If yes, how is priority resolved?

### Haptic Feedback

For each action that should produce haptic feedback:

| Action | Haptic type | Platform |
|--------|-------------|----------|
| Button tap (primary action) | impact.medium | iOS |
| Destructive action confirm | notification.warning | iOS |
| Task completion | notification.success | iOS |
| Error | notification.error | iOS |
| [action] | [type] | Android (VibrationEffect) |

iOS types: impact.light / .medium / .heavy, selection, notification.success /
.warning / .error.

Android: HapticFeedbackConstants or VibrationEffect — specify which.

### Native Components vs Custom

For each UI pattern, decide: native OS component or custom implementation?

| Pattern | Decision | Reason |
|---------|----------|--------|
| Bottom sheet | Native (UISheetPresentationController / ModalBottomSheet) | Gesture handling is correct out of the box |
| Alert | Native (UIAlertController / AlertDialog) | — |
| Action sheet | Native | — |
| Date picker | Custom | Native date picker conflicts with design system |
| Tab bar | Native (UITabBar / BottomNavigationBar) | — |
| Context menu | Native (UIContextMenuInteraction / PopupMenu) | — |

Default rule: use native components unless the design system requires custom
behavior that cannot be achieved via styling alone.

### Keyboard Behavior

- Keyboard avoidance strategy: scroll the form view up / use
  KeyboardAwareScrollView / fixed inputs above the keyboard.
- Which inputs trigger the numeric keyboard, email keyboard, URL keyboard,
  search keyboard?
- Dismiss keyboard on: tap outside / swipe down / explicit done button.
- Return key behavior per field (next field / submit / none).

### Offline and Background State

- Minimum offline capability: none / read-only cache / full offline writes.
- Background app refresh: needed for notifications, sync, or content updates?
- App state transitions: what happens on backgrounded → foregrounded?
  (Refresh data / resume last state / restart.)
- Biometric auth on foreground: re-authenticate after backgrounded for > N
  minutes?

### Push Notifications

- Types of notifications in v1 (list each).
- Tap action per notification type (open app to specific screen).
- Rich notification (image, action buttons) or plain text?
- Opt-in prompt timing: on first launch / after user completes core action /
  never in v1.

### Platform-Specific OS Integration

For each OS feature used, document the behavior:

| Feature | iOS implementation | Android implementation |
|---------|--------------------|------------------------|
| Share | UIActivityViewController | ShareCompat |
| File picker | UIDocumentPickerViewController | Intent.ACTION_OPEN_DOCUMENT |
| Camera | PHPickerViewController | ActivityResultContracts.TakePicture |
| Biometrics | LocalAuthentication | BiometricPrompt |
| Deep link | Universal Links + URL scheme | App Links + intent-filter |

---

## Desktop Question Tree

Run this tree during Stage 2 alongside per-screen iteration.

### Window Management

- Single window only, or multi-window support?
- Minimum window size (width × height).
- Resizable? Maximizable? Full-screen mode?
- Saved window position/size on relaunch: yes / no.
- If multi-window: does each window have independent state, or do they share?

### Menu Bar (macOS) / System Menu (Windows)

For each native menu item in the app, document:

| Menu > Item | Keyboard shortcut | Action | Enabled condition |
|-------------|-------------------|--------|-------------------|
| File > New | ⌘N / Ctrl+N | [action] | always |
| File > Open | ⌘O / Ctrl+O | [action] | always |
| File > Save | ⌘S / Ctrl+S | [action] | document is dirty |
| Edit > Undo | ⌘Z / Ctrl+Z | [action] | undo stack non-empty |

### Global Keyboard Shortcuts

Shortcuts registered system-wide (active even when window is not focused):

| Shortcut | Action | Conflict risk |
|----------|--------|---------------|
| ⌥Space (macOS) | Show/hide window | Low |
| Ctrl+Shift+X (Win) | [action] | Low |

### Tray / Menu Bar Icon (if applicable)

- Tray icon variants: idle / active / alert / loading.
- Click behavior: show window / show menu / toggle.
- Right-click menu items (list each with action).
- Tray icon tooltip text.

### File Associations

- Does the app own a file type? (e.g. `.myapp`, `.canvas`)
- Open-with behavior: open the app to the file's view.
- Drag-and-drop into the app window: which file types accepted, what happens.

### Auto-Updater

- Framework: Squirrel (Electron) / Sparkle (macOS) / NSIS (Windows) / other.
- Update check: on launch / on schedule / manual only.
- Update notification UX: silent install on next relaunch / in-app prompt /
  mandatory restart dialog.

### OS Notifications

- Notification types used in v1 (list each with trigger).
- Click action per notification (bring window to front / open specific view).
- Notification persistence (stays until dismissed / auto-clears after N sec).

---

## Output Format

See `output-templates.md` § 03b-native-behaviors.md.

## Relationship to Other Documents

- `03-interactions.md` captures per-button state maps and form validation.
  `03b-native-behaviors.md` captures platform-specific gesture and OS
  integration behavior that `03-interactions.md` cannot represent.
- `02-surface-map.md` captures what screens exist and how they connect.
  `03b-native-behaviors.md` captures how the transitions feel and behave
  on the platform.
- If the prototype HTML shows a "swipe to delete" row, `03b` documents the
  gesture threshold, the confirmation behavior, and the haptic feedback.
  The prototype shows the visual; `03b` shows the behavior.
