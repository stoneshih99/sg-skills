#!/usr/bin/env python3
"""檢查 Claude Code 與 Codex plugin 的共用結構與 metadata。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PLUGINS = {
    "sg-game-dev-skills": Path("plugins/sg-game-dev-skills"),
    "sg-unity-dev-skills": Path("plugins/sg-unity-dev-skills"),
    "sg-dev-skills": Path("plugins/sg-dev-skills"),
}


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"缺少 {path.relative_to(ROOT)}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(ROOT)} 不是有效 JSON：{error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)} 根節點必須是 object")
        return None
    return value


def plugin_entries(
    marketplace: dict[str, Any] | None,
    path: Path,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if marketplace is None:
        return {}
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append(f"{path.relative_to(ROOT)} 的 plugins 必須是 array")
        return {}

    entries: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(plugins):
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            errors.append(
                f"{path.relative_to(ROOT)} 的 plugins[{index}] 必須有字串 name"
            )
            continue
        name = entry["name"]
        if name in entries:
            errors.append(f"{path.relative_to(ROOT)} 重複列出 plugin {name}")
        entries[name] = entry

    expected_names = set(EXPECTED_PLUGINS)
    actual_names = set(entries)
    if actual_names != expected_names:
        errors.append(
            f"{path.relative_to(ROOT)} plugin 名單不符："
            f"預期 {sorted(expected_names)}，實際 {sorted(actual_names)}"
        )
    return entries


def check_marketplaces(errors: list[str]) -> None:
    claude_path = ROOT / ".claude-plugin/marketplace.json"
    codex_path = ROOT / ".agents/plugins/marketplace.json"
    claude_entries = plugin_entries(load_json(claude_path, errors), claude_path, errors)
    codex_entries = plugin_entries(load_json(codex_path, errors), codex_path, errors)

    for name, relative_root in EXPECTED_PLUGINS.items():
        expected_source = f"./{relative_root.as_posix()}"

        claude_entry = claude_entries.get(name)
        if claude_entry is not None and claude_entry.get("source") != expected_source:
            errors.append(
                f"Claude marketplace 的 {name} source 必須是 {expected_source}"
            )

        codex_entry = codex_entries.get(name)
        if codex_entry is None:
            continue
        expected_codex_source = {"source": "local", "path": expected_source}
        if codex_entry.get("source") != expected_codex_source:
            errors.append(
                f"Codex marketplace 的 {name} source 必須是 "
                f"{expected_codex_source}"
            )
        expected_policy = {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }
        if codex_entry.get("policy") != expected_policy:
            errors.append(
                f"Codex marketplace 的 {name} policy 必須是 {expected_policy}"
            )
        if codex_entry.get("category") != "Developer Tools":
            errors.append(
                f"Codex marketplace 的 {name} category 必須是 Developer Tools"
            )


def check_plugin_roots(errors: list[str]) -> None:
    plugins_root = ROOT / "plugins"
    if not plugins_root.is_dir():
        errors.append("缺少 plugins/ 目錄")
        return
    actual_roots = {
        path.name
        for path in plugins_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    expected_roots = set(EXPECTED_PLUGINS)
    if actual_roots != expected_roots:
        errors.append(
            f"plugins/ 目錄不符：預期 {sorted(expected_roots)}，"
            f"實際 {sorted(actual_roots)}"
        )


def check_plugin(name: str, relative_root: Path, errors: list[str]) -> None:
    plugin_root = ROOT / relative_root
    if plugin_root.name != name:
        errors.append(f"{relative_root} 目錄名稱必須與 plugin name {name} 相同")
    if plugin_root.is_symlink():
        errors.append(f"{relative_root} 不可使用 symlink")
    if not plugin_root.is_dir():
        errors.append(f"缺少 plugin 目錄 {relative_root}")
        return
    for path in plugin_root.rglob("*"):
        if path.is_symlink():
            errors.append(f"{path.relative_to(ROOT)} 不可使用 symlink")

    claude_path = plugin_root / ".claude-plugin/plugin.json"
    codex_path = plugin_root / ".codex-plugin/plugin.json"
    claude = load_json(claude_path, errors)
    codex = load_json(codex_path, errors)
    if claude is not None and codex is not None:
        if claude.get("name") != name:
            errors.append(f"{name} 的 Claude manifest name 必須是 {name}")
        if codex.get("name") != name:
            errors.append(f"{name} 的 Codex manifest name 必須是 {name}")
        for field in ("name", "version", "description", "author"):
            if claude.get(field) != codex.get(field):
                errors.append(f"{name} 的 Claude/Codex {field} 必須一致")
        if codex.get("skills") != "./skills":
            errors.append(f"{name} 的 Codex skills 必須是 ./skills")

    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        errors.append(f"{relative_root}/skills 不存在")
        return

    direct_skills = [
        path
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and not path.name.startswith(".")
    ]
    if not direct_skills:
        errors.append(f"{relative_root}/skills 沒有 skill")
        return
    for skill_root in direct_skills:
        if not (skill_root / "SKILL.md").is_file():
            errors.append(
                f"{skill_root.relative_to(ROOT)} 必須直接包含 SKILL.md"
            )

    expected_claude_skills = {f"./skills/{path.name}" for path in direct_skills}
    if claude is not None:
        raw_claude_skills = claude.get("skills")
        actual_claude_skills = (
            set(raw_claude_skills)
            if isinstance(raw_claude_skills, list)
            and all(isinstance(path, str) for path in raw_claude_skills)
            else set()
        )
        if (
            actual_claude_skills != expected_claude_skills
            or not isinstance(raw_claude_skills, list)
            or len(raw_claude_skills) != len(expected_claude_skills)
        ):
            errors.append(
                f"{name} 的 Claude skills 必須恰好列出 "
                f"{sorted(expected_claude_skills)}"
            )

    for skill_md in skills_root.rglob("SKILL.md"):
        if skill_md.parent.parent != skills_root:
            errors.append(
                f"{skill_md.relative_to(ROOT)} 不可位於巢狀 category 目錄"
            )


def main() -> int:
    errors: list[str] = []
    check_plugin_roots(errors)
    check_marketplaces(errors)
    for name, relative_root in EXPECTED_PLUGINS.items():
        check_plugin(name, relative_root, errors)

    if errors:
        print("Plugin 相容檢查失敗：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Plugin 相容檢查通過：3 個 plugin 均支援 Claude Code 與 Codex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
