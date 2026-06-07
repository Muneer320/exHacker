# Cost Optimization Guide

## Target: $0/Month Deployment

exHacker is designed to run at **zero cost** by leveraging free tiers across all services. This guide covers every aspect of cost management.

---

## Student/Hackathon $0 Profile

| Service | Platform | Cost | Notes |
|---------|----------|------|-------|
| Frontend | Vercel Free | $0 | 100 GB bandwidth, auto HTTPS |
| Backend API | Railway Free | $0 | $5 credit/month, auto-sleep |
| Database | Supabase Free | $0 | 500 MB PostgreSQL |
| Vector DB | Qdrant Free | $0 | 1 GB storage |
| LLM | Grok (free) + Ollama local | $0 | No cost inference |
| Monitoring | BetterStack Free | $0 | 10 monitors, 1 GB logs |
| Domain | `*.vercel.app` | $0 | Free subdomain |

**Total: $0.00/month**

---

## LLM Cost Comparison

| Provider | Cost per 1K input | Cost per 1K output | Free Tier | Recommended For |
|----------|-------------------|--------------------|-----------|-----------------|
| **Grok (xAI)** | $0.00 | $0.00 | Currently free | Primary free option |
| **Gemini 2.0 Flash** | $0.00 | $0.00 | 15 RPM free | Secondary free option |
| **Gemini 2.0 Pro** | $0.00 | $0.00 | Limited free tier | Higher quality when needed |
| **OpenAI GPT-4o** | $0.01 | $0.03 | None | When quality is critical |
| **OpenAI GPT-4o-mini** | $0.00015 | $0.0006 | None | Budget paid option |
| **Ollama (local)** | $0.00 | $0.00 | Unlimited | Development, offline |

### Recommended Strategy

```
Priority 1: Grok (free)      → No cost, highest priority
Priority 2: Gemini (free)    → No cost, fallback if Grok is down
Priority 3: Ollama (local)   → No cost, offline development
Priority 4: OpenAI (paid)    → Only when quality requires it
```

The backend's `LLM_PROVIDER=auto` mode automatically handles this priority chain.

---

## Using Ollama for Zero-Cost LLM Inference

Ollama runs models locally on your machine with no API costs.

### Installation

```bash
# Windows
winget install ollama

# macOS
brew install --cask ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### Pull a Model

```bash
ollama pull llama3.2
# Or smaller/faster models:
ollama pull mistral
ollama pull phi
```

### Configure exHacker to Use Ollama

```ini
# .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Running in Production (Same Machine)

You can run Ollama alongside the backend on a single VM or dedicated GPU machine. For Railway/Render, Ollama won't fit in the free tier, but you can:

1. Run Ollama on a separate local machine
2. Point `OLLAMA_BASE_URL` to that machine's IP
3. Use it for development and testing at zero cost

---

## Cost Tracking Endpoints

The built-in cost tracker records every LLM call and exposes endpoints to monitor spending.

### View Cost Summary

```bash
GET /api/v1/debug/costs
```

**Response:**
```json
{
  "total_cost": 0.0,
  "total_tokens": 12500,
  "total_calls": 15,
  "by_provider": {
    "grok": {
      "calls": 10,
      "tokens": 8500,
      "cost": 0.0
    },
    "gemini": {
      "calls": 5,
      "tokens": 4000,
      "cost": 0.0
    }
  }
}
```

### View Configured Providers

```bash
GET /api/v1/debug/providers
```

**Response:**
```json
[
  { "name": "grok", "model": "grok-2-latest" },
  { "name": "gemini", "model": "gemini-2.0-flash" },
  { "name": "openai", "model": "gpt-4o" }
]
```

### Reset Cost Tracker

```bash
POST /api/v1/debug/costs/reset
```

### Programmatic Access

```python
from app.services.llm import llm_service

# Get cost summary
summary = llm_service.summary()

# Total cost so far
total = llm_service.get_cost_tracker().total_cost

# All entries
entries = llm_service.get_cost_tracker().entries
```

---

## Token Optimization Tips

### 1. Use Shorter System Prompts

Keep system prompts concise. Instead of verbose instructions:

