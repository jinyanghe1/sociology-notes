#!/usr/bin/env python3
"""
Backward-compatible build entrypoint.

Historical behavior of this script only rebuilt site/data/index.json and did
not generate site/articles/*.html, which caused "new Markdown is visible in
index but article page not found" issues.

To avoid that footgun, this script now delegates to scripts/build.py so both
article HTML and index data are always refreshed together.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    build_script = repo_root / "scripts" / "build.py"

    cmd = [sys.executable, str(build_script)]
    result = subprocess.run(cmd, cwd=repo_root)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
