import logging
from config import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name.
    """
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        logger.setLevel(getattr(logging, LOG_LEVEL))
        ch = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

def format_response(query: str, intent: str, department: str, chunks: list[str], 
                    approval_required: bool, approval_status: str, 
                    supervisor_output: str, final_response: str) -> str:
    """
    Wraps response data into the labelled terminal output block required by Task 10.
    """
    chunk_str = "\n".join([f"  [{i+1}] {chunk.strip()}" for i, chunk in enumerate(chunks)])
    if not chunk_str:
        chunk_str = "  None"
        
    approval_req_str = "Yes" if approval_required else "No"
    
    status_map = {
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "N/A": "N/A"
    }
    
    app_status_str = status_map.get(approval_status, approval_status)
    if not approval_required:
        app_status_str = "N/A"
        
    return f"""
============================================================
Query: {query}
------------------------------------------------------------
Detected Intent  : {intent}
Routed Department: {department}
Retrieved Chunks :
{chunk_str}
Approval Required: {approval_req_str}
Approval Decision: {app_status_str}
Supervisor Output: {supervisor_output}
Final Response   : {final_response}
============================================================
"""
