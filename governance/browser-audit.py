from __future__ import annotations

from pathlib import Path, PurePosixPath
import json
import re

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "generated"
SCREENSHOTS = ROOT.parent / "pass17-browser-screenshots"
CSS = (SITE / "assets" / "site.css").read_text(encoding="utf-8")
SEARCH_JS = (SITE / "assets" / "search-index.js").read_text(encoding="utf-8")
SITE_JS = (SITE / "assets" / "site.js").read_text(encoding="utf-8")

LOCAL_STORAGE_SHIM = r"""
(() => {
  const store = Object.create(null);
  window.__auditStorage = store;
  Object.defineProperty(window, 'localStorage', {
    configurable: true,
    value: {
      getItem(key) { return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null; },
      setItem(key, value) { store[key] = String(value); },
      removeItem(key) { delete store[key]; },
      clear() { Object.keys(store).forEach((key) => delete store[key]); },
      key(index) { return Object.keys(store)[index] ?? null; },
      get length() { return Object.keys(store).length; },
    },
  });
})();
"""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def prepared_html(relative_path: str) -> str:
    source = (SITE / relative_path).read_text(encoding="utf-8")
    source = re.sub(r'<link\s+[^>]*rel="stylesheet"[^>]*>', "", source, flags=re.I)
    source = re.sub(r'<script\s+[^>]*src="[^"]+"[^>]*>\s*</script>', "", source, flags=re.I)
    parent = PurePosixPath(relative_path).parent.as_posix()
    base = "https://audit.invalid/" if parent == "." else f"https://audit.invalid/{parent}/"
    return source.replace("<head>", f'<head><base href="{base}">', 1)


def load_page(page: Page, relative_path: str, *, run_js: bool = True) -> None:
    page.set_content(prepared_html(relative_path), wait_until="domcontentloaded")
    page.add_style_tag(content=CSS)
    if run_js:
        page.add_script_tag(content=SEARCH_JS)
        page.add_script_tag(content=SITE_JS)
        page.wait_for_timeout(25)


