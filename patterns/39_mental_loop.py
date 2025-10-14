#!/usr/bin/env python3
"""
39 - Mental Loop (Simulator) Pattern
Agent tests actions in internal simulation before real-world execution.

The Mental Loop pattern enables agents to test their actions in an internal
"mental model" or simulator to predict outcomes and assess risk before acting
in the real world. This is particularly valuable for safety-critical systems,
robotics, financial trading, and any domain where actions have significant
consequences. The agent can explore different scenarios and choose the best
course of action based on simulated outcomes.

This demonstrates:
1. Internal simulation of actions before execution
2. Outcome prediction and risk assessment
3. Scenario exploration and comparison
4. Safe action selection based on simulation results
5. Iterative refinement of actions through simulation
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ActionType(Enum):
    MOVE = "move"
    INTERACT = "interact"
    COMMUNICATE = "communicate"
    ANALYZE = "analyze"
    DECIDE = "decide"

@dataclass
class Action:
    """Represents an action to be simulated."""
    action_type: ActionType
    parameters: Dict[str, Any]
    description: str
    risk_level: str
    expected_outcome: str

@dataclass
class SimulationResult:
    """Result of a simulation."""
    action: Action
    outcome: str
    success_probability: float
    risks: List[str]
    benefits: List[str]
    side_effects: List[str]
    confidence: float

class MentalSimulator:
    """Internal simulator for testing actions."""
    
    def __init__(self, llm):
        self.llm = llm
        self.simulation_history = []
        self.world_state = {
            "environment": "office",
            "time": "business_hours",
            "people_present": ["colleague1", "colleague2"],
            "mood": "neutral",
            "resources_available": ["computer", "phone", "documents"]
        }
    
    def simulate_action(self, action: Action) -> SimulationResult:
        """Simulate an action and predict its outcome."""
        print(f"🔮 Simulating action: {action.description}")
        
        # Generate simulation based on action type
        if action.action_type == ActionType.MOVE:
            outcome = self._simulate_movement(action)
        elif action.action_type == ActionType.INTERACT:
            outcome = self._simulate_interaction(action)
        elif action.action_type == ActionType.COMMUNICATE:
            outcome = self._simulate_communication(action)
        elif action.action_type == ActionType.ANALYZE:
            outcome = self._simulate_analysis(action)
        else:
            outcome = self._simulate_generic(action)
        
        # Analyze risks and benefits
        risks = self._analyze_risks(action, outcome)
        benefits = self._analyze_benefits(action, outcome)
        side_effects = self._analyze_side_effects(action, outcome)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(action, outcome)
        
        # Calculate confidence
        confidence = self._calculate_confidence(action, outcome)
        
        result = SimulationResult(
            action=action,
            outcome=outcome,
            success_probability=success_probability,
            risks=risks,
            benefits=benefits,
            side_effects=side_effects,
            confidence=confidence
        )
        
        # Store in history
        self.simulation_history.append(result)
        
        return result
    
    def _simulate_movement(self, action: Action) -> str:
        """Simulate movement actions."""
        destination = action.parameters.get("destination", "unknown")
        method = action.parameters.get("method", "walking")
        
        prompt = f"""
        Simulate this movement action:
        - Destination: {destination}
        - Method: {method}
        - Current environment: {self.world_state['environment']}
        - Time: {self.world_state['time']}
        
        Predict what would happen during this movement, including:
        - Physical obstacles or challenges
        - Time required
        - Energy expenditure
        - Potential interruptions
        - Environmental factors
        """
        
        return self.llm.generate(prompt).content
    
    def _simulate_interaction(self, action: Action) -> str:
        """Simulate interaction actions."""
        target = action.parameters.get("target", "unknown")
        interaction_type = action.parameters.get("type", "general")
        
        prompt = f"""
        Simulate this interaction:
        - Target: {target}
        - Type: {interaction_type}
        - People present: {', '.join(self.world_state['people_present'])}
        - Current mood: {self.world_state['mood']}
        
        Predict the interaction outcome, including:
        - How the target would respond
        - Emotional reactions
        - Information exchange
        - Relationship impact
        - Potential misunderstandings
        """
        
        return self.llm.generate(prompt).content
    
    def _simulate_communication(self, action: Action) -> str:
        """Simulate communication actions."""
        message = action.parameters.get("message", "")
        recipient = action.parameters.get("recipient", "unknown")
        channel = action.parameters.get("channel", "verbal")
        
        prompt = f"""
        Simulate this communication:
        - Message: {message}
        - Recipient: {recipient}
        - Channel: {channel}
        - Context: {self.world_state['environment']}
        
        Predict the communication outcome, including:
        - How the message would be received
        - Likely response
        - Misinterpretation risks
        - Relationship impact
        - Follow-up needs
        """
        
        return self.llm.generate(prompt).content
    
    def _simulate_analysis(self, action: Action) -> str:
        """Simulate analysis actions."""
        data = action.parameters.get("data", "unknown")
        analysis_type = action.parameters.get("type", "general")
        
        prompt = f"""
        Simulate this analysis:
        - Data: {data}
        - Analysis type: {analysis_type}
        - Available resources: {', '.join(self.world_state['resources_available'])}
        
        Predict the analysis outcome, including:
        - What insights would be discovered
        - Time required
        - Resource needs
        - Potential errors or biases
        - Actionable recommendations
        """
        
        return self.llm.generate(prompt).content
    
    def _simulate_generic(self, action: Action) -> str:
        """Simulate generic actions."""
        prompt = f"""
        Simulate this action: {action.description}
        
        Parameters: {json.dumps(action.parameters, indent=2)}
        Current world state: {json.dumps(self.world_state, indent=2)}
        
        Predict what would happen if this action were executed.
        """
        
        return self.llm.generate(prompt).content
    
    def _analyze_risks(self, action: Action, outcome: str) -> List[str]:
        """Analyze risks of the action."""
        prompt = f"""
        Action: {action.description}
        Predicted outcome: {outcome}
        
        Identify potential risks and negative consequences:
        1. Immediate risks
        2. Long-term risks
        3. Risks to others
        4. Reputation risks
        5. Resource risks
        
        List 3-5 specific risks.
        """
        
        response = self.llm.generate(prompt).content
        risks = []
        for line in response.split('\n'):
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                risks.append(line.strip()[1:].strip())
        
        return risks[:5] if risks else ["Potential risks identified"]
    
    def _analyze_benefits(self, action: Action, outcome: str) -> List[str]:
        """Analyze benefits of the action."""
        prompt = f"""
        Action: {action.description}
        Predicted outcome: {outcome}
        
        Identify potential benefits and positive outcomes:
        1. Immediate benefits
        2. Long-term benefits
        3. Benefits to others
        4. Learning opportunities
        5. Relationship benefits
        
        List 3-5 specific benefits.
        """
        
        response = self.llm.generate(prompt).content
        benefits = []
        for line in response.split('\n'):
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                benefits.append(line.strip()[1:].strip())
        
        return benefits[:5] if benefits else ["Potential benefits identified"]
    
    def _analyze_side_effects(self, action: Action, outcome: str) -> List[str]:
        """Analyze side effects of the action."""
        prompt = f"""
        Action: {action.description}
        Predicted outcome: {outcome}
        
        Identify potential side effects and unintended consequences:
        1. Unintended positive effects
        2. Unintended negative effects
        3. Effects on other people
        4. Environmental effects
        5. Systemic effects
        
        List 3-5 specific side effects.
        """
        
        response = self.llm.generate(prompt).content
        side_effects = []
        for line in response.split('\n'):
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                side_effects.append(line.strip()[1:].strip())
        
        return side_effects[:5] if side_effects else ["Potential side effects identified"]
    
    def _calculate_success_probability(self, action: Action, outcome: str) -> float:
        """Calculate probability of successful execution."""
        # Base probability based on action type
        base_probabilities = {
            ActionType.MOVE: 0.8,
            ActionType.INTERACT: 0.7,
            ActionType.COMMUNICATE: 0.6,
            ActionType.ANALYZE: 0.8,
            ActionType.DECIDE: 0.5
        }
        
        base_prob = base_probabilities.get(action.action_type, 0.5)
        
        # Adjust based on risk level
        risk_adjustments = {
            "low": 0.1,
            "medium": 0.0,
            "high": -0.2
        }
        
        adjustment = risk_adjustments.get(action.risk_level, 0.0)
        
        # Add some randomness
        random_factor = random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, base_prob + adjustment + random_factor))
    
    def _calculate_confidence(self, action: Action, outcome: str) -> float:
        """Calculate confidence in the simulation."""
        # Base confidence
        base_confidence = 0.7
        
        # Adjust based on action complexity
        if len(action.parameters) > 3:
            base_confidence -= 0.1
        
        # Adjust based on risk level
        if action.risk_level == "high":
            base_confidence -= 0.1
        
        return max(0.1, min(1.0, base_confidence))

class MentalLoopAgent:
    """Agent that uses mental simulation before acting."""
    
    def __init__(self, llm):
        self.llm = llm
        self.simulator = MentalSimulator(llm)
        self.action_history = []
    
    def propose_action(self, situation: str, goal: str) -> List[Action]:
        """Propose possible actions for a situation."""
        prompt = f"""
        Situation: {situation}
        Goal: {goal}
        
        Propose 3-5 possible actions to achieve the goal. For each action, specify:
        1. Action type (move, interact, communicate, analyze, decide)
        2. Parameters needed
        3. Description of what the action involves
        4. Risk level (low, medium, high)
        5. Expected outcome
        
        Format as JSON array of objects:
        [
            {{
                "action_type": "move",
                "parameters": {{"destination": "office", "method": "walking"}},
                "description": "Walk to the office",
                "risk_level": "low",
                "expected_outcome": "Reach the office safely"
            }}
        ]
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            actions_data = json.loads(json_str)
            actions = []
            
            for action_data in actions_data:
                action = Action(
                    action_type=ActionType(action_data["action_type"]),
                    parameters=action_data["parameters"],
                    description=action_data["description"],
                    risk_level=action_data["risk_level"],
                    expected_outcome=action_data["expected_outcome"]
                )
                actions.append(action)
            
            return actions
        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback actions
            return [
                Action(
                    action_type=ActionType.ANALYZE,
                    parameters={"data": situation, "type": "situation_analysis"},
                    description="Analyze the current situation",
                    risk_level="low",
                    expected_outcome="Better understanding of the situation"
                )
            ]
    
    def simulate_and_choose(self, situation: str, goal: str) -> Dict[str, Any]:
        """Simulate actions and choose the best one."""
        print(f"🎯 Situation: {situation}")
        print(f"🎯 Goal: {goal}")
        print("=" * 50)
        
        # Propose actions
        print("\n💭 Proposing actions...")
        proposed_actions = self.propose_action(situation, goal)
        print(f"Proposed {len(proposed_actions)} actions")
        
        # Simulate each action
        print("\n🔮 Simulating actions...")
        simulation_results = []
        
        for i, action in enumerate(proposed_actions, 1):
            print(f"\n--- Simulating Action {i} ---")
            print(f"Action: {action.description}")
            print(f"Type: {action.action_type.value}")
            print(f"Risk: {action.risk_level}")
            
            result = self.simulator.simulate_action(action)
            simulation_results.append(result)
            
            print(f"Success probability: {result.success_probability:.2f}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Risks: {len(result.risks)}")
            print(f"Benefits: {len(result.benefits)}")
        
        # Choose best action
        print("\n🤔 Choosing best action...")
        best_result = self._choose_best_action(simulation_results)
        
        # Execute chosen action
        print(f"\n⚡ Executing chosen action: {best_result.action.description}")
        execution_result = self._execute_action(best_result.action)
        
        # Store in history
        self.action_history.append({
            "situation": situation,
            "goal": goal,
            "chosen_action": best_result.action,
            "simulation_result": best_result,
            "execution_result": execution_result
        })
        
        return {
            "situation": situation,
            "goal": goal,
            "proposed_actions": proposed_actions,
            "simulation_results": simulation_results,
            "chosen_action": best_result.action,
            "chosen_simulation": best_result,
            "execution_result": execution_result
        }
    
    def _choose_best_action(self, simulation_results: List[SimulationResult]) -> SimulationResult:
        """Choose the best action based on simulation results."""
        # Score each result
        scored_results = []
        
        for result in simulation_results:
            # Calculate composite score
            score = (
                result.success_probability * 0.4 +
                result.confidence * 0.3 +
                (1 - len(result.risks) / 10) * 0.2 +  # Fewer risks is better
                (len(result.benefits) / 10) * 0.1     # More benefits is better
            )
            
            scored_results.append((score, result))
        
        # Return highest scoring result
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1]
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute the chosen action (simulated execution)."""
        print(f"Executing: {action.description}")
        
        # Simulate execution time
        import time
        time.sleep(0.5)
        
        # Simulate success/failure based on success probability
        success = random.random() < 0.8  # 80% success rate for demonstration
        
        if success:
            return {
                "status": "success",
                "outcome": f"Successfully executed: {action.description}",
                "timestamp": len(self.action_history)
            }
        else:
            return {
                "status": "failed",
                "outcome": f"Failed to execute: {action.description}",
                "error": "Simulated execution failure",
                "timestamp": len(self.action_history)
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.action_history:
            return {"total_actions": 0}
        
        successful_actions = len([h for h in self.action_history if h["execution_result"]["status"] == "success"])
        total_actions = len(self.action_history)
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": successful_actions / total_actions if total_actions > 0 else 0,
            "simulation_count": len(self.simulator.simulation_history)
        }

def main():
    print("🧠 Mental Loop (Simulator) Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create mental loop agent
    agent = MentalLoopAgent(llm)
    
    # Test scenarios
    scenarios = [
        {
            "situation": "You need to ask your colleague for help with a project, but they seem busy and stressed.",
            "goal": "Get the help you need without adding to their stress"
        },
        {
            "situation": "You have to present a new idea to your team, but you're not sure how they'll react.",
            "goal": "Present the idea effectively and get team buy-in"
        },
        {
            "situation": "You need to make a decision about a project deadline, but you don't have all the information.",
            "goal": "Make the best decision possible with available information"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}/{len(scenarios)}")
        result = agent.simulate_and_choose(scenario["situation"], scenario["goal"])
        
        print(f"\n📊 Scenario Summary:")
        print(f"  - Actions proposed: {len(result['proposed_actions'])}")
        print(f"  - Chosen action: {result['chosen_action'].description}")
        print(f"  - Success probability: {result['chosen_simulation'].success_probability:.2f}")
        print(f"  - Execution: {result['execution_result']['status']}")
    
    # Show performance summary
    print(f"\n{'='*60}")
    print("📈 Performance Summary:")
    summary = agent.get_performance_summary()
    print(f"  - Total actions: {summary['total_actions']}")
    print(f"  - Successful actions: {summary['successful_actions']}")
    print(f"  - Success rate: {summary['success_rate']:.1%}")
    print(f"  - Simulations run: {summary['simulation_count']}")

if __name__ == "__main__":
    main()
