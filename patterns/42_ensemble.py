#!/usr/bin/env python3
"""
42 - Ensemble Pattern
Multiple independent agents analyze problems from different perspectives.

The Ensemble pattern implements multiple independent agents that analyze the same
problem from different perspectives, with a final aggregator agent that synthesizes
their outputs for a more robust, less biased conclusion. This approach is particularly
effective for high-stakes decision support, fact-checking, and any domain where
diverse perspectives can lead to better outcomes.

This demonstrates:
1. Multiple specialized agents with different viewpoints
2. Independent analysis of the same problem
3. Aggregation of diverse perspectives
4. Robust decision-making through consensus
5. Bias reduction through multiple perspectives
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

@dataclass
class AgentAnalysis:
    """Represents an analysis from a single agent."""
    agent_name: str
    perspective: str
    analysis: str
    confidence: float
    key_points: List[str]
    recommendations: List[str]

class SpecialistAgent:
    """Base class for specialist agents in the ensemble."""
    
    def __init__(self, name: str, perspective: str, llm):
        self.name = name
        self.perspective = perspective
        self.llm = llm
    
    def analyze(self, problem: str) -> AgentAnalysis:
        """Analyze the problem from this agent's perspective."""
        # Override in subclasses
        return AgentAnalysis(
            agent_name=self.name,
            perspective=self.perspective,
            analysis="No analysis provided",
            confidence=0.0,
            key_points=[],
            recommendations=[]
        )

class TechnicalAgent(SpecialistAgent):
    """Agent focused on technical and implementation aspects."""
    
    def __init__(self, llm):
        super().__init__("Technical Expert", "Technical Implementation", llm)
    
    def analyze(self, problem: str) -> AgentAnalysis:
        """Analyze from technical perspective."""
        prompt = f"""
        As a technical expert, analyze this problem: {problem}
        
        Focus on:
        1. Technical feasibility and implementation challenges
        2. Required technologies, tools, or systems
        3. Performance considerations and scalability
        4. Technical risks and mitigation strategies
        5. Development timeline and resource requirements
        
        Provide:
        - Detailed technical analysis
        - Key technical points (3-5 points)
        - Specific technical recommendations
        - Confidence level (0-1) in your analysis
        
        Format as JSON:
        {{
            "analysis": "detailed technical analysis",
            "key_points": ["point1", "point2", "point3"],
            "recommendations": ["rec1", "rec2", "rec3"],
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
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis=data.get("analysis", "No analysis"),
                confidence=data.get("confidence", 0.5),
                key_points=data.get("key_points", []),
                recommendations=data.get("recommendations", [])
            )
        except json.JSONDecodeError:
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis="Technical analysis failed to parse",
                confidence=0.3,
                key_points=["Technical analysis unavailable"],
                recommendations=["Consult technical expert"]
            )

class BusinessAgent(SpecialistAgent):
    """Agent focused on business and commercial aspects."""
    
    def __init__(self, llm):
        super().__init__("Business Expert", "Business Strategy", llm)
    
    def analyze(self, problem: str) -> AgentAnalysis:
        """Analyze from business perspective."""
        prompt = f"""
        As a business expert, analyze this problem: {problem}
        
        Focus on:
        1. Market opportunities and competitive landscape
        2. Financial implications and ROI considerations
        3. Business model and revenue potential
        4. Customer needs and market demand
        5. Strategic advantages and positioning
        
        Provide:
        - Detailed business analysis
        - Key business points (3-5 points)
        - Specific business recommendations
        - Confidence level (0-1) in your analysis
        
        Format as JSON:
        {{
            "analysis": "detailed business analysis",
            "key_points": ["point1", "point2", "point3"],
            "recommendations": ["rec1", "rec2", "rec3"],
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
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis=data.get("analysis", "No analysis"),
                confidence=data.get("confidence", 0.5),
                key_points=data.get("key_points", []),
                recommendations=data.get("recommendations", [])
            )
        except json.JSONDecodeError:
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis="Business analysis failed to parse",
                confidence=0.3,
                key_points=["Business analysis unavailable"],
                recommendations=["Consult business expert"]
            )

