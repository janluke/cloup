from __future__ import annotations

import json
import shutil
import subprocess
import sys
from fnmatch import fnmatchcase


def select_environment_names(output: str, patterns: list[str]) -> list[str]:
    environments = json.loads(output)
    if not isinstance(environments, dict) or not all(
        isinstance(name, str) and isinstance(config, dict)
        for name, config in environments.items()
    ):
        msg = "expected `hatch env show --json` to return an environment object"
        raise ValueError(msg)

    selected: list[str] = []
    for pattern in patterns:
        matches = [name for name in environments if fnmatchcase(name, pattern)]
        if not matches:
            raise ValueError(f"pattern {pattern!r} matched no Hatch environments")
        selected.extend(name for name in matches if name not in selected)

    return sorted(selected)


def main() -> int:
    patterns = sys.argv[1:]
    if not patterns:
        print(f"Usage: {sys.argv[0]} PATTERN [PATTERN ...]", file=sys.stderr)
        return 2

    hatch = shutil.which("hatch")
    if hatch is None:
        print("Could not find the Hatch executable", file=sys.stderr)
        return 1

    result = subprocess.run(
        [hatch, "env", "show", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print(result.stdout + result.stderr, file=sys.stderr, end="")
        return result.returncode

    try:
        names = select_environment_names(result.stdout, patterns)
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Could not select Hatch environments: {error}", file=sys.stderr)
        return 1

    print(*names, sep="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
