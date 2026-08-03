# Model-invoked vs user-invoked

Every `SKILL.md` in this repo is a skill. The one axis that splits them is **invocation** — who can reach it.

## User-invoked

Reachable **only by the human typing its name**. Set `disable-model-invocation: true` in the frontmatter.

The `description` is **human-facing**: a one-line summary read by a person browsing slash commands. Strip trigger lists — no "Use when the user says…".

This is for skills whose cost lands before anyone can look at it — a false positive that is already spent by the time you see it fired.

Taking an outward-facing action is not by itself that. A skill that spawns agents, pushes branches or opens PRs can be model-invoked, provided **the gate lives inside the skill**: it states its scope back and waits before the irreversible step. Move the gate into the skill and you keep the safety while staying delegable. Leave the skill ungated and this is where it belongs.

## Model-invoked

Reachable by **model or user**. The default — omit `disable-model-invocation`.

The `description` is **model-facing** and keeps rich trigger phrasing ("Use when the user wants…, mentions…, asks for…") so auto-invocation actually fires. A model-invoked skill with a bland description never runs.

This is where reusable discipline goes — the thing you want the agent to reach for on its own because the task fits. It is also where orchestration goes once it carries its own gate, because this is the only setting an agent can be *handed* a skill in.

## The test

*If this fires and the human did not want it, what does it cost to find out?*

Cheap and visible → model-invoked. Spent before they see it → user-invoked.

Note what the test does **not** ask: whether the human named the skill. Naming it and calling it are different acts. A human who tells an agent "use `/ship-issue` on 285" has named it — but the call comes from the model, and `disable-model-invocation: true` refuses it. That flag does not only block autonomy; it blocks **delegation**, and delegation is how these skills actually get used. Reach for it when the skill has no gate of its own, not as a reflex against skills that act.

Reuse is the reason to extract a skill, not the test for which kind it is.
