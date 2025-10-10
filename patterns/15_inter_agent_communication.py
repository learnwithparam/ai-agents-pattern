#!/usr/bin/env python3
"""
15 - Inter-Agent Communication Pattern
Simple example showing how agents communicate with each other.

This demonstrates:
1. Define specialized agents
2. Enable communication between agents
3. Coordinate multi-agent workflows
4. Handle agent-to-agent messaging
"""

import sys
import os
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class Message:
    """Represents a message between agents."""
    
    def __init__(self, sender, recipient, content, message_type="request"):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.message_type = message_type
        self.timestamp = time.time()
        self.id = f"{sender}_{recipient}_{int(self.timestamp)}"
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "type": self.message_type,
            "timestamp": self.timestamp
        }

class Agent:
    """Base agent class with communication capabilities."""
    
    def __init__(self, name, role, expertise):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.llm = get_llm()
        self.message_queue = []
        self.communication_log = []
    
    def send_message(self, recipient, content, message_type="request"):
        """Send a message to another agent."""
        message = Message(self.name, recipient, content, message_type)
        return message
    
    def receive_message(self, message):
        """Receive a message from another agent."""
        self.message_queue.append(message)
        self.communication_log.append(message)
        print(f"📨 {self.name} received message from {message.sender}: {message.content[:50]}...")
    
    def process_messages(self):
        """Process pending messages."""
        responses = []
        for message in self.message_queue:
            response = self._handle_message(message)
            if response:
                responses.append(response)
        self.message_queue.clear()
        return responses
    
    def _handle_message(self, message):
        """Handle a received message."""
        prompt = f"""
        You are {self.name}, a {self.role} with expertise in {self.expertise}.
        
        You received this message from {message.sender}:
        {message.content}
        
        Respond appropriately to this message. If you need to ask for more information or delegate to another agent, mention it.
        """
        
        response_content = self.llm.generate(prompt).content
        
        # Create response message
        response = Message(
            self.name, 
            message.sender, 
            response_content, 
            "response"
        )
        
        return response
    
    def work_on_task(self, task, context=""):
        """Work on a task independently."""
        prompt = f"""
        You are {self.name}, a {self.role} with expertise in {self.expertise}.
        
        Task: {task}
        Context: {context}
        
        Provide your specialized input for this task.
        """
        
        return self.llm.generate(prompt).content

class CommunicationHub:
    """Manages communication between agents."""
    
    def __init__(self):
        self.agents = {}
        self.message_history = []
    
    def register_agent(self, agent):
        """Register an agent with the hub."""
        self.agents[agent.name] = agent
        print(f"✅ Registered agent: {agent.name} ({agent.role})")
    
    def send_message(self, sender, recipient, content, message_type="request"):
        """Send a message between agents."""
        if sender not in self.agents:
            print(f"❌ Sender agent '{sender}' not found")
            return None
        
        if recipient not in self.agents:
            print(f"❌ Recipient agent '{recipient}' not found")
            return None
        
        message = self.agents[sender].send_message(recipient, content, message_type)
        self.agents[recipient].receive_message(message)
        self.message_history.append(message)
        
        print(f"📤 {sender} → {recipient}: {content[:50]}...")
        return message
    
    def broadcast_message(self, sender, content, exclude_sender=True):
        """Broadcast a message to all agents."""
        recipients = [name for name in self.agents.keys() if not exclude_sender or name != sender]
        
        for recipient in recipients:
            self.send_message(sender, recipient, content)
    
    def process_all_messages(self):
        """Process messages for all agents."""
        all_responses = []
        for agent in self.agents.values():
            responses = agent.process_messages()
            all_responses.extend(responses)
        
        # Send responses
        for response in all_responses:
            if response.recipient in self.agents:
                self.agents[response.recipient].receive_message(response)
                self.message_history.append(response)
        
        return all_responses
    
    def get_communication_log(self):
        """Get communication history."""
        return self.message_history
    
    def get_agent_status(self):
        """Get status of all agents."""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "role": agent.role,
                "expertise": agent.expertise,
                "pending_messages": len(agent.message_queue),
                "total_messages": len(agent.communication_log)
            }
        return status

def main():
    print("🤝 Inter-Agent Communication Pattern")
    print("=" * 40)
    
    # Initialize communication hub
    hub = CommunicationHub()
    
    # Create specialized agents
    agents = [
        Agent("Researcher", "Research Specialist", "gathering and analyzing information"),
        Agent("Analyst", "Data Analyst", "analyzing data and identifying patterns"),
        Agent("Writer", "Technical Writer", "creating clear, engaging content"),
        Agent("Reviewer", "Quality Reviewer", "ensuring accuracy and completeness")
    ]
    
    # Register agents
    for agent in agents:
        hub.register_agent(agent)
    
    print(f"\n--- Agent Communication Test ---")
    
    # Test 1: Direct communication
    print(f"\n🔄 Test 1: Direct Communication")
    hub.send_message(
        "Researcher", 
        "Analyst", 
        "I found some interesting data about AI trends. Can you analyze the patterns?"
    )
    
    # Process messages
    responses = hub.process_all_messages()
    print(f"Generated {len(responses)} responses")
    
    # Test 2: Broadcast communication
    print(f"\n🔄 Test 2: Broadcast Communication")
    hub.broadcast_message(
        "Writer",
        "I need input from everyone for a comprehensive report on AI agent patterns."
    )
    
    # Process messages
    responses = hub.process_all_messages()
    print(f"Generated {len(responses)} responses")
    
    # Test 3: Multi-step communication
    print(f"\n🔄 Test 3: Multi-step Communication")
    
    # Step 1: Researcher asks Analyst
    hub.send_message("Researcher", "Analyst", "What data do you need for the analysis?")
    
    # Step 2: Analyst responds and asks Writer
    hub.process_all_messages()
    hub.send_message("Analyst", "Writer", "I need the data formatted in a specific way. Can you help?")
    
    # Step 3: Writer responds and asks Reviewer
    hub.process_all_messages()
    hub.send_message("Writer", "Reviewer", "Can you review the formatted data for accuracy?")
    
    # Process final messages
    hub.process_all_messages()
    
    # Show communication statistics
    print(f"\n--- Communication Statistics ---")
    status = hub.get_agent_status()
    for name, info in status.items():
        print(f"{name}: {info['total_messages']} messages, {info['pending_messages']} pending")
    
    # Show recent communication
    print(f"\n--- Recent Communication ---")
    recent_messages = hub.get_communication_log()[-5:]  # Last 5 messages
    for msg in recent_messages:
        print(f"{msg.sender} → {msg.recipient}: {msg.content[:50]}...")

if __name__ == "__main__":
    main()
