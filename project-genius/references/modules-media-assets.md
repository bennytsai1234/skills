# Media and Asset Planning

Deep reference used during Stage 2 Step 2.7 (asset and content pinning).
The new flow produces `05-assets-and-content.md` from these rules after
the user has confirmed voice, asset sources, and reviewed a prototype
screen filled with REAL assets and REAL copy.

Media planning is part of implementation safety. The coding agent must know
which assets are real, which are placeholders, which may be generated, and
which are blocked until the user provides files or licensing approval.

## Asset categories

Classify every asset as one of:
- content asset: essential information, such as product image or case study image.
- decorative asset: visual atmosphere, such as background image.
- functional asset: avatar, qr code, uploaded file, chart image.
- brand asset: logo, favicon, og image, app icon.
- explanatory asset: diagram, screenshot, demo video, tutorial image.

## Image rules

For each important image define:
- page or section.
- purpose.
- source.
- required or optional.
- recommended size and aspect ratio.
- crop behavior.
- focal point.
- desktop/tablet/mobile behavior.
- alt text rule.
- loading strategy.
- fallback.

## Video rules

For each video define:
- purpose.
- source.
- background, hero, content, embedded, or uploaded video.
- duration guidance.
- autoplay/muted/loop/controls.
- poster image.
- captions or transcript.
- mobile fallback.
- max file size or hosting strategy.
- performance behavior.

## Background media rules

Background images and videos must not carry essential information unless there is a non-media text alternative. Always define overlay or scrim rules when text appears above media.

For background video, default to:
- muted.
- loop only if decorative.
- no sound autoplay.
- poster fallback.
- static image fallback on mobile if performance risk exists.

## Licensing rules

Do not assume external assets are licensed for use. Mark each asset source as:
- user owns.
- open license confirmed.
- paid license needed.
- placeholder only.
- needs user confirmation.

## Generated asset rules

AI-generated drafts are allowed only when the user approves generated assets or
when the blueprint explicitly marks the asset as `AI-generated draft allowed`.
Generated assets must not be described as final brand assets unless confirmed.

## Missing asset protocol

If no real file or URL exists, the coding agent must not invent fake paths. It may only:
- use an obvious placeholder.
- create a labeled placeholder component.
- ask the user for the asset.
- use a user-approved generated draft.
