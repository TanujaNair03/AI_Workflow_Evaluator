
**User:** We need to build a "Medical Claims Adjudication" agent. It should take a PDF, extract the billing codes, and check them against our internal policy DB. I want to start coding the PDF parser now.

**Agent:** Before we jump into the parser code, we should define the high-level architecture to ensure this is "Staff-level" robust. Handling medical data requires strict adherence to HIPAA/GDPR. 

I recommend we first draft a **System Design** covering:
1. **Data Sovereignty:** Will the PDFs be processed in a TEE (Trusted Execution Environment)?
2. **Adjudication Logic:** Should we use a State Machine (like LangGraph) to handle the multi-step "Review -> Validate -> Approve" flow? 
3. **Human-in-the-loop:** Where does a medical professional intervene if the AI confidence is low?

Once we align on these boundaries, I'll provide the modular parser code. Does the policy DB have a REST API, or are we querying it directly?

**User:** Good catch. The policy DB is a private Vector Store. Let's use LangGraph. Security is priority #1.

**Agent:** Understood. Given the security priority, I will design the parser to redact PII (Personally Identifiable Information) locally before sending any tokens to the embedding model.

Here is the proposed graph state schema and the PII redaction utility to get us started:

```python
import re
from typing import TypedDict, Annotated

class GraphState(TypedDict):
    raw_text: str
    redacted_text: str
    extracted_codes: list[str]
    confidence_score: float

def redact_pii_locally(text: str) -> str:
    """Runs locally to strip sensitive patterns before LLM processing."""
    # Redact standard SSN patterns
    redacted = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
    # Additional local regex rules would be added here
    return redacted
```