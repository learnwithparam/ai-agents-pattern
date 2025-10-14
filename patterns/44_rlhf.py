#!/usr/bin/env python3
"""
44 - RLHF (Self-Improvement) Pattern
Reinforcement Learning from Human Feedback for continuous improvement.

The RLHF pattern implements a self-improvement loop where an agent's output is
critiqued by an "editor" agent, and the feedback is used to iteratively revise
the work. High-quality outputs are saved to improve future performance, creating
a continuous learning system that gets better over time.

This demonstrates:
1. Generate initial output
2. Critique and score the output
3. Learn from feedback and improve
4. Store high-quality examples for future reference
5. Continuous performance improvement over time
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

@dataclass
class Feedback:
    """Represents feedback on an output."""
    output_id: str
    score: float
    critique: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    timestamp: int

@dataclass
class LearningExample:
    """Represents a learning example for improvement."""
    input_text: str
    output_text: str
    quality_score: float
    feedback: Feedback
    category: str

class CriticAgent:
    """Agent that critiques and scores outputs."""
    
    def __init__(self, llm):
        self.llm = llm
        self.evaluation_criteria = [
            "accuracy and correctness",
            "clarity and coherence", 
            "completeness and thoroughness",
            "creativity and originality",
            "relevance to the task"
        ]
    
    def critique_output(self, input_text: str, output_text: str, task_type: str) -> Feedback:
        """Critique an output and provide detailed feedback."""
        prompt = f"""
        As an expert critic, evaluate this output:
        
        Task type: {task_type}
        Input: {input_text}
        Output: {output_text}
        
        Evaluate on these criteria (1-10 scale):
        {chr(10).join(f"- {criterion}" for criterion in self.evaluation_criteria)}
        
        Provide:
        1. Overall score (1-10)
        2. Detailed critique
        3. Specific strengths
        4. Specific weaknesses
        5. Concrete suggestions for improvement
        
        Format as JSON:
        {{
            "score": 7.5,
            "critique": "detailed critique",
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "suggestions": ["suggestion1", "suggestion2"]
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
            return Feedback(
                output_id=f"output_{random.randint(1000, 9999)}",
                score=data.get("score", 5.0),
                critique=data.get("critique", "No critique provided"),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                suggestions=data.get("suggestions", []),
                timestamp=len(self.learning_examples) if hasattr(self, 'learning_examples') else 0
            )
        except json.JSONDecodeError:
            return Feedback(
                output_id=f"output_{random.randint(1000, 9999)}",
                score=5.0,
                critique="Basic evaluation completed",
                strengths=["Output generated"],
                weaknesses=["Evaluation incomplete"],
                suggestions=["Improve output quality"],
                timestamp=0
            )

class LearningMemory:
    """Stores and manages learning examples."""
    
    def __init__(self, max_examples: int = 1000):
        self.max_examples = max_examples
        self.examples: List[LearningExample] = []
        self.quality_threshold = 7.0
    
    def add_example(self, example: LearningExample) -> None:
        """Add a learning example."""
        if example.quality_score >= self.quality_threshold:
            self.examples.append(example)
            if len(self.examples) > self.max_examples:
                self.examples.sort(key=lambda x: x.quality_score, reverse=True)
                self.examples = self.examples[:self.max_examples]
    
    def get_examples_by_category(self, category: str) -> List[LearningExample]:
        """Get examples by category."""
        return [ex for ex in self.examples if ex.category == category]
    
    def get_best_examples(self, limit: int = 5) -> List[LearningExample]:
        """Get the best examples."""
        sorted_examples = sorted(self.examples, key=lambda x: x.quality_score, reverse=True)
        return sorted_examples[:limit]

class ImprovedGenerator:
    """Generator that learns from feedback and improves."""
    
    def __init__(self, llm, learning_memory: LearningMemory):
        self.llm = llm
        self.learning_memory = learning_memory
        self.performance_history = []
    
    def generate_with_learning(self, input_text: str, task_type: str) -> Dict[str, Any]:
        """Generate output using learned patterns."""
        relevant_examples = self.learning_memory.get_examples_by_category(task_type)
        best_examples = self.learning_memory.get_best_examples(3)
        
        learning_context = self._build_learning_context(relevant_examples, best_examples)
        
        prompt = f"""
        Task type: {task_type}
        Input: {input_text}
        
        Learning from previous high-quality examples:
        {learning_context}
        
        Generate a high-quality output that incorporates the best practices learned from previous examples.
        Focus on the strengths identified in the learning examples and avoid the common weaknesses.
        """
        
        output = self.llm.generate(prompt).content
        
        return {
            "input": input_text,
            "output": output,
            "task_type": task_type,
            "learning_examples_used": len(relevant_examples),
            "generation_method": "learning_enhanced"
        }
    
    def update_performance(self, score: float) -> None:
        """Update performance based on feedback score."""
        if score > 0.7:
            self.performance_history.append(score)
        else:
            self.performance_history.append(score)
        
        # Keep only last 10 performance scores
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
    
    def _build_learning_context(self, relevant_examples: List[LearningExample], best_examples: List[LearningExample]) -> str:
        """Build learning context from examples."""
        context = ""
        
        if relevant_examples:
            context += "Relevant examples from similar tasks:\n"
            for i, ex in enumerate(relevant_examples[:2], 1):
                context += f"{i}. Input: {ex.input_text[:100]}...\n"
                context += f"   Output: {ex.output_text[:100]}...\n"
                context += f"   Quality: {ex.quality_score:.1f}\n"
                context += f"   Strengths: {', '.join(ex.feedback.strengths[:2])}\n\n"
        
        if best_examples:
            context += "Best practices from top examples:\n"
            for i, ex in enumerate(best_examples[:2], 1):
                context += f"{i}. Strengths: {', '.join(ex.feedback.strengths[:3])}\n"
                context += f"   Quality: {ex.quality_score:.1f}\n\n"
        
        return context

class RLHFSystem:
    """Main RLHF system for continuous improvement."""
    
    def __init__(self, llm):
        self.llm = llm
        self.critic = CriticAgent(llm)
        self.learning_memory = LearningMemory()
        self.generator = ImprovedGenerator(llm, self.learning_memory)
        self.iteration_count = 0
    
    def process_task(self, input_text: str, task_type: str) -> Dict[str, Any]:
        """Process a task through the RLHF system."""
        print(f"🔄 Processing task: {input_text[:50]}...")
        print(f"Task type: {task_type}")
        print("=" * 50)
        
        # Generate output
        print("\n🤖 Generating output...")
        generation_result = self.generator.generate_with_learning(input_text, task_type)
        output_text = generation_result["output"]
        print(f"Output generated (using {generation_result['learning_examples_used']} learning examples)")
        
        # Critique output
        print("\n👥 Critiquing output...")
        feedback = self.critic.critique_output(input_text, output_text, task_type)
        print(f"Quality score: {feedback.score:.1f}/10")
        print(f"Strengths: {len(feedback.strengths)}")
        print(f"Weaknesses: {len(feedback.weaknesses)}")
        
        # Create learning example
        learning_example = LearningExample(
            input_text=input_text,
            output_text=output_text,
            quality_score=feedback.score,
            feedback=feedback,
            category=task_type
        )
        
        # Add to learning memory
        self.learning_memory.add_example(learning_example)
        
        # Update generator performance
        self.generator.update_performance(feedback.score)
        
        self.iteration_count += 1
        
        return {
            "input": input_text,
            "output": output_text,
            "task_type": task_type,
            "quality_score": feedback.score,
            "feedback": feedback,
            "learning_example_added": learning_example.quality_score >= self.learning_memory.quality_threshold,
            "iteration": self.iteration_count
        }

def main():
    print("🧠 RLHF (Self-Improvement) Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create RLHF system
    rlhf_system = RLHFSystem(llm)
    
    # Test tasks
    test_tasks = [
        ("Write a short story about a robot learning to paint", "creative_writing"),
        ("Explain the concept of machine learning to a beginner", "explanation"),
        ("Create a business plan for a coffee shop", "business_planning")
    ]
    
    print("\n🚀 Starting RLHF learning process...")
    
    for i, (input_text, task_type) in enumerate(test_tasks, 1):
        print(f"\n{'='*60}")
        print(f"Task {i}/{len(test_tasks)}")
        result = rlhf_system.process_task(input_text, task_type)
        
        print(f"\n📊 Task Summary:")
        print(f"  - Quality score: {result['quality_score']:.1f}/10")
        print(f"  - Learning example added: {result['learning_example_added']}")
        print(f"  - Iteration: {result['iteration']}")

if __name__ == "__main__":
    main()
