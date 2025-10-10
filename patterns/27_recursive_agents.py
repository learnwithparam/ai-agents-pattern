#!/usr/bin/env python3
"""
27 - Recursive Agents Pattern
Simple example showing how to implement recursive AI agents that can call themselves.

This demonstrates:
1. Self-referencing agent architecture
2. Recursive problem decomposition
3. Dynamic depth control
4. Recursive task execution
"""

import sys
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class RecursiveAgent:
    """An AI agent that can recursively call itself to solve complex problems."""
    
    def __init__(self, max_depth: int = 3):
        self.llm = get_llm()
        self.max_depth = max_depth
        self.current_depth = 0
        self.call_stack = []
        self.solutions = {}
    
    def solve_problem(self, problem: str, depth: int = 0) -> Dict[str, Any]:
        """Recursively solve a problem by breaking it down into smaller parts."""
        
        # Prevent infinite recursion
        if depth >= self.max_depth:
            return {
                "solution": "Maximum recursion depth reached",
                "depth": depth,
                "status": "max_depth_reached"
            }
        
        self.current_depth = depth
        self.call_stack.append({
            "problem": problem,
            "depth": depth,
            "timestamp": self._get_timestamp()
        })
        
        print(f"{'  ' * depth}🔄 Recursive call at depth {depth}: {problem[:50]}...")
        
        # Analyze if problem can be broken down further
        analysis = self._analyze_problem(problem, depth)
        
        if analysis["should_decompose"] and depth < self.max_depth - 1:
            # Break down into sub-problems
            sub_problems = analysis["sub_problems"]
            sub_solutions = []
            
            for i, sub_problem in enumerate(sub_problems):
                print(f"{'  ' * depth}📋 Sub-problem {i+1}: {sub_problem[:30]}...")
                sub_solution = self.solve_problem(sub_problem, depth + 1)
                sub_solutions.append(sub_solution)
            
            # Combine sub-solutions
            final_solution = self._combine_solutions(problem, sub_solutions, depth)
            
        else:
            # Solve directly
            final_solution = self._solve_directly(problem, depth)
        
        # Store solution
        solution_key = f"depth_{depth}_{hash(problem) % 1000}"
        self.solutions[solution_key] = final_solution
        
        print(f"{'  ' * depth}✅ Solution at depth {depth}: {final_solution['solution'][:50]}...")
        
        return final_solution
    
    def _analyze_problem(self, problem: str, depth: int) -> Dict[str, Any]:
        """Analyze if a problem should be decomposed further."""
        
        prompt = f"""
        Analyze this problem and determine if it should be broken down into smaller parts:
        
        Problem: "{problem}"
        Current depth: {depth}
        Max depth: {self.max_depth}
        
        Respond with:
        DECOMPOSE: [yes/no]
        REASON: [brief explanation]
        SUB_PROBLEMS: [list 2-3 sub-problems if decomposing, or "none"]
        
        Consider:
        - Is this a complex problem that can be broken down?
        - Are there logical sub-components?
        - Would breaking it down help solve it better?
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response
        should_decompose = "yes" in response.lower() and "decompose" in response.lower()
        sub_problems = []
        
        if should_decompose:
            # Extract sub-problems (simplified parsing)
            lines = response.split('\n')
            for line in lines:
                if 'sub_problems:' in line.lower():
                    # Extract sub-problems from the line
                    sub_text = line.split(':', 1)[1].strip()
                    # Simple parsing - split by common delimiters
                    for delimiter in [',', ';', '\n']:
                        if delimiter in sub_text:
                            sub_problems = [p.strip() for p in sub_text.split(delimiter) if p.strip()]
                            break
                    break
        
        return {
            "should_decompose": should_decompose,
            "reason": response,
            "sub_problems": sub_problems[:3]  # Limit to 3 sub-problems
        }
    
    def _solve_directly(self, problem: str, depth: int) -> Dict[str, Any]:
        """Solve a problem directly without further decomposition."""
        
        prompt = f"""
        Solve this problem directly:
        
        Problem: "{problem}"
        
        Provide a clear, actionable solution.
        """
        
        solution = self.llm.generate(prompt).content
        
        return {
            "solution": solution,
            "depth": depth,
            "status": "solved_directly",
            "method": "direct_solution"
        }
    
    def _combine_solutions(self, original_problem: str, sub_solutions: List[Dict[str, Any]], depth: int) -> Dict[str, Any]:
        """Combine sub-solutions into a final solution."""
        
        # Extract solutions from sub-problems
        sub_solution_texts = [sol["solution"] for sol in sub_solutions]
        
        prompt = f"""
        Combine these sub-solutions to solve the original problem:
        
        Original Problem: "{original_problem}"
        
        Sub-solutions:
        {chr(10).join([f"{i+1}. {sol}" for i, sol in enumerate(sub_solution_texts)])}
        
        Provide a comprehensive solution that integrates all sub-solutions.
        """
        
        combined_solution = self.llm.generate(prompt).content
        
        return {
            "solution": combined_solution,
            "depth": depth,
            "status": "solved_recursively",
            "method": "recursive_decomposition",
            "sub_solutions": sub_solutions
        }
    
    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def get_call_stack(self):
        """Get the current call stack."""
        return self.call_stack
    
    def get_solutions_summary(self):
        """Get a summary of all solutions."""
        summary = f"""
        📊 Recursive Solutions Summary
        =============================
        Total Solutions: {len(self.solutions)}
        Max Depth Used: {max([sol['depth'] for sol in self.solutions.values()]) if self.solutions else 0}
        
        Solutions by Depth:
        """
        
        depth_counts = {}
        for solution in self.solutions.values():
            depth = solution['depth']
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        for depth in sorted(depth_counts.keys()):
            summary += f"  Depth {depth}: {depth_counts[depth]} solutions\n"
        
        return summary

class RecursiveTaskExecutor:
    """An executor that can recursively handle complex tasks."""
    
    def __init__(self, max_depth: int = 4):
        self.llm = get_llm()
        self.max_depth = max_depth
        self.execution_log = []
    
    def execute_task(self, task: str, context: Dict[str, Any] = None, depth: int = 0) -> Dict[str, Any]:
        """Recursively execute a task by breaking it into subtasks."""
        
        if context is None:
            context = {}
        
        if depth >= self.max_depth:
            return {
                "result": "Maximum execution depth reached",
                "depth": depth,
                "status": "max_depth_reached"
            }
        
        print(f"{'  ' * depth}🎯 Executing task at depth {depth}: {task[:40]}...")
        
        # Log execution
        self.execution_log.append({
            "task": task,
            "depth": depth,
            "context": context.copy(),
            "timestamp": self._get_timestamp()
        })
        
        # Analyze task complexity
        complexity_analysis = self._analyze_task_complexity(task, depth)
        
        if complexity_analysis["is_complex"] and depth < self.max_depth - 1:
            # Break into subtasks
            subtasks = complexity_analysis["subtasks"]
            subtask_results = []
            
            for i, subtask in enumerate(subtasks):
                print(f"{'  ' * depth}📝 Subtask {i+1}: {subtask[:30]}...")
                subtask_result = self.execute_task(subtask, context, depth + 1)
                subtask_results.append(subtask_result)
            
            # Combine results
            final_result = self._combine_task_results(task, subtask_results, depth)
            
        else:
            # Execute directly
            final_result = self._execute_directly(task, context, depth)
        
        print(f"{'  ' * depth}✅ Task completed at depth {depth}")
        
        return final_result
    
    def _analyze_task_complexity(self, task: str, depth: int) -> Dict[str, Any]:
        """Analyze if a task is complex enough to break down."""
        
        prompt = f"""
        Analyze this task and determine if it should be broken into subtasks:
        
        Task: "{task}"
        Current depth: {depth}
        
        Respond with:
        COMPLEX: [yes/no]
        REASON: [brief explanation]
        SUBTASKS: [list 2-3 subtasks if complex, or "none"]
        """
        
        response = self.llm.generate(prompt).content
        
        is_complex = "yes" in response.lower() and "complex" in response.lower()
        subtasks = []
        
        if is_complex:
            # Extract subtasks (simplified parsing)
            lines = response.split('\n')
            for line in lines:
                if 'subtasks:' in line.lower():
                    sub_text = line.split(':', 1)[1].strip()
                    for delimiter in [',', ';', '\n']:
                        if delimiter in sub_text:
                            subtasks = [t.strip() for t in sub_text.split(delimiter) if t.strip()]
                            break
                    break
        
        return {
            "is_complex": is_complex,
            "reason": response,
            "subtasks": subtasks[:3]  # Limit to 3 subtasks
        }
    
    def _execute_directly(self, task: str, context: Dict[str, Any], depth: int) -> Dict[str, Any]:
        """Execute a task directly."""
        
        prompt = f"""
        Execute this task:
        
        Task: "{task}"
        Context: {context}
        
        Provide the result of executing this task.
        """
        
        result = self.llm.generate(prompt).content
        
        return {
            "result": result,
            "depth": depth,
            "status": "executed_directly",
            "method": "direct_execution"
        }
    
    def _combine_task_results(self, original_task: str, subtask_results: List[Dict[str, Any]], depth: int) -> Dict[str, Any]:
        """Combine subtask results into a final result."""
        
        subtask_texts = [result["result"] for result in subtask_results]
        
        prompt = f"""
        Combine these subtask results to complete the original task:
        
        Original Task: "{original_task}"
        
        Subtask Results:
        {chr(10).join([f"{i+1}. {result}" for i, result in enumerate(subtask_texts)])}
        
        Provide the final result that combines all subtask results.
        """
        
        combined_result = self.llm.generate(prompt).content
        
        return {
            "result": combined_result,
            "depth": depth,
            "status": "executed_recursively",
            "method": "recursive_execution",
            "subtask_results": subtask_results
        }
    
    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def get_execution_log(self):
        """Get the execution log."""
        return self.execution_log

def main():
    print("🔄 Recursive Agents Pattern")
    print("=" * 50)
    
    # Test recursive problem solving
    print(f"\n--- Recursive Problem Solving ---")
    recursive_agent = RecursiveAgent(max_depth=3)
    
    test_problems = [
        "How can I improve my team's productivity?",
        "What are the steps to launch a successful startup?",
        "How do I learn machine learning effectively?"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n{'='*60}")
        print(f"PROBLEM {i}: {problem}")
        print(f"{'='*60}")
        
        solution = recursive_agent.solve_problem(problem)
        
        print(f"\n📋 Final Solution:")
        print(f"Status: {solution['status']}")
        print(f"Method: {solution['method']}")
        print(f"Depth: {solution['depth']}")
        print(f"Solution: {solution['solution'][:200]}...")
    
    # Show call stack and solutions summary
    print(f"\n--- Call Stack ---")
    call_stack = recursive_agent.get_call_stack()
    for i, call in enumerate(call_stack, 1):
        print(f"{i}. Depth {call['depth']}: {call['problem'][:50]}... at {call['timestamp']}")
    
    print(f"\n{recursive_agent.get_solutions_summary()}")
    
    # Test recursive task execution
    print(f"\n--- Recursive Task Execution ---")
    task_executor = RecursiveTaskExecutor(max_depth=3)
    
    test_tasks = [
        "Plan a birthday party",
        "Organize a team meeting",
        "Create a marketing campaign"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*60}")
        print(f"TASK {i}: {task}")
        print(f"{'='*60}")
        
        result = task_executor.execute_task(task)
        
        print(f"\n📋 Execution Result:")
        print(f"Status: {result['status']}")
        print(f"Method: {result['method']}")
        print(f"Depth: {result['depth']}")
        print(f"Result: {result['result'][:200]}...")
    
    # Show execution log
    print(f"\n--- Execution Log ---")
    execution_log = task_executor.get_execution_log()
    for i, log_entry in enumerate(execution_log, 1):
        print(f"{i}. Depth {log_entry['depth']}: {log_entry['task'][:40]}... at {log_entry['timestamp']}")
    
    print(f"\n--- Recursive Agents Pattern Summary ---")
    print(f"✅ Demonstrated self-referencing agent architecture")
    print(f"✅ Showed recursive problem decomposition")
    print(f"✅ Implemented dynamic depth control")
    print(f"✅ Created recursive task execution system")

if __name__ == "__main__":
    main()
