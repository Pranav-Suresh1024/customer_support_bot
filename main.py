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
    
    # Mocking the human input for query 4 specifically to avoid blocking
    # The requirement says "except for the human approval step in Query 4", 
    # but to make this truly automated we can mock `builtins.input` or just let it block.
    # Let's use a custom input that auto-approves if we want it fully automated, 
    # but the prompt says "except for the human approval step", implying it SHOULD block.
    # We will let it block and prompt the user in the terminal.
    
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
    # If the user doesn't want to type 'Y' manually during tests, 
    # they can monkeypatch input() here. For now, we leave it interactive.
    
    # Optional: Automatically say 'Y' to make the script non-blocking if needed by automated runners.
    # original_input = builtins.input
    # builtins.input = lambda prompt: 'Y' if "Approve?" in prompt else original_input(prompt)
    
    run_demonstration()
