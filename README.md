# ⚡ Cron Task Optimizer

**Save messaging API quota for bots and cron tasks (Feishu, Discord, WeChat, Slack, etc.)**

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/Python-3.7%2B-brightgreen.svg)](https://www.python.org/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-orange.svg)](https://github.com/openclaw/openclaw)

---

## 🎯 What Problem Does This Solve?

### The Problem: API Quota Exhaustion

If you have bots or cron tasks that send messages via **messaging platforms** (Feishu, Discord, WeChat Work, Slack, etc.), you might face:

- ❌ **API Quota Depleted** - Messaging platforms have strict API call limits (e.g., Feishu ~100 calls/day)
- ❌ **Frequent Polling Wastes Quota** - Checking every 30min = 48 calls/day, even when nothing changed
- ❌ **User Disturbance** - Constant notifications for trivial updates
- ❌ **No Intelligence** - All messages sent, regardless of importance

### The Solution: Local Status Management

**Cron Task Optimizer** uses **local file storage** to track task status, and only calls messaging APIs when there are actual updates:

- ✅ **70-95% Fewer API Calls** - Only send messages when necessary (e.g., 48 → 2-5 calls/day)
- ✅ **Zero Token Cost** - File operations are free, no API tokens consumed
- ✅ **On-Demand Notifications** - Users only get important updates
- ✅ **Smart Filtering** - Combine multiple task updates into one message

**Key Insight:** This tool saves **messaging API quota**, not LLM tokens. It's designed for scenarios where you need to send messages through platforms with API limits.

---

## 📊 Performance

| Metric | Before | After | Improvement |
|---|---|---|---|
| **Messaging API Calls** | 96/day | 0-5/day | **-95%** |
| **API Quota Usage** | 96/day | 0-5/day | **-95%** |
| **User Notifications** | Every 30min | As needed | **Better UX** |

**Example:** With Feishu's ~100 calls/day limit:
- **Before:** 2 cron tasks × 48 checks = 96 calls (96% quota used)
- **After:** Only send when updates exist = 2-5 calls (2-5% quota used)

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the skill
git clone https://github.com/RAFOLIE/cron-task-optimizer.git

# Or copy files to your workspace
cp -r cron-task-optimizer /path/to/workspace/skills/
```

### Basic Usage

```python
from cron_optimizer import TaskStatusManager

# Create manager
manager = TaskStatusManager()

# In your cron task: update status
manager.update_task_status(
    task_name="update-check",
    has_update=True,
    message="New version 2.0.0 available"
)

# In your heartbeat: check for updates
report = manager.get_pending_report()
if report:
    send_message(report)  # Only sends when there are updates
    manager.clear_report()
```

---

## 🎭 Use Cases

### When to Use This Tool

✅ **You have cron tasks that send messages** via messaging platforms (Feishu, Discord, Slack, WeChat Work, Telegram, etc.)  
✅ **Your messaging platform has API call limits** (quota, rate limits)  
✅ **Your tasks frequently check for updates** but mostly find nothing new  
✅ **You want to reduce unnecessary notifications**  

### When NOT to Use This Tool

❌ **You don't send messages through messaging platforms**  
❌ **Your messaging platform has unlimited API calls**  
❌ **You only care about reducing LLM token usage** (this tool focuses on messaging API quota)  

### Real-World Examples

**Example 1: Software Update Checker**
- **Task:** Check for software updates every 30 minutes
- **Before:** Send message every check (48 calls/day)
- **After:** Only send when new version detected (2-3 calls/day)
- **Saved:** 45 API calls/day (94%)

**Example 2: GitHub Issue Tracker**
- **Task:** Track GitHub issues every 30 minutes
- **Before:** Send message every check (48 calls/day)
- **After:** Only send when new comments detected (1-5 calls/day)
- **Saved:** 43 API calls/day (90%)

**Example 3: Multi-Task Bot**
- **Tasks:** 5 different monitors checking every 30 minutes
- **Before:** 5 × 48 = 240 calls/day (exceeds most quotas!)
- **After:** Combine updates, send 1 message with all updates (5-10 calls/day)
- **Saved:** 230 API calls/day (96%)

---

## 📖 Documentation

### Core API

#### TaskStatusManager

**Initialization:**
```python
manager = TaskStatusManager(
    status_file="cron_status.json",  # Status file name
    workspace="/path/to/workspace",   # Workspace directory
    timezone="Asia/Shanghai"          # Timezone for timestamps
)
```

**Methods:**

```python
# Update task status
manager.update_task_status(
    task_name="my-task",      # Unique task identifier
    has_update=True,          # Whether there's an update
    message="Something new",  # Human-readable message
    metadata={                # Optional additional data
        "key": "value"
    }
)

# Get pending report
report = manager.get_pending_report()
# Returns: formatted string or None

# Clear report after sending
manager.clear_report()

# Get status summary
summary = manager.get_status_summary()

# Cleanup old data
removed = manager.cleanup_old_data(days=30)
```

---

### Convenience Functions

```python
from cron_optimizer import update_task_status, get_pending_report, clear_report

# Quick update
update_task_status("my-task", True, "Update available")

# Quick check
report = get_pending_report()

# Quick clear
clear_report()
```

---

## 📝 Examples

### Example 1: Software Update Checker

```python
# Cron task: runs every 30 minutes
def check_software_updates():
    latest = fetch_latest_version()
    current = get_current_version()
    
    has_update = latest > current
    message = f"New version {latest} available" if has_update else ""
    
    manager.update_task_status("software-update", has_update, message)
    return "HEARTBEAT_OK"  # Silent return
```

### Example 2: GitHub Issue Tracker

```python
# Cron task: tracks issue updates
def track_github_issue(issue_number):
    comments = fetch_issue_comments(issue_number)
    new_comments = filter_new(comments)
    
    has_update = len(new_comments) > 0
    message = f"Issue #{issue_number} has {len(new_comments)} new comments" if has_update else ""
    
    manager.update_task_status("issue-tracker", has_update, message, {
        "issue_id": issue_number,
        "count": len(new_comments)
    })
    return "HEARTBEAT_OK"
```

### Example 3: Heartbeat Check

```python
# Heartbeat: polls every 30 minutes
def heartbeat_check():
    report = manager.get_pending_report()
    
    if report:
        send_to_user(report)  # Send combined report
        manager.clear_report()
        return "Report sent"
    else:
        return "HEARTBEAT_OK"  # No updates, silent
```

---

## 🗂️ File Structure

```
cron-task-optimizer/
├── SKILL.md              # Skill documentation
├── README.md             # This file
├── cron_optimizer.py     # Core module
├── config.example.json   # Configuration template
├── examples/             # Usage examples
│   ├── simple.py         # Basic usage
│   └── openclaw.md       # OpenClaw integration
└── LICENSE               # BSD-3-Clause license
```

---

## ⚙️ Configuration

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

## 🔒 Security Considerations

### ✅ Best Practices

- ✅ Set file permissions (chmod 600) for status file
- ✅ Don't store sensitive information in status file
- ✅ Use environment variables for secrets
- ✅ Implement error handling for file operations

### ❌ Avoid

- ❌ Storing passwords or API keys in status file
- ❌ Using world-readable file permissions
- ❌ Writing to shared directories without proper access control

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **BSD-3-Clause License** - see the [LICENSE](LICENSE) file for details.

```
Copyright (c) 2026, OpenClaw Community
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.
```

---

## 🙏 Acknowledgments

- Inspired by the need to reduce API costs in OpenClaw
- Built with simplicity and efficiency in mind
- Thanks to the OpenClaw community for feedback and testing

---

## 📮 Support

- **Issues:** [GitHub Issues](https://github.com/RAFOLIE/cron-task-optimizer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/RAFOLIE/cron-task-optimizer/discussions)
- **Documentation:** [Wiki](https://github.com/RAFOLIE/cron-task-optimizer/wiki)

---

**Made with ❤️ by the OpenClaw Community**
