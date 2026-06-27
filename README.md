# AI-Powered Customer Support Automation System

A production-quality, multi-agent customer support automation system built with **LangGraph** and **LangChain**. The system accepts customer queries, classifies intent, routes to the correct department agent, retrieves relevant information from a knowledge base using RAG, maintains conversation memory using SQLite, escalates high-risk requests for human approval, and polishes every response through a Supervisor Agent before delivery.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Sample Outputs](#sample-outputs)
- [Workflow Diagram](#workflow-diagram)
- [Knowledge Base](#knowledge-base)
- [SQLite Memory](#sqlite-memory)
- [Human-in-the-Loop](#human-in-the-loop)
- [Screenshots](#screenshots)

---

## Overview

ABC Technologies receives a high volume of daily customer support requests covering product information, technical issues, billing queries, account management, and refund requests. This system automates the handling of those requests using a multi-agent AI pipeline built on LangGraph.

The system is designed to:

- Reduce manual support workload
- Improve response consistency and professionalism
- Maintain customer conversation history across sessions
- Ensure high-risk actions are always reviewed by a human before a response is sent

---

## Features

| Feature | Description |
|---|---|
| **Intent Classification** | Automatically classifies queries into Sales, Technical, Billing, Account, Memory, or Unknown |
| **Conditional Routing** | Routes each query to the correct department agent using LangGraph conditional edges |
| **RAG Pipeline** | Retrieves the top 3 relevant knowledge base chunks using FAISS and SentenceTransformers |
| **Specialized Agents** | Dedicated agents for Sales, Technical, Billing, Account, and General Support |
| **SQLite Memory** | Stores and retrieves full conversation history per customer across sessions |
| **Human-in-the-Loop** | Pauses execution and prompts for manual approval on high-risk requests |
| **Supervisor Agent** | Reviews and polishes every draft response for grammar, tone, and accuracy |
| **Memory Recall** | Retrieves and summarises previous support interactions on request |
| **Configurable LLM** | LLM model and temperature are configurable through `config.py` |

---

## System Architecture

The system is implemented as a directed LangGraph state graph. Each node in the graph is a Python function that reads from and writes to a shared `AgentState` dictionary.

**High-level flow:**

```
Customer Query
      ↓
Memory Recall (load SQLite context)
      ↓
Intent Classification (LLM → JSON)
      ↓
RAG Retrieval (FAISS → top 3 chunks)
      ↓
Conditional Router
      ↓
┌─────────┬──────────┬─────────┬─────────┬─────────────────┐
Sales   Technical  Billing  Account  General Support
└─────────┴──────────┴─────────┴─────────┴─────────────────┘
      ↓
Approval Check
      ↓
┌─────────────────────┬──────────────────────┐
Human Approval        Supervisor Review
(if required)         (if not required)
      ↓                       ↓
Supervisor Review ────────────┘
      ↓
Store Memory (SQLite)
      ↓
Final Response → Customer
```

For Memory intent queries, the flow skips all department agents and RAG retrieval, goes directly to the Memory Recall node, and returns the customer's previous conversation history.

---

## Tech Stack

| Component | Technology |
|---|---|
| Workflow Engine | LangGraph |
| LLM Framework | LangChain |
| LLM Model | ChatOllama (`qwen2.5-coder:7b`) |
| Vector Store | FAISS |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Memory Store | SQLite |
| Data Validation | Pydantic |
| Language | Python 3.11+ |

---

## Project Structure

```
customer_support_bot/
│
├── main.py                  # Entry point — runs all 5 demonstration queries
├── graph.py                 # LangGraph workflow definition and edge wiring
├── state.py                 # AgentState TypedDict with all state fields
├── config.py                # LLM model, file paths, and system settings
├── utils.py                 # Logger setup and shared helper functions
│
├── nodes.py                 # Intent classifier and all department agent nodes
├── router.py                # Conditional routing logic based on intent
├── supervisor.py            # Supervisor review and response polishing node
├── human_loop.py            # Human approval prompt and approval logic
├── rag.py                   # FAISS vector store initialisation and retrieval node
├── memory.py                # SQLite functions and memory recall/store nodes
│
├── knowledge/               # Source documents loaded into the RAG pipeline
│   ├── company_policy.txt   # Refund, cancellation, and escalation policies
│   ├── pricing_guide.txt    # Subscription plans and add-on pricing
│   ├── technical_manual.txt # Troubleshooting guides and known issues
│   └── faq.txt              # Frequently asked questions
│
├── database/
│   └── memory.db            # SQLite database (auto-created at runtime)
│
├── screenshots/             # Execution screenshots for submission
│
├── requirements.txt         # Python dependencies
├── README.md                
└── documentation_report.md  # Full written report covering all 10 tasks
```

---

## Installation

### Prerequisites

- Python 3.11 or newer
- [Ollama](https://ollama.com) installed and running locally
- The `qwen2.5-coder:7b` model pulled in Ollama

Pull the model before running:

```bash
ollama pull qwen2.5-coder:7b
```

### Steps

**1. Clone or download the project:**

```bash
git clone <repository-url>
cd customer_support_bot
```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Verify Ollama is running:**

```bash
ollama list
```

You should see `qwen2.5-coder:7b` in the list.

---

## Configuration

All configurable settings are in `config.py`:

```python
# LLM settings
LLM_MODEL       = "qwen2.5-coder:7b"   # Change to any Ollama model
LLM_TEMPERATURE = 0             # 0 = deterministic output

# File paths
KNOWLEDGE_DIR  = "knowledge"
DATABASE_DIR   = "database"
DB_PATH        = "database/memory.db"
```

To use a different model, change `LLM_MODEL` to any model available in your Ollama installation, for example `"llama3"` or `"mistral"`.

---

## Running the System

```bash
python main.py
```

The system will automatically run all five demonstration queries. When Query 4 (refund request) is reached, you will be prompted to approve or reject the request:

```
[HUMAN APPROVAL REQUIRED]
Customer: David
Request: I need a refund for my annual subscription.
Draft Response: ...

Approve? (Y/N):
```

Enter `Y` to approve or `N` to reject.

The `database/memory.db` file and the FAISS vector store are both created automatically on the first run. No manual setup is required.

---

## Sample Outputs

### Query 1 — Pricing Plans (Sales)

```
============================================================
Query: What are the pricing plans available for your software?
------------------------------------------------------------
Detected Intent  : Sales
Routed Department: Sales
Retrieved Chunks :
  [1] [Source: pricing_guide.txt] Plans — Basic, Professional, Enterprise...
  [2] [Source: pricing_guide.txt] Add-ons — Extra Storage, Extra Users...
  [3] [Source: faq.txt] Free trial and billing cycle information...
Approval Required: No
Approval Decision: N/A
Final Response   :
  We offer three subscription plans:
  1. Basic Plan: $10/month or $100/year — 1 user, 10GB storage, email support.
  2. Professional Plan: $25/month or $250/year — 5 users, 100GB storage, email and chat support.
  3. Enterprise Plan: $100/month or $1,000/year — unlimited users, 1TB storage, 24/7 phone support.

  Add-ons are also available: extra storage at $5/month per 50GB, and extra users at $5/month each.
  We also offer a 14-day free trial on the Professional Plan — no credit card required.

  Please let us know if you need any further assistance.
============================================================
```

### Query 2 — Forgot Password (Account)

```
============================================================
Query: I forgot my account password.
------------------------------------------------------------
Detected Intent  : Account
Routed Department: Account
Retrieved Chunks :
  [1] [Source: technical_manual.txt] Login failures and password reset guide...
Approval Required: No
Approval Decision: N/A
Final Response   :
  No problem — we can get this sorted quickly.
  To reset your password:
  1. Click the "Forgot Password" link on the login page.
  2. Enter the email address associated with your account.
  3. Check your inbox for a password reset email and follow the instructions.

  Please let us know if you need any further assistance.
============================================================
```

### Query 3 — Application Crash on Upload (Technical)

```
============================================================
Query: My application crashes whenever I upload a file.
------------------------------------------------------------
Detected Intent  : Technical
Routed Department: Technical
Retrieved Chunks :
  [1] [Source: technical_manual.txt] File Upload Failures — version 2.0.5 known issue...
Approval Required: No
Approval Decision: N/A
Final Response   :
  This is a known issue in version 2.0.5 of the application.
  To resolve it:
  1. Update the application to version 2.0.6 or newer.
  2. Ensure the file you are uploading is under 50MB.
  3. Confirm the file is in a supported format: .pdf, .jpg, or .png.

  Please let us know if the issue persists after updating.
============================================================
```

### Query 4 — Refund Request (Billing + Human Approval)

```
============================================================
Query: I need a refund for my annual subscription.
------------------------------------------------------------
Detected Intent  : Billing
Routed Department: Billing
Retrieved Chunks :
  [1] [Source: company_policy.txt] Refunds and Cancellations policy...
Approval Required: Yes

[HUMAN APPROVAL REQUIRED]
Customer: David
Request: I need a refund for my annual subscription.
Approve? (Y/N): Y

Approval Decision: Approved
Final Response   :
  Thank you for contacting us regarding your refund request.
  Our policy allows a full refund within 30 days of your initial purchase.
  After 30 days, refunds are issued on a pro-rated basis for annual subscriptions,
  provided the service experienced significant downtime that was our fault.

  Could you please provide your account details so we can review your request?
  Please let us know if you need any further assistance.
============================================================
```

### Query 5 — Memory Recall

```
============================================================
Query: What was my previous support issue?
------------------------------------------------------------
Detected Intent  : Memory
Routed Department: Memory
Retrieved Chunks : None
Approval Required: No
Approval Decision: N/A
Final Response   :
  Your most recent support issue was:
  "I need a refund for my annual subscription."

  Please let us know if there is anything else we can help you with.
============================================================
```

---

## Workflow Diagram

The full LangGraph workflow is saved in `workflow_diagram.png`. 
---

## Knowledge Base

The RAG pipeline loads four documents from the `knowledge/` folder:

| Document | Contents |
|---|---|
| `company_policy.txt` | Refund eligibility, cancellation policy, escalation rules, account policies |
| `pricing_guide.txt` | Subscription plans, pricing tiers, add-ons, billing cycles |
| `technical_manual.txt` | Application crash fixes, login error codes, upload failure solutions, configuration guides |
| `faq.txt` | Common questions on billing cycles, free trials, account merging, support response times |

Documents are chunked using `RecursiveCharacterTextSplitter` (chunk size 500, overlap 50), embedded using `all-MiniLM-L6-v2`, and stored in a FAISS index. The top 3 most relevant chunks are retrieved per query.

---

## SQLite Memory

Conversation history is stored in `database/memory.db` and created automatically on first run.

**Schema:**

```sql
CREATE TABLE conversations (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name      TEXT,
    session_id         TEXT,
    user_query         TEXT,
    assistant_response TEXT,
    timestamp          DATETIME
);
```

**Functions:**

| Function | Description |
|---|---|
| `initialize_db()` | Creates the database and table if they do not exist |
| `save_conversation()` | Saves one completed interaction to the database |
| `load_previous_history()` | Returns all past turns for a given customer name |
| `search_previous_issue()` | Searches history by keyword for a given customer |

Every completed query is saved to SQLite after the Supervisor review. When a customer asks about their previous issue, the system retrieves their history and constructs a response without routing to any department agent.

---

## Human-in-the-Loop

The following request types always require human approval before a response is sent:

- Refund requests
- Subscription cancellation
- Account closure
- Compensation requests
- Escalation to management

When triggered, the graph pauses and displays a prompt in the terminal. If the operator enters `Y`, the approved response is passed to the Supervisor for final polishing. If the operator enters `N`, a polite refusal is returned to the customer and the interaction is saved to SQLite.

---

## Screenshots

Execution screenshots are saved in the `screenshots/` folder. Screenshots cover:

- Agent routing for all five queries
- Human-in-the-loop approval prompt
- RAG chunk retrieval display
- SQLite memory storage and recall
- Final response generation

---

