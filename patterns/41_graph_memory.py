#!/usr/bin/env python3
"""
41 - Graph (World-Model) Memory Pattern
Structured knowledge storage and retrieval using graph databases.

The Graph Memory pattern stores knowledge as a structured graph of entities
and relationships, enabling complex, multi-hop reasoning by traversing connections.
This approach is particularly effective for corporate intelligence, advanced research,
and any domain where understanding relationships between concepts is crucial for
problem-solving and decision-making.

This demonstrates:
1. Graph-based knowledge representation
2. Entity and relationship modeling
3. Multi-hop reasoning through graph traversal
4. Knowledge graph construction and maintenance
5. Complex query answering using graph patterns
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
class Entity:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any]
    created_at: datetime

@dataclass
class Relationship:
    """Represents a relationship between entities."""
    id: str
    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float
    created_at: datetime

class GraphMemory:
    """Graph-based memory system."""
    
    def __init__(self, llm):
        self.llm = llm
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.entity_counter = 0
        self.relationship_counter = 0
    
    def add_entity(self, name: str, entity_type: str, properties: Dict[str, Any] = None) -> str:
        """Add an entity to the graph."""
        if properties is None:
            properties = {}
        
        entity_id = f"entity_{self.entity_counter}"
        self.entity_counter += 1
        
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            properties=properties,
            created_at=datetime.now()
        )
        
        self.entities[entity_id] = entity
        return entity_id
    
    def add_relationship(self, source_entity: str, target_entity: str, 
                        relationship_type: str, properties: Dict[str, Any] = None,
                        confidence: float = 0.8) -> str:
        """Add a relationship between entities."""
        if properties is None:
            properties = {}
        
        relationship_id = f"rel_{self.relationship_counter}"
        self.relationship_counter += 1
        
        relationship = Relationship(
            id=relationship_id,
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            properties=properties,
            confidence=confidence,
            created_at=datetime.now()
        )
        
        self.relationships[relationship_id] = relationship
        return relationship_id
    
    def find_entity(self, name: str) -> Optional[Entity]:
        """Find an entity by name."""
        for entity_id, entity in self.entities.items():
            if isinstance(entity, Entity) and entity.name.lower() == name.lower():
                return entity
        return None
    
    def get_entity_relationships(self, entity_id: str) -> List[Relationship]:
        """Get all relationships for an entity."""
        relationships = []
        for rel in self.relationships.values():
            if rel.source_entity == entity_id or rel.target_entity == entity_id:
                relationships.append(rel)
        return relationships
    
    def find_path(self, source_entity: str, target_entity: str, max_depth: int = 3) -> List[List[str]]:
        """Find paths between two entities."""
        if source_entity not in self.entities or target_entity not in self.entities:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current == target:
                paths.append(path[:])
                return
            
            if current in visited:
                return
            
            visited.add(current)
            
            # Get all relationships for current entity
            relationships = self.get_entity_relationships(current)
            
            for rel in relationships:
                next_entity = rel.target_entity if rel.source_entity == current else rel.source_entity
                if next_entity not in visited:
                    path.append(rel.id)
                    dfs(next_entity, target, path, depth + 1)
                    path.pop()
            
            visited.remove(current)
        
        dfs(source_entity, target_entity, [], 0)
        return paths
    
    def query_entities(self, entity_type: str = None, properties: Dict[str, Any] = None) -> List[Entity]:
        """Query entities by type and properties."""
        results = []
        
        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            
            if properties:
                match = True
                for key, value in properties.items():
                    if entity.properties.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            results.append(entity)
        
        return results
    
    def query_relationships(self, relationship_type: str = None, 
                          source_entity: str = None, target_entity: str = None) -> List[Relationship]:
        """Query relationships by type and entities."""
        results = []
        
        for rel in self.relationships.values():
            if relationship_type and rel.relationship_type != relationship_type:
                continue
            
            if source_entity and rel.source_entity != source_entity:
                continue
            
            if target_entity and rel.target_entity != target_entity:
                continue
            
            results.append(rel)
        
        return results
    
    def extract_knowledge(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        """Extract entities and relationships from text."""
        prompt = f"""
        Extract entities and relationships from this text: {text}
        
        Identify:
        1. Entities (people, organizations, concepts, objects)
        2. Relationships between entities
        
        Format as JSON:
        {{
            "entities": [
                {{"name": "Apple Inc.", "type": "organization", "properties": {{"industry": "technology"}}}},
                {{"name": "Tim Cook", "type": "person", "properties": {{"role": "CEO"}}}}
            ],
            "relationships": [
                {{"source": "Tim Cook", "target": "Apple Inc.", "type": "is_ceo_of", "confidence": 0.9}},
                {{"source": "Apple Inc.", "target": "iPhone", "type": "manufactures", "confidence": 0.8}}
            ]
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
            
            # Add entities
            entities = []
            for entity_data in data.get("entities", []):
                entity_id = self.add_entity(
                    entity_data["name"],
                    entity_data["type"],
                    entity_data.get("properties", {})
                )
                # Get the entity object directly from the return value
                entity = self.entities[entity_id]
                entities.append(entity)
            
            # Add relationships
            relationships = []
            for rel_data in data.get("relationships", []):
                # Find source and target entities
                source_entity = self.find_entity(rel_data["source"])
                target_entity = self.find_entity(rel_data["target"])
                
                if source_entity and target_entity:
                    rel_id = self.add_relationship(
                        source_entity.id,
                        target_entity.id,
                        rel_data["type"],
                        {},
                        rel_data.get("confidence", 0.8)
                    )
                    relationships.append(self.relationships[rel_id])
            
            return entities, relationships
            
        except json.JSONDecodeError:
            return [], []
    
    def answer_question(self, question: str) -> str:
        """Answer a question using the knowledge graph."""
        print(f"🔍 Answering question: {question}")
        
        # Extract key entities from question
        entities = self._extract_question_entities(question)
        
        # Find relevant entities in graph
        relevant_entities = []
        for entity_name in entities:
            entity = self.find_entity(entity_name)
            if entity:
                relevant_entities.append(entity)
        
        # Find relationships between relevant entities
        relevant_relationships = []
        for entity in relevant_entities:
            relationships = self.get_entity_relationships(entity.id)
            relevant_relationships.extend(relationships)
        
        # Generate answer based on graph knowledge
        prompt = f"""
        Question: {question}
        
        Relevant entities in knowledge graph:
        {json.dumps([{"name": e.name, "type": e.entity_type, "properties": e.properties} for e in relevant_entities], indent=2)}
        
        Relevant relationships:
        {json.dumps([{"source": self.entities[r.source_entity].name, "target": self.entities[r.target_entity].name, "type": r.relationship_type} for r in relevant_relationships], indent=2)}
        
        Answer the question using the knowledge graph information.
        If the information is incomplete, mention what's missing.
        """
        
        return self.llm.generate(prompt).content
    
    def _extract_question_entities(self, question: str) -> List[str]:
        """Extract entity names from a question."""
        prompt = f"""
        Extract entity names from this question: {question}
        
        Return as JSON array of strings:
        ["entity1", "entity2", "entity3"]
        """
        
        response = self.llm.generate(prompt).content
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get summary of the knowledge graph."""
        entity_types = {}
        relationship_types = {}
        
        for entity in self.entities.values():
            entity_types[entity.entity_type] = entity_types.get(entity.entity_type, 0) + 1
        
        for rel in self.relationships.values():
            relationship_types[rel.relationship_type] = relationship_types.get(rel.relationship_type, 0) + 1
        
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entity_types": entity_types,
            "relationship_types": relationship_types,
            "average_confidence": sum(rel.confidence for rel in self.relationships.values()) / len(self.relationships) if self.relationships else 0
        }

class GraphMemoryAgent:
    """Agent enhanced with graph memory."""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph_memory = GraphMemory(llm)
        self.conversation_history = []
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input with graph memory."""
        print(f"💭 Processing: {user_input}")
        print("=" * 50)
        
        # Extract knowledge from input
        print("\n🧠 Extracting knowledge...")
        entities, relationships = self.graph_memory.extract_knowledge(user_input)
        print(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
        
        # Answer question using graph
        print("\n🔍 Answering using knowledge graph...")
        answer = self.graph_memory.answer_question(user_input)
        
        # Store in conversation history
        self.conversation_history.append({
            "input": user_input,
            "answer": answer,
            "entities_extracted": len(entities),
            "relationships_extracted": len(relationships),
            "timestamp": datetime.now()
        })
        
        return {
            "input": user_input,
            "answer": answer,
            "entities_extracted": entities,
            "relationships_extracted": relationships,
            "graph_summary": self.graph_memory.get_graph_summary()
        }
    
    def get_entity_info(self, entity_name: str) -> Dict[str, Any]:
        """Get detailed information about an entity."""
        entity = self.graph_memory.find_entity(entity_name)
        if not entity:
            return {"error": "Entity not found"}
        
        relationships = self.graph_memory.get_entity_relationships(entity.id)
        
        return {
            "entity": {
                "name": entity.name,
                "type": entity.entity_type,
                "properties": entity.properties
            },
            "relationships": [
                {
                    "type": rel.relationship_type,
                    "target": self.graph_memory.entities[rel.target_entity].name,
                    "confidence": rel.confidence
                } for rel in relationships
            ]
        }

def main():
    print("🕸️ Graph (World-Model) Memory Pattern")
    print("=" * 40)
    
    # Get LLM
    llm = get_llm()
    print(f"Using: {llm.provider}")
    
    # Create graph memory agent
    agent = GraphMemoryAgent(llm)
    
    # Test inputs to build knowledge graph
    test_inputs = [
        "Apple Inc. is a technology company founded by Steve Jobs. Tim Cook is the current CEO of Apple.",
        "Apple manufactures the iPhone, iPad, and Mac computers. The iPhone was first released in 2007.",
        "Steve Jobs co-founded Apple with Steve Wozniak in 1976. Apple is headquartered in Cupertino, California.",
        "The iPhone runs on iOS operating system. Apple also develops macOS for Mac computers.",
        "Apple's main competitors include Samsung, Google, and Microsoft in various product categories."
    ]
    
    print("\n🚀 Building knowledge graph...")
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n--- Input {i}/{len(test_inputs)} ---")
        result = agent.process_input(input_text)
        print(f"Entities: {result['graph_summary']['total_entities']}")
        print(f"Relationships: {result['graph_summary']['total_relationships']}")
    
    # Test questions
    print(f"\n{'='*60}")
    print("🔍 Testing knowledge graph queries...")
    
    questions = [
        "Who is the CEO of Apple?",
        "What products does Apple manufacture?",
        "Who founded Apple and when?",
        "What operating systems does Apple develop?",
        "Who are Apple's main competitors?",
        "What is the relationship between Steve Jobs and Apple?"
    ]
    
    for question in questions:
        print(f"\n--- Question: {question} ---")
        result = agent.process_input(question)
        print(f"Answer: {result['answer']}")
    
    # Show graph summary
    print(f"\n{'='*60}")
    print("📊 Knowledge Graph Summary:")
    summary = agent.graph_memory.get_graph_summary()
    print(f"  - Total entities: {summary['total_entities']}")
    print(f"  - Total relationships: {summary['total_relationships']}")
    print(f"  - Entity types: {summary['entity_types']}")
    print(f"  - Relationship types: {summary['relationship_types']}")
    print(f"  - Average confidence: {summary['average_confidence']:.2f}")
    
    # Show entity details
    print(f"\n🔍 Entity Details:")
    apple_info = agent.get_entity_info("Apple Inc.")
    if "error" not in apple_info:
        print(f"Apple Inc.: {apple_info['entity']['type']}")
        print(f"Relationships: {len(apple_info['relationships'])}")

if __name__ == "__main__":
    main()
