# Agent 反向面试 · 学习进度

> **视角**：我是学习者（对话里扮演面试官）。  
> 这里记录的是：**面试 AI 候选人的过程中，我学到了什么、还卡在哪里、下一步怎么验证**。  
> **不是**面试评分表，**不是**候选人表现复盘，**不是**面经答案汇编。

证据等级沿用仓库约定：`E0` 想学 → `E1` 能解释 → `E2` 能练习 → `E3` 能交付 → `E4` 能迁移。  
来源标签：`chat` / `github` / `external` / `own`。

源码锚点写相对路径，例如：`pi/packages/agent/...`、`codex/codex-rs/...`、`grok-build/crates/...`。

---

## 当前焦点

| 字段 | 内容 |
|---|---|
| 状态 | `active` |
| 主线 | 用反向面试啃透 coding agent harness（pi / codex / grok-build） |
| 本阶段目标 | 能自己画出通用 agent loop，并能在至少一个仓库指出对应实现 |
| 当前证据等级（自评） | E0–E1（有项目接触，尚未用三份源码形成可迁移解释） |
| 下一轮想问的主题 | （面试开始后填写，例如：停止条件 / tool schema / sandbox） |

---

## 已建立的心智模型

> 只写**我已经能用自己的话讲清**的东西。不确定的放「开放问题」。

### Agent 是什么（工作定义）

_（待第一轮后填写）_

### 一次工具调用链路

_（待填写：消息 → 模型 → tool_call → 执行 → 结果写回 → 再推理）_

### 可靠 Agent 与“会调工具的聊天”的差别

_（待填写）_

---

## 学习日志

按时间倒序追加。每一轮面试结束后更新一节。

### 模板（复制用）

```markdown
### YYYY-MM-DD · 第 N 轮 · <主题>

- 本轮问题轴：
- 我原有理解：
- 被纠正或补全后的理解：
- 新概念（用自己的话）：
- 源码锚点：
  - `path` — 我从中看到了什么
- 可迁移结论（E?）：
- 边界 / 反例 / 失效条件：
- 仍模糊：
- 主动回忆题（合上对话后自答）：
  1.
  2.
  3.
- 下一次验证：做什么、通过标准是什么
```

### 日志正文

### 2026-07-29 · 第 1 轮 · 自我介绍 / 项目全景

- 本轮问题轴：候选人自我介绍、工作经验线、四个简历项目简介
- 我原有理解：知道要面 agent 应用开发，但还没把「能力线 → 项目 → 可追问点」对齐
- 被纠正或补全后的理解：
  - 候选人履历**只认四个项目**：Pi / Codex / Grok Build / AnythingLLM
  - 经验应按**机制能力线**讲（loop、sandbox、routing、compaction、RAG），不是空泛产品黑话
  - 深挖时应按主题选项目，而不是四个仓库平铺
- 新概念（用自己的话）：
  - **Agent 应用开发** ≈ 把 LLM + 工具 + 执行环境 + 上下文治理 + 扩展拼成可上线系统
  - **能力 → 项目映射**是反向面试的导航图（loop→Pi；sandbox→Codex；compaction→Grok；RAG/routing→AnythingLLM）
- 源码锚点：
  - `pi/` — multi-provider + agent loop + TUI/extensions（尚未下钻文件）
  - `codex/` — sandbox / execpolicy / apply-patch（尚未下钻）
  - `grok-build/` — tool runtime / compaction / MCP（尚未下钻）
  - `anything-llm/` — RAG 管线 + model router（尚未下钻）
- 可迁移结论（E1）：四个项目不是重复造轮子，而是同一问题在不同约束下的切片（TS harness vs Rust 本地执行安全 vs 压缩/MCP vs RAG 路由）
- 边界 / 反例 / 失效条件：
  - 不能把学习仓库笔记 / 用户本机其它项目当成候选人履历
  - 介绍阶段没有源码路径细节是正常的；实现题必须读文件再答
