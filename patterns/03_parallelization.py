#!/usr/bin/env python3
"""
03 - Parallelization Pattern
Simple example showing how to run multiple LLM calls in parallel.

This demonstrates:
1. Multiple independent tasks
2. Run them simultaneously
3. Combine results
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def analyze_topic(topic, llm):
    """Analyze a single topic."""
    prompt = f"Give me 3 key facts about {topic}"
    response = llm.generate(prompt)
    return f"{topic}: {response.content}"

def main():
    print("⚡ Parallelization Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Topics to analyze
    topics = ["Python", "AI", "Machine Learning"]
    
    print(f"Analyzing {len(topics)} topics...")
    
    # Sequential approach (slow)
    print("\n🐌 Sequential (one by one):")
    for topic in topics:
        result = analyze_topic(topic, llm)
        print(f"  {result}")
    
    # Parallel approach (fast)
    print("\n🚀 Parallel (all at once):")
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks
        futures = [executor.submit(analyze_topic, topic, llm) for topic in topics]
        
        # Get results as they complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f"  {result}")
    
    print("\n✅ Parallel execution is much faster!")

if __name__ == "__main__":
    main()
