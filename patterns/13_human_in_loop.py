#!/usr/bin/env python3
"""
13 - Human-in-the-Loop Pattern
Simple example showing how to integrate human oversight and intervention.

This demonstrates:
1. Automated processing with human oversight
2. Escalation to humans when needed
3. Human feedback integration
4. Hybrid human-AI workflows
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class HumanInTheLoop:
    """Manages human-in-the-loop workflows."""
    
    def __init__(self):
        self.llm = get_llm()
        self.escalation_threshold = 0.7  # Confidence threshold for escalation
        self.pending_reviews = []
        self.human_feedback = {}
    
    def process_request(self, request, confidence_threshold=None):
        """Process a request with human oversight."""
        if confidence_threshold is None:
            confidence_threshold = self.escalation_threshold
        
        print(f"🔄 Processing request: {request}")
        
        # Step 1: AI processes the request
        ai_response, confidence = self._ai_process(request)
        print(f"🤖 AI Response (confidence: {confidence:.2f}): {ai_response}")
        
        # Step 2: Check if human review is needed
        if confidence < confidence_threshold:
            print(f"⚠️ Low confidence ({confidence:.2f} < {confidence_threshold:.2f}) - escalating to human")
            return self._escalate_to_human(request, ai_response, confidence)
        else:
            print(f"✅ High confidence ({confidence:.2f} >= {confidence_threshold:.2f}) - auto-approving")
            return self._auto_approve(ai_response)
    
    def _ai_process(self, request):
        """AI processes the request and returns response with confidence."""
        prompt = f"""
        Process this request: {request}
        
        Provide a response and rate your confidence in the answer (0.0 to 1.0).
        Format your response as:
        RESPONSE: [your response]
        CONFIDENCE: [confidence score]
        """
        
        response = self.llm.generate(prompt).content
        
        # Parse response and confidence
        lines = response.split('\n')
        ai_response = ""
        confidence = 0.5  # Default confidence
        
        for line in lines:
            if line.startswith('RESPONSE:'):
                ai_response = line[9:].strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line[11:].strip())
                except ValueError:
                    confidence = 0.5
        
        return ai_response, confidence
    
    def _escalate_to_human(self, request, ai_response, confidence):
        """Escalate to human for review."""
        review_id = f"review_{len(self.pending_reviews) + 1}"
        
        review_item = {
            "id": review_id,
            "request": request,
            "ai_response": ai_response,
            "confidence": confidence,
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        self.pending_reviews.append(review_item)
        
        # Simulate human review (in real implementation, this would be a UI)
        print(f"👤 Human review required (ID: {review_id})")
        print(f"Request: {request}")
        print(f"AI Response: {ai_response}")
        print(f"Confidence: {confidence:.2f}")
        
        # Simulate human decision
        human_decision = self._simulate_human_review(review_item)
        
        return {
            "status": "human_reviewed",
            "review_id": review_id,
            "final_response": human_decision["response"],
            "human_feedback": human_decision["feedback"]
        }
    
    def _simulate_human_review(self, review_item):
        """Real human review process with user input."""
        print(f"\n👤 Human review required (ID: {review_item['id']})")
        print(f"Request: {review_item['request']}")
        print(f"AI Response: {review_item['ai_response']}")
        print(f"Confidence: {review_item['confidence']}")
        
        print(f"\n🤔 Human Decision Required:")
        print(f"1. Approve as-is")
        print(f"2. Approve with modifications")
        print(f"3. Reject and provide alternative")
        print(f"4. Escalate to specialist")
        
        # Get human decision
        while True:
            try:
                choice = input("\n👤 Your decision (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                else:
                    print("❌ Please enter 1, 2, 3, or 4")
            except KeyboardInterrupt:
                print("\n⚠️ Interrupted. Defaulting to approve as-is.")
                choice = '1'
                break
        
        request = review_item["request"]
        ai_response = review_item["ai_response"]
        
        if choice == '1':
            # Approve as-is
            feedback = "Approved as-is"
            modified_response = ai_response
            print(f"✅ Approved as-is")
            
        elif choice == '2':
            # Approve with modifications
            print(f"📝 Enter your modifications (or press Enter to keep original):")
            modifications = input("Modifications: ").strip()
            if modifications:
                modified_response = f"[HUMAN MODIFIED] {ai_response}\n\nHuman modifications: {modifications}"
                feedback = "Approved with modifications"
            else:
                modified_response = f"[HUMAN APPROVED] {ai_response}"
                feedback = "Approved as-is"
            print(f"✅ Approved with modifications")
            
        elif choice == '3':
            # Reject and provide alternative
            print(f"📝 Enter alternative response:")
            alternative_response = input("Alternative response: ").strip()
            if not alternative_response:
                alternative_response = "I'm unable to provide a suitable response. Please contact our support team."
            modified_response = f"[HUMAN REJECTED] {alternative_response}"
            feedback = "Rejected - provided alternative"
            print(f"❌ Rejected with alternative")
            
        elif choice == '4':
            # Escalate to specialist
            modified_response = "This requires specialized handling. Please contact our specialist team."
            feedback = "Escalated to specialist"
            print(f"🚨 Escalated to specialist")
        
        return {"response": modified_response, "feedback": feedback}
    
    def _auto_approve(self, ai_response):
        """Auto-approve high-confidence responses."""
        return {
            "status": "auto_approved",
            "response": ai_response,
            "human_feedback": "Auto-approved due to high confidence"
        }
    
    def get_pending_reviews(self):
        """Get list of pending human reviews."""
        return [item for item in self.pending_reviews if item["status"] == "pending"]
    
    def add_human_feedback(self, review_id, feedback):
        """Add human feedback to a review."""
        for item in self.pending_reviews:
            if item["id"] == review_id:
                item["human_feedback"] = feedback
                item["status"] = "reviewed"
                break
    
    def get_review_statistics(self):
        """Get statistics about reviews."""
        total = len(self.pending_reviews)
        pending = len(self.get_pending_reviews())
        reviewed = total - pending
        
        return {
            "total_reviews": total,
            "pending_reviews": pending,
            "reviewed": reviewed,
            "escalation_rate": total / max(1, total) * 100
        }

def main():
    print("👤 Human-in-the-Loop Pattern")
    print("=" * 40)
    
    # Initialize human-in-the-loop system
    hitl = HumanInTheLoop()
    
    # Test requests with different complexity levels
    test_requests = [
        "What's the weather like today?",  # Simple - should auto-approve
        "I need urgent help with a critical system failure",  # Urgent - needs human review
        "Can you help me with a complex legal question about contracts?"  # Complex - needs human review
    ]
    
    print("Testing human-in-the-loop processing...")
    
    for i, request in enumerate(test_requests):
        print(f"\n--- Test {i + 1} ---")
        result = hitl.process_request(request)
        
        print(f"Final Result:")
        print(f"Status: {result['status']}")
        print(f"Response: {result['final_response']}")
        print(f"Human Feedback: {result['human_feedback']}")
        print("-" * 40)
    
    # Show review statistics
    print(f"\n--- Review Statistics ---")
    stats = hitl.get_review_statistics()
    print(f"Total reviews: {stats['total_reviews']}")
    print(f"Pending reviews: {stats['pending_reviews']}")
    print(f"Reviewed: {stats['reviewed']}")
    print(f"Escalation rate: {stats['escalation_rate']:.1f}%")
    
    # Show pending reviews
    pending = hitl.get_pending_reviews()
    if pending:
        print(f"\n--- Pending Reviews ---")
        for review in pending:
            print(f"ID: {review['id']}")
            print(f"Request: {review['request']}")
            print(f"Status: {review['status']}")
            print()

if __name__ == "__main__":
    main()
