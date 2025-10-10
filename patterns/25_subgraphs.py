#!/usr/bin/env python3
"""
25 - Subgraphs Pattern
Simple example showing how to use subgraphs for modular AI workflows.

This demonstrates:
1. Creating reusable subgraph components
2. Composing complex workflows from subgraphs
3. Managing state between parent and child graphs
4. Building hierarchical agent systems
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

class SubgraphState:
    """State management for subgraphs."""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        self.history = []
        self.status = "pending"
    
    def update(self, key: str, value: Any):
        """Update state data."""
        self.data[key] = value
        self.history.append(f"Updated {key}: {value}")
    
    def get(self, key: str, default=None):
        """Get state data."""
        return self.data.get(key, default)

class Subgraph:
    """A reusable subgraph component."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = get_llm()
        self.nodes = []
        self.edges = []
    
    def add_node(self, node_name: str, function):
        """Add a node to the subgraph."""
        self.nodes.append({
            "name": node_name,
            "function": function
        })
    
    def add_edge(self, from_node: str, to_node: str, condition=None):
        """Add an edge between nodes."""
        self.edges.append({
            "from": from_node,
            "to": to_node,
            "condition": condition
        })
    
    def execute(self, state: SubgraphState) -> SubgraphState:
        """Execute the subgraph with given state."""
        print(f"🔄 Executing subgraph: {self.name}")
        print(f"📝 Description: {self.description}")
        
        # Execute nodes in sequence (simplified for demo)
        for node in self.nodes:
            print(f"  📍 Node: {node['name']}")
            try:
                result = node['function'](state)
                if result:
                    state.update(f"{node['name']}_result", result)
            except Exception as e:
                print(f"  ❌ Error in {node['name']}: {e}")
                state.update(f"{node['name']}_error", str(e))
        
        state.status = "completed"
        return state

class DataProcessingSubgraph(Subgraph):
    """Subgraph for data processing tasks."""
    
    def __init__(self):
        super().__init__("DataProcessor", "Process and clean input data")
        self._setup_nodes()
    
    def _setup_nodes(self):
        """Setup data processing nodes."""
        
        def validate_input(state):
            """Validate input data."""
            input_data = state.get("input_data", "")
            if not input_data:
                return "No input data provided"
            
            # Simple validation
            if len(input_data) < 3:
                return "Input too short"
            
            return f"Validated input: {len(input_data)} characters"
        
        def clean_data(state):
            """Clean the data."""
            input_data = state.get("input_data", "")
            cleaned = input_data.strip().lower()
            return f"Cleaned data: {cleaned}"
        
        def extract_features(state):
            """Extract features from data."""
            cleaned_data = state.get("clean_data_result", "")
            features = {
                "length": len(cleaned_data),
                "word_count": len(cleaned_data.split()),
                "has_numbers": any(c.isdigit() for c in cleaned_data)
            }
            return features
        
        self.add_node("validate", validate_input)
        self.add_node("clean", clean_data)
        self.add_node("extract", extract_features)

class AnalysisSubgraph(Subgraph):
    """Subgraph for data analysis tasks."""
    
    def __init__(self):
        super().__init__("Analyzer", "Analyze processed data using AI")
        self._setup_nodes()
    
    def _setup_nodes(self):
        """Setup analysis nodes."""
        
        def analyze_sentiment(state):
            """Analyze sentiment of the data."""
            cleaned_data = state.get("clean_data_result", "")
            if not cleaned_data:
                return "No data to analyze"
            
            prompt = f"""
            Analyze the sentiment of this text: "{cleaned_data}"
            
            Respond with one word: POSITIVE, NEGATIVE, or NEUTRAL
            """
            
            response = self.llm.generate(prompt).content
            return f"Sentiment: {response.strip()}"
        
        def generate_summary(state):
            """Generate a summary of the data."""
            cleaned_data = state.get("clean_data_result", "")
            if not cleaned_data:
                return "No data to summarize"
            
            prompt = f"""
            Provide a brief summary of this text: "{cleaned_data}"
            
            Keep it to 1-2 sentences.
            """
            
            response = self.llm.generate(prompt).content
            return f"Summary: {response.strip()}"
        
        def categorize_content(state):
            """Categorize the content."""
            cleaned_data = state.get("clean_data_result", "")
            if not cleaned_data:
                return "No data to categorize"
            
            prompt = f"""
            Categorize this text into one of these categories:
            - NEWS
            - OPINION
            - TECHNICAL
            - PERSONAL
            - OTHER
            
            Text: "{cleaned_data}"
            
            Respond with just the category name.
            """
            
            response = self.llm.generate(prompt).content
            return f"Category: {response.strip()}"
        
        self.add_node("sentiment", analyze_sentiment)
        self.add_node("summary", generate_summary)
        self.add_node("categorize", categorize_content)

