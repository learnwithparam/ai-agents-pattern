#!/usr/bin/env python3
"""
40 - Meta-Controller Pattern
Supervisory agent that routes tasks to appropriate specialist agents.

The Meta-Controller pattern implements a supervisory agent that analyzes incoming
tasks and routes them to the most appropriate specialist sub-agent from a pool of
experts. This enables adaptive task distribution, load balancing, and specialized
expertise utilization. The meta-controller acts as an intelligent dispatcher that
understands both the requirements of tasks and the capabilities of available agents.

This demonstrates:
1. Task analysis and classification
2. Agent capability assessment and matching
3. Dynamic task routing and load balancing
4. Workflow orchestration and coordination
5. Result aggregation and quality control
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

class TaskCategory(Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    BUSINESS = "business"
    COMMUNICATION = "communication"

@dataclass
class Task:
    """Represents a task to be processed."""
    content: str
    category: TaskCategory
    priority: int
    complexity: str
    required_skills: List[str]
    estimated_duration: int  # in minutes

@dataclass
class AgentCapability:
    """Represents an agent's capabilities."""
    name: str
    skills: List[str]
    specialties: List[TaskCategory]
    availability: bool
    performance_score: float
    current_load: int

class SpecialistAgent:
    """Base class for specialist agents."""
    
    def __init__(self, name: str, skills: List[str], specialties: List[TaskCategory], llm):
        self.name = name
        self.skills = skills
        self.specialties = specialties
        self.llm = llm
        self.availability = True
        self.performance_score = 0.8
        self.current_load = 0
        self.max_load = 5
    
    def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the task."""
        # Check if agent is available
        if not self.availability or self.current_load >= self.max_load:
            return False
        
        # Check if agent has required skills
        has_skills = all(skill in self.skills for skill in task.required_skills)
        
        # Check if task category matches specialties
        matches_specialty = task.category in self.specialties
        
        return has_skills and (matches_specialty or len(task.required_skills) == 0)
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task and return results."""
        # Override in subclasses
        return {
            "agent": self.name,
            "task": task.content,
            "result": "Task processed",
            "confidence": 0.5,
            "time_taken": 1.0
        }

