# Policy marker scoring

What this covers: How to score an ODA activity against a policy marker. Explains principal (2), significant (1), not targeted (0), and not screened. Explains the critical difference between not targeted and not screened.

## Contents

- When to use this reference
- Concepts and definitions
- How to approach it
- Pitfalls
- What a good answer looks like

## When to use this reference

- The user asks what principal, significant, or not targeted means.
- The user asks how to interpret a score in the data.
- The user asks about the difference between not targeted and not screened.
- The user asks how to calculate totals (e.g. "gender-related ODA").

## Concepts and definitions

### The scoring system

Every bilateral allocable ODA activity that is screened against a policy marker receives one of three scores. Activities that are not screened at all receive a separate status.

Score 2 — Principal

The policy objective is the main reason the project was designed and funded. The project would not have been undertaken, or would have been designed differently, without this objective. The objective is fundamental to the project's design and expected results.

Example (gender): A project specifically designed to increase women's economic participation, where gender equality is the explicit and primary goal.

Example (climate mitigation): A renewable energy project designed specifically to reduce greenhouse gas emissions, which would not have been funded without that climate objective.

Score 1 — Significant

The policy objective is an important and deliberate part of the project, but it is not the primary reason the project was undertaken. The project has been explicitly formulated or adjusted to address the objective, even though the project's main purpose lies elsewhere.

Example (gender): A rural infrastructure project that has been explicitly designed to include women in decision-making and to address gender-differentiated access to services.

Example (climate adaptation): An agricultural development project that has been explicitly adjusted to include crop diversification to help farmers adapt to climate variability.

Score 0 — Not targeted

The project was screened against the marker and found not to address the policy objective. The objective is absent, or any reference to it is extremely limited or superficial relative to the project's overall intent.

This score means the project was examined and a deliberate decision was made that it does not qualify.

Not screened

The project was not examined against the marker at all. No score was assigned. This is different from score 0.

### The critical distinction: not targeted vs. not screened

This is the most common source of confusion in policy marker analysis.

|  | Not targeted (0) | Not screened |
| --- | --- | --- |
| Was the project examined? | Yes | No |
| What does it mean? | Examined and found not to address the objective | Never assessed |
| What does it tell you? | The donor confirmed no policy intent | Nothing about policy intent |
| How does it appear in data? | Value = 0 | Value is blank or missing |

Why this matters for analysis:

A high share of "not screened" activities in a donor's portfolio does not mean those activities do not address the policy objective. It means the donor did not report a score. This can reflect:

- Incomplete reporting practices.
- Activities that fall outside the mandatory screening scope.
- Deliberate exclusion of certain aid types from screening.

When calculating the share of ODA targeting a policy objective, always check what proportion of the denominator is "not screened." A large not-screened share makes the analysis less reliable and should be flagged as a caveat.

Practical rule: Never treat not screened as equivalent to not targeted. Do not add them together or use "not screened" as evidence of absence of policy intent.

## How to approach it

Calculating totals

Gender-related ODA (or climate-related, nutrition-related, etc.) = principal + significant (scores 2 + 1).

This is the standard approach used by OECD DAC. Label the result as "gender-related ODA" rather than "gender ODA" to reflect that it captures intent, not measured outcomes.

Principal-only ODA = score 2 only. Use this when the question is specifically about dedicated or targeted interventions, as opposed to mainstreaming.

Denominator

Always use bilateral allocable ODA as the denominator when calculating shares. Do not include non-allocable items (general budget support, debt relief, administrative costs, etc.) in the denominator. Including them would artificially deflate the share.

Handling overlap between markers

An activity can carry scores for multiple markers simultaneously. For example, a project can be scored 2 for climate mitigation and 1 for climate adaptation. When calculating total climate-related ODA:

- Do not simply add mitigation and adaptation totals — this double-counts activities marked for both.
- Use the microdataset to identify activities marked for both and count them once.
- Our practice: count an activity as "principal climate" if it scores principal on either mitigation or adaptation (or both).

## Pitfalls

Conflating not screened with not targeted. See the distinction above. This is the most consequential error in policy marker analysis.

Treating principal as the only "real" marker. Significant scores represent genuine, deliberate policy intent. Excluding them understates the donor's engagement with the policy objective.

Ignoring partial screening when calculating shares. If 40% of a donor's portfolio is not screened, the share of "gender-related ODA" calculated from the screened portion may not represent the full portfolio.

## What a good answer looks like

When explaining scores to a user:

1. Define each score clearly using the "would not have been undertaken" test for principal and the "explicitly formulated or adjusted" test for significant.
2. Explain not targeted as an active finding (the project was examined and found not to qualify).
3. Explain not screened as an absence of assessment, not a finding.
4. When presenting totals, state clearly whether the figure combines principal and significant, or is principal-only.
5. Flag the not-screened share as a caveat on the reliability of the analysis.