- 仍模糊：候选人具体 ownership 边界；各项目「自己写的 vs 仓库客观存在」尚未对源码校准
- 主动回忆题（合上对话后自答）：
  1. 四个项目各一句话分别解决什么问题？
  2. 若只问 tool-call 数据流，应优先打开哪个项目？
  3. 沙箱 / 上下文压缩 / 模型路由分别挂哪个项目？
- 下一次验证：选一条能力线（建议 agent loop 或模型路由），让候选人画出状态/数据流并指出至少一个源码路径；通过标准=能说出停止条件或 fallback，且路径可核对

### 2026-07-29 · 第 2 轮 · AnythingLLM RAG / 向量库 / 文档切分

- 本轮问题轴：RAG 用什么库、多 provider 是否都熟、Chroma 本地部署、业界向量库与 RAG 服务、embedding vs chat、文档/多模态解析与切分、企业自建 AI 中台
- 我原有理解：知道 RAG = 检索 + 生成，向量库有很多名字，但对「默认选型 / 部署方式 / 切分与格式差异」还是模糊
- 被纠正或补全后的理解：
  - AnythingLLM 向量库可插拔，**默认 LanceDB**；`VECTOR_DB` 驱动 `getVectorDbClass`
  - 多库支持 ≠ 每个都一样深；Chroma 是一等公民实现，有 normalize / cosine / 文档级删除
  - Chroma **不内置在 compose 里**，要单独起服务再配 `CHROMA_ENDPOINT`
  - **embedding 找材料，chat 写答案**；换 chat 不必重灌，换 embedding 通常要重灌
  - 文档链路是 **先 parser 成文本，再统一 RecursiveCharacterTextSplitter**；格式差在「能不能变成字」
  - 企业自建中台方向对：门户/权限/模型网关自建，向量库与解析可复用；业务线隔离建议「租户 → 多知识库 → 助手」
- **整体链路（文档入库）**：
  1. Collector 按扩展名解析（`collector/processSingleFile`）→ 抽出 `pageContent` 文本
  2. Server 入库时切分 + embed（`TextSplitter` + `addDocumentToNamespace`）
  3. 默认 RecursiveCharacterTextSplitter：`chunkSize`≈1000、`overlap`≈20，可被系统设置覆盖，且不超过 embedding 模型上限
  4. **用户 chat 消息**一般不按文档那套切：query 整段 embed 去检索；历史按条数/`messageLimit` 取
- **切分策略本身（和格式无关）** — `server/utils/TextSplitter/index.js`：
  - LangChain RecursiveCharacterTextSplitter
  - 尽量在段落/换行等边界拆
  - 可选 chunk header：标题、source 等元数据拼进每段前面
  - 部分 embedder 还有 `chunkPrefix`
  - **格式差异主要在「能不能变成字」；变成字之后，切法一套**
- **各格式实际怎么处理**：

  | 类型 | 怎么解析 | 切分/效果 |
  |---|---|---|
  | 纯文本 / md / txt | `asTxt`，直接当文本 | 正常 recursive chunk，最稳 |
  | 标准 PDF（有文字层） | `asPDF`：pdf-parse 按页抽文本，再拼成一篇 | 页信息解析时用过，最终常合成一份 pageContent 再切 |
  | 扫描 PDF | 文本层空 → `OCRLoader.ocrPDF`（Tesseract） | 能 OCR 出字才能进库；慢、吃 CPU，大文件更痛 |
  | Word 正常文字 | `asDocx`（DocxLoader）抽文本 | 和 txt 类似 |
  | Word 里全是截图 | docx 路径**不抽图、不做 OCR** | 文本空 → 失败：`No text content found` |
  | 图片 png/jpg | `asImage` → OCR | 有字才能用 |
  | Excel | `asXlsx`：单元格→CSV；**默认每 sheet 一份文档** | 表格数字/文字可以；**图表、公式图基本进不来** |
  | 20MB+ 大文件 | 无按体积特殊策略；解析完一大段再按 chunkSize 切 | 瓶颈在解析/OCR/embed 时间与向量条数 |
  | 10KB 小文件 | 同样流程；可能就 1 个 chunk | 没问题 |

