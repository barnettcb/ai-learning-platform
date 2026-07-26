# Lesson 30 — How Do I Reuse a Prompt Without Becoming Rigid?

## Outcome
You can preserve the useful structure of a successful prompt while adapting its facts, risks, and instructions to the next task.

## Direct answer
Reuse the reasoning pattern, not the old wording blindly.

A reusable prompt should separate stable elements from changeable ones:
- **Stable:** the task sequence, quality standard, review steps, and desired output structure;
- **Changeable:** the goal, audience, source material, constraints, risks, dates, and examples.

This turns a good interaction into a starting point rather than a script that controls every future situation.

## Identify what actually worked
After a successful result, ask:
- Which instruction shaped the answer most?
- Which context was necessary?
- Which constraints prevented mistakes?
- Which review step caught problems?
- Which parts were specific to this one case?

Keep only the elements that would remain useful in a similar task.

## Use placeholders deliberately
Replace case-specific details with clear fields such as:
- `[desired outcome]`
- `[audience]`
- `[source material]`
- `[deadline or time period]`
- `[constraints]`
- `[facts that must not be invented]`
- `[required review]`

A placeholder should tell the user what kind of information belongs there. Avoid vague labels like `[details]` when several kinds of details matter.

## Worked example
A useful prompt for comparing three service proposals included the decision criteria, budget ceiling, required risks, and a final recommendation.

The reusable version keeps that structure but removes the original vendors, prices, and deadline. It also adds a reminder to verify current terms before deciding. The template can now support software, insurance, or contractor comparisons without pretending those decisions are identical.

## Best practice
Before reusing a prompt, reread it as though the old task never happened. Replace every inherited fact, assumption, and constraint that may no longer apply.

## Common failure
A user copies a long prompt because it worked once. Hidden details from the first situation remain inside it, so the new answer is shaped by stale assumptions.

## Guided practice
Take this fixed instruction:

“Compare these two laptops and tell me which is best.”

Convert it into a flexible structure that asks for the buyer's purpose, budget, required features, source date, tradeoffs, and verification needs.

## Independent application
Choose one prior AI interaction that produced a useful result. Extract its reusable structure, replace case details with descriptive placeholders, and list at least three conditions that would require changing the template.

## Completion check
You are ready to continue when you can explain why a reusable prompt is a configurable framework rather than a permanent answer recipe.
