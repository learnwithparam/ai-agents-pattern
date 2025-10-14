#!/usr/bin/env python3
"""
46 - Reflexive Metacognitive Pattern
Agent with self-awareness that reasons about its own capabilities and limitations.

The Reflexive Metacognitive pattern implements an agent with a "self-model" that
reasons about its own capabilities and limitations, choosing to act, use a tool,
or escalate to a human to ensure safety and effectiveness. This is particularly
valuable for high-stakes advisory roles in medical, legal, finance, and other
domains where understanding one's own limitations is crucial.

This demonstrates:
1. Self-model and capability assessment
2. Metacognitive reasoning about own abilities
3. Capability-based decision making
4. Escalation to humans when needed
5. Self-improvement through reflection
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

class CapabilityLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class DecisionType(Enum):
    DIRECT_ANSWER = "direct_answer"
    USE_TOOL = "use_tool"
    ESCALATE_HUMAN = "escalate_human"
    REFUSE = "refuse"

@dataclass
class Capability:
    """Represents a specific capability."""
    name: str
    level: CapabilityLevel
    confidence: float
    description: str
    limitations: List[str]
    examples: List[str]

@dataclass
class SelfModel:
    """Represents the agent's self-model."""
    capabilities: Dict[str, Capability]
    overall_confidence: float
    known_limitations: List[str]
    strengths: List[str]
    improvement_areas: List[str]

@dataclass
class Decision:
    """Represents a decision made by the agent."""
    decision_type: DecisionType
    reasoning: str
    confidence: float
    alternative_actions: List[str]
    risk_assessment: str

