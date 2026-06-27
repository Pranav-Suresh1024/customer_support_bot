from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from config import LLM_MODEL, LLM_TEMPERATURE
from state import AgentState
from utils import setup_logger

logger = setup_logger(__name__)
llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)


def supervisor_review_node(state: AgentState) -> AgentState:
    """
    Supervisor agent that reviews and polishes the draft response
    before it is delivered to the customer.
    """
    draft    = state.get("response", "")
    context  = state.get("retrieved_context", "")
    query    = state.get("user_query", "")
    department = state.get("department", "Unknown")

    # --- Memory branch ---
    if department == "Memory":
        if not state.get("final_response"):
            state["final_response"] = draft or "No previous records found."
        return state

    # --- Build the context block ---
    if context:
        context_block = (
            "Reference Context (retrieved from the knowledge base — use ALL relevant sections):\n"
            + context
        )
    else:
        context_block = "Reference Context: Not available."

    system_prompt = f"""You are the Quality Assurance Supervisor for a customer support team.
Your job is to improve a draft response written by the {department} Agent before it is sent to the customer.

YOU MUST apply every rule below without exception:

1. ANSWER THE SPECIFIC QUESTION ASKED.
   The highest priority is answering the user's exact question.
   If multiple retrieved chunks discuss different problems, only use the chunks that directly answer the customer's issue.
   Ignore unrelated chunks even if they are retrieved.
   Example: if the customer says "my app crashes on upload", answer about upload crashes —
   not about startup crashes, even if the context mentions both.

2. USE ALL RELEVANT INFORMATION FROM THE CONTEXT.
   Read every chunk in the Reference Context. If multiple chunks contain relevant information
   (e.g. a pricing list AND an add-ons section), combine them into one complete answer.
   Do not ignore chunks just because the draft did not use them.

3. DO NOT CONTRADICT THE CONTEXT.
   Every factual claim must be supported by the Reference Context.
   Do not invent policies, prices, or procedures.

4. FIX ALL GRAMMAR AND SPELLING ERRORS.
   Correct every grammar, spelling, and punctuation mistake in the draft.

5. IMPROVE FORMATTING.
   Use numbered steps for instructions. Use short paragraphs.
   Do not use large blocks of unbroken text.

6. ENSURE A PROFESSIONAL AND WARM TONE.
   The response must sound helpful, polite, and customer-friendly throughout.

7. PRESERVE THE ENTIRE RESPONSE
    If the response does not already end politely,
    append ONE courteous closing sentence.
    Never replace the response with only the closing sentence.

8. OUTPUT RULES — CRITICAL:
   - Output ONLY the final customer-facing response.
   - Do NOT include any headings like "Improved Response:" or "Here is the revised version:".
   - Do NOT repeat or copy any instruction text.
   - Do NOT include meta-commentary of any kind.
   - Never remove important factual information from the draft response.
   - Never shorten the response unless it contains repetition.
   - The final response should contain all useful information from the draft plus any additional relevant context.

{context_block}"""

    user_prompt = f"""User Query: {query}

Draft Response:
{draft}"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        improved = response.content.strip()

        # Sanity check: reject suspiciously short or empty outputs
        if len(improved) < 20:
            logger.warning("Supervisor returned too-short response. Falling back to draft.")
            state["final_response"] = draft
        else:
            state["final_response"] = improved

    except Exception as e:
        logger.error(f"Supervisor review failed: {e}")
        state["final_response"] = draft

    return state
