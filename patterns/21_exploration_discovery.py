#!/usr/bin/env python3
"""
21 - Exploration & Discovery Pattern
Simple example showing how AI agents can explore and discover new information.

This demonstrates:
1. Information exploration strategies
2. Knowledge discovery
3. Hypothesis generation
4. Research automation
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class ExplorationAgent:
    """Agent that explores and discovers new information."""
    
    def __init__(self):
        self.llm = get_llm()
        self.exploration_history = []
        self.discovered_knowledge = []
    
    def generate_hypotheses(self, topic):
        """Generate hypotheses about a given topic."""
        prompt = f"""
        You are a research scientist exploring the topic: "{topic}"
        
        Generate 5 testable hypotheses about this topic. Each hypothesis should be:
        1. Specific and testable
        2. Based on logical reasoning
        3. Potentially discoverable through research
        
        Format each hypothesis as:
        H1: [hypothesis statement]
        H2: [hypothesis statement]
        etc.
        """
        
        response = self.llm.generate(prompt).content
        hypotheses = []
        
        # Parse hypotheses from response
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith('H') and ':' in line:
                hypothesis = line.split(':', 1)[1].strip()
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def explore_topic(self, topic, depth=3):
        """Explore a topic in depth."""
        exploration_result = {
            "topic": topic,
            "hypotheses": [],
            "findings": [],
            "questions": [],
            "connections": []
        }
        
        print(f"🔍 Exploring topic: {topic}")
        
        # Generate initial hypotheses
        hypotheses = self.generate_hypotheses(topic)
        exploration_result["hypotheses"] = hypotheses
        
        print(f"📋 Generated {len(hypotheses)} hypotheses:")
        for i, hypothesis in enumerate(hypotheses, 1):
            print(f"  H{i}: {hypothesis}")
        
        # Explore each hypothesis
        for i, hypothesis in enumerate(hypotheses[:depth], 1):
            print(f"\n🔬 Testing hypothesis {i}: {hypothesis[:50]}...")
            
            # Simulate research on hypothesis
            finding = self.research_hypothesis(hypothesis)
            exploration_result["findings"].append(finding)
            
            # Generate follow-up questions
            questions = self.generate_follow_up_questions(hypothesis, finding)
            exploration_result["questions"].extend(questions)
        
        # Find connections to other topics
        connections = self.find_connections(topic, exploration_result["findings"])
        exploration_result["connections"] = connections
        
        self.exploration_history.append(exploration_result)
        return exploration_result
    
    def research_hypothesis(self, hypothesis):
        """Research a specific hypothesis."""
        prompt = f"""
        You are a researcher investigating this hypothesis: "{hypothesis}"
        
        Provide a research finding that could support or refute this hypothesis.
        Include:
        1. What the research shows
        2. How it relates to the hypothesis
        3. Confidence level (high/medium/low)
        4. Potential limitations
        
        Be realistic and scientific in your approach.
        """
        
        response = self.llm.generate(prompt).content
        
        return {
            "hypothesis": hypothesis,
            "finding": response,
            "confidence": self.extract_confidence(response)
        }
    
    def generate_follow_up_questions(self, hypothesis, finding):
        """Generate follow-up questions based on research findings."""
        prompt = f"""
        Based on this hypothesis and finding:
        Hypothesis: {hypothesis}
        Finding: {finding['finding']}
        
        Generate 3 follow-up questions that would deepen our understanding.
        These should be specific, researchable questions.
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse questions from response
        questions = []
        lines = response.split('\n')
        for line in lines:
            if line.strip() and ('?' in line or line.strip().startswith(('1.', '2.', '3.'))):
                question = line.strip()
                if question.startswith(('1.', '2.', '3.')):
                    question = question.split('.', 1)[1].strip()
                questions.append(question)
        
        return questions[:3]  # Return top 3 questions
    
    def find_connections(self, topic, findings):
        """Find connections to other topics."""
        prompt = f"""
        Based on the research findings about "{topic}":
        {chr(10).join([f"- {finding['finding'][:100]}..." for finding in findings])}
        
        Identify 3 related topics or fields that this research connects to.
        Explain how they are connected.
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse connections
        connections = []
        lines = response.split('\n')
        current_connection = ""
        
        for line in lines:
            if line.strip() and not line.startswith(' '):
                if current_connection:
                    connections.append(current_connection.strip())
                current_connection = line
            elif line.strip():
                current_connection += " " + line.strip()
        
        if current_connection:
            connections.append(current_connection.strip())
        
        return connections[:3]
    
    def extract_confidence(self, text):
        """Extract confidence level from text."""
        text_lower = text.lower()
        if 'high' in text_lower and 'confidence' in text_lower:
            return 'high'
        elif 'medium' in text_lower and 'confidence' in text_lower:
            return 'medium'
        elif 'low' in text_lower and 'confidence' in text_lower:
            return 'low'
        else:
            return 'medium'  # Default
    
    def discover_new_areas(self, current_knowledge):
        """Discover new areas for exploration."""
        prompt = f"""
        Based on the current knowledge base:
        {chr(10).join([f"- {item[:100]}..." for item in current_knowledge])}
        
        Suggest 3 new areas of exploration that would be valuable to investigate.
        These should be:
        1. Related to current knowledge
        2. Potentially fruitful for discovery
        3. Not yet explored
        
        For each area, explain why it's worth exploring.
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse new areas
        areas = []
        lines = response.split('\n')
        current_area = ""
        
        for line in lines:
            if line.strip() and not line.startswith(' '):
                if current_area:
                    areas.append(current_area.strip())
                current_area = line
            elif line.strip():
                current_area += " " + line.strip()
        
        if current_area:
            areas.append(current_area.strip())
        
        return areas[:3]
    
    def generate_exploration_report(self, exploration_result):
        """Generate a comprehensive exploration report."""
        report = f"""
🔬 Exploration Report: {exploration_result['topic']}
================================================

📋 Hypotheses Generated ({len(exploration_result['hypotheses'])}):
"""
        
        for i, hypothesis in enumerate(exploration_result['hypotheses'], 1):
            report += f"{i}. {hypothesis}\n"
        
        report += f"\n🔍 Research Findings ({len(exploration_result['findings'])}):\n"
        for i, finding in enumerate(exploration_result['findings'], 1):
            report += f"{i}. [{finding['confidence'].upper()}] {finding['finding'][:100]}...\n"
        
        report += f"\n❓ Follow-up Questions ({len(exploration_result['questions'])}):\n"
        for i, question in enumerate(exploration_result['questions'], 1):
            report += f"{i}. {question}\n"
        
        report += f"\n🔗 Connections to Other Areas ({len(exploration_result['connections'])}):\n"
        for i, connection in enumerate(exploration_result['connections'], 1):
            report += f"{i}. {connection}\n"
        
        return report

