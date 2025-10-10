#!/usr/bin/env python3
"""
20 - Prioritization Pattern
Simple example showing how to prioritize tasks and manage workload.

This demonstrates:
1. Task prioritization algorithms
2. Workload management
3. Priority-based scheduling
4. Resource allocation
"""

import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class Task:
    """Represents a task with priority and metadata."""
    
    def __init__(self, id, title, description, priority="medium", deadline=None, estimated_duration=60):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority  # low, medium, high, urgent
        self.deadline = deadline
        self.estimated_duration = estimated_duration  # in minutes
        self.created_at = datetime.now()
        self.status = "pending"  # pending, in_progress, completed, cancelled
    
    def get_priority_score(self):
        """Calculate priority score for sorting."""
        priority_scores = {
            "urgent": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return priority_scores.get(self.priority, 2)
    
    def get_urgency_score(self):
        """Calculate urgency based on deadline."""
        if not self.deadline:
            return 0
        
        time_remaining = (self.deadline - datetime.now()).total_seconds() / 3600  # hours
        if time_remaining <= 0:
            return 100  # Overdue
        elif time_remaining <= 24:
            return 80   # Due within 24 hours
        elif time_remaining <= 72:
            return 60   # Due within 3 days
        elif time_remaining <= 168:
            return 40   # Due within 1 week
        else:
            return 20   # Due later
    
    def __str__(self):
        return f"[{self.priority.upper()}] {self.title} (ID: {self.id})"

class TaskPrioritizer:
    """Prioritizes tasks using various algorithms."""
    
    def __init__(self):
        self.llm = get_llm()
    
    def prioritize_by_priority(self, tasks):
        """Sort tasks by priority level."""
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)
    
    def prioritize_by_deadline(self, tasks):
        """Sort tasks by deadline urgency."""
        return sorted(tasks, key=lambda t: t.get_urgency_score(), reverse=True)
    
    def prioritize_by_effort(self, tasks):
        """Sort tasks by estimated effort (shortest first)."""
        return sorted(tasks, key=lambda t: t.estimated_duration)
    
    def prioritize_by_ai_analysis(self, tasks):
        """Use AI to analyze and prioritize tasks."""
        task_descriptions = []
        for task in tasks:
            task_descriptions.append(f"ID: {task.id}, Title: {task.title}, Description: {task.description}, Priority: {task.priority}, Deadline: {task.deadline}")
        
        prompt = f"""
        Analyze these tasks and prioritize them based on:
        1. Business impact
        2. Urgency and deadlines
        3. Dependencies
        4. Resource requirements
        
        Tasks:
        {chr(10).join(task_descriptions)}
        
        Return the task IDs in order of priority (highest first), separated by commas.
        Example: 3, 1, 5, 2, 4
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse AI response to get task order
        try:
            task_ids = [int(id.strip()) for id in response.split(',')]
            # Create ordered list based on AI analysis
            ordered_tasks = []
            for task_id in task_ids:
                for task in tasks:
                    if task.id == task_id:
                        ordered_tasks.append(task)
                        break
            return ordered_tasks
        except:
            # Fallback to priority-based sorting if AI parsing fails
            return self.prioritize_by_priority(tasks)

class WorkloadManager:
    """Manages workload and task scheduling."""
    
    def __init__(self):
        self.tasks = []
        self.prioritizer = TaskPrioritizer()
        self.max_concurrent_tasks = 3
        self.working_hours_per_day = 8
    
    def add_task(self, task):
        """Add a new task to the workload."""
        self.tasks.append(task)
        print(f"✅ Added task: {task}")
    
    def get_pending_tasks(self):
        """Get all pending tasks."""
        return [task for task in self.tasks if task.status == "pending"]
    
    def get_in_progress_tasks(self):
        """Get all in-progress tasks."""
        return [task for task in self.tasks if task.status == "in_progress"]
    
    def start_task(self, task_id):
        """Start working on a task."""
        for task in self.tasks:
            if task.id == task_id and task.status == "pending":
                if len(self.get_in_progress_tasks()) < self.max_concurrent_tasks:
                    task.status = "in_progress"
                    print(f"🚀 Started task: {task}")
                    return True
                else:
                    print(f"⚠️ Cannot start task {task_id}: Maximum concurrent tasks reached")
                    return False
        print(f"❌ Task {task_id} not found or not pending")
        return False
    
    def complete_task(self, task_id):
        """Mark a task as completed."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "completed"
                print(f"✅ Completed task: {task}")
                return True
        print(f"❌ Task {task_id} not found")
        return False
    
    def get_workload_summary(self):
        """Get summary of current workload."""
        pending = len(self.get_pending_tasks())
        in_progress = len(self.get_in_progress_tasks())
        completed = len([t for t in self.tasks if t.status == "completed"])
        
        total_estimated_hours = sum(t.estimated_duration for t in self.get_pending_tasks()) / 60
        
        return {
            "total_tasks": len(self.tasks),
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "estimated_hours_remaining": f"{total_estimated_hours:.1f}h"
        }
    
    def get_recommended_schedule(self):
        """Get AI-recommended task schedule."""
        pending_tasks = self.get_pending_tasks()
        if not pending_tasks:
            return "No pending tasks to schedule."
        
        # Use AI to prioritize tasks
        prioritized_tasks = self.prioritizer.prioritize_by_ai_analysis(pending_tasks)
        
        schedule = "📅 Recommended Task Schedule:\n"
        schedule += "=" * 40 + "\n"
        
        for i, task in enumerate(prioritized_tasks[:5], 1):  # Show top 5
            schedule += f"{i}. {task.title}\n"
            schedule += f"   Priority: {task.priority.upper()}\n"
            schedule += f"   Duration: {task.estimated_duration}min\n"
            if task.deadline:
                schedule += f"   Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
            schedule += "\n"
        
        return schedule

