# Design QA

> How to check that a built screen matches its design. Copy the "Record" part into a new file for each check (for example `docs/design-qa/dashboard-2026-01-15.md`), or ask Claude with the "Design QA a screen" prompt. Lines starting with "Guide:" explain what to write.

## How to run a design QA

1. Pick the source of truth: a Figma frame, a mockup image, or the rules in `DESIGN.md`.
2. Capture the built screen at the same size (for example 1440 x 900 desktop and 390 x 844 mobile).
3. Compare full view first, then zoom into areas too small to judge.
4. Rate each difference: **P0** broken or unusable, **P1** wrong behavior or accessibility failure, **P2** visible mismatch, **P3** polish.
5. Fix P0 to P2, capture again, and record the result.

## Record

**Screen:** Guide: route or screen name.
**Date:** Guide: date of the check.
**Source of truth:** Guide: Figma link, image file or "DESIGN.md rules".
**Captured states:** Guide: sizes, role signed in, data shown, open menus.

### Findings

| ID | Priority | Area | Difference | Fix |
|---|---|---|---|---|
| DQA-1 | Guide: P0 to P3 | Guide: typography, spacing, color, assets, copy, interaction, accessibility | | |

Check every area:
- **Typography:** fonts, sizes, weights, truncation.
- **Spacing and layout:** alignment, gaps, widths, responsive behavior.
- **Color and tokens:** only tokens from `DESIGN.md`; contrast passes.
- **Assets:** real logo and icons; no emoji or hand-drawn substitutes.
- **Copy:** matches `docs/voice.md`; no "prototype", "mock" or "demo".
- **Interaction and accessibility:** keyboard order, focus ring, 44 px targets, labels, Escape closes dialogs, focus returns.

### Comparison history
1. Guide: first comparison result.
2. Guide: fixes applied, with file names.
3. Guide: result after fixes.

### Limits
Guide: what was not checked (for example screen reader, forced colors, real data).

### Checklist
- [ ] Every P0 to P2 finding fixed and recaptured.
- [ ] Mobile and desktop captured.
- [ ] Keyboard and focus checked.

**Final result:** Guide: passed or blocked.
