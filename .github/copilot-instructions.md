## Git workflow

Whenever an agent changes files in this workspace, it should commit those changes and push the commit to the configured remote before ending the task. Keep commits scoped to the current task by staging only the files or hunks the agent changed, and report clearly if committing or pushing is blocked.

## Output location

When an agent is asked to **produce content** (decks, reports, articles, analyses, generated assets, scripts written for a specific deliverable, etc.), all produced files MUST be written under `output/<project-name>/`.

Rules:
- Pick a short, kebab-case `<project-name>` derived from the user's request (e.g. `sncb-ptu-business-case`, `q3-board-update`). If the user names the project, use that name.
- If the folder does not exist, create it. If it already exists from a prior session on the same project, reuse it and keep new artefacts in the same folder.
- Everything produced in that session — markdown, PPTX, PDF, notebooks, charts, supporting scripts, intermediate assets — goes inside that single project folder. Do not scatter outputs across `knowledge/`, the repo root, or sibling folders.
- `knowledge/` is **input-only**: reference material agents read from for style and structure. Never write generated artefacts into `knowledge/`.
- `.github/` (agents, skills, instructions) and source code the user explicitly asks to edit are **not** "produced content" and are edited in place as normal.

When unsure whether something counts as produced content, default to placing it under `output/<project-name>/`.