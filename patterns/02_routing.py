#!/usr/bin/env python3
"""
02 - Routing Pattern
Simple example showing how to route requests to different handlers.

This demonstrates:
1. Analyze user request
2. Route to appropriate handler
3. Get specialized response
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

def route_request(request, llm):
    """Decide which handler to use based on the request."""
    prompt = f"""
    Analyze this request and respond with just one word:
    - "book" for travel/hotel/restaurant bookings
    - "info" for general questions
    - "help" for unclear requests
    
    Request: {request}
    """
    
    response = llm.generate(prompt).content.strip().lower()
    
    if "book" in response:
        return "booking"
    elif "info" in response:
        return "information"
    else:
        return "help"

def handle_booking(request, llm):
    """Handle booking requests."""
    prompt = f"You are a booking assistant. Help with: {request}"
    return llm.generate(prompt).content

def handle_info(request, llm):
    """Handle information requests."""
    prompt = f"You are a helpful assistant. Answer: {request}"
    return llm.generate(prompt).content

def handle_help(request, llm):
    """Handle unclear requests."""
    return f"I'm not sure how to help with '{request}'. Can you be more specific?"

def main():
    print("🛣️ Routing Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Test requests
    requests = [
        "Book me a hotel in Paris",
        "What's the capital of France?",
        "Help me with something"
    ]
    
    for request in requests:
        print(f"\nRequest: {request}")
        
        # Route the request
        handler = route_request(request, llm)
        print(f"→ Routing to: {handler}")
        
        # Handle the request
        if handler == "booking":
            response = handle_booking(request, llm)
        elif handler == "information":
            response = handle_info(request, llm)
        else:
            response = handle_help(request, llm)
        
        print(f"Response: {response}")

if __name__ == "__main__":
    main()
