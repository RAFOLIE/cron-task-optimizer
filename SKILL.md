---
name: cron-task-optimizer
description: Save messaging API quota for bots and cron tasks (Feishu, Discord, WeChat, Slack, etc.) with local file-based status management.
version: 1.0.0
license: BSD-3-Clause
author: OpenClaw Community
homepage: https://github.com/RAFOLIE/cron-task-optimizer
metadata:
  openclaw:
    emoji: ⚡
    requires:
      bins: []
    install: []
---

# Cron Task Optimizer

**节省通讯 API 配额（飞书、Discord、微信、Slack 等），实现按需通知。**

---

## 🎯 核心价值

### 解决的问题：API 配额耗尽

如果你有机器人或定时任务需要通过**通讯平台**发送消息（飞书、Discord、企业微信、Slack 等），可能会遇到：

- ❌ **API 配额用完** - 通讯平台有严格的 API 调用限制（如飞书约 100 次/天）
- ❌ **频繁轮询浪费配额** - 每 30 分钟检查一次 = 48 次/天，即使没有更新也要调用
- ❌ **用户被频繁打扰** - 琐碎的更新也发消息
- ❌ **无智能过滤** - 所有消息都发送，不管是否重要

### 解决方案：本地状态管理

**Cron Task Optimizer** 使用**本地文件存储**来跟踪任务状态，只在有实际更新时才调用通讯 API：

- ✅ **减少 70-95% 的 API 调用** - 只在必要时发送消息（如 48 → 2-5 次/天）
- ✅ **零 token 成本** - 文件操作免费，不消耗 API token
- ✅ **按需通知** - 用户只收到重要更新
- ✅ **智能过滤** - 将多个任务更新合并成一条消息

**关键洞察：** 这个工具节省的是**通讯 API 配额**，而不是 LLM token。它专为需要通过有 API 限制的平台发送消息的场景设计。

---

## 📊 效果对比

| 维度 | 优化前 | 优化后 | 改善 |
|---|---|---|---|
| **通讯 API 调用** | 96 次/天 | 0-5 次/天 | **-95%** |
| **API 配额使用** | 96 次/天 | 0-5 次/天 | **-95%** |
| **用户体验** | 每 30 分钟一次 | 按需通知 | **显著提升** |

**示例：** 以飞书约 100 次/天的限制为例：
- **优化前：** 2 个定时任务 × 48 次检查 = 96 次（使用 96% 配额）
- **优化后：** 只在有更新时发送 = 2-5 次（使用 2-5% 配额）

---

## 🚀 快速开始

### 1. 初始化

```python
from cron_optimizer import TaskStatusManager

# 创建状态管理器
manager = TaskStatusManager()
```

### 2. 定时任务中使用

```python
# 定时任务：检查更新
def check_updates():
    has_update, message = check_for_updates()
    
    # 写入状态文件（不发送消息）
    manager.update_task_status(
        task_name="update-check",
        has_update=has_update,
        message=message
    )
    
    # 返回静默确认
    return "HEARTBEAT_OK"
```

### 3. 心跳轮询中检查

```python
# 心跳轮询：检查是否有需要汇报的内容
def heartbeat_check():
    report = manager.get_pending_report()
    
    if report:
        # 发送合并消息
        send_message(report)
        # 清空状态
        manager.clear_report()
    else:
        # 无更新，静默
        return "HEARTBEAT_OK"
```

---

## 📁 文件结构

```
cron-task-optimizer/
├── SKILL.md              # 技能说明（本文件）
├── README.md             # 用户文档
├── cron_optimizer.py     # 核心状态管理器
├── config.example.json   # 配置文件模板
├── examples/             # 使用示例
│   ├── simple.py         # 简单示例
│   ├── advanced.py       # 高级示例
│   └── openclaw.md       # OpenClaw 集成示例
└── tests/                # 测试文件
    └── test_manager.py
```

---

## 🔧 核心功能

### 1. TaskStatusManager（状态管理器）

**主要方法：**

```python
# 更新任务状态
update_task_status(task_name, has_update, message, metadata)

# 获取待汇报内容
get_pending_report()

# 清空汇报状态
clear_report()

# 获取任务历史
get_task_history(task_name, days=7)

# 清理过期数据
cleanup_old_data(days=30)
```

---

### 2. 状态文件格式

**位置：** `workspace/cron_status.json`

```json
{
  "version": "1.0.0",
  "tasks": {
    "update-check": {
      "lastCheck": "2026-02-26T10:00:00+08:00",
      "hasUpdate": false,
      "message": "",
      "metadata": {}
    },
    "issue-tracker": {
      "lastCheck": "2026-02-26T10:00:00+08:00",
      "hasUpdate": true,
      "message": "Issue #9 有新回复",
      "metadata": {
        "issue_id": 9,
        "author": "developer"
      }
    }
  },
  "lastReport": "2026-02-26T09:30:00+08:00"
}
```

---

## 📝 使用场景

### 场景 1：检查软件更新

```python
# 定时任务：每 30 分钟检查一次
def check_software_updates():
    latest_version = fetch_latest_version()
    current_version = get_current_version()
    
    has_update = latest_version > current_version
    message = f"发现新版本：{latest_version}" if has_update else ""
    
    manager.update_task_status("software-update", has_update, message)
    return "HEARTBEAT_OK"
```

---

### 场景 2：追踪 GitHub Issue

```python
# 定时任务：检查 Issue 更新
def track_github_issue(issue_number):
    comments = fetch_issue_comments(issue_number)
    new_comments = filter_new_comments(comments)
    
    has_update = len(new_comments) > 0
    message = f"Issue #{issue_number} 有 {len(new_comments)} 条新回复" if has_update else ""
    
    manager.update_task_status("issue-tracker", has_update, message)
    return "HEARTBEAT_OK"
```

---

### 场景 3：监控系统状态

```python
# 定时任务：检查系统资源
def monitor_system():
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    
    has_update = cpu_usage > 80 or memory_usage > 80
    message = f"CPU: {cpu_usage}%, Memory: {memory_usage}%" if has_update else ""
    
    manager.update_task_status("system-monitor", has_update, message)
    return "HEARTBEAT_OK"
```

---

## ⚙️ 配置选项

**config.json:**

```json
{
  "status_file": "cron_status.json",
  "history_enabled": true,
  "history_days": 30,
  "auto_cleanup": true,
  "cleanup_days": 30,
  "timezone": "Asia/Shanghai"
}
```

---

## 🔒 安全考虑

### 1. 文件权限

- 状态文件应设置为仅当前用户可读写（chmod 600）
- 避免在状态文件中存储敏感信息

### 2. 数据脱敏

- 移除用户特定信息（用户名、路径等）
- 使用通用路径和配置

### 3. 错误处理

- 文件读写失败时优雅降级
- JSON 解析错误时使用默认值

---

## 📚 最佳实践

### ✅ 推荐做法

- ✅ 为每个定时任务使用唯一的 task_name
- ✅ 在心跳轮询时合并多个任务的更新
- ✅ 定期清理过期的历史数据
- ✅ 在消息中包含时间戳

### ❌ 避免的做法

- ❌ 在状态文件中存储敏感信息
- ❌ 频繁写入文件（建议 >= 1 分钟间隔）
- ❌ 忽略错误处理

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**GitHub:** https://github.com/RAFOLIE/cron-task-optimizer

---

## 📄 许可证

BSD-3-Clause License

详见 [LICENSE](LICENSE) 文件。

---

_此技能创建于 2026-02-26，版本 1.0.0_
