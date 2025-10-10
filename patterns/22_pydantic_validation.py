#!/usr/bin/env python3
"""
22 - Pydantic Validation Pattern
Simple example showing how to use Pydantic for data validation in AI agents.

This demonstrates:
1. Data validation with Pydantic
2. Structured output from LLMs
3. Error handling and validation
4. Type safety in AI applications
"""

import sys
import os
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

# Try to import Pydantic, fall back to simple validation if not available
try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️ Pydantic not available. Using simple validation instead.")
    print("Install with: pip install pydantic")

if PYDANTIC_AVAILABLE:
    class UserProfile(BaseModel):
        """User profile with validation."""
        name: str = Field(..., min_length=2, max_length=50, description="User's full name")
        email: str = Field(..., description="User's email address")
        age: int = Field(..., ge=0, le=120, description="User's age")
        interests: List[str] = Field(default_factory=list, description="List of user interests")
        created_at: datetime = Field(default_factory=datetime.now, description="Profile creation time")
        
        @field_validator('email')
        @classmethod
        def validate_email(cls, v):
            if '@' not in v:
                raise ValueError('Email must contain @ symbol')
            return v.lower()
        
        @field_validator('interests')
        @classmethod
        def validate_interests(cls, v):
            if len(v) > 10:
                raise ValueError('Too many interests (max 10)')
            return [interest.strip().title() for interest in v if interest.strip()]
    
    class Task(BaseModel):
        """Task with validation."""
        id: int = Field(..., gt=0, description="Unique task identifier")
        title: str = Field(..., min_length=5, max_length=100, description="Task title")
        description: Optional[str] = Field(None, max_length=500, description="Task description")
        priority: str = Field(..., pattern='^(low|medium|high|urgent)$', description="Task priority level")
        due_date: Optional[datetime] = Field(None, description="Task due date")
        completed: bool = Field(default=False, description="Task completion status")
        
        @field_validator('due_date')
        @classmethod
        def validate_due_date(cls, v):
            if v and v < datetime.now():
                raise ValueError('Due date cannot be in the past')
            return v
    
    class AIResponse(BaseModel):
        """Structured AI response with validation."""
        query: str = Field(..., description="Original user query")
        response: str = Field(..., min_length=10, description="AI response content")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
        sources: List[str] = Field(default_factory=list, description="Information sources")
        timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
        
        @field_validator('sources')
        @classmethod
        def validate_sources(cls, v):
            return [source.strip() for source in v if source.strip()]

else:
    # Simple fallback classes without Pydantic
    class UserProfile:
        def __init__(self, name, email, age, interests=None, created_at=None):
            self.name = name
            self.email = email
            self.age = age
            self.interests = interests or []
            self.created_at = created_at or datetime.now()
            
            # Simple validation
            if len(name) < 2 or len(name) > 50:
                raise ValueError("Name must be 2-50 characters")
            if '@' not in email:
                raise ValueError("Email must contain @ symbol")
            if age < 0 or age > 120:
                raise ValueError("Age must be 0-120")
            if len(self.interests) > 10:
                raise ValueError("Too many interests (max 10)")
    
    class Task:
        def __init__(self, id, title, description=None, priority="medium", due_date=None, completed=False):
            self.id = id
            self.title = title
            self.description = description
            self.priority = priority
            self.due_date = due_date
            self.completed = completed
            
            # Simple validation
            if id <= 0:
                raise ValueError("ID must be positive")
            if len(title) < 5 or len(title) > 100:
                raise ValueError("Title must be 5-100 characters")
            if priority not in ['low', 'medium', 'high', 'urgent']:
                raise ValueError("Priority must be low/medium/high/urgent")
            if due_date and due_date < datetime.now():
                raise ValueError("Due date cannot be in the past")
    
    class AIResponse:
        def __init__(self, query, response, confidence, sources=None, timestamp=None):
            self.query = query
            self.response = response
            self.confidence = confidence
            self.sources = sources or []
            self.timestamp = timestamp or datetime.now()
            
            # Simple validation
            if len(response) < 10:
                raise ValueError("Response must be at least 10 characters")
            if confidence < 0.0 or confidence > 1.0:
                raise ValueError("Confidence must be 0.0-1.0")

