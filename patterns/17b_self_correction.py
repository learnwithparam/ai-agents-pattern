#!/usr/bin/env python3
"""
17b - Self-Correction Pattern
Simple example showing self-correction and validation for better reasoning.

This demonstrates:
1. Generate initial solution
2. Review and identify errors
3. Correct and improve solution
4. Validate final result
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def self_correction_reasoning(problem, llm):
    """Use self-correction to improve reasoning."""
    # Step 1: Initial attempt
    initial_prompt = f"""
    Solve this problem: {problem}
    
    Provide your initial solution.
    """
    
    initial_solution = llm.generate(initial_prompt).content
    
    # Step 2: Self-correction
    correction_prompt = f"""
    Problem: {problem}
    
    Initial solution: {initial_solution}
    
    Now review your solution and identify any errors or improvements:
    1. Is the solution correct?
    2. Are there any logical errors?
    3. Can the solution be improved?
    4. What would be a better approach?
    
    Provide a corrected and improved solution.
    """
    
    corrected_solution = llm.generate(correction_prompt).content
    
    return {
        "initial": initial_solution,
        "corrected": corrected_solution
    }

def main():
    print("🔄 Self-Correction Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Test problems
    test_problems = [
        "Calculate the area of a circle with radius 5",
        "Write a Python function to find the factorial of a number",
        "Explain the difference between HTTP and HTTPS"
    ]
    
    for i, problem in enumerate(test_problems):
        print(f"\n--- Test {i + 1}: {problem[:50]}... ---")
        
        result = self_correction_reasoning(problem, llm)
        
        print(f"Initial Solution: {result['initial'][:200]}...")
        print(f"Corrected Solution: {result['corrected'][:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
