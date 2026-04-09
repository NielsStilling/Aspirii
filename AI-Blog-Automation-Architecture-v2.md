# AI Blog Automation Architecture v2
## Fully Automated SEO-First Blog Content Pipeline

---

## Overview

This pipeline produces blog content that is optimised for topical authority, indistinguishable from human writing, and structured as an interconnected SEO system — not isolated posts. It runs 6 specialised subagents orchestrated by n8n, with a dual-mode publishing strategy: breaking news when it appears, planned cluster-building when it doesn't.

The system produces **content clusters** — pillar pages surrounded by 8-20 supporting articles with strategic internal linking — because Google ranks topic ecosystems, not individual pages.

### Key Design Principles

- **Clusters over posts.** Every article belongs to a cluster and strengthens the whole system.
- **News-first, plan-second.** Breaking AI news gets priority (publish within hours). Planned articles fill the gaps on quiet days.
- **Two-pass humanisation.** The Writer applies anti-AI rules during generation. The Editor audits and rejects drafts that still smell like AI.
- **SEO is structural, not cosmetic.** Internal linking, intent matching, cannibalisation prevention, and schema markup are built into every agent — not bolted on at the end.
- **The article plan is a config file, not code.** Swap clusters, reprioritise articles, or add new topics without touching any agent's instructions.

---

## System Architecture

```
                        ┌──────────────────┐
                        │   CRON (24h)     │
                        │   + RSS Triggers │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   AGENT 1        │
                        │   Scout v2       │◄──── article-plan.json
                        │   (Topic Select) │◄──── dedup index
                        └────────┬─────────┘◄──── audit-report.json
                                 │
                          topics.json
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   AGENT 2        │
                        │   Analyst v2     │◄──── DataForSEO API (keywords)
                        │   (Research)     │◄──── Web search / fetch
                        └────────┬─────────┘◄──── Published posts index
                                 │
                          brief.json
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   AGENT 3        │
                        │   Writer v3      │◄──── Style reference samples
                        │   (Draft)        │◄──── Humanizer skill rules
                        └────────┬─────────┘
                                 │
                          draft.json
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   AGENT 4        │
              ┌─REJECT──│   Editor v3      │
              │         │   (QA + SEO)     │
              │         └────────┬─────────┘
              │                  │
              ▼           final.json (or rejection.json)
         Back to                 │
         Writer                  ▼
                        ┌──────────────────┐
                        │   AGENT 5        │──── WordPress REST API
                        │   Publisher v2   │──── IndexNow API
                        │   (Deploy)       │──── DALL-E 3 (images)
                        └────────┬─────────┘──── Buffer (social)
                                 │
                          Updates existing posts
                          Applies schema markup
                          Submits to IndexNow
                          Posts social teasers
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   AGENT 6        │◄──── Google Search Console API
                        │   Auditor v1     │◄──── Google Analytics 4 API
                        │   (Monthly)      │◄──── Published posts index
                        └────────┬─────────┘
                                 │
                          audit-report.json
                          (feeds back to Scout)
```

### Data Flow

```
Scout → topics.json → Analyst → brief.json → Writer → draft.json → Editor → final.json → Publisher → WordPress
                                                                       │
                                                                 rejection.json → back to Writer
```

Each handoff is a JSON file with a strict schema. Agents can be rerun, debugged, or swapped independently.

---

## Agent Specifications

### AGENT 1: Scout v2 — Topic Discovery & Cluster Planning

**Role:** Determine the single most valuable article to publish next. Checks breaking news first, falls back to the article plan.

**Trigger:** Cron — runs every 24 hours. RSS triggers for major AI blogs fire on new items.

**Inputs:**
- RSS feeds (OpenAI, Anthropic, Google, Meta, Mistral, Hacker News, ArXiv)
- article-plan.json (the backlog of planned articles)
- Dedup index (previously published topics)
- audit-report.json (monthly priorities from the Auditor)

**Outputs:** topics.json — single topic brief with cluster assignment, keywords, angle, experience seeds.

