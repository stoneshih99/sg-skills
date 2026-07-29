#!/usr/bin/env python3
"""檢查完整遊戲交付 workflow 的資源與發佈契約。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
GAME_ROOT = ROOT / "plugins/sg-game-dev-skills"
EXPECTED_VERSION = "0.27.0"
EXPECTED_SKILL_COUNT = 6

GROUPS: dict[str, dict[str, Any]] = {
    "core": {
        "files": [
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/agents/openai.yaml",
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/stage-gates.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/game-brief.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/delivery-roadmap.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/acceptance-matrix.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/templates/production-status.md",
        ],
        "tokens": {
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md": [
                "Preflight",
                "Game Contract",
                "Production Blueprint",
                "Vertical Slice",
                "Content Complete",
                "Quality Complete",
                "Release Candidate",
                "重大決策",
                "Verified",
                "Unverified",
                "Blocked",
            ],
        },
    },
    "routing": {
        "files": [
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/department-routing.md",
            "plugins/sg-game-dev-skills/skills/ship-small-game/references/recovery-and-scope-control.md",
        ],
        "tokens": {
            "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md": [
                "references/department-routing.md",
                "references/recovery-and-scope-control.md",
            ],
        },
    },
}


def read_text(relative_path: str, errors: list[str]) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        errors.append(f"缺少 {relative_path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"無法讀取 {relative_path}：{error}")
        return ""


def load_json(relative_path: str, errors: list[str]) -> dict[str, Any] | None:
    text = read_text(relative_path, errors)
    if not text:
        return None
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        errors.append(f"{relative_path} 不是有效 JSON：{error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{relative_path} 根節點必須是 object")
        return None
    return value


def check_group(name: str, errors: list[str]) -> None:
    contract = GROUPS[name]
    for relative_path in contract["files"]:
        if not (ROOT / relative_path).is_file():
            errors.append(f"[{name}] 缺少 {relative_path}")
    for relative_path, tokens in contract["tokens"].items():
        text = read_text(relative_path, errors)
        for token in tokens:
            if token not in text:
                errors.append(f"[{name}] {relative_path} 缺少契約文字：{token}")


def marketplace_plugin(
    marketplace: dict[str, Any] | None,
    plugin_name: str,
) -> dict[str, Any] | None:
    if marketplace is None:
        return None
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        return None
    return next(
        (
            plugin
            for plugin in plugins
            if isinstance(plugin, dict) and plugin.get("name") == plugin_name
        ),
        None,
    )


def check_release(errors: list[str]) -> None:
    claude_manifest_path = "plugins/sg-game-dev-skills/.claude-plugin/plugin.json"
    codex_manifest_path = "plugins/sg-game-dev-skills/.codex-plugin/plugin.json"
    claude_manifest = load_json(claude_manifest_path, errors)
    codex_manifest = load_json(codex_manifest_path, errors)

    for relative_path, manifest in (
        (claude_manifest_path, claude_manifest),
        (codex_manifest_path, codex_manifest),
    ):
        if manifest is not None and manifest.get("version") != EXPECTED_VERSION:
            errors.append(
                f"[release] {relative_path} version 必須是 {EXPECTED_VERSION}"
            )

    if claude_manifest is not None:
        skills = claude_manifest.get("skills")
        if not isinstance(skills, list) or len(skills) != EXPECTED_SKILL_COUNT:
            errors.append(
                f"[release] Claude manifest skills 必須維持 "
                f"{EXPECTED_SKILL_COUNT} entries"
            )
        if not isinstance(skills, list) or "./skills/ship-small-game" not in skills:
            errors.append(
                "[release] Claude manifest 缺少 ./skills/ship-small-game"
            )

    marketplace_path = ".claude-plugin/marketplace.json"
    marketplace = load_json(marketplace_path, errors)
    game_entry = marketplace_plugin(marketplace, "sg-game-dev-skills")
    if game_entry is None:
        errors.append("[release] Claude marketplace 缺少 sg-game-dev-skills")
    else:
        description = game_entry.get("description")
        if not isinstance(description, str):
            errors.append("[release] Claude marketplace 的 sg-game-dev-skills 缺少描述")
        elif "完整遊戲" not in description:
            errors.append("[release] Claude marketplace 描述缺少契約文字：完整遊戲")

    checkout_path = str(ROOT.resolve())
    portable_path = GAME_ROOT / "skills/ship-small-game"
    if portable_path.is_dir():
        for path in portable_path.rglob("*"):
            if path.is_file() and checkout_path in path.read_text(
                encoding="utf-8", errors="ignore"
            ):
                errors.append(
                    f"[release] {path.relative_to(ROOT)} 含 checkout 絕對路徑"
                )


def main() -> int:
    available = [*GROUPS, "release"]
    selected = sys.argv[1:]
    if selected and any(name not in available for name in selected):
        print(f"可用 group：{', '.join(available)}", file=sys.stderr)
        return 2

    targets = selected or available
    errors: list[str] = []
    for name in targets:
        if name == "release":
            check_release(errors)
        else:
            check_group(name, errors)

    if errors:
        print("遊戲交付 workflow 契約檢查失敗：")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"遊戲交付 workflow 契約檢查通過：{', '.join(targets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
