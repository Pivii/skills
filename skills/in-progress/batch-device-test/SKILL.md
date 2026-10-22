---
name: batch-device-test
description: Test several open PRs of a mobile app on a real device in one build — their heads merged into a local test branch, one install, one checklist for the human with an OK/KO line per PR, then each PR merged or sent back on its own. Use when two or more PRs are waiting for a device test ("teste 136 137 138 sur le téléphone", "batch device test", "groupe ces PR pour un test sur device"), or when the human asks which open PRs can be tested together. For one branch on the phone, this is the wrong skill — use the repo's install command or `/ios-build`.
---

# Batch device test

`/batch-device-test 136 137 138` — one build carrying the three PRs, one install, one checklist, then a verdict and a merge per PR.

`/batch-device-test` with no numbers — propose a batch from the open PRs, and wait for the human to confirm it.

A device test is the slowest thing in a mobile PR's life: building, installing, setting the phone up, handing it over. A batch pays that once for several PRs, and keeps the verdict per PR so one KO holds back only its own PR.

Two roles, often held by one agent:

- the **lead** reviews and merges — steps 1 and 4;
- the **dev** sits at the machine wired to the device — steps 2, 3 and 5.

Typed by the human, you hold both. Handed to a dev agent — a `/ship-issue` sub-agent, or the agent on the machine the phone is plugged into — it runs steps 2 and 3, returns the checklist to the lead, and runs step 5 when the verdict is in.

Two gates, and they are the skill's whole safety: **the test branch stays local** — no push, no PR, ever — and **a PR merges only on the human's written OK for that PR.**

## 1. Choose the batch (lead)

Read the repo first: `gh repo view --json nameWithOwner,defaultBranchRef`, then its `CLAUDE.md` or `AGENTS.md` for the target branch, the merge style, how to build and install on a device, how to put the device in a known state, and the review tool it runs on PRs.

```bash
gh pr list --state open --base <target> --json number,title,headRefOid,baseRefName,reviewDecision,files
gh pr checks <n>
gh pr view <n> --json reviews,comments
```

A PR joins the batch when it targets the batch's branch, its checks are green **on its current head**, and its review — the repo's automated reviewer or an independent one — finished without a blocking point. Numbers the human passed that fail one of these are dropped with the reason.

**Overlap.** Two PRs that touch the same files or the same screen hide which one caused a failure. They go in separate batches. The file lists say most of it; the screen comes from reading the diffs.

Keep it to 2–5 PRs, about 15 minutes of testing.

Then state the batch back — the PRs and the head sha of each, the ones dropped and why, the target branch, the device — and wait for the human's word when the numbers were inferred rather than typed.

**Done when** each PR is in the batch with its head sha, or out with a reason.

## 2. Build the test build (dev)

The test branch is `test/batch-<numbers>`, built in its own worktree outside the repo, so the checkout the human works in never moves:

```bash
MAIN=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")   # the main clone, even from a worktree
git fetch origin <target>
git worktree add -b test/batch-136-137-138 "$MAIN/../$(basename "$MAIN")-wt/test-batch-136-137-138" origin/<target>
cd <that worktree>
git fetch origin pull/<n>/head        # per PR; check FETCH_HEAD equals the head sha from step 1
git merge --no-ff --no-edit <sha>     # per PR, by sha, so the build is the head that was chosen
```

Merging by sha pins each PR to the head the lead chose. A head that moved since step 1 goes back to step 1 for that PR.

**A conflict stops the build.** Record `git diff --name-only --diff-filter=U`, run `git merge --abort`, and report the two PRs and the files to the lead — they belong in separate batches. The test branch never carries a resolution.

**Install one build** on the device, from the worktree:

- a native iOS app: run the `/ios-build` skill from the worktree;
- anything else: the build and install command the repo documents. None documented, ask — a guessed install command fails on the phone, where nobody is looking.

Keep the app's data — an install over the existing app — unless a test needs a clean install.

**Set the device up for the test**: the human's language, the models or data the tests need already in place, nothing left from earlier tests. Then **release it**: whatever drove the device for an agent — a device-control server, a UI test runner, a mirroring session — is stopped before the human picks it up. The repo's docs name its own tools.

**Done when** you can report the target sha and each merged head sha, the build version the device reports, and that the app is on the device and opens.

## 3. Write the checklist (dev, read over by the lead)

One section per PR. Each holds 2–4 concrete steps — *open X, tap Y* — and the expected result in one sentence. Only what an agent could not prove on its own: a real voice, a real network, real hardware, how it feels. Say what stays untestable on this device.

```
Test build test/batch-136-137-138 — <app> <version>
<target>@<sha> + #136@<sha> + #137@<sha> + #138@<sha>

#136 — <short title>
1. <step>
2. <step>
Expected: <one sentence>

#137 — …

Not testable on this device: <what, and why>

Reply one line per PR:
#136 OK
#137 KO: <what happened>
```

The lead passes the checklist to the human **as written**. A summary of it loses the steps the human needs.

**Done when** the human has the checklist, and nothing more runs until their reply.

## 4. After the verdict (lead)

**Each OK** is a device validation for the head that was built. Before it counts, `gh pr view <n> --json headRefOid` — a head that changed since the build has no device test. That PR goes to a later batch.

**Merging** waits for the human's written OK for **that PR**. A verdict line says the test passed; the merge is a second word. Propose the order — the one least likely to conflict — and the repo's merge style, and merge only the PRs the human names. Then one at a time:

```bash
gh pr merge <n> --<repo's merge style>
gh pr checks <next>                       # green again before the next merge
gh pr view <next> --json mergeStateStatus # BEHIND or DIRTY → back to the dev
```

A PR that falls behind or into conflict goes back to the dev for an update. Its update is a new head, so it returns in a later batch.

**Each KO** goes back to the dev with the human's words **verbatim**, the expected result, and the proof the human asked for. A dev agent that wrote the PR is resumed rather than replaced. The PR returns in a later batch.

**A KO the combination could cause** — two PRs near the same code, a failure neither diff explains — gets a build of the suspect PR alone, `test/batch-<n>`, through steps 2 and 3, before anyone concludes.

**Done when** every PR in the batch is merged on a written OK, sent back with the human's words, or waiting for its next batch, and the human has that list.

## 5. Clean up (dev)

Once the verdict is in:

```bash
git worktree remove <test worktree>
git branch -D test/batch-136-137-138
git branch --list 'test/batch-*'              # empty
git ls-remote --heads origin 'test/batch-*'   # empty — the branch never left the machine
```

Put the device back on a build of the target branch when the human uses it day to day — the step 2 install, from a worktree detached on `origin/<target>`, removed afterwards. Leave the test build when they ask for it.

Delete the test data still on the device: notes, files, recordings, accounts the tests created.

**Done when** both listings print nothing, the device runs the build the human expects, and the report names what was deleted.
