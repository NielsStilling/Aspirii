# Blog Pipeline — Required Integrations & Cost Map

Every external service needed to run the full 6-agent pipeline, mapped to which agent uses it, what it costs, and whether a free alternative exists.

---

## 1. Keyword Research API

**What it does:** Validates target keywords with real search volume data, keyword difficulty scores, and related keyword suggestions. Without this, the Scout and Analyst are guessing at keywords.

**Which agents use it:** Scout (keyword validation when selecting topics), Analyst (refining target keywords for the brief, finding "People Also Ask" questions for FAQ sections)

### Recommended: DataForSEO

- **Why:** Pay-as-you-go, no $500/month subscription requirement. Has a dedicated Keyword Research API (Google Ads data), SERP API, and "People Also Ask" extraction. Integrates easily with n8n via HTTP request nodes.
- **Cost:** $50 minimum deposit, then pay-per-query. Standard queue: $0.0006/query (~$0.60 per 1,000 lookups). For 200 keyword lookups per week that's roughly $5/month.
- **Setup:** Create account at dataforseo.com, fund with $50, get API credentials. REST API with JSON responses.

### Alternative: SEMrush API

- **Why:** More comprehensive data, bigger keyword database, competitive analysis included.
- **Cost:** Requires Business plan at $499.95/month to get API access, plus separate API credit purchases. Massive overkill for a single blog.
- **Verdict:** Only worth it if you're already paying for SEMrush for other reasons.

### Free alternative: Google Search Console API + Google Trends (pytrends)

- **Google Search Console:** Free. Shows which keywords your site already ranks for, impressions, clicks, and position data. Excellent for the Auditor agent's monthly review. Doesn't help with discovering NEW keywords you don't rank for yet.
- **Google Trends (pytrends):** Free. Shows relative interest over time and trending topics. Good for the Scout's breaking news detection. Doesn't give absolute search volume numbers.
- **Verdict:** Good enough for the Auditor and for trend detection. Not sufficient for keyword validation — you still need volume and difficulty data from DataForSEO or similar for the Scout and Analyst.

---

## 2. Google Search Console API

**What it does:** Provides your site's actual search performance data — which queries you rank for, positions, impressions, clicks, CTR. Essential for the Auditor's monthly health checks.

**Which agents use it:** Auditor (ranking performance, keyword cannibalisation detection, declining content identification), Scout (checking which keywords you already rank for before suggesting new topics)

### Setup: Free

- **Cost:** $0. Google Search Console is free for any website you verify ownership of.
- **Setup:** Verify your site in Google Search Console (DNS or HTML tag method). Enable the Search Console API in Google Cloud Console. Create a service account with read access. The API returns query-level data: keyword, impressions, clicks, CTR, position, date range.
- **Rate limits:** 200 requests per minute, 20,000 rows per request. More than enough for a single blog.

### What you get:

- Queries your site appears for (with position and click data)
- Page-level performance (which URL ranks for which queries)
- Cannibalisation detection (multiple URLs appearing for the same query)
- Historical trends (compare month-over-month)

---

## 3. Google Analytics 4 API (or alternative)

**What it does:** Provides traffic data, bounce rate, time on page, session duration, and user behaviour metrics. The Auditor needs this to identify underperforming content and pages with high bounce rates.

**Which agents use it:** Auditor (traffic analysis, bounce rate checking, engagement metrics, zero-traffic article detection)

### Setup: Free

- **Cost:** $0. GA4 is free.
- **Setup:** Install GA4 tracking on your WordPress site (via plugin or manual tag). Enable the GA4 Data API in Google Cloud Console. Use the same service account as Search Console.

### Free alternative: Plausible Analytics or Umami

- Both are privacy-friendly, lighter weight, and have APIs. Plausible is $9/month hosted, free if self-hosted. Umami is free and self-hosted. Either works if you prefer not to use Google.

---

## 4. LLM API (for all agents)

**What it does:** Powers every agent's reasoning — topic selection, research, writing, editing, auditing. This is the core cost of the pipeline.

**Which agents use it:** All 6 agents.

### Recommended: Anthropic Claude API (Sonnet 4.6)