class ResearchAgent(SpecialistAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, llm):
        super().__init__(
            name="Research Agent",
            skills=["research", "analysis", "data_gathering", "fact_checking", "synthesis"],
            specialties=[TaskCategory.RESEARCH, TaskCategory.ANALYSIS],
            llm=llm
        )
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """Process research tasks."""
        prompt = f"""
        As a research specialist, handle this task: {task.content}
        
        Task category: {task.category.value}
        Priority: {task.priority}
        Complexity: {task.complexity}
        
        Provide:
        1. Comprehensive research findings
        2. Key insights and data points
        3. Sources and references
        4. Confidence level in your research
        5. Recommendations for next steps
        
        Format as JSON:
        {{
            "research_findings": "detailed findings",
            "key_insights": ["insight1", "insight2", "insight3"],
            "sources": ["source1", "source2"],
            "confidence": 0.8,
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
            
            data = json.loads(json_str)
            return {
                "agent": self.name,
                "task": task.content,
                "result": data.get("research_findings", "Research completed"),
                "confidence": data.get("confidence", 0.7),
                "time_taken": random.uniform(2.0, 5.0),
                "insights": data.get("key_insights", []),
                "sources": data.get("sources", []),
                "recommendations": data.get("recommendations", [])
            }
        except json.JSONDecodeError:
            return {
                "agent": self.name,
                "task": task.content,
                "result": "Research completed with basic findings",
                "confidence": 0.6,
                "time_taken": random.uniform(2.0, 5.0),
                "insights": ["Research completed"],
                "sources": ["General knowledge"],
                "recommendations": ["Further research needed"]
            }

class CreativeAgent(SpecialistAgent):
    """Agent specialized in creative tasks and ideation."""
    
    def __init__(self, llm):
        super().__init__(
            name="Creative Agent",
            skills=["creativity", "ideation", "design", "innovation", "brainstorming"],
            specialties=[TaskCategory.CREATIVE, TaskCategory.COMMUNICATION],
            llm=llm
        )
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """Process creative tasks."""
        prompt = f"""
        As a creative specialist, handle this task: {task.content}
        
        Task category: {task.category.value}
        Priority: {task.priority}
        Complexity: {task.complexity}
        
        Provide:
        1. Creative solutions and ideas
        2. Innovative approaches
        3. Design concepts if applicable
        4. Confidence level in your creativity
        5. Implementation suggestions
        
        Format as JSON:
        {{
            "creative_solutions": "detailed creative solutions",
            "ideas": ["idea1", "idea2", "idea3"],
            "innovations": ["innovation1", "innovation2"],
            "confidence": 0.8,
            "implementation": ["step1", "step2"]
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
            
            data = json.loads(json_str)
            return {
                "agent": self.name,
                "task": task.content,
                "result": data.get("creative_solutions", "Creative solutions generated"),
                "confidence": data.get("confidence", 0.7),
                "time_taken": random.uniform(2.5, 6.0),
                "ideas": data.get("ideas", []),
                "innovations": data.get("innovations", []),
                "implementation": data.get("implementation", [])
            }
        except json.JSONDecodeError:
            return {
                "agent": self.name,
                "task": task.content,
                "result": "Creative solutions generated",
                "confidence": 0.6,
                "time_taken": random.uniform(2.5, 6.0),
                "ideas": ["Creative ideas generated"],
                "innovations": ["Innovative approaches"],
                "implementation": ["Implementation steps provided"]
            }

class TechnicalAgent(SpecialistAgent):
    """Agent specialized in technical tasks."""
    
    def __init__(self, llm):
        super().__init__(
            name="Technical Agent",
            skills=["programming", "analysis", "problem_solving", "debugging", "optimization"],
            specialties=[TaskCategory.TECHNICAL, TaskCategory.ANALYSIS],
            llm=llm
        )
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """Process technical tasks."""
        prompt = f"""
        As a technical specialist, handle this task: {task.content}
        
        Task category: {task.category.value}
        Priority: {task.priority}
        Complexity: {task.complexity}
        
        Provide:
        1. Technical analysis and solution
        2. Implementation details
        3. Code examples if applicable
        4. Technical considerations
        5. Confidence level in your solution
        
        Format as JSON:
        {{
            "technical_solution": "detailed technical solution",
            "implementation": "implementation details",
            "code_examples": ["example1", "example2"],
            "considerations": ["consideration1", "consideration2"],
            "confidence": 0.8
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
            
            data = json.loads(json_str)
            return {
                "agent": self.name,
                "task": task.content,
                "result": data.get("technical_solution", "Technical solution provided"),
                "confidence": data.get("confidence", 0.7),
                "time_taken": random.uniform(1.5, 4.0),
                "implementation": data.get("implementation", ""),
                "code_examples": data.get("code_examples", []),
                "considerations": data.get("considerations", [])
            }
        except json.JSONDecodeError:
            return {
                "agent": self.name,
                "task": task.content,
                "result": "Technical solution provided",
                "confidence": 0.6,
                "time_taken": random.uniform(1.5, 4.0),
                "implementation": "Basic implementation provided",
                "code_examples": ["Code examples available"],
                "considerations": ["Technical considerations noted"]
            }

class MetaController:
    """Meta-controller that routes tasks to appropriate agents."""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = [
            ResearchAgent(llm),
            CreativeAgent(llm),
            TechnicalAgent(llm)
        ]
        self.task_history = []
        self.performance_metrics = {}
    
    def analyze_task(self, task_content: str) -> Task:
        """Analyze a task to determine its characteristics."""
        prompt = f"""
        Analyze this task and classify it: {task_content}
        
        Determine:
        1. Category (research, analysis, creative, technical, business, communication)
        2. Priority (1-5, where 5 is highest)
        3. Complexity (low, medium, high)
        4. Required skills (list of skills needed)
        5. Estimated duration in minutes
        
        Format as JSON:
        {{
            "category": "research",
            "priority": 4,
            "complexity": "medium",
            "required_skills": ["research", "analysis"],
            "estimated_duration": 30
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
            
            data = json.loads(json_str)
            return Task(
                content=task_content,
                category=TaskCategory(data.get("category", "research")),
                priority=data.get("priority", 3),
                complexity=data.get("complexity", "medium"),
                required_skills=data.get("required_skills", []),
                estimated_duration=data.get("estimated_duration", 30)
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback task classification
            return Task(
                content=task_content,
                category=TaskCategory.RESEARCH,
                priority=3,
                complexity="medium",
                required_skills=[],
                estimated_duration=30
            )
    
    def select_agent(self, task: Task) -> Optional[SpecialistAgent]:
        """Select the best agent for the task."""
        available_agents = [agent for agent in self.agents if agent.can_handle(task)]
        
        if not available_agents:
            return None
        
        # Score agents based on multiple factors
        best_agent = None
        best_score = -1
        
        for agent in available_agents:
            score = 0
            
            # Skill match score (40% weight)
            skill_match = len(set(task.required_skills) & set(agent.skills)) / max(len(task.required_skills), 1)
            score += skill_match * 0.4
            
            # Specialty match score (30% weight)
            specialty_match = task.category in agent.specialties
            score += 0.3 if specialty_match else 0.1
            
            # Performance score (20% weight)
            score += agent.performance_score * 0.2
            
            # Load balancing (10% weight)
            load_factor = 1 - (agent.current_load / agent.max_load)
            score += load_factor * 0.1
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    def process_task(self, task_content: str) -> Dict[str, Any]:
        """Process a task using the meta-controller."""
        print(f"🎯 Processing Task: {task_content}")
        print("=" * 50)
        
        # Analyze task
        print("\n📋 Analyzing task...")
        task = self.analyze_task(task_content)
        print(f"Category: {task.category.value}")
        print(f"Priority: {task.priority}")
        print(f"Complexity: {task.complexity}")
        print(f"Required skills: {', '.join(task.required_skills)}")
        print(f"Estimated duration: {task.estimated_duration} minutes")
        
        # Select agent
        print(f"\n🤖 Selecting agent...")
        selected_agent = self.select_agent(task)
        
        if not selected_agent:
            return {
                "task": task,
                "status": "failed",
                "reason": "No suitable agent available",
                "result": None
            }
        
        print(f"Selected: {selected_agent.name}")
        print(f"Skills: {', '.join(selected_agent.skills)}")
        print(f"Specialties: {[s.value for s in selected_agent.specialties]}")
        print(f"Current load: {selected_agent.current_load}/{selected_agent.max_load}")
        
        # Process task
        print(f"\n⚡ Processing with {selected_agent.name}...")
        selected_agent.current_load += 1
        result = selected_agent.process_task(task)
        selected_agent.current_load -= 1
        
        # Update performance score based on result
        if result["confidence"] > 0.7:
            selected_agent.performance_score = min(1.0, selected_agent.performance_score + 0.05)
        else:
            selected_agent.performance_score = max(0.1, selected_agent.performance_score - 0.02)
        
        # Store in history
        self.task_history.append({
            "task": task,
            "agent": selected_agent.name,
            "result": result,
            "timestamp": len(self.task_history)
        })
        
        print(f"✅ Task completed by {selected_agent.name}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Time taken: {result['time_taken']:.1f} minutes")
        
        return {
            "task": task,
            "status": "completed",
            "agent": selected_agent.name,
            "result": result,
            "performance_score": selected_agent.performance_score
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "total_agents": len(self.agents),
            "available_agents": len([a for a in self.agents if a.availability]),
            "tasks_processed": len(self.task_history),
            "agent_performance": {agent.name: agent.performance_score for agent in self.agents},
            "agent_loads": {agent.name: f"{agent.current_load}/{agent.max_load}" for agent in self.agents},
            "recent_tasks": self.task_history[-5:] if self.task_history else []
        }

def main():
    print("🎛️ Meta-Controller Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create meta-controller
    controller = MetaController(llm)
    
    # Test tasks
    tasks = [
        "Research the latest trends in artificial intelligence and machine learning",
        "Create a creative marketing campaign for a new mobile app",
        "Write a Python script to analyze sales data and generate reports",
        "Design a user interface for an e-commerce website",
        "Analyze the competitive landscape for electric vehicles",
        "Develop a technical architecture for a microservices application"
    ]
    
    for task in tasks:
        print(f"\n{'='*60}")
        result = controller.process_task(task)
        
        if result["status"] == "completed":
            print(f"\n📊 Task Summary:")
            print(f"  - Agent: {result['agent']}")
            print(f"  - Confidence: {result['result']['confidence']:.2f}")
            print(f"  - Time: {result['result']['time_taken']:.1f} minutes")
            print(f"  - Result: {str(result['result']['result'])[:100]}...")
        else:
            print(f"❌ Task failed: {result['reason']}")
    
    # Show system status
    print(f"\n{'='*60}")
    print("📈 System Status:")
    status = controller.get_system_status()
    print(f"  - Total agents: {status['total_agents']}")
    print(f"  - Available agents: {status['available_agents']}")
    print(f"  - Tasks processed: {status['tasks_processed']}")
    print(f"  - Agent performance: {status['agent_performance']}")
    print(f"  - Agent loads: {status['agent_loads']}")

if __name__ == "__main__":
    main()
