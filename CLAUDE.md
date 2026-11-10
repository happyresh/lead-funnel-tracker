# Guidance for Claude Code in this repo

## Always loaded
The two lines below load the agent instructions and the project context into every session, so work never starts cold.

@AGENTS.md
@docs/context.md

## General Principles
- Generate concise, short solutions for new modules or code.
- Review existing files before any change or refactor.
- Match the naming and style of the surrounding code.
- Watch for over-engineering, oversized files and obvious bugs.
- Comments: one sentence, no emojis or special characters.
- Markdown files use kebab-case names (ex. some-description.md).
- Write documents in the style of `docs/voice.md`.

## Code Quality
- Pick the right data structure and algorithm for the problem.
- Expose only the data a caller needs (least privilege).
- No new external libraries unless necessary; justify any you add.
- Take versions from the dependency file (package.json, pyproject.toml, go.mod), never from memory.

## Version Control
- Commit after significant changes; keep commits small and focused.
- Never commit to the production branch directly.

## Never
- Commit passwords, API keys, tokens or connection strings.
- Use real customer personal data in code, tests or demos.
- Weaken security or delete tests to make something pass.
