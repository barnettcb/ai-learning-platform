# Current Release — Repository Consistency Pass 14

This release resolves the repository-maintenance issue found during the post-deployment Pass 13 audit. It does not change the curriculum, learner interactions, or visual design.

## Changes
- Rebuilt and synchronized the complete `site/generated` directory from the canonical Pass 13 source.
- Added a deterministic generated-output audit that builds the site in a temporary directory and compares every generated file by path and SHA-256 digest.
- Updated the release gate so stale, missing, or unexpected generated files fail before packaging or GitHub Pages deployment.
- Added an optional `--output` argument to the site builder so audits can create a fresh comparison build without altering the repository copy.
- Updated release documentation to state that generated HTML is intentionally tracked and must remain synchronized with canonical source.

## Release gate
Content, generated-output consistency, UX, interaction, source/activity alignment, JavaScript, generated-site, GitHub Pages, and ZIP-integrity checks must pass before delivery.
