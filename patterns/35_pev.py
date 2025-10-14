#!/usr/bin/env python3
"""
35 - PEV (Plan-Execute-Verify) Pattern
Robust three-stage workflow with verification and error recovery.

The PEV pattern introduces a critical layer of robustness and self-correction into
agentic systems. It separates planning, execution, and verification into distinct
phases, ensuring that the output of each step is validated before the agent proceeds.
This creates a robust, self-correcting loop that can detect failures and dynamically
recover, making it ideal for safety-critical applications and systems with unreliable tools.

This demonstrates:
1. Planning phase - decompose goal into executable steps
2. Execution phase - execute individual steps with tools
3. Verification phase - validate results and handle failures
4. Dynamic re-planning on failures with context
5. Robust error handling and recovery mechanisms
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class PEVAgent:
    """PEV agent with planning, execution, and verification phases."""
    
    def __init__(self, llm):
        self.llm = llm
        self.max_retries = 3
        self.tools = {
            "search": self._search_tool,
            "calculate": self._calculate_tool,
            "get_weather": self._weather_tool,
            "get_stock_price": self._stock_tool
        }
    
    def _search_tool(self, query: str) -> Dict[str, Any]:
        """Mock search tool with occasional failures."""
        # Simulate 20% failure rate
        if random.random() < 0.2:
            return {"error": "Search service temporarily unavailable", "success": False}
        
        mock_results = {
            "apple ceo": {"result": "Tim Cook is the CEO of Apple Inc.", "success": True},
            "python programming": {"result": "Python is a high-level programming language", "success": True},
            "machine learning": {"result": "Machine learning is a subset of AI", "success": True}
        }
        
        query_lower = query.lower()
        for key, value in mock_results.items():
            if key in query_lower:
                return value
        
        return {"result": f"No results found for: {query}", "success": True}
    
    def _calculate_tool(self, expression: str) -> Dict[str, Any]:
        """Calculate mathematical expressions with error handling."""
        try:
            # Only allow safe operations
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "sqrt": lambda x: x ** 0.5
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {"result": f"Result: {result}", "success": True}
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}", "success": False}
    
    def _weather_tool(self, city: str) -> Dict[str, Any]:
        """Mock weather tool with occasional failures."""
        # Simulate 15% failure rate
        if random.random() < 0.15:
            return {"error": "Weather service unavailable", "success": False}
        
        weather_data = {
            "paris": "Sunny, 22°C",
            "london": "Cloudy, 18°C",
            "tokyo": "Rainy, 25°C",
            "new york": "Partly cloudy, 20°C"
        }
        
        city_lower = city.lower()
        if city_lower in weather_data:
            return {"result": f"Weather in {city}: {weather_data[city_lower]}", "success": True}
        else:
            return {"result": f"Weather data not available for {city}", "success": True}
    
    def _stock_tool(self, symbol: str) -> Dict[str, Any]:
        """Mock stock price tool with occasional failures."""
        # Simulate 25% failure rate
        if random.random() < 0.25:
            return {"error": "Stock service temporarily down", "success": False}
        
        stock_prices = {
            "AAPL": "$150.25",
            "GOOGL": "$2800.50",
            "MSFT": "$350.75",
            "TSLA": "$200.30"
        }
        
        symbol_upper = symbol.upper()
        if symbol_upper in stock_prices:
            return {"result": f"{symbol_upper} stock price: {stock_prices[symbol_upper]}", "success": True}
        else:
            return {"result": f"Stock symbol {symbol} not found", "success": True}
    
    def plan(self, goal: str) -> List[Dict[str, str]]:
        """Create a plan to achieve the goal."""
        prompt = f"""
        Create a detailed plan to achieve this goal: {goal}
        
        Break it down into specific, executable steps. Each step should:
        1. Be clear and actionable
        2. Specify which tool to use
        3. Include the exact parameters needed
        
        Available tools:
        - search(query): Search for information
        - calculate(expression): Perform calculations
        - get_weather(city): Get weather information
        - get_stock_price(symbol): Get stock price
        
        Format as JSON array of objects with:
        - step: description of the step
        - tool: tool name to use
        - parameters: list of parameters for the tool
        
        Example:
        [
            {{"step": "Search for information about X", "tool": "search", "parameters": ["X information"]}},
            {{"step": "Calculate the result", "tool": "calculate", "parameters": ["15 * 2 + 10"]}}
        ]
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            plan = json.loads(json_str)
            return plan
        except json.JSONDecodeError:
            # Fallback: create a simple plan
            return [
                {"step": f"Search for information about: {goal}", "tool": "search", "parameters": [goal]},
                {"step": "Analyze the results", "tool": "search", "parameters": [f"analysis of {goal}"]}
            ]
    
    def execute_step(self, step: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single step from the plan."""
        tool_name = step["tool"]
        parameters = step["parameters"]
        
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found", "success": False}
        
        try:
            result = self.tools[tool_name](*parameters)
            return result
        except Exception as e:
            return {"error": f"Execution error: {str(e)}", "success": False}
    
    def verify_step(self, step: Dict[str, str], result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if a step was executed successfully."""
        prompt = f"""
        Verify if this step was executed successfully:
        
        Step: {step['step']}
        Tool: {step['tool']}
        Parameters: {step['parameters']}
        Result: {json.dumps(result, indent=2)}
        
        Check for:
        1. Was the tool executed without errors?
        2. Does the result contain useful information?
        3. Is the result relevant to the step's goal?
        4. Are there any obvious issues or failures?
        
        Respond with JSON:
        {{
            "success": true/false,
            "reason": "explanation of verification result",
            "suggestion": "what to do next if failed"
        }}
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            verification = json.loads(json_str)
            return verification
        except json.JSONDecodeError:
            # Fallback verification
            success = result.get("success", False) and "error" not in result
            return {
                "success": success,
                "reason": "Basic verification based on result success flag",
                "suggestion": "Retry with different parameters" if not success else "Continue to next step"
            }
    
    def synthesize_results(self, goal: str, results: List[Dict[str, Any]]) -> str:
        """Synthesize all results into a final answer."""
        prompt = f"""
        Goal: {goal}
        
        Execution Results:
        {json.dumps(results, indent=2)}
        
        Synthesize all the results into a comprehensive answer to the original goal.
        Include relevant information from successful steps and note any failures.
        """
        
        return self.llm.generate(prompt).content
    
    def solve(self, goal: str) -> Dict[str, Any]:
        """Solve a problem using PEV pattern."""
        print(f"🎯 Goal: {goal}")
        print("=" * 50)
        
        # Phase 1: Plan
        print("\n📋 Phase 1: Planning")
        print("-" * 20)
        plan = self.plan(goal)
        print(f"Created plan with {len(plan)} steps:")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step['step']} (using {step['tool']})")
        
        # Phase 2: Execute and Verify
        print(f"\n⚡ Phase 2: Execute & Verify")
        print("-" * 30)
        
        results = []
        current_plan = plan.copy()
        retry_count = 0
        
        while current_plan and retry_count < self.max_retries:
            step = current_plan.pop(0)
            print(f"\nExecuting: {step['step']}")
            
            # Execute step
            result = self.execute_step(step)
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Verify step
            verification = self.verify_step(step, result)
            print(f"Verification: {verification.get('reason', 'Verification completed')}")
            
            if verification["success"]:
                results.append({
                    "step": step,
                    "result": result,
                    "verification": verification,
                    "status": "success"
                })
                retry_count = 0  # Reset retry count on success
            else:
                print(f"❌ Step failed: {verification['reason']}")
                print(f"💡 Suggestion: {verification['suggestion']}")
                
                # Add failed step back to plan for retry
                current_plan.insert(0, step)
                retry_count += 1
                
                if retry_count >= self.max_retries:
                    print(f"⚠️ Max retries reached for step: {step['step']}")
                    results.append({
                        "step": step,
                        "result": result,
                        "verification": verification,
                        "status": "failed"
                    })
                    break
        
        # Phase 3: Synthesize
        print(f"\n📝 Phase 3: Synthesis")
        print("-" * 20)
        final_answer = self.synthesize_results(goal, results)
        print(f"Final Answer: {final_answer}")
        
        return {
            "goal": goal,
            "plan": plan,
            "results": results,
            "final_answer": final_answer,
            "success_rate": len([r for r in results if r["status"] == "success"]) / len(results) if results else 0
        }

def main():
    print("🔄 PEV (Plan-Execute-Verify) Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create PEV agent
    agent = PEVAgent(llm)
    
    # Test goals
    goals = [
        "Find the current weather in Paris and calculate what 15% of 200 is",
        "Search for information about Apple's CEO and get the current stock price of AAPL",
        "What is machine learning and calculate the square root of 144"
    ]
    
    for goal in goals:
        print(f"\n{'='*60}")
        result = agent.solve(goal)
        print(f"\n📊 Summary:")
        print(f"  - Steps planned: {len(result['plan'])}")
        print(f"  - Steps executed: {len(result['results'])}")
        print(f"  - Success rate: {result['success_rate']:.1%}")
        print(f"  - Final answer: {result['final_answer'][:100]}...")

if __name__ == "__main__":
    main()
