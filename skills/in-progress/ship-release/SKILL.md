---
name: ship-release
description: Ship one release of this repo — version, tag, publish, verify — against the contract in `docs/RELEASING.md`. Use when someone wants to release, promote or deploy what is ready ("fais une release", "passe staging en prod", "cut a release", "ship 1.6.0", "mets ça en prod"), or to run one declared transition by name.
---

# Ship a release

One invocation, **one transition**. The contract names them; you run one of them, once.

Everything about how this repo releases comes from `docs/RELEASING.md`. Nothing comes from what you can infer.

## 1. Read the contract, or stop

```bash
git rev-parse --show-toplevel
```

No `docs/RELEASING.md` means **this repo has no release process yet, and inventing one now is the expensive way to find that out.** Say so, name the `/setup-releases` skill, and stop. Do not release from a guess: the branch names, the step order and where the version lives are all things this repo has an answer to and you do not.

With a contract, read it whole — block and prose. Then check the block against the repo before trusting a word of it: every declared branch resolves, every version home exists, the tag pattern matches something real. **A contract that no longer describes its repo fails here, loudly**, and the fix is `/setup-releases`, not a workaround.

Then pick the transition. Named in the invocation, use it; otherwise put the contract's list to the maintainer and let them choose. One that is marked `exercised: never` gets said out loud: they are about to take a path written at a desk and never walked.

**Done when the contract is read, every declaration resolves, and exactly one transition is chosen.**

## 2. Assemble what goes out

- **The range.** From the contract's `baseline` — the forge's own releases where it says so, never `git tag` on a fork — to the tip of the transition's source branch. Nothing to promote is a finished run: say so and stop.
- **The version.** Classify the range by its commit types and propose the bump **with the reasoning visible**: how many `feat`, how many `fix`, which features, and the number that follows. Where `derivation: indicative`, say the classification is unreliable here. Where the range holds commits you cannot classify, **list them** — an unprefixed commit that added a feature would quietly cost a MINOR. A MAJOR is never derived; it is stated by the maintainer or it does not happen.
- **The notes.** Written from the **issues** the range references, not from its commits: a commit says what moved in the code, an issue says what it was for. Follow the contract's template. Group by theme, name the impact and what is *not* affected, and carry the `⚙️` post-deploy section — **including when it is empty**, where it says so in as many words. That section is what a release half-lands without.

**Done when the range, the version with its reasoning, and the drafted notes all exist.**

## 3. The gate

One gate, here, before anything irreversible. Put the whole thing up at once: the transition and what it moves, the version and why, the notes, every step about to run, and what will be left for a human.

Then ask the one question the repo cannot answer: **what was validated, by whom, and where.** A green CI is not a validation — it says the thing builds. Take the answer as given, write it into the notes, and where the answer is "nothing", write that too. Inferring this, or letting it pass unasked, is how a release claims a check that never happened.

**Done when the maintainer has seen the full plan and answered the validation question.**

## 4. Run the steps, and stop only where it is safe to

Run the transition's `steps` **in the contract's order** — that order is load-bearing. A `tag` after `merge` records what shipped; a `tag` before `release` triggers the build that ships it. Reversed, the second one publishes nothing.

The step vocabulary is defined in the contract. Two carry their own hazard:

- **`ci`** — wait for it. Merging past a red check spends the gate's credibility on a build nobody looked at.
- **`verify`** — run the declared check and **compare**. Equal, the release landed. Different, the deploy did not happen or did not carry this build, and the tag now claims something false: say so, loudly, and leave the discrepancy in the release notes rather than closing the run quietly. Where the contract declares no check, state that nothing was verified and hand over the manual steps.

**A release stops only in a state where nothing is half-done.** There are three: *PR open, CI running* — nothing definitive has moved. *Release published and verified.* *Handed to a human*, with the steps only they can perform, written out. Never tagged-but-unpublished, never merged-but-untagged.

So when a step fails, do not push on and do not walk away. Undo what can be undone, then report exactly where it stopped, what is done, and what the repo's state now is. A half-shipped release nobody can locate costs more than the failure did.

Where the transition declares a `backmerge`, the run is not finished until the change is back on that branch. A hotfix that never returns to the integration branch is a bug the next release will faithfully restore.

**Done when the transition has reached one of the three stable states, and which one is stated.**

## 5. Report

Merging is done; deploying may still be running. Lead with the two things the maintainer needs to act:

- **What is live, and how you know** — the version, and the verify result that backs it, or the plain statement that nothing verified it.
- **What is left to do by hand** — the `⚙️` steps, plus anything the run could not check. Numbered, followable without opening the contract.

Then the release link, the issues covered, and anything that contradicted the contract along the way. Contradictions are worth more than they look: they are the contract asking to be updated, and `/setup-releases` is where that happens.

Report in the language the maintainer is speaking to you in. The notes and the commits follow the contract.

**Done when the maintainer can tell, from your message alone, what is in production and what is still theirs to do.**
