#!/usr/bin/env python3
"""輕量中文技術文案檢查器。

檢查結果分為三類：
- error：高度確定的錯誤，預設導致非零退出。
- warning：需視語境判斷的可疑表達，需人工確認。
- style：團隊風格或術語偏好，需結合專案規範判斷。

指令碼忽略 Markdown front matter、程式碼區塊、行內程式碼、URL、連結目標和
常見 API 路徑。行尾加入 ``<!-- copy-lint-disable-line -->`` 可以忽略該行。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TARGETS = ["."]
INLINE_IGNORE_MARKER = "<!-- copy-lint-disable-line -->"
SKIP_DIR_NAMES = {".git", ".venv", "node_modules", "vendor"}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(.*?)\1")
URL_RE = re.compile(r"https?://\S+")
API_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])/[A-Za-z0-9._~%-]+"
    r"(?:/[A-Za-z0-9._~%-]+)*(?:\?[^\s)]*)?(?![A-Za-z0-9_])"
)
INLINE_LINK_RE = re.compile(r"(!?\[[^\]]*]\()([^)]+)(\))")

FORBIDDEN_QUOTES = {
    '"': "ASCII 雙引號",
    "“": "中文彎引號",
    "”": "中文彎引號",
}

NON_WORD_CHARS = r"\u4e00-\u9fffA-Za-z0-9_"
PREFIX_CONTEXT_CHARS = "與跟對向給幫替為請讓"
SUFFIX_HINTS = "可會要能應需請把將來去做看讀寫用"

FORBIDDEN_ADDRESS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            rf"(?<![{NON_WORD_CHARS}])你(?=$|[^\u4e00-\u9fff]|[{SUFFIX_HINTS}])"
        ),
        "你",
    ),
    (re.compile(rf"(?<=[{PREFIX_CONTEXT_CHARS}])你"), "你"),
    (re.compile(r"您"), "您"),
    (re.compile(r"同學(?:們)?"), "同學"),
]

CASE_RULES = [
    (re.compile(r"(?<![A-Za-z0-9_])(?:id|Id)(?![A-Za-z0-9_])"), "ID"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:http|Http)(?![A-Za-z0-9_])"), "HTTP"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:url|Url)(?![A-Za-z0-9_])"), "URL"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:json|Json)(?![A-Za-z0-9_])"), "JSON"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:api|Api)(?![A-Za-z0-9_])"), "API"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:ai|Ai)(?![A-Za-z0-9_])"), "AI"),
]

ABBREVIATION_RULES = [
    (re.compile(r"(?<![A-Za-z0-9_])(?:JS|Js)(?![A-Za-z0-9_])"), "JavaScript"),
    (re.compile(r"(?<![A-Za-z0-9_])H5(?![A-Za-z0-9_])"), "行動 Web 頁面或 HTML5"),
]

AI_TERM_RULES = [
    (re.compile(r"(?<![A-Za-z0-9_])(?:llm|Llm)(?![A-Za-z0-9_])"), "LLM"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:aigc|Aigc)(?![A-Za-z0-9_])"), "AIGC"),
    (re.compile(r"(?<![A-Za-z0-9_])(?:rag|Rag)(?![A-Za-z0-9_])"), "RAG"),
    (
        re.compile(r"(?<![A-Za-z0-9_])(?:chatgpt|Chatgpt)(?![A-Za-z0-9_])"),
        "ChatGPT",
    ),
    (
        re.compile(
            r"(?<![A-Za-z0-9_])(?:openai|OpenAI)\s+(?:api|Api)(?![A-Za-z0-9_])"
        ),
        "OpenAI API",
    ),
    (re.compile(r"(?<![A-Za-z0-9_])embeding(?![A-Za-z0-9_])"), "embedding"),
    (re.compile(r"(?<![A-Za-z0-9_])finetune(?![A-Za-z0-9_])"), "fine-tuning"),
    (
        re.compile(r"(?<![A-Za-z0-9_])fine\s+tune(?![A-Za-z0-9_])"),
        "fine-tuning",
    ),
    (re.compile(r"提示工程學"), "提示工程"),
    (re.compile(r"模型出現幻聽"), "模型出現幻覺"),
]

ERROR_TYPO_RULES = [
    (re.compile(r"閥值"), "閾值"),
    (re.compile(r"佈署"), "部署"),
    (re.compile(r"反回"), "返回"),
    (re.compile(r"回朔"), "回溯"),
    (re.compile(r"做為"), "作為"),
]

CONTEXT_WARNING_RULES = [
    (re.compile(r"登陸"), "確認語義：登入系統；登陸陸地或天體"),
    (re.compile(r"配製"), "確認語義：設定參數；依比例配製溶液"),
    (re.compile(r"起用"), "確認語義：啟用功能；起用人員"),
    (re.compile(r"標示"), "確認語義：識別欄位；標示位置"),
    (re.compile(r"賬戶"), "臺灣用語通常寫「帳戶」"),
    (re.compile(r"賬號"), "臺灣用語通常寫「帳號」"),
    (re.compile(r"截止"), "確認語義：截至某時；截止日期"),
    (re.compile(r"搜索"), "臺灣技術文件通常使用「搜尋」"),
]


@dataclass(frozen=True)
class Violation:
    file: Path
    line: int
    col: int
    severity: str
    kind: str
    message: str
    snippet: str


def mask_match(text: str, regex: re.Pattern[str]) -> str:
    return regex.sub(lambda match: " " * (match.end() - match.start()), text)


def prepare_visible_line(line: str) -> str:
    visible = mask_match(line, INLINE_CODE_RE)
    visible = INLINE_LINK_RE.sub(
        lambda match: (
            f"{match.group(1)}{' ' * len(match.group(2))}{match.group(3)}"
        ),
        visible,
    )
    visible = mask_match(visible, URL_RE)
    visible = mask_match(visible, API_PATH_RE)
    return visible


def iter_forbidden_address_matches(line: str):
    seen: set[tuple[int, int, str]] = set()
    for pattern, label in FORBIDDEN_ADDRESS_PATTERNS:
        for match in pattern.finditer(line):
            key = (match.start(), match.end(), label)
            if key not in seen:
                seen.add(key)
                yield match, label


def add_rule_matches(
    violations: list[Violation],
    *,
    path: Path,
    line_no: int,
    raw: str,
    visible: str,
    rules: list[tuple[re.Pattern[str], str]],
    severity: str,
    kind: str,
    label: str,
) -> None:
    for pattern, suggested in rules:
        for match in pattern.finditer(visible):
            wrong = match.group(0)
            violations.append(
                Violation(
                    file=path,
                    line=line_no,
                    col=match.start() + 1,
                    severity=severity,
                    kind=kind,
                    message=f"{label}「{wrong}」：{suggested}",
                    snippet=raw.strip(),
                )
            )


def scan_markdown(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    fence_delimiter: str | None = None
    lines = path.read_text(encoding="utf-8").splitlines()
    in_front_matter = bool(lines and lines[0].strip() == "---")

    for line_no, raw in enumerate(lines, start=1):
        if in_front_matter:
            if line_no != 1 and raw.strip() in {"---", "..."}:
                in_front_matter = False
            continue

        fence_match = FENCE_RE.match(raw)
        if fence_match:
            delimiter = fence_match.group(1)
            if fence_delimiter is None:
                fence_delimiter = delimiter
            elif delimiter[0] == fence_delimiter[0] and len(delimiter) >= len(
                fence_delimiter
            ):
                fence_delimiter = None
            continue

        if fence_delimiter is not None or INLINE_IGNORE_MARKER in raw:
            continue

        visible = prepare_visible_line(raw)

        for quote, label in FORBIDDEN_QUOTES.items():
            for match in re.finditer(re.escape(quote), visible):
                violations.append(
                    Violation(
                        file=path,
                        line=line_no,
                        col=match.start() + 1,
                        severity="style",
                        kind="quote",
                        message=f"可見正文包含{label}，確認是否應改為直角引號「」",
                        snippet=raw.strip(),
                    )
                )

        for match, term in iter_forbidden_address_matches(visible):
            violations.append(
                Violation(
                    file=path,
                    line=line_no,
                    col=match.start() + 1,
                    severity="style",
                    kind="address",
                    message=f"可見正文包含稱呼「{term}」，確認專案是否允許",
                    snippet=raw.strip(),
                )
            )

        add_rule_matches(
            violations,
            path=path,
            line_no=line_no,
            raw=raw,
            visible=visible,
            rules=CASE_RULES,
            severity="style",
            kind="casing",
            label="術語寫法",
        )
        add_rule_matches(
            violations,
            path=path,
            line_no=line_no,
            raw=raw,
            visible=visible,
            rules=ABBREVIATION_RULES,
            severity="style",
            kind="abbreviation",
            label="縮寫需視語境確認",
        )
        add_rule_matches(
            violations,
            path=path,
            line_no=line_no,
            raw=raw,
            visible=visible,
            rules=AI_TERM_RULES,
            severity="warning",
            kind="ai-term",
            label="AI 術語",
        )
        add_rule_matches(
            violations,
            path=path,
            line_no=line_no,
            raw=raw,
            visible=visible,
            rules=ERROR_TYPO_RULES,
            severity="error",
            kind="typo",
            label="高可信度錯詞",
        )
        add_rule_matches(
            violations,
            path=path,
            line_no=line_no,
            raw=raw,
            visible=visible,
            rules=CONTEXT_WARNING_RULES,
            severity="warning",
            kind="context",
            label="語境詞",
        )

    return violations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="檢查中文技術文案常見規則")
    parser.add_argument(
        "files",
        nargs="*",
        help="要檢查的 Markdown 檔案或目錄；為空時檢查目前目錄",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="將 warning 和 style 也作為失敗處理",
    )
    return parser.parse_args()


def collect_targets(args: argparse.Namespace) -> list[Path]:
    raw_targets = args.files if args.files else DEFAULT_TARGETS
    targets: list[Path] = []

    for item in raw_targets:
        path = Path(item)
        if not path.exists():
            print(f"[WARN] 檔案不存在，已跳過: {item}", file=sys.stderr)
            continue
        if path.is_dir():
            for markdown in sorted(path.rglob("*.md")):
                if any(part in SKIP_DIR_NAMES for part in markdown.parts):
                    continue
                targets.append(markdown)
        else:
            targets.append(path)

    return sorted(
        {path.resolve(): path for path in targets}.values(), key=lambda path: str(path)
    )


def main() -> int:
    args = parse_args()
    targets = collect_targets(args)
    if not targets:
        print("未找到可檢查的 Markdown 檔案。", file=sys.stderr)
        return 1

    findings = [item for target in targets for item in scan_markdown(target)]
    if not findings:
        print(f"PASS: 共檢查 {len(targets)} 個檔案，未發現問題。")
        return 0

    counts = {
        severity: sum(item.severity == severity for item in findings)
        for severity in ("error", "warning", "style")
    }
    for item in findings:
        print(
            f"- {item.file}:{item.line}:{item.col} "
            f"[{item.severity}/{item.kind}] {item.message}\n  {item.snippet}"
        )

    should_fail = bool(counts["error"] or (args.strict and findings))
    status = "FAIL" if should_fail else "PASS WITH ADVICE"
    print(
        f"{status}: 共檢查 {len(targets)} 個檔案；"
        f"error={counts['error']} warning={counts['warning']} style={counts['style']}。"
    )
    return 2 if should_fail else 0


if __name__ == "__main__":
    sys.exit(main())
