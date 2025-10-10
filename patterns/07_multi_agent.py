#!/usr/bin/env python3
"""
07 - Multi-Agent Pattern
Simple example showing how to coordinate multiple AI agents.

This demonstrates:
1. Define specialized agents with different roles
2. Coordinate agents to work together
3. Pass information between agents
4. Combine results from multiple agents
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class Agent:
    """Simple agent class."""
    def __init__(self, name, role, expertise):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.llm = get_llm()
    
    def work(self, task, context=""):
        """Agent performs its specialized work."""
        prompt = f"""
        You are {self.name}, a {self.role} with expertise in {self.expertise}.
        
        Task: {task}
        Context: {context}
        
        Provide your specialized input for this task.
        """
        return self.llm.generate(prompt).content

def coordinate_agents(agents, task):
    """Coordinate multiple agents to work on a task."""
    print(f"Coordinating {len(agents)} agents for task: {task}")
    
    results = {}
    context = ""
    
    # Sequential execution - each agent builds on previous work
    for agent in agents:
        print(f"\n--- {agent.name} ({agent.role}) working ---")
        result = agent.work(task, context)
        results[agent.name] = result
        context += f"\n{agent.name} ({agent.role}): {result}"
        print(f"Result: {result[:100]}...")
    
    return results

def combine_agent_results(results, task, llm):
    """Combine results from all agents into final output."""
    results_text = "\n".join([f"{name}: {result}" for name, result in results.items()])
    
    prompt = f"""
    Original task: {task}
    
    Results from specialized agents:
    {results_text}
    
    Combine all the agent results into a comprehensive final response.
    """
    return llm.generate(prompt).content

def main():
    print("🤖 Multi-Agent Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Define specialized agents
    agents = [
        Agent("Researcher", "Research Specialist", "gathering and analyzing information"),
        Agent("Analyst", "Data Analyst", "analyzing data and identifying patterns"),
        Agent("Writer", "Technical Writer", "creating clear, engaging content"),
        Agent("Reviewer", "Quality Reviewer", "ensuring accuracy and completeness")
    ]
    
    print(f"\nAvailable agents:")
    for agent in agents:
        print(f"- {agent.name}: {agent.role} (expertise: {agent.expertise})")
    
    # Example task
    task = "Create a comprehensive analysis of the impact of AI on software development"
    
    print(f"\nTask: {task}")
    
    # Coordinate agents
    print(f"\n--- Coordinating Agents ---")
    results = coordinate_agents(agents, task)
    
    # Combine results
    print(f"\n--- Combining Results ---")
    final_output = combine_agent_results(results, task, llm)
    
    print(f"\n🎯 Final Output:")
    print("=" * 40)
    print(final_output)

if __name__ == "__main__":
    main()
