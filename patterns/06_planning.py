#!/usr/bin/env python3
"""
06 - Planning Pattern
Simple example showing how to break down complex tasks into plans.

This demonstrates:
1. Analyze the main task
2. Create a structured plan
3. Execute the plan step by step
4. Combine results into final output
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def create_plan(task, llm):
    """Create a structured plan for the given task."""
    prompt = f"""
    Create a detailed plan for this task: {task}
    
    Break it down into 3-5 clear, actionable steps.
    Each step should be specific and measurable.
    
    Format your response as:
    Step 1: [Description]
    Step 2: [Description]
    Step 3: [Description]
    etc.
    """
    return llm.generate(prompt).content

def execute_step(step, context, llm):
    """Execute a single step of the plan."""
    prompt = f"""
    Task context: {context}
    
    Execute this step: {step}
    
    Provide a clear, actionable result for this step.
    """
    return llm.generate(prompt).content

def combine_results(plan, results, task, llm):
    """Combine all step results into a final output."""
    results_text = "\n".join([f"Step {i+1}: {result}" for i, result in enumerate(results)])
    
    prompt = f"""
    Original task: {task}
    
    Plan:
    {plan}
    
    Step results:
    {results_text}
    
    Combine all the step results into a comprehensive final output that addresses the original task.
    """
    return llm.generate(prompt).content

def main():
    print("📋 Planning Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Example task
    task = "Write a comprehensive guide on how to learn Python programming for beginners"
    
    print(f"Task: {task}")
    
    # Step 1: Create plan
    print(f"\n--- Step 1: Creating Plan ---")
    plan = create_plan(task, llm)
    print(f"Plan:\n{plan}")
    
    # Step 2: Execute each step
    print(f"\n--- Step 2: Executing Plan ---")
    steps = [line.strip() for line in plan.split('\n') if line.strip().startswith('Step')]
    results = []
    
    for i, step in enumerate(steps):
        print(f"\nExecuting: {step}")
        result = execute_step(step, task, llm)
        results.append(result)
        print(f"Result: {result[:100]}...")
    
    # Step 3: Combine results
    print(f"\n--- Step 3: Combining Results ---")
    final_output = combine_results(plan, results, task, llm)
    
    print(f"\n🎯 Final Output:")
    print("=" * 40)
    print(final_output)

if __name__ == "__main__":
    main()
