import os
import json
import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("analyzer")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# The configured Groq developer tier allows 12,000 tokens per minute. PDF text
# is token-dense, so a conservative 12k-character source budget leaves room
# for the instructions and a structured response within that allowance.
MAX_CONTEXT_CHARS = 12_000
FINANCIAL_KEYWORDS = (
    "revenue", "sales", "income", "profit", "loss", "margin", "cash", "bank",
    "balance", "expense", "cost", "invoice", "receivable", "payable", "tax",
    "debt", "loan", "transaction", "opening", "closing",
)


def build_document_context(parsed_docs: List[Dict[str, Any]], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """Create a bounded, citation-ready context that fits within the model request.

    Large PDFs can produce thousands of extracted lines. Sending every line makes
    the chat-completions request exceed the model context window and produces a
    400 response. Prioritise finance-relevant rows, then fill the remaining
    budget in document order so every retained statement stays traceable.
    """
    candidates = []
    for doc in parsed_docs:
        for chunk in doc.get("chunks", []):
            raw_text = str(chunk.get("text", "")).strip()
            if not raw_text:
                continue
            rendered = f"[{doc['filename']} | {chunk.get('location', 'Unknown location')}]: {raw_text}\n"
            score = sum(keyword in raw_text.lower() for keyword in FINANCIAL_KEYWORDS)
            candidates.append((score, rendered))

    # Keep the highest-signal rows first, while retaining stable ordering for ties.
    candidates.sort(key=lambda item: item[0], reverse=True)
    selected, used = [], 0
    for _, rendered in candidates:
        if used + len(rendered) > max_chars:
            continue
        selected.append(rendered)
        used += len(rendered)
        if used >= max_chars:
            break

    if not selected:
        return "No readable content could be extracted from the uploaded documents."
    if len(selected) < len(candidates):
        selected.append("\n[Context note]: The source set was condensed to the most finance-relevant, cited rows to fit the analysis window.\n")
    return "".join(selected)

def run_groq_analysis(parsed_docs: List[Dict[str, Any]], benchmark_data: dict, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Combines parsed document context with benchmark data and prompts Groq.
    to perform autonomous financial analysis with traceability.
    """
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return {
            "error": "No Groq API key configured. Set GROQ_API_KEY for the backend or enter a Groq key in the workspace.",
            "current_state": "cannot be determined from the uploaded documents (API Key Missing)",
            "gap_detection": "A valid Groq API key is required to run the reasoning agent.",
            "forward_flags": "Cannot compute forward flags without AI services."
        }

    # Format document contents for the prompt
    context_str = build_document_context(parsed_docs)
            
    # Format benchmark data
    bench_str = json.dumps(benchmark_data, indent=2)
    
    # Construct System Prompt
    system_prompt = """You are a Financial Document Intelligence Agent for SMEs.
Your goal is to autonomously interpret financial documents (invoices, bank statements, P&L, balance sheets, cash flow reports) and output a reasoned analysis.

You MUST follow these strict rules:
1. NO TAX ADVICE OR INVESTMENT RECOMMENDATIONS: You must stop at analysis and flagging. If requested to advise on what the SME *should* do, decline and direct to a qualified professional.
2. STRICT TRACEABILITY: Every number, calculation, ratio, or claim must be traceable to a specific source document and location (Page/Row/Line). Include the exact text cited.
3. STRICT DATA INTEGRITY: If a figure cannot be derived from the uploaded content, you MUST write "cannot be determined from the uploaded documents" — never approximate or invent a number.
4. NO QUERY NEEDED: Provide a complete current state analysis, gap detection, and forward flags based solely on the uploaded files.

You must return a structured JSON response matching this schema:
{
  "current_state": {
    "liquidity": {
      "metric": "e.g. Current Ratio or Quick Ratio or Cash Balance",
      "value": "Derived ratio value or 'cannot be determined from the uploaded documents'",
      "interpretation": "Reasoned interpretation of the numbers, NOT just a summary. Compare with benchmarks if available.",
      "citations": [{"doc": "filename", "loc": "location details", "text": "exact row/line cited"}]
    },
    "margins": {
      "metric": "e.g. Gross Margin % or Net Margin %",
      "value": "Derived margin value or 'cannot be determined from the uploaded documents'",
      "interpretation": "Reasoned interpretation showing margin trend (squeeze, expansion).",
      "citations": [{"doc": "filename", "loc": "location details", "text": "exact row/line cited"}]
    },
    "concentration": {
      "metric": "e.g. Revenue concentration ratio or top customer share",
      "value": "Derived value or 'cannot be determined from the uploaded documents'",
      "interpretation": "Analysis of dependencies on specific customers or vendors.",
      "citations": [{"doc": "filename", "loc": "location details", "text": "exact row/line cited"}]
    },
    "anomalies": [
      {
        "title": "Title of anomalous pattern",
        "description": "Details of the anomalous expense, duplicate SaaS charge, or cash transaction.",
        "citations": [{"doc": "filename", "loc": "location details", "text": "exact row/line cited"}]
      }
    ]
  },
  "gap_detection": [
    {
      "missing_item": "e.g. Accounts Receivable Aging or Cash Flow Statement",
      "blocked_decision": "What business decision cannot be made because of this gap",
      "explanation": "Why it matters for a healthy financial picture (framed as a helpful reminder, not an error)."
    }
  ],
  "forward_flags": [
    {
      "flag_type": "Runway Risk | Receivables Risk | Seasonal Pressure",
      "trajectory_observation": "Observations of where the business is heading based on current trajectory.",
      "severity": "Low | Medium | High"
    }
  ]
}

DO NOT include any text before or after the JSON block. Output ONLY a valid JSON object.
"""

    prompt = f"""
Here are the uploaded financial documents:
{context_str}

Here is the sector benchmark data for comparison:
{bench_str}

Perform the analysis. Remember, if you cannot derive any figure, state "cannot be determined from the uploaded documents".
"""

    # Groq provides an OpenAI-compatible chat-completions endpoint.
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_completion_tokens": 1600,
        "response_format": {"type": "json_object"},
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    
    try:
        with httpx.Client(timeout=90) as client:
            response = client.post(GROQ_URL, json=payload, headers=headers)
            response.raise_for_status()
            res_json = response.json()
            
            # Extract text from response
            text = res_json["choices"][0]["message"]["content"]
            
            # Parse response into a dict
            return json.loads(text.strip())
            
    except Exception as e:
        provider_detail = ""
        # Try to parse response text if it exists but failed JSON parsing
        try:
            if 'response' in locals() and response.text:
                provider_detail = response.text[:800]
                logger.error(f"Groq API request failed: {e}; response body: {provider_detail}")
        except Exception:
            pass
        if not provider_detail:
            logger.error(f"Groq API request failed: {e}")
            
        return {
            "error": "The reasoning service could not complete this request. Please try again with a smaller document set." if not provider_detail else f"The reasoning service rejected this request: {provider_detail}",
            "current_state": {
                "liquidity": {"metric": "Cash & Liquidity", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "margins": {"metric": "Margins", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "concentration": {"metric": "Concentration", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "anomalies": []
            },
            "gap_detection": [{"missing_item": "Agent reasoning services", "blocked_decision": "Full autonomous diagnosis", "explanation": "The AI model encountered an error during inference."}],
            "forward_flags": []
        }
