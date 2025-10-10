#!/usr/bin/env python3
"""
16 - Resource-Aware Optimization Pattern
Simple example showing how to optimize resource usage based on task complexity.

This demonstrates:
1. Analyze task complexity
2. Choose appropriate resources
3. Optimize for cost vs performance
4. Monitor resource usage
"""

import sys
import os
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ResourceOptimizer:
    """Optimizes resource usage based on task complexity."""
    
    def __init__(self):
        self.llm = get_llm()
        self.resource_usage = {
            "simple_tasks": 0,
            "complex_tasks": 0,
            "total_tokens": 0,
            "total_time": 0
        }
    
    def analyze_complexity(self, task):
        """Analyze task complexity."""
        # Simple heuristics for complexity analysis
        complexity_score = 0
        
        # Length-based complexity
        word_count = len(task.split())
        if word_count > 50:
            complexity_score += 3
        elif word_count > 20:
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Keyword-based complexity
        complex_keywords = [
            "analyze", "comprehensive", "detailed", "complex", "advanced",
            "research", "investigate", "evaluate", "compare", "synthesize"
        ]
        
        for keyword in complex_keywords:
            if keyword.lower() in task.lower():
                complexity_score += 2
        
        # Question type complexity
        if "?" in task:
            complexity_score += 1
        
        if task.lower().startswith(("what", "how", "why", "when", "where")):
            complexity_score += 1
        
        return complexity_score
    
    def choose_strategy(self, task, complexity_score):
        """Choose optimization strategy based on complexity."""
        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 6:
            return "balanced"
        else:
            return "complex"
    
    def process_simple_task(self, task):
        """Process simple tasks with minimal resources."""
        print("🟢 Using simple processing strategy")
        
        # Use shorter, more focused prompt
        prompt = f"Answer briefly: {task}"
        
        start_time = time.time()
        response = self.llm.generate(prompt, temperature=0.3).content
        end_time = time.time()
        
        self.resource_usage["simple_tasks"] += 1
        self.resource_usage["total_time"] += (end_time - start_time)
        
        return {
            "response": response,
            "strategy": "simple",
            "processing_time": end_time - start_time,
            "estimated_tokens": len(prompt) + len(response)
        }
    
    def process_balanced_task(self, task):
        """Process balanced tasks with moderate resources."""
        print("🟡 Using balanced processing strategy")
        
        # Use moderate prompt with some context
        prompt = f"""
        Task: {task}
        
        Provide a clear and helpful response. Include relevant details but keep it concise.
        """
        
        start_time = time.time()
        response = self.llm.generate(prompt, temperature=0.5).content
        end_time = time.time()
        
        self.resource_usage["total_time"] += (end_time - start_time)
        
        return {
            "response": response,
            "strategy": "balanced",
            "processing_time": end_time - start_time,
            "estimated_tokens": len(prompt) + len(response)
        }
    
    def process_complex_task(self, task):
        """Process complex tasks with full resources."""
        print("🔴 Using complex processing strategy")
        
        # Use comprehensive prompt with detailed instructions
        prompt = f"""
        Task: {task}
        
        Provide a comprehensive and detailed response. Include:
        1. Clear explanation of the main points
        2. Relevant examples or details
        3. Practical implications or next steps
        4. Any important considerations
        
        Be thorough but well-organized.
        """
        
        start_time = time.time()
        response = self.llm.generate(prompt, temperature=0.7).content
        end_time = time.time()
        
        self.resource_usage["complex_tasks"] += 1
        self.resource_usage["total_time"] += (end_time - start_time)
        
        return {
            "response": response,
            "strategy": "complex",
            "processing_time": end_time - start_time,
            "estimated_tokens": len(prompt) + len(response)
        }
    
    def process_task(self, task):
        """Process a task with resource optimization."""
        print(f"📋 Processing task: {task[:50]}...")
        
        # Analyze complexity
        complexity_score = self.analyze_complexity(task)
        print(f"Complexity score: {complexity_score}")
        
        # Choose strategy
        strategy = self.choose_strategy(task, complexity_score)
        print(f"Selected strategy: {strategy}")
        
        # Process based on strategy
        if strategy == "simple":
            return self.process_simple_task(task)
        elif strategy == "balanced":
            return self.process_balanced_task(task)
        else:
            return self.process_complex_task(task)
    
    def get_resource_usage(self):
        """Get resource usage statistics."""
        total_tasks = self.resource_usage["simple_tasks"] + self.resource_usage["complex_tasks"]
        
        return {
            "total_tasks": total_tasks,
            "simple_tasks": self.resource_usage["simple_tasks"],
            "complex_tasks": self.resource_usage["complex_tasks"],
            "total_time": self.resource_usage["total_time"],
            "average_time": self.resource_usage["total_time"] / max(1, total_tasks),
            "simple_task_ratio": self.resource_usage["simple_tasks"] / max(1, total_tasks),
            "complex_task_ratio": self.resource_usage["complex_tasks"] / max(1, total_tasks)
        }
    
    def optimize_settings(self):
        """Suggest optimization settings based on usage patterns."""
        usage = self.get_resource_usage()
        
        suggestions = []
        
        if usage["simple_task_ratio"] > 0.7:
            suggestions.append("Consider using a faster, cheaper model for simple tasks")
        
        if usage["complex_task_ratio"] > 0.5:
            suggestions.append("Consider using a more powerful model for complex tasks")
        
        if usage["average_time"] > 5.0:
            suggestions.append("Consider optimizing prompts for faster processing")
        
        return suggestions

def main():
    print("⚡ Resource-Aware Optimization Pattern")
    print("=" * 40)
    
    # Initialize resource optimizer
    optimizer = ResourceOptimizer()
    
    # Test tasks with different complexity levels
    test_tasks = [
        "What's the weather like?",  # Simple
        "How do I learn Python programming?",  # Balanced
        "Can you provide a comprehensive analysis of the impact of AI on software development, including historical context, current trends, and future implications?",  # Complex
        "Hello",  # Simple
        "What are the best practices for error handling in Python applications?",  # Balanced
        "Explain the theoretical foundations of machine learning, including mathematical principles, algorithmic approaches, and practical applications in various industries."  # Complex
    ]
    
    print("Testing resource optimization with different task complexities...")
    
    results = []
    for i, task in enumerate(test_tasks):
        print(f"\n--- Test {i + 1} ---")
        result = optimizer.process_task(task)
        results.append(result)
        
        print(f"Strategy: {result['strategy']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Response: {result['response'][:100]}...")
        print("-" * 40)
    
    # Show resource usage statistics
    print(f"\n--- Resource Usage Statistics ---")
    usage = optimizer.get_resource_usage()
    print(f"Total tasks: {usage['total_tasks']}")
    print(f"Simple tasks: {usage['simple_tasks']} ({usage['simple_task_ratio']:.1%})")
    print(f"Complex tasks: {usage['complex_tasks']} ({usage['complex_task_ratio']:.1%})")
    print(f"Total time: {usage['total_time']:.2f}s")
    print(f"Average time per task: {usage['average_time']:.2f}s")
    
    # Show optimization suggestions
    print(f"\n--- Optimization Suggestions ---")
    suggestions = optimizer.optimize_settings()
    if suggestions:
        for suggestion in suggestions:
            print(f"💡 {suggestion}")
    else:
        print("✅ Current resource usage is well-optimized")

if __name__ == "__main__":
    main()