**Dual-mode logic:**
1. Is there breaking AI news in the last 48h with high search demand? → Publish as urgent, assign to cluster
2. Does the Auditor's report have priority actions (content refresh, sub-pillar trigger)? → Execute those
3. Neither? → Pull next unpublished article from article-plan.json

**Key capability:** Every topic includes which cluster it belongs to, what role it plays (pillar / sub-pillar / cluster article), and which existing articles it should link to.

**SKILL file:** `SKILL-scout-agent-v2.md`

---

### AGENT 2: Analyst v2 — Research & Brief Builder

**Role:** Take the Scout's topic and produce a complete research brief that the Writer can turn into a publishable post without additional research.

**Trigger:** Webhook — fires when topics.json is written.

**Inputs:** topics.json, web search, DataForSEO API (keyword validation), published posts index.

**Outputs:** brief.json — research, outline, internal link map, intent classification, experience seeds, FAQ questions.

**Key capabilities (new in v2):**
- **Intent classification:** Informational / informational-commercial / transactional. Determines content format.
- **Bidirectional internal link mapping:** Which existing posts this article links TO, and which existing posts should link BACK to this article (for the Publisher to execute post-publish).
- **Experience seeds:** 2-3 specific practitioner scenarios with dollar amounts and real details for E-E-A-T signals.
- **FAQ questions:** Sourced from "People Also Ask" for featured snippet targeting and FAQPage schema.
- **Schema hints:** Notes for the Writer on which sections should be formatted for FAQ, HowTo, or comparison table schema.

**SKILL file:** `SKILL-analyst-agent-v2.md`

---

### AGENT 3: Writer v3 — Draft Generation

**Role:** Write a complete blog post that reads like a knowledgeable human practitioner wrote it. The hardest agent to get right.

**Trigger:** Webhook — fires when brief.json is written.

**Inputs:** brief.json, style reference samples (2-3 example posts), humanizer skill rules.

**Outputs:** draft.json — complete markdown post with frontmatter, cluster assignment, schema types, internal links used.

**Key capabilities:**
- **Anti-AI detection rules:** 3-Max Rule (no repeating section structure), Summary Block Ban, phrase blacklist (30+ banned AI-isms), sentence/paragraph length variance requirements, transition variety mandate.
- **Experience injection:** Minimum 1 practitioner scenario per 500 words with specific numbers.
- **Opinion density:** Minimum 1 personal take per 200 words, embedded in flow (not in labelled boxes).
- **E-E-A-T structural signals:** Author perspective, source citations inline, specific dates for time-sensitive claims, limitations acknowledged.
- **Schema-ready formatting:** FAQ sections with H3 questions, direct answers under H2s for featured snippets, comparison tables for commercial-intent articles.
- **Internal linking:** Uses all outbound links from the brief, places at least one in the top 30% of the article.

**SKILL file:** `SKILL-writer-agent-v3.md`

**Supporting reference:** `SKILL-humanizer-combined.md` (30 AI pattern categories + 3-tier word replacement table)

---

### AGENT 4: Editor v3 — Quality Assurance, Humanisation & SEO Systems

**Role:** Last line of defense. Four-pass review. Can reject drafts back to the Writer.

**Trigger:** Webhook — fires when draft.json is written.

**Inputs:** draft.json, brief.json (for fact-checking), published posts index (for cannibalisation checking).

**Outputs:** final.json (accepted) or rejection.json (sent back to Writer with specific guidance).

**Four passes:**
1. **Humanisation audit** (highest priority) — structural pattern check, sentence/paragraph variance, transition audit, opinion density, experience injection count, blacklist phrase scan, summary block detection. REJECT if structural patterns repeat >3 times or zero experience texture.
2. **Fact-check** — every pricing figure, model name, version number, and date verified against brief sources.
3. **SEO systems check** (new in v3) — cluster fit validation, keyword cannibalisation detection, internal link integrity (all outbound links present? pillar linked? keyword-rich anchor text?), intent match between brief and draft.
4. **On-page SEO** — title/meta under character limits, primary keyword in first 100 words, H2s descriptive and keyword-rich, FAQ section present, featured snippet readiness, schema type declarations.

