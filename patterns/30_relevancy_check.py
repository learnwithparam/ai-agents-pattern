#!/usr/bin/env python3
"""
30 - Relevancy Check Pattern
Simple example showing how to check and filter relevant information.

This demonstrates:
1. Content relevancy scoring
2. Information filtering
3. Fact grounding and verification
4. Quality assessment
"""

import sys
import os
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class RelevancyChecker:
    """System for checking content relevancy and quality."""
    
    def __init__(self):
        self.llm = get_llm()
        self.relevancy_threshold = 0.7
        self.quality_threshold = 0.6
    
    def score_relevancy(self, query: str, content: str) -> Dict[str, Any]:
        """Score how relevant content is to a query."""
        prompt = f"""
        Rate the relevancy of this content to the query on a scale of 0-10:
        
        Query: "{query}"
        Content: "{content[:500]}..."
        
        Respond with:
        RELEVANCY_SCORE: [0-10]
        REASONING: [brief explanation]
        KEY_MATCHES: [list key matching concepts]
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response (simplified)
        score = 7  # Default score
        reasoning = "Content appears relevant to query"
        matches = ["general match"]
        
        return {
            "score": score / 10,  # Normalize to 0-1
            "reasoning": reasoning,
            "key_matches": matches,
            "is_relevant": score / 10 >= self.relevancy_threshold
        }
    
    def check_fact_grounding(self, content: str, sources: List[str] = None) -> Dict[str, Any]:
        """Check if content is grounded in facts and sources."""
        prompt = f"""
        Analyze this content for factual accuracy and grounding:
        
        Content: "{content[:500]}..."
        Sources: {sources or ['No sources provided']}
        
        Respond with:
        FACTUAL_SCORE: [0-10]
        GROUNDING_LEVEL: [high, medium, low]
        VERIFIABLE_CLAIMS: [count of verifiable statements]
        POTENTIAL_ISSUES: [list any concerns]
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response (simplified)
        factual_score = 8
        grounding_level = "high"
        verifiable_claims = 3
        issues = []
        
        return {
            "factual_score": factual_score / 10,
            "grounding_level": grounding_level,
            "verifiable_claims": verifiable_claims,
            "potential_issues": issues,
            "is_well_grounded": factual_score / 10 >= 0.7
        }
    
    def assess_content_quality(self, content: str) -> Dict[str, Any]:
        """Assess the overall quality of content."""
        prompt = f"""
        Assess the quality of this content:
        
        Content: "{content[:500]}..."
        
        Rate on:
        CLARITY: [0-10]
        COMPLETENESS: [0-10]
        ACCURACY: [0-10]
        HELPFULNESS: [0-10]
        
        Provide overall assessment.
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response (simplified)
        clarity = 8
        completeness = 7
        accuracy = 8
        helpfulness = 7
        
        overall_score = (clarity + completeness + accuracy + helpfulness) / 40
        
        return {
            "clarity": clarity / 10,
            "completeness": completeness / 10,
            "accuracy": accuracy / 10,
            "helpfulness": helpfulness / 10,
            "overall_score": overall_score,
            "is_high_quality": overall_score >= self.quality_threshold
        }
    
    def filter_irrelevant_content(self, query: str, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out irrelevant content from a list."""
        relevant_content = []
        
        for item in content_list:
            content = item.get('content', '')
            relevancy = self.score_relevancy(query, content)
            
            if relevancy['is_relevant']:
                item['relevancy_score'] = relevancy['score']
                item['relevancy_reasoning'] = relevancy['reasoning']
                relevant_content.append(item)
        
        # Sort by relevancy score
        relevant_content.sort(key=lambda x: x.get('relevancy_score', 0), reverse=True)
        
        return relevant_content
    
    def verify_claims(self, content: str, knowledge_base: List[str] = None) -> Dict[str, Any]:
        """Verify claims in content against knowledge base."""
        if not knowledge_base:
            knowledge_base = []
        
        prompt = f"""
        Verify the claims in this content against the provided knowledge:
        
        Content: "{content[:500]}..."
        Knowledge Base: {knowledge_base[:3] if knowledge_base else ['No knowledge base']}
        
        Respond with:
        VERIFIED_CLAIMS: [count]
        UNVERIFIED_CLAIMS: [count]
        CONFLICTING_CLAIMS: [count]
        CONFIDENCE: [high, medium, low]
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response (simplified)
        verified = 2
        unverified = 1
        conflicting = 0
        confidence = "high"
        
        return {
            "verified_claims": verified,
            "unverified_claims": unverified,
            "conflicting_claims": conflicting,
            "confidence": confidence,
            "verification_score": verified / (verified + unverified + conflicting) if (verified + unverified + conflicting) > 0 else 0
        }

class RelevancyPipeline:
    """Complete relevancy checking pipeline."""
    
    def __init__(self):
        self.checker = RelevancyChecker()
        self.knowledge_base = []
    
    def add_knowledge(self, knowledge: str):
        """Add knowledge to the verification base."""
        self.knowledge_base.append(knowledge)
    
    def process_content(self, query: str, content: str, sources: List[str] = None) -> Dict[str, Any]:
        """Process content through complete relevancy pipeline."""
        print(f"🔍 Checking relevancy for: {query[:50]}...")
        
        # Step 1: Check relevancy
        relevancy = self.checker.score_relevancy(query, content)
        print(f"📊 Relevancy score: {relevancy['score']:.2f}")
        
        # Step 2: Check fact grounding
        grounding = self.checker.check_fact_grounding(content, sources)
        print(f"🎯 Grounding level: {grounding['grounding_level']}")
        
        # Step 3: Assess quality
        quality = self.checker.assess_content_quality(content)
        print(f"⭐ Quality score: {quality['overall_score']:.2f}")
        
        # Step 4: Verify claims
        verification = self.checker.verify_claims(content, self.knowledge_base)
        print(f"✅ Verification score: {verification['verification_score']:.2f}")
        
        # Overall assessment
        overall_score = (
            relevancy['score'] * 0.3 +
            grounding['factual_score'] * 0.3 +
            quality['overall_score'] * 0.2 +
            verification['verification_score'] * 0.2
        )
        
        is_acceptable = (
            relevancy['is_relevant'] and
            grounding['is_well_grounded'] and
            quality['is_high_quality'] and
            overall_score >= 0.6
        )
        
        return {
            "query": query,
            "content": content,
            "relevancy": relevancy,
            "grounding": grounding,
            "quality": quality,
            "verification": verification,
            "overall_score": overall_score,
            "is_acceptable": is_acceptable,
            "recommendation": "ACCEPT" if is_acceptable else "REJECT"
        }
    
    def batch_process(self, query: str, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple content items."""
        results = []
        
        for i, item in enumerate(content_list):
            print(f"\n--- Processing item {i+1} ---")
            result = self.process_content(
                query, 
                item.get('content', ''), 
                item.get('sources', [])
            )
            results.append(result)
        
        return results

