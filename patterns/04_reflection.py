#!/usr/bin/env python3
"""
04 - Reflection Pattern
Simple example showing how to use reflection to improve code quality.

This demonstrates:
1. Generate initial code
2. Reflect on the code quality
3. Iteratively improve based on feedback
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def generate_code(task, llm):
    """Generate initial code for the task."""
    prompt = f"""
    Create a Python function for this task:
    {task}
    
    Requirements:
    - Include clear docstring
    - Handle edge cases
    - Include error handling
    - Follow Python best practices
    """
    return llm.generate(prompt).content

def reflect_on_code(code, task, llm):
    """Reflect on the code quality and provide feedback."""
    prompt = f"""
    You are a senior Python developer reviewing this code:
    
    Task: {task}
    
    Code:
    {code}
    
    Review the code and provide specific feedback:
    - Are there any bugs or issues?
    - Are edge cases handled properly?
    - Is the code readable and well-documented?
    - Are there any improvements needed?
    
    If the code is perfect, respond with "CODE_IS_PERFECT".
    Otherwise, provide specific suggestions for improvement.
    """
    return llm.generate(prompt).content

def improve_code(code, feedback, task, llm):
    """Improve the code based on feedback."""
    prompt = f"""
    Original task: {task}
    
    Current code:
    {code}
    
    Feedback from code review:
    {feedback}
    
    Please improve the code based on the feedback. Keep the same function name and interface.
    """
    return llm.generate(prompt).content

def main():
    print("🔄 Reflection Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Task: Create a function to calculate factorial
    task = """
    Create a function called 'calculate_factorial' that:
    1. Takes an integer n as input
    2. Returns n! (factorial of n)
    3. Handles edge cases (0! = 1)
    4. Raises ValueError for negative numbers
    """
    
    print(f"Task: {task.strip()}")
    
    # Reflection loop
    max_iterations = 3
    current_code = ""
    
    for i in range(max_iterations):
        print(f"\n--- Iteration {i + 1} ---")
        
        if i == 0:
            print("Generating initial code...")
            current_code = generate_code(task, llm)
        else:
            print("Improving code based on feedback...")
            current_code = improve_code(current_code, feedback, task, llm)
        
        print(f"\nCode (v{i + 1}):")
        print(current_code)
        
        # Reflect on the code
        print("\nReflecting on code quality...")
        feedback = reflect_on_code(current_code, task, llm)
        
        if "CODE_IS_PERFECT" in feedback:
            print("\n✅ Code is perfect! No further improvements needed.")
            break
        
        print(f"\nFeedback: {feedback}")
    
    print(f"\n🎯 Final Result:")
    print("=" * 40)
    print(current_code)

if __name__ == "__main__":
    main()