**Key output:** post_publish_actions array — tells the Publisher exactly which existing articles to update with backlinks to the new post.

**SKILL file:** `SKILL-editor-agent-v3.md`

---

### AGENT 5: Publisher v2 — WordPress Deployment, Cluster Linking & Distribution

**Role:** Publish the final post and maintain the cluster's link architecture.

**Trigger:** Webhook — fires when final.json is written.

**Inputs:** final.json, WordPress API credentials, image generation API, social media templates.

**Outputs:** Published WordPress post, updated existing posts (backlinks), IndexNow submissions, social media teasers.

**Key capabilities (new in v2):**
- **Schema markup injection:** JSON-LD for Article (always), FAQPage (when FAQ section exists), HowTo (when tutorial with steps). Applied via script tag in post content.
- **Post-publish cluster backlinking:** Executes the Editor's post_publish_actions — fetches existing posts via WordPress API, adds inline links with keyword-rich anchor text, updates them.
- **Pillar page update:** Adds a link to the new article in the relevant section of the pillar page. Every new cluster article = pillar gets refreshed.
- **IndexNow submission:** Submits ALL modified URLs (new post + every updated existing post) so search engines re-crawl the whole cluster.
- **Featured image generation:** DALL-E 3 API, 1200x630px, dark background, teal accents. Uploaded to WordPress media library.
- **Social teasers:** LinkedIn (4 lines + link + 4 hashtags) and Twitter/X (under 200 characters + link) via Buffer.
- **Article plan update:** Marks the article as published with URL, date, and WordPress post ID.

**SKILL file:** `SKILL-publisher-agent-v2.md`

---

### AGENT 6: Auditor v1 — Monthly SEO Health & Cluster Integrity

**Role:** Diagnose what's broken, decaying, or missing. Recommend actions. Doesn't publish or edit — only recommends.

**Trigger:** Cron — runs 1st of every month.

**Inputs:** Google Search Console API, Google Analytics 4 API, published posts index, article-plan.json, previous month's audit report.

**Outputs:** audit-report-YYYY-MM.json — prioritised action list that feeds back into the Scout.

**Six audits:**
1. **Cluster completeness** — planned vs published articles, missing pillars/sub-pillars, gap identification.
2. **Ranking performance** — categorises every article as rising/stable/declining/page-2-opportunity/zero-traffic. Flags page 2 articles for optimisation push.
3. **Keyword cannibalisation** — detects when 2+ articles compete for the same query. Recommends consolidation or re-targeting.
4. **Internal link health** — orphan pages (zero inbound links), missing pillar connections, broken links, weak anchor text.
5. **Content freshness** — pricing data older than 2 months, deprecated model references, outdated statistics.
6. **Cluster expansion signals** — orphan article accumulation suggesting new clusters, sub-cluster threshold triggers, competitor gap analysis.

**Priority actions feed back to Scout:** refresh > consolidate > publish sub-pillar > add internal links > optimise page 2 content. Scout checks for fresh audit reports on every run.

**SKILL file:** `SKILL-auditor-agent-v1.md`

---

## Content Strategy

### Cluster Architecture

The blog is organised as a hierarchy of content clusters:

```
Master Cluster: AI Models in 2026
├── Pillar: "The 5 Best AI Models in 2026"
├── Core articles (cross-cutting): pricing, benchmarks, selection guide, migration, routing, open vs closed
├── Sub-cluster: Claude (Anthropic)
│   ├── Sub-pillar: "Claude in 2026: Everything You Need to Know"
│   └── 6 supporting articles (deep dive, Sonnet vs Opus, Batch API, Claude Code, agents, Claude vs GPT)
├── Sub-cluster: OpenAI GPT
│   ├── Sub-pillar: "OpenAI GPT in 2026: The Full Picture"
│   └── 5 supporting articles (deep dive, deprecation, Nano, fine-tuning, API ecosystem)
└── Sub-cluster: Google Gemini
    ├── Sub-pillar: "Google Gemini in 2026: The Budget Powerhouse"
    └── 5 supporting articles (deep dive, free tier, multimodal, context pricing, 3-way comparison)
```

