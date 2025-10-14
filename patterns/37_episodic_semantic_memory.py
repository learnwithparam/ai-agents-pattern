#!/usr/bin/env python3
"""
37 - Episodic + Semantic Memory Pattern
Dual-memory system combining conversation history and structured knowledge.

The Episodic + Semantic Memory pattern implements a sophisticated memory system
that combines two types of memory: episodic memory for storing past conversations
and experiences, and semantic memory for structured facts and knowledge. This
enables true long-term personalization and context-aware interactions by allowing
the agent to remember both what happened in previous conversations and what it
knows about the world.

This demonstrates:
1. Episodic memory for conversation history and experiences
2. Semantic memory for structured facts and knowledge
3. Memory retrieval and integration mechanisms
4. Long-term personalization capabilities
5. Context-aware decision making
"""

import sys
import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

@dataclass
class EpisodicMemory:
    """Represents an episodic memory entry."""
    timestamp: datetime
    conversation_id: str
    user_input: str
    agent_response: str
    context: Dict[str, Any]
    importance: float
    tags: List[str]

@dataclass
class SemanticMemory:
    """Represents a semantic memory entry."""
    entity: str
    relationship: str
    target: str
    confidence: float
    source: str
    timestamp: datetime

class MemorySystem:
    """Dual memory system with episodic and semantic components."""
    
    def __init__(self, llm):
        self.llm = llm
        self.episodic_memories: List[EpisodicMemory] = []
        self.semantic_memories: List[SemanticMemory] = []
        self.conversation_id = 0
    
    def store_episodic_memory(self, user_input: str, agent_response: str, context: Dict[str, Any] = None) -> None:
        """Store an episodic memory."""
        if context is None:
            context = {}
        
        # Calculate importance based on content
        importance = self._calculate_importance(user_input, agent_response)
        
        # Extract tags
        tags = self._extract_tags(user_input, agent_response)
        
        memory = EpisodicMemory(
            timestamp=datetime.now(),
            conversation_id=f"conv_{self.conversation_id}",
            user_input=user_input,
            agent_response=agent_response,
            context=context,
            importance=importance,
            tags=tags
        )
        
        self.episodic_memories.append(memory)
    
    def store_semantic_memory(self, entity: str, relationship: str, target: str, source: str) -> None:
        """Store a semantic memory."""
        memory = SemanticMemory(
            entity=entity,
            relationship=relationship,
            target=target,
            confidence=0.8,  # Default confidence
            source=source,
            timestamp=datetime.now()
        )
        
        self.semantic_memories.append(memory)
    
    def _calculate_importance(self, user_input: str, agent_response: str) -> float:
        """Calculate importance of a memory entry."""
        prompt = f"""
        Rate the importance of this conversation exchange (0.0 to 1.0):
        
        User: {user_input}
        Agent: {agent_response}
        
        Consider:
        - Personal information shared
        - Specific requests or preferences
        - Emotional content
        - Technical details
        - Future reference value
        
        Respond with just a number between 0.0 and 1.0.
        """
        
        response = self.llm.generate(prompt).content.strip()
        
        try:
            importance = float(response)
            return max(0.0, min(1.0, importance))
        except ValueError:
            # Fallback importance calculation
            return 0.5
    
    def _extract_tags(self, user_input: str, agent_response: str) -> List[str]:
        """Extract relevant tags from the conversation."""
        prompt = f"""
        Extract relevant tags from this conversation:
        
        User: {user_input}
        Agent: {agent_response}
        
        Return 3-5 tags that describe the main topics, themes, or categories.
        Format as a JSON array of strings.
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            tags = json.loads(json_str)
            return tags[:5]  # Limit to 5 tags
        except json.JSONDecodeError:
            # Fallback tags
            return ["general", "conversation"]
    
    def retrieve_relevant_memories(self, query: str, memory_type: str = "both") -> Dict[str, List]:
        """Retrieve relevant memories for a query."""
        relevant_episodic = []
        relevant_semantic = []
        
        if memory_type in ["episodic", "both"]:
            relevant_episodic = self._retrieve_episodic_memories(query)
        
        if memory_type in ["semantic", "both"]:
            relevant_semantic = self._retrieve_semantic_memories(query)
        
        return {
            "episodic": relevant_episodic,
            "semantic": relevant_semantic
        }
    
    def _retrieve_episodic_memories(self, query: str) -> List[EpisodicMemory]:
        """Retrieve relevant episodic memories."""
        # Simple keyword-based retrieval (in real implementation, use vector similarity)
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in self.episodic_memories:
            # Check if query matches user input or agent response
            if (query_lower in memory.user_input.lower() or 
                query_lower in memory.agent_response.lower()):
                relevant_memories.append(memory)
            # Check tags
            elif any(tag.lower() in query_lower for tag in memory.tags):
                relevant_memories.append(memory)
        
        # Sort by importance and recency
        relevant_memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        return relevant_memories[:5]  # Return top 5
    
    def _retrieve_semantic_memories(self, query: str) -> List[SemanticMemory]:
        """Retrieve relevant semantic memories."""
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in self.semantic_memories:
            if (query_lower in memory.entity.lower() or 
                query_lower in memory.target.lower() or
                query_lower in memory.relationship.lower()):
                relevant_memories.append(memory)
        
        # Sort by confidence and recency
        relevant_memories.sort(key=lambda m: (m.confidence, m.timestamp), reverse=True)
        return relevant_memories[:5]  # Return top 5
    
    def extract_semantic_facts(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract semantic facts from text."""
        prompt = f"""
        Extract semantic facts from this text: {text}
        
        Identify entities and their relationships in the format:
        (entity, relationship, target)
        
        Examples:
        - (Apple, is_a, company)
        - (Tim Cook, is_ceo_of, Apple)
        - (Python, is_a, programming_language)
        
        Return as JSON array of [entity, relationship, target] tuples.
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            facts = json.loads(json_str)
            return [(fact[0], fact[1], fact[2]) for fact in facts if len(fact) == 3]
        except json.JSONDecodeError:
            return []
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory system."""
        return {
            "episodic_count": len(self.episodic_memories),
            "semantic_count": len(self.semantic_memories),
            "conversation_id": self.conversation_id,
            "recent_episodic": self.episodic_memories[-3:] if self.episodic_memories else [],
            "recent_semantic": self.semantic_memories[-3:] if self.semantic_memories else []
        }