class MetacognitiveReasoner:
    """Handles metacognitive reasoning about capabilities."""
    
    def __init__(self, llm):
        self.llm = llm
        self.self_model = self._initialize_self_model()
        self.decision_history = []
    
    def _initialize_self_model(self) -> SelfModel:
        """Initialize the agent's self-model."""
        capabilities = {
            "text_generation": Capability(
                name="text_generation", level=CapabilityLevel.ADVANCED, confidence=0.8,
                description="Generate coherent and contextually appropriate text",
                limitations=["May generate factually incorrect information", "Limited to training data knowledge"],
                examples=["Creative writing", "Explanations", "Summaries"]
            ),
            "mathematical_reasoning": Capability(
                name="mathematical_reasoning", level=CapabilityLevel.INTERMEDIATE, confidence=0.7,
                description="Solve mathematical problems and perform calculations",
                limitations=["Complex proofs may be challenging", "Limited to standard mathematical concepts"],
                examples=["Arithmetic", "Algebra", "Basic calculus"]
            ),
            "code_generation": Capability(
                name="code_generation", level=CapabilityLevel.ADVANCED, confidence=0.8,
                description="Generate and analyze code in multiple programming languages",
                limitations=["May not handle very complex architectures", "Limited to common patterns"],
                examples=["Python scripts", "Web applications", "Data analysis"]
            ),
            "research": Capability(
                name="research", level=CapabilityLevel.BASIC, confidence=0.5,
                description="Search for and synthesize information",
                limitations=["No real-time access to current information", "Limited to training data"],
                examples=["Historical research", "Conceptual explanations", "Literature reviews"]
            ),
            "safety_critical": Capability(
                name="safety_critical", level=CapabilityLevel.BASIC, confidence=0.3,
                description="Handle safety-critical decisions",
                limitations=["Not trained for high-stakes decisions", "May lack domain expertise"],
                examples=["Basic safety advice", "General guidelines", "Risk identification"]
            )
        }
        
        return SelfModel(
            capabilities=capabilities, overall_confidence=0.7,
            known_limitations=[
                "No real-time information access",
                "Limited to training data knowledge",
                "May generate plausible but incorrect information",
                "Not suitable for high-stakes decisions without human oversight"
            ],
            strengths=[
                "Strong language understanding", "Good at pattern recognition",
                "Creative problem solving", "Code generation and analysis"
            ],
            improvement_areas=[
                "Real-time information access", "Domain-specific expertise",
                "High-stakes decision making", "Fact verification"
            ]
        )
    
    def assess_capability(self, task: str, required_capability: str) -> Dict[str, Any]:
        """Assess capability for a specific task."""
        if required_capability not in self.self_model.capabilities:
            return {
                "capable": False, "confidence": 0.0,
                "reason": "Unknown capability", "recommendation": "Escalate to human"
            }
        
        capability = self.self_model.capabilities[required_capability]
        
        prompt = f"""
        Analyze the complexity of this task: {task}
        
        Required capability: {required_capability}
        My capability level: {capability.level.value}
        My confidence: {capability.confidence}
        
        Assess:
        1. Task complexity (1-10)
        2. Whether I can handle this task
        3. Confidence level (0-1)
        4. Specific risks or limitations
        5. Recommendation for action
        
        Format as JSON:
        {{
            "task_complexity": 7,
            "capable": true/false,
            "confidence": 0.8,
            "risks": ["risk1", "risk2"],
            "recommendation": "direct_answer/use_tool/escalate_human/refuse"
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
            return {
                "task_complexity": 5, "capable": capability.level in [CapabilityLevel.ADVANCED, CapabilityLevel.EXPERT],
                "confidence": capability.confidence, "risks": capability.limitations,
                "recommendation": "direct_answer" if capability.level in [CapabilityLevel.ADVANCED, CapabilityLevel.EXPERT] else "escalate_human"
            }
    
    def make_decision(self, task: str, context: Dict[str, Any] = None) -> Decision:
        """Make a metacognitive decision about how to handle a task."""
        print(f"🤔 Analyzing task: {task[:50]}...")
        
        prompt = f"""
        Analyze this task and determine what capabilities are needed: {task}
        
        Available capabilities: {', '.join(self.self_model.capabilities.keys())}
        
        Determine:
        1. Primary capability needed
        2. Secondary capabilities
        3. Task complexity (1-10)
        4. Safety implications
        5. Whether this requires human expertise
        
        Format as JSON:
        {{
            "primary_capability": "text_generation",
            "secondary_capabilities": ["research"],
            "complexity": 6,
            "safety_critical": false,
            "requires_human": false
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
            
            task_analysis = json.loads(json_str)
        except json.JSONDecodeError:
            task_analysis = {
                "primary_capability": "text_generation", "secondary_capabilities": [],
                "complexity": 5, "safety_critical": False, "requires_human": False
            }
        
        capability_assessment = self.assess_capability(task, task_analysis["primary_capability"])
        decision_type = self._determine_decision_type(task_analysis, capability_assessment)
        reasoning = self._generate_reasoning(task, task_analysis, capability_assessment, decision_type)
        risk_assessment = self._assess_risks(task, task_analysis, capability_assessment)
        alternatives = self._generate_alternatives(task, decision_type)
        
        decision = Decision(
            decision_type=decision_type, reasoning=reasoning,
            confidence=capability_assessment.get("confidence", 0.5),
            alternative_actions=alternatives, risk_assessment=risk_assessment
        )
        
        self.decision_history.append({
            "task": task, "decision": decision, "timestamp": len(self.decision_history)
        })
        
        return decision
    
    def _determine_decision_type(self, task_analysis: Dict[str, Any], capability_assessment: Dict[str, Any]) -> DecisionType:
        """Determine the type of decision to make."""
        if task_analysis.get("safety_critical", False) or task_analysis.get("requires_human", False):
            return DecisionType.ESCALATE_HUMAN
        
        if not capability_assessment.get("capable", False) or capability_assessment.get("confidence", 0) < 0.5:
            return DecisionType.ESCALATE_HUMAN
        
        if task_analysis.get("complexity", 5) > 7:
            return DecisionType.USE_TOOL
        
        return DecisionType.DIRECT_ANSWER
    
    def _generate_reasoning(self, task: str, task_analysis: Dict[str, Any], capability_assessment: Dict[str, Any], decision_type: DecisionType) -> str:
        """Generate reasoning for the decision."""
        return f"Decision based on task complexity {task_analysis.get('complexity', 5)}, capability assessment {capability_assessment.get('capable', False)}, and confidence {capability_assessment.get('confidence', 0.5):.2f}"
    
    def _assess_risks(self, task: str, task_analysis: Dict[str, Any], capability_assessment: Dict[str, Any]) -> str:
        """Assess risks associated with the decision."""
        risks = capability_assessment.get("risks", [])
        if task_analysis.get("safety_critical", False):
            risks.append("Safety-critical task requires human oversight")
        if capability_assessment.get("confidence", 0) < 0.7:
            risks.append("Low confidence in capability")
        return "; ".join(risks) if risks else "Low risk"
    
    def _generate_alternatives(self, task: str, decision_type: DecisionType) -> List[str]:
        """Generate alternative actions."""
        if decision_type == DecisionType.DIRECT_ANSWER:
            return ["Use specialized tools for better accuracy", "Break down into smaller sub-tasks", "Escalate to human expert"]
        elif decision_type == DecisionType.USE_TOOL:
            return ["Provide direct answer with disclaimers", "Escalate to human expert", "Request more specific information"]
        else:
            return ["Provide preliminary analysis with clear limitations", "Suggest specific questions for human expert", "Offer to help with related tasks within capabilities"]

class ReflexiveMetacognitiveAgent:
    """Main reflexive metacognitive agent."""
    
    def __init__(self, llm):
        self.llm = llm
        self.metacognitive_reasoner = MetacognitiveReasoner(llm)
        self.tools = {
            "calculator": self._calculator_tool,
            "search": self._search_tool,
            "code_analyzer": self._code_analyzer_tool
        }
    
    def _calculator_tool(self, expression: str) -> str:
        """Calculator tool for mathematical operations."""
        try:
            allowed_names = {"abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _search_tool(self, query: str) -> str:
        """Mock search tool."""
        return f"Search results for: {query} (This is a mock search tool)"
    
    def _code_analyzer_tool(self, code: str) -> str:
        """Mock code analyzer tool."""
        return f"Code analysis: {len(code)} characters, appears to be valid code"
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process a request using metacognitive reasoning."""
        print(f"🎯 Processing request: {request}")
        print("=" * 50)
        
        decision = self.metacognitive_reasoner.make_decision(request)
        
        print(f"\n🧠 Metacognitive Analysis:")
        print(f"Decision: {decision.decision_type.value}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Risks: {decision.risk_assessment}")
        
        if decision.decision_type == DecisionType.DIRECT_ANSWER:
            result = self._provide_direct_answer(request)
        elif decision.decision_type == DecisionType.USE_TOOL:
            result = self._use_tool(request)
        elif decision.decision_type == DecisionType.ESCALATE_HUMAN:
            result = self._escalate_to_human(request, decision)
        else:
            result = self._refuse_request(request, decision)
        
        return {
            "request": request, "decision": decision, "result": result,
            "timestamp": len(self.metacognitive_reasoner.decision_history)
        }
    
    def _provide_direct_answer(self, request: str) -> Dict[str, Any]:
        """Provide direct answer to the request."""
        print("\n💬 Providing direct answer...")
        prompt = f"Answer this request directly and accurately: {request}\n\nBe clear about any limitations or uncertainties in your response."
        answer = self.llm.generate(prompt).content
        return {"type": "direct_answer", "content": answer, "confidence": 0.8}
    
    def _use_tool(self, request: str) -> Dict[str, Any]:
        """Use appropriate tool to handle the request."""
        print("\n🔧 Using tool...")
        
        if any(word in request.lower() for word in ["calculate", "math", "compute", "solve"]):
            tool_name = "calculator"
        elif any(word in request.lower() for word in ["search", "find", "look up"]):
            tool_name = "search"
        elif any(word in request.lower() for word in ["code", "program", "analyze"]):
            tool_name = "code_analyzer"
        else:
            tool_name = "search"
        
        tool_result = self.tools[tool_name](request)
        final_prompt = f"Request: {request}\nTool used: {tool_name}\nTool result: {tool_result}\n\nProvide a comprehensive response using the tool result."
        final_answer = self.llm.generate(final_prompt).content
        
        return {
            "type": "tool_usage", "tool_used": tool_name, "tool_result": tool_result,
            "final_answer": final_answer, "confidence": 0.7
        }
    
    def _escalate_to_human(self, request: str, decision: Decision) -> Dict[str, Any]:
        """Escalate request to human."""
        print("\n👥 Escalating to human...")
        escalation_reason = f"This request has been escalated to a human expert because:\n\n{decision.reasoning}\n\nRisks identified: {decision.risk_assessment}\n\nAlternative actions considered:\n{chr(10).join(f'- {alt}' for alt in decision.alternative_actions)}\n\nPlease provide guidance on how to handle this request."
        return {"type": "escalation", "reason": escalation_reason, "confidence": 1.0}
    
    def _refuse_request(self, request: str, decision: Decision) -> Dict[str, Any]:
        """Refuse to handle the request."""
        print("\n❌ Refusing request...")
        refusal_reason = f"I cannot handle this request because:\n\n{decision.reasoning}\n\nThis request is outside my capabilities or poses too high a risk.\nPlease consider rephrasing the request or consulting a human expert."
        return {"type": "refusal", "reason": refusal_reason, "confidence": 1.0}

def main():
    print("🧠 Reflexive Metacognitive Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create reflexive metacognitive agent
    agent = ReflexiveMetacognitiveAgent(llm)
    
    # Test requests
    test_requests = [
        "What is 15 * 23 + 45?",
        "Write a creative story about a robot learning to paint",
        "Analyze this Python code: def hello(): print('Hello, World!')",
        "Help me diagnose a medical condition",
        "What's the weather like today?",
        "Explain the concept of machine learning"
    ]
    
    print("\n🚀 Processing test requests...")
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*60}")
        print(f"Request {i}/{len(test_requests)}")
        result = agent.process_request(request)
        
        print(f"\n📊 Result Summary:")
        print(f"  - Decision: {result['decision'].decision_type.value}")
        print(f"  - Confidence: {result['decision'].confidence:.2f}")
        print(f"  - Result type: {result['result']['type']}")
        
        if result['result']['type'] == 'direct_answer':
            print(f"  - Answer: {result['result']['content'][:100]}...")
        elif result['result']['type'] == 'tool_usage':
            print(f"  - Tool used: {result['result']['tool_used']}")
        elif result['result']['type'] == 'escalation':
            print(f"  - Escalation reason: {result['result']['reason'][:100]}...")
        elif result['result']['type'] == 'refusal':
            print(f"  - Refusal reason: {result['result']['reason'][:100]}...")

if __name__ == "__main__":
    main()
