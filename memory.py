import sqlite3
import os
from datetime import datetime
from config import DB_PATH, DATABASE_DIR
from utils import setup_logger
from state import AgentState
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from config import LLM_MODEL, LLM_TEMPERATURE

logger = setup_logger(__name__)
llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

def initialize_db():
    """Creates the database and table if they do not exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        session_id TEXT,
        user_query TEXT,
        assistant_response TEXT,
        timestamp DATETIME
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def save_conversation(customer_name: str, session_id: str, user_query: str, response: str):
    """Saves one turn to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now()
    cursor.execute('''
    INSERT INTO conversations (customer_name, session_id, user_query, assistant_response, timestamp)
    VALUES (?, ?, ?, ?, ?)
    ''', (customer_name, session_id, user_query, response, timestamp))
    
    conn.commit()
    conn.close()

def load_previous_history(customer_name: str) -> list:
    """Returns the most recent meaningful past turn for a customer."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT user_query, assistant_response, timestamp 
    FROM conversations 
    WHERE customer_name = ?
      AND LOWER(user_query) NOT LIKE '%previous%'
      AND LOWER(user_query) NOT LIKE '%last time%'
      AND LOWER(user_query) NOT LIKE '%earlier%'
      AND LOWER(user_query) NOT IN ('hi', 'hello', 'thanks', 'thank you')
    ORDER BY timestamp DESC
    LIMIT 1
    ''', (customer_name,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def search_previous_issue(customer_name: str, keyword: str) -> list:
    """Searches history by keyword."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = f"%{keyword}%"
    cursor.execute('''
    SELECT user_query, assistant_response, timestamp 
    FROM conversations 
    WHERE customer_name = ? AND (user_query LIKE ? OR assistant_response LIKE ?)
    ORDER BY timestamp DESC
    ''', (customer_name, query, query))
    
    results = cursor.fetchall()
    conn.close()
    return results

def memory_recall_node(state: AgentState) -> AgentState:
    """
    Node for loading history from SQLite and using it to construct
    the response directly for Memory intents. Sets both response and
    final_response to protect against downstream state overwrites.
    """
    customer_name = state.get("customer_name", "Unknown Customer")
    history = load_previous_history(customer_name)

    state["department"] = "Memory"

    if not history:
        msg = (
            f"I don't have any previous support records for {customer_name} in our system. "
            "This may be your first interaction with us."
        )
        state["response"] = msg
        state["final_response"] = msg
        logger.info("Memory recall: no history found.")
        return state

    # Format the last 5 turns for the LLM
    history_text = "Previous support conversations:\n"
    for idx, (q, r, ts) in enumerate(history[-5:]):
        history_text += f"\nInteraction {idx + 1} (at {ts}):\n  Customer: {q}\n  Support: {r}\n"

    state["memory_context"] = history_text

    system_prompt = (
        "You are a helpful customer support agent. "
        "The customer is asking about their previous interactions with support. "
        "Use the conversation history below to answer their question directly and concisely. "
        "Do not make up any information. "
        "If the customer asks what their previous issue was, state it clearly.\n\n"
        + history_text
    )

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_query"])
        ])
        answer = response.content.strip()
        if not answer:
            raise ValueError("LLM returned empty response.")
    except Exception as e:
        logger.error(f"Memory Recall LLM call failed: {e}")
        # Build a plain-text fallback directly from SQLite without the LLM
        last_query, last_response, last_ts = history[-1]
        answer = (
            f"Your most recent support issue was:\n\"{last_query}\"\n\n"
            f"Our response at the time was:\n\"{last_response}\"\n\n"
            "Please let us know if you need further assistance."
        )

    state["response"] = answer
    state["final_response"] = answer   # Set directly — supervisor will preserve this for Memory
    logger.info(f"Memory recall: retrieved {len(history)} records for {customer_name}.")
    return state
    
def store_memory_node(state: AgentState) -> AgentState:
    """Saves the final interaction to SQLite before ending."""
    customer_name = state.get("customer_name", "Unknown Customer")
    session_id = state.get("session_id", "Unknown Session")
    user_query = state.get("user_query", "")
    
    # Important: Save the final response if available, else the draft response, else refusal
    if state.get("approval_status") == "rejected":
        response = state.get("response", "Request was rejected.")
    else:
        response = state.get("final_response", state.get("response", ""))
        
    save_conversation(customer_name, session_id, user_query, response)
    return state
