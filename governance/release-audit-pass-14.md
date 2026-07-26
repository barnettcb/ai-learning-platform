# AI Learning Platform — Pass 14 Iterative Audit

## Scope
Repository consistency only. The curriculum, learner-facing design, interactions, navigation, and assessment rules remain unchanged from Live-Site Corrective Pass 13.

## Pre-implementation finding
The deployed GitHub Pages artifact was correct because the workflow rebuilt the site from canonical source, but the repository's checked-in `site/generated` tree could remain stale after a partial browser upload. That created three avoidable risks:

- Repository inspection could show old HTML that differed from the live site.
- A user downloading the repository without rebuilding could receive outdated pages.
- The release gate rebuilt generated output before checking it, so it could not detect pre-existing drift.

## Options reviewed

### Stop tracking generated HTML
Cleaner in a conventional build pipeline, but not selected for this project. The user uses browser-based GitHub uploads and benefits from a repository that is directly downloadable and testable without a build step.

### Continue tracking generated HTML without a drift gate
Rejected because it permits the same repository/live-site mismatch to recur.

### Track the complete generated site and verify it deterministically
Selected. It preserves browser-only usability while adding one focused consistency control.

## Implementation
- Rebuilt all generated files from canonical source.
- Added `governance/generated-consistency.py`.
- Added `site/build_site.py --output <directory>` for isolated comparison builds.
- Added the consistency audit before the normal build in `governance/release_check.py`.
- Added the new script to Python compilation checks.
- Updated governance and README documentation.

## Iterative verification

### Deterministic comparison
A fresh temporary build matched all 108 tracked generated files by relative path and SHA-256 digest.

### Negative test
A deliberate one-byte change to a generated page caused the consistency audit to fail and identify the stale file. Restoring the page returned the audit to a passing state.

### Simplification review
No new learner-facing control, page, navigation option, dependency, or deployment mechanism was added. One small audit script and one optional builder argument are sufficient for the identified defect.

## Release decision
Pass. Repository output, canonical source, release packaging, and the GitHub Pages deployment artifact now use the same deterministic generated tree.
