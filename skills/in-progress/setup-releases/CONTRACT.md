# The format of `docs/RELEASING.md`

One file, two halves. The **block** states what must never be misread. The **prose** says why, and carries what only a human could have told you.

## The block

YAML, at the top of the file. Every field is load-bearing; a release run reads it rather than interpreting sentences, because branch names are not a matter of interpretation — `staging`, `develop` and `dev` are all somebody's integration branch.

```yaml
forge: github            # github | gitlab | none
notes_language: fr       # the language release notes are written in

version:
  tags: "v*"             # the tag pattern of THIS project's line
  baseline: forge-releases   # forge-releases | tag-pattern | none
  derivation: reliable       # reliable | indicative
  homes:                     # every file the number lives in; [] if the tag is its only home
    - { file: package.json, field: version }
    - { file: src-tauri/tauri.conf.json, field: version }

transitions:
  prod:
    from: staging
    to: main
    bump: derived          # derived | patch | minor | major | none
    steps: [version, pr, ci, merge, tag, release, verify, issues]
    verify: "GET https://example.com/api/health → .version equals the tag"
    backmerge: null        # branch the change must return to, or null
```

**`baseline`** is where "the last release" is read from. `forge-releases` on any fork — `git tag` there returns the upstream's tags, and a diff from one of those describes work nobody in this repo did.

**`derivation`** records how far the version bump can be trusted from commit messages, and the prose says why: `reliable` at a high conventional-commit rate, `indicative` when a large share of commits cannot be classified. A repo that never writes `!` or `BREAKING CHANGE` cannot derive a MAJOR at all — say so, so nobody waits for one.

### The step vocabulary

Fixed set. The list order **is** the execution order.

| step | what it does |
|---|---|
| `version` | write the number into every home, commit on the source branch |
| `pr` | open the release PR, source → target |
| `ci` | wait for checks |
| `merge` | merge the PR |
| `tag` | annotated tag, pushed |
| `release` | publish the forge release, carrying the notes |
| `verify` | run the declared check |
| `issues` | safety net over the issues referenced by the promoted commits |
| `handoff` | stop, and hand a human the written steps only they can perform |

Order is the whole point of listing them. `[..., merge, tag, release]` is a tag that **records** what shipped. `[version, tag, release, verify]` is a tag that **triggers** the build that ships. Same word, opposite roles — and getting it backwards on a repo where the tag triggers CI publishes nothing at all.

A transition ending in `handoff` is complete when the steps have been handed over, not when the thing is live. An App Store submission is somebody at a keyboard; the contract says which keyboard and which steps.

## The prose

Seven sections. Each earns its place by holding something the block cannot.

**What a version means here.** Three levels, each with **a real past release of this repo** beside it. `MINOR — a page, a feature, one more language. v1.4.0, server rendering and per-URL i18n.` A lived example settles an edge case; an abstract definition restates the question. Where a level has never happened, say so and name what would qualify.

**The transitions**, one heading each, in words: what it is for, when to reach for it, what it leaves behind. This is what a person reads who has never released here.

**What counts as validation.** Who checks what, on which environment, before it reaches users. A release run asks for this to be *declared* rather than inferring it — green CI is not validation, and this section is what a truthful answer looks like.

**Standing post-deploy actions.** What must happen outside the code every time: a migration to run, a cache to clear, where environment variables live and which of them need a rebuild rather than a redeploy. The per-release list belongs in that release's notes; the recurring ones belong here.

**Rollback.** The procedure, in steps. Then, in as many words, **tested** or **untested**. A rollback nobody has ever performed is an intention, and an incident is a bad place to discover the difference.

**Scars.** What has bitten someone here that the repo does not reveal — a forge call that needs a REST fallback, a closing keyword the forge ignores in this language, a build-time variable that a redeploy will not pick up. Written once, they stop costing anything. Left in someone's head, they are paid for again every time.

**Deviations.** Wherever this repo departs from the default, the departure **and its reason**: *"no `release/*` freeze branches — for a small team they add ceremony without value."* Six months on, the reason is what stops the deviation being read as a mistake and quietly corrected.

## Marking what is not known

Where something is unverified, the contract says so in plain words — `untested`, `no automatic verification, check by hand: <steps>`, `untraced before v1.0.0`.

This is the same rule the release run answers to. Confidence a release cannot back is worse than a stated gap: the gap gets checked, and the false claim gets believed.
