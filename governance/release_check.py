from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT.parent / "ai-learning-platform-working.zip"


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def verify_release_documentation() -> None:
    audit_numbers = []
    for path in (ROOT / "governance").glob("release-audit-pass-*.md"):
        match = re.search(r"pass-(\d+)$", path.stem)
        if match:
            audit_numbers.append(int(match.group(1)))
    if not audit_numbers:
        raise RuntimeError("No numbered release-audit document found")

    latest = max(audit_numbers)
    current_path = ROOT / "governance" / "current-release.md"
    first_line = current_path.read_text(encoding="utf-8").splitlines()[0]
    if f"Pass {latest}" not in first_line:
        raise RuntimeError(
            f"Current release documentation is stale: latest audit is Pass {latest}, "
            f"but current-release.md begins with {first_line!r}"
        )
    print(f"RELEASE DOCUMENTATION PASSED: current-release.md matches Pass {latest}")


def main() -> None:
    verify_release_documentation()
    run(sys.executable, "governance/content-audit.py")
    run(sys.executable, "governance/generated-consistency.py")
    run(sys.executable, "site/build_site.py")
    run(sys.executable, "governance/site-audit.py")
    run(
        sys.executable,
        "-m",
        "py_compile",
        "governance/content-audit.py",
        "governance/site-audit.py",
        "governance/browser-audit.py",
        "governance/release_check.py",
        "governance/generated-consistency.py",
        "site/build_site.py",
    )
    node = shutil.which("node")
    if node:
        run(node, "--check", "site/static/site.js")
        run(node, "--check", "site/generated/assets/site.js")
    else:
        print("SKIP: Node.js is unavailable; JavaScript syntax check not run.")

    if DIST.exists():
        DIST.unlink()
    with zipfile.ZipFile(DIST, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, Path(ROOT.name) / path.relative_to(ROOT))

    with zipfile.ZipFile(DIST) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP integrity check failed at {bad}")
        if not archive.namelist():
            raise RuntimeError("ZIP archive is empty")

    print(f"RELEASE CHECK PASSED: {DIST}")


if __name__ == "__main__":
    main()
