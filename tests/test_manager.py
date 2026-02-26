#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Cron Task Optimizer
"""

import sys
import os
import json
import tempfile
import shutil

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cron_optimizer import TaskStatusManager


def test_basic_functionality():
    """Test basic functionality of TaskStatusManager."""
    print("Running basic functionality tests...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test initialization
        manager = TaskStatusManager(workspace=temp_dir)
        print("  ✓ Manager initialized")
        
        # Test update task status
        manager.update_task_status("test-task", True, "Test message")
        print("  ✓ Task status updated")
        
        # Test get pending report
        report = manager.get_pending_report()
        assert report is not None, "Report should not be None"
        assert "test-task" in report, "Report should contain task name"
        print("  ✓ Pending report generated")
        
        # Test clear report
        manager.clear_report()
        report_after = manager.get_pending_report()
        assert report_after is None, "Report should be None after clearing"
        print("  ✓ Report cleared")
        
        # Test status summary
        summary = manager.get_status_summary()
        assert "total_tasks" in summary, "Summary should contain total_tasks"
        assert "tasks_with_updates" in summary, "Summary should contain tasks_with_updates"
        print("  ✓ Status summary generated")
        
        print("\n✅ All basic functionality tests passed!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_multiple_tasks():
    """Test handling multiple tasks."""
    print("\nRunning multiple tasks tests...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = TaskStatusManager(workspace=temp_dir)
        
        # Add multiple tasks
        manager.update_task_status("task-1", True, "Task 1 update")
        manager.update_task_status("task-2", False, "")
        manager.update_task_status("task-3", True, "Task 3 update")
        print("  ✓ Multiple tasks updated")
        
        # Get report
        report = manager.get_pending_report()
        assert report is not None, "Report should not be None"
        assert "task-1" in report, "Report should contain task-1"
        assert "task-3" in report, "Report should contain task-3"
        assert "task-2" not in report, "Report should not contain task-2 (no update)"
        print("  ✓ Report includes only tasks with updates")
        
        print("\n✅ Multiple tasks tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_metadata():
    """Test metadata functionality."""
    print("\nRunning metadata tests...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = TaskStatusManager(workspace=temp_dir)
        
        # Update task with metadata
        metadata = {
            "issue_id": 123,
            "author": "test_user",
            "count": 5
        }
        manager.update_task_status(
            "metadata-test",
            True,
            "Test with metadata",
            metadata=metadata
        )
        print("  ✓ Task updated with metadata")
        
        # Read status file to verify metadata
        status_file = os.path.join(temp_dir, "cron_status.json")
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        task_status = status["tasks"]["metadata-test"]
        assert task_status["metadata"]["issue_id"] == 123, "Metadata should be saved"
        print("  ✓ Metadata preserved correctly")
        
        print("\n✅ Metadata tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_cleanup():
    """Test cleanup functionality."""
    print("\nRunning cleanup tests...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = TaskStatusManager(workspace=temp_dir)
        
        # Add a task
        manager.update_task_status("old-task", True, "Old task")
        print("  ✓ Old task added")
        
        # Cleanup (should not remove recent tasks)
        removed = manager.cleanup_old_data(days=30)
        assert removed == 0, "Should not remove recent tasks"
        print("  ✓ Recent tasks preserved")
        
        print("\n✅ Cleanup tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("=" * 50)
    print("Cron Task Optimizer - Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_multiple_tasks()
        test_metadata()
        test_cleanup()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
