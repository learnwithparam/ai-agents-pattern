#!/usr/bin/env python3
"""
34 - ReAct (Reason + Act) Pattern
Dynamic reasoning and action loop for complex problem-solving.

The ReAct pattern enables agents to interleave reasoning steps with actions in a
continuous loop. Instead of planning all steps upfront, the agent generates a
thought about its immediate next step, takes an action (like calling a tool),
observes the result, and then uses that new information to generate its next
thought and action. This creates a dynamic and adaptive problem-solving process.

This demonstrates:
1. Think-Act-Observe loop for dynamic problem solving
2. Multi-step reasoning with tool integration
3. Adaptive planning based on real-time observations
4. Complex question answering through iterative exploration
"""

import sys
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ReActAgent:
    """ReAct agent that interleaves reasoning and action."""
    
    def __init__(self, llm):
        self.llm = llm
        self.max_iterations = 10
        self.tools = {
            "search": self._search_tool,
            "calculate": self._calculate_tool,
            "get_fact": self._get_fact_tool
        }
    
    def _search_tool(self, query: str) -> str:
        """Mock search tool - in real implementation, use actual search API."""
        mock_results = {
            "apple ceo": "Tim Cook is the CEO of Apple Inc.",
            "iphone manufacturer": "Apple Inc. manufactures the iPhone",
            "tim cook company": "Tim Cook is the CEO of Apple Inc.",
            "python programming": "Python is a high-level programming language",
            "machine learning": "Machine learning is a subset of artificial intelligence"
        }
        query_lower = query.lower()
        for key, value in mock_results.items():
            if key in query_lower:
                return value
        return f"No results found for: {query}"
    
    def _calculate_tool(self, expression: str) -> str:
        """Calculate mathematical expressions safely."""
        try:
            # Only allow safe operations
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_fact_tool(self, topic: str) -> str:
        """Mock fact retrieval tool."""
        facts = {
            "apple": "Apple Inc. is an American multinational technology company",
            "iphone": "iPhone is a line of smartphones designed and marketed by Apple",
            "ceo": "CEO stands for Chief Executive Officer",
            "tim cook": "Tim Cook is the current CEO of Apple Inc."
        }
        topic_lower = topic.lower()
        for key, value in facts.items():
            if key in topic_lower:
                return value
        return f"No facts available for: {topic}"
    
    def _parse_thought(self, response: str) -> Optional[str]:
        """Extract thought from response."""
        if "THOUGHT:" in response:
            return response.split("THOUGHT:")[1].split("ACTION:")[0].strip()
        return None
    
    def _parse_action(self, response: str) -> Optional[tuple]:
        """Extract action from response."""
        if "ACTION:" in response:
            action_line = response.split("ACTION:")[1].split("OBSERVATION:")[0].strip()
            if "(" in action_line and ")" in action_line:
                tool_name = action_line.split("(")[0].strip()
                args_str = action_line.split("(")[1].split(")")[0].strip()
                args = [arg.strip().strip('"\'') for arg in args_str.split(",") if arg.strip()]
                return tool_name, args
        return None, None
    
    def _execute_action(self, tool_name: str, args: List[str]) -> str:
        """Execute the specified tool with arguments."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            return self.tools[tool_name](*args)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def _is_final_answer(self, response: str) -> bool:
        """Check if the response contains a final answer."""
        return "FINAL ANSWER:" in response
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract the final answer from response."""
        if "FINAL ANSWER:" in response:
            return response.split("FINAL ANSWER:")[1].strip()
        return response
    
    def solve(self, question: str) -> Dict[str, Any]:
        """Solve a problem using ReAct pattern."""
        print(f"🤔 Question: {question}")
        print("=" * 50)
        
        # Initialize state
        thoughts = []
        actions = []
        observations = []
        
        # ReAct loop
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Build context
            context = f"Question: {question}\n\n"
            
            if thoughts:
                context += "Previous thoughts and actions:\n"
                for i, (thought, action, obs) in enumerate(zip(thoughts, actions, observations)):
                    context += f"Thought {i+1}: {thought}\n"
                    context += f"Action {i+1}: {action}\n"
                    context += f"Observation {i+1}: {obs}\n\n"
            
            # Generate thought and action
            prompt = f"""
            {context}
            
            You are a helpful assistant solving this question step by step.
            Available tools: search(query), calculate(expression), get_fact(topic)
            
            Think about what you need to do next, then take an action.
            Format your response as:
            THOUGHT: [your reasoning]
            ACTION: tool_name(arg1, arg2)
            
            If you have enough information to answer the question, respond with:
            FINAL ANSWER: [your complete answer]
            """
            
            response = self.llm.generate(prompt).content
            print(f"Response: {response}")
            
            # Check if this is a final answer
            if self._is_final_answer(response):
                final_answer = self._extract_final_answer(response)
                print(f"\n🎯 Final Answer: {final_answer}")
                return {
                    "answer": final_answer,
                    "thoughts": thoughts,
                    "actions": actions,
                    "observations": observations,
                    "iterations": iteration + 1
                }
            
            # Parse thought and action
            thought = self._parse_thought(response)
            action_tool, action_args = self._parse_action(response)
            
            if not thought or not action_tool:
                print("❌ Could not parse thought or action")
                continue
            
            thoughts.append(thought)
            actions.append(f"{action_tool}({', '.join(action_args) if action_args else ''})")
            
            print(f"Thought: {thought}")
            print(f"Action: {action_tool}({', '.join(action_args) if action_args else ''})")
            
            # Execute action
            observation = self._execute_action(action_tool, action_args)
            observations.append(observation)
            
            print(f"Observation: {observation}")
        
        print(f"\n⚠️ Max iterations reached ({self.max_iterations})")
        return {
            "answer": "Could not find a complete answer within the iteration limit",
            "thoughts": thoughts,
            "actions": actions,
            "observations": observations,
            "iterations": self.max_iterations
        }

def main():
    print("🔄 ReAct (Reason + Act) Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create ReAct agent
    agent = ReActAgent(llm)
    
    # Test questions
    questions = [
        "Who is the CEO of the company that makes the iPhone?",
        "What is 15 * 23 + 45?",
        "What is machine learning and who invented it?"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        result = agent.solve(question)
        print(f"\n📊 Summary:")
        print(f"  - Iterations: {result['iterations']}")
        print(f"  - Actions taken: {len(result['actions'])}")
        print(f"  - Answer: {result['answer']}")

if __name__ == "__main__":
    main()
