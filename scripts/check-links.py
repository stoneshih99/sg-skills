#!/usr/bin/env python3
"""全 monorepo 連結檢查：掃 plugins/ 下所有 SKILL.md 與 references/*.md。

檢查三類 backtick 內連結：
  1. 裸檔名  `foo.md`         → 必須存在於同一個 references/ 目錄
  2. 相對路徑 `../a/b.md`、`references/x.md` → 相對該檔所在目錄解析後必須存在
  3. 相對目錄 `../other-hub/` → 相對該檔所在目錄解析後必須存在

跨 plugin 的相對連結（../../../../<另一個 plugin>）在安裝後各 plugin 獨立快取、
會斷——這類一律以文字提及，不用相對連結；本檢查若發現跨 plugin 相對連結會標 WARN。
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
PLUGINS = os.path.join(ROOT, "plugins")

# backtick 內、以 .md 結尾的連結
LINK = re.compile(r"`([^`\n]+?\.md)`")
# backtick 內、以 ./ 或 ../ 開頭並以 / 結尾的目錄連結
DIR_LINK = re.compile(r"`((?:\.\.?/)+[^`\n]+/)`")

bad = 0
warn = 0
checked = 0

for dirpath, _, filenames in os.walk(PLUGINS):
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        path = os.path.join(dirpath, fn)
        text = open(path, encoding="utf-8").read()
        for m in LINK.finditer(text):
            link = m.group(1).strip()
            # 跳過非路徑用途的行內文字（含空白的多半是描述，不是連結）
            if " " in link:
                continue
            checked += 1
            rel = os.path.relpath(path, ROOT)
            # 裸檔名（無路徑分隔）：慣例上指「本 hub 的 reference」，
            # 同目錄或同目錄下 references/ 命中都算通過（SKILL.md 在 hub 根、
            # reference 檔在 references/ 內，兩種來源都會裸名提及）。
            if os.sep not in link:
                cands = [
                    os.path.join(dirpath, link),
                    os.path.join(dirpath, "references", link),
                ]
                if any(os.path.isfile(c) for c in cands):
                    continue
                print(f"MISS  {rel}  ->  {link}")
                bad += 1
                continue
            target = os.path.normpath(os.path.join(dirpath, link))
            if not os.path.isfile(target):
                print(f"MISS  {rel}  ->  {link}")
                bad += 1
                continue
            # 跨 plugin 相對連結偵測
            trg_rel = os.path.relpath(target, PLUGINS)
            src_rel = os.path.relpath(path, PLUGINS)
            if trg_rel.split(os.sep)[0] != src_rel.split(os.sep)[0] and ".." in link:
                print(f"WARN  跨 plugin 相對連結（快取後會斷，改文字提及）: {rel} -> {link}")
                warn += 1

        for m in DIR_LINK.finditer(text):
            link = m.group(1).strip()
            checked += 1
            rel = os.path.relpath(path, ROOT)
            target = os.path.normpath(os.path.join(dirpath, link))
            if not os.path.isdir(target):
                print(f"MISS  {rel}  ->  {link}")
                bad += 1
                continue
            trg_rel = os.path.relpath(target, PLUGINS)
            src_rel = os.path.relpath(path, PLUGINS)
            if trg_rel.split(os.sep)[0] != src_rel.split(os.sep)[0] and ".." in link:
                print(f"WARN  跨 plugin 相對連結（快取後會斷，改文字提及）: {rel} -> {link}")
                warn += 1

print(f"\n檢查連結 {checked}，斷鏈 {bad}，跨 plugin 警告 {warn}")
sys.exit(1 if bad or warn else 0)
