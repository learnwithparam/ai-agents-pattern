#!/usr/bin/env python3
"""
26 - State Machines Pattern
Simple example showing how to implement state machines for AI agents.

This demonstrates:
1. Finite state machine implementation
2. State transitions and conditions
3. Event-driven agent behavior
4. Hierarchical state management
"""

import sys
import os
from enum import Enum
from typing import Dict, Any
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class AgentState(Enum):
    """Defines possible states for an AI agent."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    SLEEPING = "sleeping"

class Event(Enum):
    """Defines possible events that can trigger state transitions."""
    USER_INPUT = "user_input"
    PROCESSING_COMPLETE = "processing_complete"
    ERROR_OCCURRED = "error_occurred"
    TIMEOUT = "timeout"
    SLEEP_COMMAND = "sleep_command"
    WAKE_COMMAND = "wake_command"
    RESET_COMMAND = "reset_command"

class StateMachine:
    """A finite state machine for AI agent behavior."""
    
    def __init__(self, initial_state: AgentState):
        self.current_state = initial_state
        self.previous_state = None
        self.transitions = {}
        self.state_actions = {}
        self.llm = get_llm()
        self.context = {}
        self.history = []
        
        # Setup default transitions
        self._setup_transitions()
        self._setup_state_actions()
    
    def _setup_transitions(self):
        """Setup state transition rules."""
        self.transitions = {
            (AgentState.IDLE, Event.USER_INPUT): AgentState.LISTENING,
            (AgentState.LISTENING, Event.PROCESSING_COMPLETE): AgentState.PROCESSING,
            (AgentState.PROCESSING, Event.PROCESSING_COMPLETE): AgentState.RESPONDING,
            (AgentState.RESPONDING, Event.PROCESSING_COMPLETE): AgentState.IDLE,
            (AgentState.ERROR, Event.RESET_COMMAND): AgentState.IDLE,
            (AgentState.IDLE, Event.SLEEP_COMMAND): AgentState.SLEEPING,
            (AgentState.SLEEPING, Event.WAKE_COMMAND): AgentState.IDLE,
            (AgentState.LISTENING, Event.ERROR_OCCURRED): AgentState.ERROR,
            (AgentState.PROCESSING, Event.ERROR_OCCURRED): AgentState.ERROR,
            (AgentState.RESPONDING, Event.ERROR_OCCURRED): AgentState.ERROR,
            (AgentState.LISTENING, Event.TIMEOUT): AgentState.IDLE,
            (AgentState.PROCESSING, Event.TIMEOUT): AgentState.ERROR,
        }
    
    def _setup_state_actions(self):
        """Setup actions to perform in each state."""
        self.state_actions = {
            AgentState.IDLE: self._idle_action,
            AgentState.LISTENING: self._listening_action,
            AgentState.PROCESSING: self._processing_action,
            AgentState.RESPONDING: self._responding_action,
            AgentState.ERROR: self._error_action,
            AgentState.SLEEPING: self._sleeping_action,
        }
    
    def transition(self, event: Event, data: Dict[str, Any] = None) -> bool:
        """Attempt to transition to a new state based on an event."""
        if data is None:
            data = {}
        
        # Check if transition is valid
        transition_key = (self.current_state, event)
        if transition_key not in self.transitions:
            print(f"❌ Invalid transition: {self.current_state.value} + {event.value}")
            return False
        
        # Record the transition
        self.previous_state = self.current_state
        new_state = self.transitions[transition_key]
        
        print(f"🔄 Transition: {self.current_state.value} → {new_state.value} (event: {event.value})")
        
        # Update state
        self.current_state = new_state
        
        # Record in history
        self.history.append({
            "from": self.previous_state.value,
            "to": new_state.value,
            "event": event.value,
            "data": data,
            "timestamp": self._get_timestamp()
        })
        
        # Execute state action
        self._execute_state_action(data)
        
        return True
    
    def _execute_state_action(self, data: Dict[str, Any]):
        """Execute the action for the current state."""
        action = self.state_actions.get(self.current_state)
        if action:
            try:
                action(data)
            except Exception as e:
                print(f"❌ Error in state action: {e}")
                self.transition(Event.ERROR_OCCURRED, {"error": str(e)})
    
    def _idle_action(self, data: Dict[str, Any]):
        """Action to perform when in IDLE state."""
        print("😴 Agent is idle, waiting for input...")
        self.context["last_action"] = "idle"
    
    def _listening_action(self, data: Dict[str, Any]):
        """Action to perform when in LISTENING state."""
        user_input = data.get("input", "")
        print(f"👂 Agent is listening: '{user_input}'")
        self.context["user_input"] = user_input
        self.context["last_action"] = "listening"
        
        # Simulate processing completion
        self.transition(Event.PROCESSING_COMPLETE, data)
    
    def _processing_action(self, data: Dict[str, Any]):
        """Action to perform when in PROCESSING state."""
        user_input = self.context.get("user_input", "")
        print(f"🧠 Agent is processing: '{user_input}'")
        
        try:
            # Use LLM to process the input
            prompt = f"""
            Process this user input and provide a helpful response:
            "{user_input}"
            
            Be concise and helpful.
            """
            
            response = self.llm.generate(prompt).content
            self.context["llm_response"] = response
            self.context["last_action"] = "processing"
            
            print(f"💭 Processing complete: {response[:50]}...")
            
            # Transition to responding
            self.transition(Event.PROCESSING_COMPLETE, {"response": response})
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            self.transition(Event.ERROR_OCCURRED, {"error": str(e)})
    
    def _responding_action(self, data: Dict[str, Any]):
        """Action to perform when in RESPONDING state."""
        response = data.get("response", self.context.get("llm_response", ""))
        print(f"💬 Agent is responding: '{response}'")
        self.context["final_response"] = response
        self.context["last_action"] = "responding"
        
        # Simulate response completion
        self.transition(Event.PROCESSING_COMPLETE, {"completed": True})
    
    def _error_action(self, data: Dict[str, Any]):
        """Action to perform when in ERROR state."""
        error = data.get("error", "Unknown error")
        print(f"❌ Agent encountered error: {error}")
        self.context["error"] = error
        self.context["last_action"] = "error"
    
    def _sleeping_action(self, data: Dict[str, Any]):
        """Action to perform when in SLEEPING state."""
        print("😴 Agent is sleeping...")
        self.context["last_action"] = "sleeping"
    
    def _get_timestamp(self):
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def get_state_info(self):
        """Get current state information."""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "context": self.context,
            "history_count": len(self.history)
        }
    
    def get_history(self):
        """Get state transition history."""
        return self.history

class HierarchicalStateMachine:
    """A hierarchical state machine with parent-child relationships."""
    
    def __init__(self):
        self.llm = get_llm()
        self.parent_states = {
            "ACTIVE": ["WORKING", "RESTING"],
            "INACTIVE": ["SLEEPING", "MAINTENANCE"]
        }
        self.current_parent = "ACTIVE"
        self.current_child = "WORKING"
        self.context = {}
    
    def transition_parent(self, new_parent: str):
        """Transition to a new parent state."""
        if new_parent in self.parent_states:
            print(f"🔄 Parent transition: {self.current_parent} → {new_parent}")
            self.current_parent = new_parent
            # Reset to first child state
            self.current_child = self.parent_states[new_parent][0]
            return True
        return False
    
    def transition_child(self, new_child: str):
        """Transition to a new child state within current parent."""
        if new_child in self.parent_states[self.current_parent]:
            print(f"🔄 Child transition: {self.current_child} → {new_child}")
            self.current_child = new_child
            return True
        return False
    
    def get_current_state(self):
        """Get current hierarchical state."""
        return f"{self.current_parent}.{self.current_child}"
    
    def process_event(self, event: str, data: Dict[str, Any] = None):
        """Process an event in the hierarchical state machine."""
        if data is None:
            data = {}
        
        current_state = self.get_current_state()
        print(f"📡 Processing event '{event}' in state '{current_state}'")
        
        # Simple event processing logic
        if event == "work_request" and self.current_parent == "ACTIVE":
            self.transition_child("WORKING")
        elif event == "rest_request" and self.current_parent == "ACTIVE":
            self.transition_child("RESTING")
        elif event == "sleep_request":
            self.transition_parent("INACTIVE")
            self.transition_child("SLEEPING")
        elif event == "wake_request":
            self.transition_parent("ACTIVE")
            self.transition_child("WORKING")
        
        return self.get_current_state()

def main():
    print("🔄 State Machines Pattern")
    print("=" * 50)
    
    # Test basic state machine
    print(f"\n--- Basic State Machine Test ---")
    sm = StateMachine(AgentState.IDLE)
    
    # Simulate a conversation flow
    test_events = [
        (Event.USER_INPUT, {"input": "Hello, how are you?"}),
        (Event.SLEEP_COMMAND, {}),
        (Event.WAKE_COMMAND, {}),
        (Event.USER_INPUT, {"input": "What's the weather like?"}),
        (Event.RESET_COMMAND, {})
    ]
    
    for event, data in test_events:
        print(f"\n--- Event: {event.value} ---")
        sm.transition(event, data)
        state_info = sm.get_state_info()
        print(f"Current state: {state_info['current_state']}")
        print(f"Context: {state_info['context'].get('last_action', 'none')}")
    
    # Show state history
    print(f"\n--- State Transition History ---")
    history = sm.get_history()
    for i, transition in enumerate(history, 1):
        print(f"{i}. {transition['from']} → {transition['to']} ({transition['event']}) at {transition['timestamp']}")
    
    # Test hierarchical state machine
    print(f"\n--- Hierarchical State Machine Test ---")
    hsm = HierarchicalStateMachine()
    
    # Simulate hierarchical state transitions
    test_events_hierarchical = [
        ("work_request", {}),
        ("rest_request", {}),
        ("sleep_request", {}),
        ("wake_request", {}),
        ("work_request", {})
    ]
    
    for event, data in test_events_hierarchical:
        current_state = hsm.process_event(event, data)
        print(f"Current hierarchical state: {current_state}")
    
    print(f"\n--- State Machines Pattern Summary ---")
    print(f"✅ Demonstrated finite state machine implementation")
    print(f"✅ Showed state transitions and event handling")
    print(f"✅ Implemented hierarchical state management")
    print(f"✅ Created event-driven agent behavior")

if __name__ == "__main__":
    main()