Future clusters (built after Cluster 1 matures): AI Agents, AI for Business, AI Dev Tools, AI Safety & Ethics.

### Sub-cluster trigger: Create a sub-cluster when 5+ articles exist about a specific subtopic within the parent cluster. Write the sub-pillar after 5 articles, not before.

### Cluster size limit: 20-25 articles per cluster. Beyond that, split into sub-clusters or start a new top-level cluster.

### Publishing Strategy

**Phase 1 (weeks 1-7):** 4 articles/week. Build Cluster 1 core structure + begin first sub-cluster. ~28 articles.

**Phase 2 (weeks 8-16):** 2-3 articles/week. Mix of new articles, news responses, and updates to existing posts. Start Cluster 2 when Cluster 1 is solid.

**Phase 3 (week 16+):** 2 articles/week steady state. Mostly news-driven and updates, with planned gap-fillers on quiet weeks.

### Dual-Mode Priority Stack

Every day the Scout evaluates what to publish next:

1. **Breaking news** (high urgency) — publish within hours. Must have high search demand + cluster fit.
2. **Audit recommendations** (monthly priorities) — content refreshes, cannibalisation fixes, sub-pillar triggers.
3. **Planned articles** from article-plan.json — cluster gap-filling on quiet days.

News articles aren't orphans — they get assigned to the relevant cluster and linked into the system. A Gemini release becomes the Gemini deep dive. A pricing change becomes an update to the pricing comparison article.

### Content Update Strategy

Updates to existing articles often outperform new posts because they build on accumulated authority:

**Update when:** The article already ranks but information is outdated, a competitor published better coverage, or the Auditor flags it as declining.

**New post when:** There's a genuinely new subtopic deserving its own page, or the search intent is different from any existing article.

**Ratio over time:**
- Months 1-6: 80% new posts / 20% updates
- Months 6-12: 50% new / 50% updates
- Months 12+: 30% new / 70% updates

---

## SEO System

### Topical Authority

Every article strengthens the cluster it belongs to. The system builds topical authority through:

- **Comprehensive coverage:** 15-25 articles per cluster covering every angle of the topic
- **Internal linking:** Every article links to its pillar, its sub-pillar, and 2-3 sibling articles
- **Consistent publishing:** Regular additions signal to Google that the site is actively maintained
- **Content freshness:** Monthly audits catch and fix outdated information

### E-E-A-T Signals

Built into every article by the Writer and verified by the Editor:

- **Experience:** Practitioner scenarios with specific numbers (1 per 500 words minimum)
- **Expertise:** Technical depth, precise terminology, code examples, edge cases
- **Authoritativeness:** Citations to official docs and research, author attribution, external authority links
- **Trustworthiness:** Transparent about limitations, specific dates on time-sensitive claims, sources cited inline

### Schema Markup

Applied by the Publisher:

- **Article schema:** Every post (author, publisher, dates)
- **FAQPage schema:** When FAQ section exists (pillar pages, tutorials)
- **HowTo schema:** When tutorial with numbered steps

### Internal Linking Rules

- Every cluster article links to its pillar (mandatory)
- Every sub-cluster article links to its sub-pillar AND the main pillar
- Links use keyword-rich anchor text (suggested by the Analyst)
- At least one internal link in the top 30% of the article (Google weights these higher)
- Publisher updates existing posts with backlinks to new articles post-publish
- Pillar page is updated every time a new cluster article publishes

### Cannibalisation Prevention

- Analyst checks target keywords against published posts index
- Editor rejects drafts targeting keywords already owned by another article
- Auditor detects cannibalisation monthly using Search Console query data
- Resolution: consolidate (merge articles) or retarget (change the keyword)

