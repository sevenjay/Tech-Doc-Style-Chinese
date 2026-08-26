# Chinese Tech Doc Style

本專案只是一份面向繁體中文技術文件、產品文案與介面文案的寫作 Skill。

這份 Skill 的目標很明確：中文技術寫作應更剋制、更準確、更易讀。不追求宣傳感，也不試圖把所有內容都寫成統一範本，而是著重處理幾類常見問題：

- 中文技術文案容易空泛、重複、宣傳化
- 中文與英文、數字混合排版時可讀性差
- 常見英文狀態詞和錯誤詞容易被機械直譯
- 文件首頁、解決方案頁、API 說明頁、FAQ 的資訊密度和結構經常失衡

如果需要一套適合中文技術文件的基礎寫作規範，這份 Skill 可以直接拿來使用，或是作為參考。

## 適用情境

本 Skill 適合以下內容：

- 文件首頁、著陸頁、第一屏文案
- API 文件、參數說明、錯誤碼說明、更新記錄
- 產品功能介紹、解決方案頁、功能說明頁
- 介面文案、按鈕文案、導覽標籤、提示資訊

不適合以下內容：

- 程式碼字面量
- JSON 鍵名
- URL
- API 路徑
- 資料庫欄位名稱
- 其他機器可讀識別符號

## 核心規則概覽

這份 Skill 主要涵蓋以下規則：

- 改寫時保留事實、限制、條件和確定程度
- 中文引號統一使用直角引號 `「」`
- 預設避免不必要的直接稱呼；專案語氣規範可以覆寫此規則
- 在可見正文中處理中文與英文、數字之間的留白
- 避免機械直譯 `Success`、`Invalid`、`Bad Request` 等英文狀態詞
- 避免常見網路黑話，如 `賦能`、`抓手`、`閉環`、`打通`
- 對操作、疑難排解和維運文件套用受控中文技術寫作方法

完整規範請閱讀：

- [SKILL.md](./SKILL.md)
- [公開說明稿](./NoCode-Skill.md)

## 儲存庫結構

```text
tech-doc-style-chinese/
├── SKILL.md
├── NoCode-Skill.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── api-status-copy.md
│   ├── controlled-technical-chinese.md
│   ├── project-overrides-example.md
│   └── terminology-and-typography.md
├── scripts/
│   └── lint_copy_rules.py
└── tests/
    └── test_lint_copy_rules.py
```

各檔案的作用：

- `SKILL.md`：正式技能入口，供 Codex、Claude Code 等 Agent 使用
- `NoCode-Skill.md`：對外說明稿，適合公開閱讀和分享
- `README.md`：GitHub 儲存庫首頁說明
- `agents/openai.yaml`：技能顯示中繼資料
- `references/`：依任務讀取的詳細規則和專案覆寫範本
- `scripts/lint_copy_rules.py`：輕量檢查器
- `tests/test_lint_copy_rules.py`：檢查器迴歸測試

## 如何在 Codex 中使用

### 使用 npx 安裝（推薦）

如果本機有 Node.js 環境，可直接用 `npx skills` 安裝：

```bash
# 直接安裝
npx skills add https://github.com/Fenng/tech-doc-style-chinese
```

如需無互動並以全域方式安裝到 Codex，可使用：

```bash
npx -y skills add https://github.com/Fenng/tech-doc-style-chinese -a codex -g
```

參數說明：

- `-a codex` 表示安裝到 Codex agent
- `-g` 表示全域安裝（使用者層級），不加則安裝到目前專案範圍
- `-y` 表示跳過互動確認，便於自動化執行

安裝後建議重啟 Codex，以確保新 Skill 被載入。

### 依 Release 安裝（推薦）

固定版本安裝，方便團隊重現相同環境：

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"

git clone --depth 1 --branch <release-tag> \
  https://github.com/Fenng/tech-doc-style-chinese.git \
  "$CODEX_HOME/skills/tech-doc-style-chinese"
