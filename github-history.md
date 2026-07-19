# GitHub 历史映射

以下内容来自已读取的仓库 README、提交记录或代码差异，每项都附上后续复盘问题，避免只罗列项目。

## agent

项目演示 Python 调用兼容 Anthropic Messages API 的端点，包含环境变量、CLI、Tool Use 与多轮工具编排；提交记录还出现并行工具执行、向量库、RAG 和会话记录。

来源：[EvilIrving/agent](https://github.com/EvilIrving/agent)

待复盘：工具 schema 怎样约束模型，循环何时停止，兼容端点有哪些差异，错误和超时如何传播，哪些部分需要单元测试。

## web-pronunciation

README 当前保存 Supabase、Cambridge Dictionary API、dictionaryapi.dev 与 Cloudflare 的相关入口；提交历史显示登录、速率控制、跟踪脚本、主题，以及音标 provider 轮询和 LLM fallback。

来源：[EvilIrving/web-pronunciation](https://github.com/EvilIrving/web-pronunciation)

待复盘：发音学习目标是什么，词典数据如何归一化，provider 失败如何降级，埋点是否测到学习效果而不只是点击。

## Pension-Estimation

项目使用年龄、平均月收入、工资增长率、企业与个人缴费比例、退休年龄等输入估算养老金。

来源：[EvilIrving/Pension-Estimation](https://github.com/EvilIrving/Pension-Estimation)

待复盘：公式和政策来源是什么，名义值与实际购买力是否区分，参数不确定性如何呈现，结果是否容易被误读为承诺。

## cbti-sleep

项目明确区分算法给出的 `Sleep Window` 与真实发生的 `Sleep Diary`，并从上床时间、入睡潜伏期和起床时间推导 TIB、TST 与睡眠效率；技术栈包含 SwiftUI、Charts 与 SwiftData。

来源：[EvilIrving/cbti-sleep](https://github.com/EvilIrving/cbti-sleep)

待复盘：计划数据和事实数据为何必须分开，用户偏离计划时怎样避免羞耻感，哪些建议属于产品教育，哪些情况必须提示寻求专业帮助。

## mediabrief

项目采用字幕优先、Whisper 兜底、LLM 清洗与总结的管线，包含统一任务队列、SSE 进度、重试、RSS、SQLite 历史、FastAPI 后端、React 前端以及前后端测试。

来源：[EvilIrving/mediabrief](https://github.com/EvilIrving/mediabrief)

待复盘：每个阶段的输入输出和幂等性，任务状态机与取消语义，重试为何不重复下载或转录，结构化 LLM 输出如何测试，隐私和临时文件如何管理。

## light-stats

项目是原生 macOS 菜单栏监控工具，强调默认无外部请求、可选权限、系统指标采集、健康评分、窗口管理、更新验证、诊断日志、测试和 CI。

来源：[EvilIrving/light-stats](https://github.com/EvilIrving/light-stats)

待复盘：主线程与 actor 的职责边界，采样频率和性能取舍，默认关闭功能的契约怎样测试，权限与隐私如何影响架构，评分缺失维度怎样重加权。

## swift-fitness

一次“更新动作清单”的提交扩展到二十二个动作，分类集中在胸、背、肩、肱二头肌、肱三头肌和核心，并为动作配置传感器轴、阈值、时间窗和自适应参数。

来源：[动作清单提交](https://github.com/EvilIrving/swift-fitness/commit/a992fa2b0faa063b41ba86feb848166f5d10ae49)

待复盘：当前动作库明显偏上肢，腿部、髋主导、蹲、走和旋转模式需要补齐；传感器阈值是经验值还是实验值，如何建立误计数和漏计数数据集，动作识别不能替代教练安全评估。

## exercise-weapp

仓库存在并可访问，证明有健身小程序实践，但本轮尚未读取到足够文档形成具体知识结论。

来源：[EvilIrving/exercise-weapp](https://github.com/EvilIrving/exercise-weapp)