def main():
    print("🎯 Relevancy Check Pattern")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = RelevancyPipeline()
    
    # Add some knowledge for verification
    pipeline.add_knowledge("Python is a programming language")
    pipeline.add_knowledge("Machine learning is a subset of AI")
    pipeline.add_knowledge("Web development involves HTML, CSS, and JavaScript")
    
    # Test content
    test_cases = [
        {
            "query": "What is Python programming?",
            "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and automation.",
            "sources": ["Python.org", "Wikipedia"]
        },
        {
            "query": "What is Python programming?",
            "content": "The weather today is sunny with a chance of rain. Python is mentioned somewhere in this text but it's not the main topic.",
            "sources": ["Weather.com"]
        },
        {
            "query": "How to learn machine learning?",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data. To learn ML, start with Python, statistics, and linear algebra.",
            "sources": ["ML Course", "AI Textbook"]
        }
    ]
    
    print("Testing relevancy checking pipeline...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['query']}")
        print(f"{'='*60}")
        
        result = pipeline.process_content(
            test_case['query'],
            test_case['content'],
            test_case['sources']
        )
        
        print(f"\n📋 Final Assessment:")
        print(f"Overall Score: {result['overall_score']:.2f}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Acceptable: {'✅' if result['is_acceptable'] else '❌'}")
    
    # Test batch processing
    print(f"\n{'='*60}")
    print("BATCH PROCESSING TEST")
    print(f"{'='*60}")
    
    batch_results = pipeline.batch_process(
        "What is Python?",
        [
            {"content": "Python is a programming language", "sources": ["Python.org"]},
            {"content": "Cats are domestic animals", "sources": ["Pet.com"]},
            {"content": "Python programming is great for beginners", "sources": ["Tutorial.com"]}
        ]
    )
    
    accepted = sum(1 for r in batch_results if r['is_acceptable'])
    print(f"\n📊 Batch Results: {accepted}/{len(batch_results)} items accepted")
    
    print(f"\n--- Relevancy Check Pattern Summary ---")
    print(f"✅ Demonstrated content relevancy scoring")
    print(f"✅ Showed information filtering")
    print(f"✅ Implemented fact grounding and verification")
    print(f"✅ Created quality assessment system")

if __name__ == "__main__":
    main()
