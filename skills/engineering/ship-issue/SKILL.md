---
name: ship-issue
description: Run an agent on a tracker issue in its own git worktree, through five phases — context, plan, implement, verify, report.
disable-model-invocation: true
---

# Ship an issue

`/ship-issue 271` — one agent, one worktree, on issue #271.

`/ship-issue 255 252 241` — an agent and a worktree each.

You pass issue numbers. Everything else is discovered.

## 1. Read the ground

Assume nothing about this repo. Find it:

```bash
git rev-parse --show-toplevel
gh repo view --json nameWithOwner,defaultBranchRef
git branch -r
```

Then read the repo's own instructions — `CLAUDE.md`, `AGENTS.md`, and `CONTEXT.md` plus `docs/adr/` where they exist — for the branch work starts from, the branch-name convention, the build command, the test command, the lint command, what PRs target, whether the house style is merge or squash, and the language its issues and PRs are written in.

**Done when you can state each of those and where you got it.** Ask the maintainer for anything the repo doesn't say — a guessed build command burns an agent's whole run before it fails.

## 2. Refuse work that isn't ready

The **brief** — the implementation spec written on the issue — is the contract the agent builds against. Without one it invents the spec, and you spend your review reading an invention.

An issue leaves the run, with its reason reported, when it carries no brief, or when it still hides a design decision nobody has made. Both are cheaper to settle now than to unpick from a diff.

**Done when every number you were passed is either cleared or dropped with a stated reason.**

## 3. One worktree per issue

A checkout holds one set of files on one branch. An agent working in the main clone edits the files the maintainer is reading and moves the branch under them; two agents there overwrite each other. So each issue gets its own:

```bash
git fetch -q && git checkout <base> -q && git pull -q
git worktree add -b <convention>/<N>-<slug> <worktrees>/<N> <base>
```

`<worktrees>` sits **outside** the repo — a sibling directory such as `../<repo>-wt/` — so no worktree can be swept into a commit. An existing worktree for the same issue is reused by merging `<base>` into it; leave it in place, another agent may be inside.

Pass on the harness's built-in worktree isolation here. Those are temporary and throwaway-named, and this work has to end as a PR on a branch named to the repo's convention.

### Overlap

Agents collide on **shared files**, not on their own code. Before spawning, read each brief and name the surface it touches. A generated file, a registry, a lockfile, or a barrel export that two issues both edit is enough of an overlap — those two run in sequence, and only the rest run together.

**Done when every cleared issue has a worktree, and no two issues spawning together share a file.**

## 4. Spawn

One sub-agent per issue (`general-purpose` in Claude Code), its worktree as the working directory, the commands from step 1 substituted in. Parallel where step 3 allowed it. Hand it the phases whole — their never varying is the point:

> Implement issue #N in `<owner/repo>`.
>
> **Your working directory is `<path>`** — a git worktree already on this issue's branch. Stay inside it; the main clone and the other worktrees belong to other people. Your branch exists — use it.
>
> Work these five phases in order, and write phase 2 down before you touch code.
>
> **1 — Context.** Read the issue and every comment (`gh issue view N --comments`), and every issue it references. **The brief is the contract**; the body is context, and the brief wins where they disagree. Read the repo's instructions: `<the files from step 1>`.
>
> **2 — Plan.** Briefs name behaviours, not paths — locate every site yourself. Map every consumer of what you are about to change *before* changing it. Then write the plan: ordered changes, risks, and how each acceptance criterion gets verified. If the plan shows the brief is wrong or incomplete, **stop and report** — the contract gets renegotiated with the maintainer, not around them.
>
> **3 — Implement.** Atomic commits referencing `(refs #N)`. Match the surrounding code, its comment density included. Ship complete work: every path you open, you finish.
>
> **4 — Verify.** Run `<build>`, `<test>`, `<lint>`. Leave lint green — fix what you introduced, or suppress it inline with a written reason. Add tests where the change is testable. Then walk the acceptance criteria one at a time and record **evidence** for each: the command you ran and what it printed.
>
> **Run headless.** The maintainer is working on this machine, so anything that opens a window steals their focus. Use the headless form of every tool. Where a check has no headless form, add it to the maintainer's manual list instead of running it — as you do for anything else you cannot validate, with exact steps.
>
> **5 — Report.** Push and open a PR against `<target>`, then stop; merging is the maintainer's. Recap: what changed and why in plain terms; each acceptance criterion with its status and evidence; what you could not verify and exactly how to check it; anything that contradicted the issue, or that you are not comfortable with.
>
> Commits and the PR go in `<repo language>`. The recap is addressed to the maintainer, so write it in the language they are speaking to you in.
>
> Untested means untested. A recap that overstates what was verified costs more than the gap it hides.

## 5. After the report

A green CI is not a verification. Each PR earns a review pass and, where the change is only visible to a human, a manual check — then merges in the repo's house style.

Retire the worktree once its PR is merged:

```bash
git worktree remove <worktrees>/<N>
```