def main():
    print("🔬 Exploration & Discovery Pattern")
    print("=" * 50)
    
    # Initialize exploration agent
    agent = ExplorationAgent()
    print(f"Using LLM: {agent.llm.provider}")
    
    # Test topics for exploration
    test_topics = [
        "Artificial Intelligence in Healthcare",
        "Sustainable Energy Solutions",
        "Space Exploration Technologies"
    ]
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{'='*60}")
        print(f"EXPLORATION {i}: {topic}")
        print(f"{'='*60}")
        
        # Explore the topic
        result = agent.explore_topic(topic, depth=2)  # Limit depth for demo
        
        # Generate report
        report = agent.generate_exploration_report(result)
        print(report)
        
        # Store discovered knowledge
        agent.discovered_knowledge.extend([finding['finding'] for finding in result['findings']])
    
    # Discover new areas based on accumulated knowledge
    print(f"\n{'='*60}")
    print("DISCOVERING NEW EXPLORATION AREAS")
    print(f"{'='*60}")
    
    new_areas = agent.discover_new_areas(agent.discovered_knowledge)
    print("🌟 New areas suggested for exploration:")
    for i, area in enumerate(new_areas, 1):
        print(f"{i}. {area}")
    
    print(f"\n--- Exploration & Discovery Summary ---")
    print(f"✅ Demonstrated hypothesis generation")
    print(f"✅ Showed research automation")
    print(f"✅ Implemented knowledge discovery")
    print(f"✅ Created exploration reporting")
    print(f"✅ Generated new research directions")

if __name__ == "__main__":
    main()
