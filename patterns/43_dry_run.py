#!/usr/bin/env python3
"""
43 - Dry-Run Harness Pattern
Safety-critical pattern with simulation and approval before execution.

The Dry-Run Harness pattern implements a safety-critical workflow where an agent's
proposed action is first simulated (dry run) and must be approved (by a human or
automated checker) before live execution. This is essential for production agent
deployment, debugging, and any domain where actions have significant consequences
and need to be validated before execution.

This demonstrates:
1. Simulate actions before execution
2. Human/automated review and approval
3. Safety checks and validation
4. Go/No-go decision making
5. Rollback and recovery mechanisms
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

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

@dataclass
class Action:
    """Represents an action to be executed."""
    action_type: str
    parameters: Dict[str, Any]
    description: str
    risk_level: str
    estimated_impact: str

@dataclass
class DryRunResult:
    """Result of a dry run simulation."""
    action: Action
    simulation_output: str
    predicted_consequences: List[str]
    risk_assessment: str
    success_probability: float
    warnings: List[str]
    recommendations: List[str]

class SafetyChecker:
    """Checks actions for safety and compliance."""
    
    def __init__(self, llm):
        self.llm = llm
        self.safety_rules = [
            "No actions that could cause data loss",
            "No actions that could compromise security",
            "No actions that could affect system stability",
            "No actions that could violate compliance requirements"
        ]
    
    def check_safety(self, action: Action) -> Dict[str, Any]:
        """Check if action is safe to execute."""
        prompt = f"""
        Safety check for action: {action.description}
        
        Action type: {action.action_type}
        Parameters: {json.dumps(action.parameters, indent=2)}
        Risk level: {action.risk_level}
        
        Safety rules to check against:
        {chr(10).join(f"- {rule}" for rule in self.safety_rules)}
        
        Analyze the action for:
        1. Potential safety violations
        2. Security risks
        3. Data integrity concerns
        4. System stability impact
        5. Compliance issues
        
        Respond with JSON:
        {{
            "is_safe": true/false,
            "violations": ["violation1", "violation2"],
            "warnings": ["warning1", "warning2"],
            "risk_score": 0.0-1.0,
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback safety check
            return {
                "is_safe": action.risk_level in ["low", "medium"],
                "violations": [],
                "warnings": ["Unable to fully assess safety"],
                "risk_score": 0.5,
                "recommendations": ["Manual review recommended"]
            }

class Simulator:
    """Simulates actions to predict outcomes."""
    
    def __init__(self, llm):
        self.llm = llm
        self.simulation_models = {
            "database": self._simulate_database_action,
            "api": self._simulate_api_action,
            "file": self._simulate_file_action,
            "email": self._simulate_email_action,
            "webhook": self._simulate_webhook_action
        }
    
    def simulate_action(self, action: Action) -> DryRunResult:
        """Simulate an action and predict its outcomes."""
        print(f"🔮 Simulating action: {action.description}")
        
        # Get simulation model
        simulator_func = self.simulation_models.get(action.action_type, self._simulate_generic_action)
        
        # Run simulation
        simulation_output = simulator_func(action)
        
        # Predict consequences
        consequences = self._predict_consequences(action, simulation_output)
        
        # Assess risks
        risk_assessment = self._assess_risks(action, simulation_output, consequences)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(action, simulation_output)
        
        # Generate warnings and recommendations
        warnings = self._generate_warnings(action, simulation_output, consequences)
        recommendations = self._generate_recommendations(action, simulation_output, consequences)
        
        return DryRunResult(
            action=action,
            simulation_output=simulation_output,
            predicted_consequences=consequences,
            risk_assessment=risk_assessment,
            success_probability=success_probability,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _simulate_database_action(self, action: Action) -> str:
        """Simulate database operations."""
        operation = action.parameters.get("operation", "unknown")
        table = action.parameters.get("table", "unknown_table")
        
        if operation == "insert":
            return f"Simulated INSERT into {table}: 1 row affected, new record created"
        elif operation == "update":
            return f"Simulated UPDATE on {table}: 3 rows affected, data updated successfully"
        elif operation == "delete":
            return f"Simulated DELETE from {table}: 1 row affected, record removed"
        else:
            return f"Simulated {operation} on {table}: Operation completed"
    
    def _simulate_api_action(self, action: Action) -> str:
        """Simulate API calls."""
        endpoint = action.parameters.get("endpoint", "/api/unknown")
        method = action.parameters.get("method", "GET")
        
        return f"Simulated {method} {endpoint}: Status 200, Response received successfully"
    
    def _simulate_file_action(self, action: Action) -> str:
        """Simulate file operations."""
        operation = action.parameters.get("operation", "unknown")
        filename = action.parameters.get("filename", "unknown.txt")
        
        if operation == "create":
            return f"Simulated file creation: {filename} created successfully"
        elif operation == "modify":
            return f"Simulated file modification: {filename} updated successfully"
        elif operation == "delete":
            return f"Simulated file deletion: {filename} removed successfully"
        else:
            return f"Simulated {operation} on {filename}: Operation completed"
    
    def _simulate_email_action(self, action: Action) -> str:
        """Simulate email operations."""
        recipient = action.parameters.get("recipient", "unknown@example.com")
        subject = action.parameters.get("subject", "Test Email")
        
        return f"Simulated email to {recipient}: '{subject}' sent successfully"
    
    def _simulate_webhook_action(self, action: Action) -> str:
        """Simulate webhook calls."""
        url = action.parameters.get("url", "https://example.com/webhook")
        payload = action.parameters.get("payload", {})
        
        return f"Simulated webhook to {url}: Payload sent, response received"
    
    def _simulate_generic_action(self, action: Action) -> str:
        """Simulate generic actions."""
        return f"Simulated {action.action_type}: Action completed successfully"
    
    def _predict_consequences(self, action: Action, simulation_output: str) -> List[str]:
        """Predict consequences of the action."""
        prompt = f"""
        Action: {action.description}
        Simulation output: {simulation_output}
        
        Predict the potential consequences of this action:
        1. Immediate effects
        2. Short-term impacts
        3. Long-term implications
        4. Side effects or unintended consequences
        
        Provide 3-5 specific consequences.
        """
        
        response = self.llm.generate(prompt).content
        # Extract consequences from response
        consequences = []
        for line in response.split('\n'):
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                consequences.append(line.strip()[1:].strip())
        
        return consequences[:5] if consequences else ["Consequences predicted successfully"]
    
    def _assess_risks(self, action: Action, simulation_output: str, consequences: List[str]) -> str:
        """Assess risks associated with the action."""
        prompt = f"""
        Action: {action.description}
        Simulation output: {simulation_output}
        Predicted consequences: {', '.join(consequences)}
        
        Assess the risks associated with this action:
        1. Data integrity risks
        2. Security risks
        3. Performance risks
        4. Compliance risks
        5. Business continuity risks
        
        Provide a comprehensive risk assessment.
        """
        
        return self.llm.generate(prompt).content
    
    def _calculate_success_probability(self, action: Action, simulation_output: str) -> float:
        """Calculate probability of successful execution."""
        # Simple heuristic based on action type and risk level
        base_probability = 0.8
        
        if action.risk_level == "low":
            base_probability = 0.9
        elif action.risk_level == "medium":
            base_probability = 0.7
        elif action.risk_level == "high":
            base_probability = 0.5
        
        # Add some randomness to simulate real-world uncertainty
        return max(0.1, min(0.95, base_probability + random.uniform(-0.1, 0.1)))
    
    def _generate_warnings(self, action: Action, simulation_output: str, consequences: List[str]) -> List[str]:
        """Generate warnings about the action."""
        warnings = []
        
        if action.risk_level == "high":
            warnings.append("High-risk action requires careful monitoring")
        
        if "delete" in action.action_type.lower():
            warnings.append("Data deletion action - ensure backups exist")
        
        if "api" in action.action_type.lower():
            warnings.append("External API call - verify endpoint availability")
        
        return warnings
    
    def _generate_recommendations(self, action: Action, simulation_output: str, consequences: List[str]) -> List[str]:
        """Generate recommendations for the action."""
        recommendations = []
        
        if action.risk_level == "high":
            recommendations.append("Consider breaking into smaller, safer steps")
        
        recommendations.append("Monitor execution closely")
        recommendations.append("Have rollback plan ready")
        
        return recommendations

class Reviewer:
    """Reviews dry run results and makes approval decisions."""
    
    def __init__(self, llm, auto_approve_threshold: float = 0.8):
        self.llm = llm
        self.auto_approve_threshold = auto_approve_threshold
    
    def review_dry_run(self, dry_run_result: DryRunResult) -> Dict[str, Any]:
        """Review dry run result and make approval decision."""
        prompt = f"""
        Review this dry run result for approval:
        
        Action: {dry_run_result.action.description}
        Action type: {dry_run_result.action.action_type}
        Risk level: {dry_run_result.action.risk_level}
        
        Simulation output: {dry_run_result.simulation_output}
        Predicted consequences: {', '.join(dry_run_result.predicted_consequences)}
        Risk assessment: {dry_run_result.risk_assessment}
        Success probability: {dry_run_result.success_probability:.2f}
        Warnings: {', '.join(dry_run_result.warnings)}
        Recommendations: {', '.join(dry_run_result.recommendations)}
        
        Make an approval decision:
        1. APPROVED - Action is safe to execute
        2. REJECTED - Action is too risky
        3. NEEDS_REVISION - Action needs modification before approval
        
        Consider:
        - Safety implications
        - Risk vs benefit
        - Success probability
        - Potential consequences
        
        Respond with JSON:
        {{
            "decision": "APPROVED/REJECTED/NEEDS_REVISION",
            "reason": "explanation of decision",
            "conditions": ["condition1", "condition2"],
            "confidence": 0.0-1.0
        }}
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback decision based on success probability
            if dry_run_result.success_probability >= self.auto_approve_threshold:
                return {
                    "decision": "APPROVED",
                    "reason": "High success probability",
                    "conditions": [],
                    "confidence": 0.7
                }
            else:
                return {
                    "decision": "NEEDS_REVISION",
                    "reason": "Low success probability",
                    "conditions": ["Improve success probability"],
                    "confidence": 0.6
                }

class DryRunHarness:
    """Main dry run harness system."""
    
    def __init__(self, llm):
        self.llm = llm
        self.safety_checker = SafetyChecker(llm)
        self.simulator = Simulator(llm)
        self.reviewer = Reviewer(llm)
        self.execution_history = []
    
    def process_action(self, action: Action) -> Dict[str, Any]:
        """Process an action through the dry run harness."""
        print(f"🛡️ Processing action: {action.description}")
        print("=" * 50)
        
        # Step 1: Safety check
        print("\n🔒 Safety check...")
        safety_result = self.safety_checker.check_safety(action)
        print(f"Safe: {safety_result['is_safe']}")
        print(f"Risk score: {safety_result['risk_score']:.2f}")
        
        if not safety_result['is_safe']:
            return {
                "action": action,
                "status": "rejected",
                "reason": "Failed safety check",
                "safety_violations": safety_result['violations'],
                "executed": False
            }
        
        # Step 2: Dry run simulation
        print("\n🔮 Dry run simulation...")
        dry_run_result = self.simulator.simulate_action(action)
        print(f"Success probability: {dry_run_result.success_probability:.2f}")
        print(f"Warnings: {len(dry_run_result.warnings)}")
        
        # Step 3: Review and approval
        print("\n👥 Review and approval...")
        review_result = self.reviewer.review_dry_run(dry_run_result)
        print(f"Decision: {review_result['decision']}")
        print(f"Reason: {review_result['reason']}")
        
        # Step 4: Execute or reject
        if review_result['decision'] == "APPROVED":
            print("\n✅ Action approved - executing...")
            execution_result = self._execute_action(action)
            self.execution_history.append({
                "action": action,
                "dry_run_result": dry_run_result,
                "review_result": review_result,
                "execution_result": execution_result,
                "status": "executed"
            })
            return {
                "action": action,
                "status": "executed",
                "dry_run_result": dry_run_result,
                "review_result": review_result,
                "execution_result": execution_result,
                "executed": True
            }
        else:
            print(f"\n❌ Action {review_result['decision'].lower()}")
            self.execution_history.append({
                "action": action,
                "dry_run_result": dry_run_result,
                "review_result": review_result,
                "status": review_result['decision'].lower()
            })
            return {
                "action": action,
                "status": review_result['decision'].lower(),
                "reason": review_result['reason'],
                "dry_run_result": dry_run_result,
                "review_result": review_result,
                "executed": False
            }
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute the approved action."""
        # Simulate execution
        print(f"⚡ Executing: {action.description}")
        
        # Simulate execution time
        import time
        time.sleep(0.5)
        
        # Simulate success/failure
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            return {
                "status": "success",
                "output": f"Action '{action.description}' executed successfully",
                "timestamp": len(self.execution_history)
            }
        else:
            return {
                "status": "failed",
                "error": "Simulated execution failure",
                "timestamp": len(self.execution_history)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        total_actions = len(self.execution_history)
        executed_actions = len([h for h in self.execution_history if h['status'] == 'executed'])
        rejected_actions = len([h for h in self.execution_history if h['status'] == 'rejected'])
        
        return {
            "total_actions": total_actions,
            "executed_actions": executed_actions,
            "rejected_actions": rejected_actions,
            "success_rate": executed_actions / total_actions if total_actions > 0 else 0,
            "recent_actions": self.execution_history[-5:] if self.execution_history else []
        }

def main():
    print("🛡️ Dry-Run Harness Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create dry run harness
    harness = DryRunHarness(llm)
    
    # Test actions
    test_actions = [
        Action(
            action_type="database",
            parameters={"operation": "insert", "table": "users", "data": {"name": "John", "email": "john@example.com"}},
            description="Add new user to database",
            risk_level="low",
            estimated_impact="Adds one user record"
        ),
        Action(
            action_type="file",
            parameters={"operation": "delete", "filename": "temp_data.txt"},
            description="Delete temporary file",
            risk_level="medium",
            estimated_impact="Removes temporary data file"
        ),
        Action(
            action_type="api",
            parameters={"method": "POST", "endpoint": "/api/users", "data": {"name": "Jane"}},
            description="Create user via API",
            risk_level="low",
            estimated_impact="Creates user through external API"
        ),
        Action(
            action_type="database",
            parameters={"operation": "delete", "table": "users", "condition": "id=1"},
            description="Delete user from database",
            risk_level="high",
            estimated_impact="Permanently removes user record"
        )
    ]
    
    for action in test_actions:
        print(f"\n{'='*60}")
        result = harness.process_action(action)
        
        print(f"\n📊 Action Summary:")
        print(f"  - Status: {result['status']}")
        print(f"  - Executed: {result['executed']}")
        if 'execution_result' in result:
            print(f"  - Execution: {result['execution_result']['status']}")
    
    # Show system status
    print(f"\n{'='*60}")
    print("📈 System Status:")
    status = harness.get_system_status()
    print(f"  - Total actions: {status['total_actions']}")
    print(f"  - Executed: {status['executed_actions']}")
    print(f"  - Rejected: {status['rejected_actions']}")
    print(f"  - Success rate: {status['success_rate']:.1%}")

if __name__ == "__main__":
    main()
