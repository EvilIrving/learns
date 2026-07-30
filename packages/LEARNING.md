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
| 主线 | coding agent harness：**prompt + tools 组装**（Grok vs Codex）；旁路仍保留 Agentic RAG / tool 化检索 |
| 本阶段目标 | 能对比 Grok「Agent build 定 toolset + 模板渲染 system」vs Codex「每 turn plan tools + base_instructions/world-state 分片」；能指到 Sampler/Actor 职责 |
| 当前证据等级（自评） | E2（AnythingLLM 旋钮→接口→UI 字段；Grok/Codex prompt+tools 概念对照）；Pi agent loop 仍待下钻 |
| 下一轮想问的主题 | Codex turn 内 tool 执行 + sandbox 边界；或 Grok compaction 与 system 保留；或 Pi agent-loop 停止条件 |

---

## 已建立的心智模型

> 只写**我已经能用自己的话讲清**的东西。不确定的放「开放问题」。

### Agent 是什么（工作定义）

_（待第一轮后填写）_

### 一次工具调用链路

消息进 context → LLM（带 tools schema）→ 若有 `tool_call` → runtime 执行 handler → `tool_result` 写回 messages → 再调 LLM → 直到无 tool、给出最终回答。  
检索只是 tools 之一：`search_docs` / `rag-memory` / hosted `file_search` / `attachment_search`。

### 可靠 Agent 与“会调工具的聊天”的差别

| 会调工具的聊天 | 更可靠的 Agent |
|---|---|
| 有 tool schema 就能叫 | 何时用何工具有清晰分工（业务 MCP vs 文档 search） |
| 调完讲一段话 | 可执行动作、可鉴权、失败可改道 |
| 每轮强制检索也叫「智能」 | 按需检索；状态/流程走系统真源 |

### Pipeline 知识库问答 vs Agentic RAG（本轮定稿）

| | Pipeline 知识库问答 | Agentic RAG |
|---|---|---|
| 检索触发 | 应用几乎每轮强制 | 模型/runtime 按需 tool call |
| 产品隐喻 | 企业搜索 + 聊天框主入口 | agent 的一个能力 |
| 真源假设 | 文档 ≈ 现行 | 文档可选；系统/MCP 优先 |
| 终态 | 自然语言答案 | 可再调动作工具，不止问答 |

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

### 2026-07-30 · 第 4 轮 · 检索接口字段 / Grok 分层与命名 / prompt+tools（Grok vs Codex）

- 本轮问题轴：
  1. AnythingLLM 检索相关「原始接口」有哪些字段，最终渲染到界面用了哪些  
  2. 是否「底层都是 curl HTTPS，再拼一层」  
  3. Grok Build 项目整体怎么做（对照 RAG 产品）  
  4. 为何叫 **Sampler**；为何叫 **Actor-based**；`spawn` 是什么  
  5. Grok 如何组装 **prompt + tools**  
  6. Codex 如何考虑 prompt + tools；是否与 Grok 一样  

- 我原有理解（进本轮前）：
  - 第 3 轮已懂 topN / threshold / rerank 语义与 Lance 默认/精排路径  
  - 模糊认为「前端 → 后端 → 出网 API」差不多都是 curl 拼字段  
  - 知道 Grok 是 coding agent / compaction，但没拆 Sampler、Actor、prompt 组装  
  - 直觉上 coding agent 的 prompt+tools 各仓库应该差不多  

- 被纠正或补全后的理解（按讨论块）：

