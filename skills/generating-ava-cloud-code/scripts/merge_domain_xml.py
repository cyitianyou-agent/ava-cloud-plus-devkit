#!/usr/bin/env python3
"""Merge btulz per-business-object XML files into one conflict-checked Domain."""

from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ElementTree
from pathlib import Path


def signature(element: ElementTree.Element) -> tuple[object, ...]:
    """Build a whitespace-insensitive semantic signature for duplicate checks."""
    text = (element.text or "").strip()
    children = tuple(signature(child) for child in list(element))
    return element.tag, tuple(sorted(element.attrib.items())), text, children


def findInputs(source: Path, output: Path) -> list[Path]:
    """Resolve one XML or all direct XML children of a directory."""
    if source.is_file():
        files = [source]
    elif source.is_dir():
        files = sorted(path for path in source.glob("*.xml") if path.is_file())
    else:
        raise ValueError(f"input does not exist: {source}")
    outputPath = output.resolve()
    files = [path for path in files if path.resolve() != outputPath]
    if not files:
        raise ValueError(f"no input XML files found: {source}")
    return files


def itemKey(element: ElementTree.Element) -> str:
    """Use stable XML identifiers for models and top-level business objects."""
    if element.tag == "Model":
        key = element.get("Name")
    elif element.tag == "BusinessObject":
        key = element.get("Name") or element.get("MappedModel")
    else:
        raise ValueError(f"unsupported Domain child: {element.tag}")
    if not key:
        raise ValueError(f"{element.tag} is missing its stable identifier")
    return key


def mergeFiles(files: list[Path]) -> ElementTree.Element:
    """Merge identical duplicates and reject conflicting definitions."""
    mergedRoot: ElementTree.Element | None = None
    models: dict[str, tuple[ElementTree.Element, Path]] = {}
    objects: dict[str, tuple[ElementTree.Element, Path]] = {}
    for path in files:
        root = ElementTree.parse(path).getroot()
        if root.tag != "Domain":
            raise ValueError(f"root is not Domain: {path}")
        if mergedRoot is None:
            mergedRoot = ElementTree.Element("Domain", dict(root.attrib))
        elif root.attrib != mergedRoot.attrib:
            raise ValueError(
                f"Domain attributes conflict: {files[0]} {mergedRoot.attrib} != {path} {root.attrib}"
            )
        for child in list(root):
            key = itemKey(child)
            items = models if child.tag == "Model" else objects
            existing = items.get(key)
            if existing is None:
                items[key] = (copy.deepcopy(child), path)
            elif signature(existing[0]) != signature(child):
                raise ValueError(
                    f"conflicting {child.tag} '{key}': {existing[1]} != {path}"
                )
    assert mergedRoot is not None
    for element, _ in models.values():
        mergedRoot.append(element)
    for element, _ in objects.values():
        mergedRoot.append(element)
    modelNames = set(models)
    for businessObject, path in objects.values():
        for item in businessObject.iter():
            if item.tag not in {"BusinessObject", "RelatedBO"}:
                continue
            mappedModel = item.get("MappedModel")
            if not mappedModel or mappedModel not in modelNames:
                raise ValueError(
                    f"unresolved MappedModel '{mappedModel}' in {path}"
                )
    return mergedRoot


def main() -> int:
    """Merge the source XML set and write one UTF-8 staging XML."""
    parser = argparse.ArgumentParser(
        description="Merge direct btulz Domain XML files and reject conflicting duplicates."
    )
    parser.add_argument("source", type=Path, help="One XML file or a directory of XML files")
    parser.add_argument("output", type=Path, help="Merged staging XML file")
    args = parser.parse_args()
    output = args.output.resolve()
    files = findInputs(args.source.resolve(), output)
    root = mergeFiles(files)
    output.parent.mkdir(parents=True, exist_ok=True)
    ElementTree.indent(root, space="  ")
    ElementTree.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    print(
        f"merged {len(files)} file(s): "
        f"{len(root.findall('Model'))} model(s), "
        f"{len(root.findall('BusinessObject'))} business object(s) -> {output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ElementTree.ParseError) as error:
        raise SystemExit(f"merge failed: {error}") from error
