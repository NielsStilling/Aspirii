# AI Blog Automation Pipeline — Aspirii

## What This Is

A fully automated SEO-first blog content pipeline for an AI-focused blog. Six specialised subagents orchestrated by Claude Code produce content clusters — pillar pages surrounded by supporting articles with strategic internal linking.

## Architecture

See `reference/AI-Blog-Automation-Architecture-v2.md` for full details.

### Pipeline Flow

```
Scout → topics.json → Analyst → brief.json → Writer → draft.json → Editor → final.json → Publisher → WordPress
                                                                       │
                                                                 rejection.json → back to Writer (max 2 retries)
```

### Agents

| Agent | SKILL File | Trigger | Output |
|-------|-----------|---------|--------|
| Scout v2 | `agents/scout/SKILL-scout-agent-v2.md` | Daily cron / RSS | `workspace/topics.json` |
| Analyst v2 | `agents/analyst/SKILL-analyst-agent-v2.md` | After Scout | `workspace/brief.json` |
| Writer v3 | `agents/writer/SKILL-writer-agent-v3.md` | After Analyst | `workspace/draft.json` |
| Editor v3 | `agents/editor/SKILL-editor-agent-v3.md` | After Writer | `workspace/final.json` or `workspace/rejection.json` |
| Publisher v2 | `agents/publisher/SKILL-publisher-agent-v2.md` | After Editor accepts | WordPress + updates |
| Auditor v1 | `agents/auditor/SKILL-auditor-agent-v1.md` | Monthly (1st) | `data/audit-reports/audit-report-YYYY-MM.json` |

The Humanizer (`agents/writer/SKILL-humanizer-combined.md`) is a reference skill used by Writer and Editor, not a standalone agent.

## Directory Structure

```
agents/           — SKILL files for each subagent
config/           — article-plan.json, rss-feeds.json, integration-map.md
workspace/        — pipeline handoff JSON files (topics, brief, draft, final)
data/             — published-posts-index.json, dedup-index.json, audit-reports/
orchestrator/     — pipeline runner script
reference/        — architecture docs, style samples
```

## Running the Pipeline

### Full daily run (Scout → Publisher)
```bash
./orchestrator/run-pipeline.sh
```

### Individual agents
```bash
./orchestrator/run-pipeline.sh scout
./orchestrator/run-pipeline.sh analyst
./orchestrator/run-pipeline.sh writer
./orchestrator/run-pipeline.sh editor
./orchestrator/run-pipeline.sh publisher
```

### Monthly audit
```bash
./orchestrator/run-pipeline.sh auditor
```

## Key Rules

1. **Every article belongs to a cluster.** No orphan posts.
2. **Breaking news gets priority** over planned content.
3. **Editor can reject drafts** — Writer retries with guidance (max 2 retries).
4. **Internal linking is structural** — Editor rejects if <75% of brief's outbound links used.
5. **Humanisation is non-negotiable** — 30 AI pattern categories checked, blacklist enforced.
6. **The article plan is a config file** — edit `config/article-plan.json` to change priorities.

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys. Required:

- `ANTHROPIC_API_KEY` — Claude API (all agents)
- `WORDPRESS_URL` — Your WordPress site URL
- `WORDPRESS_APP_PASSWORD` — WordPress application password
- `WORDPRESS_USERNAME` — WordPress username

Optional (add as needed):
- `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`
- `OPENAI_API_KEY` (DALL-E 3 images)
- `INDEXNOW_API_KEY`
- `BUFFER_ACCESS_TOKEN`
- `GSC_CREDENTIALS_PATH` (Google Search Console)
- `GA4_CREDENTIALS_PATH` (Google Analytics 4)

## Content Strategy

The blog builds **topical authority** through content clusters:

- **Cluster 1 (active):** AI Models in 2026 — pillar + 6 core + 3 sub-clusters (Claude, GPT, Gemini)
- **Future clusters:** AI Agents, AI for Business, AI Dev Tools, AI Safety

Publishing cadence:
- Phase 1 (weeks 1-7): 4 articles/week
- Phase 2 (weeks 8-16): 2-3 articles/week
- Phase 3 (week 16+): 2 articles/week steady state

## Dual-Mode Priority

Each day the Scout evaluates:
1. Breaking AI news (last 48h, high search demand) → publish urgently
2. Auditor recommendations (monthly) → refresh/consolidate/expand
3. Planned articles from article-plan.json → fill cluster gaps
