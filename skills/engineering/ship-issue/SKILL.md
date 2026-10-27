---
name: ship-issue
description: Run an agent on a tracker issue in its own git worktree, through five phases — context, plan, implement, verify, report. Use when someone hands you issue numbers to build — "ship issue 285", "lance le dev sur #271", "take 255 252 241 in parallel" — or asks for tracker issues to be implemented in isolated worktrees. This one writes code, pushes branches and opens PRs; for reading, triaging or estimating an issue, don't reach for it.
---

# Ship an issue

`/ship-issue 271` — one agent, one worktree, on issue #271.

`/ship-issue 255 252 241` — an agent and a worktree each.

`/ship-issue 271 avec captures et vidéo` — the same, with proof attached; see [Proof, on request](#proof-on-request).

You pass issue numbers. Everything else is discovered.

## 1. Read the ground

Assume nothing about this repo. Find it:

```bash
git rev-parse --show-toplevel
gh repo view --json nameWithOwner,defaultBranchRef
git branch -r
```

Then read the repo's own instructions — `CLAUDE.md`, `AGENTS.md`, and `CONTEXT.md` plus `docs/adr/` where they exist — for the branch work starts from, the branch-name convention, the build command, the test command, the lint command, what PRs target, whether the house style is merge or squash, the language its issues and PRs are written in, and — for step 5 — which checkout the maintainer builds from when they test by hand, and how a running build says which commit it came from.

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

The run reaches you two ways — the maintainer types it, or an agent they're talking to is told to use it. Both are fine. What isn't fine is spawning on numbers nobody confirmed: the branches, the commits and the PRs all land under the maintainer's name, and that is the step you cannot take back.

So say it back first — the issues cleared, the ones dropped and why, which ones run together, the base and target branches you found, and any proof asked for. Then spawn. If the numbers reached you inferred rather than stated, stop there and wait for the maintainer's word.

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
> **5 — Report.** Push and open a PR against `<target>`, then stop; merging is the maintainer's.
>
> Your recap does not reach the maintainer directly — it returns to the agent that spawned you, to be relayed. Write it to survive that hop, and open it with these two:
>
> - **What this was for.** The need, in the maintainer's terms, from the brief — not a summary of your diff. They wrote that issue a while ago and have held ten other things since.
> - **To test by hand.** Numbered; each line a step and the result to expect. Everything phase 4 left unverified, plus every criterion only a human eye can settle. Followable without reopening the issue. If there is genuinely nothing left, say so and name the commands that covered it — never pad this list to look thorough.
>
> Both go in the PR body as well, so they are still there at review time when this conversation is gone.
>
> Then the rest: what changed and why; each acceptance criterion with its status and evidence; anything that contradicted the issue, or that you are not comfortable with.
>
> Commits and the PR go in `<repo language>`. The recap reaches the maintainer once relayed, so write it in the language they are speaking to you in.
>
> Untested means untested. A recap that overstates what was verified costs more than the gap it hides.

### Proof, on request

Off by default: a run with no word about media is exactly the run above. The maintainer turns each medium on at launch, in their own words — "avec captures", "avec vidéo", "with screenshots and video"; "sans captures" keeps it off. Screenshots and video are separate switches, and one never implies the other. They cover every issue in the run unless the wording ties them to one.

When either is on, append this block to the prompt, keeping only the media asked for and the section for the project's kind:

> **Proof — <screenshots | video | screenshots and video>.** The maintainer will validate this PR on proof instead of retesting it, so capture what phase 4 exercised: screenshots of every screen the change touches — and the same screens built from `<base>` when the difference is the point, in a throwaway `git worktree add --detach "$(mktemp -d)" <base>` you remove afterwards, so your branch never moves — it starts with no dependencies, so install them there, or link your branch's when the lockfile is identical — and a video of the tested path, start to finish. Write the files outside the worktree (`proof=$(mktemp -d)`) so none is swept into a commit. If the repo's instructions define a proof workflow of their own — CI artifacts, a media folder — follow it and link what it produces.
>
> *iOS.* Capture on a simulator of your own: the one already booted may be the maintainer's. `xcrun simctl create` it with a device type its runtime supports (`supportedDeviceTypes` in `xcrun simctl list runtimes -j`), then `xcrun simctl boot <udid>` — booting through `simctl` opens no window; opening Simulator.app does. `simctl` cannot tap, so drive the path with an XCUITest — the repo's, or one you write — pinned with `xcodebuild test -destination id=<udid>`, and take the screenshots inside it as attachments, exported with `xcrun xcresulttool export attachments` and renamed from its `manifest.json` (`suggestedHumanReadableName`) — the files come out named by UUID: only the test knows the moment after each action. A static screen with no test to drive it — a `<base>` build, say — is fine with `simctl install` / `launch` and `xcrun simctl io <udid> screenshot <file>.png`. For video, `xcrun simctl io <udid> recordVideo --codec=h264 <file>.mp4 & rec=$!`, wait for `Recording started` on its stderr, run the test, then `kill -INT "$rec"` — the file is only finalized on SIGINT, and the PID keeps you off another agent's recorder. The opening seconds show the home screen while the runner installs; that is fine. `xcrun simctl delete <udid>` when done.
>
> *Web.* Serve the site the way the repo says, and capture with a headless browser — Playwright's default, after `npx playwright install --only-shell chromium` (headless, downloaded once). `npx playwright screenshot --full-page --wait-for-timeout <ms> <url> <file>.png` per static page, the wait outlasting any entrance animation; where content draws on scroll — lazy images, in-view animations — a full-page shot leaves it blank, so scroll it into view in a short script, or shoot the viewport around the changed element once it is visible. A script needs the `playwright` package: `npm i playwright` in a tools dir of its own (`mktemp -d`), never in the repo. Look at every shot: it must show what it claims. For video, a short Playwright script with `recordVideo` on the browser context, which writes a `.webm` when the context closes. When the site deploys on Vercel, add the branch preview once the PR is open: Vercel records it as a GitHub deployment on the head commit — `gh api "repos/<owner/repo>/deployments?sha=<head sha>"`, then that deployment's `statuses_url` for `environment_url`.
>
> GitHub has no API to upload into a PR body, so publish the files on a branch of their own that is never merged — one orphan commit, which touches neither your branch nor your worktree:
>
> ```bash
> tree=$(for f in "$proof"/*; do printf '100644 blob %s\t%s\n' "$(git hash-object -w --no-filters "$f")" "${f##*/}"; done | git mktree)
> sha=$(git commit-tree "$tree" -m "proof for #N")
> git push -f origin "${sha}:refs/heads/proof/N"   # braces: zsh reads "$sha:r…" as a modifier
> ```
>
> Link each file as `https://github.com/<owner/repo>/blob/<sha>/<file>?raw=true` — screenshots inline as `![…](…)`, the video as a link. On a private repo these resolve only for a logged-in reader; an anonymous 404 is not a broken link. If the push is refused, give the local paths instead and say why.
>
> In phase 5, the recap and the PR body both carry a **Proof** section: every proof asked for, linked, plus the Vercel preview — or "no Vercel preview: none recorded" when the deployments come back empty. A proof asked for and not produced is named there with the reason it could not be — a silent gap reads as a pass. That includes a change with no screen or path to show: the medium is *not applicable*, with why. Capturing an unrelated page in its place fakes the proof; a command transcript may back the claim up, never stand in for it.

## 5. Relay, then stop

The reports came back to **you**. A sub-agent's final report is not shown to the human — so right now the run looks finished from where you sit and invisible from where the maintainer sits. Nothing any agent wrote has reached them.

So relay it before anything else, one block per issue, leading with the two things that let a review actually start: **what the issue was for**, and **what to test by hand**. Pass those test steps through as they were written. Compressing them to "a few manual checks remain" throws away the one part the maintainer cannot reconstruct from the diff. Then the PR link; the Proof section when one was asked for, its links and its gaps passed through as written; what was verified and how, and anything the agent flagged or was uncomfortable with.

That relay is the deliverable of this whole run. The maintainer should be able to start testing from your message alone, without opening an issue or reading a diff to remember what any of this was for.

### Hand the test list a place to run

The steps were written inside the worktree and carry its assumptions, so open them with the PR head sha, the checkout the maintainer builds from, and the one command that proves what is running is that commit — `git -C <path> log -1 --oneline` where the repo offers nothing better.

Then move nothing. Both checkouts are already spoken for, and moving either is how a maintainer ends up testing code that isn't there. The worktree is the agent's — leave it, and a rework costs nothing. The main clone is the maintainer's, and they are probably working in it right now: say what testing would take and wait for their word. When it comes, `git checkout <sha>` there detaches and passes, where `git checkout <branch>` is refused while the worktree holds it.

**Done when the maintainer can start testing without asking you where anything is.**

Then stop. **Do not review the PRs and do not merge them.** Reviewing is a run of its own, and every repo already has its own path for it — a CI pipeline, an automated reviewer, a human. A pass you add on top lands as a second opinion from the system that wrote the code, on a thread that belongs to someone else. If the maintainer wants one from you, they will ask.

Say once what is still owed, and leave it there: a green CI is not a verification, and the manual list you just relayed is the part no reviewer will cover.

### When it comes back

A failed test sends the issue back to the agent, not to you. Resume the one that wrote it (`SendMessage` in Claude Code) rather than spawning fresh over the same branch — its context is the reason the second attempt is cheaper than the first. Its worktree is where it left it, so there is nothing to restore. What goes stale is the maintainer's checkout, and you are the only one who knows: say so before the agent starts.

Retire the worktree once its PR is merged, and its proof branch if it has one — every clone fetches it otherwise. The PR's proof links die with it; they were for the review, and the review is over.

```bash
git worktree remove <worktrees>/<N>
git push origin --delete proof/<N>
```