```

`<release-tag>` 可替換為已釋出版本，例如 `v0.1.0.2.4`。

### 本地目錄安裝（開發情境）

如果正在本地修改或除錯，可直接複製目錄：

```bash
mkdir -p "$CODEX_HOME/skills/tech-doc-style-chinese"
cp -R ./* "$CODEX_HOME/skills/tech-doc-style-chinese/"
```

安裝後可快速驗證：

```bash
test -f "$CODEX_HOME/skills/tech-doc-style-chinese/SKILL.md" && echo "installed"
```

安裝完成後，可在任務中明確呼叫：

```text
Use $tech-doc-style-chinese to rewrite this Chinese technical copy.
```

也可以直接在相關任務中觸發，例如：

- 重寫中文技術文案
- 整理 FAQ
- 最佳化 API 文件措辭
- 最佳化著陸頁中文文案

## 如何在 Claude Code 中使用

### 直接讓 Claude Code 安裝（最簡單）

如果目前 Claude Code 環境支援安裝 Skills，可讓它讀取本儲存庫並安裝：

```text
請安裝這份 Skill：https://github.com/Fenng/tech-doc-style-chinese
```

這種方式較省事，但要安裝在專案層級或全域範圍，取決於 Claude Code 當時的能力與判斷。團隊協作或需要寫入文件、CI 的情境，建議使用下列 npx 命令。

### 使用 npx 安裝（推薦）

如果本機有 Node.js 環境，可直接用 `npx skills` 安裝：

```bash
# 安裝到目前專案
npx skills add https://github.com/Fenng/tech-doc-style-chinese -a claude-code
```

如需無互動並以全域方式安裝到 Claude Code，可使用：

```bash
npx -y skills add https://github.com/Fenng/tech-doc-style-chinese -a claude-code -g
```

參數說明：

- `-a claude-code` 表示安裝到 Claude Code
- `-g` 表示全域安裝（使用者層級，寫入 `~/.claude/skills/`），不加則安裝到目前專案範圍（寫入 `./.claude/skills/`）
- `-y` 表示跳過互動確認，便於自動化執行

安裝後建議重啟 Claude Code，以確保新 Skill 被載入。

### 本地目錄安裝（開發情境）

如果正在本地修改或除錯，可直接複製目錄：

```bash
mkdir -p ~/.claude/skills/tech-doc-style-chinese
cp SKILL.md ~/.claude/skills/tech-doc-style-chinese/
cp -R references ~/.claude/skills/tech-doc-style-chinese/
```

安裝後可快速驗證：

```bash
test -f ~/.claude/skills/tech-doc-style-chinese/SKILL.md && echo "installed"
```

Claude Code 會根據 `SKILL.md` 裡的 `description` 自動判斷何時呼叫該 Skill，無須手動觸發，例如：

- 重寫中文技術文案
- 整理 FAQ
- 最佳化 API 文件措辭
- 最佳化著陸頁中文文案

## 如何設定專案覆寫規則

這份 Skill 只收錄通用規則，不把特定專案的版本顯示方式、品牌語氣、術語表或資訊架構寫死在核心規範中。

如果專案有自己的約定，請在目標專案中建立獨立的覆寫規則檔。可以從以下範本開始：

- `references/project-overrides-example.md`

這類覆寫規則檔適合放：

- 版本顯示方式
- 品牌或術語偏好
- 文件結構偏好
- 目前專案特有範例

範本本身不包含預設生效的業務術語。不要把範例檔案當成目標專案約定。

## 輕量檢查與 CI

儲存庫內建一個不需額外相依套件的輕量檢查指令碼，用於檢查常見規則。結果分為：

- `error`：高度確定的錯誤，預設以非零結束碼結束
- `warning`：需視語境判斷的可疑表達，需要人工確認
- `style`：專案風格和術語偏好

檢查器會保護程式碼區塊、行內程式碼、URL、Markdown 連結目標，以及單段或多段 API 路徑。`截止日期`、`登陸月球`、`配製溶液`、`H5` 等需視語境判斷的詞，不再視為確定錯誤。

本地執行：

```bash
python scripts/lint_copy_rules.py
```

僅檢查指定檔案或目錄：

```bash
python scripts/lint_copy_rules.py SKILL.md NoCode-Skill.md references/
```

將警告和風格提示也作為失敗處理：

```bash
python scripts/lint_copy_rules.py --strict SKILL.md references/
```

忽略單行檢查：

```markdown
需要保留的原文 <!-- copy-lint-disable-line -->
```

執行迴歸測試：

```bash
python -m unittest discover -s tests -v
```

GitHub Actions 設定檔為 `.github/workflows/skill-lint.yml`，會在 `pull_request` 和 `main` 分支 `push` 時自動執行。

## 釋出建議

如果只是公開分享規範內容：

- 保留 `NoCode-Skill.md`
- 用 `README.md` 做儲存庫首頁說明

如果希望他人能直接安裝使用：

- 保留 `SKILL.md`
- 保留 `agents/openai.yaml`
- 在儲存庫裡明確目錄結構和安裝方式

<!-- 作者：Fenng（GitHub：@Fenng） -->

## License

本專案採用 MIT License。

詳見 [LICENSE](./LICENSE)。