def main():
    print("📋 Prioritization Pattern")
    print("=" * 50)
    
    # Initialize workload manager
    manager = WorkloadManager()
    print(f"Using LLM: {manager.prioritizer.llm.provider}")
    
    # Create sample tasks
    tasks = [
        Task(1, "Fix critical bug", "Fix the login authentication bug affecting users", "urgent", 
             datetime.now() + timedelta(hours=4), 120),
        Task(2, "Write documentation", "Document the new API endpoints", "medium", 
             datetime.now() + timedelta(days=3), 180),
        Task(3, "Code review", "Review pull request #123", "high", 
             datetime.now() + timedelta(hours=12), 60),
        Task(4, "Update dependencies", "Update project dependencies to latest versions", "low", 
             datetime.now() + timedelta(days=7), 90),
        Task(5, "Design new feature", "Design the user dashboard interface", "high", 
             datetime.now() + timedelta(days=2), 240),
        Task(6, "Write tests", "Add unit tests for the payment module", "medium", 
             datetime.now() + timedelta(days=5), 150)
    ]
    
    # Add tasks to manager
    print(f"\n--- Adding {len(tasks)} tasks ---")
    for task in tasks:
        manager.add_task(task)
    
    # Show workload summary
    print(f"\n--- Workload Summary ---")
    summary = manager.get_workload_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Show recommended schedule
    print(f"\n--- AI-Recommended Schedule ---")
    schedule = manager.get_recommended_schedule()
    print(schedule)
    
    # Demonstrate task management
    print(f"\n--- Task Management Demo ---")
    
    # Start some tasks
    manager.start_task(1)  # Start urgent bug fix
    manager.start_task(3)  # Start code review
    
    # Show current status
    print(f"\nIn Progress Tasks:")
    for task in manager.get_in_progress_tasks():
        print(f"- {task}")
    
    # Complete a task
    manager.complete_task(1)
    
    # Show updated summary
    print(f"\n--- Updated Workload Summary ---")
    summary = manager.get_workload_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\n--- Prioritization Pattern Summary ---")
    print(f"✅ Demonstrated task prioritization algorithms")
    print(f"✅ Showed AI-powered task analysis")
    print(f"✅ Implemented workload management")
    print(f"✅ Created intelligent scheduling recommendations")

if __name__ == "__main__":
    main()
