# Grok build的上下文压缩机制


Shell 的主策略是 lossy full-replace compaction：

压完后典型结构：

1. System
2. User prefix（user_info / project_layout 等）
3. AGENTS.md / project instructions（有则有）
4. Last real user query（有则有）
5. Compaction summary
     "This session is being continued from a previous conversation..."
     + 格式化后的 Summary: ...
     + 可选 transcript/segments hint
6. System reminder（todos / tasks / MCP / plan mode…，有则有）


自动触发阈值

used * 100 >= context_window * threshold_percent(DEFAULT_AUTO_COMPACT_THRESHOLD_PERCENT = 85)
 


场景	条件
预采样 auto-compact	估计 token ≥ 窗口的 85%
tool 后 preflight overflow	估计 token > 100% 窗口（已越界）
API 报 context overflow	按错误 metadata 再救一次
手动 /compact	无视阈值，直接压


阈值可配，优先级：

1. env GROK_AUTO_COMPACT_THRESHOLD_PERCENT
2. 用户 TOML  per-model
3. 用户 TOML  global session
4. remote per-model
5. remote global
6. 默认 85


500K 窗 口
窗口 = 500_000 tokens
threshold = 85%  →  触发线 = 425_000 tokens

用量
0 ─────────────── 425K (85%) ─────────────── 500K (100%) ───>
│                      │                          │
│ 正常聊               │ 采样前 auto-compact        │ tool 后
│ 不做任何 prefire     │ → 同步 single-pass 摘要     │ preflight
│                      │ → reseed                   │ 若已 >500K
│                      │ → 再继续模型               │ 再压一次

## 
 two_pass_compaction 开

75% 后台 pass1：
  对「当时整段对话」做 95/5 切分
  摘要 95%，留下 5% 不摘要
  → 95/5 第一次出现

继续聊到 85%：
  pass2 = NOTE₁
        +（当时 5% + 之后新增）
  → 95/5 的切点还在用（prefix_len 冻结）
  → 不是按窗口 75/85 重新切一刀

然后 reseed：只有最终 summary 骨架
  （这里既没有 95/5，也没有 75/85 残留原文）

 术语


prefire   = 提前开火：还没到必须压缩，就先在后台做第一遍摘要
preflight = 起飞前检查：工具执行完，看 token 有没有已经超过窗口
lead      = 提前量：比如阈值 85%，lead=10 → 到 75% 就开始 prefire
tail      = 尾巴：历史里最近那一小段（two-pass 默认约 5% token）
prefix    = 前缀：历史里更早的那一大段（约 95%）
successor = 接班模型：压缩后只看到新上下文的那次助手
reseed    = 重种上下文：用摘要等材料替换旧 conversation
prefill   = 模型读 prompt 的前半计算（性能语境，不是业务开关）



Single-pass：

0 ──────────────────────── 425K ──────────>
                           │
                           └─ 阻塞：整段历史 → 1 次摘要 → reseed
                              用户要等这一整次 summarizer prefill

Two-pass：

0 ──────── 375K(75%) ──── 425K(85%) ────>
             │               │
             │ 后台：当时对话 95%→NOTE₁
             │ 不阻塞
             └─ 阻塞：NOTE₁ + tail → Pass2 → reseed
                用户主要等 Pass2（输入小很多）

Single-pass 的代价：
真正压的时候，摘要模型可能要 吞接近整窗的历史（或 ladder 裁过后的大头）→ 延迟和失败率 通常高于 two-pass 的 Pass2。

Single-pass 的好处：
实现简单、无 stale NOTE₁、无 fingerprint 失效回退；默认就走这条。



[features]
two_pass_compaction = false   # prefire two-pass compaction (default: false, opt-in) 


1. 环境变量 GROK_TWO_PASS_COMPACTION
2. 用户配置 ~/.grok/config.toml → [features] two_pass_compaction