class UserExperienceAgent(SpecialistAgent):
    """Agent focused on user experience and usability."""
    
    def __init__(self, llm):
        super().__init__("UX Expert", "User Experience", llm)
    
    def analyze(self, problem: str) -> AgentAnalysis:
        """Analyze from UX perspective."""
        prompt = f"""
        As a UX expert, analyze this problem: {problem}
        
        Focus on:
        1. User needs, pain points, and behaviors
        2. Usability and accessibility considerations
        3. User journey and interaction design
        4. User feedback and testing requirements
        5. Design principles and best practices
        
        Provide:
        - Detailed UX analysis
        - Key UX points (3-5 points)
        - Specific UX recommendations
        - Confidence level (0-1) in your analysis
        
        Format as JSON:
        {{
            "analysis": "detailed UX analysis",
            "key_points": ["point1", "point2", "point3"],
            "recommendations": ["rec1", "rec2", "rec3"],
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
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis=data.get("analysis", "No analysis"),
                confidence=data.get("confidence", 0.5),
                key_points=data.get("key_points", []),
                recommendations=data.get("recommendations", [])
            )
        except json.JSONDecodeError:
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis="UX analysis failed to parse",
                confidence=0.3,
                key_points=["UX analysis unavailable"],
                recommendations=["Consult UX expert"]
            )

class RiskAgent(SpecialistAgent):
    """Agent focused on risk assessment and mitigation."""
    
    def __init__(self, llm):
        super().__init__("Risk Expert", "Risk Assessment", llm)
    
    def analyze(self, problem: str) -> AgentAnalysis:
        """Analyze from risk perspective."""
        prompt = f"""
        As a risk expert, analyze this problem: {problem}
        
        Focus on:
        1. Potential risks and vulnerabilities
        2. Risk likelihood and impact assessment
        3. Mitigation strategies and controls
        4. Compliance and regulatory considerations
        5. Contingency planning and recovery
        
        Provide:
        - Detailed risk analysis
        - Key risk points (3-5 points)
        - Specific risk recommendations
        - Confidence level (0-1) in your analysis
        
        Format as JSON:
        {{
            "analysis": "detailed risk analysis",
            "key_points": ["point1", "point2", "point3"],
            "recommendations": ["rec1", "rec2", "rec3"],
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
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis=data.get("analysis", "No analysis"),
                confidence=data.get("confidence", 0.5),
                key_points=data.get("key_points", []),
                recommendations=data.get("recommendations", [])
            )
        except json.JSONDecodeError:
            return AgentAnalysis(
                agent_name=self.name,
                perspective=self.perspective,
                analysis="Risk analysis failed to parse",
                confidence=0.3,
                key_points=["Risk analysis unavailable"],
                recommendations=["Consult risk expert"]
            )

class EnsembleSystem:
    """Main ensemble system that coordinates multiple agents."""
    
    def __init__(self, llm):
        self.llm = llm
        self.agents = [
            TechnicalAgent(llm),
            BusinessAgent(llm),
            UserExperienceAgent(llm),
            RiskAgent(llm)
        ]
    
    def analyze_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze problem using ensemble of agents."""
        print(f"🎯 Problem: {problem}")
        print("=" * 50)
        
        print("\n👥 Ensemble Analysis Starting")
        print("-" * 30)
        
        # Get analysis from each agent
        analyses = []
        for agent in self.agents:
            print(f"\nAnalyzing with {agent.name} ({agent.perspective})...")
            analysis = agent.analyze(problem)
            analyses.append(analysis)
            print(f"Confidence: {analysis.confidence:.2f}")
            print(f"Key points: {len(analysis.key_points)}")
        
        # Aggregate results
        aggregated_result = self._aggregate_analyses(problem, analyses)
        
        return {
            "problem": problem,
            "individual_analyses": analyses,
            "aggregated_result": aggregated_result
        }
    
    def _aggregate_analyses(self, problem: str, analyses: List[AgentAnalysis]) -> Dict[str, Any]:
        """Aggregate individual analyses into final result."""
        # Collect all key points and recommendations
        all_key_points = []
        all_recommendations = []
        
        for analysis in analyses:
            all_key_points.extend(analysis.key_points)
            all_recommendations.extend(analysis.recommendations)
        
        # Create aggregation prompt
        analyses_text = ""
        for analysis in analyses:
            analyses_text += f"\n{analysis.agent_name} ({analysis.perspective}):\n"
            analyses_text += f"Analysis: {analysis.analysis}\n"
            analyses_text += f"Key Points: {', '.join(str(point) for point in analysis.key_points)}\n"
            analyses_text += f"Recommendations: {', '.join(str(rec) for rec in analysis.recommendations)}\n"
            analyses_text += f"Confidence: {analysis.confidence:.2f}\n"
        
        prompt = f"""
        Problem: {problem}
        
        Individual Agent Analyses:
        {analyses_text}
        
        As an expert aggregator, synthesize these diverse perspectives into a comprehensive solution:
        
        1. Identify common themes and consensus points
        2. Highlight areas of disagreement or tension
        3. Prioritize recommendations based on confidence and feasibility
        4. Create an integrated action plan
        5. Note any gaps or areas needing further investigation
        
        Provide:
        - Executive summary
        - Integrated analysis
        - Prioritized recommendations
        - Implementation roadmap
        - Risk assessment
        - Success metrics
        """
        
        aggregated_analysis = self.llm.generate(prompt).content
        
        # Calculate consensus metrics
        avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        consensus_score = self._calculate_consensus(analyses)
        
        return {
            "executive_summary": aggregated_analysis,
            "consensus_score": consensus_score,
            "average_confidence": avg_confidence,
            "total_key_points": len(all_key_points),
            "total_recommendations": len(all_recommendations),
            "agent_count": len(analyses)
        }
    
    def _calculate_consensus(self, analyses: List[AgentAnalysis]) -> float:
        """Calculate consensus score between analyses."""
        # Simple consensus based on confidence variance
        confidences = [a.confidence for a in analyses]
        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
        
        # Lower variance = higher consensus
        consensus = max(0, 1 - variance)
        return consensus

def main():
    print("👥 Ensemble Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create ensemble system
    ensemble = EnsembleSystem(llm)
    
    # Test problems
    problems = [
        "How should a company implement a remote work policy?",
        "What are the best strategies for launching a new mobile app?",
        "How can a business improve its customer retention rates?"
    ]
    
    for problem in problems:
        print(f"\n{'='*60}")
        result = ensemble.analyze_problem(problem)
        
        print(f"\n📊 Ensemble Summary:")
        print(f"  - Agents consulted: {result['aggregated_result']['agent_count']}")
        print(f"  - Average confidence: {result['aggregated_result']['average_confidence']:.2f}")
        print(f"  - Consensus score: {result['aggregated_result']['consensus_score']:.2f}")
        print(f"  - Total key points: {result['aggregated_result']['total_key_points']}")
        print(f"  - Total recommendations: {result['aggregated_result']['total_recommendations']}")
        
        print(f"\n🎯 Integrated Analysis:")
        print(result['aggregated_result']['executive_summary'][:300] + "...")

if __name__ == "__main__":
    main()
