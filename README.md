# learns

个人学习与实践仓库。它不是资源收藏夹，而是一套把“想学”推进到“能解释、能练习、能交付、能复盘”的记录系统。

仓库保持根目录平铺结构，方便搜索、预览和直接编辑。当前内容来自本次可见 ChatGPT 对话与已经检查过的 GitHub 项目历史；未读取到的旧对话不会被写成事实。

## 从这里开始

| 文件 | 用途 |
|---|---|
| `now.md` | 当前建议的启动周期和本周完成标准 |
| `progress.md` | 各主题已有证据、主要缺口和下一件成果 |
| `inbox.md` | 暂存新想法，避免打断当前学习 |
| `learning-system.md` | 状态、证据等级、工作流和复盘规则 |
| `chat-history.md` | 当前可见对话中的决定和主题 |
| `github-history.md` | 已检查项目的实践证据和待复盘问题 |
| `weekly-review.md` | 每周复盘模板 |
| `project-retrospective.md` | 从已有项目提炼可迁移知识 |
| `note-template.md` | 单篇学习笔记模板 |
| `publish.md` | 下载后自行推送到 GitHub |

## 核心主题

| 主题 | 文件 | 当前方向 |
|---|---|---|
| 英语 | `english.md` | 建立可测量的听说读写和发音输出 |
| 健身教练 | `fitness-coach.md` | 从动作知识走向安全评估、计划和带练能力 |
| 金融投资 | `finance-investing.md` | 建立现金流、养老金、资产配置和风险框架 |
| Python | `python.md` | 从已有 Agent 与转录项目提炼工程能力 |
| SQL | `sql.md` | 使用真实学习数据库练习查询和分析 |

`swift-apple.md`、`ai-agents.md`、`web-product.md`、`health-sleep.md`、`data-analytics.md` 来自已有项目实践，暂时作为复盘池，不与五个核心主题争抢注意力。

## 工作流

新想法先写进 `inbox.md`，每周只选择一个主要交付物；学习时使用 `learning_tracker.py` 记录时长、方式、结果和信心；完成笔记或代码后更新 `progress.md`；周末填写 `weekly-review.md`；已有项目统一使用 `project-retrospective.md` 提炼知识。

## 学习记录工具

仓库附带一个只使用 Python 标准库的 SQLite 学习记录 CLI，并配有数据模型、演示数据、SQL 练习和单元测试。

```bash
python3 learning_tracker.py init
python3 learning_tracker.py add --topic Python --minutes 45 --kind project --result "完成 SQLite 初始化" --confidence 3
python3 learning_tracker.py summary --days 30
python3 learning_tracker.py export --output learning-sessions.csv
python3 -m unittest -v
```

需要演示数据时运行：

```bash
python3 learning_tracker.py seed
sqlite3 learns.db < sql-practice.sql
```

## 记录规则

每条结论注明来源为 `chat`、`github`、`external` 或 `own`。技术项目只能证明做过相关实践，不能自动证明已经掌握对应学科。任何“完成”都需要留下可检查产出，例如录音、文章、查询、测试、模型或复盘。同一时间最多保留两个项目型主题，英语可以作为日常维护习惯。
