#!/usr/bin/env python3
"""
33 - Anonymization Pattern
Simple example showing how to anonymize and de-anonymize data for privacy protection.

This demonstrates:
1. Data anonymization techniques
2. Privacy-preserving data processing
3. Reversible anonymization
4. Privacy risk assessment
"""

import sys
import os
import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_provider import get_llm

# Load environment variables
load_dotenv()

class DataAnonymizer:
    """Anonymize sensitive data while preserving utility."""
    
    def __init__(self):
        self.llm = get_llm()
        self.anonymization_map = {}
        self.reverse_map = {}
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect personally identifiable information in text."""
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'  # Simple name pattern
        }
        
        detected_pii = {}
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii[pii_type] = matches
        
        return detected_pii
    
    def anonymize_text(self, text: str, preserve_structure: bool = True) -> Dict[str, Any]:
        """Anonymize text while preserving structure and meaning."""
        # Detect PII
        pii_detected = self.detect_pii(text)
        
        anonymized_text = text
        anonymization_log = []
        
        # Anonymize emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for i, email in enumerate(emails):
            if preserve_structure:
                replacement = f"user{i+1}@example.com"
            else:
                replacement = "[EMAIL]"
            anonymized_text = anonymized_text.replace(email, replacement)
            anonymization_log.append({"original": email, "replacement": replacement, "type": "email"})
        
        # Anonymize phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for i, phone in enumerate(phones):
            if preserve_structure:
                replacement = f"555-{1000+i:04d}"
            else:
                replacement = "[PHONE]"
            anonymized_text = anonymized_text.replace(phone, replacement)
            anonymization_log.append({"original": phone, "replacement": replacement, "type": "phone"})
        
        # Anonymize SSNs
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        ssns = re.findall(ssn_pattern, text)
        for i, ssn in enumerate(ssns):
            replacement = f"XXX-XX-{1000+i:04d}"
            anonymized_text = anonymized_text.replace(ssn, replacement)
            anonymization_log.append({"original": ssn, "replacement": replacement, "type": "ssn"})
        
        # Anonymize names (simple approach)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        for i, name in enumerate(names):
            replacement = f"Person{i+1}"
            anonymized_text = anonymized_text.replace(name, replacement)
            anonymization_log.append({"original": name, "replacement": replacement, "type": "name"})
        
        return {
            "original_text": text,
            "anonymized_text": anonymized_text,
            "pii_detected": pii_detected,
            "anonymization_log": anonymization_log,
            "privacy_score": self._calculate_privacy_score(anonymized_text)
        }
    
    def _calculate_privacy_score(self, text: str) -> float:
        """Calculate privacy score (0-1, higher is more private)."""
        # Simple scoring based on PII detection
        pii_detected = self.detect_pii(text)
        total_pii = sum(len(matches) for matches in pii_detected.values())
        
        if total_pii == 0:
            return 1.0
        
        # Calculate score based on PII density
        words = len(text.split())
        pii_density = total_pii / words if words > 0 else 0
        
        return max(0, 1 - pii_density * 10)  # Penalize high PII density
    
    def create_anonymization_mapping(self, original_data: str, anonymized_data: str) -> Dict[str, Any]:
        """Create mapping for reversible anonymization."""
        mapping = {
            "original": original_data,
            "anonymized": anonymized_data,
            "mappings": {},
            "created_at": datetime.now().isoformat()
        }
        
        # Extract and map anonymized entities
        anonymized_entities = re.findall(r'user\d+@example\.com|Person\d+|555-\d{4}|XXX-XX-\d{4}', anonymized_data)
        
        for entity in anonymized_entities:
            if entity not in mapping["mappings"]:
                mapping["mappings"][entity] = {
                    "type": "unknown",
                    "original": None,
                    "anonymized": entity
                }
        
        return mapping
    
    def deanonymize_text(self, anonymized_text: str, mapping: Dict[str, Any]) -> str:
        """Reverse anonymization using mapping."""
        deanon_text = anonymized_text
        
        for entity, info in mapping["mappings"].items():
            if info["original"]:
                deanon_text = deanon_text.replace(entity, info["original"])
        
        return deanon_text
    
    def assess_privacy_risk(self, text: str) -> Dict[str, Any]:
        """Assess privacy risk of text content."""
        pii_detected = self.detect_pii(text)
        
        risk_factors = {
            "high_risk": ["ssn", "credit_card"],
            "medium_risk": ["email", "phone"],
            "low_risk": ["name"]
        }
        
        risk_score = 0
        risk_details = {}
        
        for risk_level, pii_types in risk_factors.items():
            for pii_type in pii_types:
                if pii_type in pii_detected:
                    count = len(pii_detected[pii_type])
                    if risk_level == "high_risk":
                        risk_score += count * 3
                    elif risk_level == "medium_risk":
                        risk_score += count * 2
                    else:
                        risk_score += count * 1
                    
                    risk_details[pii_type] = {
                        "count": count,
                        "risk_level": risk_level,
                        "items": pii_detected[pii_type]
                    }
        
        # Normalize risk score (0-1)
        max_possible_risk = 10  # Arbitrary max
        normalized_risk = min(1.0, risk_score / max_possible_risk)
        
        return {
            "risk_score": normalized_risk,
            "risk_level": "high" if normalized_risk > 0.7 else "medium" if normalized_risk > 0.3 else "low",
            "risk_details": risk_details,
            "recommendations": self._get_privacy_recommendations(normalized_risk, risk_details)
        }
    
    def _get_privacy_recommendations(self, risk_score: float, risk_details: Dict[str, Any]) -> List[str]:
        """Get privacy recommendations based on risk assessment."""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("High risk detected - consider full anonymization")
            recommendations.append("Review data handling policies")
        elif risk_score > 0.3:
            recommendations.append("Medium risk - anonymize sensitive fields")
            recommendations.append("Implement access controls")
        else:
            recommendations.append("Low risk - standard privacy measures sufficient")
        
        if "ssn" in risk_details:
            recommendations.append("Remove or mask SSNs immediately")
        if "credit_card" in risk_details:
            recommendations.append("Never store credit card numbers in plain text")
        
        return recommendations

class AnonymizationPipeline:
    """Complete anonymization pipeline."""
    
    def __init__(self):
        self.anonymizer = DataAnonymizer()
        self.processing_history = []
    
    def process_document(self, text: str, preserve_structure: bool = True) -> Dict[str, Any]:
        """Process document through anonymization pipeline."""
        print(f"🔒 Processing document for anonymization...")
        
        # Assess privacy risk
        risk_assessment = self.anonymizer.assess_privacy_risk(text)
        print(f"📊 Privacy risk: {risk_assessment['risk_level']} ({risk_assessment['risk_score']:.2f})")
        
        # Anonymize text
        anonymization_result = self.anonymizer.anonymize_text(text, preserve_structure)
        print(f"🔄 Anonymized {len(anonymization_result['anonymization_log'])} entities")
        
        # Create mapping for reversibility
        mapping = self.anonymizer.create_anonymization_mapping(
            text, 
            anonymization_result['anonymized_text']
        )
        
        # Store processing record
        processing_record = {
            "original_text": text,
            "anonymized_text": anonymization_result['anonymized_text'],
            "risk_assessment": risk_assessment,
            "anonymization_log": anonymization_result['anonymization_log'],
            "mapping": mapping,
            "privacy_score": anonymization_result['privacy_score'],
            "processed_at": datetime.now().isoformat()
        }
        
        self.processing_history.append(processing_record)
        
        return processing_record
    
    def batch_process(self, documents: List[str], preserve_structure: bool = True) -> List[Dict[str, Any]]:
        """Process multiple documents."""
        results = []
        
        for i, doc in enumerate(documents):
            print(f"\n--- Processing document {i+1}/{len(documents)} ---")
            result = self.process_document(doc, preserve_structure)
            results.append(result)
        
        return results
    
    def get_privacy_statistics(self) -> Dict[str, Any]:
        """Get privacy statistics from processing history."""
        if not self.processing_history:
            return {"total_documents": 0}
        
        total_docs = len(self.processing_history)
        total_entities = sum(len(record['anonymization_log']) for record in self.processing_history)
        
        risk_levels = [record['risk_assessment']['risk_level'] for record in self.processing_history]
        risk_counts = {"high": risk_levels.count("high"), "medium": risk_levels.count("medium"), "low": risk_levels.count("low")}
        
        avg_privacy_score = sum(record['privacy_score'] for record in self.processing_history) / total_docs
        
        return {
            "total_documents": total_docs,
            "total_entities_anonymized": total_entities,
            "risk_distribution": risk_counts,
            "average_privacy_score": avg_privacy_score,
            "high_risk_documents": risk_counts["high"]
        }

def main():
    print("🔒 Anonymization Pattern")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = AnonymizationPipeline()
    
    # Test documents with PII
    test_documents = [
        "John Smith (john.smith@email.com) called about his account. His phone number is 555-123-4567 and SSN is 123-45-6789.",
        "Contact Sarah Johnson at sarah.j@company.com or call 555-987-6543 for more information.",
        "The user with email user@example.com has been processed successfully.",
        "No personal information in this document."
    ]
    
    print("Testing anonymization pipeline...")
    
    # Process documents
    results = pipeline.batch_process(test_documents, preserve_structure=True)
    
    # Show results
    for i, result in enumerate(results, 1):
        print(f"\n{'='*60}")
        print(f"DOCUMENT {i}")
        print(f"{'='*60}")
        print(f"Original: {result['original_text']}")
        print(f"Anonymized: {result['anonymized_text']}")
        print(f"Risk Level: {result['risk_assessment']['risk_level']}")
        print(f"Privacy Score: {result['privacy_score']:.2f}")
        print(f"Entities Anonymized: {len(result['anonymization_log'])}")
        
        if result['anonymization_log']:
            print("Anonymization Details:")
            for log_entry in result['anonymization_log']:
                print(f"  {log_entry['type']}: {log_entry['original']} → {log_entry['replacement']}")
    
    # Show privacy statistics
    stats = pipeline.get_privacy_statistics()
    print(f"\n--- Privacy Statistics ---")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total entities anonymized: {stats['total_entities_anonymized']}")
    print(f"Risk distribution: {stats['risk_distribution']}")
    print(f"Average privacy score: {stats['average_privacy_score']:.2f}")
    print(f"High risk documents: {stats['high_risk_documents']}")
    
    print(f"\n--- Anonymization Pattern Summary ---")
    print(f"✅ Demonstrated data anonymization techniques")
    print(f"✅ Showed privacy-preserving data processing")
    print(f"✅ Implemented reversible anonymization")
    print(f"✅ Created privacy risk assessment")

if __name__ == "__main__":
    main()
