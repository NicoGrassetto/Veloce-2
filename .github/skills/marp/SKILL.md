---
name: marp
description: Use this skill whenever the user asks to create, build, draft, or export a slide deck, presentation, slides, or pitch using Markdown. Trigger for phrases like "create a deck", "make slides about X", "turn this report into a presentation", "build a pitch deck", "export slides to PDF/PPTX", "marp", "marpit", "slides from this markdown", or any request that produces a `.pptx`, `.pdf`, or HTML slide deck from Markdown content. Decks are authored in Marp Markdown and exported with the official `@marp-team/marp-cli` via `npx`. Source decks live under `knowledge/decks/`.
---

# Marp Deck Skill

Author slide decks in Marp Markdown and export them to PDF + PPTX (and optionally HTML/PNG) using the official Marp CLI.

## When to use

- "Create a deck about …" / "make slides on …"
- "Turn this report (e.g. `knowledge/reports/*.md`) into a presentation"
- "Export these slides to PDF and PowerPoint"
- Any request whose deliverable is a `.pdf` or `.pptx` slide deck built from Markdown

## Prerequisites (verify once per machine)

```bash
node --version                                  # must be >= 18
npx @marp-team/marp-cli@latest --version        # downloads/caches Marp CLI on first run
```

PDF and PPTX export require a Chromium-based browser (Chrome or Edge) or Firefox installed locally. If Marp can't auto-detect it, pass `--browser-path /path/to/browser`.

## Conventions

- **Source path:** `knowledge/decks/<slug>-<YYYY-MM-DD>.md` (slug is kebab-case, date is the deck's creation date).
- **Outputs:** write `.pdf` and `.pptx` next to the source in `knowledge/decks/`.
- **Images / assets:** reference from `knowledge/assets/` with relative paths; exports must then include `--allow-local-files`.
- **Source reuse:** if a matching report exists under `knowledge/reports/`, use it as the content source rather than inventing material.

## Quickstart skeleton

Every deck starts with YAML frontmatter and uses `---` to split slides.

```markdown
---
marp: true
theme: default        # default | gaia | uncover (or path to custom CSS)
paginate: true
size: 16:9
title: <Deck title>
author: <Author>
---

# <Title slide>

<Subtitle / one-line takeaway>

---

<!-- _class: lead -->

# Section header

---

## Slide title

- Bullet one
- Bullet two
- Bullet three

<!-- Presenter note: speak to the "why" here. -->
```

## Authoring guidance

### Choosing a theme

| Theme | Use when |
|---|---|
| `default` | Clean, neutral, business/technical decks. Safe default. |
| `gaia` | Warm, branded, marketing-leaning decks; good for keynotes. |
| `uncover` | Minimal, centered, big-typography decks; good for short pitches. |

Override per deck via the `theme:` frontmatter key, or per export with `--theme <name|path>`.

### Directives cheat sheet

- **Global (frontmatter):** `theme`, `paginate`, `size` (e.g. `16:9`, `4:3`, `widescreen`), `header`, `footer`, `style` (inline CSS overrides), `backgroundColor`, `color`.
- **Local (HTML comment, applies from here onward):** `<!-- backgroundColor: #111 -->`, `<!-- color: white -->`, `<!-- class: invert -->`.
- **Spot (single slide, underscore prefix):** `<!-- _class: lead -->`, `<!-- _backgroundColor: aqua -->`, `<!-- _paginate: false -->` (commonly used to hide pagination on the title slide).
- **Presenter notes:** plain HTML comments that are *not* directives are treated as speaker notes and survive into PPTX.

### Slide patterns

**Title slide (no pagination):**
```markdown
<!-- _paginate: false -->
<!-- _class: lead -->

# Deck title

Subtitle or hook
```

**Background image (full bleed):**
```markdown
![bg](../assets/cover.jpg)

# Title over image
```

**Side-by-side image:**
```markdown
![bg right:40%](../assets/diagram.png)

# Heading

- Point one
- Point two
```

**Two-column layout (via inline style):**
```markdown
<style scoped>
section { columns: 2; }
</style>

# Two columns

- left col bullet
- left col bullet
- right col bullet
- right col bullet
```

**Quote / lead slide:**
```markdown
<!-- _class: lead -->

> "One sharp quote per deck goes a long way."
> — Source
```

### Content rubric (apply before writing)

1. **Audience** — one sentence on who's in the room.
2. **Key takeaway** — one sentence the audience should remember.
3. **Length** — aim for 5–12 slides. Title + agenda + 3–8 body + closing.
4. **One idea per slide.** Prefer 3–5 bullets over paragraphs.
5. **Section dividers** between logical chunks (use `_class: lead`).
6. **Closing slide** with the call to action or next step.

## Export workflow

### Default: PDF + PPTX next to the source

`-o` accepts only one output path, so call the CLI twice — once per format.

```bash
DECK=knowledge/decks/my-deck-2026-05-27.md

npx @marp-team/marp-cli@latest "$DECK" --pdf  --allow-local-files
npx @marp-team/marp-cli@latest "$DECK" --pptx --allow-local-files
```

Outputs land at `knowledge/decks/my-deck-2026-05-27.pdf` and `…pptx`.

### Other useful invocations

```bash
# HTML preview (no browser needed)
npx @marp-team/marp-cli@latest "$DECK"

# Live preview window + watch
npx @marp-team/marp-cli@latest "$DECK" -p -w

# Title-slide PNG (e.g. for an OG image)
npx @marp-team/marp-cli@latest "$DECK" --image png --allow-local-files

# Override theme without editing frontmatter
npx @marp-team/marp-cli@latest "$DECK" --theme gaia --pdf

# Editable PPTX (experimental; requires LibreOffice; avoid with `gaia`)
npx @marp-team/marp-cli@latest "$DECK" --pptx --pptx-editable --allow-local-files
```

## Troubleshooting

- **"Local file access is blocked"** in the exported PDF/PPTX → add `--allow-local-files`. Only do this with Markdown you trust.
- **"No browser found"** → install Chrome/Edge, or pass `--browser-path /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome`.
- **Editable PPTX renders broken** → drop `--pptx-editable` (the regular `--pptx` is image-based but reliable). The `gaia` theme is known to break editable export.
- **Frontmatter ignored** → make sure the very first line of the file is `---` and `marp: true` is present.
- **Slide doesn't split** → ensure there's a blank line before the `---` divider (CommonMark requirement).

## Minimal complete example

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
title: Logic Apps vs BizTalk — 2026 Snapshot
author: Veloce
---

<!-- _paginate: false -->
<!-- _class: lead -->

# Logic Apps vs BizTalk

A 2026 integration platform snapshot

---

## Agenda

1. Where BizTalk stands today
2. Logic Apps Standard, in one slide
3. Cost & operations
4. Migration triggers
5. Recommendation

---

<!-- _class: lead -->

# 1. Where BizTalk stands today

---

## BizTalk in 2026

- Mainstream support ended; extended support window closing
- On-prem only, Windows + SQL Server footprint
- Strong EDI / legacy adapter ecosystem
- High operational cost per integration

<!-- Frame this as "still works, but the runway is short." -->

---

<!-- _class: lead -->

# Recommendation

Start net-new on Logic Apps Standard.
Migrate BizTalk workloads opportunistically, EDI last.
```

Export it:

```bash
npx @marp-team/marp-cli@latest knowledge/decks/logic-apps-vs-biztalk-2026-05-27.md --pdf  --allow-local-files
npx @marp-team/marp-cli@latest knowledge/decks/logic-apps-vs-biztalk-2026-05-27.md --pptx --allow-local-files
```
