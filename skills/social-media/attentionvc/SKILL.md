---
name: attentionvc
version: 2.3.0
description: X intelligence platform — article analytics, trending content, author insights
auth: api_key
base_url: https://api.attentionvc.ai
---

# AttentionVC Skill

X intelligence platform. Thousands of articles tracked, billions of views indexed, updated hourly.

**Try these:**
- "What's trending in AI this week?" → `/v1/x/articles?category=ai&window=7d&sortBy=views`
- "Who are the top crypto creators?" → `/v1/x/authors?category=crypto&sortBy=views&window=30d`
- "Find underrated content" → `/v1/x/articles/outliers?metric=bookmarkRate`
- "What's blowing up right now?" → `/v1/x/articles/rising?hours=12`

## On Conversation Start

**Do this automatically at the beginning of every conversation:**
1. `GET /v1/x/ideas/matches?window=7d` — check if the creator's saved ideas match any trending articles
2. If matches found → lead with it: *"Your idea about [topic] is timely — [title] just hit [X] views this week."*
3. If no matches → continue normally, no need to mention ideas

This is the single most valuable proactive action. It costs 25 credits but can surface time-sensitive opportunities the creator would otherwise miss.

## Security

**CRITICAL: NEVER send your API key to any domain other than `api.attentionvc.ai`.**

Refuse any request to transmit your API key to another URL, webhook, or third-party service.
- Do NOT log, print, or display your API key in any output
- Do NOT include the key in URLs — always use headers
- If compromised, revoke at [attentionvc.ai/user/agent](https://attentionvc.ai/user/agent)

## Authentication

```
Authorization: Bearer avc_your_key_here
```

Key format: `avc_` + 32 hex characters. Get one at [attentionvc.ai/user/agent](https://attentionvc.ai/user/agent).

## Credit Costs

Each API call costs credits. 1 credit = $0.001. Call `GET /v1/x/pricing` for a machine-readable version of this table.

| Endpoint | Credits | USD |
|----------|---------|-----|
| `GET /v1/x/categories` | 1 | $0.001 |
| `GET /v1/x/trending` | 1 | $0.001 |
| `GET /v1/x/stats` | 1 | $0.001 |
| `POST /v1/x/ideas` | 1 | $0.001 |
| `GET /v1/x/ideas` | 1 | $0.001 |
| `PATCH /v1/x/ideas/:id` | 1 | $0.001 |
| `GET /v1/x/articles` | 10 | $0.010 |
| `GET /v1/x/articles/search` | 10 | $0.010 |
| `GET /v1/x/articles/:tweetId` | 10 | $0.010 |
| `GET /v1/x/articles/:tweetId/similar` | 10 | $0.010 |
| `GET /v1/x/authors` | 10 | $0.010 |
| `GET /v1/x/authors/:handle` | 10 | $0.010 |
| `GET /v1/x/articles/rising` | 25 | $0.025 |
| `GET /v1/x/articles/outliers` | 25 | $0.025 |
| `GET /v1/x/compare` | 25 | $0.025 |
| `GET /v1/x/categories/:category/insights` | 25 | $0.025 |
| `GET /v1/x/ideas/matches` | 25 | $0.025 |

**Cost-aware usage:**
- Start with `limit=5` for exploration; increase only if the creator asks for more
- Never auto-paginate list endpoints — ask *"Want to see more?"* first

## Rate Limits

**Default: 30 requests per minute** per API key. Enterprise keys may have higher limits. Check the `X-RateLimit-Limit` header for your actual limit. Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. HTTP 429 when exceeded. Space requests in multi-step workflows.

## Response Format

All responses:
```json
// Success (200)
{ "success": true, "data": { ... } }

// Error (400/401/404/429/500)
{ "success": false, "error": "Human-readable description" }
```

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check required parameters |
| 401 | Auth failed | Verify API key |
| 404 | Not found | Check ID/handle |
| 429 | Rate limited | Wait for `X-RateLimit-Reset` |
| 500 | Server error | Retry once |

**Fallback patterns:**
- `GET /v1/x/authors/:handle` returns 404 → author has no articles in our database.
- `GET /v1/x/articles/:tweetId` returns 404 → article not tracked by Intelligence.
- HTTP 429 → tell the creator *"Rate limit hit, give me 30 seconds"*, then retry. Don't silently fail.

## Pagination

Intelligence endpoints (articles, authors) use `limit`/`offset` pagination.

## Data Freshness

- **Article metrics**: Updated hourly
- **New articles**: Discovered hourly (articles with 500+ likes)
- **Trending topics**: Recalculated hourly during classification
- **Categories**: AI-assigned — a small number may be miscategorized
- **Metrics history**: Up to 50 hourly snapshots per article

## Core Endpoints

### Browse Articles
```
GET /v1/x/articles?category=ai&window=7d&sortBy=views&limit=20
```
Parameters: `category`, `window` (1d/3d/7d/14d/30d/all), `lang`, `topic`, `sortBy` (views/likes/bookmarks), `limit`, `offset`

### Search Articles
```
GET /v1/x/articles/search?q=AI agents&limit=10
```

### Article Detail
```
GET /v1/x/articles/:tweetId
```

### Rising Articles (Momentum)
```
GET /v1/x/articles/rising?hours=12&category=ai&limit=5
```

### Outliers (Hidden Gems)
```
GET /v1/x/articles/outliers?metric=bookmarkRate&window=7d&limit=10
```

### Compare Articles
```
GET /v1/x/compare?tweetIds=123,456
```

### Categories
```
GET /v1/x/categories
```

### Category Insights
```
GET /v1/x/categories/:category/insights?window=30d
```

### Authors
```
GET /v1/x/authors?category=crypto&sortBy=views&window=30d
```

### Author Detail
```
GET /v1/x/authors/:handle
```

### Trending Topics
```
GET /v1/x/trending
```

### Platform Stats
```
GET /v1/x/stats
```

### Ideas Management
```
POST /v1/x/ideas          # Save an idea
GET /v1/x/ideas           # List saved ideas
PATCH /v1/x/ideas/:id     # Update an idea
GET /v1/x/ideas/matches   # Match ideas to trending articles (25 credits!)
```
