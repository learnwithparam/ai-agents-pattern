#!/usr/bin/env python3
"""
05 - Tool Calling Pattern
Simple example showing how to use tools with LLMs.

This demonstrates:
1. Define available tools
2. Let LLM choose which tool to use
3. Execute the tool and get results
4. Use results in the final response
"""

import sys
import os
import math
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

# Available tools
def calculator(expression):
    """Calculate mathematical expressions safely."""
    try:
        # Only allow safe operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_time():
    """Get the current date and time."""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def get_weather(city):
    """Get weather information for a city (mock function)."""
    # This is a mock function - in real implementation, you'd call a weather API
    weather_data = {
        "paris": "Sunny, 22°C",
        "london": "Cloudy, 18°C", 
        "tokyo": "Rainy, 25°C",
        "new york": "Partly cloudy, 20°C"
    }
    city_lower = city.lower()
    if city_lower in weather_data:
        return f"Weather in {city}: {weather_data[city_lower]}"
    else:
        return f"Weather data not available for {city}"

# Tool registry
TOOLS = {
    "calculator": {
        "description": "Calculate mathematical expressions",
        "function": calculator,
        "parameters": ["expression"]
    },
    "get_current_time": {
        "description": "Get current date and time",
        "function": get_current_time,
        "parameters": []
    },
    "get_weather": {
        "description": "Get weather information for a city",
        "function": get_weather,
        "parameters": ["city"]
    }
}

def get_tool_description():
    """Get description of all available tools."""
    descriptions = []
    for name, tool in TOOLS.items():
        params = ", ".join(tool["parameters"])
        descriptions.append(f"- {name}({params}): {tool['description']}")
    return "\n".join(descriptions)

def parse_tool_call(response):
    """Parse tool call from LLM response."""
    # Look for tool call pattern: TOOL: tool_name(arg1, arg2)
    lines = response.split('\n')
    for line in lines:
        if line.strip().startswith('TOOL:'):
            tool_call = line.strip()[5:].strip()  # Remove 'TOOL:'
            if '(' in tool_call and ')' in tool_call:
                tool_name = tool_call.split('(')[0].strip()
                args_str = tool_call.split('(')[1].split(')')[0].strip()
                args = [arg.strip().strip('"\'') for arg in args_str.split(',')] if args_str else []
                return tool_name, args
    return None, None

def execute_tool(tool_name, args):
    """Execute a tool with given arguments."""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found"
    
    tool = TOOLS[tool_name]
    try:
        if tool_name == "calculator":
            return tool["function"](args[0] if args else "")
        elif tool_name == "get_current_time":
            return tool["function"]()
        elif tool_name == "get_weather":
            return tool["function"](args[0] if args else "")
        else:
            return f"Error: Tool '{tool_name}' not implemented"
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

def main():
    print("🔧 Tool Calling Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Available tools
    print(f"\nAvailable tools:")
    print(get_tool_description())
    
    # Test queries
    queries = [
        "What's 15 * 23 + 45?",
        "What time is it now?",
        "What's the weather like in Paris?",
        "Calculate the square root of 144"
    ]
    
    for query in queries:
        print(f"\n--- Query: {query} ---")
        
        # Create prompt for tool calling
        prompt = f"""
        You have access to these tools:
        {get_tool_description()}
        
        User query: {query}
        
        If you need to use a tool, respond with:
        TOOL: tool_name(arg1, arg2)
        
        If no tool is needed, respond normally.
        """
        
        # Get LLM response
        response = llm.generate(prompt).content
        print(f"LLM Response: {response}")
        
        # Check if tool call is needed
        tool_name, args = parse_tool_call(response)
        
        if tool_name:
            print(f"Executing tool: {tool_name}({', '.join(args) if args else ''})")
            tool_result = execute_tool(tool_name, args)
            print(f"Tool result: {tool_result}")
            
            # Get final response with tool result
            final_prompt = f"""
            User query: {query}
            Tool result: {tool_result}
            
            Provide a helpful final response to the user.
            """
            final_response = llm.generate(final_prompt).content
            print(f"Final response: {final_response}")
        else:
            print("No tool call needed")

if __name__ == "__main__":
    main()