class ReportGenerationSubgraph(Subgraph):
    """Subgraph for generating reports."""
    
    def __init__(self):
        super().__init__("ReportGenerator", "Generate comprehensive reports")
        self._setup_nodes()
    
    def _setup_nodes(self):
        """Setup report generation nodes."""
        
        def compile_results(state):
            """Compile all analysis results."""
            results = {
                "features": state.get("extract_result", {}),
                "sentiment": state.get("sentiment_result", ""),
                "summary": state.get("summary_result", ""),
                "category": state.get("categorize_result", "")
            }
            return results
        
        def generate_report(state):
            """Generate final report."""
            results = state.get("compile_result", {})
            if not results:
                return "No results to report"
            
            prompt = f"""
            Generate a comprehensive report based on this analysis:
            
            Features: {results.get('features', {})}
            Sentiment: {results.get('sentiment', '')}
            Summary: {results.get('summary', '')}
            Category: {results.get('category', '')}
            
            Create a well-structured report with sections for each analysis component.
            """
            
            response = self.llm.generate(prompt).content
            return response
        
        def format_output(state):
            """Format the final output."""
            report = state.get("generate_report_result", "")
            if not report:
                return "No report to format"
            
            formatted = f"""
            ========================================
            DATA ANALYSIS REPORT
            ========================================
            
            {report}
            
            ========================================
            Report generated successfully
            ========================================
            """
            return formatted
        
        self.add_node("compile", compile_results)
        self.add_node("generate", generate_report)
        self.add_node("format", format_output)

class SubgraphOrchestrator:
    """Orchestrates multiple subgraphs to create complex workflows."""
    
    def __init__(self):
        self.subgraphs = {}
        self.workflow_history = []
    
    def register_subgraph(self, subgraph: Subgraph):
        """Register a subgraph for use in workflows."""
        self.subgraphs[subgraph.name] = subgraph
        print(f"✅ Registered subgraph: {subgraph.name}")
    
    def execute_workflow(self, workflow_name: str, subgraph_sequence: List[str], initial_data: Dict[str, Any]):
        """Execute a workflow using a sequence of subgraphs."""
        print(f"\n🚀 Starting workflow: {workflow_name}")
        print(f"📋 Subgraph sequence: {' → '.join(subgraph_sequence)}")
        
        # Initialize state
        state = SubgraphState(initial_data)
        self.workflow_history.append({
            "workflow": workflow_name,
            "start_data": initial_data.copy()
        })
        
        # Execute each subgraph in sequence
        for subgraph_name in subgraph_sequence:
            if subgraph_name not in self.subgraphs:
                print(f"❌ Subgraph '{subgraph_name}' not found")
                continue
            
            subgraph = self.subgraphs[subgraph_name]
            state = subgraph.execute(state)
            
            # Pass results to next subgraph
            if state.status == "completed":
                print(f"✅ Completed subgraph: {subgraph_name}")
            else:
                print(f"❌ Failed subgraph: {subgraph_name}")
                break
        
        # Store final results
        self.workflow_history[-1]["final_state"] = state.data
        self.workflow_history[-1]["status"] = state.status
        
        return state
    
    def get_workflow_summary(self):
        """Get summary of all executed workflows."""
        summary = f"""
        📊 Workflow Execution Summary
        ============================
        Total Workflows: {len(self.workflow_history)}
        
        """
        
        for i, workflow in enumerate(self.workflow_history, 1):
            status_icon = "✅" if workflow["status"] == "completed" else "❌"
            summary += f"{status_icon} Workflow {i}: {workflow['workflow']}\n"
        
        return summary

def main():
    print("🔗 Subgraphs Pattern")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = SubgraphOrchestrator()
    
    # Create and register subgraphs
    data_processor = DataProcessingSubgraph()
    analyzer = AnalysisSubgraph()
    report_generator = ReportGenerationSubgraph()
    
    orchestrator.register_subgraph(data_processor)
    orchestrator.register_subgraph(analyzer)
    orchestrator.register_subgraph(report_generator)
    
    # Test data
    test_inputs = [
        "This is a wonderful day! I love the sunny weather and feel so happy.",
        "The technical documentation is comprehensive and well-structured.",
        "I'm not sure about this decision. It seems risky and uncertain."
    ]
    
    # Execute workflows
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_input[:50]}...")
        print(f"{'='*60}")
        
        # Execute complete workflow
        result = orchestrator.execute_workflow(
            f"Analysis Workflow {i}",
            ["DataProcessor", "Analyzer", "ReportGenerator"],
            {"input_data": test_input}
        )
        
        # Show final output
        final_report = result.get("format_result", "No report generated")
        print(f"\n📄 Final Report:")
        print(final_report)
    
    # Show workflow summary
    print(f"\n{orchestrator.get_workflow_summary()}")
    
    print(f"\n--- Subgraphs Pattern Summary ---")
    print(f"✅ Demonstrated modular subgraph components")
    print(f"✅ Showed workflow composition from subgraphs")
    print(f"✅ Implemented state management between subgraphs")
    print(f"✅ Created hierarchical agent system architecture")

if __name__ == "__main__":
    main()
