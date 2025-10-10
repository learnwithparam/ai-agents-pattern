#!/usr/bin/env python3
"""
32 - Plan Executor Pattern
Simple example showing how to execute structured plans with monitoring and adaptation.

This demonstrates:
1. Plan parsing and validation
2. Step-by-step execution
3. Progress monitoring
4. Dynamic plan adaptation
5. Error handling and recovery
"""

import sys
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class PlanStep:
    """Represents a single step in an execution plan."""
    
    def __init__(self, step_id: str, description: str, action: str, dependencies: List[str] = None):
        self.step_id = step_id
        self.description = description
        self.action = action
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "action": self.action,
            "dependencies": self.dependencies,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "result": self.result,
            "error": self.error
        }

class PlanExecutor:
    """Executes structured plans with monitoring and adaptation."""
    
    def __init__(self):
        self.llm = get_llm()
        self.execution_history = []
        self.current_plan = None
    
    def parse_plan(self, plan_text: str) -> List[PlanStep]:
        """Parse a text plan into structured steps."""
        # Create simplified steps based on plan text
        steps = []
        
        # Extract key actions from plan text (simplified approach)
        if "web application" in plan_text.lower():
            steps = [
                PlanStep("setup", "Set up development environment", "Install required tools and frameworks", []),
                PlanStep("auth", "Implement user authentication", "Create login/register functionality", ["setup"]),
                PlanStep("dashboard", "Build user dashboard", "Create dashboard interface", ["auth"]),
                PlanStep("deploy", "Deploy application", "Deploy to production environment", ["dashboard"])
            ]
        elif "machine learning" in plan_text.lower():
            steps = [
                PlanStep("data", "Collect and prepare data", "Gather and clean training data", []),
                PlanStep("model", "Build ML model", "Train machine learning model", ["data"]),
                PlanStep("evaluate", "Evaluate model performance", "Test model accuracy and metrics", ["model"]),
                PlanStep("deploy", "Deploy model", "Deploy model to production", ["evaluate"])
            ]
        elif "chatbot" in plan_text.lower():
            steps = [
                PlanStep("design", "Design chatbot architecture", "Plan chatbot structure and capabilities", []),
                PlanStep("implement", "Implement chatbot logic", "Build chatbot functionality", ["design"]),
                PlanStep("train", "Train chatbot", "Train on conversation data", ["implement"]),
                PlanStep("test", "Test chatbot", "Test chatbot responses", ["train"])
            ]
        else:
            # Generic steps for any plan
            steps = [
                PlanStep("plan", "Plan the project", "Create detailed project plan", []),
                PlanStep("implement", "Implement solution", "Build the main functionality", ["plan"]),
                PlanStep("test", "Test the solution", "Test and validate the implementation", ["implement"]),
                PlanStep("deploy", "Deploy solution", "Deploy to production environment", ["test"])
            ]
        
        return steps
    
    def validate_plan(self, steps: List[PlanStep]) -> Dict[str, Any]:
        """Validate a plan for completeness and dependencies."""
        issues = []
        warnings = []
        
        # Check for empty plan
        if not steps:
            issues.append("Plan is empty")
            return {"is_valid": False, "issues": issues, "warnings": warnings}
        
        # Check step IDs are unique
        step_ids = [step.step_id for step in steps]
        if len(step_ids) != len(set(step_ids)):
            issues.append("Duplicate step IDs found")
        
        # Check dependencies
        valid_step_ids = set(step_ids)
        for step in steps:
            for dep in step.dependencies:
                if dep not in valid_step_ids:
                    issues.append(f"Step {step.step_id} depends on non-existent step {dep}")
        
        # Check for circular dependencies (simplified)
        for step in steps:
            if step.step_id in step.dependencies:
                issues.append(f"Step {step.step_id} has circular dependency")
        
        # Check for orphaned steps
        all_deps = set()
        for step in steps:
            all_deps.update(step.dependencies)
        
        orphaned = valid_step_ids - all_deps - {steps[0].step_id}  # First step can be orphaned
        if len(orphaned) > 1:
            warnings.append(f"Multiple orphaned steps: {orphaned}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_steps": len(steps),
            "dependency_chains": len([s for s in steps if s.dependencies])
        }
    
    def execute_step(self, step: PlanStep, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single plan step."""
        print(f"🔄 Executing step: {step.step_id}")
        print(f"   Description: {step.description}")
        print(f"   Action: {step.action}")
        
        step.status = "running"
        step.start_time = datetime.now().isoformat()
        
        try:
            # Simulate step execution
            time.sleep(0.5)  # Simulate processing time
            
            # Use LLM to simulate step execution
            prompt = f"""
            Simulate executing this step:
            
            Step: {step.description}
            Action: {step.action}
            Context: {context or 'No context'}
            
            Provide a brief result of what would happen.
            """
            
            result = self.llm.generate(prompt).content
            step.result = result
            step.status = "completed"
            step.end_time = datetime.now().isoformat()
            
            print(f"   ✅ Completed: {result[:100]}...")
            
            return {
                "success": True,
                "result": result,
                "execution_time": "0.5s"
            }
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = datetime.now().isoformat()
            
            print(f"   ❌ Failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": "0.5s"
            }
    
    def execute_plan(self, plan_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete plan."""
        print(f"📋 Executing plan: {plan_text[:50]}...")
        
        # Parse plan
        steps = self.parse_plan(plan_text)
        print(f"📝 Parsed {len(steps)} steps")
        
        # Validate plan
        validation = self.validate_plan(steps)
        if not validation["is_valid"]:
            print(f"❌ Plan validation failed: {validation['issues']}")
            return {"success": False, "error": "Plan validation failed"}
        
        if validation["warnings"]:
            print(f"⚠️ Plan warnings: {validation['warnings']}")
        
        # Execute steps in dependency order
        executed_steps = set()
        results = []
        
        while len(executed_steps) < len(steps):
            # Find steps ready to execute
            ready_steps = []
            for step in steps:
                if step.step_id not in executed_steps:
                    deps_met = all(dep in executed_steps for dep in step.dependencies)
                    if deps_met:
                        ready_steps.append(step)
            
            if not ready_steps:
                print("❌ No steps ready to execute - possible circular dependency")
                break
            
            # Execute ready steps
            for step in ready_steps:
                result = self.execute_step(step, context)
                results.append({
                    "step": step.to_dict(),
                    "result": result
                })
                executed_steps.add(step.step_id)
        
        # Store execution history
        execution_record = {
            "plan_text": plan_text,
            "steps": [step.to_dict() for step in steps],
            "results": results,
            "executed_at": datetime.now().isoformat(),
            "total_steps": len(steps),
            "completed_steps": len([r for r in results if r["result"]["success"]]),
            "failed_steps": len([r for r in results if not r["result"]["success"]])
        }
        
        self.execution_history.append(execution_record)
        
        return execution_record
    
    def adapt_plan(self, original_plan: str, execution_results: Dict[str, Any]) -> str:
        """Adapt plan based on execution results."""
        failed_steps = [r for r in execution_results["results"] if not r["result"]["success"]]
        
        if not failed_steps:
            return original_plan  # No adaptation needed
        
        prompt = f"""
        Adapt this plan based on execution results:
        
        Original Plan: "{original_plan}"
        
        Failed Steps:
        {[f"- {r['step']['step_id']}: {r['result']['error']}" for r in failed_steps]}
        
        Provide an improved version of the plan that addresses the failures.
        """
        
        adapted_plan = self.llm.generate(prompt).content
        return adapted_plan
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about plan executions."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        total_steps = sum(exec["total_steps"] for exec in self.execution_history)
        completed_steps = sum(exec["completed_steps"] for exec in self.execution_history)
        failed_steps = sum(exec["failed_steps"] for exec in self.execution_history)
        
        return {
            "total_executions": total_executions,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "success_rate": completed_steps / total_steps if total_steps > 0 else 0
        }

def main():
    print("🎯 Plan Executor Pattern")
    print("=" * 50)
    
    # Initialize executor
    executor = PlanExecutor()
    
    # Test plans
    test_plans = [
        "Create a simple web application with user authentication and a dashboard",
        "Set up a machine learning pipeline for data analysis",
        "Build a chatbot that can answer questions about Python programming"
    ]
    
    print("Testing plan execution...")
    
    for i, plan in enumerate(test_plans, 1):
        print(f"\n{'='*60}")
        print(f"PLAN {i}: {plan}")
        print(f"{'='*60}")
        
        # Execute plan
        result = executor.execute_plan(plan, {"user": "test_user", "environment": "development"})
        
        print(f"\n📊 Execution Summary:")
        print(f"Total steps: {result['total_steps']}")
        print(f"Completed: {result['completed_steps']}")
        print(f"Failed: {result['failed_steps']}")
        
        # Adapt plan if needed
        if result['failed_steps'] > 0:
            print(f"\n🔄 Adapting plan...")
            adapted_plan = executor.adapt_plan(plan, result)
            print(f"Adapted plan: {adapted_plan[:100]}...")
    
    # Show execution statistics
    stats = executor.get_execution_stats()
    print(f"\n--- Execution Statistics ---")
    print(f"Total executions: {stats['total_executions']}")
    print(f"Total steps: {stats['total_steps']}")
    print(f"Success rate: {stats['success_rate']:.1%}")
    
    print(f"\n--- Plan Executor Pattern Summary ---")
    print(f"✅ Demonstrated plan parsing and validation")
    print(f"✅ Showed step-by-step execution")
    print(f"✅ Implemented progress monitoring")
    print(f"✅ Created dynamic plan adaptation")

if __name__ == "__main__":
    main()
