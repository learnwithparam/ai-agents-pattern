#!/usr/bin/env python3
"""
38 - Tree of Thoughts (ToT) Pattern
Systematic exploration of multiple reasoning paths to find optimal solutions.

The Tree of Thoughts pattern enables agents to solve complex problems by exploring
multiple reasoning paths in a tree structure, evaluating and pruning branches to
systematically find the optimal solution. This approach is particularly effective
for problems that require systematic exploration, such as logic puzzles, constrained
planning, and multi-step reasoning tasks where the solution path is not immediately obvious.

This demonstrates:
1. Generate multiple thought branches from current state
2. Evaluate each branch using scoring criteria
3. Prune unpromising branches to focus resources
4. Expand promising branches with new thoughts
5. Find optimal solution through systematic search
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

@dataclass
class ThoughtNode:
    """Represents a node in the tree of thoughts."""
    content: str
    parent: Optional['ThoughtNode'] = None
    children: List['ThoughtNode'] = None
    evaluation_score: float = 0.0
    depth: int = 0
    is_terminal: bool = False
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def add_child(self, child: 'ThoughtNode') -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)
    
    def get_path(self) -> List[str]:
        """Get the path from root to this node."""
        path = []
        current = self
        while current:
            path.insert(0, current.content)
            current = current.parent
        return path

class TreeOfThoughts:
    """Tree of Thoughts implementation."""
    
    def __init__(self, llm, max_depth: int = 4, branching_factor: int = 3):
        self.llm = llm
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.root = None
        self.evaluation_criteria = {
            "logic": "Is the reasoning logically sound?",
            "feasibility": "Is this approach feasible?",
            "completeness": "Does this address the problem completely?",
            "creativity": "Is this a creative or novel approach?"
        }
    
    def generate_thoughts(self, problem: str, current_path: List[str], num_thoughts: int = 3) -> List[str]:
        """Generate multiple thought branches from current state."""
        path_context = " -> ".join(current_path) if current_path else "Starting point"
        
        prompt = f"""
        Problem: {problem}
        
        Current reasoning path: {path_context}
        
        Generate {num_thoughts} different next steps or approaches to continue solving this problem.
        Each thought should be:
        1. A specific, actionable step
        2. Logically connected to the current path
        3. Different from the other thoughts
        4. One sentence or short phrase
        
        Format as a JSON array of strings:
        ["thought1", "thought2", "thought3"]
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            thoughts = json.loads(json_str)
            return thoughts[:num_thoughts]  # Limit to requested number
        except json.JSONDecodeError:
            # Fallback: generate simple thoughts
            return [
                f"Approach 1: Continue with current path",
                f"Alternative 2: Try different method",
                f"Backup 3: Reconsider previous step"
            ][:num_thoughts]
    
    def evaluate_thought(self, problem: str, thought_path: List[str]) -> Dict[str, Any]:
        """Evaluate a thought path using multiple criteria."""
        path_text = " -> ".join(thought_path)
        
        prompt = f"""
        Problem: {problem}
        
        Thought path: {path_text}
        
        Evaluate this reasoning path on the following criteria (1-10 scale):
        1. Logic: Is the reasoning logically sound?
        2. Feasibility: Is this approach feasible?
        3. Completeness: Does this address the problem completely?
        4. Creativity: Is this a creative or novel approach?
        
        Also provide:
        - Overall assessment (1-10)
        - Strengths of this approach
        - Weaknesses or concerns
        - Whether this path should be continued or pruned
        
        Respond with JSON:
        {{
            "logic": 8,
            "feasibility": 7,
            "completeness": 6,
            "creativity": 9,
            "overall": 7.5,
            "strengths": "Good logical flow, creative approach",
            "weaknesses": "May be too complex",
            "continue": true
        }}
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            evaluation = json.loads(json_str)
            return evaluation
        except json.JSONDecodeError:
            # Fallback evaluation
            return {
                "logic": 7,
                "feasibility": 7,
                "completeness": 7,
                "creativity": 7,
                "overall": 7.0,
                "strengths": "Reasonable approach",
                "weaknesses": "Standard approach",
                "continue": True
            }
    
    def is_terminal(self, problem: str, thought_path: List[str]) -> bool:
        """Check if a thought path represents a complete solution."""
        path_text = " -> ".join(thought_path)
        
        prompt = f"""
        Problem: {problem}
        
        Thought path: {path_text}
        
        Does this path represent a complete solution to the problem?
        A complete solution should:
        1. Address all aspects of the problem
        2. Provide actionable steps or conclusions
        3. Be implementable or verifiable
        
        Respond with JSON:
        {{
            "is_complete": true/false,
            "reason": "explanation of why it is or isn't complete"
        }}
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            result = json.loads(json_str)
            return result.get("is_complete", False)
        except json.JSONDecodeError:
            # Fallback: consider complete if path is long enough
            return len(thought_path) >= 3
    
    def build_tree(self, problem: str) -> ThoughtNode:
        """Build the tree of thoughts."""
        print(f"🌳 Building Tree of Thoughts for: {problem}")
        print("=" * 50)
        
        # Initialize root
        self.root = ThoughtNode(content="Start solving the problem")
        
        # BFS to build tree
        queue = [self.root]
        level = 0
        
        while queue and level < self.max_depth:
            level += 1
            print(f"\n--- Level {level} ---")
            
            next_queue = []
            
            for node in queue:
                current_path = node.get_path()
                
                # Generate thoughts for this node
                thoughts = self.generate_thoughts(problem, current_path, self.branching_factor)
                print(f"Node: {node.content}")
                print(f"Generated {len(thoughts)} thoughts")
                
                for thought_content in thoughts:
                    child = ThoughtNode(content=thought_content)
                    node.add_child(child)
                    
                    # Evaluate the new path
                    new_path = child.get_path()
                    evaluation = self.evaluate_thought(problem, new_path)
                    child.evaluation_score = evaluation["overall"]
                    
                    # Check if terminal
                    child.is_terminal = self.is_terminal(problem, new_path)
                    
                    print(f"  - {thought_content} (score: {child.evaluation_score:.1f})")
                    
                    # Add to next level if not terminal and score is good
                    if not child.is_terminal and child.evaluation_score >= 6.0:
                        next_queue.append(child)
            
            queue = next_queue
        
        return self.root
    
    def find_best_solution(self, problem: str) -> Dict[str, Any]:
        """Find the best solution by exploring the tree."""
        root = self.build_tree(problem)
        
        # Find all terminal nodes
        terminal_nodes = self._find_terminal_nodes(root)
        
        if not terminal_nodes:
            return {
                "solution": "No complete solutions found",
                "best_path": [],
                "score": 0.0,
                "explanation": "No terminal nodes reached"
            }
        
        # Find best terminal node
        best_node = max(terminal_nodes, key=lambda n: n.evaluation_score)
        best_path = best_node.get_path()
        
        # Generate final solution
        solution = self._generate_final_solution(problem, best_path)
        
        return {
            "solution": solution,
            "best_path": best_path,
            "score": best_node.evaluation_score,
            "explanation": f"Best path found with score {best_node.evaluation_score:.1f}"
        }
    
    def _find_terminal_nodes(self, node: ThoughtNode) -> List[ThoughtNode]:
        """Find all terminal nodes in the tree."""
        terminals = []
        
        if node.is_terminal:
            terminals.append(node)
        
        for child in node.children:
            terminals.extend(self._find_terminal_nodes(child))
        
        return terminals
    
    def _generate_final_solution(self, problem: str, path: List[str]) -> str:
        """Generate final solution from the best path."""
        path_text = " -> ".join(path)
        
        prompt = f"""
        Problem: {problem}
        
        Best reasoning path: {path_text}
        
        Generate a comprehensive final solution based on this reasoning path.
        The solution should be clear, actionable, and directly address the original problem.
        """
        
        return self.llm.generate(prompt).content
    
    def print_tree(self, node: ThoughtNode = None, depth: int = 0) -> None:
        """Print the tree structure."""
        if node is None:
            node = self.root
        
        if node is None:
            return
        
        indent = "  " * depth
        print(f"{indent}{node.content} (score: {node.evaluation_score:.1f})")
        
        for child in node.children:
            self.print_tree(child, depth + 1)

def main():
    print("🌳 Tree of Thoughts (ToT) Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create Tree of Thoughts
    tot = TreeOfThoughts(llm, max_depth=3, branching_factor=2)
    
    # Test problems
    problems = [
        "How can a company reduce its carbon footprint while maintaining profitability?",
        "What are the best strategies for learning a new programming language?",
        "How can a small business compete with larger corporations in the same market?"
    ]
    
    for problem in problems:
        print(f"\n{'='*60}")
        result = tot.find_best_solution(problem)
        
        print(f"\n🎯 Best Solution:")
        print(f"Score: {result['score']:.1f}")
        print(f"Path: {' -> '.join(result['best_path'])}")
        print(f"Solution: {result['solution']}")
        
        print(f"\n📊 Tree Structure:")
        tot.print_tree()

if __name__ == "__main__":
    main()