#### A. AnythingLLM：接口 ≠ 全 curl；UI 字段是裁剪后的

  - **不是**「UI → curl 第三方 → 拼字段」；是 **UI → 自家 REST/SSE → Server 读 workspace 配置 → 向量库（Lance 本地或云 HTTP）→（可选本地 rerank）→ LLM**  
  - 三个旋钮是 **workspace 配置**，聊天 body **不带** topN/threshold/rerank；服务端读库后塞进 `performSimilaritySearch`  

  **设置页（可写/只读）**

  | 字段 | 接口 | UI |
  |---|---|---|
  | `topN` | GET workspace / POST `.../update` | MaxContextSnippets number |
  | `similarityThreshold` | 同上 | select 固定 0 / 0.25 / 0.5 / 0.75 |
  | `vectorSearchMode` | 同上（`default`\|`rerank`） | Search Preference；**仅 LanceDB 渲染** |
  | `slug` / 向量条数 | 只读 + totalIndexes | 展示用 |

  **聊天引用（SSE `sources`）UI 真用到的**：`id, title, text, chunkSource, score`（`combineLikeSources`）；元数据里还有 url/author 等多数不进小胶囊。  
  **独立 API** `POST /v1/workspace/:slug/vector-search`：入参 `query, topN, scoreThreshold`；rerank 仍跟 workspace；出参已整形 `results[{id,text,metadata,distance,score}]`。

#### B. Grok Build：不是 RAG 产品；分层与命名

  | | AnythingLLM | Grok Build |
  |---|---|---|
  | 形态 | Web 知识库问答 | 本机 Rust TUI / headless / ACP coding agent |
  | 上下文 | 向量 topN 等 | 工具读仓库 + compaction |
  | 主出网 | Embed + LLM + 可选云向量 | **Sampler** 调模型；工具默认打本机 |

  主路径：`shell(session) → 组装 prompt/tools → sampler(HTTPS) → tool 执行 → transcript → 满了 compact`。

  - **Sampler**：ML 语义「从模型 sample 一轮输出」；crate 描述为 sampling/inference 层。HTTPS 是落地方式，命名不是「网络模块」。职责：stream、retry、cancel；**不**碰 shell/tools/TUI。  
  - **Actor-based**：Actor 模型——**独占状态 + mailbox（mpsc 命令）+ cloneable Handle**；actor 串行处理命令，per-request `tokio::spawn` 并行 stream。轻量（tokio task，不是 Actix）。与 hunk-tracker / session actor 同构。  
  - **spawn**：多数是「起异步任务」；`SamplerActor::spawn` / `tokio::spawn` 等。

#### C. Grok 组装 prompt + tools

  **System（偏静态）**  
  - `PromptContext`：base template（Primary/Subagent）+ `prompt_body` + placeholders（os/shell/cwd/date/memory…）+ AGENTS.md 列表  
  - `PromptMode::Extend | Full`；MiniJinja 渲染；`${{ tools.by_kind.* }}` 从 **finalized ToolBridge 注册表**解析工具显示名  
  - Session 启动：`install_system_prompt` → conversation 第一条 System；AGENTS 可作 project_instructions  

  **User 前缀（偏动态）**  
  - `user_message`：`<user_info>`、git status、rules/skills/MCP 说明等  

  **Tools**  
  - `AgentBuilder::build` 时按 definition + feature 加减工具 → `ToolBridge::finalize`  
  - 每 turn：`prepare_tool_definitions` → `ToolSpec`（+ hosted tools / StructuredOutput）→ `chat_state.build_request`  
  - **文本指令**与 **tools 数组**两通道，不全塞一个大 prompt  

#### D. Codex 组装 prompt + tools：概念同构、实现不同构

  Codex 请求体是 `Prompt { base_instructions, input, tools, parallel_tool_calls, output_schema }`：

  | 维度 | Codex | Grok |
  |---|---|---|
  | 指令主路径 | base_instructions + developer 分片 + **world-state** render | 一条 system（模板渲染） |
  | tools 何时定 | **每 turn** `build_tool_router` / PlannedTools | **Agent build** finalize + turn snapshot |
  | 可见性 | exposure / deferred / tool_search | 注册表 + 开关 + plan 过滤 |
  | 产品压力 | 本机执行安全、apply-patch、exec policy | 长会话 TUI、compaction、扩展面 |

  Codex 取舍（候选人口径）：  
  1. 安全不靠 prompt，执行前 policy/sandbox 硬拦  
  2. tools 按 turn plan，贴 feature/MCP/model 变化  
  3. context 用 role 分片，利于测与 compact  
  4. 与 Grok **不对齐实现**，能力可对照、边界按产品问题拆  

