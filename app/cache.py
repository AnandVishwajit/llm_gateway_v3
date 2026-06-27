import os
import numpy as np
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY exists:", os.getenv("SUPABASE_KEY") is not None)

SIMILARITY_THRESHOLD = 0.85

def get_embedding(text: str) -> list:
    embedding = model.encode(text)
    return embedding.tolist()

async def find_similar(prompt: str) -> dict | None:
    embedding = get_embedding(prompt)
    
    result = supabase.rpc("match_cache", {
        "query_embedding": embedding,
        "match_threshold": SIMILARITY_THRESHOLD,
        "match_count": 1
    }).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None

async def store_cache(prompt: str, response: str, tokens_used: int):
    embedding = get_embedding(prompt)
    
    supabase.table("cache").insert({
        "prompt": prompt,
        "response": response,
        "tokens_used": tokens_used,
        "embedding": embedding
    }).execute()