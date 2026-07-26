# AI Learning Platform

Website-first self-study system for practical AI competence.

## Current build state

### Product foundation
- Product brief
- Editorial standard
- Content model
- Assessment framework
- Release review process
- Automated structural and repetition audit

### Curriculum architecture
- Four-part, twelve-module core curriculum
- Thirty-six canonical lessons
- Concept ownership register
- Dependency map
- Capstone structure

### Website architecture
- Sitemap
- Page patterns
- Canonical-content and search rules

### Content production
- Consolidated orientation on all twelve module landing pages
- All thirty-six canonical lessons
- Module 1–12 completion tasks
- Complete capstone project specification
- Core workflow, output-review checklist, and project-handoff template
- Start Here pages and saved interactive initial self-assessment
- Browsable static website prototype with responsive navigation
- Unified practice hub for all module completion tasks, readiness checks, and the capstone
- AI-use decision guide, core prompt pattern, verification ladder, privacy checklist, and glossary

### Website prototype
Run `python site/build_site.py`, then open `site/generated/index.html` in a browser.

The generated site is dependency-light, responsive, and built directly from the canonical Markdown content.

### Current completed learning sequence
1. What AI is good at
2. Use AI deliberately
3. Define the assignment
4. Shape the response
5. Improve through conversation
6. Research reliably
7. Work with information
8. Write, learn, and apply
9. Plan and decide
10. Use AI in high-stakes domains
11. Make good work repeatable
12. Manage ongoing work
13. Complete a real AI-assisted capstone project

## Core constraints
- Basic computer literacy assumed
- Platform neutral, with ChatGPT as the basis of design
- Direct best-practice guidance
- Practical rather than technical
- Website-first delivery
- One canonical home for each concept
- Iterative review before content is surfaced

## Current learner-experience features
- Full-text client-side search across canonical lessons, readiness checks, and reference pages
- Previous/next navigation across the complete guided sequence, including tasks and readiness checks
- Browser-local tracking for lessons, module tasks, readiness checks, and the capstone
- Private browser-local bookmarks and notes, accessible from Progress and page study tools
- Learning-data export/import covering progress, bookmarks, notes, and applied-task responses
- Separate reset controls for progress and workspace data
- Guided resume-learning path that interleaves each module’s lessons, applied task, and readiness check
- Simplified responsive navigation with an expandable module list and print-friendly lesson pages
- Clear first-time orientation, substantive saved diagnostic feedback, complete module landing pages, and a unified Practice hub
- Page-type metadata with reading-time labels for lessons and realistic completion-time labels for activities
- Active navigation, keyboard skip navigation, visible focus states, and reduced-motion support
- Scenario-based readiness checks with selectable answers, automatic scoring, immediate explanations, retry support, and persistent completion recognition
- One compact decision check in every lesson with saved selections, immediate rationale, and retry support
- Saved readiness-check attempts with restored explanations and direct lesson links, item-specific review focus, and a concise course-complete state on the Progress page
- A seven-part browser-saved capstone planner aligned with one concise project record
- Complete learning-data export/import for lesson decisions, diagnostics, worksheets, readiness checks, notes, bookmarks, progress, and the capstone plan
- A personal, printable course-completion summary that appears only after all guided work is complete
- GitHub Pages production metadata, favicon, and an accessible project-site-aware 404 page
- Full guided-path sequencing plus interactive worksheets on all twelve module completion tasks with aligned fields, response tallies, completion meters, autosave, and clear/review controls
- Automated generated-site checks for links, full-path navigation, source/activity alignment, assessment-to-lesson review links, outcomes-map coverage, accessibility elements, realistic effort labels, and repository/build consistency
- A polished professional visual system with consistent typography, comfortably sized metadata chips, 44-pixel global controls, action hierarchy, selected-answer states, responsive forms, refined navigation, and high-contrast accessible colors

## Build and verification
Run the complete reproducible release gate:

```text
python governance/release_check.py
```

This first verifies that the tracked `site/generated` tree exactly matches a fresh canonical build, then rebuilds the site, runs iterative content and site audits, compiles Python, checks source and generated JavaScript when Node.js is available, creates the distributable ZIP, and verifies its integrity.

Then open `site/generated/index.html`. Search, milestone tracking, scored readiness checks, interactive task worksheets, bookmarks, notes, learner-data export/import, and resume-learning guidance work without a server or account.

## Publish on GitHub Pages

This repository is configured to build and deploy the generated site with GitHub Actions.
The published site remains safe when GitHub hosts it beneath a repository path such as
`https://username.github.io/repository-name/`; navigation does not assume a custom domain
or a site hosted at `/`.

### First deployment

1. Create a GitHub repository and place this project at the repository root.
2. Push the project to the `main` branch.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **GitHub Actions** as the source.
5. Open **Actions** and confirm that **Build and deploy GitHub Pages** passes.
6. Use the Pages URL shown by the completed deployment job.

Every later push to `main` rebuilds the canonical Markdown content, runs the release
checks, and publishes `site/generated`. A manual deployment can also be started from
the workflow's **Run workflow** button.

The generated site is intentionally committed to the repository so browser-only downloads and code inspection match the deployed site. Whenever canonical content or the builder changes, run `python site/build_site.py` and commit the complete `site/generated` update. The release gate blocks deployment when the tracked generated tree is stale or incomplete.

For optional deep browser QA on a development machine with Playwright and Chromium installed, run `python governance/browser-audit.py`. The standard GitHub Pages release gate does not require that extra dependency; its canonical, generated-output, markup, and JavaScript checks remain self-contained.

### Repository files added for hosting

- `.github/workflows/deploy-pages.yml` — reproducible Pages build and deployment
- `requirements.txt` — pinned Python build dependency
- `.gitignore` — excludes local caches and release artifacts
- `site/generated/.nojekyll` — prevents Jekyll processing of generated files
- `site/generated/404.html` — static fallback for unknown Pages routes

### Local preview

A direct file-open still works for most testing. For behavior closest to GitHub Pages,
serve the generated directory locally:

```text
python site/build_site.py
python -m http.server 8000 --directory site/generated
```

Then open `http://localhost:8000/`.
