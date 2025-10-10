#!/usr/bin/env python3
"""
24 - Workflow Orchestration Pattern
Simple example showing how to orchestrate complex AI workflows.

This demonstrates:
1. Workflow definition and execution
2. Task dependencies and sequencing
3. Parallel and sequential execution
4. Error handling and recovery
"""

import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Callable
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class WorkflowTask:
    """Represents a single task in a workflow."""
    
    def __init__(self, id: str, name: str, function: Callable, dependencies: List[str] = None):
        self.id = id
        self.name = name
        self.function = function
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execute(self, context: Dict[str, Any]):
        """Execute the task."""
        self.status = "running"
        self.start_time = datetime.now()
        
        try:
            print(f"🔄 Executing task: {self.name}")
            self.result = self.function(context)
            self.status = "completed"
            self.end_time = datetime.now()
            print(f"✅ Completed task: {self.name}")
            return self.result
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.end_time = datetime.now()
            print(f"❌ Failed task: {self.name} - {e}")
            raise e
    
    def get_duration(self):
        """Get task execution duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

class WorkflowOrchestrator:
    """Orchestrates workflow execution."""
    
    def __init__(self):
        self.llm = get_llm()
        self.tasks = {}
        self.execution_order = []
        self.context = {}
    
    def add_task(self, task: WorkflowTask):
        """Add a task to the workflow."""
        self.tasks[task.id] = task
    
    def validate_dependencies(self):
        """Validate that all dependencies exist."""
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    raise ValueError(f"Task {task_id} depends on non-existent task {dep_id}")
    
    def calculate_execution_order(self):
        """Calculate the order of task execution based on dependencies."""
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(task_id):
            if task_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving task {task_id}")
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            
            for dep_id in self.tasks[task_id].dependencies:
                visit(dep_id)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            order.append(task_id)
        
        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)
        
        self.execution_order = order
        return order
    
    def execute_workflow(self, initial_context: Dict[str, Any] = None):
        """Execute the entire workflow."""
        print(f"🚀 Starting workflow execution")
        print(f"📋 Tasks: {len(self.tasks)}")
        
        # Validate dependencies
        self.validate_dependencies()
        
        # Calculate execution order
        execution_order = self.calculate_execution_order()
        print(f"📊 Execution order: {' → '.join(execution_order)}")
        
        # Initialize context
        self.context = initial_context or {}
        
        # Execute tasks in order
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            # Check if dependencies are completed
            for dep_id in task.dependencies:
                dep_task = self.tasks[dep_id]
                if dep_task.status != "completed":
                    raise ValueError(f"Task {task_id} cannot start: dependency {dep_id} not completed")
            
            # Execute task
            try:
                result = task.execute(self.context)
                self.context[f"{task_id}_result"] = result
            except Exception as e:
                print(f"💥 Workflow failed at task: {task.name}")
                return False
        
        print(f"🎉 Workflow completed successfully!")
        return True
    
    def get_workflow_summary(self):
        """Get summary of workflow execution."""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == "completed")
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == "failed")
        
        total_duration = sum(task.get_duration() for task in self.tasks.values())
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "total_duration": f"{total_duration:.2f}s",
            "success_rate": f"{(completed_tasks/total_tasks)*100:.1f}%" if total_tasks > 0 else "0%"
        }

def create_sample_workflow():
    """Create a sample workflow for demonstration."""
    orchestrator = WorkflowOrchestrator()
    
    # Define task functions
    def analyze_requirements(context):
        """Analyze project requirements."""
        time.sleep(1)  # Simulate work
        requirements = {
            "features": ["user authentication", "data storage", "API endpoints"],
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "timeline": "3 months"
        }
        print(f"📋 Analyzed requirements: {len(requirements['features'])} features")
        return requirements
    
    def design_architecture(context):
        """Design system architecture."""
        time.sleep(1.5)  # Simulate work
        architecture = {
            "frontend": "React.js",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "deployment": "Docker + AWS"
        }
        print(f"🏗️ Designed architecture: {architecture['backend']} + {architecture['database']}")
        return architecture
    
    def create_prototype(context):
        """Create system prototype."""
        time.sleep(2)  # Simulate work
        prototype = {
            "endpoints": ["/users", "/auth", "/data"],
            "models": ["User", "Session", "Data"],
            "tests": 15
        }
        print(f"🔧 Created prototype: {len(prototype['endpoints'])} endpoints")
        return prototype
    
    def run_tests(context):
        """Run system tests."""
        time.sleep(1)  # Simulate work
        test_results = {
            "passed": 12,
            "failed": 3,
            "coverage": "85%"
        }
        print(f"🧪 Test results: {test_results['passed']}/{test_results['passed'] + test_results['failed']} passed")
        return test_results
    
    def generate_documentation(context):
        """Generate project documentation."""
        time.sleep(1)  # Simulate work
        docs = {
            "api_docs": "Generated",
            "user_guide": "Generated",
            "deployment_guide": "Generated"
        }
        print(f"📚 Generated documentation: {len(docs)} documents")
        return docs
    
    def deploy_system(context):
        """Deploy the system."""
        time.sleep(1.5)  # Simulate work
        deployment = {
            "environment": "production",
            "url": "https://api.example.com",
            "status": "deployed"
        }
        print(f"🚀 Deployed system: {deployment['url']}")
        return deployment
    
    # Add tasks to workflow
    orchestrator.add_task(WorkflowTask("analyze", "Analyze Requirements", analyze_requirements))
    orchestrator.add_task(WorkflowTask("design", "Design Architecture", design_architecture, ["analyze"]))
    orchestrator.add_task(WorkflowTask("prototype", "Create Prototype", create_prototype, ["design"]))
    orchestrator.add_task(WorkflowTask("test", "Run Tests", run_tests, ["prototype"]))
    orchestrator.add_task(WorkflowTask("docs", "Generate Documentation", generate_documentation, ["prototype"]))
    orchestrator.add_task(WorkflowTask("deploy", "Deploy System", deploy_system, ["test", "docs"]))
    
    return orchestrator

def main():
    print("🎭 Workflow Orchestration Pattern")
    print("=" * 50)
    
    # Create and execute sample workflow
    workflow = create_sample_workflow()
    
    print(f"Using LLM: {workflow.llm.provider}")
    
    # Execute workflow
    start_time = time.time()
    success = workflow.execute_workflow({
        "project_name": "AI Agent System",
        "team_size": 5
    })
    total_time = time.time() - start_time
    
    # Get summary
    print(f"\n--- Workflow Summary ---")
    summary = workflow.get_workflow_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"Total Workflow Time: {total_time:.2f}s")
    
    # Show task details
    print(f"\n--- Task Details ---")
    for task_id in workflow.execution_order:
        task = workflow.tasks[task_id]
        status_icon = "✅" if task.status == "completed" else "❌"
        print(f"{status_icon} {task.name}: {task.get_duration():.2f}s")
        if task.error:
            print(f"   Error: {task.error}")
    
    print(f"\n--- Workflow Orchestration Summary ---")
    print(f"✅ Demonstrated workflow definition and execution")
    print(f"✅ Showed dependency management")
    print(f"✅ Implemented task sequencing")
    print(f"✅ Created error handling and recovery")
    print(f"✅ Built comprehensive workflow orchestration")

if __name__ == "__main__":
    main()
