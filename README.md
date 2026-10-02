# Agentic UPI Payments Operations & Investigation Copilot

An **Agentic AI system for UPI-like payment operations and failure
investigation**, built with **LangGraph, local LLMs through Ollama,
SQLite, ChromaDB, Sentence Transformers, and MCP**.

The project is designed as an engineering-focused demonstration of how
an AI agent can move beyond a simple chatbot and perform a controlled
operational workflow:

**Understand the request → select the workflow → retrieve verified
transaction evidence → retrieve operational knowledge → investigate →
validate the reasoning → retry when validation fails → generate an
incident report → request human approval → create a simulated incident
only when approved.**

The system uses **synthetic payment data and synthetic operational
documentation** so that the project can demonstrate the architecture
without exposing real payment or customer information.

------------------------------------------------------------------------

## Table of Contents

-   [Why This Project](#why-this-project)
-   [Problem Statement](#problem-statement)
-   [What the System Does](#what-the-system-does)
-   [Architecture](#architecture)
-   [End-to-End Request Flow](#end-to-end-request-flow)
-   [Project Structure](#project-structure)
-   [Core Components](#core-components)
-   [Agent and Workflow Design](#agent-and-workflow-design)
-   [Data and Database Layer](#data-and-database-layer)
-   [RAG and Operational Knowledge](#rag-and-operational-knowledge)
-   [Grounded Investigation and
    Guardrails](#grounded-investigation-and-guardrails)
-   [Human-in-the-Loop Safety](#human-in-the-loop-safety)
-   [MCP Integration](#mcp-integration)
-   [Evaluation Framework](#evaluation-framework)
-   [Evaluation Results](#evaluation-results)
-   [Performance Benchmark](#performance-benchmark)
-   [Challenges Faced and Engineering
    Decisions](#challenges-faced-and-engineering-decisions)
-   [Key Design Decisions](#key-design-decisions)
-   [Limitations](#limitations)
-   [Tech Stack](#tech-stack)
-   [Setup](#setup)
-   [Running the Project](#running-the-project)
-   [Example Workflow](#example-workflow)
-   [Testing](#testing)
-   [Future Improvements](#future-improvements)
-   [Project Positioning](#project-positioning)

------------------------------------------------------------------------

## Why This Project

Payment operations teams frequently need to answer questions such as:

-   What is the current payment success rate?
-   Why are payments failing?
-   Which failure reasons are most common?
-   Which sender or receiver banks have the most failures?
-   What operational guidance applies to a particular failure code?
-   What should be investigated next?
-   Can an investigation be converted into an incident?

A conventional chatbot can generate an answer, but an operational system
needs stronger guarantees around:

-   **verified data**
-   **controlled tool usage**
-   **retrieval of relevant operational knowledge**
-   **grounded reasoning**
-   **validation of generated conclusions**
-   **recovery from validation failures**
-   **human approval before consequential actions**

This project focuses on those engineering concerns.

------------------------------------------------------------------------

# Problem Statement

The goal is to build a small but realistic **PayOps investigation
copilot** that can combine structured transaction data, operational
documentation, deterministic analytics, an LLM, workflow orchestration,
validation, and human approval.

The project intentionally does **not** attempt to diagnose real payment
infrastructure or access production systems.

Instead, it creates a reproducible environment where the complete
agentic workflow can be developed and evaluated safely.

------------------------------------------------------------------------

# What the System Does

The system supports five high-level request intents:

  Intent               Example
  -------------------- ----------------------------------------
  `SUCCESS_RATE`       "What is the payment success rate?"
  `FAILURE_ANALYSIS`   "Why are payments failing?"
  `BANK_ANALYSIS`      "Which bank has the most failures?"
  `INVESTIGATION`      "Investigate why payments are failing"
  `OUT_OF_SCOPE`       "What is the weather today?"

For simple analytical requests, the router sends the request directly to
the appropriate deterministic tool.

For an investigation request, LangGraph executes a multi-step workflow.

------------------------------------------------------------------------

# Architecture

``` text
                         USER QUESTION
                              |
                              v
                    +--------------------+
                    |      PLANNER       |
                    | Intent Selection   |
                    +---------+----------+
                              |
               +--------------+--------------+
               |              |              |
               v              v              v
        SUCCESS_RATE   FAILURE_ANALYSIS  BANK_ANALYSIS
               |              |              |
               v              v              v
          Analytics       Failure Tool     Bank Tool
               |              |              |
               +--------------+--------------+
                              |
                         INVESTIGATION
                              |
                              v
                 +------------------------+
                 |     INVESTIGATION      |
                 |        GRAPH           |
                 +-----------+------------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
       Transaction Data              Operational Knowledge
          / SQLite                    / RAG + ChromaDB
              |                             |
              +--------------+--------------+
                             |
                             v
                    Investigation Agent
                      Local LLM/Ollama
                             |
                             v
                     Validation / Guardrails
                             |
                    +--------+--------+
                    |                 |
                  VALID           INVALID
                    |                 |
                    v                 v
                  Report            Retry
                    |                 |
                    v                 |
             Human Approval <---------+
                    |
             +------+------+
             |             |
          APPROVED       REJECTED
             |             |
             v             v
      Simulated Incident  BLOCKED
```

------------------------------------------------------------------------

# End-to-End Request Flow

Consider:

> **"Investigate why payments are failing."**

The request follows this path.

### 1. Planner

The planner determines that the request is an:

``` text
INVESTIGATION
```

The planner uses deterministic keyword rules for known operational
intents and a local Ollama LLM fallback for broader classification.

Unknown or invalid classifications fail closed to:

``` text
OUT_OF_SCOPE
```

This prevents unrelated requests from entering the operational workflow.

------------------------------------------------------------------------

### 2. Transaction Evidence

The investigation workflow invokes the data layer.

The data agent retrieves the relevant failure summary from SQLite.

Example verified evidence:

``` text
Total failed transactions: 8

TIMEOUT:              3
INSUFFICIENT_FUNDS:   2
BANK_ERROR:           2
TECHNICAL_ERROR:      1
```

The system does not ask the LLM to calculate these numbers.

The calculations are performed deterministically by Python/database
logic.

------------------------------------------------------------------------

### 3. Evidence Construction

The raw database result is converted into structured evidence.

For example:

``` text
total_failed = 8
most_common_failure_reason = TIMEOUT
most_common_failure_count = 3
most_common_failure_percentage = 37.5%
```

This creates a clean boundary between:

**verified facts** and **LLM interpretation**.

------------------------------------------------------------------------

### 4. Operational Knowledge Retrieval

The system identifies the observed failure codes and queries the
operational knowledge base.

The RAG pipeline is:

``` text
Operational document
        |
        v
Document loader
        |
        v
Chunking
        |
        v
Sentence Transformer embeddings
        |
        v
ChromaDB
        |
        v
Similarity retrieval
```

For the example above, knowledge related to:

``` text
TIMEOUT
INSUFFICIENT_FUNDS
BANK_ERROR
TECHNICAL_ERROR
```

can be retrieved.

The knowledge base provides definitions and investigation guidance.

It is deliberately treated as **operational guidance, not transaction
evidence**.

------------------------------------------------------------------------

### 5. Investigation Agent

The local LLM receives:

-   verified transaction evidence
-   retrieved operational knowledge
-   optional validation feedback from a previous attempt

The investigation response is constrained to four sections:

``` text
OBSERVED EVIDENCE
INTERPRETATION
LIMITATIONS
NEXT INVESTIGATION
```

The prompt explicitly prevents the model from inventing unsupported
causes.

For example, the model should not turn:

``` text
TIMEOUT occurred 3 times
```

into:

``` text
The network caused the failures.
```

The available evidence does not establish that causal relationship.

------------------------------------------------------------------------

### 6. Validation

The generated investigation is passed through deterministic guardrails.

The validator checks for issues such as:

-   unsupported numbers
-   unsupported percentages
-   unsupported relationships
-   unsupported causal claims
-   unsupported infrastructure claims
-   missing required sections

For example, this should fail validation:

``` text
The network outage caused the TIMEOUT failures.
```

The validator therefore acts as a second layer between the LLM and
downstream operational actions.

------------------------------------------------------------------------

### 7. Retry

If validation fails, the graph can retry the investigation.

The validation errors are passed back to the investigation agent as
feedback.

The current workflow allows one retry before ending the recovery path.

This makes the system more than a simple:

``` text
LLM -> answer
```

pipeline.

It becomes:

``` text
LLM
 |
 v
Validate
 |
 +---- valid ------> continue
 |
 +---- invalid ----> retry with feedback
```

------------------------------------------------------------------------

### 8. Incident Report

Once the investigation passes validation, the system creates a
structured incident report containing:

-   question
-   verified evidence
-   investigation
-   draft status
-   human-review requirement

The report is still treated as a draft at this stage.

------------------------------------------------------------------------

### 9. Human Approval

Before incident creation, the workflow reaches a human approval
boundary.

Two possible paths exist:

``` text
APPROVED
   |
   v
Incident creation allowed
```

or:

``` text
REJECTED
   |
   v
Incident creation blocked
```

This is an intentional safety boundary.

The AI does not independently decide that a consequential operational
action should happen.

------------------------------------------------------------------------

### 10. Simulated Incident Creation

The final incident tool is deliberately simulated.

When approved, it produces an incident ID such as:

``` text
INC-XXXXXXXXXXXX
```

When rejected:

``` text
created: false
status: BLOCKED
message: Incident creation requires human approval.
```

No real external incident-management system is modified.

------------------------------------------------------------------------

# Project Structure

``` text
payops-agent/
│
├── app/
│   ├── agents/
│   │   ├── investigation_agent.py
│   │   ├── planner.py
│   │   └── sql_agent.py
│   │
│   ├── analytics/
│   │   ├── evidence.py
│   │   └── guardrails.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── queries.py
│   │
│   ├── graph/
│   │   ├── investigation_graph.py
│   │   └── routing_graph.py
│   │
│   ├── mcp/
│   │   └── server.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── document_loader.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   │
│   └── tools/
│       ├── analytics_tools.py
│       ├── approval_tools.py
│       ├── bank_tools.py
│       ├── failure_tools.py
│       ├── incident_tools.py
│       ├── knowledge_tools.py
│       └── report_tools.py
│
├── data/
│   ├── documents/
│   │   └── failure_code_reference.md
│   └── transactions.csv
│
├── evaluation/
│   ├── intent_cases.json
│   ├── retrieval_cases.json
│   ├── groundedness_cases.json
│   ├── task_completion_cases.json
│   ├── recovery_cases.json
│   ├── evaluate_intent.py
│   ├── evaluate_retrieval.py
│   ├── evaluate_groundedness.py
│   ├── evaluate_task_completion.py
│   ├── evaluate_recovery.py
│   ├── evaluate_latency.py
│   ├── run_all.py
│   └── results/
│       └── latest_results.json
│
├── scripts/
│   ├── generate_transactions.py
│   ├── load_database.py
│   └── index_knowledge.py
│
├── tests/
├── .gitignore
└── requirements.txt
```

Generated runtime artifacts such as the SQLite database, ChromaDB index,
Python caches, virtual environment, and `.env` are intentionally
excluded from version control.

------------------------------------------------------------------------

# Core Components

## Planner

**File:** `app/agents/planner.py`

Responsibilities:

-   classify incoming requests
-   identify operational intent
-   use deterministic rules for known intents
-   use the local LLM as fallback
-   fail closed to `OUT_OF_SCOPE`

Supported intents:

``` text
SUCCESS_RATE
FAILURE_ANALYSIS
BANK_ANALYSIS
INVESTIGATION
OUT_OF_SCOPE
```

------------------------------------------------------------------------

## Data Agent

**File:** `app/agents/sql_agent.py`

The data agent is responsible for retrieving the database evidence
required by the request.

It routes supported operational questions to deterministic database
queries such as:

-   success rate
-   failure summary
-   bank failure analysis

The agent does not allow the LLM to invent transaction numbers.

------------------------------------------------------------------------

## Analytics Tools

The tool layer exposes deterministic operations through LangChain tools.

Examples:

``` text
calculate_success_rate
get_failure_summary
get_bank_failure_summary
```

The actual calculations remain outside the LLM.

------------------------------------------------------------------------

## Investigation Agent

**File:** `app/agents/investigation_agent.py`

The investigation agent uses a local Ollama-hosted model to generate a
structured investigation from verified evidence and operational
knowledge.

The current default model is:

``` text
qwen2.5:1.5b
```

The model can be changed through environment configuration.

------------------------------------------------------------------------

## Investigation Graph

**File:** `app/graph/investigation_graph.py`

LangGraph orchestrates:

``` text
Data
  ↓
Knowledge
  ↓
Investigation
  ↓
Validation
  ↓
Retry or Report
  ↓
Human Approval
  ↓
Incident
```

This explicit workflow makes the state transitions and safety boundaries
visible.

------------------------------------------------------------------------

## Routing Graph

**File:** `app/graph/routing_graph.py`

The top-level graph determines which workflow should handle the request.

``` text
START
  ↓
Planner
  ↓
Intent
  ├── SUCCESS_RATE
  ├── FAILURE_ANALYSIS
  ├── BANK_ANALYSIS
  ├── INVESTIGATION
  └── OUT_OF_SCOPE
```

------------------------------------------------------------------------

# Data and Database Layer

The project uses a reproducible synthetic transaction dataset.

The generator uses:

``` text
random.seed(42)
```

so the dataset can be recreated consistently.

The source dataset contains:

``` text
100 synthetic transactions
```

with fields including:

-   transaction ID
-   timestamp
-   amount
-   sender bank
-   receiver bank
-   merchant category
-   payment type
-   status
-   failure reason
-   channel
-   response time

The operational database is SQLite.

The current generated dataset contains:

``` text
Total transactions: 100
Successful:          92
Failed:               8
```

Failure reasons:

``` text
TIMEOUT:             3
INSUFFICIENT_FUNDS:  2
BANK_ERROR:          2
TECHNICAL_ERROR:     1
```

The CSV is the reproducible source data, while SQLite is the operational
data source used by the application.

------------------------------------------------------------------------

# RAG and Operational Knowledge

The project includes a small synthetic operational reference document
covering the failure codes represented in the transaction dataset.

The RAG pipeline uses:

-   Sentence Transformers
-   `all-MiniLM-L6-v2`
-   ChromaDB
-   persistent local vector storage

The pipeline is:

``` text
Markdown document
      ↓
Heading-based chunking
      ↓
Sentence Transformer embeddings
      ↓
Normalized vectors
      ↓
ChromaDB
      ↓
Top-K similarity retrieval
```

The retrieved knowledge is intentionally separated from transaction
evidence.

For example:

``` text
Database evidence:
"TIMEOUT occurred 3 times."

Operational knowledge:
"TIMEOUT is a failure category requiring further investigation."
```

The second statement does not prove the cause of the first.

This distinction is important for grounded operational reasoning.

------------------------------------------------------------------------

# Grounded Investigation and Guardrails

One of the main engineering challenges was preventing the local LLM from
turning observed failure codes into unsupported root-cause claims.

For example, a model may naturally produce something like:

``` text
TIMEOUT failures suggest that network issues were the primary cause.
```

The transaction dataset does not establish that.

The guardrail layer therefore checks the generated response before the
workflow can continue.

### Guardrail categories

The validator checks for:

1.  Required response sections
2.  Unsupported numeric values
3.  Unsupported percentages
4.  Unsupported relationships
5.  Unsupported causal language
6.  Unsupported infrastructure claims

Examples of claims that should be rejected include:

``` text
The network outage caused the failures.

The server was overloaded.

SBI was responsible for the TIMEOUT failures.

TIMEOUT failures were correlated with high transaction amounts.

TIMEOUT affected 75% of all transactions.
```

The validator is deterministic and independent of the LLM.

This creates a useful architecture:

``` text
LLM reasoning
      ↓
Deterministic validation
      ↓
Only validated output continues
```

------------------------------------------------------------------------

# Human-in-the-Loop Safety

The project intentionally separates:

**recommendation / analysis**

from

**consequential action**.

The investigation can produce an incident report, but the incident tool
checks for an explicit approval result.

``` text
Investigation
     ↓
Report
     ↓
Human approval
     |
     +---- APPROVED ----> Incident created
     |
     +---- REJECTED ----> Incident blocked
```

This is currently a simulated approval mechanism and a simulated
incident-management integration.

No real production incident is created.

------------------------------------------------------------------------

# MCP Integration

The project includes an MCP server at:

``` text
app/mcp/server.py
```

The MCP server exposes read-only operational capabilities including:

``` text
get_payment_failure_summary
search_operational_knowledge
```

Incident creation is intentionally **not exposed through MCP**.

This keeps the current MCP surface focused on read-only operational
context rather than consequential actions.

The server can be started with:

``` bash
python -m app.mcp.server
```

------------------------------------------------------------------------

# Evaluation Framework

The project includes a dedicated evaluation layer rather than relying
only on unit tests.

The evaluation suite measures five functional dimensions:

### 1. Intent Selection

Does the planner select the expected workflow?

Dataset:

``` text
36 scenarios
```

------------------------------------------------------------------------

### 2. Retrieval Recall@2

Does the correct failure-code knowledge appear within the top two
retrieved results?

Dataset:

``` text
20 scenarios
```

------------------------------------------------------------------------

### 3. Groundedness

Does the deterministic validator correctly accept grounded responses and
reject unsupported claims?

Dataset:

``` text
15 scenarios
```

------------------------------------------------------------------------

### 4. Task Completion

Does the investigation workflow reach the expected incident outcome
after going through the full graph?

Dataset:

``` text
8 scenarios
```

------------------------------------------------------------------------

### 5. Failure Recovery

Does the graph correctly retry after a validation failure and stop after
the retry limit?

Dataset:

``` text
6 scenarios
```

------------------------------------------------------------------------

# Evaluation Results

The final functional evaluation produced:

  Metric                                    Result
  --------------------------- --------------------
  Intent Selection Accuracy     **36/36 --- 100%**
  Retrieval Recall@2            **20/20 --- 100%**
  Groundedness Accuracy         **15/15 --- 100%**
  Task Completion Rate            **8/8 --- 100%**
  Failure Recovery Accuracy       **6/6 --- 100%**

These results are measured against the project's **synthetic evaluation
datasets**. They should not be interpreted as production accuracy or
real-world operational performance.

------------------------------------------------------------------------

# Performance Benchmark

A separate end-to-end investigation latency benchmark was run three
times.

Latest benchmark:

  Run                 Latency
  ------------- -------------
  1                   14.64 s
  2                   20.95 s
  3                   22.96 s
  **Average**     **19.52 s**
  Minimum             14.64 s
  Maximum             22.96 s

This is a **local development benchmark**, not a production SLA.

Latency depends on the local hardware, Ollama inference,
embedding/retrieval work, graph execution, and the number of LLM
operations involved in the investigation workflow.

The benchmark is intentionally kept separate from the functional
evaluation suite.

Run it with:

``` bash
python -m evaluation.evaluate_latency
```

------------------------------------------------------------------------

# Challenges Faced and Engineering Decisions

## Challenge 1: The LLM generated unsupported root causes

A direct investigation response could transform an observed `TIMEOUT`
failure into an unsupported explanation such as a network or server
problem.

### What changed

The investigation prompt was tightened and a deterministic validation
layer was added.

The validator rejects unsupported causal, relationship, numeric, and
infrastructure claims.

### Engineering lesson

**Do not rely on prompting alone for operational safety.**

The LLM generates a candidate explanation, while deterministic code
decides whether that explanation is sufficiently grounded to continue.

------------------------------------------------------------------------

## Challenge 2: Groundedness checks initially missed indirect causal language

A direct statement such as:

``` text
The network caused the failures.
```

was easy to detect.

But a softer statement such as:

``` text
This suggests that network issues were the primary cause.
```

could bypass an overly narrow causal pattern.

### What changed

The causal detection rules were expanded to identify indirect
formulations such as:

``` text
suggests that ... cause
indicates that ... cause
appears to be caused by
likely caused by
```

A regression test was added for this specific failure mode.

### Engineering lesson

Guardrails need adversarial test cases, not only happy-path examples.

------------------------------------------------------------------------

## Challenge 3: Keeping deterministic facts outside the LLM

It would have been easy to ask the LLM to calculate:

``` text
3 / 8 = 37.5%
```

But doing so makes a factual operational metric dependent on model
generation.

### What changed

Evidence construction and numerical calculations were moved into
deterministic Python code.

The LLM receives verified evidence rather than raw data that it must
calculate itself.

### Engineering lesson

**Use code for facts and models for interpretation.**

------------------------------------------------------------------------

## Challenge 4: Retry behavior needed to be explicit

A failed investigation should not automatically become a final answer.

### What changed

The LangGraph workflow explicitly routes validation failures through:

``` text
Validation
   ↓
Retry
   ↓
Investigation
```

with a retry limit.

The retry evaluator tests this routing independently.

### Engineering lesson

Agentic systems need explicit recovery states rather than implicit
exception handling.

------------------------------------------------------------------------

## Challenge 5: Consequential actions need a human boundary

An AI-generated incident should not automatically become a real
operational action.

### What changed

Incident creation is gated by an explicit approval result.

``` text
APPROVED → allowed
REJECTED → blocked
```

The current implementation is simulated and does not connect to a real
incident platform.

### Engineering lesson

Human-in-the-loop control should be part of the workflow architecture,
not an afterthought.

------------------------------------------------------------------------

## Challenge 6: Keeping the project reproducible without real payment data

The project needed enough operational structure to demonstrate realistic
workflows without using sensitive production information.

### What changed

The project uses:

-   synthetic transactions
-   synthetic operational documentation
-   deterministic data generation
-   local SQLite
-   local vector storage
-   local Ollama inference

### Engineering lesson

A production-inspired architecture can be demonstrated safely using
reproducible synthetic data.

------------------------------------------------------------------------

## Challenge 7: Running local AI on CPU-only hardware

The project was developed on a machine without an NVIDIA CUDA GPU.

The system therefore uses lightweight local models through Ollama rather
than depending on a cloud API or dedicated GPU.

### Engineering lesson

Model selection has to consider the actual deployment environment, not
only benchmark quality.

------------------------------------------------------------------------

# Key Design Decisions

## Deterministic analytics + LLM reasoning

The architecture intentionally separates:

``` text
Deterministic layer
    ↓
Facts / calculations / validation

LLM layer
    ↓
Interpretation / investigation wording
```

This reduces the amount of factual responsibility placed on the language
model.

------------------------------------------------------------------------

## LangGraph instead of a single agent loop

The investigation workflow has explicit states:

``` text
Data
Knowledge
Investigation
Validation
Retry
Report
Approval
Incident
```

LangGraph makes these transitions explicit and testable.

------------------------------------------------------------------------

## Local-first architecture

The core system can run locally using:

``` text
Ollama
SQLite
ChromaDB
Sentence Transformers
```

This avoids making the core workflow dependent on a paid hosted LLM API.

------------------------------------------------------------------------

## Read-only MCP surface

MCP exposes operational information retrieval but not incident creation.

This intentionally keeps the external tool surface conservative.

------------------------------------------------------------------------

## Fail closed

When the planner cannot confidently identify an operational intent, it
routes the request to:

``` text
OUT_OF_SCOPE
```

rather than guessing an operational workflow.

------------------------------------------------------------------------

# Limitations

This is an engineering prototype and evaluation environment, not a
production payment-operations platform.

Current limitations include:

-   Synthetic transaction data rather than live UPI/payment data.
-   SQLite rather than a production operational database.
-   Simulated incident creation rather than a real Jira/ServiceNow
    integration.
-   Simulated human approval rather than a real approval UI.
-   A small operational knowledge base.
-   Rule-based planner logic with local LLM fallback rather than a
    trained intent model.
-   A lightweight local LLM running through Ollama.
-   Latency is currently relatively high for an interactive operational
    workflow.
-   The evaluation datasets are intentionally small and
    project-specific.
-   The guardrails use deterministic pattern-based validation and are
    not a complete semantic safety system.

These limitations are intentional boundaries of the current
implementation.

------------------------------------------------------------------------

# Tech Stack

  Area                     Technology
  ------------------------ ---------------------------------
  Language                 Python 3.12
  Workflow orchestration   LangGraph
  LLM runtime              Ollama
  Default local model      Qwen 2.5 1.5B
  LLM integration          LangChain Ollama
  Database                 SQLite
  Vector database          ChromaDB
  Embeddings               Sentence Transformers
  Embedding model          `all-MiniLM-L6-v2`
  Agent tools              LangChain Core tools
  Protocol integration     MCP
  Testing                  pytest
  Data                     Synthetic UPI-like transactions
  Knowledge format         Markdown

------------------------------------------------------------------------

# Setup

## 1. Clone the repository

``` bash
git clone <YOUR_REPOSITORY_URL>
cd payops-agent
```

## 2. Create a virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

``` bash
pip install -r requirements.txt
```

## 4. Make sure Ollama is installed

The project expects Ollama to be available locally.

Verify:

``` bash
ollama --version
```

## 5. Pull the default model

``` bash
ollama pull qwen2.5:1.5b
```

The model can be changed through environment configuration.

------------------------------------------------------------------------

# Rebuild the Local Data

The generated database and vector store are intentionally ignored by
Git.

Recreate the transaction data:

``` bash
python -m scripts.generate_transactions
```

Load the transactions into SQLite:

``` bash
python -m scripts.load_database
```

Index the operational knowledge:

``` bash
python -m scripts.index_knowledge
```

This gives the project a reproducible setup flow:

``` text
Source CSV
   ↓
SQLite database

Source operational document
   ↓
Chunks
   ↓
Embeddings
   ↓
ChromaDB
```

------------------------------------------------------------------------

# Running the Project

## Run the top-level routing graph

The routing graph can be imported and invoked from Python.

Example:

``` python
from app.graph.routing_graph import graph

result = graph.invoke(
    {
        "question": "What is the payment success rate?",
        "intent": "",
        "result": {},
    }
)

print(result)
```

------------------------------------------------------------------------

## Run an investigation

``` python
from app.graph.investigation_graph import graph

result = graph.invoke(
    {
        "question": "Investigate why payments are failing",
        "evidence": {},
        "operational_knowledge": {},
        "investigation": "",
        "validation": {},
        "retry_count": 0,
        "report": {},
        "approval_status": "REJECTED",
        "approval": {},
        "incident": {},
    }
)

print(result)
```

The default example uses `REJECTED` approval so that the simulated
consequential action remains blocked.

------------------------------------------------------------------------

# Running the MCP Server

``` bash
python -m app.mcp.server
```

The MCP server exposes read-only operational tools for payment failure
analysis and operational knowledge retrieval.

------------------------------------------------------------------------

# Testing

Run the complete automated test suite:

``` bash
python -m pytest -q
```

Final validation result:

``` text
37 passed
```

------------------------------------------------------------------------

# Running Evaluations

Run all functional evaluations:

``` bash
python -m evaluation.run_all
```

Run the latency benchmark separately:

``` bash
python -m evaluation.evaluate_latency
```

The latest functional results are stored at:

``` text
evaluation/results/latest_results.json
```

------------------------------------------------------------------------

# Future Improvements

Potential next iterations include:

### Production database integration

Replace SQLite with a production-grade transactional or analytical data
source.

### Real incident-management integration

Add a sandboxed Jira/ServiceNow-style integration behind the existing
human approval boundary.

### Stronger semantic guardrails

Replace pattern-only validation with a combination of:

-   schema validation
-   deterministic rules
-   semantic contradiction checks
-   evidence attribution
-   structured model output

### Better observability

Add:

-   structured logs
-   trace IDs
-   node-level latency
-   tool latency
-   LLM latency
-   retry counts
-   failure reasons

### More rigorous evaluation

Expand the evaluation framework with:

-   100+ scenarios
-   adversarial groundedness cases
-   tool-selection accuracy
-   evidence attribution
-   hallucination rate
-   p50/p95/p99 latency
-   failure-injection testing
-   regression evaluation across model versions

### Production-grade API

Expose the agent through a FastAPI service with authentication, request
tracing, and operational monitoring.

------------------------------------------------------------------------

# Project Positioning

This project is intentionally positioned as an **Agentic AI engineering
system**, rather than a generic chatbot.

The core engineering ideas demonstrated are:

``` text
Intent routing
       +
Deterministic data tools
       +
RAG
       +
Local LLM reasoning
       +
LangGraph orchestration
       +
Validation / guardrails
       +
Retry / recovery
       +
Human-in-the-loop approval
       +
MCP
       +
Evaluation
```

The most important design principle is:

> **The LLM should reason over verified operational evidence, not become
> the source of truth for operational facts.**

That principle drives the separation between the database/evidence
layer, RAG knowledge layer, investigation LLM, deterministic guardrails,
and human approval boundary.

------------------------------------------------------------------------

## Author

**Mohan Dongara**

GitHub: `https://github.com/Mohanaspiringcoder`

------------------------------------------------------------------------

## Disclaimer

This project uses synthetic UPI-like transaction data and synthetic
operational documentation for educational and engineering demonstration
purposes.

It is not connected to production payment systems and does not process
real customer or payment information.
