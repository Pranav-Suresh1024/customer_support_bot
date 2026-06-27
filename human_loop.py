from state import AgentState
from utils import setup_logger

logger = setup_logger(__name__)

def check_approval_required(state: AgentState) -> AgentState:
    """
    Checks if the intent and query require human approval.
    """
    query = state["user_query"].lower()
    
    requires_approval_keywords = [
        "refund", "cancel", "closure", "compensation", "escalate", "management"
    ]
    
    state["approval_required"] = any(keyword in query for keyword in requires_approval_keywords)
    
    if state["approval_required"]:
        state["approval_status"] = "pending"
    else:
        state["approval_status"] = "N/A"
        
    return state

def route_approval(state: AgentState) -> str:
    """
    Conditional routing logic for approval check.
    """
    if state.get("approval_required", False):
        return "HumanApproval"
    return "SupervisorReview"

def human_approval_node(state: AgentState) -> AgentState:
    """
    Pauses execution and displays prompt to the terminal for human input.
    """
    customer_name = state.get("customer_name", "Unknown")
    user_query = state.get("user_query", "")
    draft_response = state.get("response", "")
    
    print("\n[HUMAN APPROVAL REQUIRED]")
    print(f"Customer: {customer_name}")
    print(f"Request: {user_query}")
    print(f"Draft Response: {draft_response}\n")
    
    while True:
        decision = input("Approve? (Y/N): ").strip().upper()
        
        if decision == 'Y':
            state["approval_status"] = "approved"
            logger.info("Human approved the response.")
            break
        elif decision == 'N':
            state["approval_status"] = "rejected"
            state["response"] = "We apologize, but we are unable to process your request at this time as it was not approved by management."
            logger.info("Human rejected the response.")
            break
        else:
            print("Please enter 'Y' or 'N'.")
            
    return state

def route_after_approval(state: AgentState) -> str:
    """
    Conditional routing after human approval.
    """
    if state.get("approval_status") == "approved":
        return "SupervisorReview"
    return "StoreMemory" # Skip supervisor if rejected