- **Cost:** $3/$15 per MTok (input/output). A typical blog post pipeline run (Scout + Analyst + Writer + Editor) processes roughly 30-50K tokens total across all agents. At Sonnet pricing, that's roughly $0.50-1.00 per published article.
- **Monthly estimate at 4 articles/week:** $8-16/month.
- **Setup:** Create API key at console.anthropic.com. 

### Alternative: OpenAI GPT-4.1

- **Cost:** $2/$8 per MTok. Slightly cheaper per article, roughly $0.30-0.70 per pipeline run.
- **Tradeoff:** Less strong on the writing quality side compared to Claude for blog content.

### Budget alternative: Gemini 2.5 Flash

- **Cost:** $0.30/$2.50 per MTok. Roughly $0.05-0.15 per pipeline run. Extremely cheap.
- **Tradeoff:** Lower quality writing. Would need more aggressive editing passes.
- **Verdict:** Could use Gemini for the Scout and Analyst (research tasks) and Claude for the Writer and Editor (quality-critical tasks) to reduce costs.

---

## 5. WordPress REST API

**What it does:** Publishes posts, updates existing posts, manages categories/tags, uploads media. The Publisher agent's primary integration.

**Which agents use it:** Publisher (publish new posts, update existing posts with backlinks, upload featured images, apply categories/tags), Auditor (reading published post index)

### Setup: Free (built into WordPress)

- **Cost:** $0. The REST API is built into every WordPress installation.
- **Setup:** Enable JWT authentication or Application Passwords for API access. Install the "Application Passwords" feature (built into WP 5.6+) or use a JWT plugin. Your Simply.com hosted WordPress already supports this.

### What you need to configure:

- Create an Application Password for the API user (Settings → Users → your user → Application Passwords)
- Ensure the REST API is not blocked by security plugins
- Map your WordPress category and tag IDs so the Publisher can assign them correctly

---

## 6. IndexNow API

**What it does:** Instantly notifies search engines (Bing, Yandex, and others that support it) when you publish or update content. Dramatically speeds up indexing compared to waiting for natural crawl.

**Which agents use it:** Publisher (submit new and updated URLs after every publish)

### Setup: Free

- **Cost:** $0. IndexNow is a free protocol.
- **Setup:** Generate an API key, host a key file at your site root (yoursite.com/{key}.txt), then POST new URLs to api.indexnow.org. Takes 5 minutes to set up.
- **Note:** Google doesn't officially support IndexNow but does accept submissions via Search Console API's URL inspection tool. For Google, the Sitemap + Search Console combination handles indexing.

---

## 7. Image Generation API

**What it does:** Generates featured images / blog thumbnails for each post.

**Which agents use it:** Publisher (generates featured image from the prompt in the frontmatter)

### Recommended: OpenAI DALL-E 3 API

- **Cost:** $0.040 per image (1024x1024). At 4 articles/week, that's about $0.64/month. Negligible.
- **Setup:** Use the same OpenAI API key. Send the image prompt from the frontmatter, download the result, upload to WordPress media library.

### Free alternative: Canva API or manual Canva templates

- You already use Canva for thumbnails. You could skip the API entirely and create a batch of templates with your dark background / teal accent style, then manually assign them. Less automated but $0.
- **Verdict:** At $0.64/month, DALL-E is worth automating. But Canva is fine if you want manual control over brand consistency.

---

## 8. RSS Feed Parsing

**What it does:** Monitors competitor blogs, official AI company blogs, and news sources for breaking news detection.

**Which agents use it:** Scout (breaking news monitoring, competitor coverage checking)

### Setup: Free

