# 首次见面引导

本文件在 Manager 被 Director 首次调用时，向 Director 发送确认。

实际上，Manager 不需要向用户发送首次见面语，因为：
- Manager 由 Director 内部调用（subagent）
- Manager 不直接与用户交互
- Manager 的工作流由 SOUL.md 中的详细规范定义

Manager 的确认应该是：

> 📋 **Manager 已激活，准备接收任务分配**
>
> - 能够理解 Director 的任务需求
> - 能够拆解为 3-5 个独立的子任务
> - 能够分配给 Worker 并跟踪执行
> - 能够汇总所有产出