- 新概念（用自己的话）：
  - **BFF 自研后端**：前端只打自家 API；出网是子集（LLM/云库），不是一切 curl  
  - **配置旋钮 vs 请求旋钮**：workspace 存 topN 等；聊天请求体不带  
  - **Sampler = 推理采样层**，不是 HTTP client 的别名  
  - **Actor = 状态所有权 + 消息 API**，不是「多线程服务」的笼统说法  
  - **指令通道 vs tools 通道**：system/developer 文本 ≠ ToolSpec 数组  
  - **turn-level tool planning**（Codex）vs **agent-level toolset**（Grok）  

- 源码锚点：
  - `anything-llm/server/models/workspace.js` — writable/validations：topN、threshold、vectorSearchMode  
  - `anything-llm/frontend/.../VectorDatabase/*` — 设置页三个控件  
  - `anything-llm/frontend/.../Citation/index.jsx` — `combineLikeSources` 用到的字段  
  - `anything-llm/server/endpoints/api/workspace/index.js` — vector-search 入参/出参整形  
  - `anything-llm/server/utils/chats/stream.js` / `apiChatHandler.js` — 聊天用 workspace 配置调检索  
  - `grok-build/crates/codegen/xai-grok-sampler/` — SamplerActor、SamplerHandle、SamplingClient  
  - `grok-build/.../xai-grok-agent/src/prompt/context.rs` — PromptContext.render  
  - `grok-build/.../xai-grok-agent/src/builder.rs` — tool_config finalize + system_prompt  
  - `grok-build/.../shell/.../sampler_turn.rs` — prepare_tool_definitions  
  - `grok-build/.../shell/.../turn.rs` — build_request + tools  
  - `codex/codex-rs/core/src/client_common.rs` — `Prompt` 结构  
  - `codex/codex-rs/core/src/session/turn.rs` — `build_prompt`  
  - `codex/codex-rs/core/src/tools/spec_plan.rs` — PlannedTools / build_tool_router  
  - `codex/codex-rs/core/src/session/mod.rs` — build_initial_context_with_world_state  

- 可迁移结论：
  - **E2**：AnythingLLM 旋钮→接口→UI→citations 字段链路可画清；聊天不传三旋钮  
  - **E2**：「底层 curl」要分层说；本地 Lance/本地 rerank 不出网  
  - **E2**：Grok Sampler/Actor 命名各有固定语义，面试能一句话区分  
  - **E2**：coding agent 组装共性 = 文本指令 + tools schema 分离；Grok/Codex **实现策略不同**（模板+build-time toolset vs 分片+turn-time plan）  
  - **E1→E2**：Codex 的 world-state / deferred tools / apply-patch 与安全叙事绑定，读 tool 要连 sandbox  

- 边界 / 反例 / 失效条件：
  - Grok turn 路径里 `tool_definitions_builtins_only` 与 MCP 注册并存，MCP 曝光细节比「全量 defs」更绕，未本轮读透  
  - Codex hosted tools / tool_search 完整数据流未跟完  
  - 四项目「能力可对照」≠「代码可互换」  

- 仍模糊：
  - Grok MCP 何时进入 model_visible tools（与 builtins_only 的精确关系）  
  - Codex compact 后 base_instructions vs world-state 如何重注  
  - Pi 的 prompt+tools 组装是否更接近 Grok 还是更薄  

- 主动回忆题（合上对话后自答）：
  1. AnythingLLM 设置页三个检索字段各自 API 名与默认值？聊天请求带不带？  
  2. 引用 UI 最少用 source 的哪几个字段？  
  3. 为何叫 Sampler 不叫 LLMClient？为何叫 Actor？  
  4. Grok system prompt 里工具名如何写进模板？  
  5. Codex `Prompt` 五个关键字段是什么？tools 在哪一步填？  
  6. 用一张表对比 Grok vs Codex 的 prompt 主路径与 tools 定稿时机。  

