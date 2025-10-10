#!/usr/bin/env python3
"""
08 - Memory Management Pattern
Simple example showing how to manage conversation memory and context.

This demonstrates:
1. Store conversation history
2. Retrieve relevant context
3. Manage session state
4. Use memory to improve responses
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ConversationMemory:
    """Simple conversation memory manager."""
    
    def __init__(self):
        self.history = []
        self.user_preferences = {}
        self.session_data = {}
    
    def add_message(self, role, content):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(message)
    
    def get_recent_context(self, limit=5):
        """Get recent conversation context."""
        recent = self.history[-limit:] if len(self.history) > limit else self.history
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])
    
    def get_user_preferences(self):
        """Get stored user preferences."""
        if not self.user_preferences:
            return "No preferences stored yet."
        return "\n".join([f"{key}: {value}" for key, value in self.user_preferences.items()])
    
    def update_preferences(self, key, value):
        """Update user preferences."""
        self.user_preferences[key] = value
    
    def get_session_summary(self):
        """Get session summary."""
        return {
            "total_messages": len(self.history),
            "user_preferences": len(self.user_preferences),
            "session_start": self.history[0]["timestamp"] if self.history else None
        }

def chat_with_memory(memory, user_input, llm):
    """Chat with memory management."""
    # Add user message to memory
    memory.add_message("user", user_input)
    
    # Get context for LLM
    recent_context = memory.get_recent_context()
    user_preferences = memory.get_user_preferences()
    
    # Create prompt with memory context
    prompt = f"""
    You are a helpful assistant with access to conversation history and user preferences.
    
    Recent conversation:
    {recent_context}
    
    User preferences:
    {user_preferences}
    
    Current user message: {user_input}
    
    Respond naturally, and if the user mentions preferences or personal information, 
    acknowledge that you'll remember it for future conversations.
    """
    
    # Get LLM response
    response = llm.generate(prompt).content
    
    # Add assistant response to memory
    memory.add_message("assistant", response)
    
    return response

def extract_preferences(user_input, llm):
    """Extract user preferences from input."""
    prompt = f"""
    Analyze this user input for any preferences or personal information:
    {user_input}
    
    If you find any preferences (like favorite color, programming language, etc.), 
    respond with: PREFERENCE: key=value
    If no preferences found, respond with: NO_PREFERENCES
    """
    
    response = llm.generate(prompt).content
    
    if "PREFERENCE:" in response:
        pref_line = response.split("PREFERENCE:")[1].strip()
        if "=" in pref_line:
            key, value = pref_line.split("=", 1)
            return key.strip(), value.strip()
    
    return None, None

def main():
    print("🧠 Memory Management Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Initialize memory
    memory = ConversationMemory()
    
    # Simulate conversation
    conversation = [
        "Hi! I'm learning Python programming.",
        "What's your favorite programming language?",
        "I prefer Python because it's easy to read.",
        "Can you help me with a Python function?",
        "I like clean, well-documented code.",
        "What's the best way to handle errors in Python?"
    ]
    
    print("Simulating conversation with memory management...")
    
    for i, user_input in enumerate(conversation):
        print(f"\n--- Turn {i + 1} ---")
        print(f"User: {user_input}")
        
        # Extract preferences
        pref_key, pref_value = extract_preferences(user_input, llm)
        if pref_key and pref_value:
            memory.update_preferences(pref_key, pref_value)
            print(f"📝 Stored preference: {pref_key} = {pref_value}")
        
        # Get response with memory
        response = chat_with_memory(memory, user_input, llm)
        print(f"Assistant: {response}")
    
    # Show memory summary
    print(f"\n--- Memory Summary ---")
    summary = memory.get_session_summary()
    print(f"Total messages: {summary['total_messages']}")
    print(f"User preferences: {summary['user_preferences']}")
    print(f"Session start: {summary['session_start']}")
    
    print(f"\nStored preferences:")
    for key, value in memory.user_preferences.items():
        print(f"  {key}: {value}")
    
    print(f"\nRecent context:")
    print(memory.get_recent_context(3))

if __name__ == "__main__":
    main()
