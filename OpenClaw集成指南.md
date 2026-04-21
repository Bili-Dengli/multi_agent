# OpenClaw 集成指南

## 快速开始

### 1. 安装

```bash
cd openclaw-skillspack/skills/multi_agents
chmod +x install.sh
./install.sh
```

### 2. 验证

```bash
openclaw agents list
# 应看到：director, manager, worker
```

### 3. 发送任务

```bash
openclaw agents call director --message "帮我开发用户注册功能"
```

---

## 工作流程

```
用户消息 → Director(创建任务) → Manager(拆解) → Worker(执行) → 产物 → 回复用户
```

### 任务ID格式
- `TASK-YYYYMMDD-NNN` 例：`TASK-20260421-001`

### 产物位置
```
~/.openclaw/workspace/multi_agents/shared/TASK-xxx/
├── interim/   # 中间产物
└── final/     # 最终产物
```

---

## 常用命令

| 功能 | 命令 |
|-----|------|
| 查看任务 | `cat ~/.openclaw/workspace/multi_agents/data/tasks.json \| jq .` |
| 查看产物 | `ls -R ~/.openclaw/workspace/multi_agents/shared/` |
| 配置 API Key | `openclaw config set openai_api_key "sk-..."` |
| 查看配置 | `openclaw config show` |

---

## 目录结构

```
multi_agents/
├── scripts/task_update.py          # 任务状态管理
├── director/                       # Director 角色
├── manager/                        # Manager 角色
├── worker/                         # Worker 角色
├── agents.json                     # Agent 注册配置
└── install.sh                      # 安装脚本
```

---

## 故障排除

### Agent 不存在
```bash
openclaw agents list | grep -E "director|manager|worker"
# 缺失则重新运行 install.sh
```

### 无法通信
```bash
openclaw config set sessions.visibility all
```

### Windows 符号链接问题
使用 junction 替代：
```cmd
mklink /J "%USERPROFILE%\.openclaw\workspace-director\data" "%USERPROFILE%\.openclaw\workspace\multi_agents\data"
```

---

## 进阶用法

### 手动创建任务
```bash
python3 ~/.openclaw/workspace-director/scripts/task_update.py create TASK-20260421-001 "任务标题"
```

### 实时监控
```bash
watch -n 1 'cat ~/.openclaw/workspace/multi_agents/data/tasks.json | jq .'
```

### 与飞书集成
```bash
openclaw config set feishu_bot_token "..."
# 然后在飞书群中 @Director 即可
```

---

## 最佳实践

✅ **清晰的任务描述**
```
请开发用户认证系统：
1. 数据库设计
2. 注册/登录 API
3. JWT token 管理
4. 单元测试
5. API 文档

技术栈：Python FastAPI + PostgreSQL
```

❌ **模糊的任务描述**
```
帮我做个系统
```

---

## 工作流程细节

### Director 流程
1. 接收用户消息
2. 调用 `task_update.py create` 创建任务
3. 调用 Manager subagent
4. 汇总结果回复用户

### Manager 流程
1. 接收 Director 任务
2. 拆解为子任务
3. 逐一调用 Worker subagent
4. 返回汇总结果

### Worker 流程
1. 接收 Manager 指令
2. 执行具体任务
3. 调用 `task_update.py done` 标记完成
4. 产物存储到 `shared/<task_id>/interim/`

---

## 完整工作流示例

```bash
# 1. 发送任务给 Director
openclaw agents call director --message "设计一个订单管理系统"

# 2. 查看任务状态
cat ~/.openclaw/workspace/multi_agents/data/tasks.json | jq '.[] | {id, state}'

# 3. 查看产物
ls ~/.openclaw/workspace/multi_agents/shared/TASK-20260421-001/interim/

# 4. 查看最终报告
cat ~/.openclaw/workspace/multi_agents/shared/TASK-20260421-001/final/report.md
```

---

## 常见问题

**Q: 如何自定义 Agent 角色？**  
A: 修改 `director/SOUL.md`、`manager/SOUL.md`、`worker/SOUL.md` 中的工作流程定义

**Q: 产物太多占用磁盘？**  
A: 定期清理 `shared/` 中超过 7 天的任务产物

**Q: 能否添加新的 Agent？**  
A: 可以，注册新 Agent 后在 `agents.json` 中配置权限关系

---

## 配置参考

### openclaw.json
```json
{
  "agents": [
    { "name": "director", "workspace": "~/.openclaw/workspace-director" },
    { "name": "manager", "workspace": "~/.openclaw/workspace-manager" },
    { "name": "worker", "workspace": "~/.openclaw/workspace-worker" }
  ]
}
```

---

**更多详情请查看：**
- `技术方案.md` — 技术细节
- `README.md` — 项目概述
