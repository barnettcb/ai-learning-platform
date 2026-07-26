from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "generated"
STATIC = ROOT / "site" / "static"
SITE_DESCRIPTION = "A practical, platform-neutral self-study course for using conversational AI clearly, critically, and responsibly."

markdown = mistune.create_markdown(escape=False)

MODULE_NAMES = {
    1: "Understand What AI Can Do",
    2: "Use AI Deliberately",
    3: "Define the Assignment",
    4: "Shape the Response",
    5: "Improve Through Conversation",
    6: "Research Reliably",
    7: "Work with Information",
    8: "Write and Learn",
    9: "Plan and Decide",
    10: "Use AI in High-Stakes Domains",
    11: "Make Good Work Repeatable",
    12: "Manage Ongoing Work",
}

SEARCH_ITEMS: list[dict[str, str]] = []
MILESTONE_ITEMS: list[dict[str, str | int]] = []
ASSESSMENTS = json.loads((ROOT / "assessments" / "module-checks.json").read_text(encoding="utf-8"))
ACTIVITIES = {int(item["module"]): item for item in json.loads((ROOT / "practice" / "activity-bank.json").read_text(encoding="utf-8"))}
LESSON_CHECKS = {int(item["lesson"]): item for item in json.loads((ROOT / "practice" / "lesson-checks.json").read_text(encoding="utf-8"))}

LEARNING_OUTCOMES = [
    (
        "Use AI with sound judgment",
        "Decide when AI is useful, where human control must remain, and how much review a task deserves.",
        [1, 2, 3, 22, 23],
    ),
    (
        "Communicate clearly with AI",
        "Define outcomes, context, constraints, examples, and response formats that make useful work more likely.",
        [4, 5, 6, 10, 11, 12],
    ),
    (
        "Improve work through collaboration",
        "Use conversation, critique, revision, and structured handoffs instead of expecting one perfect request.",
        [13, 14, 15, 30, 31],
    ),
    (
        "Research and verify reliably",
        "Frame research questions, work from evidence, check changing facts, and preserve uncertainty when it matters.",
        [16, 17, 18, 28, 35],
    ),
    (
        "Work with information and files",
        "Summarize, compare, transform, and extract information while protecting meaning and source fidelity.",
        [19, 24, 25, 26, 27],
    ),
    (
        "Write, learn, plan, and decide",
        "Apply AI to practical thinking tasks without surrendering authorship, understanding, or responsibility.",
        [20, 21, 29, 32, 33],
    ),
    (
        "Protect privacy and manage risk",
        "Minimize sensitive information and use stronger controls in health, legal, financial, employment, and safety contexts.",
        [22, 23, 34],
    ),
    (
        "Build repeatable personal workflows",
        "Turn successful work into reusable processes, preserve project continuity, and create a durable personal operating method.",
        [30, 31, 32, 33, 34, 36],
    ),
]

REFERENCE_GROUPS = [
    ("Decide and plan", ["ai-use-decision-guide", "core-workflow"]),
    ("Prompt and collaborate", ["core-prompt-pattern", "project-handoff-template"]),
    ("Verify and review", ["output-review-checklist", "verification-ladder"]),
    ("Protect information", ["privacy-before-sharing"]),
    ("Look up a term", ["glossary"]),
]


