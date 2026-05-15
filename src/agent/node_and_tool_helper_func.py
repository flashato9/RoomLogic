from langgraph.store.base import BaseStore

from agent.models import MemoryValue

async def get_relevant_memories(
    query: str, 
    namespace: tuple, 
    store: BaseStore, 
    threshold: float = 0.70,
    limit: int = 5
) -> str:
    """
    Retrieves the most semantically relevant memories, sorts them 
    chronologically, and formats them with timestamps.
    """
    # 1. Perform semantic search (Ordered by Score)
    search_results = await store.asearch(namespace, query=query, limit=limit)
    
    if not search_results:
        return ""

    # 2. Filter by threshold and parse into MemoryValue objects
    relevant_memories = [
        MemoryValue(**res.value) 
        for res in search_results 
        if res.score >= threshold
    ]

    if not relevant_memories:
        return ""

    # 3. Sort by created_at (Oldest -> Newest)
    # This ensures the most recent information is the last thing the LLM reads.
    relevant_memories.sort(key=lambda m: m.created_at)

    # 4. Format for the LLM
    header = "\nRelevant Long-term Context (Chronological Order):\n"
    
    formatted_items = []
    for m in relevant_memories:
        # Option A: Clean ISO format (e.g., 2026-05-13 23:38)
        # We replace the 'T' with a space and take the first 16 characters
        timestamp_label = m.created_at.replace("T", " ")[:16]
        
        # 2. Append with the category and content
        formatted_items.append(f"- [{timestamp_label}] ({m.category}) {m.content}")
    
    return header + "\n".join(formatted_items)