- 下一次验证：
  - 任选：跟一次 Codex `run_sampling_request` → tool call → sandbox 拒绝路径；或 Grok 一次 compact 前后 conversation 形态  
  - 通过标准：能不看笔记画出 Grok 与 Codex 各一张「prompt+tools → 模型 → tool 执行」时序，并指出至少一处产品约束导致的实现分叉  

---

### 2026-07-30 · 第 3 轮 · RAG 深挖 / 过时知识 / 检索旋钮 / 知识库问答批判 / Agentic RAG

- 本轮问题轴：
  1. chunk 怎么定、为何 ~1000、为何不更大  
  2. chunk 后是否保留原始文件  
  3. 历史冗余/过时信息如何治（无足够专家人工筛库）  
  4. topN / similarityThreshold / rerank 是什么、怎么做  
  5. 「RAG 过时、大部分场景无意义」  
  6. OpenAI / Anthropic hosted tool（file_search 等）vs AnythingLLM 知识库  
  7. OpenAI file_search / xAI attachment_search 是否比知识库问答更「正确」  
  8. Pipeline 知识库问答是否已死；系统 MCP 是否更好  
  9. 为何认定知识库已死  
  10. Agentic 中 RAG 如何实现、如何当 tool 用  

- 我原有理解（进本轮前）：
  - 第 2 轮已建立：入库 = 解析 → chunk(~1000) → embed → 向量库；检索有 topN 等旋钮  
  - 默认仍把「企业知识库问答」当成 RAG 的正统产品形态  
  - 对 hosted tool 与 pipeline 的差别只有模糊印象  

- 被纠正或补全后的理解（按讨论块）：

#### A. Chunk 设计（工程默认，非理论最优）

  - 默认约 **1000 字符、overlap 20**，LangChain `RecursiveCharacterTextSplitter`  
  - 真正入库前 `determineMaxChunkSize`：`min(配置, embedder.embeddingMaxChunkLength)`，超限强制砍  
  - 选 1k 的理由：检索粒度（一段主题清晰）、与 topN 配套控上下文、跨 embedder 保守默认、文档类型杂时好运维  
  - 不故意再大：多主题冲淡向量、topN 固定时噪声与 token 暴涨、改文档重嵌更粗、撞 embedder 上限  
  - 可调，但改 chunk 会清向量缓存重嵌；overlap 很小，防拦腰切断，不靠大 overlap 装连续  

#### B. 原件是否保留（两层）

  | 层 | chunk 后 | 原因 |
  |---|---|---|
  | 上传二进制（PDF 等） | 可不长期留 | 解析完成即完成使命；审计/重跑解析另说 |
  | 解析全文 JSON（`storage/documents`） | **要留** | pin、改 chunk 重嵌、watch 同步、列表与合规回放 |
  | 向量块（payload 含 `text`） | 检索回答用 | 日常问答靠这一层 |

  - DB 的 workspace 文档记录只存 docpath/metadata，全文在 JSON；删源不能只删向量一边，要完整 purge  

#### C. 过时/冗余信息（不靠专家全量筛）

  - 问题重定义：不是「库零错误」，而是权威优先、可替换可下线、专家只仲裁冲突  
  - 策略：粗规则入主库（来源/路径/时间/类型）→ workspace 隔离冷热 → 活源 watch 同步替换 → pin/阈值/来源偏好 → 线上反馈下线脏源  
  - **禁止**默认五年全量进主库靠模型甄别；**禁止**把「提示词请小心」当安全/真源  

