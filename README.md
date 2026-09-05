# Chinese Tech Doc Style

本專案提供一套針對繁體中文技術文件、產品文案與介面文案的寫作 Skill。

這份 Skill 以準確、清楚、事實保真、可執行和易於瀏覽為優先。不追求宣傳感，也不把所有內容套入統一範本，而是著重處理幾類常見問題：

- 中文技術文案容易空泛、重複、宣傳化
- 中文與英文、數字混合排版時可讀性差
- 常見英文狀態詞和錯誤詞容易被機械直譯
- 文件首頁、解決方案頁、API 說明頁、FAQ 的資訊密度和結構經常失衡

如果需要一套適合中文技術文件的基礎寫作規範，這份 Skill 可以直接拿來使用，或是作為參考。

## 適用情境

本 Skill 適合以下內容：

- 文件首頁、活動到達頁 (Landing Page)、首頁主視覺 (Above the Fold) 文案
- API 文件、參數說明、錯誤碼說明、更新記錄
- 產品功能介紹、解決方案頁、功能說明頁
- 操作手冊、疑難排解、維運 Runbook、安全說明、FAQ
- 介面文案、按鈕文案、導覽標籤、提示資訊

程式碼常值/字面值 (Literal)、JSON 鍵名、URL、API 路徑、資料庫欄位名稱、命令、設定項和其他機器可讀識別符號不屬於自然語言改寫範圍。

## 事實保真

文案最佳化不能改變事實。不得自行增加原文沒有的日期、數字、單位、處理期限、SLA、產品功能、前置條件、因果關係或確定性結論，也不能刪除適用範圍、例外、風險和失敗處理。資料不足時，應保留原意或明確標記待確認。

## 核心規則概覽

這份 Skill 主要涵蓋以下規則：

- 中文引號統一使用直角單引號「」或直角雙引號『』
- 預設避免不必要的直接稱呼；專案語氣規範可以覆寫此規則
- 在可見正文中處理中文與英文、數字之間的留白
- 避免機械直譯 `Success`、`Invalid`、`Bad Request` 等英文狀態詞
- 避免常見網路黑話，如 `賦能`、`抓手`、`閉環`、`打通`
- 對操作、疑難排解和維運文件套用受控中文技術寫作方法

受控中文技術寫作著重術語一致、條件先於動作、步驟只有一個主要動作，以及執行者、對象和結果明確。這套方法受 ASD-STE100 啟發，但不是 ASD-STE100 的中文版本，也不表示輸出符合 ASD-STE100。

完整規範請閱讀 [SKILL.md](./skills/tech-doc-style-chinese-tw/SKILL.md)。詳細規則會依任務讀取：

- [術語與排版](./skills/tech-doc-style-chinese-tw/references/terminology-and-typography.md)
- [API 狀態與錯誤文案](./skills/tech-doc-style-chinese-tw/references/api-status.md)
- [受控中文技術寫作](./skills/tech-doc-style-chinese-tw/references/controlled-technical-chinese.md)

## 儲存庫結構

```text
tech-doc-style-chinese/
├── README.md
├── skills/
│   └── tech-doc-style-chinese-tw/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   ├── api-status.md
│       │   ├── controlled-technical-chinese.md
│       │   └── terminology-and-typography.md
│       └── scripts/
│           └── lint_copy_rules.py
└── tests/
    ├── test_lint_copy_rules.py
    └── test_skill_structure.py
```

各檔案的作用：

- `skills/tech-doc-style-chinese-tw/SKILL.md`：正式技能入口，供 Codex、Claude Code 等 Agent 使用
- `README.md`：GitHub 儲存庫首頁說明
- `skills/tech-doc-style-chinese-tw/agents/openai.yaml`：技能顯示中繼資料
- `skills/tech-doc-style-chinese-tw/references/`：依任務讀取的詳細規則
- `skills/tech-doc-style-chinese-tw/scripts/lint_copy_rules.py`：輕量檢查器
- `tests/test_lint_copy_rules.py`：檢查器迴歸測試

## 使用範例

可在任務中明確呼叫：

```text
Use $tech-doc-style-chinese-tw to rewrite this Taiwan Chinese technical copy.
```

也可以直接在相關任務中觸發，例如：

- 重寫中文技術文案
- 整理 FAQ
- 最佳化 API 文件措辭
- 最佳化活動到達頁 (Landing Page) 中文文案


## 如何設定專案覆寫規則

這份 Skill 只收錄通用規則，不把特定專案的版本顯示方式、品牌語氣、術語表或資訊架構寫死在核心規範中。

如果專案有自己的約定，請在目標專案中建立獨立的覆寫規則（例如在 `AGENTS.md`、`CONTEXT.md` 或專案設定中）。

這類覆寫規則適合放：

- 版本顯示方式
- 品牌或術語偏好
- 文件結構偏好
- 目前專案特有範例

## 輕量檢查與 CI

儲存庫內建一個不需額外相依套件的輕量檢查指令碼，用於檢查常見規則。結果分為：

- `error`：高度確定的錯誤，預設以非零結束狀態碼結束
- `warning`：需視語境判斷的可疑表達，需要人工確認
- `style`：專案風格和術語偏好

檢查器會保護程式碼區塊、行內程式碼、URL、Markdown 連結目標，以及單段或多段 API 路徑。`截止日期`、`登陸月球`、`配製溶液`、`H5` 等需視語境判斷的詞，不再視為確定錯誤。

本機執行：

```bash
python3 skills/tech-doc-style-chinese-tw/scripts/lint_copy_rules.py
```

僅檢查指定檔案或目錄：

```bash
python3 skills/tech-doc-style-chinese-tw/scripts/lint_copy_rules.py \
  README.md skills/tech-doc-style-chinese-tw/
```

將警告和風格提示也作為失敗處理：

```bash
python3 skills/tech-doc-style-chinese-tw/scripts/lint_copy_rules.py \
  --strict skills/tech-doc-style-chinese-tw/
```

忽略單行檢查：

```markdown
需要保留的原文 <!-- copy-lint-disable-line -->
```

執行迴歸測試：

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions 設定檔為 `.github/workflows/skill-lint.yml`，會在 `pull_request` 和 `main` 分支 `push` 時自動執行。


## License

本專案採用 MIT License。

詳見 [LICENSE](./LICENSE)。
