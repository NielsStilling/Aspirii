# AI Blog Automation Pipeline — Aspirii

## What This Is

A fully automated SEO-first blog content pipeline for an AI-focused blog. Claude Code runs all pipeline steps directly in a single session — no subagents, no shell scripts. The SKILL files in `agents/` define the rules for each step; Claude Code has them in context and applies them inline.

## Architecture

See `reference/AI-Blog-Automation-Architecture-v2.md` for full details.

### Pipeline Flow (optimized — ~5-8 minutes per article)

```
Scout → topics.json → Analyst → brief.json → Writer → draft.json → Editor → final.json → Publisher → WordPress draft
```

All steps run directly in the Claude Code conversation. No subagents (they time out on large tasks). No orchestrator script.

### Pipeline Steps

| Step | What happens | Time |
|------|-------------|------|
| **Scout** | Pick topic from article-plan.json or breaking news. Write `workspace/topics.json`. | ~30s |
| **Analyst** | Run DataForSEO for keyword volume + PAA. Web search for sources. Write `workspace/brief.json`. | ~2-3 min |
| **Writer** | Write the full article directly. Follow SKILL rules + Humanizer. Write `workspace/draft.json`. | ~2-3 min |
| **Editor** | Run automated Python checks (blacklist, links, meta lengths) + manual review. Write `workspace/final.json`. | ~1 min |
| **Publisher** | Convert to HTML, POST to WordPress as draft, set Yoast fields. Save `.md` to repo. | ~30s |

### SKILL Files (reference — already in context after first read)

| Step | SKILL File | Key Rules |
|------|-----------|-----------|
| Scout | `agents/scout/SKILL-scout-agent-v2.md` | Dual-mode priority, cluster assignment, dedup |
| Analyst | `agents/analyst/SKILL-analyst-agent-v2.md` | Intent classification, link mapping, experience seeds |
| Writer | `agents/writer/SKILL-writer-agent-v3.md` | 3-Max Rule, opinion density, E-E-A-T signals |
| Humanizer | `agents/writer/SKILL-humanizer-combined.md` | 30 AI patterns, 3-tier word blacklist, voice rules |
| Editor | `agents/editor/SKILL-editor-agent-v3.md` | 4-pass QA, rejection criteria, tighten to ≤95% |
| Publisher | `agents/publisher/SKILL-publisher-agent-v2.md` | WordPress API, schema markup, backlinking |
| Auditor | `agents/auditor/SKILL-auditor-agent-v1.md` | Monthly: rankings, cannibalisation, freshness |

## Directory Structure

```
agents/           — SKILL files (reference docs, read once per session)
config/           — article-plan.json, article-formats.json, rss-feeds.json
workspace/        — pipeline JSON files + published article .md files
data/             — published-posts-index.json, dedup-index.json, audit-reports/
orchestrator/     — dataforseo.py (keyword research utility)
reference/        — architecture docs
```

## Running the Pipeline

Tell Claude Code: **"Write an article about [topic]"** or **"Run the daily pipeline"**.

Claude Code will:
1. Pick/create the topic (Scout)
2. Research with DataForSEO + web search (Analyst)
3. Write the article directly (Writer)
4. Run automated QA checks (Editor)
5. Push to WordPress as draft (Publisher)

### DataForSEO (keyword research)

Used in the Analyst step. Utility at `orchestrator/dataforseo.py`:
```bash
python3 orchestrator/dataforseo.py volume "keyword1" "keyword2"
python3 orchestrator/dataforseo.py related "seed keyword"
python3 orchestrator/dataforseo.py paa "keyword"
```

### Monthly audit
Run manually: "Run the monthly audit" — Claude Code reads GSC/GA4 data and produces `data/audit-reports/audit-report-YYYY-MM.json`.

## Key Rules

1. **Every article belongs to a cluster.** No orphan posts.
2. **Breaking news gets priority** over planned content.
3. **Editor rejects if:** <75% outbound links used, no pillar link, 3+ blacklist phrases, zero experience texture, >3 same structural patterns.
4. **Humanisation is non-negotiable** — 30 AI pattern categories, 47 Tier 1 banned words, structural variation enforced.
5. **The article plan is a config file** — edit `config/article-plan.json` to change priorities.
6. **Vary article formats** — use `config/article-formats.json` to rotate between 5 structural templates. Never use the same format 3+ articles in a row.
7. **FAQ is conditional** — only include when DataForSEO returns real People Also Ask questions with search volume. Not every article needs a FAQ.
8. **DataForSEO drives keyword selection** — validate search volume before committing to a target keyword. Don't guess at PAA questions.

## Article Format Rotation

Five formats defined in `config/article-formats.json`:

| Format | Best for | Has FAQ? |
|--------|----------|----------|
| **Practitioner Story** | Tutorials, migration guides, tool reviews | No |
| **Analysis / Deep Dive** | Model reviews, tech overviews | Only if real PAA |
| **Contrarian / Hot Take** | Opinion pieces, challenging consensus | No |
| **Head-to-Head Comparison** | X vs Y, selection guides | Only if real PAA |
| **How It Works / Tutorial** | API guides, setup guides, workflows | Only if real PAA |

The Analyst picks the format based on topic + intent + what was used recently.

## Environment Variables

Copy `.env.example` to `.env` and fill in your API keys.

**Required for article drafts:**
- `WORDPRESS_URL` — Your WordPress site URL
- `WORDPRESS_USERNAME` — WordPress username
- `WORDPRESS_APP_PASSWORD` — WordPress application password

**Required for keyword research:**
- `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`

**Optional (add as needed):**
- `OPENAI_API_KEY` (DALL-E 3 images)
- `INDEXNOW_API_KEY`
- `BUFFER_ACCESS_TOKEN`
- `GSC_CREDENTIALS_PATH` / `GA4_CREDENTIALS_PATH` (for Auditor)

## Content Strategy

The blog builds **topical authority** through content clusters:

- **Cluster 1 (active):** AI Models in 2026 — pillar + 6 core + 3 sub-clusters (Claude, GPT, Gemini)
- **Future clusters:** AI Agents, AI for Business, AI Dev Tools, AI Safety

## Dual-Mode Priority

Each day the Scout evaluates:
1. Breaking AI news (last 48h, high search demand) → publish urgently
2. Auditor recommendations (monthly) → refresh/consolidate/expand
3. Planned articles from article-plan.json → fill cluster gaps

## WordPress Publishing

Articles are pushed as **drafts** to WordPress via REST API. The human reviews and publishes.

```
POST https://aspirii.com/wp-json/wp/v2/posts
Auth: Basic (WORDPRESS_USERNAME:WORDPRESS_APP_PASSWORD)
Status: draft
```

Yoast SEO fields (meta description, focus keyword) are set via the post meta API.
