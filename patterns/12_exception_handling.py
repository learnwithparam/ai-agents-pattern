#!/usr/bin/env python3
"""
12 - Exception Handling & Recovery Pattern
Simple example showing how to handle exceptions and recover gracefully.

This demonstrates:
1. Try primary approach first
2. Handle exceptions gracefully
3. Fallback to alternative approaches
4. Provide meaningful error messages
"""

import sys
import os
import time
import random
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ServiceError(Exception):
    """Custom exception for service errors."""
    pass

class PrimaryService:
    """Simulates a primary service that might fail."""
    
    def __init__(self, success_rate=0.7):
        self.success_rate = success_rate
    
    def get_data(self, query):
        """Get data from primary service."""
        # Simulate random failures
        if random.random() > self.success_rate:
            raise ServiceError(f"Primary service failed for query: {query}")
        
        # Simulate processing time
        time.sleep(0.1)
        return f"Primary service result for: {query}"

class FallbackService:
    """Simulates a fallback service."""
    
    def get_data(self, query):
        """Get data from fallback service."""
        # Simulate processing time
        time.sleep(0.2)
        return f"Fallback service result for: {query}"

class ExceptionHandler:
    """Handles exceptions and provides recovery strategies."""
    
    def __init__(self):
        self.llm = get_llm()
        self.primary_service = PrimaryService()
        self.fallback_service = FallbackService()
        self.retry_count = 0
        self.max_retries = 3
    
    def handle_with_retry(self, operation, *args, **kwargs):
        """Handle operation with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                if attempt > 0:
                    print(f"✅ Success on attempt {attempt + 1}")
                return result
            except Exception as e:
                last_exception = e
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
        
        raise last_exception
    
    def handle_with_fallback(self, primary_operation, fallback_operation, *args, **kwargs):
        """Handle operation with fallback strategy."""
        try:
            print("🔄 Trying primary approach...")
            result = primary_operation(*args, **kwargs)
            print("✅ Primary approach succeeded")
            return result
        except Exception as e:
            print(f"❌ Primary approach failed: {str(e)}")
            print("🔄 Trying fallback approach...")
            try:
                result = fallback_operation(*args, **kwargs)
                print("✅ Fallback approach succeeded")
                return result
            except Exception as fallback_error:
                print(f"❌ Fallback approach also failed: {str(fallback_error)}")
                return self._generate_error_response(str(e), str(fallback_error))
    
    def _generate_error_response(self, primary_error, fallback_error):
        """Generate a helpful error response using LLM."""
        prompt = f"""
        Primary service failed with: {primary_error}
        Fallback service failed with: {fallback_error}
        
        Generate a helpful error message for the user that:
        1. Acknowledges the issue
        2. Explains what went wrong in simple terms
        3. Suggests alternative actions the user can take
        4. Is friendly and professional
        """
        
        return self.llm.generate(prompt).content
    
    def get_data_with_recovery(self, query):
        """Get data with comprehensive error handling."""
        def primary_get():
            return self.primary_service.get_data(query)
        
        def fallback_get():
            return self.fallback_service.get_data(query)
        
        return self.handle_with_fallback(primary_get, fallback_get)
    
    def get_data_with_retry(self, query):
        """Get data with retry logic."""
        def get_operation():
            return self.primary_service.get_data(query)
        
        return self.handle_with_retry(get_operation)

def main():
    print("🛡️ Exception Handling & Recovery Pattern")
    print("=" * 40)
    
    # Initialize exception handler
    handler = ExceptionHandler()
    
    # Test queries
    queries = [
        "Get weather information",
        "Fetch user profile data",
        "Retrieve product information",
        "Load configuration settings"
    ]
    
    print("Testing exception handling with different strategies...")
    
    for i, query in enumerate(queries):
        print(f"\n--- Test {i + 1}: {query} ---")
        
        # Test with fallback strategy
        print(f"\n🔄 Testing fallback strategy:")
        result = handler.get_data_with_recovery(query)
        print(f"Result: {result}")
        
        # Test with retry strategy
        print(f"\n🔄 Testing retry strategy:")
        try:
            result = handler.get_data_with_retry(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"All retries failed: {str(e)}")
        
        print("-" * 40)
    
    # Test error response generation
    print(f"\n--- Testing Error Response Generation ---")
    error_response = handler._generate_error_response(
        "Service temporarily unavailable",
        "Backup service also down"
    )
    print(f"Generated error response: {error_response}")

if __name__ == "__main__":
    main()