def main() -> None:
    html_paths = sorted(path.relative_to(SITE).as_posix() for path in SITE.rglob("*.html"))
    functional_checks = 0
    render_checks = 0
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path="/usr/bin/chromium")
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        context.add_init_script(LOCAL_STORAGE_SHIM)
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)

        load_page(page, "index.html")
        expect(page.locator(".home-hero .primary-action").count() == 1, "Home must have one dominant first-time action")
        expect(page.get_by_text("Open Module 1", exact=True).count() == 0, "Home still exposes the orientation bypass")
        expect(page.locator("[data-continue-link]").first.get_attribute("href").endswith("/modules/module-01/lesson-01.html"), "Continue Learning does not open the first guided item")
        functional_checks += 3

        load_page(page, "start.html")
        expect(page.get_by_role("link", name="Begin Module 1").count() >= 2, "Start Here needs Module 1 actions before and after the diagnostic")
        for number in range(1, 6):
            page.locator(f'input[name="diagnostic-{number}"][value="2"]').check()
        page.locator("[data-diagnostic-submit]").click()
        expect("10 of 10 points" in page.locator("[data-diagnostic-result]").inner_text(), "Diagnostic score is not shown")
        expect(page.locator("[data-diagnostic-feedback]:visible").count() == 5, "Diagnostic question feedback is incomplete")
        load_page(page, "start.html")
        expect("10 of 10 points" in page.locator("[data-diagnostic-result]").inner_text(), "Saved diagnostic result did not restore")
        functional_checks += 4
        page.screenshot(path=str(SCREENSHOTS / "start-diagnostic-desktop.png"), full_page=True)

        load_page(page, "modules/module-01/index.html")
        expect(page.locator(".module-orientation-grid section").count() == 3, "Module landing page lacks consolidated orientation")
        expect(page.locator(".module-step").count() == 3, "Module landing page should show exactly three lesson steps")
        expect(page.locator('a[href="overview.html"]').count() == 0, "Module landing page still links to a separate overview")
        functional_checks += 3
        page.screenshot(path=str(SCREENSHOTS / "module-01-desktop.png"), full_page=True)

        load_page(page, "modules/module-01/overview.html")
        expect(page.get_by_role("heading", name="Module 1 orientation moved").count() == 1, "Legacy overview route does not explain the move")
        expect(page.locator('a[href="index.html"]').count() >= 1, "Legacy overview route does not link to the module landing page")
        functional_checks += 2

        load_page(page, "modules/module-02/lesson-04.html")
        expect(page.locator('.lesson-navigation a[href="../../assessments/module-01-readiness-check.html"]').count() == 1, "Module 2 first lesson does not link back to Module 1 readiness")
        load_page(page, "practice/module-01-completion-task.html")
        expect(page.locator("[data-activity-challenge]").count() == 0, "Redundant task challenge remains")
        expect(page.locator('.lesson-navigation a[href="../modules/module-01/lesson-03.html"]').count() == 1, "Applied task lacks previous-lesson link")
        inputs = page.locator("[data-activity-input]")
        for index in range(inputs.count()):
            inputs.nth(index).fill(f"Response {index + 1}")
        page.wait_for_timeout(300)
        page.locator("[data-activity-review]").click()
        expect("All required responses are complete" in page.locator("[data-activity-status]").inner_text(), "Task completion review failed")
        load_page(page, "practice/module-01-completion-task.html")
        expect(page.locator("[data-activity-input]").first.input_value() == "Response 1", "Task responses did not restore")
        functional_checks += 5

        load_page(page, "assessments/module-01-readiness-check.html")
        expect(page.locator('.lesson-navigation a[href="../practice/module-01-completion-task.html"]').count() == 1, "Readiness check lacks previous-task link")
        expect(page.locator("[data-explanation] a").count() == 2, "Readiness questions lack direct lesson links")
        load_page(page, "assessments/module-05-readiness-check.html")
        expect(page.locator("[data-question]").count() == 3, "Module 5 does not assess example use")
        load_page(page, "assessments/module-08-readiness-check.html")
        expect(page.locator("[data-question]").count() == 3, "Module 8 does not assess all three application areas")
        functional_checks += 4

        load_page(page, "practice/module-07-completion-task.html")
        expect(page.locator('a[href="module-07-source-packet.html"]').count() == 1, "Module 7 task does not link to the packet")
        load_page(page, "practice/module-07-source-packet.html")
        expect(page.locator(".source-figure").count() == 1, "Module 7 source packet lacks the annotated image record")
        article_text = page.locator("article").inner_text()
        expect("$18,450" in article_text and "$18,950" in article_text, "Source packet does not preserve the deliberate total conflict")
        functional_checks += 3
        page.screenshot(path=str(SCREENSHOTS / "module-07-source-packet-desktop.png"), full_page=True)

        page.evaluate("""() => {
          localStorage.setItem('practical-ai-learning-responses-v1', JSON.stringify({
            'lesson-check-01': {choice: 1, correct: false},
            'module-01-readiness-check': {choices: [0, 0], score: 0, passed: false, attempts: 1}
          }));
        }""")
        load_page(page, "progress.html")
        expect(page.locator(".progress-review li").count() == 2, "Progress review does not list exact missed items")
        expect(page.locator('.progress-review a[href="modules/module-01/lesson-01.html"]').count() == 1, "Progress review lacks missed lesson link")
        expect(page.locator('.progress-review a[href="assessments/module-01-readiness-check.html"]').count() == 1, "Progress review lacks failed readiness link")
        functional_checks += 3
        page.screenshot(path=str(SCREENSHOTS / "progress-review-desktop.png"), full_page=True)

        page.evaluate("""() => localStorage.setItem('practical-ai-learning-completed-v1', JSON.stringify(['module-01-lesson-01']))""")
        load_page(page, "index.html")
        expect(page.locator("[data-continue-link]").first.get_attribute("href").endswith("/modules/module-01/lesson-02.html"), "Continue Learning did not advance after completion")
        functional_checks += 1

        expect(not errors, f"Browser console or page errors during functional audit: {errors[:3]}")
        context.close()

        for viewport_name, viewport in (("desktop", {"width": 1366, "height": 900}), ("mobile", {"width": 390, "height": 844})):
            render_context = browser.new_context(viewport=viewport)
            render_context.add_init_script(LOCAL_STORAGE_SHIM)
            render_page = render_context.new_page()
            render_errors: list[str] = []
            render_page.on("pageerror", lambda error: render_errors.append(str(error)))
            render_page.on("console", lambda message: render_errors.append(message.text) if message.type == "error" else None)
            for path in html_paths:
                load_page(render_page, path)
                overflow = render_page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
                expect(not overflow, f"Horizontal overflow on {viewport_name}: {path}")
                if viewport_name == "mobile":
                    nav_heights = render_page.locator(".lesson-navigation a").evaluate_all("elements => elements.map((element) => element.getBoundingClientRect().height)")
                    expect(all(height <= 100 for height in nav_heights), f"Oversized mobile sequence action on {path}: {nav_heights}")
                if viewport_name == "mobile" and path in {"start.html", "modules/module-01/index.html", "practice/module-07-source-packet.html"}:
                    safe_name = path.replace("/", "-").replace(".html", "")
                    render_page.screenshot(path=str(SCREENSHOTS / f"{safe_name}-mobile.png"), full_page=True)
                render_checks += 1
            expect(not render_errors, f"Browser errors during {viewport_name} render audit: {render_errors[:3]}")
            render_context.close()

        browser.close()

    print(f"BROWSER AUDIT PASSED: {functional_checks} functional checks; {render_checks} desktop/mobile page renders")


if __name__ == "__main__":
    main()
