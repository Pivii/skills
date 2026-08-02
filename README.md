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

Skills split on one axis — **who can invoke them**. **User-invoked** skills are reachable only when you type them (e.g. `/some-skill`); their job is to orchestrate. **Model-invoked** skills can be invoked by you *or* reached for automatically by the agent when the task fits; they hold the reusable discipline. See [.agents/invocation.md](./.agents/invocation.md).

### Engineering

Skills for daily code work.

*Nothing shipped yet.*

### Productivity

General workflow tools, not code-specific.

*Nothing shipped yet.*

## Credits

The repo layout and conventions — bucket folders, the user-invoked / model-invoked split, the promoted-bucket rule — are borrowed from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The skills themselves are mine.

## License

MIT — see [LICENSE](./LICENSE).
