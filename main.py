import builtins
import uuid
from memory import initialize_db
from graph import create_workflow
from utils import setup_logger, format_response

logger = setup_logger(__name__)

def run_demonstration():
    """Runs the 5 required demonstration queries."""
    
    # 1. Initialize the database
    initialize_db()
    
    # 2. Compile the graph
    app = create_workflow()
    
    customer_name = "David"
    session_id = str(uuid.uuid4())
    
    queries = [
        "What are the pricing plans available for your software?",
        "I forgot my account password.",
        "My application crashes whenever I upload a file.",
        "I need a refund for my annual subscription.",
        "What was my previous support issue?"
    ]
    
    for query in queries:
        initial_state = {
            "customer_name": customer_name,
            "session_id": session_id,
            "user_query": query,
            "intent": "",
            "department": "",
            "retrieved_context": "",
            "memory_context": "",
            "approval_required": False,
            "approval_status": "pending",
            "response": "",
            "final_response": "",
            "conversation_history": [],
            "retrieved_chunks": []
        }
        
        # Execute the graph
        final_state = app.invoke(initial_state)
        
        # Format and print the result
        output = format_response(
            query=query,
            intent=final_state.get("intent", "Unknown"),
            department=final_state.get("department", "Unknown"),
            chunks=final_state.get("retrieved_chunks", []),
            approval_required=final_state.get("approval_required", False),
            approval_status=final_state.get("approval_status", "N/A"),
            supervisor_output=final_state.get("final_response", ""),
            final_response=final_state.get("final_response", final_state.get("response", ""))
        )
        
        print(output)

if __name__ == "__main__":
    run_demonstration()