- **Cost:** $0. RSS is an open protocol.
- **Setup:** Use an RSS parser library (feedparser in Python, or n8n's built-in RSS trigger node). Configure feeds for: OpenAI blog, Anthropic blog, Google AI blog, Meta AI blog, Mistral blog, Hacker News front page (RSS feed available), ArXiv cs.AI/cs.LG new submissions.
- **n8n integration:** n8n has a native RSS Feed Trigger node that checks feeds on a schedule and fires when new items appear. This is the simplest way to implement the Scout's news monitoring.

---

## 9. Orchestration Platform

**What it does:** Connects all agents together. Runs the cron schedules, handles the webhook triggers between agents, manages the data handoffs (topics.json → brief.json → draft.json → etc).

**Which agents use it:** All (this is the glue)

### Recommended: n8n (self-hosted)

- **Cost:** $0 if self-hosted. Their cloud plans start at $24/month if you don't want to manage infrastructure.
- **Why:** Visual workflow builder, native nodes for HTTP requests, RSS, cron, webhooks, WordPress, and file operations. You can build the entire Scout → Analyst → Writer → Editor → Publisher pipeline as a visual workflow. Self-hostable on a cheap VPS.
- **Setup:** Docker install on a VPS ($5-10/month for a small Hetzner or DigitalOcean instance) or use n8n cloud.

### Alternative: Make.com (formerly Integromat)

- **Cost:** Free tier has 1,000 operations/month. Pro plan at $10.59/month for 10,000 operations. A full pipeline run uses roughly 15-25 operations, so 4 articles/week = 60-100 operations/week = 240-400/month. Free tier might work, but it's tight.
- **Tradeoff:** Easier to set up than self-hosted n8n, but less flexible and you're dependent on their cloud.

---

## 10. Social Media APIs (optional)

**What it does:** Auto-posts LinkedIn teasers and tweets when articles publish.

**Which agents use it:** Publisher (posting social media teasers)

### LinkedIn API

- **Cost:** Free to use, but LinkedIn's API requires an approved app with specific permissions. The Share API lets you post on behalf of a user. Setup is bureaucratic — you need to apply for API access and get approved.
- **Alternative:** Use n8n's LinkedIn node or a tool like Buffer ($6/month) for scheduling. Buffer is simpler and doesn't require API approval.

### Twitter/X API

- **Cost:** Basic tier is $200/month (yes, really). Free tier only allows reading, not posting.
- **Alternative:** Buffer ($6/month) handles Twitter posting too. Or skip Twitter entirely — for a B2B AI blog, LinkedIn is where your audience lives.

---

## Cost Summary

### Minimum viable setup (all agents functional):

| Integration | Monthly cost | Notes |
|------------|-------------|-------|
| DataForSEO | ~$5/month (from $50 deposit) | Keyword validation. Can delay this and use free alternatives initially |
| Google Search Console | $0 | Essential for Auditor |
| Google Analytics 4 | $0 | Essential for Auditor |
| Claude API (Sonnet 4.6) | $8-16/month | Core LLM for all agents |
| WordPress REST API | $0 | Built-in |
| IndexNow | $0 | Free protocol |
| DALL-E 3 (images) | ~$1/month | Featured images |
| RSS feeds | $0 | News monitoring |
| n8n (self-hosted) | $5-10/month (VPS) | Orchestration |
| **Total** | **$19-32/month** | |

### With social media automation:

| Add-on | Monthly cost |
|--------|-------------|
| Buffer (LinkedIn + Twitter) | $6/month |
| **Total with social** | **$25-38/month** |

### If you skip DataForSEO initially:

Use Google Search Console + Google Trends + manual keyword research. Saves $5/month but means keywords are less data-driven. Add DataForSEO once the blog has 10+ published articles and you want to optimise based on real search data.

### If you want premium keyword data:

SEMrush Business at $499.95/month is the gold standard but complete overkill for a single blog. Only consider this if you're running SEO for multiple client sites.

---

## Setup Priority Order

1. **WordPress REST API** — configure Application Passwords (30 minutes)
2. **Google Search Console** — verify site, enable API (1 hour)
3. **Google Analytics 4** — install tracking, enable API (1 hour)
4. **Claude API** — create key at console.anthropic.com (10 minutes)
5. **n8n** — install on VPS or sign up for cloud (1-2 hours)
6. **RSS feeds** — configure feed URLs in n8n (30 minutes)
7. **IndexNow** — generate key, host file, test submission (15 minutes)
8. **DALL-E 3** — create OpenAI API key (10 minutes)
9. **DataForSEO** — create account, fund $50, test keyword endpoint (1 hour)
10. **Buffer** — connect LinkedIn account (15 minutes)

Total setup time: roughly one afternoon for the full stack.
