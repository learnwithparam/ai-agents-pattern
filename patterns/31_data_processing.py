#!/usr/bin/env python3
"""
31 - Data Processing Pattern
Simple example showing how to process and structure data for RAG systems.

This demonstrates:
1. Data cleaning and preprocessing
2. Data restructuring and formatting
3. Data validation and quality checks
4. Data transformation for retrieval
"""

import sys
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class DataCleaner:
    """Clean and preprocess data for RAG systems."""
    
    def __init__(self):
        self.llm = get_llm()
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing noise and standardizing format."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Standardize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove multiple punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text content."""
        # Extract potential title (first sentence or line)
        lines = text.split('\n')
        title = lines[0].strip() if lines else ""
        if len(title) > 100:
            title = title[:100] + "..."
        
        # Extract key topics (simplified)
        topics = []
        if "python" in text.lower():
            topics.append("python")
        if "ai" in text.lower() or "artificial intelligence" in text.lower():
            topics.append("ai")
        if "machine learning" in text.lower():
            topics.append("machine learning")
        if "web" in text.lower() or "website" in text.lower():
            topics.append("web development")
        
        # Calculate basic metrics
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len([s for s in text.split('.') if s.strip()])
        
        return {
            "title": title,
            "topics": topics,
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "created_at": datetime.now().isoformat()
        }
    
    def validate_content(self, text: str) -> Dict[str, Any]:
        """Validate content quality and completeness."""
        issues = []
        warnings = []
        
        # Check minimum length
        if len(text) < 50:
            issues.append("Content too short")
        
        # Check for empty content
        if not text.strip():
            issues.append("Empty content")
        
        # Check for repetitive content
        words = text.lower().split()
        if len(set(words)) < len(words) * 0.5:
            warnings.append("Content may be repetitive")
        
        # Check for proper sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) < 2:
            warnings.append("Content may lack proper structure")
        
        # Check for encoding issues
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            issues.append("Encoding issues detected")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "quality_score": max(0, 1 - (len(issues) * 0.3 + len(warnings) * 0.1))
        }

class DataRestructurer:
    """Restructure data for better retrieval and processing."""
    
    def __init__(self):
        self.llm = get_llm()
    
    def chunk_content(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """Split content into overlapping chunks."""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                "id": f"chunk_{len(chunks)}",
                "content": chunk_text,
                "start_index": i,
                "end_index": min(i + chunk_size, len(words)),
                "word_count": len(chunk_words)
            })
        
        return chunks
    
    def create_summary(self, content: str) -> str:
        """Create a summary of the content."""
        prompt = f"""
        Create a concise summary of this content (2-3 sentences):
        
        Content: "{content[:1000]}..."
        
        Focus on the main points and key information.
        """
        
        summary = self.llm.generate(prompt).content
        return summary.strip()
    
    def extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content."""
        prompt = f"""
        Extract 5-7 key phrases from this content:
        
        Content: "{content[:1000]}..."
        
        Return only the key phrases, one per line.
        """
        
        response = self.llm.generate(prompt).content
        phrases = [line.strip() for line in response.split('\n') if line.strip()]
        return phrases[:7]  # Limit to 7 phrases
    
    def structure_for_retrieval(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Structure content for optimal retrieval."""
        # Create chunks
        chunks = self.chunk_content(content)
        
        # Create summary
        summary = self.create_summary(content)
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(content)
        
        return {
            "id": f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": metadata.get("title", "Untitled"),
            "summary": summary,
            "content": content,
            "chunks": chunks,
            "key_phrases": key_phrases,
            "topics": metadata.get("topics", []),
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        }

