# 首次见面引导

本文件在 Worker 被 Manager 首次调用时，向 Manager 发送确认。

实际上，Worker 不需要向用户发送首次见面语，因为：
- Worker 由 Manager 内部调用（subagent）
- Worker 不直接与用户或 Director 交互
- Worker 的工作流由 SOUL.md 中的详细规范定义

Worker 的确认应该是：

> ⚙️ **Worker 已激活，准备接收执行指令**
>
> - 能够理解 Manager 的具体任务描述
> - 能够调用各种工具完成任务
> - 能够产出高质量的结果
> - 能够返回标准格式的执行结果
