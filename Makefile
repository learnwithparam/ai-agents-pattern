# AI Agentic Patterns - Makefile
# Commands for setting up and running the project

.PHONY: help setup venv install clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Set up virtual environment and install dependencies"
	@echo "  venv      - Show how to activate virtual environment"
	@echo "  run       - Run all patterns"
	@echo "  clean     - Clean up virtual environment and cache files"

# Set up virtual environment and install dependencies
setup:
	@echo "Setting up virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Run 'make venv' to activate."

# Show how to activate virtual environment
venv:
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"


# Install dependencies in current environment
install:
	pip install -r requirements.txt

# Clean up
clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Run all patterns
run: activate
	@echo "Running all patterns..."
	. venv/bin/activate && python patterns/01_prompt_chaining.py
	. venv/bin/activate && python patterns/02_routing.py
	. venv/bin/activate && python patterns/03_parallelization.py
	. venv/bin/activate && python patterns/04_reflection.py
	. venv/bin/activate && python patterns/05_tool_calling.py
	. venv/bin/activate && python patterns/06_planning.py
	. venv/bin/activate && python patterns/07_multi_agent.py
	. venv/bin/activate && python patterns/08_memory_management.py
	. venv/bin/activate && python patterns/10_mcp.py
	. venv/bin/activate && python patterns/11_goal_setting.py
	. venv/bin/activate && python patterns/12_exception_handling.py
	. venv/bin/activate && python patterns/13_human_in_loop.py
	. venv/bin/activate && python patterns/14_knowledge_retrieval.py
	. venv/bin/activate && python patterns/15_inter_agent_communication.py
	. venv/bin/activate && python patterns/16_resource_optimization.py
	. venv/bin/activate && python patterns/17a_chain_of_thought.py
	. venv/bin/activate && python patterns/17b_self_correction.py
	. venv/bin/activate && python patterns/17c_problem_decomposition.py
	. venv/bin/activate && python patterns/18_guardrails.py
	. venv/bin/activate && python patterns/19a_evaluation.py
	. venv/bin/activate && python patterns/19b_monitoring.py
	. venv/bin/activate && python patterns/20_prioritization.py
	. venv/bin/activate && python patterns/21_exploration_discovery.py
	. venv/bin/activate && python patterns/22_pydantic_validation.py
	. venv/bin/activate && python patterns/23_agentic_rag.py
	. venv/bin/activate && python patterns/24_workflow_orchestration.py
	. venv/bin/activate && python patterns/25_subgraphs.py
	. venv/bin/activate && python patterns/26_state_machines.py
	. venv/bin/activate && python patterns/27_recursive_agents.py
	. venv/bin/activate && python patterns/28_code_execution.py
	. venv/bin/activate && python patterns/29_query_rewriter.py
	. venv/bin/activate && python patterns/30_relevancy_check.py
	. venv/bin/activate && python patterns/31_data_processing.py
	. venv/bin/activate && python patterns/32_plan_executor.py
	. venv/bin/activate && python patterns/33_anonymization.py

# Run tests
test: activate
	. venv/bin/activate && python -m pytest tests/ -v

# Run linting
lint: activate
	. venv/bin/activate && flake8 examples/ tests/
	. venv/bin/activate && black --check examples/ tests/

# Format code
format: activate
	. venv/bin/activate && black examples/ tests/

# Show activation command
activate:
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"
