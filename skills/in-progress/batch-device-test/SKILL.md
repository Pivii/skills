---
name: batch-device-test
description: Test several open PRs of a mobile app on a real device in one build — their heads merged into a local test branch, one install, one checklist for the human with an OK/KO line per PR, then each PR merged or sent back on its own. Use when two or more PRs are waiting for a device test ("teste 136 137 138 sur le téléphone", "batch device test", "groupe ces PR pour un test sur device"), or when the human asks which open PRs can be tested together. For one branch on the phone, this is the wrong skill — use the repo's install command or `/ios-build`.
---

# Batch device test

`/batch-device-test 136 137 138` — one build carrying the three PRs, one install, one checklist, then a verdict and a merge per PR.

`/batch-device-test` with no numbers — propose a batch from the open PRs.

A device test is the slowest thing in a mobile PR's life: building, installing, setting the phone up, handing it over. A batch pays that once for several PRs, and keeps the verdict per PR so one KO holds back only its own PR.

Two roles, often held by one agent:

- the **lead** reviews and merges — steps 1 and 4;
- the **dev** sits at the machine wired to the device — steps 2, 3 and 5, and any solo build step 4 asks for.

Typed by the human, you hold both. Handed to a dev agent — a `/ship-issue` sub-agent, or the agent on the machine the phone is plugged into — it runs steps 2 and 3, returns the checklist to the lead, and runs the rest when the verdict is in.

Two gates, and they are the skill's whole safety: **the test branch stays local** — no upstream, no push, no PR, ever — and **a PR merges only on the human's written OK for that PR.**

## 1. Choose the batch (lead)

Read the repo: `gh repo view --json nameWithOwner,defaultBranchRef`, then its `CLAUDE.md` or `AGENTS.md` for the target branch, the merge style, the review tool it runs on PRs, how to build and install on a device, how to put the device in a known state, and how a build identifies itself on the device. Note the main clone's branch and `git status --short` — step 5 checks they are unchanged.

```bash
gh pr list --state open --base <target> --json number,title,headRefOid,files
gh pr checks <n>
gh pr view <n> --json reviews,comments
```

A PR joins the batch when all four hold:

- **it targets the batch's branch;**
- **its checks are green on its current head.** Pending checks get a bounded wait — `gh pr checks <n> --watch --fail-fast` under your tool's command timeout, 20 minutes absent a figure in the repo's docs. Still pending, the PR is out: *checks pending*;
- **its review finished without a blocking point** — the repo's reviewer, or, when the repo has none, your own read of the diff, said as such in the announcement;
- **it changes something the device can show.** Docs, CI or tooling alone have nothing to test on a phone: *nothing device-visible*.

**Overlap.** Two PRs overlap when they touch the same files, or the same **screen** — any view where both changes render at once, a shared header or tab bar counting on every view it appears in. An overlap hides which PR caused a failure, so the pair goes in separate batches: the older PR in this one, unless the human picks. Two PRs that are **alternatives** — each solving the same thing so only one can merge — are flagged as such, and the human picks one. The human may also accept an overlap and keep both; that acceptance is recorded in the announcement and in the checklist header.

Keep it to 2–5 PRs, about 15 minutes of testing. A filter that leaves one PR says so and offers the choice: a solo build through the same steps, or stop.

**Announce** the batch: each PR with its head sha, each PR dropped or held back with its reason, overlaps accepted, the target branch, the device, and what the repo's docs left open — merge style, reviewer, install command — asked once, here. Then wait for the human's word whenever the batch differs from the numbers they typed, or they typed none.

**Done when** each PR is in the batch with its head sha, or out with a reason, and the human confirmed any batch that is not exactly what they typed.

From here to the end, a PR whose head changes is back at step 1 for that PR: checks and review again on the new head.

## 2. Build the test build (dev)

The test branch is `test/batch-<numbers>`, built in its own worktree beside the main clone, so the checkout the human works in never moves. `--no-track` leaves it without an upstream — no `git push` can carry it anywhere by default:

```bash
MAIN=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")   # the main clone, even from a worktree
WT="$MAIN/../$(basename "$MAIN")-wt/test-batch-136-137-138"
git fetch origin <target>
git worktree add --no-track -b test/batch-136-137-138 "$WT" origin/<target>
```

Merge each PR's head by its sha from step 1, in a POSIX shell so the loop reads the same whatever the user's shell is. The pairs are written out literally:

```bash
cd "$WT" && sh -eu <<'EOF'
for pr in 136:<sha> 137:<sha> 138:<sha>; do
  n=${pr%%:*}; sha=${pr#*:}
  git fetch -q origin "pull/$n/head"
  [ "$(git rev-parse FETCH_HEAD)" = "$(git rev-parse "$sha")" ] || { echo "#$n: head moved since step 1"; exit 1; }
  git merge -q --no-ff --no-edit "$sha"
done
git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null && { echo "test branch has an upstream"; exit 1; }
echo "test tree $(git rev-parse --short HEAD)"
EOF
```

