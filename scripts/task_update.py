#!/usr/bin/env python3
"""任务状态更新 CLI - 供 Director/Manager/Worker Agent 调用

用法:
  python3 task_update.py create <task_id> <title>
  python3 task_update.py flow <task_id> <from> <to> <remark>
  python3 task_update.py progress <task_id> <now> [<todos>]
  python3 task_update.py done <task_id> <summary>
"""

import json
import pathlib
import sys
from pathlib import Path
from datetime import datetime

# 路径配置（通过符号链接访问本地文件）
BASE = Path(__file__).resolve().parent
TASKS_FILE = BASE / "data" / "tasks.json"
SHARED_DIR = BASE / "shared"


def ensure_dirs():
    """确保必要目录存在"""
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SHARED_DIR.mkdir(parents=True, exist_ok=True)


def load_tasks():
    """读取任务列表"""
    ensure_dirs()
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_tasks(tasks):
    """保存任务列表"""
    ensure_dirs()
    TASKS_FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_task(tasks, task_id):
    """查找任务"""
    return next((t for t in tasks if t.get("id") == task_id), None)


def now_iso():
    """获取当前 ISO 8601 时间"""
    return datetime.now().isoformat()


def cmd_create(task_id, title):
    """创建新任务

    task_id: TASK-YYYYMMDD-NNN
    title: 任务标题（中文，10-30字）
    """
    tasks = load_tasks()

    # 检查重复
    if find_task(tasks, task_id):
        print(f"⚠️  任务 {task_id} 已存在，跳过创建", file=sys.stderr)
        return

    # 创建任务
    task = {
        "id": task_id,
        "title": title,
        "state": "created",  # 任务状态
        "owner": "director",  # 当前负责人
        "flow_log": [  # 流转记录
            {
                "at": now_iso(),
                "from": "user",
                "to": "director",
                "remark": f"创建任务: {title}",
            }
        ],
        "progress_log": [],  # 进展日志
        "output": "",  # 最终产出
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }

    tasks.insert(0, task)  # 新任务插到最前面
    save_tasks(tasks)
    print(f"✅ 创建任务: {task_id}")


def cmd_flow(task_id, from_dept, to_dept, remark):
    """记录流转

    task_id: 任务ID
    from_dept: 从（部门/Agent）
    to_dept: 到（部门/Agent）
    remark: 备注（10-120字）
    """
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if not task:
        print(f"❌ 任务 {task_id} 不存在", file=sys.stderr)
        return

    # 添加流转记录
    task.setdefault("flow_log", []).append(
        {"at": now_iso(), "from": from_dept, "to": to_dept, "remark": remark}
    )

    # 更新所有者
    task["owner"] = to_dept
    task["updatedAt"] = now_iso()

    save_tasks(tasks)
    print(f"✅ 流转: {from_dept} → {to_dept} ({remark[:30]})")


def cmd_progress(task_id, now_text, todos_pipe=""):
    """实时进展上报

    task_id: 任务ID
    now_text: 当前在做什么（一句话）
    todos_pipe: 可选，todo 列表（用 | 分隔，✅/🔄 标记状态）
               例: "分析需求✅|拆解子任务🔄|执行|汇总"
    """
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if not task:
        print(f"❌ 任务 {task_id} 不存在", file=sys.stderr)
        return

    # 解析 todos
    todos = []
    if todos_pipe:
        for i, item in enumerate(todos_pipe.split("|"), 1):
            item = item.strip()
            if not item:
                continue

            if item.endswith("✅"):
                status = "done"
                title = item[:-1].strip()
            elif item.endswith("🔄"):
                status = "in_progress"
                title = item[:-1].strip()
            else:
                status = "pending"
                title = item

            todos.append({"id": str(i), "title": title, "status": status})

    # 添加进展日志
    log_entry = {"at": now_iso(), "text": now_text, "todos": todos}
    task.setdefault("progress_log", []).append(log_entry)

    # 限制日志大小（最多 100 条）
    if len(task.get("progress_log", [])) > 100:
        task["progress_log"] = task["progress_log"][-100:]

    task["updatedAt"] = now_iso()

    save_tasks(tasks)

    # 输出统计
    done_count = sum(1 for t in todos if t.get("status") == "done")
    total_count = len(todos)
    if total_count > 0:
        print(f"📡 进展: {now_text[:40]} [{done_count}/{total_count}]")
    else:
        print(f"📡 进展: {now_text[:40]}")


def cmd_done(task_id, summary):
    """标记完成

    task_id: 任务ID
    summary: 产出摘要（3-5句话）
    """
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if not task:
        print(f"❌ 任务 {task_id} 不存在", file=sys.stderr)
        return

    # 更新任务
    task["state"] = "done"
    task["output"] = summary
    task["updatedAt"] = now_iso()

    # 记录完成流转
    task.setdefault("flow_log", []).append(
        {
            "at": now_iso(),
            "from": task.get("owner", "unknown"),
            "to": "completed",
            "remark": f"✅ 完成: {summary[:50]}",
        }
    )

    save_tasks(tasks)
    print(f"✅ 完成: {task_id}")


def print_help():
    """打印帮助信息"""
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "create":
            if len(sys.argv) < 4:
                print(f"❌ create 需要 2 个参数: <task_id> <title>", file=sys.stderr)
                sys.exit(1)
            cmd_create(sys.argv[2], sys.argv[3])

        elif cmd == "flow":
            if len(sys.argv) < 6:
                print(
                    f"❌ flow 需要 4 个参数: <task_id> <from> <to> <remark>",
                    file=sys.stderr,
                )
                sys.exit(1)
            cmd_flow(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

        elif cmd == "progress":
            if len(sys.argv) < 4:
                print(
                    f"❌ progress 需要至少 2 个参数: <task_id> <now> [<todos>]",
                    file=sys.stderr,
                )
                sys.exit(1)
            todos = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_progress(sys.argv[2], sys.argv[3], todos)

        elif cmd == "done":
            if len(sys.argv) < 4:
                print(f"❌ done 需要 2 个参数: <task_id> <summary>", file=sys.stderr)
                sys.exit(1)
            cmd_done(sys.argv[2], sys.argv[3])

        else:
            print(f"❌ 未知命令: {cmd}", file=sys.stderr)
            print_help()
            sys.exit(1)

    except Exception as e:
        print(f"❌ 执行错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
