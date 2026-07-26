from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TRACKED = ROOT / "site" / "generated"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def file_map(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> None:
    if not TRACKED.exists():
        raise SystemExit("GENERATED CONSISTENCY FAILED: site/generated is missing")

    with tempfile.TemporaryDirectory(prefix="practical-ai-generated-") as temp_dir:
        fresh = Path(temp_dir) / "generated"
        subprocess.run(
            [sys.executable, "site/build_site.py", "--output", str(fresh)],
            cwd=ROOT,
            check=True,
        )

        tracked_files = file_map(TRACKED)
        fresh_files = file_map(fresh)

    missing = sorted(fresh_files.keys() - tracked_files.keys())
    extra = sorted(tracked_files.keys() - fresh_files.keys())
    changed = sorted(
        path
        for path in tracked_files.keys() & fresh_files.keys()
        if tracked_files[path] != fresh_files[path]
    )

    if missing or extra or changed:
        details: list[str] = []
        details.extend(f"missing generated file: {path}" for path in missing)
        details.extend(f"unexpected generated file: {path}" for path in extra)
        details.extend(f"stale generated file: {path}" for path in changed)
        preview = "\n".join(details[:25])
        remainder = len(details) - 25
        if remainder > 0:
            preview += f"\n... and {remainder} more difference(s)"
        raise SystemExit(
            "GENERATED CONSISTENCY FAILED: site/generated does not match the canonical source.\n"
            + preview
            + "\nRun `python site/build_site.py`, review the changes, and commit the complete generated output."
        )

    print(
        "GENERATED CONSISTENCY PASSED: "
        f"{len(tracked_files)} generated files match the canonical source"
    )


if __name__ == "__main__":
    main()
