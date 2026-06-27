from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 1024

class ChatResponse(BaseModel):
    response: str
    cached: bool = False
    tokens_used: int = 0