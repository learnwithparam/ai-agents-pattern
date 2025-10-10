#!/usr/bin/env python3
"""
23 - Agentic RAG Pattern
Simple example showing how to build an agentic RAG system that decides when to retrieve.

This demonstrates:
1. Query analysis and routing
2. Document retrieval decision making
3. Response generation with context
4. Quality assessment and feedback
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class DocumentStore:
    """Simple document store for demonstration."""
    
    def __init__(self):
        self.documents = {
            "python": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
            "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines. It includes machine learning, natural language processing, and computer vision.",
            "machine_learning": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
            "web_development": "Web development involves creating websites and web applications using technologies like HTML, CSS, JavaScript, and various frameworks.",
            "data_science": "Data Science combines statistics, programming, and domain expertise to extract insights from data using various analytical methods."
        }
    
    def search(self, query, top_k=3):
        """Search for relevant documents."""
        query_lower = query.lower()
        results = []
        
        for topic, content in self.documents.items():
            if any(word in query_lower for word in topic.split('_')):
                results.append({
                    "topic": topic,
                    "content": content,
                    "relevance_score": 0.8  # Simplified scoring
                })
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

class AgenticRAG:
    """Agentic RAG system that decides when to retrieve information."""
    
    def __init__(self):
        self.llm = get_llm()
        self.document_store = DocumentStore()
        self.retrieval_threshold = 0.7  # Confidence threshold for retrieval
    
    def analyze_query(self, query):
        """Analyze if the query needs document retrieval."""
        analysis_prompt = f"""
        Analyze this user query and determine if it needs information retrieval:
        
        Query: "{query}"
        
        Respond with:
        NEEDS_RETRIEVAL: [yes/no]
        CONFIDENCE: [0.0-1.0]
        REASONING: [brief explanation]
        
        Consider:
        - Does this require specific factual information?
        - Is this a general question that can be answered without retrieval?
        - Does this need current or domain-specific knowledge?
        """
        
        response = self.llm.generate(analysis_prompt).content
        
        # Parse response
        needs_retrieval = "yes" in response.lower() and "needs_retrieval" in response.lower()
        confidence = 0.5  # Default confidence
        
        try:
            # Extract confidence score
            for line in response.split('\n'):
                if 'confidence:' in line.lower():
                    confidence = float(line.split(':')[1].strip())
                    break
        except:
            pass
        
        return {
            "needs_retrieval": needs_retrieval,
            "confidence": confidence,
            "reasoning": response
        }
    
    def retrieve_documents(self, query):
        """Retrieve relevant documents."""
        print(f"🔍 Retrieving documents for: {query}")
        documents = self.document_store.search(query)
        
        if documents:
            print(f"📚 Found {len(documents)} relevant documents:")
            for doc in documents:
                print(f"  - {doc['topic']}: {doc['content'][:50]}...")
        else:
            print("📚 No relevant documents found")
        
        return documents
    
    def generate_response(self, query, documents=None):
        """Generate response with or without retrieved context."""
        if documents:
            context = "\n".join([doc["content"] for doc in documents])
            prompt = f"""
            Based on the following context, answer the user's question:
            
            Context:
            {context}
            
            Question: {query}
            
            Provide a helpful, accurate answer based on the context provided.
            If the context doesn't contain enough information, say so.
            """
        else:
            prompt = f"""
            Answer this question based on your general knowledge:
            
            Question: {query}
            
            Provide a helpful, accurate answer.
            """
        
        response = self.llm.generate(prompt).content
        return response
    
    def assess_response_quality(self, query, response, documents=None):
        """Assess the quality of the generated response."""
        assessment_prompt = f"""
        Assess the quality of this AI response:
        
        Query: {query}
        Response: {response}
        Used Retrieval: {'Yes' if documents else 'No'}
        
        Rate the response on:
        1. Accuracy (1-10)
        2. Completeness (1-10)
        3. Helpfulness (1-10)
        
        Provide scores and brief explanation.
        """
        
        assessment = self.llm.generate(assessment_prompt).content
        
        # Simple parsing for demo
        try:
            lines = assessment.split('\n')
            scores = {}
            for line in lines:
                if 'accuracy' in line.lower():
                    scores['accuracy'] = int(line.split(':')[1].strip())
                elif 'completeness' in line.lower():
                    scores['completeness'] = int(line.split(':')[1].strip())
                elif 'helpfulness' in line.lower():
                    scores['helpfulness'] = int(line.split(':')[1].strip())
        except:
            scores = {'accuracy': 7, 'completeness': 7, 'helpfulness': 7}
        
        return {
            "scores": scores,
            "explanation": assessment
        }
    
    def process_query(self, query):
        """Process a query through the agentic RAG pipeline."""
        print(f"\n{'='*60}")
        print(f"🔍 Processing Query: {query}")
        print(f"{'='*60}")
        
        # Step 1: Analyze query
        print(f"\n--- Step 1: Query Analysis ---")
        analysis = self.analyze_query(query)
        print(f"Needs Retrieval: {'✅ Yes' if analysis['needs_retrieval'] else '❌ No'}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        print(f"Reasoning: {analysis['reasoning'][:100]}...")
        
        # Step 2: Decide on retrieval
        documents = None
        if analysis['needs_retrieval'] and analysis['confidence'] >= self.retrieval_threshold:
            print(f"\n--- Step 2: Document Retrieval ---")
            documents = self.retrieve_documents(query)
        else:
            print(f"\n--- Step 2: Direct Response ---")
            print("Skipping retrieval - using general knowledge")
        
        # Step 3: Generate response
        print(f"\n--- Step 3: Response Generation ---")
        response = self.generate_response(query, documents)
        print(f"Response: {response[:200]}...")
        
        # Step 4: Assess quality
        print(f"\n--- Step 4: Quality Assessment ---")
        quality = self.assess_response_quality(query, response, documents)
        print(f"Quality Scores: {quality['scores']}")
        
        return {
            "query": query,
            "analysis": analysis,
            "documents": documents,
            "response": response,
            "quality": quality
        }

def main():
    print("🤖 Agentic RAG Pattern")
    print("=" * 50)
    
    # Initialize agentic RAG system
    rag_system = AgenticRAG()
    print(f"Using LLM: {rag_system.llm.provider}")
    
    # Test queries
    test_queries = [
        "What is Python programming?",
        "How do I make a sandwich?",
        "What are the latest developments in machine learning?",
        "What is the capital of France?",
        "How does artificial intelligence work?",
        "What's the weather like today?"
    ]
    
    results = []
    
    for query in test_queries:
        result = rag_system.process_query(query)
        results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 AGENTIC RAG SUMMARY")
    print(f"{'='*60}")
    
    retrieval_count = sum(1 for r in results if r['documents'])
    direct_count = len(results) - retrieval_count
    
    print(f"Total Queries: {len(results)}")
    print(f"Retrieval Used: {retrieval_count}")
    print(f"Direct Responses: {direct_count}")
    
    avg_quality = {}
    for result in results:
        for metric, score in result['quality']['scores'].items():
            if metric not in avg_quality:
                avg_quality[metric] = []
            avg_quality[metric].append(score)
    
    print(f"\nAverage Quality Scores:")
    for metric, scores in avg_quality.items():
        avg_score = sum(scores) / len(scores)
        print(f"  {metric.title()}: {avg_score:.1f}/10")
    
    print(f"\n--- Agentic RAG Pattern Summary ---")
    print(f"✅ Demonstrated intelligent retrieval decision making")
    print(f"✅ Showed query analysis and routing")
    print(f"✅ Implemented quality assessment")
    print(f"✅ Created adaptive RAG system")

if __name__ == "__main__":
    main()
