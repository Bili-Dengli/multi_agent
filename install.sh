#!/bin/bash
set -e

# Multi-Agents Linux 安装脚本
# 用法: chmod +x install.sh && ./install.sh

OPENCLAW_HOME=~/.openclaw

echo "== Multi-Agents 安装脚本 (Linux) =="
echo

# 1. 创建数据目录
echo "1. 创建数据目录"
mkdir -p $OPENCLAW_HOME/workspace/multi_agents/data
mkdir -p $OPENCLAW_HOME/workspace/multi_agents/shared
echo "✅ 创建: $OPENCLAW_HOME/workspace/multi_agents/data"
echo "✅ 创建: $OPENCLAW_HOME/workspace/multi_agents/shared"

# 2. 注册 Agent
echo
echo "2. 注册 Agent (需确认 openclaw 在 PATH 中)"
if command -v openclaw &> /dev/null; then
    echo "✅ openclaw 命令可用，正在注册 Agent"
    
    # 注册 Director
    if openclaw agents list | grep -q "director"; then
        echo "ℹ️  Agent director 已存在，跳过注册"
    else
        openclaw agents add director \
            --workspace $OPENCLAW_HOME/workspace-director \
            --subagents manager
        echo "✅ 注册 Agent: director"
    fi
    
    # 注册 Manager
    if openclaw agents list | grep -q "manager"; then
        echo "ℹ️  Agent manager 已存在，跳过注册"
    else
        openclaw agents add manager \
            --workspace $OPENCLAW_HOME/workspace-manager \
            --subagents worker
        echo "✅ 注册 Agent: manager"
    fi
    
    # 注册 Worker
    if openclaw agents list | grep -q "worker"; then
        echo "ℹ️  Agent worker 已存在，跳过注册"
    else
        openclaw agents add worker \
            --workspace $OPENCLAW_HOME/workspace-worker
        echo "✅ 注册 Agent: worker"
    fi
else
    echo "⚠️  未找到 openclaw 命令，跳过自动注册"
    echo "   请手动运行:"
    echo "     openclaw agents add director --workspace $OPENCLAW_HOME/workspace-director --subagents manager"
    echo "     openclaw agents add manager --workspace $OPENCLAW_HOME/workspace-manager --subagents worker"
    echo "     openclaw agents add worker --workspace $OPENCLAW_HOME/workspace-worker"
fi

# 3. 创建符号链接
echo
echo "3. 创建符号链接"

# Director
ln -sf $OPENCLAW_HOME/workspace/multi_agents/data $OPENCLAW_HOME/workspace-director/data
ln -sf $OPENCLAW_HOME/workspace/multi_agents/shared $OPENCLAW_HOME/workspace-director/shared
echo "✅ Director 符号链接创建完成"

# Manager
ln -sf $OPENCLAW_HOME/workspace/multi_agents/data $OPENCLAW_HOME/workspace-manager/data
ln -sf $OPENCLAW_HOME/workspace/multi_agents/shared $OPENCLAW_HOME/workspace-manager/shared
echo "✅ Manager 符号链接创建完成"

# Worker
ln -sf $OPENCLAW_HOME/workspace/multi_agents/data $OPENCLAW_HOME/workspace-worker/data
ln -sf $OPENCLAW_HOME/workspace/multi_agents/shared $OPENCLAW_HOME/workspace-worker/shared
echo "✅ Worker 符号链接创建完成"

# 4. 复制脚本
echo
echo "4. 复制脚本"
mkdir -p $OPENCLAW_HOME/workspace-director/scripts
mkdir -p $OPENCLAW_HOME/workspace-manager/scripts
mkdir -p $OPENCLAW_HOME/workspace-worker/scripts

cp scripts/task_update.py $OPENCLAW_HOME/workspace-director/scripts/
cp scripts/task_update.py $OPENCLAW_HOME/workspace-manager/scripts/
cp scripts/task_update.py $OPENCLAW_HOME/workspace-worker/scripts/
echo "✅ 脚本复制完成"

echo
echo "== 安装完成 =="
echo
echo "验证安装:"
echo "  openclaw agents list | grep -E \"director|manager|worker\""
echo
echo "使用方法:"
echo "  用户发送复杂任务给 director 即可启动多 Agent 协作"
echo "  任务ID格式: TASK-YYYYMMDD-NNN (例: TASK-20260421-001)"
