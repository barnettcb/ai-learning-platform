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
- Page title matches the learner's likely question without repeating the site name.
- Headings support scanning.
- Interactive elements have a non-interactive fallback.
- Written instructions match the fields and scenarios in the rendered activity.
- Course-sequence navigation renders as semantic, descriptive links rather than visible Markdown syntax.
- Reading-time and activity-time labels describe the actual learner effort.
- Content works on narrow screens.

## Visual polish checks
- Typography establishes a clear title, section, body, label, and helper-text hierarchy.
- Metadata labels sit next to the page title and remain readable without overpowering it.
- Primary and secondary actions use consistent size, radius, color, and hover/focus behavior.
- Form labels remain adjacent to their controls; selected answers and validation states are visually unambiguous.
- Text and control colors meet WCAG AA contrast targets on their intended surfaces.
- Cards, borders, shadows, and tinted panels communicate hierarchy rather than decorate every section equally.
- Desktop and narrow-screen layouts have no horizontal overflow, clipped controls, or stranded labels.
- Touch targets for primary interactive controls are at least 44 pixels high.
- Reduced-motion, keyboard-focus, and print behavior remain intact.

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


## Repository consistency checks
- The complete tracked `site/generated` tree matches a fresh build from canonical source.
- Missing, extra, or byte-different generated files block release and deployment.
- Generated output is rebuilt and committed as one complete set whenever canonical content or the builder changes.
