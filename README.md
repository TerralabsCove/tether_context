# tether_context

The shared source of truth for the Tether project (Terra Labs, fall 2026). If you want to know what we decided, who owns what, or what the robot actually is, it's here.

**Start at [INDEX.md](INDEX.md).**

## How this repo is organized

| Folder | What goes in it | Trust level | Who edits |
|---|---|---|---|
| `truth/` | Canonical facts: project overview, robot specs, team, decisions, open questions, glossary | **Authoritative** | Anyone, via PR. Keep it small. |
| `plans/` | One living doc per workstream, each with a named owner | Working | The plan's owner |
| `meetings/` | One summary per meeting | Historical record | Whoever took notes. Frozen after the day. |
| `notes/` | Research, AI-agent output, drafts, scratch | **Not authoritative** | Anyone |
| `assets/` | Decks, PDFs, images, CAD exports | Reference | Anyone |
| `archive/` | Superseded docs. Moved here, never deleted. | Historical | Anyone |

## The rules

1. **Only `truth/` is the source of truth.** Everything else is input. If a fact matters, promote it into `truth/` and link back to where it came from.
2. **Meetings flow into decisions.** After a meeting, add its note to `meetings/`, then copy each decision into [truth/decisions.md](truth/decisions.md) as a new numbered entry. Update other `truth/` files if the decision changes them.
3. **Never rewrite a decision.** If it changes, add a new entry and mark the old one superseded.
4. **AI agents write to `notes/` by default.** They only touch `truth/` when a person explicitly asks. See [AGENTS.md](AGENTS.md).
5. **Every file has a header** with status, owner, and last-reviewed date. Meetings use the template in [meetings/_template.md](meetings/_template.md).
6. **Tag robot facts** as verified, as built, decided, or assumed. Nothing is "verified" without a measurement artifact.
7. **No new top-level folders** without talking to a PM first.
8. **Code docs stay with the code.** Architecture docs and anything that goes stale when code changes live in the [tether repo](https://github.com/TerralabsCove/tether). Link to them from here instead of copying.

## File naming

- Meetings: `meetings/YYYY-MM-DD-topic.md`
- Notes: `notes/YYYY-MM-DD-author-topic.md`. "Author" is the person, even if their AI agent wrote it.
- Assets: `assets/YYYY-MM-DD-name.ext`
- Lowercase, hyphens, no spaces.

## Adding a meeting summary

1. Copy [meetings/_template.md](meetings/_template.md) to `meetings/YYYY-MM-DD-topic.md`.
2. Paste the Granola summary under the header. Keep the transcript link.
3. Add new decisions to [truth/decisions.md](truth/decisions.md) and list their IDs in the meeting header.
4. Move answered questions out of [truth/open-questions.md](truth/open-questions.md). Add new ones.
5. Add one line to [INDEX.md](INDEX.md).

Or ask your AI agent to "file this meeting note in tether_context", and it will follow [AGENTS.md](AGENTS.md).
