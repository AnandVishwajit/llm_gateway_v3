from fastapi import FastAPI, Depends
from app.models import ChatRequest, ChatResponse
from app.auth import verify_api_key
from app.gemini import call_gemini
from app.cache import find_similar, store_cache, supabase
from app.ratelimit import check_rate_limit

app = FastAPI(title="LLM Gateway")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    # Check rate limit
    check_rate_limit(api_key)

    # Check cache first
    cached = await find_similar(request.message)
    if cached:
        return ChatResponse(
            response=cached["response"],
            cached=True,
            tokens_used=0
        )

    # Cache miss — call Groq
    result = await call_gemini(request.message, request.max_tokens)

    # Store in cache
    await store_cache(
        request.message,
        result["response"],
        result["tokens_used"]
    )

    return ChatResponse(
        response=result["response"],
        cached=False,
        tokens_used=result["tokens_used"]
    )


@app.get("/stats")
async def stats(api_key: str = Depends(verify_api_key)):
    result = supabase.table("cache").select("tokens_used").execute()

    total_requests = len(result.data)
    total_tokens = sum(r["tokens_used"] for r in result.data)

    return {
        "total_cached_entries": total_requests,
        "total_tokens_used": total_tokens
    }