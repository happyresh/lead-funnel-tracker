# Brand

**Status:** Draft

> Applies to projects with users who see or hear the product; otherwise mark it Not triggered in `docs/index.md`. How the product should feel and speak. `DESIGN.md` holds the exact values (colors, type, spacing, components). Lines starting with "Guide:" explain what to write; delete them once filled. When brand and design disagree, this file decides the feeling and `DESIGN.md` decides the value.

## 1. Brand Stance

- **Brand idea:** Guide: one short phrase that every screen should express (PATHWAYS used "make the pathway visible").
- **Brand promise:** Guide: one sentence about what users can always count on.
- **Experience character:** Guide: five to eight adjectives it must feel like (for example calm, clear, trustworthy, guided).
- **Must not feel:** Guide: adjectives it must avoid (for example noisy, intimidating, gamified, salesy).

### What the brand communicates
1. Guide: first message (for example "your data is handled carefully").
2. Guide: second message.
3. Guide: third message.

## 2. Surface Modes

Guide: describe each distinct area of the product and how it looks. Common modes:

| Mode | Purpose | Look |
|---|---|---|
| Workspace | Daily work by signed-in staff | Guide: for example dark navigation, white workspace, compact |
| Sign-in | Access and account flows | Guide: for example centered card, light background, one task per screen |
| Public | Pages anyone can see | Guide: for example larger headings, storytelling, aggregate data only |

## 3. Anti-references

Avoid:
- default purple SaaS gradients and glass-heavy dashboards;
- color as the only signal of status;
- actions that appear only on hover;
- tiny controls and dense terminal-like screens;
- animation without a purpose;
- fake data or stock photos presented as real;
- AI or chat styling for features that are plain rules;
- the words "prototype", "mock" or "demo" in user-facing text.

Guide: add anything specific to your field or competitors.

## 4. Design Principles

1. **One clear next action:** each screen makes the most important next step obvious.
2. **Recognition before recall:** show options and context; do not make users remember codes or steps.
3. **Progressive disclosure:** glance (status), scan (list), inspect (detail), in that order.
4. **Context over navigation:** show where the user is, what they are looking at, and what it connects to.
5. **Human control:** the system suggests; people decide. Risky actions need confirmation and can be undone where possible.
6. **Safety by design:** destructive or irreversible actions are deliberate (confirm, type to confirm, or two steps).
7. **Inclusive by design:** works by keyboard, with screen readers, at 200% zoom, on low-end phones and slow connections.

**Brand decision test:** when unsure, choose the option that makes the user's next safe action clearer.

## 5. Voice and Language

- Plain words, short sentences, active voice.
- Name things the way users name them (see `docs/context.md` section 7 Domain Glossary).
- Truthful empty, error and unavailable states; never hide a failure.
- Guide: preferred words and banned words for this project. Full writing rules are in `docs/voice.md`.

## 6. Logo and Imagery

- **Logo files:** Guide: where they live (for example `public/brand/`), minimum size, clear space.
- **Imagery:** Guide: what photos or illustrations are allowed, and consent rules for real people.
