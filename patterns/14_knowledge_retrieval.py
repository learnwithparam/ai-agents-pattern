#!/usr/bin/env python3
"""
14 - Knowledge Retrieval (RAG) Pattern
Simple example showing how to retrieve and use knowledge for better responses.

This demonstrates:
1. Store knowledge in a simple format
2. Retrieve relevant information
3. Use retrieved knowledge to enhance responses
4. Implement basic RAG (Retrieval-Augmented Generation)
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class KnowledgeBase:
    """Simple knowledge base for storing and retrieving information."""
    
    def __init__(self):
        self.knowledge = []
        self.llm = get_llm()
    
    def add_knowledge(self, title, content, tags=None):
        """Add knowledge to the knowledge base."""
        if tags is None:
            tags = []
        
        knowledge_item = {
            "id": len(self.knowledge) + 1,
            "title": title,
            "content": content,
            "tags": tags
        }
        self.knowledge.append(knowledge_item)
    
    def search_knowledge(self, query, limit=3):
        """Search for relevant knowledge based on query."""
        if not self.knowledge:
            return []
        
        # Simple keyword-based search (in real implementation, use embeddings)
        query_lower = query.lower()
        scored_items = []
        
        # Extract key terms from query
        query_terms = query_lower.split()
        
        for item in self.knowledge:
            score = 0
            
            # Check title match (exact phrase)
            if query_lower in item["title"].lower():
                score += 3
            
            # Check title match (individual words)
            for term in query_terms:
                if term in item["title"].lower():
                    score += 2
            
            # Check content match (exact phrase)
            if query_lower in item["content"].lower():
                score += 2
            
            # Check content match (individual words)
            for term in query_terms:
                if term in item["content"].lower():
                    score += 1
            
            # Check tags match
            for tag in item["tags"]:
                if query_lower in tag.lower():
                    score += 1
                for term in query_terms:
                    if term in tag.lower():
                        score += 1
            
            if score > 0:
                scored_items.append((item, score))
        
        # Sort by score and return top results
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_items[:limit]]
    
    def get_knowledge_by_id(self, knowledge_id):
        """Get knowledge by ID."""
        for item in self.knowledge:
            if item["id"] == knowledge_id:
                return item
        return None

class RAGSystem:
    """Retrieval-Augmented Generation system."""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.llm = get_llm()
        self._initialize_sample_knowledge()
    
    def _initialize_sample_knowledge(self):
        """Initialize with sample knowledge."""
        sample_knowledge = [
            {
                "title": "Python Best Practices",
                "content": "Python best practices include using meaningful variable names, following PEP 8 style guide, writing docstrings, and using type hints. Always handle exceptions properly and write unit tests.",
                "tags": ["python", "programming", "best-practices"]
            },
            {
                "title": "AI Agent Patterns",
                "content": "Common AI agent patterns include prompt chaining, routing, parallelization, reflection, tool calling, planning, multi-agent coordination, and memory management.",
                "tags": ["ai", "agents", "patterns"]
            },
            {
                "title": "Error Handling in Python",
                "content": "Use try-except blocks to handle errors gracefully. Catch specific exceptions rather than general Exception. Use finally blocks for cleanup. Log errors for debugging.",
                "tags": ["python", "error-handling", "exceptions"]
            },
            {
                "title": "Machine Learning Basics",
                "content": "Machine learning involves training models on data to make predictions. Common types include supervised learning (classification, regression), unsupervised learning (clustering), and reinforcement learning.",
                "tags": ["machine-learning", "ai", "data-science"]
            },
            {
                "title": "Web Development with Python",
                "content": "Popular Python web frameworks include Django (full-featured), Flask (lightweight), and FastAPI (modern, fast). Use virtual environments and follow security best practices.",
                "tags": ["python", "web-development", "frameworks"]
            }
        ]
        
        for item in sample_knowledge:
            self.knowledge_base.add_knowledge(
                item["title"], 
                item["content"], 
                item["tags"]
            )
    
    def query(self, question):
        """Query the RAG system with a question."""
        print(f"🔍 Searching knowledge base for: {question}")
        
        # Step 1: Retrieve relevant knowledge
        relevant_knowledge = self.knowledge_base.search_knowledge(question)
        
        if not relevant_knowledge:
            print("❌ No relevant knowledge found")
            return self._generate_response_without_knowledge(question)
        
        print(f"✅ Found {len(relevant_knowledge)} relevant knowledge items")
        
        # Step 2: Prepare context from retrieved knowledge
        context = self._prepare_context(relevant_knowledge)
        
        # Step 3: Generate response using retrieved knowledge
        return self._generate_response_with_knowledge(question, context)
    
    def _prepare_context(self, knowledge_items):
        """Prepare context from retrieved knowledge items."""
        context_parts = []
        for item in knowledge_items:
            context_parts.append(f"Title: {item['title']}\nContent: {item['content']}")
        return "\n\n".join(context_parts)
    
    def _generate_response_with_knowledge(self, question, context):
        """Generate response using retrieved knowledge."""
        prompt = f"""
        Based on the following knowledge, answer the user's question:
        
        Knowledge Context:
        {context}
        
        User Question: {question}
        
        Provide a comprehensive answer based on the knowledge provided. If the knowledge doesn't fully answer the question, say so and provide what information you can.
        """
        
        response = self.llm.generate(prompt).content
        return {
            "answer": response,
            "knowledge_used": len(context.split("\n\n")),
            "has_knowledge": True
        }
    
    def _generate_response_without_knowledge(self, question):
        """Generate response without retrieved knowledge."""
        prompt = f"""
        Answer this question based on your general knowledge:
        {question}
        
        Note that I don't have specific knowledge about this topic in my knowledge base.
        """
        
        response = self.llm.generate(prompt).content
        return {
            "answer": response,
            "knowledge_used": 0,
            "has_knowledge": False
        }
    
    def add_knowledge(self, title, content, tags=None):
        """Add new knowledge to the system."""
        self.knowledge_base.add_knowledge(title, content, tags)
        print(f"✅ Added knowledge: {title}")
    
    def list_knowledge(self):
        """List all knowledge in the system."""
        return self.knowledge_base.knowledge

def main():
    print("📚 Knowledge Retrieval (RAG) Pattern")
    print("=" * 40)
    
    # Initialize RAG system
    rag = RAGSystem()
    
    print(f"Knowledge base initialized with {len(rag.list_knowledge())} items")
    
    # Test queries
    test_questions = [
        "What are Python best practices?",
        "How do I handle errors in Python?",
        "What are some AI agent patterns?",
        "Tell me about machine learning",
        "What's the weather like today?"  # Should not find relevant knowledge
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n--- Test {i + 1} ---")
        result = rag.query(question)
        
        print(f"Question: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Knowledge used: {result['knowledge_used']} items")
        print(f"Has knowledge: {result['has_knowledge']}")
        print("-" * 40)
    
    # Demonstrate adding new knowledge
    print(f"\n--- Adding New Knowledge ---")
    rag.add_knowledge(
        "Docker Basics",
        "Docker is a containerization platform that allows you to package applications and their dependencies into containers. Use docker-compose for multi-container applications.",
        ["docker", "containers", "devops"]
    )
    
    # Test with new knowledge
    print(f"\n--- Testing New Knowledge ---")
    result = rag.query("What is Docker?")
    print(f"Answer: {result['answer']}")
    print(f"Knowledge used: {result['knowledge_used']} items")

if __name__ == "__main__":
    main()
