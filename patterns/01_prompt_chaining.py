#!/usr/bin/env python3
"""
01 - Prompt Chaining Pattern
Simple example showing how to chain prompts together.

This demonstrates:
1. Extract information from text
2. Transform it into structured format
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def main():
    print("🔗 Prompt Chaining Pattern")
    print("=" * 40)
    
    # Get LLM (auto-detects provider from your API keys)
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Input text
    text = "The laptop has an Intel i7 processor, 16GB RAM, and 512GB SSD."
    print(f"Input: {text}")
    
    # Step 1: Extract specifications
    print("\nStep 1: Extracting specs...")
    extract_prompt = f"Extract the technical specifications from: {text}"
    specs = llm.generate(extract_prompt).content
    print(f"Extracted: {specs}")
    
    # Step 2: Format as JSON
    print("\nStep 2: Formatting as JSON...")
    json_prompt = f"Convert these specs to JSON: {specs}"
    result = llm.generate(json_prompt).content
    print(f"JSON: {result}")

if __name__ == "__main__":
    main()