def title_from_markdown(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return re.sub(r"^#\s+", "", line).strip()
    return path.stem.replace("-", " ").title()


def learner_lesson_title(path: Path) -> str:
    title = title_from_markdown(path)
    return re.sub(r"^Lesson\s+\d+\s+[—-]\s+", "", title).strip()


def reading_time(markdown_text: str) -> int:
    text = re.sub(r"<[^>]+>", " ", markdown_text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    words = re.findall(r"\b[\w’'-]+\b", text)
    return max(1, round(len(words) / 210))


def plain_summary(markdown_text: str, limit: int = 190) -> str:
    text = re.sub(r"```.*?```", " ", markdown_text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[#>*_`\[\]()\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


def render_page(
    title: str,
    body: str,
    nav: str,
    depth: int,
    *,
    page_id: str = "",
    page_kind: str = "content",
    reading_minutes: int | None = None,
    page_label: str | None = None,
    description: str = SITE_DESCRIPTION,
) -> str:
    prefix = "../" * depth
    progress_control = ""
    if page_kind in {"lesson", "practice", "capstone"}:
        labels = {
            "lesson": ("I can do this", "I can do this ✓"),
            "practice": ("I completed this task", "Task completed ✓"),
            "capstone": ("I completed the capstone", "Capstone completed ✓"),
        }
        incomplete, complete = labels[page_kind]
        progress_control = (
            '<button class="completion-button" type="button" '
            f'data-completion-toggle data-label-incomplete="{incomplete}" '
            f'data-label-complete="{complete}" aria-pressed="false">{incomplete}</button>'
        )
    kind_labels = {
        "lesson": "Lesson",
        "practice": "Applied practice",
        "assessment": "Readiness check",
        "reference": "Reference tool",
        "overview": "Module overview",
        "capstone": "Capstone",
        "module": "Module",
        "start": "Orientation",
        "outcomes": "Learning map",
        "completion": "Completion summary",
    }
    meta_bits = []
    if page_label:
        meta_bits.append(page_label)
    elif page_kind in kind_labels:
        meta_bits.append(kind_labels[page_kind])
    if reading_minutes and page_kind in {"lesson", "practice", "reference", "overview", "capstone", "start"}:
        meta_bits.append(f"About {reading_minutes} min")
    page_meta = ""
    if meta_bits:
        page_meta = '<p class="page-meta" aria-label="Page details">' + "<span>·</span>".join(
            f"<span>{html.escape(bit)}</span>" for bit in meta_bits
        ) + "</p>"

    study_tools = ""
    if page_id and page_kind in {"lesson", "practice", "capstone", "assessment", "reference", "overview"}:
        study_tools = f'''
<section class="study-tools" aria-labelledby="study-tools-heading">
  <div class="study-tools-header">
    <div>
      <p class="eyebrow">Private workspace</p>
      <h2 id="study-tools-heading">Save this page</h2>
    </div>
    <button class="bookmark-button" type="button" data-bookmark-toggle aria-pressed="false">Bookmark page</button>
  </div>
  <label for="page-note">My notes</label>
  <textarea id="page-note" rows="6" placeholder="Capture a useful idea, question, or next step. Notes stay in this browser."></textarea>
  <p id="note-status" class="muted" role="status" aria-live="polite"></p>
</section>'''
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="theme-color" content="#176571">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Practical AI Learning">
<title>{html.escape(title)} | Practical AI Learning</title>
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body data-page-id="{html.escape(page_id)}" data-page-kind="{html.escape(page_kind)}" data-page-title="{html.escape(title)}">
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="topbar">
  <a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">AI</span><span>Practical AI Learning</span></a>
  <div class="topbar-actions">
    <a class="search-link" href="{prefix}search.html">Search</a>
    <button id="nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false">Menu</button>
  </div>
</header>
<div class="layout">
<nav id="sidebar" class="sidebar" aria-label="Program navigation">{nav}</nav>
<main id="main-content" class="content" tabindex="-1">
  <article>
    {page_meta}
    {body}
  </article>
  {study_tools}
  {progress_control}
  <footer class="site-footer">
    <p>Practical AI Learning · Private, local-first self-study</p>
    <p><a href="{prefix}start.html">Start Here</a> · <a href="{prefix}progress.html">My Progress</a> · <a href="{prefix}reference/index.html">Reference Library</a></p>
  </footer>
</main>
</div>
<script src="{prefix}assets/search-index.js"></script>
<script src="{prefix}assets/site.js"></script>
</body>
</html>"""


def build_nav() -> str:
    primary = [
        ('Home', '/index.html'),
        ('Continue Learning', '/index.html#continue-learning'),
        ('Practice', '/practice/index.html'),
        ('Progress', '/progress.html'),
        ('Reference', '/reference/index.html'),
    ]
    items = [f'<div class="nav-item"><a href="{href}">{label}</a></div>' for label, href in primary[:2]]
    module_links = ''.join(
        f'<div class="nav-item nav-module"><a href="/modules/module-{num:02d}/index.html">Module {num}: {html.escape(name)}</a></div>'
        for num, name in MODULE_NAMES.items()
    )
    items.append(
        '<details class="nav-modules"><summary>Modules</summary><div class="nav-module-list">'
        + module_links
        + '</div></details>'
    )
    items.extend(f'<div class="nav-item"><a href="{href}">{label}</a></div>' for label, href in primary[2:])
    return ''.join(items).replace('href="/', 'href="__ROOT__')


def relative_nav(nav: str, depth: int) -> str:
    prefix = "../" * depth
    return nav.replace("__ROOT__", prefix)


def write_page(
    out_path: Path,
    title: str,
    markdown_text: str,
    nav: str,
    *,
    page_id: str = "",
    page_kind: str = "content",
    searchable: bool = True,
    page_label: str | None = None,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    depth = len(out_path.relative_to(OUT).parents) - 1
    body = markdown(markdown_text)
    minutes = reading_time(markdown_text)
    out_path.write_text(
        render_page(
            title,
            body,
            relative_nav(nav, depth),
            depth,
            page_id=page_id,
            page_kind=page_kind,
            reading_minutes=minutes,
            page_label=page_label,
            description=plain_summary(markdown_text, 160) or SITE_DESCRIPTION,
        ),
        encoding="utf-8",
    )
    if searchable:
        SEARCH_ITEMS.append(
            {
                "id": page_id,
                "title": title,
                "url": out_path.relative_to(OUT).as_posix(),
                "summary": plain_summary(markdown_text),
                "kind": page_kind,
            }
        )



def activity_field_html(field: dict, field_id: str, response_key: str) -> str:
    label = html.escape(str(field["label"]))
    required = " data-required=\"true\"" if field.get("required") else ""
    field_type = str(field.get("type", "text"))
    if field_type == "select":
        options = []
        for index, option in enumerate(field.get("options", [])):
            value = "" if index == 0 else str(option)
            options.append(f'<option value="{html.escape(value)}">{html.escape(str(option))}</option>')
        control = f'<select id="{field_id}" data-activity-input data-response-key="{response_key}"{required}>' + "".join(options) + "</select>"
    elif field_type == "textarea":
        rows = 8 if field.get("large") else 4
        control = f'<textarea id="{field_id}" rows="{rows}" data-activity-input data-response-key="{response_key}"{required} placeholder="Type your response here…"></textarea>'
    else:
        control = f'<input id="{field_id}" type="text" data-activity-input data-response-key="{response_key}"{required} placeholder="Type your response here…">'
    return f'<div class="activity-field"><label for="{field_id}">{label}</label>{control}</div>'


def activity_markup(record: dict) -> str:
    module_num = int(record["module"])
    activity_id = f"module-{module_num:02d}-activity"
    lines = [
        '<section class="interactive-activity" data-interactive-activity ',
        f'data-activity-id="{activity_id}" aria-labelledby="{activity_id}-heading">',
        '<div class="activity-heading">',
        '<div>',
        '<p class="eyebrow">Interactive worksheet</p>',
        f'<h2 id="{activity_id}-heading">{html.escape(str(record["title"]))}</h2>',
        f'<p>{html.escape(str(record["intro"]))}</p>',
        '</div>',
        '<div class="activity-meter" aria-live="polite"><strong data-activity-count>0 of 0</strong><span>responses completed</span></div>',
        '</div>',
        '<div class="activity-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span data-activity-progress></span></div>',
    ]
    challenge = record.get("challenge")
    if challenge:
        lines.extend([
            '<section class="activity-challenge" data-activity-challenge>',
            '<div class="activity-challenge-heading">',
            '<p class="eyebrow">Decision check</p>',
            f'<h3>{html.escape(str(challenge["prompt"]))}</h3>',
            '</div>',
            '<div class="activity-choice-list">',
        ])
        for option_index, option in enumerate(challenge.get("options", [])):
            choice_id = f'{activity_id}-challenge-{option_index + 1}'
            lines.append(
                f'<label class="activity-choice" for="{choice_id}"><input id="{choice_id}" type="radio" name="{activity_id}-challenge" value="{option_index}" data-challenge-choice> <span>{html.escape(str(option))}</span></label>'
            )
        lines.extend([
            '</div>',
            f'<button class="challenge-check-button" type="button" data-challenge-check data-answer="{int(challenge["answer"])}">Check decision</button>',
            f'<p class="challenge-feedback" data-challenge-feedback data-explanation="{html.escape(str(challenge["explanation"]), quote=True)}" role="status" aria-live="polite"></p>',
            '</section>',
        ])
    repeat = record.get("repeat")
    if repeat:
        for item_index, item in enumerate(repeat.get("items", []), start=1):
            lines.extend([
                '<fieldset class="activity-scenario">',
                f'<legend><span>{item_index}</span>{html.escape(str(item))}</legend>',
                '<div class="activity-fields">',
            ])
            for field in repeat.get("fields", []):
                key = f'item-{item_index}-{field["key"]}'
                field_id = f'{activity_id}-{key}'
                lines.append(activity_field_html(field, field_id, key))
            lines.extend(['</div>', '</fieldset>'])
    else:
        lines.append('<div class="activity-fields activity-fields-single">')
        for field in record.get("fields", []):
            key = str(field["key"])
            field_id = f'{activity_id}-{key}'
            lines.append(activity_field_html(field, field_id, key))
        lines.append('</div>')
    lines.extend([
        '<div class="activity-actions">',
        '<button type="button" data-activity-review>Review completion</button>',
        '<button type="button" class="secondary-button" data-activity-clear>Clear worksheet</button>',
        '</div>',
        '<p class="activity-status muted" data-activity-status role="status" aria-live="polite">Responses save automatically in this browser.</p>',
        '</section>',
    ])
    return "\n".join(lines)


def capstone_workbook_markup() -> str:
    fields = [
        ("project", "Project and intended result", "What meaningful project will you complete, and what usable result should exist at the end?"),
        ("role", "AI role and human control", "What will AI help with, and which judgments or actions will remain yours?"),
        ("evidence", "Evidence and constraints", "What sources, facts, limits, privacy rules, or current information must guide the work?"),
        ("stages", "Work stages", "List the few stages you will use so important decisions can be reviewed before later work depends on them."),
        ("verification", "Verification plan", "How will you check accuracy, completeness, usefulness, and risk?"),
        ("delivery", "Delivery and preservation", "Who will use the result, what makes it ready, and what brief record or reusable asset should be kept?"),
        ("reflection", "Reflection", "What did AI improve, what did it weaken, and where was human judgment essential?"),
    ]
    lines = [
        '<section class="capstone-workbook" data-capstone-workbook aria-labelledby="capstone-workbook-heading">',
        '<div class="activity-heading"><div><p class="eyebrow">Capstone planner</p><h2 id="capstone-workbook-heading">Plan the project before you build it</h2><p>Keep this concise. The planner saves in this browser and gives you one place to hold the decisions that matter.</p></div>',
        '<div class="activity-meter"><strong data-capstone-count>0 of 7</strong><span>planning responses completed</span></div></div>',
        '<div class="activity-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span data-capstone-progress></span></div>',
        '<div class="activity-fields activity-fields-single">',
    ]
    for key, label, prompt in fields:
        field_id = f"capstone-{key}"
        lines.append(f'<div class="activity-field"><label for="{field_id}">{html.escape(label)}</label><p class="field-help">{html.escape(prompt)}</p><textarea id="{field_id}" rows="4" data-capstone-input data-response-key="{key}"></textarea></div>')
    lines.extend([
        '</div>',
        '<div class="activity-actions"><button type="button" data-capstone-review>Review plan</button></div>',
        '<p class="activity-status muted" data-capstone-status role="status" aria-live="polite">Responses save automatically in this browser.</p>',
        '</section>',
    ])
    return "\n".join(lines)


def assessment_markdown(record: dict) -> str:
    module_num = int(record["module"])
    lines = [
        f'# {record["title"]}',
        '',
        str(record["intro"]),
        '',
        'Choose one answer for each scenario, then submit the check. Explanations appear after each attempt, your latest result is saved, and a perfect score marks the check complete.',
        '',
        f'<form class="knowledge-check" data-assessment-form data-assessment-id="module-{module_num:02d}-readiness-check">',
    ]
    for q_index, question in enumerate(record["questions"]):
        lines.extend([
            f'<fieldset class="assessment-question" data-question data-answer="{int(question["answer"])}">',
            f'<legend>{q_index + 1}. {html.escape(str(question["prompt"]))}</legend>',
        ])
        for option_index, option in enumerate(question["options"]):
            input_id = f'm{module_num:02d}-q{q_index + 1}-o{option_index + 1}'
            lines.append(
                f'<label for="{input_id}"><input id="{input_id}" type="radio" name="question-{q_index + 1}" value="{option_index}"> {html.escape(str(option))}</label>'
            )
        lines.extend([
            f'<p class="assessment-explanation" data-explanation hidden>{html.escape(str(question["explanation"]))}</p>',
            '</fieldset>',
        ])
    lines.extend([
        '<button class="assessment-submit" type="submit">Check my answers</button>',
        '<p class="assessment-result" data-assessment-result role="status" aria-live="polite"></p>',
        '</form>',
        '',
        f'[Return to Module {module_num}](../modules/module-{module_num:02d}/index.html)',
    ])
    return "\n".join(lines)

def outcomes_page(sequence: list[tuple[int, Path]]) -> str:
    by_number: dict[int, tuple[int, Path]] = {}
    for module_num, lesson in sequence:
        match = re.search(r"lesson-(\d+)", lesson.stem)
        if match:
            by_number[int(match.group(1))] = (module_num, lesson)

    sections = [
        "# Learning Outcomes",
        "",
        "Use this map when you want to learn toward a practical capability rather than browse the course module by module. The links point to the same canonical lessons; no content is duplicated.",
        "",
        '<div class="outcome-grid">',
    ]
    for title, description, lesson_numbers in LEARNING_OUTCOMES:
        sections.extend([
            '<section class="outcome-card">',
            f"<h2>{html.escape(title)}</h2>",
            f"<p>{html.escape(description)}</p>",
            "<ul>",
        ])
        for number in lesson_numbers:
            module_num, lesson = by_number[number]
            lesson_title = learner_lesson_title(lesson)
            url = f"modules/module-{module_num:02d}/{lesson.with_suffix('.html').name}"
            sections.append(f'<li><a href="{url}">{html.escape(lesson_title)}</a></li>')
        sections.extend(["</ul>", "</section>"])
    sections.extend([
        "</div>",
        "",
        "## Recommended use",
        "",
        "Complete the twelve modules in order on your first pass. Return to this map later when a real task reveals a specific capability you want to strengthen.",
    ])
    return "\n".join(sections)


def module_page(module_num: int, lesson_paths: list[Path]) -> str:
    lesson_cards = []
    for position, lesson in enumerate(lesson_paths, start=1):
        title = learner_lesson_title(lesson)
        lesson_cards.append(
            '<a class="module-step" href="' + lesson.name.replace('.md', '.html') + '">'
            f'<span class="module-step-number">{position}</span>'
            f'<span><strong>Lesson {position} of {len(lesson_paths)}</strong><small>{html.escape(title)}</small></span>'
            '</a>'
        )
    return "\n".join([
        f"# Module {module_num}: {MODULE_NAMES[module_num]}",
        "",
        '<p class="module-intro">Start with the overview, complete the three lessons in order, then use the task and readiness check to apply what you learned.</p>',
        '<div class="module-step-grid">',
        '<a class="module-step module-step-overview" href="overview.html"><span class="module-step-number">0</span><span><strong>Module overview</strong><small>Purpose, prerequisites, and expected result</small></span></a>',
        *lesson_cards,
        '</div>',
        '<section class="module-finish" aria-labelledby="module-finish-heading">',
        '<p class="eyebrow">Complete the module</p>',
        '<h2 id="module-finish-heading">Practice, then check readiness</h2>',
        '<div class="module-finish-actions">',
        f'<a href="../../practice/module-{module_num:02d}-completion-task.html"><strong>Applied task</strong><span>Use the skill in a realistic scenario.</span></a>',
        f'<a href="../../assessments/module-{module_num:02d}-readiness-check.html"><strong>Readiness check</strong><span>Confirm that you can recognize sound judgment.</span></a>',
        '</div>',
        '</section>',
    ])


def practice_hub_page() -> str:
    assessment_by_module = {int(record["module"]): record for record in ASSESSMENTS}
    cards = []
    for module_num in range(1, 13):
        task = ROOT / "practice" / f"module-{module_num:02d}-completion-task.md"
        task_title = title_from_markdown(task)
        check_title = str(assessment_by_module[module_num]["title"])
        cards.append(
            '<section class="practice-module-card">'
            f'<p class="eyebrow">Module {module_num}</p>'
            f'<h2>{html.escape(MODULE_NAMES[module_num])}</h2>'
            '<div class="practice-module-links">'
            f'<a href="{task.with_suffix(".html").name}"><strong>Applied task</strong><span>{html.escape(task_title)}</span></a>'
            f'<a href="../assessments/module-{module_num:02d}-readiness-check.html"><strong>Readiness check</strong><span>{html.escape(check_title)}</span></a>'
            '</div>'
            '</section>'
        )
    return "\n".join([
        "# Practice",
        "",
        "Use each module task after its three lessons, then complete the readiness check. These activities measure practical judgment rather than memorized terminology.",
        "",
        '<div class="practice-module-grid">',
        *cards,
        '</div>',
        '<section class="practice-capstone">',
        '<p class="eyebrow">Final application</p>',
        '<h2>Complete a real AI-assisted project</h2>',
        '<p>Use the capstone after all twelve modules to plan, produce, verify, and preserve one meaningful piece of work.</p>',
        '<p><a class="primary-action" href="../capstone/capstone-project.html">Open the capstone</a></p>',
        '</section>',
    ])


def simplify_lesson_markdown(text: str) -> str:
    text = re.sub(r"^#\s+Lesson\s+\d+\s+[—-]\s+", "# ", text, count=1, flags=re.M)
    replacements = {
        '## Outcome': '## What you will be able to do',
        '## Direct answer': '## The key idea',
        '## Worked example': '## Example',
        '## Guided practice': '## Try it',
        '## Independent application': '### Apply it',
        '## Completion check': '## Check yourself',
        '## Best practice': '**Best practice**',
        '## Common failure': '**Watch for this**',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def lesson_check_markup(lesson_number: int) -> str:
    record = LESSON_CHECKS.get(lesson_number)
    if not record:
        return ""
    check_id = f"lesson-check-{lesson_number:02d}"
    parts = [
        f'<section class="lesson-check" data-lesson-check data-check-id="{check_id}" data-answer="{int(record["answer"])}">',
        '<p class="eyebrow">Pause and decide</p>',
        f'<h2>{html.escape(str(record["prompt"]))}</h2>',
        '<div class="lesson-check-options">',
    ]
    for index, option in enumerate(record.get("options", [])):
        option_id = f"{check_id}-option-{index}"
        parts.append(
            f'<label class="lesson-check-option" for="{option_id}"><input id="{option_id}" type="radio" name="{check_id}" value="{index}"> <span>{html.escape(str(option))}</span></label>'
        )
    parts.extend([
        '</div>',
        '<button type="button" data-lesson-check-submit>Check my answer</button>',
        f'<p class="lesson-check-feedback" data-lesson-check-feedback data-explanation="{html.escape(str(record["explanation"]), quote=True)}" role="status" aria-live="polite"></p>',
        '</section>',
    ])
    return "\n".join(parts)


def lesson_sequence() -> list[tuple[int, Path]]:
    sequence: list[tuple[int, Path]] = []
    for module_num in range(1, 13):
        folder = ROOT / "modules" / f"module-{module_num:02d}"
        lessons = sorted(
            folder.glob("lesson-*.md"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        )
        sequence.extend((module_num, lesson) for lesson in lessons)
    return sequence


def lesson_nav_markdown(index: int, sequence: list[tuple[int, Path]]) -> str:
    module_num, lesson = sequence[index]
    links: list[str] = []
    if index > 0:
        prev_module, prev_lesson = sequence[index - 1]
        rel = Path("..") / f"module-{prev_module:02d}" / prev_lesson.with_suffix(".html").name
        links.append(f"[← Previous: {learner_lesson_title(prev_lesson)}]({rel.as_posix()})")
    links.append(f"[Module {module_num} home](index.html)")
    if index + 1 < len(sequence) and sequence[index + 1][0] == module_num:
        next_module, next_lesson = sequence[index + 1]
        rel = Path("..") / f"module-{next_module:02d}" / next_lesson.with_suffix(".html").name
        links.append(f"[Next: {learner_lesson_title(next_lesson)} →]({rel.as_posix()})")
    else:
        links.append(
            f"[Continue to the Module {module_num} completion task →]"
            f"(../../practice/module-{module_num:02d}-completion-task.html)"
        )
    return "\n\n---\n\n<div class=\"lesson-navigation\">" + " · ".join(links) + "</div>"


def main() -> None:
    SEARCH_ITEMS.clear()
    MILESTONE_ITEMS.clear()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy2(STATIC / "site.css", OUT / "assets" / "site.css")
    shutil.copy2(STATIC / "site.js", OUT / "assets" / "site.js")
    shutil.copy2(STATIC / "favicon.svg", OUT / "assets" / "favicon.svg")
    nav = build_nav()

    home = """<section class="home-hero">
<p class="eyebrow">Practical, platform-neutral self-study</p>
<h1>Learn to use AI with clear judgment</h1>
<p class="home-lede">Build practical skill in defining tasks, guiding conversations, checking important claims, protecting sensitive information, and turning good work into repeatable workflows.</p>
<div class="hero-actions">
<a class="primary-action" href="start.html">Start the program</a>
<a class="secondary-action" href="modules/module-01/index.html">Open Module 1</a>
</div>
<div class="course-facts" aria-label="Program facts">
<span><strong>12</strong> modules</span>
<span><strong>36</strong> focused lessons</span>
<span><strong>Local</strong> progress and notes</span>
</div>
</section>

<section class="home-path" aria-labelledby="home-path-heading">
<p class="eyebrow">How the course works</p>
<h2 id="home-path-heading">Learn, practice, verify, apply</h2>
<div class="home-stage-grid">
<div><span>1</span><strong>Learn</strong><p>Read one focused lesson and make a decision.</p></div>
<div><span>2</span><strong>Practice</strong><p>Use the skill in a short applied worksheet.</p></div>
<div><span>3</span><strong>Verify</strong><p>Pass a realistic readiness check.</p></div>
<div><span>4</span><strong>Apply</strong><p>Complete a real capstone project.</p></div>
</div>
</section>

<section aria-labelledby="home-outcomes-heading">
<p class="eyebrow">What you will be able to do</p>
<h2 id="home-outcomes-heading">Work with AI without surrendering judgment</h2>
<ul class="home-outcome-list">
<li>Choose when AI is useful and when another approach is safer.</li>
<li>Define outcomes, context, constraints, examples, and formats clearly.</li>
<li>Research, verify, and preserve uncertainty when facts matter.</li>
<li>Use AI for writing, planning, learning, files, images, and current information.</li>
<li>Build reusable workflows while keeping responsibility human.</li>
</ul>
<p><a href="outcomes.html">Explore the full learning-outcomes map</a></p>
</section>

<div id="continue-learning" class="continue-learning" aria-live="polite"></div>
"""
    write_page(OUT / "index.html", "Practical AI Learning", home, nav, page_kind="home")

    start_parts = [
        "# Start Here",
        "",
        "Use this orientation once before beginning Module 1. Your answers and progress stay in this browser.",
    ]
    for path in sorted((ROOT / "site" / "start-here").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^#\s+", "## ", text, count=1, flags=re.M)
        start_parts.append(text)
    write_page(
        OUT / "start.html",
        "Start Here",
        "\n\n---\n\n".join(start_parts),
        nav,
        page_kind="start",
    )

    progress_md = """# My Progress

This page shows completed lessons, applied tasks, readiness checks, and the capstone in this browser.

<div id="next-recommended-step" class="continue-learning" aria-live="polite"></div>

<div id="progress-dashboard" class="progress-dashboard" aria-live="polite"></div>

<div class="progress-actions">
<button id="export-progress" type="button">Export progress</button>
<button id="import-progress" type="button">Import progress</button>
<input id="import-progress-file" type="file" accept="application/json,.json" hidden>
<button id="reset-progress" type="button">Reset progress</button>
</div>
<p id="progress-status" class="muted" role="status" aria-live="polite"></p>

## Saved work

[Open saved notes and bookmarks](workspace.html)

## How progress works

Use the “I can do this” or completion button at the bottom of lessons, module tasks, and the capstone. Progress is stored locally in the browser and is not sent anywhere. Clearing browser storage will reset it.
"""
    write_page(
        OUT / "progress.html",
        "My Progress",
        progress_md,
        nav,
        page_kind="progress",
        searchable=False,
    )

    workspace_md = """# My Workspace

Bookmarks and notes saved from lessons, practice tasks, overviews, the capstone, and reference pages appear here. Everything stays in this browser unless you export your learning data.

<div id="workspace-dashboard" class="workspace-dashboard" aria-live="polite"></div>

<div class="progress-actions">
<button id="clear-workspace" type="button">Clear bookmarks and notes</button>
</div>
<p id="workspace-status" class="muted" role="status" aria-live="polite"></p>
"""
    write_page(
        OUT / "workspace.html",
        "My Workspace",
        workspace_md,
        nav,
        page_kind="workspace",
        searchable=False,
    )

    sequence = lesson_sequence()
    write_page(
        OUT / "outcomes.html",
        "Learning Outcomes",
        outcomes_page(sequence),
        nav,
        page_kind="outcomes",
    )

    lesson_records: list[dict[str, str | int]] = []
    for index, (module_num, lesson) in enumerate(sequence):
        lesson_id = f"module-{module_num:02d}-{lesson.stem}"
        lesson_records.append(
            {
                "id": lesson_id,
                "title": learner_lesson_title(lesson),
                "module": module_num,
                "url": f"modules/module-{module_num:02d}/{lesson.with_suffix('.html').name}",
            }
        )

    for module_num in range(1, 13):
        folder = ROOT / "modules" / f"module-{module_num:02d}"
        lessons = sorted(
            folder.glob("lesson-*.md"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        )
        module_out = OUT / "modules" / f"module-{module_num:02d}"
        write_page(
            module_out / "index.html",
            f"Module {module_num}: {MODULE_NAMES[module_num]}",
            module_page(module_num, lessons),
            nav,
            page_kind="module",
        )
        overview = folder / "module-overview.md"
        if overview.exists():
            write_page(
                module_out / "overview.html",
                title_from_markdown(overview),
                overview.read_text(encoding="utf-8"),
                nav,
                page_id=f"module-{module_num:02d}-overview",
                page_kind="overview",
            )

    module_positions: dict[int, int] = {}
    for index, (module_num, lesson) in enumerate(sequence):
        module_positions[module_num] = module_positions.get(module_num, 0) + 1
        local_position = module_positions[module_num]
        module_out = OUT / "modules" / f"module-{module_num:02d}"
        lesson_number = int(re.search(r"(\d+)", lesson.stem).group(1))
        lesson_text = simplify_lesson_markdown(lesson.read_text(encoding="utf-8")) + "\n\n" + lesson_check_markup(lesson_number) + lesson_nav_markdown(index, sequence)
        lesson_id = f"module-{module_num:02d}-{lesson.stem}"
        write_page(
            module_out / lesson.with_suffix(".html").name,
            learner_lesson_title(lesson),
            lesson_text,
            nav,
            page_id=lesson_id,
            page_kind="lesson",
            page_label=f"Lesson {local_position} of 3",
        )

    practice_paths = sorted((ROOT / "practice").glob("*.md"))
    for path in practice_paths:
        match = re.search(r"module-(\d+)", path.stem)
        module_num = int(match.group(1)) if match else 0
        task_id = f"module-{module_num:02d}-completion-task"
        title = title_from_markdown(path)
        url = f"practice/{path.with_suffix('.html').name}"
        MILESTONE_ITEMS.append(
            {"id": task_id, "title": title, "module": module_num, "url": url, "kind": "practice"}
        )
        activity = ACTIVITIES.get(module_num)
        interactive = "\n\n" + activity_markup(activity) if activity else ""
        task_text = path.read_text(encoding="utf-8") + interactive + (
            "\n\n---\n\n<div class=\"lesson-navigation\">"
            f"[Module {module_num} home](../modules/module-{module_num:02d}/index.html) · "
            f"[Continue to the readiness check →](../assessments/module-{module_num:02d}-readiness-check.html)"
            "</div>"
        )
        write_page(
            OUT / "practice" / path.with_suffix(".html").name,
            title,
            task_text,
            nav,
            page_id=task_id,
            page_kind="practice",
        )
    for record in ASSESSMENTS:
        module_num = int(record["module"])
        title = str(record["title"])
        assessment_id = f"module-{module_num:02d}-readiness-check"
        url = f"assessments/{assessment_id}.html"
        MILESTONE_ITEMS.append(
            {"id": assessment_id, "title": title, "module": module_num, "url": url, "kind": "assessment"}
        )
        if module_num < 12:
            continuation = (
                "\n\n---\n\n<div class=\"lesson-navigation\">"
                f"[Module {module_num} home](../modules/module-{module_num:02d}/index.html) · "
                f"[Continue to Module {module_num + 1} →](../modules/module-{module_num + 1:02d}/index.html)"
                "</div>"
            )
        else:
            continuation = (
                "\n\n---\n\n<div class=\"lesson-navigation\">"
                "[Module 12 home](../modules/module-12/index.html) · "
                "[Continue to the capstone →](../capstone/capstone-project.html)"
                "</div>"
            )
        write_page(
            OUT / "assessments" / f"{assessment_id}.html",
            title,
            assessment_markdown(record) + continuation,
            nav,
            page_id=assessment_id,
            page_kind="assessment",
        )

    write_page(
        OUT / "practice" / "index.html",
        "Practice",
        practice_hub_page(),
        nav,
        page_kind="practice-index",
    )

    refs = sorted((ROOT / "reference").glob("*.md"))
    refs_by_stem = {path.stem: path for path in refs}
    ref_index = [
        "# Reference Library",
        "",
        "Open the group that matches what you are trying to do. Each tool has one canonical home and can be bookmarked or annotated in your private workspace.",
    ]
    listed_stems: set[str] = set()
    for group_title, stems in REFERENCE_GROUPS:
        ref_index.extend(["", f"## {group_title}"])
        for stem in stems:
            path = refs_by_stem[stem]
            listed_stems.add(stem)
            title = title_from_markdown(path)
            ref_index.append(f"- [{title}]({path.with_suffix('.html').name})")
    for path in refs:
        title = title_from_markdown(path)
        write_page(
            OUT / "reference" / path.with_suffix(".html").name,
            title,
            path.read_text(encoding="utf-8"),
            nav,
            page_id=f"reference-{path.stem}",
            page_kind="reference",
        )
    ungrouped = [path for path in refs if path.stem not in listed_stems]
    if ungrouped:
        ref_index.extend(["", "## Additional tools"])
        for path in ungrouped:
            ref_index.append(f"- [{title_from_markdown(path)}]({path.with_suffix('.html').name})")
    write_page(
        OUT / "reference" / "index.html",
        "Reference Library",
        "\n".join(ref_index),
        nav,
        page_kind="reference-index",
    )

    capstone = ROOT / "capstone" / "capstone-project.md"
    capstone_id = "capstone-project"
    capstone_title = title_from_markdown(capstone)
    MILESTONE_ITEMS.append(
        {"id": capstone_id, "title": capstone_title, "module": 13, "url": "capstone/capstone-project.html", "kind": "capstone"}
    )
    write_page(
        OUT / "capstone" / "capstone-project.html",
        capstone_title,
        capstone.read_text(encoding="utf-8") + "\n\n" + capstone_workbook_markup() + "\n\n---\n\n[Review your overall progress](../progress.html)",
        nav,
        page_id=capstone_id,
        page_kind="capstone",
    )

    completion_md = """# Course Completion

This page provides a personal completion summary for the self-study program. It is not an accredited credential.

<div class="completion-summary" data-completion-summary aria-live="polite"></div>

<div class="completion-actions">
<button id="print-completion" type="button" hidden>Print or save as PDF</button>
<a href="progress.html">Return to My Progress</a>
</div>
"""
    write_page(
        OUT / "completion.html",
        "Course Completion",
        completion_md,
        nav,
        page_kind="completion",
        searchable=False,
    )

    search_md = """# Search

Find canonical lessons and reference tools by topic, task, or practical skill.

<label class="search-label" for="site-search">Search lessons and reference tools</label>
<input id="site-search" class="site-search" type="search" placeholder="Try: verification, context, privacy…" autocomplete="off">
<div id="search-results" class="search-results" aria-live="polite"></div>
"""
    write_page(
        OUT / "search.html",
        "Search",
        search_md,
        nav,
        page_kind="search",
        searchable=False,
    )

    guided_path: list[dict[str, str | int]] = []
    for module_num in range(1, 13):
        guided_path.extend(item for item in lesson_records if item["module"] == module_num)
        task = next(
            item for item in MILESTONE_ITEMS
            if item["kind"] == "practice" and item["module"] == module_num
        )
        check = next(
            item for item in MILESTONE_ITEMS
            if item["kind"] == "assessment" and item["module"] == module_num
        )
        guided_path.extend([task, check])
    guided_path.extend(item for item in MILESTONE_ITEMS if item["kind"] == "capstone")

    search_payload = "window.PRACTICAL_AI_SEARCH_INDEX = " + json.dumps(
        SEARCH_ITEMS, ensure_ascii=False
    ) + ";\nwindow.PRACTICAL_AI_LESSONS = " + json.dumps(
        lesson_records, ensure_ascii=False
    ) + ";\nwindow.PRACTICAL_AI_MILESTONES = " + json.dumps(
        MILESTONE_ITEMS, ensure_ascii=False
    ) + ";\nwindow.PRACTICAL_AI_GUIDED_PATH = " + json.dumps(
        guided_path, ensure_ascii=False
    ) + ";\n"
    (OUT / "assets" / "search-index.js").write_text(search_payload, encoding="utf-8")

    # GitHub Pages publishes this directory directly. The marker prevents Jekyll
    # from altering generated assets or ignoring future underscore-prefixed paths.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # GitHub Pages serves this file for unknown routes. The home link is
    # calculated for both project sites and custom domains without forcing an
    # automatic redirect that could hide the error from the learner.
    not_found = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#176571">
<title>Page not found | Practical AI Learning</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; background: #f4f6f5; color: #182126; font: 16px/1.6 system-ui, sans-serif; }
  main { width: min(620px, 100%); padding: clamp(28px, 7vw, 56px); border: 1px solid #d9e0df; border-radius: 18px; background: #fff; box-shadow: 0 18px 50px rgba(22, 42, 48, .08); }
  h1 { margin: 0 0 .5rem; line-height: 1.15; font-size: clamp(2rem, 8vw, 3.4rem); }
  p { max-width: 55ch; }
  a { display: inline-block; margin-top: .6rem; padding: 11px 16px; border-radius: 9px; background: #176571; color: #fff; font-weight: 700; text-decoration: none; }
  a:focus-visible { outline: 3px solid rgba(23, 101, 113, .3); outline-offset: 3px; }
  .skip-link { position: fixed; left: 16px; top: 10px; transform: translateY(-160%); }
  .skip-link:focus { transform: translateY(0); }
  .site-footer { margin-top: 1.4rem; color: #5f6d74; font-size: .88rem; }
</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<main id="main-content">
  <p><strong>Practical AI Learning</strong></p>
  <h1>Page not found</h1>
  <p>The address may have changed, or the page may no longer exist. Return to the course home page and continue from there.</p>
  <a id="home-link" href="./">Return to course home</a>
  <footer class="site-footer"><p>Practical AI Learning</p></footer>
</main>
<script>
(function () {
  var isGitHubPages = window.location.hostname.endsWith('.github.io');
  var segments = window.location.pathname.split('/').filter(Boolean);
  var rootPath = isGitHubPages && segments.length ? '/' + segments[0] + '/' : '/';
  document.getElementById('home-link').href = window.location.origin + rootPath;
}());
</script>
</body>
</html>
"""
    (OUT / "404.html").write_text(not_found, encoding="utf-8")

    print(f"Built site at {OUT} ({len(SEARCH_ITEMS)} searchable pages)")


if __name__ == "__main__":
    main()
