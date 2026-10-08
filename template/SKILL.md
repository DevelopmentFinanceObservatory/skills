---
name: _template
description: >-
  One or two sentences saying what expertise this skill carries and when an
  agent should load it. Discovery matches against this text, so write it for
  the match, not for a human browsing the repo. Name the domain, the
  questions the skill answers, and the trigger vocabulary.
license: CC-BY-4.0
---

# Skill title

The body is what the agent reads once the skill loads. Structure it however serves the domain. The launch skills are expected to cover, in some mix:

- Definitions: the terms of art, what counts and what does not, the distinctions practitioners rely on (commitments vs disbursements, grant equivalent vs flow).
- Methodological considerations: the choices an analysis must surface rather than silently make, and the defaults an expert would pick.
- Validation rules: checks a result must pass before it is presented, and the known failure modes to test for.
- Analytical recipes: step-by-step methods for the questions the domain gets asked most, naming the data and the computation.

Keep the body self-contained and load-cheap. Supporting files (reference tables, longer method notes) go in a `references/` directory beside this file, and the body links to each one by that path, so the agent reads it only when the task needs it:

## References

- [references/example.md](references/example.md) — what this file covers, in a clause

Name every reference file here. One the body never names will never load, and the build rejects it. Keep those pointers one level deep: a reference file that sends the agent on to another one makes the skill harder to load a piece at a time.
