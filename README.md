# AI Agentic Patterns

**AI Agent Patterns** for bootcamp students. Each pattern is a single, focused file demonstrating core agentic AI concepts. Works with OpenAI, Gemini, Claude, Fireworks AI, Mistral, and Ollama.

## 🚀 Ready to Build Production AI Systems?

These patterns are just the beginning. If you want to master **production-ready AI engineering** and build real applications that users love, check out my **AI Bootcamp for Software Engineers**.

![AI Bootcamp for Software Engineers](https://learnwithparam.com/og-image.jpg)

### 🎁 Special GitHub Discount:
**Use code `GITHUB300` for €300 off** the AI Bootcamp for Software Engineers!

**Next Cohort**: November 3rd, 2025

[**Enroll Now with GITHUB300 Discount**](https://www.learnwithparam.com/ai-engineering-bootcamp)

---

*This repository contains the foundational patterns you'll master in the bootcamp. Ready to go from demos to production? Join the next cohort!*

## 🚀 Quick Start

```bash
# 1. Setup
make setup

# 2. Add API key (or use Ollama locally)
cp env.example .env
# Edit .env and add your API key

# 3. Run all patterns
make run

# 4. Or run individual patterns
python patterns/01_prompt_chaining.py
python patterns/02_routing.py
python patterns/03_parallelization.py
```

## 📁 All AI Agentic Patterns

### 🏗️ Foundation Patterns (1-8)
- **01_prompt_chaining.py** - Chain prompts together
  - *Automated RFP writer that extracts requirements from client brief → summarizes key needs → generates full proposal draft with cover letter and deliverables*
  - *FAQ summarizer that extracts answers from docs → reformats → writes human-friendly version*
- **02_routing.py** - Route requests to different handlers  
  - *Customer service triage that routes incoming messages to "refunds", "shipping", or "technical" LLM sub-agents for specialized responses*
  - *In-app chatbot that detects sentiment → routes angry users to human escalation pipeline*
- **03_parallelization.py** - Run multiple LLM calls in parallel
  - *SEO content pipeline that generates meta title, meta description, blog intro, and social post captions simultaneously*
  - *Resume enhancer that parallel-generates versions optimized for LinkedIn, ATS, and portfolio*
- **04_reflection.py** - Use reflection to improve code/output quality
  - *Autonomous code reviewer that generates code → reviews it for style/performance → regenerates improved version*
  - *Blog summarizer that re-evaluates tone ("too formal?" → "rewrite in friendlier tone")*
- **05_tool_calling.py** - Use tools with LLMs
  - *Smart operations assistant that can fetch Jira tickets, query database metrics, and trigger Slack updates via tool APIs*
  - *Calendar assistant that uses a "schedule" tool to book meetings from natural text*
- **06_planning.py** - Break down complex tasks into plans
  - *Marketing campaign planner that creates multi-step plan with timelines and assets needed for "launch new product" goal*
  - *Travel planner that turns "3 days in Rome" into structured itinerary*
- **07_multi_agent.py** - Coordinate multiple AI agents
  - *AI newsroom with reporter agent drafting story → editor agent refining tone → fact-checker agent verifying sources*
  - *Video creation bot with separate agents for script, voiceover, and thumbnail*
- **08_memory_management.py** - Manage conversation memory and context
  - *AI career coach that remembers user's goals, prior feedback, and performance over time to offer context-aware coaching*
  - *Customer chatbot that remembers user preferences (size, brand, last order)*

### 🔧 Advanced Patterns (10-16)
- **10_mcp.py** - Use external tools via Model Context Protocol
  - *Enterprise assistant that interacts with CRM, internal wiki, and file servers securely via standardized protocol*
  - *AI that can query Notion, Jira, and Google Drive seamlessly using MCP connectors*
- **11_goal_setting.py** - Set goals and monitor progress
  - *Sales enablement AI that sets quarterly sales targets, tracks progress, and suggests next best actions*
  - *Habit tracker AI that checks daily progress and adjusts reminders dynamically*
- **12_exception_handling.py** - Handle exceptions and recover gracefully
  - *Financial automation bot that handles failed API calls or invalid data by retrying, alerting, or falling back to cached data*
  - *Chatbot that detects "API unavailable" and apologizes with an alternate response*
- **13_human_in_loop.py** - Integrate human oversight and intervention
  - *Legal AI that drafts contracts and flags ambiguous clauses for lawyer review*
  - *Social media moderator AI that sends uncertain posts to a human for manual approval*
- **14_knowledge_retrieval.py** - Retrieve and use domain knowledge
  - *Customer success AI that answers queries using company-specific knowledge base + recent case studies*
  - *AI that looks up specific product specs or FAQ answers before replying*
- **15_inter_agent_communication.py** - Enable communication between agents
  - *Smart factory system where maintenance agent reports sensor issues → logistics agent orders parts → scheduler agent delays affected lines*
  - *Fitness coach AI coordinating with nutrition agent to align meal and workout plans*
- **16_resource_optimization.py** - Optimize compute/resources
  - *Multi-tenant AI SaaS that dynamically adjusts LLM model size based on user tier or query complexity*
  - *Chatbot that uses GPT-4 for "creative writing" and GPT-3.5 for "FAQ lookup"*

### 🧠 Reasoning Patterns (17a-17c)
- **17a_chain_of_thought.py** - Show reasoning steps
  - *AI math grader that solves student problem step-by-step and checks each reasoning step*
  - *Expense classifier showing reasoning for why a transaction is "travel" vs "meals"*
- **17b_self_correction.py** - Self-validation and repair
  - *Codegen AI that generates script → runs unit test → debugs based on output automatically*
  - *Text summarizer that re-checks if summary misses any key entity*
- **17c_problem_decomposition.py** - Break complex problems into parts
  - *Startup advisor AI that breaks "launch a product" into market research, MVP, and growth phases*
  - *Homework helper that splits a multi-step word problem before solving*

### 🛡️ Safety & Quality Patterns (18-19b)
- **18_guardrails.py** - Implement content/policy filters
  - *AI writing assistant that filters confidential data, PII, or bias-inducing terms before output*
  - *Prevents profanity or misinformation in AI-generated tweets*
- **19a_evaluation.py** - Evaluate LLM output
  - *AI tutor QA system that grades AI explanations based on clarity, correctness, and engagement*
  - *Automated prompt evaluator scoring outputs for fluency and factuality*
- **19b_monitoring.py** - Monitor agent performance
  - *AI customer support dashboard that tracks response latency, satisfaction scores, and escalation rates*
  - *Alerts when AI's error rate exceeds threshold or response time spikes*

### 📊 Management Patterns (20-22)
- **20_prioritization.py** - Manage task queues
  - *AI ops scheduler that prioritizes background jobs based on urgency, dependency, and ROI*
  - *Email assistant that prioritizes unread emails by importance (CEO > newsletter)*
- **21_exploration_discovery.py** - Explore unknowns
  - *R&D assistant that finds unexplored research areas and relevant citations automatically*
  - *News summarizer that surfaces trending but underreported stories*
- **22_pydantic_validation.py** - Data schema validation
  - *LLM data ingestion pipeline that validates structured outputs (JSON, schema-bound fields) before storing*
  - *API wrapper that ensures AI responses fit a strict ProductSchema*

### 🚀 System Patterns (23-28)
- **23_agentic_rag.py** - Agentic retrieval-augmented generation
  - *Corporate knowledge AI that fetches from internal docs, emails, and dashboards, then synthesizes actionable insight*
  - *AI that answers "What did we discuss last meeting?" by retrieving meeting notes*
- **24_workflow_orchestration.py** - Orchestrate complex flows
  - *Automated video production system with script writer → voiceover → visual generation → upload*
  - *Job application AI that drafts resume → tailors cover letter → applies automatically*
- **25_subgraphs.py** - Modular AI components
  - *AI architecture library with reusable subgraphs for parsing input, enriching context, and output formatting*
  - *Plug-in LLM component that handles summarization across different workflows*
- **26_state_machines.py** - Finite state workflow logic
  - *Loan processing system that transitions between "application submitted → under review → approved → funded"*
  - *Conversational flow that tracks user from greeting → query → solution → feedback*
- **27_recursive_agents.py** - Self-referencing reasoning
  - *Research planner AI that recursively delegates subtasks like literature review → summarization → synthesis*
  - *Debugging AI that recursively investigates root causes in logs*
- **28_code_execution.py** - Safely run generated code
  - *Data analyst copilot that generates code to compute KPIs, runs safely in sandbox, and returns results*
  - *Spreadsheet assistant that writes & executes formulas based on user queries*

## 🔧 API Keys

Add at least one to your `.env` file:

```bash
OPENAI_API_KEY=your_key_here      # Most common
GOOGLE_API_KEY=your_key_here      # Free tier available
ANTHROPIC_API_KEY=your_key_here   # Claude models
FIREWORKS_API_KEY=your_key_here   # Fast inference
MISTRAL_API_KEY=your_key_here     # European models
# Ollama: No API key needed (local)
```

## 💡 What You'll Learn

### 🏗️ Foundation Concepts
1. **Prompt Chaining** - Break complex tasks into steps
2. **Routing** - Smart delegation based on request type
3. **Parallelization** - Speed up multiple LLM calls
4. **Reflection** - Improve code quality through self-review
5. **Tool Calling** - Use external tools with LLMs
6. **Planning** - Break down complex tasks into structured plans
7. **Multi-Agent** - Coordinate multiple specialized agents
8. **Memory Management** - Manage conversation context and user preferences

### 🔧 Advanced Techniques
9. **MCP** - Connect to external tools via Model Context Protocol
10. **Goal Setting** - Set and track progress toward objectives
11. **Exception Handling** - Handle errors and recover gracefully
12. **Human-in-the-Loop** - Integrate human oversight and intervention
13. **Knowledge Retrieval** - Use RAG for better responses
14. **Inter-Agent Communication** - Enable agents to work together
15. **Resource Optimization** - Optimize for cost vs performance

### 🧠 Reasoning & Problem Solving
16. **Chain-of-Thought** - Step-by-step reasoning process
17. **Self-Correction** - Review and improve solutions
18. **Problem Decomposition** - Break down complex problems

### 🛡️ Safety & Quality Assurance
19. **Guardrails** - Implement safety and content filtering
20. **Evaluation** - Assess AI response quality and safety
21. **Monitoring** - Track performance and behavior metrics

### 📊 Management & Organization
22. **Prioritization** - Manage tasks and workload intelligently
23. **Exploration & Discovery** - Research and knowledge discovery
24. **Pydantic Validation** - Type-safe data validation

### 🚀 System Architecture
25. **Agentic RAG** - Intelligent retrieval-augmented generation
26. **Workflow Orchestration** - Coordinate complex AI workflows
27. **Subgraphs** - Create modular, reusable components
28. **State Machines** - Implement event-driven agent behavior
29. **Recursive Agents** - Build self-referencing AI systems
30. **Code Execution** - Safely execute code with AI agents

### 🔄 RAG Pipeline Patterns
- **29_query_rewriter.py** - Rewrite and optimize queries for better retrieval
  - *Search engine that rewrites user queries to improve results: "how to code" → "Python programming tutorial for beginners"*
  - *Customer support that expands vague questions into specific, actionable queries*
- **30_relevancy_check.py** - Check and filter relevant information
  - *Content moderation system that scores articles for relevance to user interests*
  - *Research assistant that filters academic papers by relevance to research topic*
- **31_data_processing.py** - Process and structure data for RAG systems
  - *Document processor that cleans, chunks, and structures PDFs for knowledge base*
  - *Data pipeline that transforms raw text into searchable, categorized content*
- **32_plan_executor.py** - Execute structured plans with monitoring
  - *Project management AI that breaks down tasks into steps and tracks progress*
  - *Workflow automation that executes complex business processes step-by-step*
- **33_anonymization.py** - Anonymize and de-anonymize data for privacy
  - *Healthcare system that removes patient names while preserving medical data*
  - *Customer data processor that anonymizes PII for analytics while maintaining reversibility*

## 🎯 Supported Providers

- **OpenAI** - GPT models (most common)
- **Google Gemini** - Free tier available
- **Anthropic Claude** - Advanced reasoning
- **Fireworks AI** - Fast inference
- **Mistral** - European models
- **Ollama** - Local models (no API key needed)

The system auto-detects available providers and works offline with Ollama!

## 📚 Learning Approach

**Each pattern is a single, focused file** - perfect for bootcamp students:

- ✅ **One concept per file** - No cognitive overload
- ✅ **Self-contained** - Each pattern runs independently  
- ✅ **Simple & clear** - Easy to understand and modify
- ✅ **Progressive complexity** - Build from basics to advanced
- ✅ **Real examples** - Working code you can run immediately

## 🎯 Perfect For

- **Bootcamp Students** - Progressive learning with single-file patterns
- **AI Developers** - Quick reference for common agentic patterns
- **Educators** - Ready-to-use examples for teaching
- **Researchers** - Foundation for building complex AI systems

## 🚀 Next Steps

1. **Start with Foundation** - Run patterns 01-08 first
2. **Explore Advanced** - Try patterns 10-16 for complex behaviors
3. **Master Reasoning** - Practice patterns 17a-17c for better AI thinking
4. **Build Systems** - Combine patterns 23-28 for production systems
5. **Master RAG** - Learn patterns 29-33 for advanced retrieval systems

## 🎓 Ready to Go Beyond Patterns?

These patterns are just the foundation. To build **production-ready AI systems** that solve real business problems, join the **AI Bootcamp for Software Engineers**.

### Why Join the Bootcamp?
- **6 weeks** of hands-on learning with live sessions
- **Production-ready AI projects** you'll build and deploy
- **Expert support** from Param Harrison (15+ years engineering experience)
- **Real applications** like voice assistants, research agents, and automated workflows
- **Production focus** - not just demos, but systems that scale

### 🎁 GitHub Community Special:
**Use code `GITHUB300` for €300 off!**

**Next Cohort**: November 3rd, 2025

[**Enroll Now**](https://www.learnwithparam.com/ai-engineering-bootcamp) | [**Download Syllabus**](https://www.learnwithparam.com/ai-engineering-bootcamp)

---

*Perfect for bootcamp students learning AI agent development. Ready to build production systems? Join the next cohort!*