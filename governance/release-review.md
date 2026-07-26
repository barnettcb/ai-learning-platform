# Content Release Review

A content object may be released only after all applicable checks pass.

## Instructional checks
- Teaches one primary idea.
- States an observable learner outcome.
- Requires a meaningful learner action.
- Assumes only concepts already taught or explicitly listed as prerequisites.
- Uses examples that demonstrate the target skill rather than decorate the page.

## Editorial checks
- Uses the simplest accurate explanation.
- Gives direct guidance before exceptions.
- Defines unavoidable jargon on first use.
- Removes repetition within the page.
- Avoids inflated claims and unnecessary motivational language.

## Canonical-content checks
- Confirms the concept owner in `concept-ownership.md`.
- Links to prior concepts instead of reteaching them.
- Does not create a competing definition, checklist, or framework.
- Updates dependent references when the canonical object changes.

## Reliability checks
- Distinguishes facts, judgment, and examples.
- Identifies claims that require current sources.
- Includes verification guidance where error could materially matter.
- Includes privacy or escalation guidance where relevant.

## Web checks
- Page title matches the learner's likely question.
- Headings support scanning.
- Interactive elements have a non-interactive fallback.
- Links have descriptive labels.
- Content works on narrow screens.

## Final simplification pass
Delete any sentence, example, callout, or section that does not improve understanding, action, safety, or navigation.
## Iterative release gate
1. Audit the current build before proposing changes.
2. Separate defects and design drift from optional polish.
3. Implement the smallest coherent correction set.
4. Re-run the relevant content, UX, consistency, interaction, and technical audits.
5. Repeat when a correction exposes another issue.
6. Package a release only after the complete reproducible gate passes.

The audit is part of development, not a document produced after the work.

