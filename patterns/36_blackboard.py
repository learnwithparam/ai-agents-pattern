#!/usr/bin/env python3
"""
36 - Blackboard Systems Pattern
Multi-agent collaboration with shared memory and dynamic control.

The Blackboard pattern enables multiple specialist agents to collaborate by reading
from and writing to a shared, central data repository called the 'blackboard'. A
controller or scheduler dynamically determines which agent should act next based on
the evolving state of the solution on the blackboard. This allows for opportunistic
and emergent problem-solving workflows that adapt to the specific needs of each problem.

This demonstrates:
1. Shared blackboard for agent communication and data storage
2. Dynamic controller for intelligent agent activation
3. Specialist agents with different expertise areas
4. Opportunistic problem-solving workflow
5. Emergent collaboration patterns
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class Blackboard:
    """Shared memory space for agent collaboration."""
    
    def __init__(self):
        self.data = {
            "problem": "",
            "findings": [],
            "partial_solutions": [],
            "current_state": "initializing",
            "agent_contributions": {}
        }
    
    def read(self, key: str = None) -> Any:
        """Read data from blackboard."""
        if key:
            return self.data.get(key)
        return self.data.copy()
    
    def write(self, key: str, value: Any) -> None:
        """Write data to blackboard."""
        self.data[key] = value
    
    def add_finding(self, agent_name: str, finding: str, confidence: float = 1.0) -> None:
        """Add a finding to the blackboard."""
        self.data["findings"].append({
            "agent": agent_name,
            "finding": finding,
            "confidence": confidence,
            "timestamp": len(self.data["findings"])
        })
    
    def add_solution(self, agent_name: str, solution: str, completeness: float = 1.0) -> None:
        """Add a partial solution to the blackboard."""
        self.data["partial_solutions"].append({
            "agent": agent_name,
            "solution": solution,
            "completeness": completeness,
            "timestamp": len(self.data["partial_solutions"])
        })
    
    def get_summary(self) -> str:
        """Get a summary of current blackboard state."""
        summary = f"Problem: {self.data['problem']}\n"
        summary += f"Current State: {self.data['current_state']}\n"
        summary += f"Findings: {len(self.data['findings'])}\n"
        summary += f"Partial Solutions: {len(self.data['partial_solutions'])}\n"
        return summary

class SpecialistAgent:
    """Base class for specialist agents."""
    
    def __init__(self, name: str, expertise: str, llm):
        self.name = name
        self.expertise = expertise
        self.llm = llm
    
    def can_contribute(self, blackboard: Blackboard) -> bool:
        """Check if this agent can contribute to the current problem."""
        # Override in subclasses
        return True
    
    def contribute(self, blackboard: Blackboard) -> Dict[str, Any]:
        """Contribute to solving the problem."""
        # Override in subclasses
        return {"type": "finding", "content": "No contribution", "confidence": 0.0}

class ResearchAgent(SpecialistAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, llm):
        super().__init__("Researcher", "Research and Information Gathering", llm)
        self.research_tools = {
            "search": self._search_tool,
            "analyze": self._analyze_tool
        }
    
    def _search_tool(self, query: str) -> str:
        """Mock search tool."""
        mock_data = {
            "apple financial": "Apple Inc. reported revenue of $394.3 billion in 2023",
            "stock market": "The S&P 500 is a stock market index",
            "machine learning": "Machine learning is a subset of artificial intelligence",
            "python programming": "Python is a high-level programming language"
        }
        
        query_lower = query.lower()
        for key, value in mock_data.items():
            if key in query_lower:
                return value
        return f"Research data for: {query}"
    
    def _analyze_tool(self, data: str) -> str:
        """Mock analysis tool."""
        return f"Analysis of: {data[:50]}..."
    
    def can_contribute(self, blackboard: Blackboard) -> bool:
        """Can contribute if we need more information."""
        findings = blackboard.read("findings")
        return len(findings) < 3  # Need more research
    
    def contribute(self, blackboard: Blackboard) -> Dict[str, Any]:
        """Contribute research findings."""
        problem = blackboard.read("problem")
        
        # Generate research query based on problem
        prompt = f"""
        Based on this problem: {problem}
        
        Generate a specific research query to gather relevant information.
        Focus on factual, data-driven aspects.
        """
        
        query = self.llm.generate(prompt).content.strip()
        
        # Perform research
        research_result = self._search_tool(query)
        analysis = self._analyze_tool(research_result)
        
        # Add to blackboard
        finding = f"Research Query: {query}\nResult: {research_result}\nAnalysis: {analysis}"
        blackboard.add_finding(self.name, finding, 0.8)
        
        return {
            "type": "finding",
            "content": finding,
            "confidence": 0.8
        }

class AnalysisAgent(SpecialistAgent):
    """Agent specialized in data analysis and interpretation."""
    
    def __init__(self, llm):
        super().__init__("Analyst", "Data Analysis and Interpretation", llm)
    
    def can_contribute(self, blackboard: Blackboard) -> bool:
        """Can contribute if we have findings to analyze."""
        findings = blackboard.read("findings")
        return len(findings) >= 2  # Need findings to analyze
    
    def contribute(self, blackboard: Blackboard) -> Dict[str, Any]:
        """Contribute analysis of findings."""
        findings = blackboard.read("findings")
        problem = blackboard.read("problem")
        
        # Analyze findings
        findings_text = "\n".join([f["finding"] for f in findings])
        
        prompt = f"""
        Problem: {problem}
        
        Findings to analyze:
        {findings_text}
        
        Provide a comprehensive analysis of these findings.
        Identify patterns, relationships, and key insights.
        Suggest what additional information might be needed.
        """
        
        analysis = self.llm.generate(prompt).content
        
        # Add to blackboard
        blackboard.add_finding(self.name, f"Analysis: {analysis}", 0.9)
        
        return {
            "type": "analysis",
            "content": analysis,
            "confidence": 0.9
        }

class SolutionAgent(SpecialistAgent):
    """Agent specialized in generating solutions."""
    
    def __init__(self, llm):
        super().__init__("Solver", "Solution Generation", llm)
    
    def can_contribute(self, blackboard: Blackboard) -> bool:
        """Can contribute if we have enough information."""
        findings = blackboard.read("findings")
        return len(findings) >= 3  # Need sufficient information
    
    def contribute(self, blackboard: Blackboard) -> Dict[str, Any]:
        """Contribute solution based on findings."""
        findings = blackboard.read("findings")
        problem = blackboard.read("problem")
        
        # Generate solution
        findings_text = "\n".join([f["finding"] for f in findings])
        
        prompt = f"""
        Problem: {problem}
        
        Available information:
        {findings_text}
        
        Generate a comprehensive solution to the problem.
        Use the available information to support your solution.
        If information is incomplete, note what's missing.
        """
        
        solution = self.llm.generate(prompt).content
        
        # Add to blackboard
        blackboard.add_solution(self.name, solution, 0.85)
        
        return {
            "type": "solution",
            "content": solution,
            "confidence": 0.85
        }

class Controller:
    """Controller that decides which agent to activate next."""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = []
    
    def add_agent(self, agent: SpecialistAgent) -> None:
        """Add an agent to the system."""
        self.agents.append(agent)
    
    def select_agent(self, blackboard: Blackboard) -> Optional[SpecialistAgent]:
        """Select the best agent to activate next."""
        available_agents = [agent for agent in self.agents if agent.can_contribute(blackboard)]
        
        if not available_agents:
            return None
        
        # Simple priority-based selection
        # Research -> Analysis -> Solution
        for agent_type in [ResearchAgent, AnalysisAgent, SolutionAgent]:
            for agent in available_agents:
                if isinstance(agent, agent_type):
                    return agent
        
        # Fallback to first available
        return available_agents[0]
    
    def is_complete(self, blackboard: Blackboard) -> bool:
        """Check if the problem is solved."""
        solutions = blackboard.read("partial_solutions")
        findings = blackboard.read("findings")
        
        # Consider complete if we have solutions and sufficient findings
        return len(solutions) > 0 and len(findings) >= 3

class BlackboardSystem:
    """Main blackboard system orchestrator."""
    
    def __init__(self, llm):
        self.llm = llm
        self.blackboard = Blackboard()
        self.controller = Controller(llm)
        self.max_iterations = 5
        
        # Add specialist agents
        self.controller.add_agent(ResearchAgent(llm))
        self.controller.add_agent(AnalysisAgent(llm))
        self.controller.add_agent(SolutionAgent(llm))
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Solve a problem using blackboard system."""
        print(f"🎯 Problem: {problem}")
        print("=" * 50)
        
        # Initialize blackboard
        self.blackboard.write("problem", problem)
        self.blackboard.write("current_state", "active")
        
        print("\n📋 Blackboard System Starting")
        print("-" * 30)
        
        iterations = 0
        contributions = []
        
        while iterations < self.max_iterations:
            iterations += 1
            print(f"\n--- Iteration {iterations} ---")
            
            # Select next agent
            selected_agent = self.controller.select_agent(self.blackboard)
            
            if not selected_agent:
                print("No agents can contribute further")
                break
            
            print(f"Activating: {selected_agent.name} ({selected_agent.expertise})")
            
            # Agent contributes
            contribution = selected_agent.contribute(self.blackboard)
            contributions.append({
                "iteration": iterations,
                "agent": selected_agent.name,
                "contribution": contribution
            })
            
            print(f"Contribution: {contribution['type']}")
            print(f"Content: {contribution['content'][:100]}...")
            
            # Check if complete
            if self.controller.is_complete(self.blackboard):
                print("✅ Problem solved!")
                break
        
        # Generate final solution
        final_solution = self._synthesize_solution()
        
        return {
            "problem": problem,
            "iterations": iterations,
            "contributions": contributions,
            "blackboard_state": self.blackboard.read(),
            "final_solution": final_solution
        }
    
    def _synthesize_solution(self) -> str:
        """Synthesize final solution from blackboard."""
        findings = self.blackboard.read("findings")
        solutions = self.blackboard.read("partial_solutions")
        
        findings_text = "\n".join([f["finding"] for f in findings])
        solutions_text = "\n".join([s["solution"] for s in solutions])
        
        prompt = f"""
        Based on the collaborative work of multiple agents, synthesize a final solution:
        
        Problem: {self.blackboard.read('problem')}
        
        Research Findings:
        {findings_text}
        
        Partial Solutions:
        {solutions_text}
        
        Provide a comprehensive, final solution that integrates all the work done.
        """
        
        return self.llm.generate(prompt).content

def main():
    print("🖥️ Blackboard Systems Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create blackboard system
    system = BlackboardSystem(llm)
    
    # Test problems (reduced for faster testing)
    problems = [
        "How can a small business improve its online presence?"
    ]
    
    for problem in problems:
        print(f"\n{'='*60}")
        result = system.solve(problem)
        print(f"\n📊 Summary:")
        print(f"  - Iterations: {result['iterations']}")
        print(f"  - Contributions: {len(result['contributions'])}")
        print(f"  - Findings: {len(result['blackboard_state']['findings'])}")
        print(f"  - Solutions: {len(result['blackboard_state']['partial_solutions'])}")
        print(f"\n🎯 Final Solution:")
        print(result['final_solution'][:200] + "...")

if __name__ == "__main__":
    main()
