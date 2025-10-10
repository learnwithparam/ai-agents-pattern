#!/usr/bin/env python3
"""
10 - MCP (Model Context Protocol) Pattern
Simple example showing how to use external tools via MCP.

This demonstrates:
1. Mock MCP server simulation
2. Tool discovery and execution
3. Standardized tool interface
4. LLM integration with external tools

Note: This uses mock MCP servers for simplicity. 
See documentation below for real MCP server setup.
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class MockMCPServer:
    """Mock MCP server for demonstration purposes."""
    
    def __init__(self):
        self.tools = {
            "filesystem_list": {
                "description": "List files and directories in a given path",
                "parameters": {"path": "string (optional, defaults to current directory)"}
            },
            "filesystem_read": {
                "description": "Read the content of a specified file",
                "parameters": {"filepath": "string (required)"}
            },
            "weather_get": {
                "description": "Get current weather information for a city",
                "parameters": {"city": "string (required)"}
            },
            "math_calculate": {
                "description": "Calculate mathematical expressions",
                "parameters": {"expression": "string (required, e.g., '2 + 2')"}
            }
        }
    
    def list_tools(self):
        """Return available tools."""
        return self.tools
    
    def execute_tool(self, tool_name, input_data):
        """Execute a tool with given input."""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        # Mock implementations
        if tool_name == "filesystem_list":
            path = input_data.get("path", ".")
            return {
                "files": ["test.txt", "readme.md", "config.json"],
                "directories": ["src/", "docs/"],
                "path": path
            }
        
        elif tool_name == "filesystem_read":
            filepath = input_data.get("filepath", "")
            return {
                "content": f"Mock content of {filepath}: This is a sample file with some text content.",
                "filepath": filepath,
                "size": 45
            }
        
        elif tool_name == "weather_get":
            city = input_data.get("city", "")
            return {
                "city": city,
                "temperature": "22°C",
                "condition": "Sunny",
                "humidity": "65%",
                "wind": "Light winds"
            }
        
        elif tool_name == "math_calculate":
            expression = input_data.get("expression", "")
            try:
                # Simple eval for demo (not safe for production)
                result = eval(expression)
                return {
                    "expression": expression,
                    "result": result
                }
            except Exception as e:
                return {
                    "expression": expression,
                    "error": f"Invalid expression: {str(e)}"
                }
        
        return {"error": "Tool execution failed"}

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self):
        self.llm = get_llm()
        self.server = MockMCPServer()
        self.available_tools = self.server.list_tools()
    
    def get_tools_description(self):
        """Get formatted description of available tools."""
        description = "Available MCP tools:\n"
        for tool_name, tool_info in self.available_tools.items():
            description += f"- {tool_name}: {tool_info['description']}\n"
            description += f"  Parameters: {tool_info['parameters']}\n"
        return description
    
    def parse_tool_call(self, response):
        """Parse tool call from LLM response."""
        # Look for MCP call pattern: MCP: tool_name(input_data)
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith('MCP:'):
                mcp_call = line.strip()[4:].strip()  # Remove 'MCP:'
                if '(' in mcp_call and ')' in mcp_call:
                    tool_name = mcp_call.split('(')[0].strip()
                    input_str = mcp_call.split('(')[1].split(')')[0].strip()
                    
                    # Parse input data
                    try:
                        # Try to parse as JSON first
                        input_data = json.loads(input_str)
                    except:
                        # If not JSON, treat as simple string parameter
                        input_data = {"input": input_str.strip('"\'')}
                    
                    return tool_name, input_data
        return None, None
    
    def execute_tool(self, tool_name, input_data):
        """Execute a tool on the MCP server."""
        return self.server.execute_tool(tool_name, input_data)
    
    def process_query(self, query):
        """Process a user query using MCP tools."""
        # Create prompt for tool calling
        tools_description = self.get_tools_description()
        
        prompt = f"""
        You have access to these MCP tools:
        {tools_description}
        
        User query: {query}
        
        If you need to use an MCP tool, respond with:
        MCP: tool_name(input_data)
        
        Examples:
        - MCP: filesystem_list({{"path": "."}})
        - MCP: weather_get({{"city": "Paris"}})
        - MCP: math_calculate({{"expression": "2 + 2"}})
        
        If no MCP tool is needed, respond normally.
        """
        
        # Get LLM response
        response = self.llm.generate(prompt).content
        print(f"LLM Response: {response}")
        
        # Check if tool call is needed
        tool_name, input_data = self.parse_tool_call(response)
        
        if tool_name:
            print(f"Executing MCP tool: {tool_name}({input_data})")
            tool_result = self.execute_tool(tool_name, input_data)
            print(f"MCP tool result: {tool_result}")
            
            # Get final response with tool result
            final_prompt = f"""
            User query: {query}
            MCP tool result: {tool_result}
            
            Provide a helpful final response to the user based on the tool result.
            """
            final_response = self.llm.generate(final_prompt).content
            return final_response
        else:
            return response

def main():
    print("🔌 MCP (Model Context Protocol) Pattern")
    print("=" * 50)
    
    # Initialize MCP client
    mcp_client = MCPClient()
    print(f"Using LLM: {mcp_client.llm.provider}")
    print(f"Mode: Mock MCP Server (for simplicity)")
    
    print(f"\nAvailable MCP tools:")
    for tool_name, tool_info in mcp_client.available_tools.items():
        print(f"- {tool_name}: {tool_info['description']}")
    
    # Test queries
    test_queries = [
        "List the files in the current directory",
        "Read the content of test.txt",
        "What's the weather like in Paris?",
        "Calculate 15 * 23 + 45",
        "What is the capital of France?"  # No tool needed
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        result = mcp_client.process_query(query)
        print(f"Final response: {result}")
        print("-" * 50)
    
    print(f"\n--- MCP Pattern Summary ---")
    print(f"✅ Demonstrated MCP tool integration")
    print(f"✅ Showed tool discovery and execution")
    print(f"✅ Used mock server for simplicity")
    print(f"✅ LLM successfully chose appropriate tools")

if __name__ == "__main__":
    main()