from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT.parent / "ai-learning-platform-working.zip"


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run(sys.executable, "governance/content-audit.py")
    run(sys.executable, "site/build_site.py")
    run(sys.executable, "governance/site-audit.py")
    run(
        sys.executable,
        "-m",
        "py_compile",
        "governance/content-audit.py",
        "governance/site-audit.py",
        "governance/release_check.py",
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