- 新概念（用自己的话）：
  - **托管的钱与锁定**：钱 = 用量账单；锁定 = API/数据模型迁出成本高（以 Pinecone 为例）
  - **Chroma 起步 / Qdrant 长跑**：轻量私有化 vs 过滤与生产向
  - **解析管线 ≠ 切分策略**：OCR/表格/截图是 parser 问题；chunkSize/overlap 是文本切分问题
- 源码锚点：
  - `anything-llm/server/utils/helpers/index.js` — `getVectorDbClass`，默认 `lancedb`
  - `anything-llm/server/utils/vectorDbProviders/chroma/index.js` — connect / normalize / cosine / query / DocumentVectors 删除
  - `anything-llm/server/utils/TextSplitter/index.js` — RecursiveCharacterTextSplitter，chunkSize/overlap，header meta
  - `anything-llm/collector/processSingleFile/index.js` — 按扩展名选 converter
  - `anything-llm/collector/processSingleFile/convert/asPDF/index.js` — 空文本走 OCR
  - `anything-llm/collector/processSingleFile/convert/asDocx.js` — 只抽文本，不 OCR 截图
  - `anything-llm/collector/processSingleFile/convert/asXlsx.js` — 单元格→CSV，sheet 可拆文档
  - `anything-llm/collector/processSingleFile/convert/asImage.js` — 图片 OCR
  - `anything-llm/collector/utils/OCRLoader/index.js` — 扫描 PDF / 图片 Tesseract
  - `anything-llm/docker/.env.example` — `VECTOR_DB=chroma`、`CHROMA_ENDPOINT`
- 可迁移结论（E2 偏 E1）：
  - 选型先问约束（已有 PG？要 filter？私有化？量级？）再选库，不是背品牌榜
  - 企业 RAG 体验差，往往是权限/灌库反馈/引用可解释，不只是「换个向量库」
  - 截图 Word、Excel 图表、复杂扫描件是 Anything 明确短板；自建要在 parser 层按模态分支
- 边界 / 反例 / 失效条件：
  - 换 `VECTOR_DB` 会 reset，不是热迁移
  - Chroma collection 名有硬规则，workspace slug 会 normalize
  - Word 全截图：docx 路径抽不出字 → 失败，不是 chunk 参数能救
  - Excel 图/公式图进不了向量，只有单元格值
- 仍模糊：
  - 公司级多业务线权限模型（文档级 vs 库级）如何最小落地
  - hybrid（向量+关键词）在 Anything 里具体开到哪一层
  - 大文件（20MB+）异步队列与失败重试的推荐实现
- 主动回忆题（合上对话后自答）：
  1. Anything 默认向量库是什么？Chroma 要配哪几个 env？
  2. embedding 和 chat 各在 RAG 哪一步？换哪个要重灌？
  3. 扫描 PDF、纯截图 Word、带图表 Excel 在 collector 里分别会怎样？
- 下一次验证：自己顺着「上传 PDF → collector → TextSplitter → chroma add → similarity query」画 6～8 步数据流，每步标一个真实路径；通过标准=能指出扫描 PDF 与截图 Word 的分叉

---

## 当前焦点（本轮后更新）

| 字段 | 内容 |
|---|---|
| 状态 | `active` |
| 主线 | AnythingLLM RAG 管线（向量库 / 解析切分 / 企业中台）+ 仍保留 coding agent harness |
| 本阶段目标 | 能讲清 RAG 入库与检索主链路，并指出 Chroma + TextSplitter + collector 锚点 |
| 当前证据等级（自评） | E1–E2（RAG 主链路有路径；agent loop 仍待下钻） |
| 下一轮想问的主题 | 模型路由（AnythingLLM router sticky/fallback）或 上传→检索完整数据流对质 |

---

## 概念卡片

> 稳定下来的概念，从日志提炼到这里。一条一个卡片，避免只堆聊天记录。

