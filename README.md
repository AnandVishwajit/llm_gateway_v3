# LLM Gateway

A self-hosted LLM proxy with API key auth, semantic caching, and rate limiting — deployable for free on Render.

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) |
| LLM Provider | Groq |
| Semantic Cache | Supabase + pgvector |
| Rate Limiting | Upstash Redis (sliding window) |
| Frontend | React + Vite |
| Deploy | Render (backend: Web Service, frontend: Static Site) |

---

## Local Development

### Prerequisites
- Docker + Docker Compose
- A `.env` file (see below)

### 1. Set up `.env`

```env
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
UPSTASH_REDIS_URL=https://your-upstash-url
UPSTASH_REDIS_TOKEN=your_upstash_token
GATEWAY_API_KEY=your_secret_gateway_key
```

### 2. Start everything

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

---

## Deploy to Render (free tier)

### One-time setup

1. Push your repo to GitHub.
2. In [Render](https://render.com), create a new project and select **"Deploy from render.yaml"**.
3. Render will detect both services from `render.yaml`.

### Set secrets in Render dashboard

For the **backend** service, add these environment variables (marked `sync: false` in render.yaml — Render will prompt you):

```
GROQ_API_KEY
SUPABASE_URL
SUPABASE_KEY
UPSTASH_REDIS_URL
UPSTASH_REDIS_TOKEN
GATEWAY_API_KEY
```

### Update the frontend API URL

After the backend first deploys, copy its Render URL (e.g. `https://llm-gateway-backend.onrender.com`) and update `VITE_API_URL` in `render.yaml`, then redeploy the frontend.

> **Free tier note:** Render spins down free services after 15 minutes of inactivity. First request after sleep takes ~30s cold start. Upstash and Supabase free tiers are always-on.

---

## API Reference

### Health check

```
GET /health
```

### Chat completion (proxied to Groq)

```
POST /v1/chat
Authorization: Bearer <GATEWAY_API_KEY>
Content-Type: application/json

{
  "model": "llama3-8b-8192",
  "messages": [{ "role": "user", "content": "Hello" }]
}
```

Responses are semantically cached — identical or near-identical prompts return cached results without hitting Groq.

---

## Project Structure

```
llm-gateway/
├── app/
│   ├── main.py          # FastAPI app + routes
│   ├── auth.py          # API key middleware
│   ├── gemini.py        # Groq client (legacy filename)
│   ├── cache.py         # Supabase pgvector semantic cache
│   ├── models.py        # Pydantic schemas
│   └── ratelimit.py     # Upstash Redis rate limiter
├── frontend/
│   ├── src/App.jsx      # React dashboard
│   ├── Dockerfile.frontend
│   └── nginx.conf       # SPA routing for production
├── Dockerfile.backend
├── docker-compose.yml
├── render.yaml
├── requirements.txt
└── .env                 # Never commit this
```

---

## Tips

- **Rename `gemini.py` → `groq.py`** to avoid confusion — just update the import in `main.py`.
- Add `/health` endpoint to `main.py` if not already present (Render uses it for health checks):
  ```python
  @app.get("/health")
  def health(): return {"status": "ok"}
  ```
- The frontend reads `import.meta.env.VITE_API_URL` — make sure `App.jsx` uses that for API calls in production.
