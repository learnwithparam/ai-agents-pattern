#!/usr/bin/env python3
"""
11 - Goal Setting & Monitoring Pattern
Simple example showing how to set goals and monitor progress.

This demonstrates:
1. Define clear, measurable goals
2. Monitor progress toward goals
3. Adjust strategy based on progress
4. Achieve goals through iterative improvement
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class Goal:
    """Represents a goal with tracking capabilities."""
    
    def __init__(self, name, description, target_value, current_value=0):
        self.name = name
        self.description = description
        self.target_value = target_value
        self.current_value = current_value
        self.created_at = datetime.now()
        self.status = "in_progress"
    
    def update_progress(self, new_value):
        """Update the current progress toward the goal."""
        self.current_value = new_value
        if self.current_value >= self.target_value:
            self.status = "completed"
        elif self.current_value > 0:
            self.status = "in_progress"
        else:
            self.status = "not_started"
    
    def get_progress_percentage(self):
        """Get progress as a percentage."""
        if self.target_value == 0:
            return 100 if self.current_value > 0 else 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    def is_completed(self):
        """Check if goal is completed."""
        return self.status == "completed"

class GoalTracker:
    """Tracks multiple goals and their progress."""
    
    def __init__(self):
        self.goals = {}
        self.llm = get_llm()
    
    def add_goal(self, name, description, target_value):
        """Add a new goal to track."""
        goal = Goal(name, description, target_value)
        self.goals[name] = goal
        return goal
    
    def update_goal(self, name, new_value):
        """Update progress for a specific goal."""
        if name in self.goals:
            self.goals[name].update_progress(new_value)
            return True
        return False
    
    def get_goal_status(self, name):
        """Get status of a specific goal."""
        if name in self.goals:
            goal = self.goals[name]
            return {
                "name": goal.name,
                "status": goal.status,
                "progress": goal.get_progress_percentage(),
                "current": goal.current_value,
                "target": goal.target_value
            }
        return None
    
    def get_all_goals_status(self):
        """Get status of all goals."""
        return [self.get_goal_status(name) for name in self.goals.keys()]
    
    def generate_strategy(self, goal_name):
        """Generate strategy to achieve a goal."""
        if goal_name not in self.goals:
            return "Goal not found"
        
        goal = self.goals[goal_name]
        prompt = f"""
        Goal: {goal.name}
        Description: {goal.description}
        Current Progress: {goal.current_value}/{goal.target_value} ({goal.get_progress_percentage():.1f}%)
        Status: {goal.status}
        
        Generate a specific strategy to help achieve this goal. Provide actionable steps.
        """
        
        return self.llm.generate(prompt).content
    
    def evaluate_progress(self, goal_name):
        """Evaluate progress and suggest improvements."""
        if goal_name not in self.goals:
            return "Goal not found"
        
        goal = self.goals[goal_name]
        prompt = f"""
        Goal: {goal.name}
        Description: {goal.description}
        Current Progress: {goal.current_value}/{goal.target_value} ({goal.get_progress_percentage():.1f}%)
        Status: {goal.status}
        
        Evaluate the current progress and suggest specific improvements or next steps.
        """
        
        return self.llm.generate(prompt).content

def main():
    print("🎯 Goal Setting & Monitoring Pattern")
    print("=" * 40)
    
    # Initialize goal tracker
    tracker = GoalTracker()
    
    # Add some example goals
    tracker.add_goal(
        "python_learning", 
        "Learn Python programming fundamentals", 
        10  # 10 topics to complete
    )
    
    tracker.add_goal(
        "project_completion", 
        "Complete a Python project", 
        1  # 1 project to complete
    )
    
    tracker.add_goal(
        "code_reviews", 
        "Participate in code reviews", 
        5  # 5 code reviews to participate in
    )
    
    print("Initial goals set:")
    for status in tracker.get_all_goals_status():
        print(f"- {status['name']}: {status['current']}/{status['target']} ({status['progress']:.1f}%)")
    
    # Simulate progress updates
    print(f"\n--- Simulating Progress Updates ---")
    
    # Update Python learning progress
    tracker.update_goal("python_learning", 3)
    print(f"Updated python_learning: 3/10 topics completed")
    
    # Update project completion
    tracker.update_goal("project_completion", 1)
    print(f"Updated project_completion: 1/1 project completed")
    
    # Update code reviews
    tracker.update_goal("code_reviews", 2)
    print(f"Updated code_reviews: 2/5 reviews completed")
    
    # Show updated status
    print(f"\n--- Updated Goal Status ---")
    for status in tracker.get_all_goals_status():
        print(f"- {status['name']}: {status['current']}/{status['target']} ({status['progress']:.1f}%) - {status['status']}")
    
    # Generate strategies for incomplete goals
    print(f"\n--- Generating Strategies ---")
    for goal_name in tracker.goals.keys():
        goal = tracker.goals[goal_name]
        if not goal.is_completed():
            print(f"\nStrategy for {goal_name}:")
            strategy = tracker.generate_strategy(goal_name)
            print(f"{strategy[:200]}...")
    
    # Evaluate progress
    print(f"\n--- Progress Evaluation ---")
    for goal_name in tracker.goals.keys():
        goal = tracker.goals[goal_name]
        if not goal.is_completed():
            print(f"\nEvaluation for {goal_name}:")
            evaluation = tracker.evaluate_progress(goal_name)
            print(f"{evaluation[:200]}...")

if __name__ == "__main__":
    main()
