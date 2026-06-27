from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import (
    intent_classification_node,
    SalesAgent,
    TechnicalAgent,
    BillingAgent,
    AccountAgent,
    GeneralSupportAgent
)
from rag import rag_retrieval_node
from router import route_intent
from human_loop import check_approval_required, route_approval, human_approval_node, route_after_approval
from supervisor import supervisor_review_node
from memory import memory_recall_node, store_memory_node

def final_response_node(state: AgentState) -> AgentState:
    """No-op node to represent the final response step before END."""
    return state

def create_workflow() -> StateGraph:
    """
    Constructs the LangGraph workflow based on the Mermaid diagram.
    """
    workflow = StateGraph(AgentState)
    
    # 1. Add all nodes
    workflow.add_node("IntentClassification", intent_classification_node)
    
    workflow.add_node("SalesAgent", SalesAgent)
    workflow.add_node("TechnicalAgent", TechnicalAgent)
    workflow.add_node("BillingAgent", BillingAgent)
    workflow.add_node("AccountAgent", AccountAgent)
    workflow.add_node("GeneralSupportAgent", GeneralSupportAgent)
    
    workflow.add_node("MemoryRecall", memory_recall_node)
    
    workflow.add_node("RAGRetrieval", rag_retrieval_node)
    workflow.add_node("ApprovalCheck", check_approval_required)
    workflow.add_node("HumanApproval", human_approval_node)
    workflow.add_node("SupervisorReview", supervisor_review_node)
    workflow.add_node("StoreMemory", store_memory_node)
    workflow.add_node("FinalResponse", final_response_node)
    
    # 2. Add edges
    # Entry point: IntentClassification
    workflow.set_entry_point("IntentClassification")
    
    # IntentClassification → RAGRetrieval (RAG runs BEFORE routing so agents have context)
    workflow.add_edge("IntentClassification", "RAGRetrieval")
    
    # RAGRetrieval → Router (conditional edges based on intent)
    workflow.add_conditional_edges(
        "RAGRetrieval",
        route_intent,
        {
            "SalesAgent": "SalesAgent",
            "TechnicalAgent": "TechnicalAgent",
            "BillingAgent": "BillingAgent",
            "AccountAgent": "AccountAgent",
            "GeneralSupportAgent": "GeneralSupportAgent",
            "MemoryRecall": "MemoryRecall"
        }
    )
    
    # All department agents go to ApprovalCheck (RAG already ran before them)
    for agent in ["SalesAgent", "TechnicalAgent", "BillingAgent", "AccountAgent", "GeneralSupportAgent"]:
        workflow.add_edge(agent, "ApprovalCheck")
        
    # Memory Recall goes directly to StoreMemory (no RAG or Supervisor needed)
    workflow.add_edge("MemoryRecall", "StoreMemory")
    
    # Approval Check Router
    workflow.add_conditional_edges(
        "ApprovalCheck",
        route_approval,
        {
            "HumanApproval": "HumanApproval",
            "SupervisorReview": "SupervisorReview"
        }
    )
    
    # Human Approval Router
    workflow.add_conditional_edges(
        "HumanApproval",
        route_after_approval,
        {
            "SupervisorReview": "SupervisorReview",
            "StoreMemory": "StoreMemory"
        }
    )
    
    # Supervisor -> StoreMemory -> FinalResponse -> END
    workflow.add_edge("SupervisorReview", "StoreMemory")
    workflow.add_edge("StoreMemory", "FinalResponse")
    workflow.add_edge("FinalResponse", END)
    
    return workflow.compile()