class MemoryEnhancedAgent:
    """Agent enhanced with dual memory system."""
    
    def __init__(self, llm):
        self.llm = llm
        self.memory_system = MemorySystem(llm)
        self.conversation_id = 0
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input with memory enhancement."""
        print(f"💭 Processing: {user_input}")
        print("=" * 50)
        
        # Retrieve relevant memories
        print("\n🔍 Retrieving relevant memories...")
        memories = self.memory_system.retrieve_relevant_memories(user_input)
        
        print(f"Found {len(memories['episodic'])} episodic memories")
        print(f"Found {len(memories['semantic'])} semantic memories")
        
        # Build context from memories
        context = self._build_memory_context(memories)
        
        # Generate response with memory context
        print("\n🤖 Generating response with memory context...")
        response = self._generate_response(user_input, context)
        
        # Store this interaction in episodic memory
        self.memory_system.store_episodic_memory(user_input, response, {
            "conversation_id": self.conversation_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract and store semantic facts
        print("\n🧠 Extracting semantic facts...")
        facts = self.memory_system.extract_semantic_facts(user_input + " " + response)
        for entity, relationship, target in facts:
            self.memory_system.store_semantic_memory(entity, relationship, target, f"conv_{self.conversation_id}")
            print(f"  - {entity} {relationship} {target}")
        
        self.conversation_id += 1
        
        return {
            "user_input": user_input,
            "response": response,
            "memories_used": memories,
            "facts_extracted": facts,
            "conversation_id": self.conversation_id - 1
        }
    
    def _build_memory_context(self, memories: Dict[str, List]) -> str:
        """Build context string from retrieved memories."""
        context = ""
        
        if memories["episodic"]:
            context += "Relevant past conversations:\n"
            for memory in memories["episodic"][:3]:  # Limit to 3 most relevant
                context += f"- User: {memory.user_input}\n"
                context += f"  Agent: {memory.agent_response}\n"
                context += f"  Tags: {', '.join(memory.tags)}\n\n"
        
        if memories["semantic"]:
            context += "Relevant knowledge:\n"
            for memory in memories["semantic"][:3]:  # Limit to 3 most relevant
                context += f"- {memory.entity} {memory.relationship} {memory.target}\n"
        
        return context
    
    def _generate_response(self, user_input: str, memory_context: str) -> str:
        """Generate response with memory context."""
        prompt = f"""
        You are a helpful assistant with access to your memory of past conversations and knowledge.
        
        Current user input: {user_input}
        
        Memory context:
        {memory_context}
        
        Generate a response that:
        1. Directly addresses the user's input
        2. References relevant past conversations when appropriate
        3. Uses your knowledge base to provide accurate information
        4. Shows continuity and personalization
        5. Asks follow-up questions when relevant
        
        Be natural and conversational while leveraging your memory effectively.
        """
        
        return self.llm.generate(prompt).content

def main():
    print("🧠 Episodic + Semantic Memory Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create memory-enhanced agent
    agent = MemoryEnhancedAgent(llm)
    
    # Simulate a conversation
    conversation = [
        "Hi, I'm John and I'm interested in learning Python programming.",
        "What are the best resources for learning Python?",
        "I work in finance and want to use Python for data analysis.",
        "Can you recommend some Python libraries for financial data?",
        "What did we discuss earlier about Python libraries?",
        "I also mentioned I work in finance - what libraries would be good for that?",
        "Tell me more about pandas since you mentioned it before."
    ]
    
    print("\n🚀 Starting conversation with memory...")
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n{'='*60}")
        print(f"Turn {i}/{len(conversation)}")
        result = agent.process_input(user_input)
        
        print(f"\n📊 Turn Summary:")
        print(f"  - Episodic memories used: {len(result['memories_used']['episodic'])}")
        print(f"  - Semantic memories used: {len(result['memories_used']['semantic'])}")
        print(f"  - Facts extracted: {len(result['facts_extracted'])}")
        print(f"  - Response: {result['response'][:100]}...")
    
    # Show memory summary
    print(f"\n{'='*60}")
    print("📈 Memory System Summary:")
    summary = agent.memory_system.get_memory_summary()
    print(f"  - Total episodic memories: {summary['episodic_count']}")
    print(f"  - Total semantic memories: {summary['semantic_count']}")
    print(f"  - Conversations: {summary['conversation_id']}")
    
    if summary['recent_episodic']:
        print(f"  - Recent episodic: {len(summary['recent_episodic'])} memories")
    if summary['recent_semantic']:
        print(f"  - Recent semantic: {len(summary['recent_semantic'])} memories")

if __name__ == "__main__":
    main()
