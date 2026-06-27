from state import AgentState

def route_intent(state: AgentState) -> str:
    """
    Conditional routing logic based on the intent field in state.
    Returns the name of the next node to execute.
    """
    intent = state.get("intent", "Unknown")
    
    if intent == "Sales":
        return "SalesAgent"
    elif intent == "Technical":
        return "TechnicalAgent"
    elif intent == "Billing":
        return "BillingAgent"
    elif intent == "Account":
        return "AccountAgent"
    elif intent == "Memory":
        return "MemoryRecall"
    else:
        return "GeneralSupportAgent"
