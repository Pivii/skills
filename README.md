# Skills

My agent skills, packaged as a Claude Code plugin.

These are small, composable skills — each one wrangles a bit of determinism out of a stochastic system, so the agent takes the same *process* every run. Take them, adapt them, make them your own.

## Install

### Claude Code (managed, auto-updating)

```
/plugin marketplace add Pivii/skills
/plugin install pivi-skills@pivi
```

Installed skills are available in every session and every project, read-only. Pull my latest with `/plugin marketplace update`.

### Codex and other agents (editable copies)

```bash
npx skills@latest add Pivii/skills
```

This writes the skills into your repo as ordinary files you own and can edit. Nothing updates behind your back; pull changes when you want them with `npx skills update`.

## Reference

Skills split on one axis — **who can invoke them**. **User-invoked** skills are reachable only when you type them (e.g. `/some-skill`) — that lock is for skills whose cost is already spent by the time you notice they fired. **Model-invoked** skills you can type, hand to a sub-agent, or let the agent reach for when the task fits. See [.agents/invocation.md](./.agents/invocation.md).

### Engineering

Skills for daily code work.

**Model-invoked**

- **[ship-issue](./skills/engineering/ship-issue/SKILL.md)** — Run an agent on a tracker issue in its own git worktree, through five phases: context, plan, implement, verify, report. Everything about the target repo — base branch, branch naming, build, test and lint commands, PR target — is discovered, not assumed. Type it yourself, or tell an agent to use it; either way it states its scope back before it spawns anything.

### Productivity

General workflow tools, not code-specific.

*Nothing shipped yet.*

## Credits

The repo layout and conventions — bucket folders, the user-invoked / model-invoked split, the promoted-bucket rule — are borrowed from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The skills themselves are mine.

## License

MIT — see [LICENSE](./LICENSE).