---

## Integrations

| Integration | Agent(s) | Cost | Purpose |
|------------|----------|------|---------|
| DataForSEO API | Scout, Analyst | ~$5/mo | Keyword volume validation, "People Also Ask" extraction |
| Google Search Console API | Auditor, Scout | $0 | Ranking data, cannibalisation detection, declining content |
| Google Analytics 4 API | Auditor | $0 | Traffic, bounce rate, engagement metrics |
| Claude API (Sonnet 4.6) | All agents | $8-16/mo | Core LLM powering all reasoning |
| WordPress REST API | Publisher, Auditor | $0 | Publish, update posts, manage media |
| IndexNow API | Publisher | $0 | Fast indexing of new and updated URLs |
| DALL-E 3 API | Publisher | ~$1/mo | Featured image generation |
| RSS feeds | Scout | $0 | Breaking news monitoring |
| n8n (self-hosted) | Orchestration | $5-10/mo | Pipeline orchestration, cron, webhooks |
| Buffer | Publisher | $6/mo (optional) | LinkedIn + Twitter auto-posting |
| **Total** | | **$19-32/mo** | |

For full details on each integration, setup priority, and free alternatives, see `integration-map.md`.

---

## File Structure

```
/ai-blog-pipeline/
├── agents/
│   ├── scout/
│   │   └── SKILL-scout-agent-v2.md
│   ├── analyst/
│   │   └── SKILL-analyst-agent-v2.md
│   ├── writer/
│   │   ├── SKILL-writer-agent-v3.md
│   │   ├── SKILL-humanizer-combined.md      # Reference for anti-AI rules
│   │   └── style-samples/                   # 2-3 example blog posts
│   ├── editor/
│   │   └── SKILL-editor-agent-v3.md
│   ├── publisher/
│   │   └── SKILL-publisher-agent-v2.md
│   └── auditor/
│       └── SKILL-auditor-agent-v1.md
│
├── config/
│   ├── article-plan.json                    # The Scout's article backlog
│   ├── integration-map.md                   # Full integration reference
│   └── rss-feeds.json                       # Feed URLs for news monitoring
│
├── workspace/                                # Pipeline handoff files
│   ├── topics.json
│   ├── brief.json
│   ├── draft.json
│   ├── final.json                           # or rejection.json
│   └── publish-log.json
│
├── data/
│   ├── published-posts-index.json           # All published articles with slugs, keywords, dates
│   ├── dedup-index.json                     # Previously published topics
│   └── audit-reports/
│       └── audit-report-2026-05.json
│
├── orchestrator/
│   └── (n8n workflows or custom pipeline scripts)
│
└── reference/
    └── rewritten-llm-pricing-post.md        # Example of target output quality
```

---

## Error Handling

```
Agent fails           → retry 2x with exponential backoff
3 consecutive fails   → write to errors.json, alert via email/Slack
Editor rejects draft  → Writer regenerates with rejection guidance (max 2 retries)
3 Editor rejections   → pipeline pauses, flag for human review
Scout finds 0 topics  → output no_action, wait for next cycle
Auditor finds issues  → priority actions queued for Scout's next run
```

---

## Summary

| Agent | Version | Responsibility | Key Output |
|-------|---------|---------------|------------|
| Scout | v2 | Find best topic (news or planned) | topics.json |
| Analyst | v2 | Research + brief + link map + keywords | brief.json |
| Writer | v3 | Write human-sounding, SEO-structured draft | draft.json |
| Editor | v3 | 4-pass QA: humanise + fact-check + SEO systems + on-page | final.json or rejection |
| Publisher | v2 | Deploy + schema + backlink cluster + IndexNow + social | WordPress post + updates |
| Auditor | v1 | Monthly health: rankings + cannibalisation + freshness | audit-report.json |
| Humanizer | v1 | Reference skill: 30 AI patterns + word table + voice rules | (used by Writer + Editor) |
