#!/usr/bin/env python3
"""
17c - Problem Decomposition Pattern
Simple example showing how to break down complex problems into smaller parts.

This demonstrates:
1. Analyze complex problems
2. Break into smaller components
3. Identify sub-problems
4. Plan solution order
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def problem_decomposition(problem, llm):
    """Break down complex problems into smaller parts."""
    prompt = f"""
    Break down this complex problem into smaller, manageable parts:
    
    Problem: {problem}
    
    Decompose it into:
    1. What are the main components?
    2. What are the sub-problems?
    3. What is the order of solving them?
    4. How do the parts connect?
    
    Provide a structured breakdown.
    """
    
    return llm.generate(prompt).content

def main():
    print("🔧 Problem Decomposition Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Test problems
    test_problems = [
        "Design a system for managing a library's book inventory",
        "Create a web application for online shopping",
        "Build a machine learning model to predict house prices"
    ]
    
    for i, problem in enumerate(test_problems):
        print(f"\n--- Test {i + 1}: {problem[:50]}... ---")
        
        result = problem_decomposition(problem, llm)
        print(f"Decomposition: {result[:300]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
