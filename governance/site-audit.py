from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "generated"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.has_h1 = False
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"] or "")
        if attr_map.get("id"):
            value = attr_map["id"] or ""
            if value in self.ids:
                self.duplicate_ids.add(value)
            self.ids.add(value)
        if tag == "h1":
            self.has_h1 = True
            self.h1_count += 1


def audit() -> list[str]:
    failures: list[str] = []
    html_files = sorted(SITE.rglob("*.html"))
    if len(html_files) < 100:
        failures.append(f"expected at least 100 HTML pages, found {len(html_files)}")
    required = [
        SITE / "index.html",
        SITE / "start.html",
        SITE / "search.html",
        SITE / "progress.html",
        SITE / "workspace.html",
        SITE / "practice" / "index.html",
        SITE / "assessments" / "module-01-readiness-check.html",
        SITE / "assets" / "site.css",
        SITE / "assets" / "site.js",
        SITE / "assets" / "search-index.js",
        SITE / "assets" / "favicon.svg",
        SITE / ".nojekyll",
        SITE / "404.html",
        SITE / "completion.html",
    ]
    for path in required:
        if not path.exists():
            failures.append(f"missing required generated asset: {path.relative_to(ROOT)}")

    for path in html_files:
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if not parser.has_h1:
            failures.append(f"missing h1: {path.relative_to(ROOT)}")
        elif parser.h1_count != 1:
            failures.append(f"expected exactly one h1, found {parser.h1_count}: {path.relative_to(ROOT)}")
        page_text = path.read_text(encoding="utf-8")
        raw_markdown_links = re.findall(r"\[[^\]\n]+\]\([^\)\n]+\)", page_text)
        if raw_markdown_links:
            failures.append(
                f"raw Markdown link visible in generated HTML: {path.relative_to(ROOT)} -> "
                + raw_markdown_links[0]
            )
        for token in ('class="skip-link"', 'id="main-content"', 'class="site-footer"'):
            if token not in page_text:
                failures.append(f"missing accessibility/polish element {token}: {path.relative_to(ROOT)}")
        if path.name != "404.html":
            for token in ('name="description"', 'name="theme-color"', 'property="og:title"', 'rel="icon"'):
                if token not in page_text:
                    failures.append(f"missing production metadata {token}: {path.relative_to(ROOT)}")
        if parser.duplicate_ids:
            failures.append(
                f"duplicate element IDs in {path.relative_to(ROOT)}: "
                + ", ".join(sorted(parser.duplicate_ids))
            )
        for href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "#", "javascript:")):
                continue
            target_text = href.split("#", 1)[0]
            if not target_text:
                continue
            target = (path.parent / target_text).resolve()
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                failures.append(f"link escapes generated site: {path.relative_to(ROOT)} -> {href}")
                continue
            if not target.exists():
                failures.append(f"broken link: {path.relative_to(ROOT)} -> {href}")


    not_found_page = SITE / "404.html"
    if not_found_page.exists():
        text = not_found_page.read_text(encoding="utf-8")
        for token in ("Page not found", ".github.io", 'id="home-link"'):
            if token not in text:
                failures.append(f"GitHub Pages fallback missing behavior: {token}")
        if "window.location.replace" in text:
            failures.append("GitHub Pages fallback should not force an automatic redirect")



    completion_page = SITE / "completion.html"
    if completion_page.exists():
        text = completion_page.read_text(encoding="utf-8")
        for token in ("data-completion-summary", 'id="print-completion"', 'data-page-kind="completion"'):
            if token not in text:
                failures.append(f"completion page missing control: {token}")

    module_pages = list((SITE / "modules").glob("module-*/index.html"))
    for path in module_pages:
        text = path.read_text(encoding="utf-8")
        if text.count('class="module-step') < 4 or 'class="module-finish"' not in text:
            failures.append(f"module landing page missing simplified learning path: {path.relative_to(ROOT)}")

    practice_hub = SITE / "practice" / "index.html"
    if practice_hub.exists():
        text = practice_hub.read_text(encoding="utf-8")
        if text.count('class="practice-module-card"') != 12 or 'class="practice-capstone"' not in text:
            failures.append("practice hub missing twelve module cards or capstone action")

    start_page = SITE / "start.html"
    if start_page.exists():
        text = start_page.read_text(encoding="utf-8")
        for token in ("data-initial-assessment", "data-diagnostic-question", "data-diagnostic-submit", "data-diagnostic-result"):
            if token not in text:
                failures.append(f"interactive opening diagnostic missing control: {token}")

    home_page = SITE / "index.html"
    if home_page.exists():
        text = home_page.read_text(encoding="utf-8")
        if 'class="nav-modules"' not in text:
            failures.append("simplified navigation missing expandable Modules section")
        if text.count('class="nav-item"><a') != 5:
            failures.append("simplified navigation should expose exactly five direct primary links")
        for token in ('class="home-hero"', 'class="home-stage-grid"', 'class="course-facts"', 'id="continue-learning"'):
            if token not in text:
                failures.append(f"home page missing orientation element: {token}")
        if text.count('<div><span>') != 4:
            failures.append("home page should show exactly four learning stages")
        if "<title>Practical AI Learning</title>" not in text:
            failures.append("home page browser title should not duplicate the site name")

    module_one_task = SITE / "practice" / "module-01-completion-task.html"
    module_two_task = SITE / "practice" / "module-02-completion-task.html"
    if module_one_task.exists() and module_one_task.read_text(encoding="utf-8").count('class="activity-scenario"') != 4:
        failures.append("Module 1 task should contain four scenarios")
    if module_two_task.exists() and module_two_task.read_text(encoding="utf-8").count('class="activity-scenario"') != 4:
        failures.append("Module 2 task should contain four scenarios")

    activity_records = {
        int(item["module"]): item
        for item in json.loads((ROOT / "practice" / "activity-bank.json").read_text(encoding="utf-8"))
    }
    for module_num in (1, 2):
        source_path = ROOT / "practice" / f"module-{module_num:02d}-completion-task.md"
        source_text = source_path.read_text(encoding="utf-8")
        scenario_section = re.search(r"## Scenarios\s+(.*?)(?=\n## |\Z)", source_text, flags=re.S)
        source_scenarios = []
        if scenario_section:
            source_scenarios = [
                match.group(1).strip()
                for match in re.finditer(r"^\d+\.\s+(.+)$", scenario_section.group(1), flags=re.M)
            ]
        interactive_scenarios = [str(item) for item in activity_records[module_num]["repeat"]["items"]]
        if source_scenarios != interactive_scenarios:
            failures.append(
                f"Module {module_num} written scenarios do not match the interactive worksheet"
            )

    lesson_pages = list((SITE / "modules").glob("module-*/lesson-*.html"))
    if len(lesson_pages) != 36:
        failures.append(f"expected 36 generated lesson pages, found {len(lesson_pages)}")
    for path in lesson_pages:
        text = path.read_text(encoding="utf-8")
        if 'data-page-kind="lesson"' not in text:
            failures.append(f"lesson missing page kind: {path.relative_to(ROOT)}")
        if "data-completion-toggle" not in text:
            failures.append(f"lesson missing completion control: {path.relative_to(ROOT)}")
        if "lesson-navigation" not in text:
            failures.append(f"lesson missing sequence navigation: {path.relative_to(ROOT)}")
        elif not re.search(r'<nav class="lesson-navigation"[^>]*>.*?<a href=', text, flags=re.S):
            failures.append(f"lesson sequence navigation is not rendered as links: {path.relative_to(ROOT)}")
        for token in ("data-lesson-check", "data-lesson-check-submit", "data-lesson-check-feedback"):
            if token not in text:
                failures.append(f"lesson missing decision check {token}: {path.relative_to(ROOT)}")
        if not re.search(r'class="page-meta"[^>]*>.*?About \d+ min read', text, flags=re.S):
            failures.append(f"lesson missing reading-time metadata: {path.relative_to(ROOT)}")

    practice_pages = list((SITE / "practice").glob("module-*-completion-task.html"))
    if len(practice_pages) != 12:
        failures.append(f"expected 12 generated practice pages, found {len(practice_pages)}")
    for path in practice_pages:
        text = path.read_text(encoding="utf-8")
        if 'data-page-kind="practice"' not in text:
            failures.append(f"practice page missing page kind: {path.relative_to(ROOT)}")
        if "data-completion-toggle" not in text:
            failures.append(f"practice page missing completion control: {path.relative_to(ROOT)}")
        if not re.search(r'<nav class="lesson-navigation"[^>]*>.*?<a href=', text, flags=re.S):
            failures.append(f"practice sequence navigation is not rendered as links: {path.relative_to(ROOT)}")
        if "About 10–20 min" not in text:
            failures.append(f"practice page missing activity-time metadata: {path.relative_to(ROOT)}")
        for token in (
            "data-interactive-activity",
            "data-activity-input",
            "data-activity-count",
            "data-activity-progress",
            "data-activity-review",
            "data-activity-clear",
            "data-activity-status",
            "data-activity-challenge",
            "data-challenge-choice",
            "data-challenge-check",
            "data-challenge-feedback",
        ):
            if token not in text:
                failures.append(f"practice page missing interactive control {token}: {path.relative_to(ROOT)}")


    assessment_pages = list((SITE / "assessments").glob("module-*-readiness-check.html"))
    if len(assessment_pages) != 12:
        failures.append(f"expected 12 generated assessment pages, found {len(assessment_pages)}")
    for path in assessment_pages:
        text = path.read_text(encoding="utf-8")
        if 'data-page-kind="assessment"' not in text:
            failures.append(f"assessment page missing page kind: {path.relative_to(ROOT)}")
        if not re.search(r'<nav class="lesson-navigation"[^>]*>.*?<a href=', text, flags=re.S):
            failures.append(f"assessment sequence navigation is not rendered as links: {path.relative_to(ROOT)}")
        if "About 5 min" not in text:
            failures.append(f"assessment page missing activity-time metadata: {path.relative_to(ROOT)}")
        for token in ("data-assessment-form", "data-question", "data-answer", "data-assessment-result"):
            if token not in text:
                failures.append(f"assessment page missing control {token}: {path.relative_to(ROOT)}")

    capstone_page = SITE / "capstone" / "capstone-project.html"
    if capstone_page.exists():
        text = capstone_page.read_text(encoding="utf-8")
        if 'data-page-kind="capstone"' not in text or "data-completion-toggle" not in text:
            failures.append("capstone missing completion tracking")
        for token in ("data-capstone-workbook", "data-capstone-input", "data-capstone-count", "data-capstone-progress", "data-capstone-review", "data-capstone-status", "Delivery and preservation", "Keep a concise project record"):
            if token not in text:
                failures.append(f"capstone missing aligned planner or record content: {token}")
        if "Plan: about 15–20 min; project time varies" not in text:
            failures.append("capstone missing realistic effort metadata")

    progress_page = SITE / "progress.html"
    if progress_page.exists():
        js_text = (SITE / "assets" / "site.js").read_text(encoding="utf-8")
        for token in ("Review focus", "savedAssessment", "data-capstone-workbook"):
            if token not in js_text:
                failures.append(f"feedback/completion behavior missing from generated JavaScript: {token}")

    study_pages = lesson_pages + practice_pages + assessment_pages + [capstone_page]
    study_pages += list((SITE / "reference").glob("*.html"))
    study_pages += list((SITE / "modules").glob("module-*/overview.html"))
    study_pages = [path for path in study_pages if path.exists() and path.name != "index.html"]
    for path in study_pages:
        text = path.read_text(encoding="utf-8")
        for token in ("data-bookmark-toggle", 'id="page-note"', 'id="note-status"'):
            if token not in text:
                failures.append(f"study page missing workspace control {token}: {path.relative_to(ROOT)}")
        if 'data-page-id=""' in text:
            failures.append(f"study page missing stable page ID: {path.relative_to(ROOT)}")

    progress_page = SITE / "progress.html"
    if progress_page.exists():
        text = progress_page.read_text(encoding="utf-8")
        for control_id in (
            "export-progress",
            "import-progress",
            "import-progress-file",
            "reset-progress",
            "progress-status",
        ):
            if f'id="{control_id}"' not in text:
                failures.append(f"progress page missing control: {control_id}")

    workspace_page = SITE / "workspace.html"
    if workspace_page.exists():
        text = workspace_page.read_text(encoding="utf-8")
        for control_id in ("workspace-dashboard", "clear-workspace", "workspace-status"):
            if f'id="{control_id}"' not in text:
                failures.append(f"workspace page missing control: {control_id}")

    site_css = SITE / "assets" / "site.css"
    if site_css.exists():
        css_text = site_css.read_text(encoding="utf-8")
        defined_vars = set(re.findall(r"(--[a-z0-9-]+)\s*:", css_text, flags=re.I))
        used_vars = set(re.findall(r"var\((--[a-z0-9-]+)\)", css_text, flags=re.I))
        undefined_vars = sorted(used_vars - defined_vars)
        if undefined_vars:
            failures.append("undefined CSS custom properties: " + ", ".join(undefined_vars))

    site_js = SITE / "assets" / "site.js"
    if site_js.exists():
        text = site_js.read_text(encoding="utf-8")
        for token in (
            "completed_ids",
            "bookmark_ids",
            "notes",
            "import-progress-file",
            "progressKey",
            "bookmarksKey",
            "notesKey",
            "responsesKey",
            "activity_responses",
            "data-interactive-activity",
            "workspace-dashboard",
            "data-assessment-form",
            "Readiness check complete",
            "initial-self-assessment",
            "complete === total",
            "data-lesson-check",
            "lesson-check-[a-z0-9-]+",
            "activity|readiness-check",
            "capstone-project",
            "Course complete",
            "data-completion-summary",
            "print-completion",
            "sanitizeImportedValue",
        ):
            if token not in text:
                failures.append(f"generated JavaScript missing learner-data behavior: {token}")

    search_index = SITE / "assets" / "search-index.js"
    if search_index.exists():
        text = search_index.read_text(encoding="utf-8")
        if "PRACTICAL_AI_MILESTONES" not in text:
            failures.append("search index missing milestone records")
        if "PRACTICAL_AI_GUIDED_PATH" not in text:
            failures.append("search index missing guided learning path")
        for module_num in range(1, 13):
            lesson_marker = f'"module": {module_num}'
            task_marker = f'"id": "module-{module_num:02d}-completion-task"'
            check_marker = f'"id": "module-{module_num:02d}-readiness-check"'
            if lesson_marker not in text or task_marker not in text or check_marker not in text:
                failures.append(f"guided path missing Module {module_num} records")

    progress_page = SITE / "progress.html"
    if progress_page.exists() and 'id="next-recommended-step"' not in progress_page.read_text(encoding="utf-8"):
        failures.append("progress page missing next recommended step")

    return failures


if __name__ == "__main__":
    problems = audit()
    if problems:
        print("SITE AUDIT FAILED")
        for problem in problems:
            print(f"- {problem}")
        sys.exit(1)
    pages = len(list(SITE.rglob("*.html")))
    print(f"SITE AUDIT PASSED: {pages} HTML pages checked")
