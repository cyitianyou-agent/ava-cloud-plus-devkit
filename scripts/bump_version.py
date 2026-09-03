#!/usr/bin/env python3
"""Update the repository version in every authoritative version file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


versionPattern = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
repoDir = Path(__file__).resolve().parent.parent
pluginFile = repoDir / ".codex-plugin" / "plugin.json"
versionFile = repoDir / "VERSION"


def parseArgs() -> argparse.Namespace:
    """Accept only a strict stable semantic version to keep releases predictable."""
    parser = argparse.ArgumentParser(description="Update VERSION and the Codex plugin manifest.")
    parser.add_argument("version", help="New semantic version, for example 0.2.0")
    args = parser.parse_args()
    if not versionPattern.fullmatch(args.version):
        parser.error("version must use MAJOR.MINOR.PATCH without a prefix or suffix")
    return args


def main() -> None:
    """Preserve the manifest structure while changing only its version field."""
    args = parseArgs()
    plugin = json.loads(pluginFile.read_text(encoding="utf-8"))
    plugin["version"] = args.version
    pluginFile.write_text(json.dumps(plugin, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    versionFile.write_text(args.version + "\n", encoding="utf-8")
    print(f"Updated plugin version to {args.version}.")
    print("Remember to update CHANGELOG.md before tagging the release.")


if __name__ == "__main__":
    main()