#### D. topN + similarityThreshold + rerank

  | 参数 | 默认（量级） | 作用 |
  |---|---|---|
  | topN | 4 | 最终最多几条 chunk 进上下文 |
  | similarityThreshold | 0.25（0~1） | 相似度下限，不够像的丢 |
  | vectorSearchMode | `default` / `rerank` | 是否二次重排 |

  - **默认路径**：query embed → cosine 近邻 `limit(topN)` → 距离转相似度 → 低于 threshold 丢 → 过滤已 pin 源  
  - **rerank 路径**（Lance 等）：先粗召回 `searchLimit = clamp(库规模×10%, 10~50)` → NativeEmbeddingReranker 对 query+chunk 打分 → 截 topN → 再过 threshold  
  - 聊天还可 pin 全文、`fillSourceWindow` 历史回填；**旋钮控噪声，不解决「文档过时」**  

#### E. 产品形态结论（本轮主结论，定稿语气）

  - **死的是**：十年文档沉淀 + 每轮 Pipeline 检索 + 聊天框当企业智能**主入口/主方案**  
  - **没死的是**：检索增强作为技术手段；当轮附件；agent 里可选的 `search_*` tool；系统 API/MCP 实时查询  

  认定「知识库问答主方案已死」的四条硬约束：

  1. **真源不在文档**：现行在权限/工单/配置/主数据；文档是滞后影子  
  2. **质量不可规模化运营**：无人维护现行集；「像人话」好评 ≠ 与现网一致；库越大静默错误面越大  
  3. **高频刚需题用错工具**：权限/流程/产品线 → 系统实时查，不是 PDF 考古  
  4. **接不上 agent/自动化**：问答终态是自然语言，默认不能动作；可调用系统能力才是资产  

  - 流程类更好的默认栈：**系统为真源（API/MCP）→ agent 编排动作 → 文档检索降级为可选弱 tool**  
  - 「问答库先上再演进 agent」经常是死胡同，不是必经课  

#### F. Hosted tool vs AnythingLLM 知识库

  | | OpenAI `file_search` | xAI `attachment_search` | AnythingLLM 主路径 |
  |---|---|---|---|
  | 形态 | hosted tool + Vector Store | 挂附件后隐式 server-side tool，变 agentic | 应用侧先检索再生成 |
  | 触发 | 模型 tool call | 附件驱动，模型自主搜 | 几乎每轮强制 |
  | 数据 | 平台托管 | 附件/还可有 Collections | 自管 documents + 向量库 |
  | 适合 | 可出域、快速挂库给 agent | 当轮/会话材料 | 私有化、换模、可运维治理 |

  - Anthropic 更偏 Files/长上下文 + 自备检索 tool，**不是**与 OpenAI VS 一一同构的公开主叙事  
  - Attachment search **作用域更干净**（用户当轮材料），不背全公司脏库——这是比 Pipeline 知识库「更正确」的 RAG 用法之一  

#### G. Agentic RAG 怎么实现（tool 化）

  三层：

  1. **Tool schema**：name/description/parameters（query、scope、top_k）；description 写清何时用/不用  
  2. **Handler**：鉴权 → embed → 检索 → 返回片段+来源（字符串/结构化）  
  3. **Agent loop**：有 tool_call 就执行写回，可多跳、改 query、换业务 tool  

  三种落地：

  - Hosted：OpenAI / xAI，平台执行检索  
  - 应用 plugin：AnythingLLM `rag-memory`（search 时调 `performSimilaritySearch`）  
  - MCP/自建：`search_docs` 与业务工具并列注册  

  与 Pipeline 同引擎、不同编排：**按需 call ≠ 每轮强制**。

- 新概念（用自己的话）：
  - **Pipeline RAG**：应用写死 retrieve-then-generate  
  - **Agentic RAG**：检索是 tool，模型决定是否/何时/用什么 query 搜  
  - **三层存储**：二进制原件 / 解析全文 JSON / 向量 chunk text  
  - **粗召回 + 精排**：向量先取 10–50，reranker 再压到 topN  
  - **真源分层**：系统状态 > 现行规范 pin > 一般文档检索  
  - **问答库主产品已死 / 检索 tool 侧车仍活**：产品结论与技术手段分开说  

