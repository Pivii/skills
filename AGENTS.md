# Repo conventions

Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

`engineering/` and `productivity/` are the **promoted** buckets. The plugin ships exactly the promoted set.

## Invariants

Break any of these and the repo lies to its users.

1. **Every skill in a promoted bucket** must have an entry in the top-level `README.md` **and** in `.claude-plugin/plugin.json`'s `skills` array. Skills in `in-progress/` and `deprecated/` must appear in **neither** — they live in the repo but are not shipped.
2. **The `skills` array is explicit, never implicit.** Listing paths by hand is what keeps drafts and dead skills out of the plugin. Do not replace it with directory auto-discovery.
3. **Each README entry links the skill name to its `SKILL.md`**, and groups entries under **User-invoked** or **Model-invoked**.
4. **Every skill is one or the other** — see [.agents/invocation.md](./.agents/invocation.md). The `description` is written for a different reader in each case; getting this wrong is the most common way a skill misfires.
5. **Bump `version` in `.claude-plugin/plugin.json` on every release.** Claude Code uses that field to decide when installed users see an update. A change shipped without a bump is a change nobody receives.
6. **Run `claude plugin validate . --strict` after touching either manifest**, before pushing.

## Adding a skill

1. Write it under the right bucket — start in `in-progress/` if it isn't ready.
2. Invoke `/writing-great-skills` and hold the draft against it.
3. When it's ready, move it to a promoted bucket and do invariants 1, 3, 5.
4. Validate, then push.

## Dependencies between skills

Expressed as `/skill`-style prose invocation ("Run the `/some-skill` skill"), not deep `../other-skill/FILE.md` cross-references. Shared reference docs live inside the skill that owns them; other skills reach that material by invoking the skill, not by linking across folders.

A user-invoked skill may invoke model-invoked skills, but never another user-invoked one.

## Portability

These skills are installed into other people's repos. Nothing in a `SKILL.md` may hardcode an absolute path, a machine, or a project-specific convention. Derive the repo root with `git rev-parse --show-toplevel`, the remote with `gh repo view`, and read build/lint conventions from the target repo's own `CLAUDE.md` or `AGENTS.md`. A skill that only works on my laptop belongs in that project's `.claude/skills/`, not here.
