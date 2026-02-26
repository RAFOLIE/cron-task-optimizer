#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron Task Optimizer - Task Status Manager

A local file-based status management system for reducing API calls
and token usage in cron tasks.

License: BSD-3-Clause
Author: OpenClaw Community
Version: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from pathlib import Path


class TaskStatusManager:
    """
    Manage cron task status with local file storage.
    
    Usage:
        manager = TaskStatusManager()
        manager.update_task_status("update-check", has_update=True, message="New version available")
        report = manager.get_pending_report()
    """
    
    def __init__(
        self,
        status_file: str = "cron_status.json",
        workspace: Optional[str] = None,
        timezone: str = "Asia/Shanghai"
    ):
        """
        Initialize the status manager.
        
        Args:
            status_file: Name of the status file (default: cron_status.json)
            workspace: Workspace directory (default: current directory)
            timezone: Timezone for timestamps (default: Asia/Shanghai)
        """
        self.timezone = timezone
        self.workspace = workspace or os.getcwd()
        self.status_file_path = Path(self.workspace) / status_file
        
        # Initialize status file if not exists
        if not self.status_file_path.exists():
            self._initialize_status_file()
    
    def _initialize_status_file(self):
        """Initialize empty status file."""
        initial_data = {
            "version": "1.0.0",
            "tasks": {},
            "lastReport": None,
            "createdAt": self._get_timestamp()
        }
        self._write_status(initial_data)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.now().isoformat()
    
    def _read_status(self) -> Dict:
        """Read status file."""
        try:
            with open(self.status_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If file is corrupted, reinitialize
            self._initialize_status_file()
            return self._read_status()
    
    def _write_status(self, data: Dict):
        """Write status file."""
        with open(self.status_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_task_status(
        self,
        task_name: str,
        has_update: bool,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update status for a specific task.
        
        Args:
            task_name: Unique identifier for the task
            has_update: Whether this task has an update to report
            message: Human-readable message describing the update
            metadata: Optional additional data (e.g., issue_id, author)
        """
        status = self._read_status()
        
        status["tasks"][task_name] = {
            "lastCheck": self._get_timestamp(),
            "hasUpdate": has_update,
            "message": message,
            "metadata": metadata or {}
        }
        
        self._write_status(status)
    
    def get_pending_report(self) -> Optional[str]:
        """
        Get pending report for all tasks with updates.
        
        Returns:
            Formatted report string if there are updates, None otherwise
        """
        status = self._read_status()
        
        # Filter tasks with updates
        tasks_with_updates = {
            name: task for name, task in status["tasks"].items()
            if task.get("hasUpdate", False)
        }
        
        if not tasks_with_updates:
            return None
        
        # Format report
        report_lines = ["📊 定时任务汇报", ""]
        
        for task_name, task in tasks_with_updates.items():
            emoji = self._get_task_emoji(task_name)
            report_lines.append(f"{emoji} **{task_name}**")
            report_lines.append(task["message"])
            report_lines.append("")
        
        report_lines.append("---")
        report_lines.append(f"_汇报时间：{self._get_timestamp()}_")
        
        return "\n".join(report_lines)
    
    def _get_task_emoji(self, task_name: str) -> str:
        """Get emoji for task based on name."""
        emoji_map = {
            "update": "🔄",
            "issue": "📌",
            "monitor": "📊",
            "check": "✅",
            "track": "🔍"
        }
        
        for key, emoji in emoji_map.items():
            if key in task_name.lower():
                return emoji
        
        return "📋"  # Default emoji
    
    def clear_report(self):
        """Clear hasUpdate flags for all tasks after report is sent."""
        status = self._read_status()
        
        for task_name in status["tasks"]:
            status["tasks"][task_name]["hasUpdate"] = False
        
        status["lastReport"] = self._get_timestamp()
        
        self._write_status(status)
    
    def get_task_history(
        self,
        task_name: str,
        days: int = 7
    ) -> list:
        """
        Get history for a specific task (if history logging is enabled).
        
        Note: This is a placeholder for future history functionality.
        Currently returns empty list.
        
        Args:
            task_name: Task identifier
            days: Number of days to look back
            
        Returns:
            List of historical status entries
        """
        # TODO: Implement history logging
        return []
    
    def cleanup_old_data(self, days: int = 30):
        """
        Remove tasks that haven't been updated in N days.
        
        Args:
            days: Number of days to keep (default: 30)
        """
        status = self._read_status()
        cutoff = datetime.now() - timedelta(days=days)
        
        tasks_to_remove = []
        
        for task_name, task in status["tasks"].items():
            last_check = datetime.fromisoformat(task["lastCheck"])
            if last_check < cutoff:
                tasks_to_remove.append(task_name)
        
        for task_name in tasks_to_remove:
            del status["tasks"][task_name]
        
        if tasks_to_remove:
            self._write_status(status)
        
        return len(tasks_to_remove)
    
    def get_status_summary(self) -> Dict:
        """Get summary of current status."""
        status = self._read_status()
        
        total_tasks = len(status["tasks"])
        tasks_with_updates = sum(
            1 for task in status["tasks"].values()
            if task.get("hasUpdate", False)
        )
        
        return {
            "total_tasks": total_tasks,
            "tasks_with_updates": tasks_with_updates,
            "last_report": status.get("lastReport"),
            "status_file": str(self.status_file_path)
        }


# Convenience functions for quick usage
_manager = None


def get_manager(workspace: Optional[str] = None) -> TaskStatusManager:
    """Get global manager instance."""
    global _manager
    if _manager is None:
        _manager = TaskStatusManager(workspace=workspace)
    return _manager


def update_task_status(task_name: str, has_update: bool, message: str = "", **kwargs):
    """Convenience function to update task status."""
    manager = get_manager()
    manager.update_task_status(task_name, has_update, message, kwargs)


def get_pending_report() -> Optional[str]:
    """Convenience function to get pending report."""
    manager = get_manager()
    return manager.get_pending_report()


def clear_report():
    """Convenience function to clear report."""
    manager = get_manager()
    manager.clear_report()


if __name__ == "__main__":
    # Example usage
    print("Cron Task Optimizer - Task Status Manager")
    print("=" * 50)
    
    # Create manager
    manager = TaskStatusManager()
    
    # Update some tasks
    manager.update_task_status(
        "software-update",
        has_update=True,
        message="发现新版本：v2.0.0",
        metadata={"version": "2.0.0"}
    )
    
    manager.update_task_status(
        "issue-tracker",
        has_update=False,
        message=""
    )
    
    # Get report
    report = manager.get_pending_report()
    print(report)
    
    # Get summary
    summary = manager.get_status_summary()
    print("\nStatus Summary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
