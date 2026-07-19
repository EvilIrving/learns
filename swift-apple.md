# Swift 与 Apple 平台

## 已有实践

`light-stats` 涵盖 SwiftUI、AppKit、Combine、Swift Concurrency、系统 API、菜单栏、权限、事件 tap、更新验证、日志、测试和 CI。

`cbti-sleep` 涵盖 SwiftUI、Charts、SwiftData、时间数据模型和行为训练产品；`swift-fitness` 涵盖 Apple Watch 交互、动作模型和传感器检测。

## 学习地图

语言和值语义，SwiftUI 数据流，AppKit 互操作，actor 与主线程边界，持久化，系统权限，采样与性能，测试，签名、公证和发布。

## 复盘问题

哪些状态必须在 MainActor，哪些采集器适合 actor，采样频率如何影响电量和 UI，默认关闭的权限功能怎样形成可测试契约，系统 API 失败时怎样降级。

## 下一件成果

使用 `project-retrospective.md` 完成 Light Stats 架构复盘，画出 SystemMonitor、服务、ViewModel、视图和异步采集器的数据流。