| 概念 | 我的一句话定义 | 证据等级 | 源码或例子 | 反例 / 边界 |
|---|---|---|---|---|
| embedding vs chat | embedding 把文本变向量负责检索；chat 负责生成回答 | E2 | EmbeddingEngines / AiProviders | 换 embed 通常要重灌；换 chat 一般不用 |
| 向量库可插拔 | `VECTOR_DB` 选 provider，默认 LanceDB | E2 | `server/utils/helpers/index.js` `getVectorDbClass` | 切换会 reset，非热迁 |
| Chroma 接入 | 独立部署 + endpoint；collection 名 normalize；cosine | E2 | `vectorDbProviders/chroma/index.js` | URL 勿尾斜杠；slug 可能被改名 |
| 托管的钱与锁定 | 钱=用量费；锁定=迁出 API/数据路径成本高 | E1 | Pinecone 类比 | 自建也有运维绑定 |
| 解析后再切分 | 格式→文本（collector），再 Recursive chunk（TextSplitter） | E2 | `collector/processSingleFile` + `TextSplitter` | 截图 Word 解析失败；Excel 图丢失 |
| 企业 AI 中台 | 门户/权限/模型网关自建；向量库可插拔；业务线隔离 | E1 | chat 经验 | 别一上来重写 chunk 算法 |

---

## 三仓库对照（学习用）

同一问题轴，三份实现怎么回答。格子空着 = 还没学到。

| 问题轴 | pi | codex | grok-build | 我的对比结论 |
|---|---|---|---|---|
| agent loop 在哪 | | | | |
| 工具如何注册与校验 | | | | |
| 权限 / sandbox | | | | |
| 上下文装配与压缩 | | | | |
| 扩展（skills/plugins/MCP…） | | | | |
| 如何测 agent 行为 | | | | |
| 失败与取消语义 | | | | |

---

## 开放问题（ ent 里的洞）

- [ ] agent loop 的停止条件有哪些类型（正常 / 预算 / 用户中断 / 工具失败）？
- [ ] tool schema 如何约束模型，约束失败时运行时怎么办？
- [ ] 并行 tool call 的结果顺序与写回语义？
- [ ] sandbox 与“提示词里写请小心”的本质差别？
- [ ] 上下文压缩丢的是什么，如何发现静默错误？
- [ ] 怎样做不烧真模型钱的回归（mock provider / transcript）？
- [ ] AnythingLLM hybrid / vectorSearchMode 具体行为？
- [ ] 多业务线权限：库级够不够，何时要文档级 ACL？
- [ ] 大文件 OCR/解析的异步队列与超时策略怎么做最小可用？

---

## 可检查产出（学习交付物）

完成后勾选，并链到具体文件或笔记位置。

- [ ] 手绘/markdown：通用 tool-call 数据流图  
- [ ] 手绘/markdown：agent 状态机（含异常边）  
- [ ] 一篇：pi 上跟完一次最小 tool 循环（带路径）  
- [ ] 一篇：codex sandbox 或 execpolicy 机制笔记  
- [ ] 一篇：三仓库扩展模型对照表（填满上表至少 4 行）  
- [ ] 一组失败案例：超时、工具抛错、schema 不符、用户取消  
- [ ] 主动回忆：不看资料讲 10 分钟 agent loop + 安全边界  

---

## 与全局学习系统的衔接

- 主题地图：根目录 `ai-agents.md`  
- 证据与状态规则：`learning-system.md`  
- 有可检查产出时：回写 `progress.md`，必要时记入 `learning_tracker.py`  
- 角色与面试规则：`packages/AGENTS.md`  

---

## 更新约定

1. **每轮面试结束** → 追加一条「学习日志」，并视情况更新概念卡片 / 对照表 / 开放问题。  
2. **只记录我学会的**，不记录“候选人答得怎样”。候选人的好答案应改写成**我的理解**。  
3. 连续两轮没碰的开放问题，要么降级删除，要么变成下轮固定题。  
4. 源码结论必须能指到路径；指不到就标 `chat`/`own` 并保持 E0–E1。  