A moved head sends that PR back to step 1. **A conflict stops the build**: record `git diff --name-only --diff-filter=U`, run `git merge --abort`, and report the two PRs and the files to the lead — they belong in separate batches. The test branch never carries a resolution.

**Build the combined tree before installing it.** CI built each PR alone; nobody has compiled them together. Run the repo's build command in the worktree, and its tests when they are quick. A failure here is a result, reported like a conflict.

**Install one build** on the device, from the worktree:

- a native iOS app: run the `/ios-build` skill from the worktree;
- anything else: the install command the repo documents, or the one the human gave at step 1.

Keep the app's data — an install over the existing app — unless a test needs a clean install.

**Set the device up for the test**: the human's language, the models or data the tests need already in place, nothing left from earlier tests. Then **release it**: whatever drove the device for an agent — a device-control server, a UI test runner, a mirroring session — is stopped before the human picks it up. The repo's docs name its own tools.

**Done when** you can report the target sha, each merged head sha, the test tree's sha, and the identifier the device shows for the installed build — one unique to this build, such as the commit stamped in an about screen or a build number. A marketing version repeated across builds proves nothing; when the app shows nothing unique, say so and report what the install command printed.

## 3. Write the checklist (dev, read over by the lead)

One section per PR. Each holds 2–4 concrete steps — *open X, tap Y* — and the expected result in one sentence. Only what an agent could not prove on its own: a real voice, a real network, real hardware, how it feels. Say what stays untestable on this device.

Write each step from **where the change renders on this device**, not from the PR description. Read the diff for the view it lands in and what that view shows at the device's size and orientation: a label hidden below a breakpoint, a control only in landscape, a screen three taps deep. Then the step goes there — *turn the phone landscape*, *open Settings → About* — and the expected result is what the human will actually see.

```
Test build test/batch-136-137-138 — <app>, build <identifier from step 2>
<target>@<sha> + #136@<sha> + #137@<sha> + #138@<sha>
Overlap accepted: <#a and #b both change <screen>> | none

#136 — <short title>
1. <step>
2. <step>
Expected: <one sentence>

#137 — …

Not testable on this device: <what, and why>

Reply one line per PR:
#136 OK              tested, hold the merge
#136 OK, merge       tested, merge it
#137 KO: <what happened>
```

The lead passes the checklist to the human **as written**. A summary of it loses the steps the human needs.

**Done when** the human has the checklist, and nothing more runs until their reply.

## 4. After the verdict (lead)

**Each OK** is a device validation for the head that was built. Before it counts, `gh pr view <n> --json headRefOid` — a head that changed since the build has no device test, and the PR is back at step 1.

**Merging** needs the human's written OK for **that PR**: `#<n> OK, merge` in the verdict, or a later message naming it. A bare `#<n> OK` holds the merge — ask for the word. Merge in the order least likely to conflict, in the repo's merge style, one at a time:

```bash
gh pr merge <n> --<merge style>
gh pr checks <next>                       # green again before the next merge
gh pr view <next> --json mergeStateStatus # BEHIND or DIRTY → back to the dev, then step 1
```

**Each KO** is settled in this order:

1. **Suspect the combination** when the KO lands on a screen another PR in the batch also changes, or on an overlap the human accepted. Then the dev builds the suspect PR **alone** — `test/batch-<n>`, steps 2 and 3, over the existing app's data — and the human tests that. The batch branch stays until the solo result is in.
2. **Then send it back** with the human's words **verbatim**, the expected result, the proof the human asked for, and the solo result when there is one: KO alone is the PR's own bug; OK alone means the combination, and both PRs go back. A dev agent that wrote the PR is resumed rather than replaced. With no agent attached, the KO is a PR comment — `gh pr comment <n> --body-file <file>` — read back with `gh pr view <n> --json comments -q '.comments[-1].body'`.

The PR returns in a later batch.

**Done when** every PR in the batch is merged on a written OK, sent back with the human's words, or waiting for its next batch, and the human has that list.

## 5. Clean up (dev)

Once every PR, solo builds included, is settled:

```bash
git worktree remove <each test worktree>
git branch -D test/batch-136-137-138 <each solo test/batch-<n>>
git branch --list 'test/batch-*'              # empty
git ls-remote --heads origin 'test/batch-*'   # empty — no test branch ever left the machine
```

A deletion your permissions refuse goes to the human as the exact command to run, listed in the report.

Put the device back on a build of the target branch when the human uses it day to day — the step 2 install, from a worktree detached on `origin/<target>`, removed afterwards; check the identifier the device shows against that sha. Leave the test build when they ask for it.

Delete the test data still on the device: notes, files, recordings, accounts the tests created.

Check the main clone against step 1: same branch, same `git status --short`.

**Done when** both listings print nothing — or the human holds the commands that make them — the device runs the build the human expects, the main clone is as step 1 found it, and the report names what was deleted.
