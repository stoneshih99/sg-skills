#!/usr/bin/env python3
"""檢查完整遊戲交付 workflow 的資源與發佈契約。"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_VERSION = "0.27.0"
EXPECTED_SKILL_COUNT = 6
SKILL_PATH = "plugins/sg-game-dev-skills/skills/ship-small-game/SKILL.md"
STAGE_GATES_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/references/stage-gates.md"
)
DEPARTMENT_ROUTING_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/"
    "references/department-routing.md"
)
RECOVERY_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/"
    "references/recovery-and-scope-control.md"
)
GAME_BRIEF_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/templates/game-brief.md"
)
DELIVERY_ROADMAP_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/"
    "templates/delivery-roadmap.md"
)
ACCEPTANCE_MATRIX_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/"
    "templates/acceptance-matrix.md"
)
PRODUCTION_STATUS_PATH = (
    "plugins/sg-game-dev-skills/skills/ship-small-game/"
    "templates/production-status.md"
)

STAGES = [
    "Preflight",
    "Game Contract",
    "Production Blueprint",
    "Vertical Slice",
    "Content Complete",
    "Quality Complete",
    "Release Candidate",
]
STAGE_CONTRACTS = {
    "Preflight": {
        "entry": "收到遊戲構想或既有專案的交付請求",
        "next": "Game Contract",
    },
    "Game Contract": {
        "entry": "Preflight 已完成",
        "next": "Production Blueprint",
    },
    "Production Blueprint": {
        "entry": "Game Contract 已核准",
        "next": "Vertical Slice",
    },
    "Vertical Slice": {
        "entry": "Production Blueprint 已建立",
        "next": "Content Complete",
    },
    "Content Complete": {
        "entry": "Vertical Slice 已核准",
        "next": "Quality Complete",
        "required": {
            "核准閘門": "Content Complete 後停止新增功能",
        },
    },
    "Quality Complete": {
        "entry": "Content Complete 已達成",
        "next": "Release Candidate",
        "required": {
            "完成證據": "程式／完整流程／視覺／效能／存檔／玩測皆有執行證據",
        },
    },
    "Release Candidate": {
        "entry": "Quality Complete 已完成",
        "next": "交付或正式發佈",
        "required": {
            "完成證據": "有可執行 Build",
        },
    },
}
STAGE_FIELDS = ["進入條件", "必做工作", "核准閘門", "完成證據", "下一階段"]
GAME_BRIEF_HEADINGS = [
    "Product Promise",
    "Target Player And Platform",
    "Core Loop",
    "Start-To-End Flow",
    "Must / Cut / Not Doing",
    "Definition Of Done",
    "Approved Major Decisions",
]
DELIVERY_ROADMAP_HEADINGS = [
    "Current Stage",
    "Stage Status",
    "Work Packages",
    "Risks And Gates",
    "Next Executable Step",
]
PRODUCTION_STATUS_HEADINGS = [
    "Last Updated",
    "Current Stage",
    "Completed",
    "In Progress",
    "Next",
    "Blocked",
    "Recent Decisions And Scope Changes",
    "Resume Here",
]
ACCEPTANCE_AREAS = [
    "Gameplay",
    "Start-To-End",
    "Visual",
    "Content",
    "Code",
    "Tests",
    "Performance",
    "Save",
    "Build",
]
RECOVERY_ROWS = [
    (
        "Missing engine/SDK/account/build tool",
        "Blocked",
        "記錄缺口與最小解阻步驟",
    ),
    (
        "Asset provenance unclear",
        "Blocked for RC",
        "使用合法暫代資產或取得授權",
    ),
    (
        "Verification cannot run",
        "Unverified",
        "保留命令與所需環境",
    ),
    ("Test fails", "Not complete", "修復或經核准縮減範圍"),
    (
        "Scope grows after Content Complete",
        "Gate required",
        "回到 scope cutting 並更新四份文件",
    ),
    (
        "Existing project lacks docs",
        "Reconstruct",
        "從 repository 證據重建狀態",
    ),
    (
        "Session resumes",
        "Resume",
        "執行最早且依賴已滿足的未完成項目",
    ),
]
PORTABLE_TEXT_ROOTS = {
    ".agents",
    ".claude-plugin",
    "CLAUDE.md",
    "README.md",
    "docs",
    "plugins",
}
PORTABLE_TEXT_SUFFIXES = {
    ".json",
    ".md",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
COMMON_CHECKOUT_PATH = re.compile(
    r"(?:^|[\s`'\"(=])(/(?:Users|Volumes)/[^\s`'\"<>)]*)"
)

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
            SKILL_PATH: [
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
            SKILL_PATH: [
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
    if name == "core":
        check_core_contract(errors)
    elif name == "routing":
        check_routing_contract(errors)


def h2_sections(text: str) -> tuple[list[str], dict[str, str]]:
    matches = list(re.finditer(r"^##[ \t]+(.+?)[ \t]*$", text, re.MULTILINE))
    headings = [match.group(1) for match in matches]
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[match.end() : end]
    return headings, sections


def check_h2_headings(
    relative_path: str,
    text: str,
    expected: list[str],
    errors: list[str],
) -> dict[str, str]:
    headings, sections = h2_sections(text)
    if headings != expected:
        errors.append(
            f"[core] {relative_path} 的二級 headings 必須依序為 {expected}，"
            f"實際為 {headings}"
        )
    return sections


def check_h1(
    relative_path: str,
    text: str,
    expected: str,
    errors: list[str],
) -> None:
    headings = re.findall(r"^#[ \t]+(.+?)[ \t]*$", text, re.MULTILINE)
    if headings != [expected]:
        errors.append(
            f"[core] {relative_path} 的一級 heading 必須是 {expected}，"
            f"實際為 {headings}"
        )


def markdown_table(text: str) -> tuple[list[str], list[list[str]]]:
    table_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(table_lines) < 2:
        return [], []

    parsed = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in table_lines
    ]
    separator = parsed[1]
    if not separator or not all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        return parsed[0], parsed[1:]
    return parsed[0], parsed[2:]


def field_value(section: str, field: str) -> str:
    match = re.search(
        rf"^-\s+{re.escape(field)}：(.*)$",
        section,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def check_stage_gates(errors: list[str]) -> None:
    text = read_text(STAGE_GATES_PATH, errors)
    headings, sections = h2_sections(text)
    if headings != STAGES:
        errors.append(
            f"[core] {STAGE_GATES_PATH} 的七階段必須依序為 {STAGES}，"
            f"實際為 {headings}"
        )

    for stage in STAGES:
        section = sections.get(stage)
        if section is None:
            continue
        fields = re.findall(
            r"^-\s+(進入條件|必做工作|核准閘門|完成證據|下一階段)：",
            section,
            re.MULTILINE,
        )
        if fields != STAGE_FIELDS:
            errors.append(
                f"[core] {STAGE_GATES_PATH} 的 {stage} 欄位必須依序為 "
                f"{STAGE_FIELDS}，實際為 {fields}"
            )

        contract = STAGE_CONTRACTS[stage]
        entry = field_value(section, "進入條件")
        if contract["entry"] not in entry:
            errors.append(
                f"[core] {STAGE_GATES_PATH} 的 {stage} 進入條件缺少："
                f"{contract['entry']}"
            )
        next_stage = field_value(section, "下一階段")
        if contract["next"] not in next_stage:
            errors.append(
                f"[core] {STAGE_GATES_PATH} 的 {stage} 下一階段缺少："
                f"{contract['next']}"
            )
        for field, token in contract.get("required", {}).items():
            if token not in field_value(section, field):
                errors.append(
                    f"[core] {STAGE_GATES_PATH} 的 {stage} {field}缺少：{token}"
                )


def check_templates(errors: list[str]) -> None:
    game_brief = read_text(GAME_BRIEF_PATH, errors)
    check_h1(GAME_BRIEF_PATH, game_brief, "Game Brief", errors)
    check_h2_headings(
        GAME_BRIEF_PATH,
        game_brief,
        GAME_BRIEF_HEADINGS,
        errors,
    )

    roadmap = read_text(DELIVERY_ROADMAP_PATH, errors)
    check_h1(DELIVERY_ROADMAP_PATH, roadmap, "Delivery Roadmap", errors)
    roadmap_sections = check_h2_headings(
        DELIVERY_ROADMAP_PATH,
        roadmap,
        DELIVERY_ROADMAP_HEADINGS,
        errors,
    )
    stage_header, stage_rows = markdown_table(
        roadmap_sections.get("Stage Status", "")
    )
    expected_stage_header = ["Stage", "Status", "Evidence Or Notes"]
    if stage_header != expected_stage_header:
        errors.append(
            f"[core] {DELIVERY_ROADMAP_PATH} 的 Stage Status 欄位必須是 "
            f"{expected_stage_header}，實際為 {stage_header}"
        )
    expected_stage_rows = [[stage, "Not Started", ""] for stage in STAGES]
    if stage_rows != expected_stage_rows:
        errors.append(
            f"[core] {DELIVERY_ROADMAP_PATH} 必須預置七階段狀態列："
            f"{expected_stage_rows}，實際為 {stage_rows}"
        )

    work_header, _ = markdown_table(roadmap_sections.get("Work Packages", ""))
    expected_work_header = [
        "ID",
        "Deliverable",
        "Department",
        "Depends On",
        "Verification",
        "Status",
    ]
    if work_header != expected_work_header:
        errors.append(
            f"[core] {DELIVERY_ROADMAP_PATH} 的 Work Packages 欄位必須是 "
            f"{expected_work_header}，實際為 {work_header}"
        )

    acceptance = read_text(ACCEPTANCE_MATRIX_PATH, errors)
    check_h1(ACCEPTANCE_MATRIX_PATH, acceptance, "Acceptance Matrix", errors)
    acceptance_header, acceptance_rows = markdown_table(acceptance)
    expected_acceptance_header = [
        "Area",
        "Acceptance",
        "State",
        "Evidence Or Reproduction",
        "Accepted Risk Owner",
        "Accepted Risk Reason",
    ]
    if acceptance_header != expected_acceptance_header:
        errors.append(
            f"[core] {ACCEPTANCE_MATRIX_PATH} 欄位必須是 "
            f"{expected_acceptance_header}，實際為 {acceptance_header}"
        )
    actual_areas = [row[0] for row in acceptance_rows if row]
    if actual_areas != ACCEPTANCE_AREAS:
        errors.append(
            f"[core] {ACCEPTANCE_MATRIX_PATH} areas 必須依序為 "
            f"{ACCEPTANCE_AREAS}，實際為 {actual_areas}"
        )
    for row in acceptance_rows:
        if len(row) != len(expected_acceptance_header):
            errors.append(
                f"[core] {ACCEPTANCE_MATRIX_PATH} row 欄位數錯誤：{row}"
            )
        elif row[2] != "Unverified":
            errors.append(
                f"[core] {ACCEPTANCE_MATRIX_PATH} 預置 state 必須是 "
                f"Unverified：{row}"
            )
    if "State 僅允許 Verified、Unverified、Blocked。" not in acceptance:
        errors.append(
            f"[core] {ACCEPTANCE_MATRIX_PATH} 缺少 acceptance 三態規則"
        )

    production_status = read_text(PRODUCTION_STATUS_PATH, errors)
    check_h1(PRODUCTION_STATUS_PATH, production_status, "Production Status", errors)
    check_h2_headings(
        PRODUCTION_STATUS_PATH,
        production_status,
        PRODUCTION_STATUS_HEADINGS,
        errors,
    )


def check_core_contract(errors: list[str]) -> None:
    skill = read_text(SKILL_PATH, errors)
    _, skill_sections = h2_sections(skill)
    stage_section = skill_sections.get("階段", "")
    stage_sequence = " → ".join(STAGES)
    if stage_sequence not in stage_section:
        errors.append(f"[core] {SKILL_PATH} 缺少依序七階段：{stage_sequence}")
    if "不可跳過中間階段" not in stage_section:
        errors.append(f"[core] {SKILL_PATH} 缺少不可跳 stage 規則")

    check_stage_gates(errors)
    check_templates(errors)


def check_routing_contract(errors: list[str]) -> None:
    routing = read_text(DEPARTMENT_ROUTING_PATH, errors)
    _, routing_sections = h2_sections(routing)
    handoff = routing_sections.get("Handoff Contract", "")
    handoff_fields = re.findall(r"^-\s+([^：\n]+)：\s*$", handoff, re.MULTILINE)
    expected_handoff_fields = [
        "Input",
        "Expected output",
        "Dependencies",
        "Verification",
        "Core artifacts to update",
    ]
    if handoff_fields != expected_handoff_fields:
        errors.append(
            f"[routing] {DEPARTMENT_ROUTING_PATH} 的 handoff 五欄必須依序為 "
            f"{expected_handoff_fields}，實際為 {handoff_fields}"
        )

    recovery = read_text(RECOVERY_PATH, errors)
    recovery_header, recovery_rows = markdown_table(recovery)
    expected_recovery_header = ["Condition", "Disposition", "Required action"]
    if recovery_header != expected_recovery_header:
        errors.append(
            f"[routing] {RECOVERY_PATH} 欄位必須是 "
            f"{expected_recovery_header}，實際為 {recovery_header}"
        )
    expected_recovery_rows = [list(row) for row in RECOVERY_ROWS]
    if recovery_rows != expected_recovery_rows:
        errors.append(
            f"[routing] {RECOVERY_PATH} 必須保留七個恢復情境，"
            f"實際為 {recovery_rows}"
        )


def tracked_portable_text_paths(errors: list[str]) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(
            "[release] 無法列出 repository 追蹤檔案："
            f"{result.stderr.strip() or 'git ls-files failed'}"
        )
        return []

    paths: list[Path] = []
    for value in result.stdout.split("\0"):
        if not value:
            continue
        relative_path = Path(value)
        top_level = relative_path.parts[0]
        if top_level not in PORTABLE_TEXT_ROOTS:
            continue
        if (
            relative_path.suffix.lower() not in PORTABLE_TEXT_SUFFIXES
            and relative_path.name not in {"CLAUDE.md", "README.md"}
        ):
            continue
        paths.append(relative_path)
    return paths


def check_portable_paths(errors: list[str]) -> None:
    checkout_path = str(ROOT.resolve())
    for relative_path in tracked_portable_text_paths(errors):
        path = ROOT / relative_path
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as error:
            errors.append(f"[release] 無法讀取 {relative_path}：{error}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            matched_path = ""
            if checkout_path in line:
                matched_path = checkout_path
            else:
                match = COMMON_CHECKOUT_PATH.search(line)
                if match is not None:
                    matched_path = match.group(1)
            if matched_path:
                errors.append(
                    f"[release] {relative_path}:{line_number} "
                    f"含 checkout 絕對路徑：{matched_path}"
                )


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

    check_portable_paths(errors)


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
