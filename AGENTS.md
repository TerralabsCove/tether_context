# Instructions for AI agents working in tether_context

This repo is the team's source of truth for the Tether robot project. Read [README.md](README.md) for the human rules. These rules are stricter.

## Before you answer anything about the project

Read [INDEX.md](INDEX.md), then the relevant files in `truth/`. Treat `truth/` as authoritative. Treat `notes/` as unverified. Treat `meetings/` as a record of what was said on that date, which may have been superseded since. Check [truth/decisions.md](truth/decisions.md) for the latest status.

## Where you may write

| Location | When |
|---|---|
| `notes/` | Default for anything you produce: research, summaries, drafts, analysis. Name it `notes/YYYY-MM-DD-<person>-<topic>.md`, where `<person>` is the human you're working for. |
| `meetings/` | Only when asked to file a meeting note. Use [meetings/_template.md](meetings/_template.md). Keep the original summary text. Do not rewrite or "improve" it. |
| `truth/` | Only when a person explicitly asks you to update it. Make the smallest change, and update `last_reviewed`. |
| `plans/` | Only when asked by the plan's owner. |
| `INDEX.md` | Add one line whenever you add a file outside `notes/`. |

Never create new top-level folders. Never delete files. Move superseded files to `archive/` instead.

## When filing a meeting note

1. Save it as `meetings/YYYY-MM-DD-topic.md` with the template header. If the date is unknown, use the best date you have and mark it `UNCONFIRMED` in the header.
2. For each decision, append a new row to [truth/decisions.md](truth/decisions.md) with the next ID. Never edit an existing row's decision text. If a new decision replaces an old one, set the old row's status to `superseded by D-XXX`.
3. Update [truth/robot.md](truth/robot.md), [truth/team.md](truth/team.md), or [truth/project.md](truth/project.md) if the decision changes them.
4. Remove answered items from [truth/open-questions.md](truth/open-questions.md). Add new unresolved items. **If the new note contradicts something in `truth/`, do not pick a winner. Add it to open questions under "Conflicts between sources" and tell the person.**
5. Add a line to [INDEX.md](INDEX.md).

## Writing style

- Every file starts with a YAML header: `status` (draft / active / superseded), `owner`, `last_reviewed`.
- Tag robot facts: **[verified]** (measured, with an artifact), **[as built]**, **[decided]** (with a D-number), **[assumed]**. Never upgrade a fact to verified without a measurement.
- Short sentences. Link instead of copying. One fact lives in one place.
- Do not invent names, dates, or numbers. If a source is ambiguous, say so.

## Related repos

- [TerralabsCove/tether](https://github.com/TerralabsCove/tether): the COVE2 sim and code. Code-coupled docs live there.
- [TerralabsCove/cove-controls](https://github.com/TerralabsCove/cove-controls): Cove's controls code and URDF.
