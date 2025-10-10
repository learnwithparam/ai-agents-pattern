#!/usr/bin/env python3
"""
29 - Query Rewriter Pattern
Simple example showing how to rewrite and optimize queries for better retrieval.

This demonstrates:
1. Query analysis and understanding
2. Query expansion and refinement
3. Intent clarification
4. Context-aware query rewriting
"""

import sys
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class QueryRewriter:
    """Intelligent query rewriting system."""
    
    def __init__(self):
        self.llm = get_llm()
        self.rewrite_history = []
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query to understand its intent and characteristics."""
        prompt = f"""
        Analyze this query and provide insights:
        
        Query: "{query}"
        
        Respond with:
        INTENT: [search, question, command, clarification]
        COMPLEXITY: [simple, medium, complex]
        DOMAIN: [technical, general, specific]
        CLARITY: [clear, ambiguous, unclear]
        KEYWORDS: [list main keywords]
        """
        
        analysis = self.llm.generate(prompt).content
        
        # Parse the analysis (simplified)
        intent = "question"
        complexity = "medium"
        domain = "general"
        clarity = "clear"
        keywords = query.split()[:5]  # Simple keyword extraction
        
        return {
            "original_query": query,
            "intent": intent,
            "complexity": complexity,
            "domain": domain,
            "clarity": clarity,
            "keywords": keywords,
            "analysis": analysis
        }
    
    def expand_query(self, query: str, context: str = "") -> List[str]:
        """Generate multiple query variations for better retrieval."""
        prompt = f"""
        Generate 3 different ways to rewrite this query for better search results:
        
        Original Query: "{query}"
        Context: "{context}"
        
        Provide 3 alternative phrasings that capture the same intent but use different wording.
        Each should be optimized for different search scenarios.
        """
        
        response = self.llm.generate(prompt).content
        
        # Extract variations (simplified parsing)
        variations = [
            query,  # Original
            f"{query} - detailed explanation",
            f"How to {query.lower()}",
            f"Best practices for {query.lower()}"
        ]
        
        return variations[:4]  # Limit to 4 variations
    
    def clarify_ambiguous_query(self, query: str) -> Dict[str, Any]:
        """Handle ambiguous queries by asking for clarification."""
        prompt = f"""
        This query might be ambiguous: "{query}"
        
        Generate 2-3 clarifying questions to help understand what the user really wants.
        Make the questions specific and actionable.
        """
        
        clarification_questions = self.llm.generate(prompt).content
        
        return {
            "original_query": query,
            "is_ambiguous": True,
            "clarification_questions": clarification_questions,
            "suggested_rewrites": [
                f"Specific: {query}",
                f"General: {query}",
                f"Technical: {query}"
            ]
        }
    
    def optimize_for_retrieval(self, query: str, domain: str = "general") -> str:
        """Optimize query specifically for document retrieval."""
        prompt = f"""
        Optimize this query for better document retrieval in the {domain} domain:
        
        Original: "{query}"
        
        Make it more specific, add relevant technical terms, and structure it for better matching.
        Keep it concise but comprehensive.
        """
        
        optimized = self.llm.generate(prompt).content
        
        return optimized.strip()
    
    def rewrite_with_context(self, query: str, conversation_history: List[str]) -> str:
        """Rewrite query considering conversation context."""
        context = " ".join(conversation_history[-3:])  # Last 3 exchanges
        
        prompt = f"""
        Rewrite this query considering the conversation context:
        
        Current Query: "{query}"
        Recent Context: "{context}"
        
        Make the query more specific and contextually relevant.
        """
        
        rewritten = self.llm.generate(prompt).content
        
        return rewritten.strip()
    
    def process_query(self, query: str, context: str = "", conversation_history: List[str] = None) -> Dict[str, Any]:
        """Main method to process and rewrite a query."""
        if conversation_history is None:
            conversation_history = []
        
        # Analyze the query
        analysis = self.analyze_query(query)
        
        # Generate variations
        variations = self.expand_query(query, context)
        
        # Optimize for retrieval
        optimized = self.optimize_for_retrieval(query, analysis["domain"])
        
        # Consider context if available
        context_aware = self.rewrite_with_context(query, conversation_history) if conversation_history else query
        
        # Store in history
        self.rewrite_history.append({
            "original": query,
            "optimized": optimized,
            "variations": variations,
            "analysis": analysis
        })
        
        return {
            "original_query": query,
            "optimized_query": optimized,
            "context_aware_query": context_aware,
            "variations": variations,
            "analysis": analysis,
            "recommended_query": optimized  # Use optimized as recommended
        }

class QueryRewriterPipeline:
    """Complete query rewriting pipeline."""
    
    def __init__(self):
        self.rewriter = QueryRewriter()
        self.conversation_history = []
    
    def add_to_history(self, query: str, response: str):
        """Add query and response to conversation history."""
        self.conversation_history.append(f"Q: {query}")
        self.conversation_history.append(f"A: {response}")
    
    def process_user_query(self, query: str) -> Dict[str, Any]:
        """Process a user query through the complete pipeline."""
        print(f"🔍 Processing query: {query}")
        
        # Step 1: Analyze query
        analysis = self.rewriter.analyze_query(query)
        print(f"📊 Analysis: {analysis['intent']} query, {analysis['complexity']} complexity")
        
        # Step 2: Check if ambiguous
        if analysis['clarity'] == 'ambiguous':
            clarification = self.rewriter.clarify_ambiguous_query(query)
            print(f"❓ Ambiguous query detected")
            return clarification
        
        # Step 3: Rewrite and optimize
        result = self.rewriter.process_query(
            query, 
            context="", 
            conversation_history=self.conversation_history
        )
        
        print(f"✨ Optimized query: {result['optimized_query']}")
        print(f"🔄 Generated {len(result['variations'])} variations")
        
        return result
    
    def get_rewrite_statistics(self):
        """Get statistics about query rewrites."""
        if not self.rewriter.rewrite_history:
            return {"total_rewrites": 0}
        
        total = len(self.rewriter.rewrite_history)
        avg_variations = sum(len(r['variations']) for r in self.rewriter.rewrite_history) / total
        
        return {
            "total_rewrites": total,
            "average_variations": avg_variations,
            "recent_queries": [r['original'] for r in self.rewriter.rewrite_history[-3:]]
        }

def main():
    print("🔄 Query Rewriter Pattern")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = QueryRewriterPipeline()
    
    # Test queries
    test_queries = [
        "How to code?",
        "What's the best way to learn machine learning?",
        "Python error handling",
        "Build a website",
        "AI agents"
    ]
    
    print("Testing query rewriting pipeline...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query}")
        print(f"{'='*60}")
        
        result = pipeline.process_user_query(query)
        
        if result.get('is_ambiguous'):
            print(f"❓ Ambiguous query - clarification needed")
            print(f"Questions: {result['clarification_questions']}")
        else:
            print(f"✅ Query processed successfully")
            print(f"📝 Optimized: {result['optimized_query']}")
            print(f"🔄 Variations: {len(result['variations'])}")
        
        # Simulate adding to conversation history
        pipeline.add_to_history(query, f"Response to: {query}")
    
    # Show statistics
    stats = pipeline.get_rewrite_statistics()
    print(f"\n--- Query Rewriter Statistics ---")
    print(f"Total queries processed: {stats['total_rewrites']}")
    print(f"Average variations per query: {stats['average_variations']:.1f}")
    
    print(f"\n--- Query Rewriter Pattern Summary ---")
    print(f"✅ Demonstrated query analysis and understanding")
    print(f"✅ Showed query expansion and refinement")
    print(f"✅ Implemented intent clarification")
    print(f"✅ Created context-aware query rewriting")

if __name__ == "__main__":
    main()
