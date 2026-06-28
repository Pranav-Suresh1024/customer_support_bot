import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from config import LLM_MODEL, LLM_TEMPERATURE
from utils import setup_logger

logger = setup_logger(__name__)

llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

def intent_classification_node(state: AgentState) -> AgentState:
    """Classifies the user query into one of the allowed intents."""
    query = state["user_query"]

    system_prompt = """
You are an expert intent classification system for a customer support bot.
Classify the user's query into exactly one of the following intents:

- Sales: pricing, plans, subscriptions, product information
- Technical: crashes, installation issues, login failures, configuration problems, upload failures
- Billing: invoices, payments, refund requests
- Account: password reset, account activation, profile updates, account closure
- Memory: ANY query asking about PAST interactions, previous issues, earlier conversations,
          or conversation history. Keywords include: "previous issue", "last time", "before",
          "history", "earlier", "remember", "what did I ask", "what was my problem",
          "what was my issue", "my last request", "my previous request".
          IMPORTANT: If the user is asking what they spoke about before, classify as Memory,
          NOT as Account, even if the topic sounds account-related.
- Unknown: anything that does not fit the above

Few-shot examples:
  "What are the pricing plans?" → Sales
  "My app crashes on upload." → Technical
  "I need a refund." → Billing
  "I forgot my password." → Account
  "What was my previous issue?" → Memory
  "What did I ask last time?" → Memory
  "Do you remember my earlier problem?" → Memory

You MUST respond with ONLY a valid JSON object in the exact format below.
No markdown, no code fences, no extra text:
{
  "intent": "<Intent Name>",
  "confidence": "<high/medium/low>",
  "reasoning": "<brief explanation>"
}
If you are unsure, use "Unknown".
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ])

        # Robust JSON extraction — handles plain JSON and markdown-fenced responses
        content = response.content.strip()
        if "```" in content:
            parts = content.split("```")
            content = parts[1]
            if content.startswith("json"):
                content = content[4:]

        result = json.loads(content.strip())
        intent = result.get("intent", "Unknown")

        # Validate intent against allowed list
        valid_intents = ["Sales", "Technical", "Billing", "Account", "Memory", "Unknown"]
        if intent not in valid_intents:
            intent = "Unknown"

        state["intent"] = intent
        logger.info(f"Classified intent: {intent}")

    except Exception as e:
        logger.error(f"Intent classification failed: {e}. Raw response: {response.content}")
        state["intent"] = "Unknown"

    return state

def create_agent(department_name: str, role_description: str):
    """Factory function to create department-specific agents."""
    def agent_node(state: AgentState) -> AgentState:
        state["department"] = department_name
        query = state["user_query"]
        context = state.get("retrieved_context", "")
        
        system_prompt = f"""
You are the {department_name} Agent for our customer support team.
{role_description}

You must explain policies clearly using ONLY the information provided in the Context below.
Never fabricate or assume company policies. If the context doesn't contain the answer, politely state that you don't have that information.
Write in a professional, customer-friendly tone.

Context:
{context}
"""
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ])
            state["response"] = response.content
        except Exception as e:
            logger.error(f"{department_name} failed: {e}")
            state["response"] = f"I apologize, but I encountered an error processing your request in the {department_name} department."
            
        return state
    return agent_node

# Create the specific agents
SalesAgent = create_agent(
    "Sales", 
    "You handle: pricing, plans, subscriptions, and product information."
)

TechnicalAgent = create_agent(
    "Technical", 
    "You handle: crashes, installation issues, login failures, configuration problems, and upload failures."
)

BillingAgent = create_agent(
    "Billing", 
    "You handle: invoices, payments, and refund requests."
)

AccountAgent = create_agent(
    "Account", 
    "You handle: password reset, account activation, profile updates, and account closure."
)

GeneralSupportAgent = create_agent(
    "General Support", 
    "You handle any queries with an Unknown intent. Acknowledge the query, provide what help you can, and direct the customer to the right channel."
)
