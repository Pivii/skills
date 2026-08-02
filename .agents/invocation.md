# Model-invoked vs user-invoked

Every `SKILL.md` in this repo is a skill. The one axis that splits them is **invocation** — who can reach it.

## User-invoked

Reachable **only by the human typing its name**. Set `disable-model-invocation: true` in the frontmatter.

The `description` is **human-facing**: a one-line summary read by a person browsing slash commands. Strip trigger lists — no "Use when the user says…".

This is where orchestration goes. Anything that spawns agents, creates branches, opens PRs, or otherwise takes an outward-facing action should be user-invoked: the human decides when it fires, not the model.

## Model-invoked

Reachable by **model or user**. The default — omit `disable-model-invocation`.

The `description` is **model-facing** and keeps rich trigger phrasing ("Use when the user wants…, mentions…, asks for…") so auto-invocation actually fires. A model-invoked skill with a bland description never runs.

This is where reusable discipline goes — the thing you want the agent to reach for on its own because the task fits.

## The test

*Could the model usefully reach for this autonomously, without the human having asked for it by name?*

Yes → model-invoked. No → user-invoked.

Reuse is the reason to extract a skill, not the test for which kind it is.
