# Documentation Report
## AI-Powered Customer Support Automation System

## 1. Objective

The objective of this project is to automate customer support using LangGraph by integrating intent classification, department-specific agents, Retrieval-Augmented Generation (RAG), SQLite-based conversational memory, human-in-the-loop approval, and a supervisor agent to generate accurate and professional customer responses.

## 2. Technologies Used

- Python 3.11
- LangGraph
- LangChain
- ChatOllama
- qwen2.5-coder:7b 
- SQLite
- FAISS
- Sentence Transformers
- RecursiveCharacterTextSplitter

### 2. System Architecture Overview
The workflow begins with intent classification.
Depending on the detected intent, the graph either:
- routes to the Memory node,
- or routes to one of the department-specific agents.

The selected agent performs Retrieval-Augmented Generation using the company knowledge base.If the request requires human approval, execution pauses until approval is received.
Finally, the Supervisor Agent reviews the response before it is stored in SQLite memory and returned to the customer.

### 3. Implementation of the 10 Tasks

**Task 1: LangGraph Workflow**
Implemented in `graph.py`. The workflow strictly adheres to the requested Mermaid diagram, utilizing conditional edges for both the Intent Router and the Human Approval Check.

**Task 2: State**
Implemented in `state.py`. An `AgentState` typed dictionary acts as the single source of truth across the graph execution, holding variables like `user_query`, `intent`, `approval_status`, and `final_response`.

**Task 3: Intent Classification**
Implemented in `nodes.py`. The `intent_classification_node` forces the LLM to output a strict JSON structure containing the intent, confidence, and reasoning.

**Task 4: Conditional Routing**
Implemented in `router.py`. The `route_intent` function acts as the conditional edge logic, directing the state to the appropriate department agent based on the parsed JSON intent.

**Task 5: Specialized Agents**
Implemented in `nodes.py`. A factory function `create_agent()` is used to dynamically instantiate the Sales, Technical, Billing, Account, and General Support agents with specific system prompts.

**Task 6: RAG**
Implemented in `rag.py`. `RecursiveCharacterTextSplitter` parses the 4 text documents in `knowledge/`. The chunks are embedded using `SentenceTransformer` and indexed in a FAISS vector store. The retrieved chunks are stored in the graph state as `retrieved_context`.
The department agent and supervisor both use this context to generate responses grounded in the company documents instead of relying solely on the language model.

**Task 7: SQLite Memory**
Implemented in `memory.py`. An SQLite database automatically initializes at runtime. It stores all conversation turns. A specific `memory_recall_node` allows the agent to bypass the normal RAG pipeline and directly query this SQL database when the intent is `Memory`.
Each conversation stores:
- customer name
- user query
- assistant response
- timestamp

This allows future memory queries such as
"What was my previous support issue?"
to be answered directly from SQLite.

**Task 8: Human-in-the-Loop**
Implemented in `human_loop.py`. Keywords trigger an approval flag in state. When triggered, the graph execution hits a node that uses `builtins.input` to pause execution, requiring the user to explicitly type 'Y' or 'N' in the terminal.
The following requests require human approval:
- Refund requests
- Subscription cancellation
- Account closure
- Compensation requests
- Escalation to management

**Task 9: Supervisor Agent**
Implemented in `supervisor.py`. Acts as a quality assurance gate, reviewing the draft response against the retrieved RAG context. It produces the `final_response`.

**Task 10: Demonstration**
Implemented in `main.py`. The script iterates over 5 predefined queries, invoking the compiled graph for each, and formatting the output via a utility function to match the requested UI block.

### 4. Challenges and Solutions
- **JSON Parsing for Intent**: Smaller models like `gemma3:1b` occasionally fail to output pure JSON. The solution involved robust prompt engineering and a fallback try/catch block that defaults to `Unknown` intent if parsing fails.
- **Graph State Persistence**: Handling the looping logic for the Memory node was tricky because we didn't want it to enter the standard RAG -> Supervisor pipeline if it merely recalling past conversation. We explicitly routed `MemoryRecall` straight to `StoreMemory`.

### 5. References
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- SQLite3 Documentation: https://docs.python.org/3/library/sqlite3.html
- FAISS via LangChain: https://python.langchain.com/docs/integrations/vectorstores/faiss/
