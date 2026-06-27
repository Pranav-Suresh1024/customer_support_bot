```mermaid
flowchart TD
    START --> MemoryRecall
    MemoryRecall --> IntentClassification
    IntentClassification --> Router

    Router -->|Sales| SalesAgent
    Router -->|Technical| TechnicalAgent
    Router -->|Billing| BillingAgent
    Router -->|Account| AccountAgent
    Router -->|Memory| MemoryRecall
    Router -->|Unknown| GeneralSupportAgent

    SalesAgent --> RAGRetrieval
    TechnicalAgent --> RAGRetrieval
    BillingAgent --> RAGRetrieval
    AccountAgent --> RAGRetrieval
    GeneralSupportAgent --> RAGRetrieval

    RAGRetrieval --> ApprovalCheck

    ApprovalCheck -->|Required| HumanApproval
    ApprovalCheck -->|Not Required| SupervisorReview

    HumanApproval -->|Approved| SupervisorReview
    HumanApproval -->|Rejected| StoreMemory

    SupervisorReview --> StoreMemory
    StoreMemory --> FinalResponse
    FinalResponse --> END
```
