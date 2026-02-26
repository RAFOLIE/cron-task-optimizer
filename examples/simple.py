#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Example - Cron Task Optimizer

This example demonstrates basic usage of the TaskStatusManager.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cron_optimizer import TaskStatusManager


def main():
    print("🎯 Cron Task Optimizer - Simple Example")
    print("=" * 50)
    
    # Create status manager
    manager = TaskStatusManager()
    
    # Simulate checking for updates
    print("\n1. Checking for software updates...")
    latest_version = "2.0.0"
    current_version = "1.0.0"
    has_update = latest_version > current_version
    
    manager.update_task_status(
        task_name="software-update",
        has_update=has_update,
        message=f"发现新版本：{latest_version}" if has_update else ""
    )
    
    print(f"   Current: {current_version}, Latest: {latest_version}")
    print(f"   Has update: {has_update}")
    
    # Simulate checking GitHub issues
    print("\n2. Checking GitHub issues...")
    new_comments = 3  # Simulated
    
    manager.update_task_status(
        task_name="issue-tracker",
        has_update=new_comments > 0,
        message=f"Issue #123 有 {new_comments} 条新回复" if new_comments > 0 else ""
    )
    
    print(f"   New comments: {new_comments}")
    
    # Get pending report
    print("\n3. Getting pending report...")
    report = manager.get_pending_report()
    
    if report:
        print("\n" + report)
    else:
        print("   No updates to report")
    
    # Clear report (simulate sending)
    print("\n4. Clearing report (simulate sending)...")
    manager.clear_report()
    print("   ✓ Report cleared")
    
    # Get status summary
    print("\n5. Status Summary:")
    summary = manager.get_status_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
