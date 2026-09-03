#!/usr/bin/env python3
"""Validate the repository's Codex plugin, marketplace, version, and Skill layout."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


repoDir = Path(__file__).resolve().parent.parent
pluginFile = repoDir / ".codex-plugin" / "plugin.json"
marketFile = repoDir / ".agents" / "plugins" / "marketplace.json"
skillsDir = repoDir / "skills"
versionFile = repoDir / "VERSION"
namePattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
versionPattern = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
linkPattern = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")
sourcePattern = re.compile(r"(?:[A-Za-z]:\\|/Users/|/home/|customeSkills|\.codex[/\\]skills)", re.IGNORECASE)


def loadJson(path: Path) -> dict:
    """Load JSON with a useful path in any parse error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"缺少文件: {path.relative_to(repoDir)}") from None
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON 无效: {path.relative_to(repoDir)}: {error}") from error


def readFrontmatter(path: Path) -> dict[str, str]:
    """Read the simple scalar frontmatter required by Codex Skill files."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"缺少 YAML frontmatter: {path.relative_to(repoDir)}")
    try:
        endIndex = lines.index("---", 1)
    except ValueError:
        raise ValueError(f"frontmatter 未闭合: {path.relative_to(repoDir)}") from None
    values: dict[str, str] = {}
    for line in lines[1:endIndex]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validatePlugin(errors: list[str]) -> None:
    """Check fields that make the root installable as one Codex plugin."""
    try:
        plugin = loadJson(pluginFile)
    except ValueError as error:
        errors.append(str(error))
        return
    required = ["name", "version", "description", "author", "skills", "interface"]
    for key in required:
        if not plugin.get(key):
            errors.append(f"plugin.json 缺少必填字段: {key}")
    if plugin.get("name") != "ava-cloud-plus-devkit":
        errors.append("plugin.json name 必须是 ava-cloud-plus-devkit")
    version = plugin.get("version", "")
    if not versionPattern.fullmatch(version):
        errors.append(f"plugin.json version 不是严格语义化版本: {version}")
    savedVersion = versionFile.read_text(encoding="utf-8").strip() if versionFile.exists() else ""
    if version != savedVersion:
        errors.append(f"VERSION ({savedVersion}) 与 plugin.json ({version}) 不一致")
    if plugin.get("skills") != "./skills/":
        errors.append("plugin.json skills 必须指向 ./skills/")
    defaultPrompt = plugin.get("interface", {}).get("defaultPrompt")
    if not isinstance(defaultPrompt, list) or not 1 <= len(defaultPrompt) <= 3:
        errors.append("interface.defaultPrompt 必须是包含 1-3 项的数组")


def validateMarketplace(errors: list[str]) -> None:
    """Ensure a Git checkout can act as a marketplace and plugin package."""
    try:
        marketplace = loadJson(marketFile)
    except ValueError as error:
        errors.append(str(error))
        return
    if marketplace.get("name") != "ava-cloud-plus-devkit":
        errors.append("marketplace name 必须是 ava-cloud-plus-devkit")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append("marketplace 必须且只能声明当前插件")
        return
    entry = plugins[0]
    if entry.get("name") != "ava-cloud-plus-devkit":
        errors.append("marketplace 插件名与 manifest 不一致")
    if entry.get("source") != {"source": "url", "url": "./"}:
        errors.append("Git marketplace 的插件源必须指向仓库根目录 ./")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
        errors.append("marketplace policy 必须保持 AVAILABLE / ON_INSTALL")


def validateSkills(errors: list[str]) -> None:
    """Check Skill identity, local links, portability, and accidental placeholders."""
    if not skillsDir.is_dir():
        errors.append("缺少 skills 目录")
        return
    skillDirs = sorted(path for path in skillsDir.iterdir() if path.is_dir())
    if len(skillDirs) != 4:
        errors.append(f"应包含 4 个 Skill，实际为 {len(skillDirs)} 个")
    for skillDir in skillDirs:
        skillFile = skillDir / "SKILL.md"
        if not skillFile.is_file():
            errors.append(f"缺少 {skillDir.name}/SKILL.md")
            continue
        try:
            metadata = readFrontmatter(skillFile)
        except ValueError as error:
            errors.append(str(error))
            continue
        if metadata.get("name") != skillDir.name:
            errors.append(f"Skill 名称不一致: {skillDir.name} != {metadata.get('name')}")
        if not metadata.get("description"):
            errors.append(f"Skill 缺少 description: {skillDir.name}")
        for filePath in skillDir.rglob("*"):
            if not filePath.is_file() or filePath.suffix.lower() not in {".md", ".yaml", ".yml", ".xml", ".jrxml"}:
                continue
            text = filePath.read_text(encoding="utf-8")
            if "[TODO:" in text or "FIXME" in text:
                errors.append(f"存在未完成占位符: {filePath.relative_to(repoDir)}")
            if sourcePattern.search(text):
                errors.append(f"存在本机绝对路径或源目录引用: {filePath.relative_to(repoDir)}")
            if filePath.suffix.lower() == ".md":
                for target in linkPattern.findall(text):
                    cleanTarget = target.split("#", 1)[0]
                    if cleanTarget and not (filePath.parent / cleanTarget).resolve().exists():
                        errors.append(f"无效相对链接: {filePath.relative_to(repoDir)} -> {target}")


def main() -> int:
    """Run every check and return a CI-friendly process status."""
    errors: list[str] = []
    validatePlugin(errors)
    validateMarketplace(errors)
    validateSkills(errors)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed: plugin, marketplace, version, and 4 Skills are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
