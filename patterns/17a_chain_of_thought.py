#!/usr/bin/env python3
"""
17a - Chain-of-Thought (CoT) Reasoning Pattern
Simple example showing Chain-of-Thought reasoning for better problem solving.

This demonstrates:
1. Step-by-step reasoning process
2. Breaking down complex problems
3. Showing reasoning chain
4. Verifying solutions
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def chain_of_thought_reasoning(problem, llm):
    """Use Chain-of-Thought reasoning to solve problems."""
    prompt = f"""
    Solve this problem step by step using Chain-of-Thought reasoning:
    
    Problem: {problem}
    
    Think through this step by step:
    1. What is the problem asking?
    2. What information do I need?
    3. What steps should I take?
    4. What is the solution?
    5. How can I verify my answer?
    
    Show your reasoning process clearly.
    """
    
    return llm.generate(prompt).content

def main():
    print("🧠 Chain-of-Thought (CoT) Reasoning Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Test problems
    test_problems = [
        "If a train leaves station A at 60 mph and another leaves station B at 40 mph, and they are 200 miles apart, when will they meet?",
        "How can I optimize the performance of a Python web application?",
        "What are the pros and cons of using microservices architecture?"
    ]
    
    for i, problem in enumerate(test_problems):
        print(f"\n--- Test {i + 1}: {problem[:50]}... ---")
        
        result = chain_of_thought_reasoning(problem, llm)
        print(f"CoT Result: {result[:300]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
