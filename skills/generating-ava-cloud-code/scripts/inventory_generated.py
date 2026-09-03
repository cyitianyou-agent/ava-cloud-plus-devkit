#!/usr/bin/env python3
"""Inventory staged btulz code against a target module without writing files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ignoredParts = {".git", ".hg", ".svn", ".vs", "node_modules"}
emptyMarkers = {".gitkeep", ".keep", "desktop.ini", ".ds_store"}


def collectFiles(root: Path) -> dict[str, Path]:
    """Collect files while excluding VCS internals and dependency trees."""
    if not root.exists():
        return {}
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.lower() in ignoredParts for part in relative.parts):
            continue
        files[relative.as_posix()] = path
    return files


def digest(path: Path) -> str:
    """Hash bytes so newline and encoding differences remain visible."""
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def buildReport(generatedRoot: Path, targetRoot: Path) -> dict[str, object]:
    """Classify paths without deciding which differences should be merged."""
    generatedFiles = collectFiles(generatedRoot)
    targetFiles = collectFiles(targetRoot)
    newFiles: list[str] = []
    changedFiles: list[str] = []
    sameFiles: list[str] = []
    for relative, generatedPath in sorted(generatedFiles.items()):
        targetPath = targetFiles.get(relative)
        if targetPath is None:
            newFiles.append(relative)
        elif digest(generatedPath) == digest(targetPath):
            sameFiles.append(relative)
        else:
            changedFiles.append(relative)
    targetOnly = sorted(set(targetFiles) - set(generatedFiles))
    codeFiles = [
        relative
        for relative in targetFiles
        if Path(relative).name.lower() not in emptyMarkers
    ]
    return {
        "generatedRoot": str(generatedRoot.resolve()),
        "targetRoot": str(targetRoot.resolve()),
        "targetHasCode": bool(codeFiles),
        "counts": {
            "new": len(newFiles),
            "changed": len(changedFiles),
            "same": len(sameFiles),
            "targetOnly": len(targetOnly),
        },
        "new": newFiles,
        "changed": changedFiles,
        "same": sameFiles,
        "targetOnly": targetOnly,
    }


def main() -> int:
    """Parse arguments and emit a text or JSON inventory."""
    parser = argparse.ArgumentParser(description="Compare generated and target module roots.")
    parser.add_argument("generated", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    generatedRoot = args.generated.resolve()
    targetRoot = args.target.resolve()
    if not generatedRoot.is_dir():
        raise SystemExit(f"generated root is not a directory: {generatedRoot}")
    report = buildReport(generatedRoot, targetRoot)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    print(f"generated: {report['generatedRoot']}")
    print(f"target: {report['targetRoot']}")
    print(f"targetHasCode: {str(report['targetHasCode']).lower()}")
    counts = report["counts"]
    assert isinstance(counts, dict)
    print(
        f"counts: new={counts['new']} changed={counts['changed']} "
        f"same={counts['same']} target-only={counts['targetOnly']}"
    )
    for status in ("new", "changed", "same", "targetOnly"):
        paths = report[status]
        assert isinstance(paths, list)
        if paths:
            print(f"\n[{status}]")
            for path in paths:
                print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