- 源码锚点：
  - `anything-llm/server/utils/TextSplitter/index.js` — chunk 默认 1000/20、`determineMaxChunkSize`、RecursiveSplitter  
  - `anything-llm/server/models/systemSettings.js` — `text_splitter_chunk_size` 校验失败回落 1000；改设置 purge 向量缓存  
  - `anything-llm/server/utils/vectorDbProviders/*/index.js`（如 qdrant/lance）— 入库 split + embed；payload 含 `text`  
  - `anything-llm/server/utils/files/` + `purgeDocument.js` — 源文档路径、purge 源+cache+关联  
  - `anything-llm/server/utils/DocumentManager/index.js` — pin 读全文 `pageContent`  
  - `anything-llm/server/jobs/sync-watched-documents.js` — 活源 stale 同步、比 pageContent、重嵌  
  - `anything-llm/server/utils/vectorDbProviders/lance/index.js` — `similarityResponse` / `rerankedSimilarityResponse`、distance→similarity、searchLimit 10–50  
  - `anything-llm/server/utils/EmbeddingRerankers/native/index.js` — cross-encoder 式 rerank  
  - `anything-llm/server/utils/chats/apiChatHandler.js` — pin + `performSimilaritySearch` + topN/threshold/rerank  
  - `anything-llm/server/models/workspace.js` — topN/threshold/vectorSearchMode 校验默认值  
  - `anything-llm/server/utils/agents/aibitat/plugins/memory.js` — **agent 内 RAG tool**：`rag-memory` search/store  
  - `pi/packages/agent/src/agent-loop.ts` — 通用 tool 循环形状（本轮点到，未深挖停止条件）  
  - 外部：OpenAI file_search + Vector Store；xAI attachment_search / Collections（docs.x.ai）  

- 可迁移结论：
  - **E2**：chunk 大小是「粒度 × topN × embedder 上限」的工程默认，不是魔法数  
  - **E2**：原件二进制可丢，解析全文源与向量生命周期要一起设计  
  - **E2**：topN 控量、threshold 控门槛、rerank 控排序；都不解决过时真源  
  - **E2（本轮最重要）**：企业智能默认栈应是 **系统查询 + agent 动作**；文档检索最多侧车 tool  
  - **E1→E2**：Agentic RAG = schema + handler + loop；Anything 的 `rag-memory` 是同库检索的 tool 形态活例  
  - **E1**：hosted file_search / attachment_search 把「决策权」放对层（模型按需搜），比强制 Pipeline 更贴 agent 时代  

- 边界 / 反例 / 失效条件：
  - 「知识库已死」≠「永远不要存文档」；人在环辅助阅读、小而干净规范、当轮附件仍有用  
  - xAI 也有 Collections（持久库），说明平台也区分附件 vs 数据集，不是只有 attachment  
  - 无系统可查、只有叙述性遗产文档时，检索仍可能是无奈选项，但**不应承诺现行正确**  
  - rerank 费 CPU/延迟；Lance 路径注释里本机秒级开销，不能无限扩候选  
  - agent 乱调 search：靠 tool description 与并列业务 tool 分流，不是再堆阈值  

- 仍模糊：
  - 自建企业里 `search_docs` 与 20+ MCP 并列时，如何系统性地减少误调（tool search / 分组 / 权限裁剪）  
  - Anthropic 开放 API 上「集合检索」与产品面差异，需按版本再对一次文档  
  - Pipeline 已死之后，存量知识助手产品如何迁移话术与架构（只降级 tool？整产品下线？）  
  - Pi agent-loop 的停止条件、并行 tool、失败写回仍未读透  

- 主动回忆题（合上对话后自答）：
  1. 画出 Pipeline vs Agentic RAG 两张时序图，各三步以上。  
  2. chunk 默认约多少？为什么不默认 3k？硬上限是谁？  
  3. topN、threshold、rerank 各杀哪一类噪声？哪一个**不能**解决文档过时？  
  4. chunk 后哪一层存储必须留？pin / 重嵌 / 同步各依赖哪一层？  
  5. AnythingLLM 里 agent 用哪个 plugin 做检索？handler 最终调什么？  
  6. 用四条理由说明「为何 Pipeline 知识库问答主方案已死」。  
  7. 权限申请类问题，正确工具形态是什么？文档 search 应处于什么优先级？  