```python
# ❌ Expensive
system_prompt = """
You are an expert hackathon project analyst with 15 years of experience
in judging hackathons and evaluating project proposals...
"""

# ✅ Efficient
system_prompt = "Analyze this hackathon challenge and extract key requirements."
```

### 2. Reduce Max Tokens

Only request as many tokens as you need:

```ini
# .env
OPENAI_MAX_TOKENS=2048   # Instead of 4096
```

### 3. Use Smaller Models for Simple Tasks

For structured data extraction or simple classification, use cheaper models:

```python
# For complex reasoning
llm_service.generate(prompt, agent_name="architect")

# For simple extraction, use OpenAI's cheaper model
# (Not implemented yet - future optimization)
```

### 4. Cache Repeated Results

If the same challenge is processed multiple times, cache the results:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def analyze_challenge(challenge_text: str) -> dict:
    return await llm_service.generate(...)
```

### 5. Batch Similar Requests

Combine multiple small prompts into one larger prompt to reduce token overhead:

```python
# ❌ Expensive: 5 separate calls
for idea in ideas:
    result = await llm_service.validate(idea)

# ✅ Efficient: 1 batch call
result = await llm_service.validate_all(ideas)  # Hypothetical batch method
```

### 6. Monitor Prompt Sizes

Log prompt sizes to identify overly verbose prompts:

```python
# app/services/llm/service.py already tracks tokens per call
# Check /debug/costs to see token counts per provider
```

---

## Platform Cost Breakdown

### Backend Hosting Comparison

| Platform | Free Tier Cost | RAM | CPU | Auto-Sleep | Monthly Hours | Overages |
|----------|---------------|-----|-----|------------|---------------|----------|
| Railway | $0 (with $5 credit) | 500 MB | Shared | 5 min inactivity | ~300h (credit) | Credit depleted |
| Render | $0 | 512 MB | 0.1 vCPU | 15 min inactivity | 750h | Hours blocked |
| Fly.io | $0 (card required) | 256 MB | Shared | No | 2340h | Bandwidth $ |
| Northflank | $0 | 1 GB | Shared | Yes | Limited | Pay-as-you-go |

### Database Cost Comparison

| Platform | Free Storage | Connections | Backup | Overages |
|----------|-------------|-------------|--------|----------|
| Supabase | 500 MB | 10 regular + 5 pgbouncer | 7 days | $0.015/GB/month |
| Neon | 500 MB | 10 | 7 days | $3.50/GB/month |
| Railway Postgres | $5 credit | Included | None | Credit depleted |

### Frontend Hosting Comparison

| Platform | Bandwidth | Build Minutes | Concurrency | Domains |
|----------|-----------|---------------|-------------|---------|
| Vercel Free | 100 GB | 6000 | 1 | Unlimited custom |
| Netlify Free | 100 GB | 300 | 1 | Unlimited custom |
| Cloudflare Pages | Unlimited | 500 | 1 | Unlimited custom |

---

## Cost Audit Checklist

- [ ] Verified all LLM providers are set to free-tier options (Grok, Gemini)
- [ ] Confirmed `LLM_PROVIDER=auto` to prioritize free providers
- [ ] Checked `/debug/costs` to verify tokens and cost are $0
- [ ] Reviewed system prompt sizes (under 500 tokens where possible)
- [ ] Verified database connection pooling is efficient (not opening/closing constantly)
- [ ] Confirmed frontend is not making redundant API calls
- [ ] Checked that auto-sleep is enabled on Railway/Render
- [ ] Verified no OpenAI API key is set (to avoid accidental charges)
- [ ] Set up cost alerts if using any paid service

---

## If You Exceed Free Tiers

If you hit free tier limits, upgrade in this order (lowest cost first):

1. **Database**: Supabase Pro ($25/month) → 8 GB database
2. **Backend**: Railway Hobby ($5/month) → No sleep, more CPU
3. **LLM**: Add OpenAI $5 prepaid → Use GPT-4o-mini ($0.00015/$0.0006 per 1K)
4. **Monitoring**: BetterStack Pro ($18/month) → 30s check intervals
5. **Everything**: DigitalOcean $12 droplet → Single VM with all services