class ValidationAgent:
    """Agent that uses structured validation for data processing."""
    
    def __init__(self):
        self.llm = get_llm()
    
    def create_user_profile(self, user_data):
        """Create a validated user profile."""
        try:
            if PYDANTIC_AVAILABLE:
                profile = UserProfile(**user_data)
            else:
                profile = UserProfile(**user_data)
            
            print(f"✅ Created valid user profile: {profile.name}")
            return profile
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return None
    
    def create_task(self, task_data):
        """Create a validated task."""
        try:
            if PYDANTIC_AVAILABLE:
                task = Task(**task_data)
            else:
                task = Task(**task_data)
            
            print(f"✅ Created valid task: {task.title}")
            return task
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return None
    
    def generate_structured_response(self, query):
        """Generate a structured AI response with validation."""
        prompt = f"""
        Answer this query: "{query}"
        
        Provide your response in this format:
        Response: [Your detailed response here]
        Confidence: [0.0-1.0 confidence score]
        Sources: [List any sources, one per line]
        """
        
        llm_response = self.llm.generate(prompt).content
        
        # Parse the structured response
        try:
            lines = llm_response.split('\n')
            response_text = ""
            confidence = 0.8
            sources = []
            
            for line in lines:
                if line.startswith('Response:'):
                    response_text = line.replace('Response:', '').strip()
                elif line.startswith('Confidence:'):
                    try:
                        confidence = float(line.replace('Confidence:', '').strip())
                    except:
                        confidence = 0.8
                elif line.startswith('Sources:'):
                    # Get remaining lines as sources
                    source_lines = lines[lines.index(line)+1:]
                    sources = [s.strip() for s in source_lines if s.strip()]
            
            # Create validated response
            if PYDANTIC_AVAILABLE:
                ai_response = AIResponse(
                    query=query,
                    response=response_text,
                    confidence=confidence,
                    sources=sources
                )
            else:
                ai_response = AIResponse(
                    query=query,
                    response=response_text,
                    confidence=confidence,
                    sources=sources
                )
            
            print(f"✅ Generated structured response with confidence {confidence}")
            return ai_response
            
        except Exception as e:
            print(f"❌ Error creating structured response: {e}")
            return None
    
    def validate_data_batch(self, data_list, data_type):
        """Validate a batch of data."""
        valid_items = []
        invalid_items = []
        
        for i, data in enumerate(data_list):
            try:
                if data_type == "user":
                    item = UserProfile(**data)
                elif data_type == "task":
                    item = Task(**data)
                else:
                    continue
                
                valid_items.append(item)
                print(f"✅ Item {i+1}: Valid")
                
            except Exception as e:
                invalid_items.append({"data": data, "error": str(e)})
                print(f"❌ Item {i+1}: {e}")
        
        return {
            "valid": valid_items,
            "invalid": invalid_items,
            "valid_count": len(valid_items),
            "invalid_count": len(invalid_items)
        }

def main():
    print("🔍 Pydantic Validation Pattern")
    print("=" * 50)
    
    # Initialize validation agent
    agent = ValidationAgent()
    print(f"Using LLM: {agent.llm.provider}")
    print(f"Pydantic Available: {'✅ Yes' if PYDANTIC_AVAILABLE else '❌ No'}")
    
    # Test user profile validation
    print(f"\n--- User Profile Validation ---")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "interests": ["Python", "AI", "Machine Learning"]
    }
    
    profile = agent.create_user_profile(user_data)
    if profile:
        print(f"Profile: {profile.name}, Age: {profile.age}, Interests: {profile.interests}")
    
    # Test invalid user data
    print(f"\n--- Testing Invalid User Data ---")
    invalid_user_data = {
        "name": "A",  # Too short
        "email": "invalid-email",  # No @ symbol
        "age": 150,  # Too old
        "interests": ["A"] * 15  # Too many interests
    }
    
    invalid_profile = agent.create_user_profile(invalid_user_data)
    
    # Test task validation
    print(f"\n--- Task Validation ---")
    task_data = {
        "id": 1,
        "title": "Complete AI project",
        "description": "Finish the AI agent implementation",
        "priority": "high",
        "due_date": datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    }
    
    task = agent.create_task(task_data)
    if task:
        print(f"Task: {task.title}, Priority: {task.priority}")
    
    # Test structured AI response
    print(f"\n--- Structured AI Response ---")
    query = "What is machine learning?"
    response = agent.generate_structured_response(query)
    if response:
        print(f"Query: {response.query}")
        print(f"Response: {response.response[:100]}...")
        print(f"Confidence: {response.confidence}")
        print(f"Sources: {response.sources}")
    
    # Test batch validation
    print(f"\n--- Batch Validation ---")
    user_batch = [
        {"name": "Alice", "email": "alice@example.com", "age": 25, "interests": ["AI"]},
        {"name": "Bob", "email": "bob@example.com", "age": 35, "interests": ["Python", "Web Dev"]},
        {"name": "C", "email": "invalid", "age": -5, "interests": []},  # Invalid
        {"name": "Diana", "email": "diana@example.com", "age": 28, "interests": ["Data Science"]}
    ]
    
    batch_result = agent.validate_data_batch(user_batch, "user")
    print(f"Valid: {batch_result['valid_count']}, Invalid: {batch_result['invalid_count']}")
    
    print(f"\n--- Pydantic Validation Summary ---")
    print(f"✅ Demonstrated data validation")
    print(f"✅ Showed structured output generation")
    print(f"✅ Implemented error handling")
    print(f"✅ Created type-safe AI applications")
    if PYDANTIC_AVAILABLE:
        print(f"✅ Used Pydantic for advanced validation")
    else:
        print(f"⚠️ Used simple validation (install Pydantic for advanced features)")

if __name__ == "__main__":
    main()