- 下一次验证：
  - 读通 `memory.js` + 一次 agent 调用链（从 tools 注册到 search handler），自己写 10 行伪代码「最小 search_docs tool」  
  - 通过标准：能不看笔记讲清 tool 化与 Pipeline 的触发差异，并指出 `rag-memory` 与 `performSimilaritySearch` 路径  

---

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
| 主线 | Pipeline 知识库问答批判已定稿 → **Agentic RAG / tool 化检索**；coding agent loop 待下钻 |
| 本阶段目标 | 能讲清 chunk/检索旋钮/三层存储，并能画 Agentic RAG 时序、指出 `rag-memory` 锚点 |
| 当前证据等级（自评） | E2（RAG 机制 + 产品结论）；agent loop 细节仍 E0–E1 |
| 下一轮想问的主题 | 最小 `search_docs` tool 实现；或 Pi agent-loop 停止条件；或 MCP 与 docs tool 并列 |

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
| 企业 AI 中台 | 门户/权限/模型网关自建；向量库可插拔；业务线隔离 | E1 | chat 经验 | 第 3 轮修正：中台默认能力应是系统 MCP/动作，不是文档问答库 |
| chunk ~1000 | 粒度×topN×embedder 上限的工程默认，非最优理论 | E2 | `TextSplitter` + `determineMaxChunkSize` | 可调大但噪声与上下文成本升；改设置需重嵌 |
| 三层文档存储 | 二进制原件 / 解析 JSON 全文 / 向量 chunk text | E2 | documents + vector payload | 日常问答靠向量；pin/重嵌靠 JSON |
| topN / threshold / rerank | 控条数 / 控相似度门槛 / 粗召回后精排 | E2 | lance `similarityResponse` / `rerankedSimilarityResponse` | 不解决文档过时 |
| Pipeline vs Agentic RAG | 强制每轮检索 vs 检索当 tool 按需调用 | E2 | chat handler vs `rag-memory` | hosted file_search / attachment_search 属后者 |
| 知识库问答主方案已死 | 十年脏库+强制管道+聊天主入口不可作为企业智能默认 | E2 | chat 结论 + 真源/质量/场景/自动化四条 | 附件检索、侧车 tool、人在环阅读仍可活 |
| 系统真源优先 | 流程/权限/状态走 API/MCP，文档最多叙述侧车 | E2 | chat | 无系统可查时文档是无奈，不能承诺现行正确 |
| Agentic RAG 三层 | tool schema + 检索 handler + agent loop | E2 | `plugins/memory.js` + `agent-loop.ts` | description 写不好会误调或从不调 |

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

## 开放问题（脑子里的洞）

- [ ] agent loop 的停止条件有哪些类型（正常 / 预算 / 用户中断 / 工具失败）？
- [ ] tool schema 如何约束模型，约束失败时运行时怎么办？
- [ ] 并行 tool call 的结果顺序与写回语义？
- [ ] sandbox 与“提示词里写请小心”的本质差别？
- [ ] 上下文压缩丢的是什么，如何发现静默错误？
- [ ] 怎样做不烧真模型钱的回归（mock provider / transcript）？
- [x] AnythingLLM `vectorSearchMode` / rerank 具体行为？（第 3 轮：default vs rerank，Lance 粗召回 10–50 再精排）
- [ ] hybrid（向量+关键词）在 Anything 里是否存在、开到哪一层？
- [ ] 多业务线权限：库级够不够，何时要文档级 ACL？
- [ ] 大文件 OCR/解析的异步队列与超时策略怎么做最小可用？
- [ ] 多 MCP + search_docs 并列时，如何减少误调（tool search / 分组）？
- [ ] 存量 Pipeline 知识助手产品如何迁移到 tool/MCP 栈？
- [ ] `rag-memory` 的 store 路径与「污染工作区向量」风险？

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