class DataProcessor:
    """Main data processing pipeline."""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.restructurer = DataRestructurer()
        self.processed_documents = []
    
    def process_document(self, content: str, source: str = "unknown") -> Dict[str, Any]:
        """Process a single document through the complete pipeline."""
        print(f"📄 Processing document from: {source}")
        
        # Step 1: Clean the content
        cleaned_content = self.cleaner.clean_text(content)
        print(f"🧹 Cleaned content: {len(cleaned_content)} characters")
        
        # Step 2: Extract metadata
        metadata = self.cleaner.extract_metadata(cleaned_content)
        print(f"📊 Extracted metadata: {len(metadata['topics'])} topics")
        
        # Step 3: Validate content
        validation = self.cleaner.validate_content(cleaned_content)
        print(f"✅ Validation: {'PASS' if validation['is_valid'] else 'FAIL'}")
        
        if not validation['is_valid']:
            print(f"❌ Issues: {validation['issues']}")
            return None
        
        # Step 4: Structure for retrieval
        structured = self.restructurer.structure_for_retrieval(cleaned_content, metadata)
        structured['source'] = source
        
        # Add to processed documents
        self.processed_documents.append(structured)
        
        print(f"📚 Document processed: {structured['id']}")
        return structured
    
    def batch_process(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process multiple documents."""
        results = []
        
        for i, doc in enumerate(documents):
            print(f"\n--- Processing document {i+1}/{len(documents)} ---")
            result = self.process_document(doc['content'], doc.get('source', f'doc_{i+1}'))
            if result:
                results.append(result)
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about processed documents."""
        if not self.processed_documents:
            return {"total_documents": 0}
        
        total_chunks = sum(len(doc['chunks']) for doc in self.processed_documents)
        total_words = sum(doc['metadata']['word_count'] for doc in self.processed_documents)
        
        all_topics = []
        for doc in self.processed_documents:
            all_topics.extend(doc['topics'])
        
        unique_topics = list(set(all_topics))
        
        return {
            "total_documents": len(self.processed_documents),
            "total_chunks": total_chunks,
            "total_words": total_words,
            "unique_topics": len(unique_topics),
            "topics": unique_topics,
            "average_chunks_per_doc": total_chunks / len(self.processed_documents)
        }

def main():
    print("🔄 Data Processing Pattern")
    print("=" * 50)
    
    # Initialize processor
    processor = DataProcessor()
    
    # Sample documents to process
    sample_documents = [
        {
            "content": """
            Python Programming Best Practices
            
            Python is a versatile programming language known for its simplicity and readability. 
            When writing Python code, follow these best practices:
            
            1. Use meaningful variable names
            2. Follow PEP 8 style guide
            3. Write comprehensive docstrings
            4. Handle exceptions properly
            5. Write unit tests for your code
            
            These practices will make your code more maintainable and professional.
            """,
            "source": "python_guide.txt"
        },
        {
            "content": """
            Machine Learning Fundamentals
            
            Machine learning is a subset of artificial intelligence that enables computers to learn 
            from data without being explicitly programmed. Key concepts include:
            
            - Supervised learning (classification, regression)
            - Unsupervised learning (clustering, dimensionality reduction)
            - Neural networks and deep learning
            - Feature engineering and selection
            
            Understanding these fundamentals is essential for building effective ML models.
            """,
            "source": "ml_basics.txt"
        },
        {
            "content": "Short content",  # This should fail validation
            "source": "invalid.txt"
        }
    ]
    
    print("Processing sample documents...")
    
    # Process documents
    results = processor.batch_process(sample_documents)
    
    print(f"\n--- Processing Results ---")
    print(f"Successfully processed: {len(results)} documents")
    
    # Show details for successful documents
    for result in results:
        print(f"\n📄 Document: {result['id']}")
        print(f"Title: {result['title']}")
        print(f"Topics: {result['topics']}")
        print(f"Chunks: {len(result['chunks'])}")
        print(f"Key phrases: {result['key_phrases'][:3]}...")
        print(f"Summary: {result['summary'][:100]}...")
    
    # Show processing statistics
    stats = processor.get_processing_stats()
    print(f"\n--- Processing Statistics ---")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Unique topics: {stats['unique_topics']}")
    print(f"Topics found: {stats['topics']}")
    
    print(f"\n--- Data Processing Pattern Summary ---")
    print(f"✅ Demonstrated data cleaning and preprocessing")
    print(f"✅ Showed data restructuring and formatting")
    print(f"✅ Implemented data validation and quality checks")
    print(f"✅ Created data transformation for retrieval")

if __name__ == "__main__":
    main()
