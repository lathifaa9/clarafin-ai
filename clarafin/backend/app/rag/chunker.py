from typing import List, Dict, Any

def chunk_parsed_document(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Takes a parsed document dictionary and returns list of structure-aware chunks.
    For financial documents, each row, line, or sheet row is treated as a chunk
    retaining metadata.
    """
    chunks = []
    filename = parsed_doc["filename"]
    doc_type = parsed_doc["doc_type"]
    
    for c in parsed_doc["chunks"]:
        chunks.append({
            "text": c["text"],
            "location": c["location"],
            "page": c["page"],
            "detail": c["detail"],
            "filename": filename,
            "doc_type": doc_type
        })
    return chunks
