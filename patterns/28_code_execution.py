#!/usr/bin/env python3
"""
28 - Code Execution Pattern
Simple example showing how to safely execute code with AI agents.

This demonstrates:
1. Safe code execution environments
2. Code validation and sanitization
3. Dynamic code generation and execution
4. Error handling in code execution
"""

import sys
import os
import subprocess
import tempfile
import ast
from typing import Dict, Any
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class CodeExecutor:
    """A safe code execution environment for AI agents."""
    
    def __init__(self):
        self.llm = get_llm()
        self.allowed_modules = {
            'math', 'random', 'datetime', 'json', 'csv', 
            'os', 'sys', 're', 'collections', 'itertools'
        }
        self.execution_history = []
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """Validate code for safety and syntax."""
        try:
            # Parse the code to check syntax
            ast.parse(code)
            
            # Check for potentially dangerous operations
            dangerous_patterns = [
                'import subprocess',
                'import os.system',
                'exec(',
                'eval(',
                '__import__',
                'open(',
                'file(',
                'input(',
                'raw_input('
            ]
            
            for pattern in dangerous_patterns:
                if pattern in code:
                    return {
                        "valid": False,
                        "error": f"Potentially dangerous operation detected: {pattern}",
                        "safe": False
                    }
            
            return {
                "valid": True,
                "error": None,
                "safe": True
            }
            
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {e}",
                "safe": False
            }
    
    def execute_python_code(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code safely."""
        validation = self.validate_code(code)
        
        if not validation["valid"]:
            return {
                "success": False,
                "output": "",
                "error": validation["error"],
                "execution_time": 0
            }
        
        # Create a temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            import time
            start_time = time.time()
            
            # Execute the code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "execution_time": execution_time
            }
            
        except subprocess.TimeoutExpired:
            os.unlink(temp_file)
            return {
                "success": False,
                "output": "",
                "error": f"Code execution timed out after {timeout} seconds",
                "execution_time": timeout
            }
        except Exception as e:
            os.unlink(temp_file)
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {e}",
                "execution_time": 0
            }
    
    def generate_and_execute(self, task: str) -> Dict[str, Any]:
        """Generate code for a task and execute it."""
        print(f"🎯 Task: {task}")
        
        # Generate code using LLM
        prompt = f"""
        Write Python code to solve this task: {task}
        
        Requirements:
        - Use only safe, standard library modules
        - Include proper error handling
        - Make the code clear and well-commented
        - Return the result in a clear format
        
        Respond with only the Python code, no explanations.
        """
        
        generated_code = self.llm.generate(prompt).content
        
        # Clean up the code (remove markdown formatting if present)
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0]
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0]
        
        print(f"📝 Generated code:\n{generated_code}")
        
        # Execute the code
        result = self.execute_python_code(generated_code)
        
        # Store in history
        self.execution_history.append({
            "task": task,
            "code": generated_code,
            "result": result,
            "timestamp": self._get_timestamp()
        })
        
        return result
    
    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

class CodeAnalysisAgent:
    """An AI agent that can analyze and execute code."""
    
    def __init__(self):
        self.llm = get_llm()
        self.executor = CodeExecutor()
    
    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality using AI."""
        prompt = f"""
        Analyze this Python code for quality, style, and potential issues:
        
        ```python
        {code}
        ```
        
        Provide analysis in this format:
        QUALITY_SCORE: [1-10]
        ISSUES: [list any issues found]
        SUGGESTIONS: [list improvement suggestions]
        """
        
        analysis = self.llm.generate(prompt).content
        
        return {
            "code": code,
            "analysis": analysis,
            "timestamp": self._get_timestamp()
        }
    
    def debug_code(self, code: str, error: str) -> Dict[str, Any]:
        """Debug code using AI analysis."""
        prompt = f"""
        Debug this Python code that has an error:
        
        Code:
        ```python
        {code}
        ```
        
        Error:
        {error}
        
        Provide:
        1. The cause of the error
        2. The corrected code
        3. Explanation of the fix
        """
        
        debug_result = self.llm.generate(prompt).content
        
        return {
            "original_code": code,
            "error": error,
            "debug_result": debug_result,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    print("💻 Code Execution Pattern")
    print("=" * 50)
    
    # Test code execution
    print(f"\n--- Code Execution Tests ---")
    executor = CodeExecutor()
    
    test_tasks = [
        "Calculate the factorial of 5",
        "Generate a list of prime numbers up to 20",
        "Create a simple calculator that adds two numbers",
        "Sort a list of names alphabetically"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {task}")
        print(f"{'='*60}")
        
        result = executor.generate_and_execute(task)
        
        if result["success"]:
            print(f"✅ Execution successful!")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            print(f"📤 Output:\n{result['output']}")
        else:
            print(f"❌ Execution failed!")
            print(f"🚨 Error: {result['error']}")
    
    # Test code analysis
    print(f"\n--- Code Analysis Tests ---")
    analyzer = CodeAnalysisAgent()
    
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
    
    print(f"📊 Analyzing code quality...")
    analysis = analyzer.analyze_code_quality(sample_code)
    print(f"Analysis result:\n{analysis['analysis']}")
    
    # Test code debugging
    print(f"\n--- Code Debugging Tests ---")
    
    buggy_code = """
def divide_numbers(a, b):
    result = a / b
    return result

# This will cause an error
print(divide_numbers(10, 0))
"""
    
    print(f"🐛 Debugging buggy code...")
    debug_result = analyzer.debug_code(buggy_code, "ZeroDivisionError: division by zero")
    print(f"Debug result:\n{debug_result['debug_result']}")
    
    # Show execution history
    print(f"\n--- Execution History ---")
    for i, entry in enumerate(executor.execution_history, 1):
        status = "✅" if entry["result"]["success"] else "❌"
        print(f"{i}. {status} {entry['task'][:40]}... at {entry['timestamp']}")
    
    print(f"\n--- Code Execution Pattern Summary ---")
    print(f"✅ Demonstrated safe code execution environments")
    print(f"✅ Showed code validation and sanitization")
    print(f"✅ Implemented dynamic code generation and execution")
    print(f"✅ Created error handling in code execution")

if __name__ == "__main__":
    main()
