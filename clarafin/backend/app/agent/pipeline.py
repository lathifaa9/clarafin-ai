import os
import json
import httpx
import logging
from typing import List, Dict, Any, Optional
from clarafin.backend.app.agent.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger("pipeline")

GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def run_agent_reasoning(
    parsed_docs: List[Dict[str, Any]], 
    benchmarks: dict, 
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends document context and benchmark data to Gemini API,
    enforcing structure and constraints.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return {
            "error": "No Gemini API Key configured. Please set the GEMINI_API_KEY environment variable or configure it in the UI.",
            "current_state": {
                "liquidity": {"metric": "Current Ratio", "value": "cannot be determined from the uploaded documents (API Key Missing)", "interpretation": "Reasoning engine unavailable.", "citations": []},
                "margins": {"metric": "Operating Margin", "value": "cannot be determined from the uploaded documents (API Key Missing)", "interpretation": "Reasoning engine unavailable.", "citations": []},
                "concentration": {"metric": "Revenue Concentration", "value": "cannot be determined from the uploaded documents (API Key Missing)", "interpretation": "Reasoning engine unavailable.", "citations": []},
                "anomalies": []
            },
            "gap_detection": [{"missing_item": "Gemini API Configuration", "blocked_decision": "Autonomous Reasoning", "explanation": "Provide an API key to restore diagnostic functions."}],
            "forward_flags": []
        }

    # Format document contents
    context_str = ""
    for doc in parsed_docs:
        context_str += f"\n=== DOCUMENT: {doc['filename']} (Type: {doc['doc_type']}) ===\n"
        for chunk in doc["chunks"]:
            context_str += f"[{chunk['location']}]: {chunk['text']}\n"
            
    # Include benchmarks
    bench_str = json.dumps(benchmarks, indent=2)
    
    prompt = f"""
Here are the uploaded financial documents:
{context_str}

Here is the sector benchmark data for comparison:
{bench_str}

Perform the analysis. Remember:
- If a figure cannot be derived (such as cash burn if a month is missing), you MUST set its value to 'cannot be determined from the uploaded documents' and detail the missing period.
- Provide a structured interpretation, not a summary.
- Enforce the absolute boundary: No tax/investment recommendations.
"""

    url = f"{GEMINI_URL}/{GEMINI_MODEL}:generateContent?key={key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": SYSTEM_PROMPT + "\n\n" + prompt}
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        with httpx.Client(timeout=90) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            res_json = response.json()
            
            text = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        return {
            "error": f"Failed to execute reasoning pipeline: {str(e)}",
            "current_state": {
                "liquidity": {"metric": "Liquidity Metrics", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "margins": {"metric": "Gross & Net Margins", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "concentration": {"metric": "Revenue Concentration", "value": "cannot be determined from the uploaded documents", "interpretation": "Reasoning failed.", "citations": []},
                "anomalies": []
            },
            "gap_detection": [{"missing_item": "Reasoning Loop Execution", "blocked_decision": "Full diagnostic insight", "explanation": "Inference engine failed to return a response."}],
            "forward_flags": []
        }
