#!/usr/bin/env python3
"""Fact-check audit for WordPress drafts before publishing.

Surfaces what needs verification: stale model names, pricing references,
specific dates, and sibling articles published since the draft was created.
Then suggests WebSearches to run. Does NOT auto-update — fact-checking is
qualitative, the operator (Claude) verifies and applies fixes.

Usage:
    python3 orchestrator/factcheck_audit.py <post_id>

Exit codes: 0 always (informational). Use for guidance, not gating.
"""
import argparse
import base64
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

def load_env():
    env = {}
    env_path = Path(__file__).parent.parent / '.env'
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"')
    return env

ENV = load_env()
WP = ENV['WORDPRESS_URL']
AUTH = base64.b64encode(f"{ENV['WORDPRESS_USERNAME']}:{ENV['WORDPRESS_APP_PASSWORD']}".encode()).decode()
H = {'Authorization': f'Basic {AUTH}', 'Content-Type': 'application/json'}

def api(path, retries=4):
    url = f"{WP}/wp-json/wp/v2{path}"
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=H)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if i == retries:
                print(f"error: WordPress API failed — {e}", file=sys.stderr)
                sys.exit(2)
            time.sleep(2 ** (i + 1))

GREEN = '\033[32m'; RED = '\033[31m'; YELLOW = '\033[33m'; CYAN = '\033[36m'; BOLD = '\033[1m'; RESET = '\033[0m'

# --- patterns we know go stale fast in AI content ---
STALE_MODEL_PATTERNS = [
    # OpenAI: any pre-GPT-5 reference is suspect now
    (r'\bGPT-4o\b', 'GPT-4o (OpenAI flagship is GPT-5+ since Aug 2025)'),
    (r'\bGPT-4(?!\.)\b', 'GPT-4 (consider GPT-5)'),
    (r'\bGPT-4 Turbo\b', 'GPT-4 Turbo (deprecated)'),
    (r'\bGPT-3\.5\b', 'GPT-3.5 (legacy)'),
    (r'\bo1\b(?!-)', 'o1 (consider GPT-5 reasoning)'),
    (r'\bo3\b', 'o3 / GPT-o3 (consider GPT-5 Pro)'),
    (r'\bDALL[-·]?E 3\b', 'DALL-E 3 (consider GPT-Image or current image model)'),
    # Claude: any pre-Sonnet 4.x is now stale in 2026
    (r'\bClaude 3\.5\b', 'Claude 3.5 (current: Sonnet 4.6 / Opus 4.7)'),
    (r'\bClaude 3 (Opus|Sonnet|Haiku)\b', 'Claude 3 family (legacy)'),
    (r'\bOpus 4\.6\b', 'Opus 4.6 (current: Opus 4.7 since April 2026)'),
    (r'\bSonnet 4\.5\b', 'Sonnet 4.5 (current: Sonnet 4.6)'),
    # Google
    (r'\bGemini 1\.[05]\b', 'Gemini 1.x (consider Gemini 2+ / 3 beta)'),
    (r'\bGemini Pro\b(?! \d)', 'Generic "Gemini Pro" (specify version)'),
    # Specific tools that change names
    (r'\bCodeium\b(?! \(?Windsurf)', 'Codeium (rebranded to Windsurf)'),
    (r'\bBard\b', 'Bard (rebranded to Gemini)'),
]

# Relative time references that get stale fast
RELATIVE_TIME_PATTERNS = [
    (r'\b(?:last|past)\s+(?:month|quarter|year)\b', 'relative time ("last month/year")'),
    (r'\b(?:recently|just released|currently|right now|today)\b', 'time-bound phrase'),
    (r'\bin (?:early|mid|late) 20\d\d\b', 'specific period reference'),
]

# Currency / pricing — often changes
PRICING_PATTERN = r'\$\d+(?:\.\d+)?(?:/(?:month|mo|user|user/month|second|sec|token|hour|year))?'

def analyze(content):
    """Return dict of fact-check findings."""
    # Strip HTML for analysis
    text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;|&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    findings = {
        'stale_models': [],
        'relative_time': [],
        'prices': [],
        'dates': [],
    }

    # Stale model name detection
    for pattern, label in STALE_MODEL_PATTERNS:
        for m in re.finditer(pattern, text):
            ctx_start = max(0, m.start() - 40)
            ctx_end = min(len(text), m.end() + 40)
            findings['stale_models'].append({
                'match': m.group(0),
                'label': label,
                'context': text[ctx_start:ctx_end].strip(),
            })

    # Relative time references
    for pattern, label in RELATIVE_TIME_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            findings['relative_time'].append({
                'match': m.group(0),
                'label': label,
            })

    # Pricing
    for m in re.finditer(PRICING_PATTERN, text):
        ctx_start = max(0, m.start() - 30)
        ctx_end = min(len(text), m.end() + 30)
        findings['prices'].append({
            'match': m.group(0),
            'context': text[ctx_start:ctx_end].strip(),
        })

    # Specific calendar references (years, full dates)
    for m in re.finditer(r'\b(20\d\d)\b', text):
        year = int(m.group(1))
        if year < datetime.now().year:
            findings['dates'].append({'year': year, 'match': m.group(0)})

    return findings, text

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('post_id', type=int, help='WordPress post ID')
    args = ap.parse_args()

    post = api(f"/posts/{args.post_id}?context=edit")
    title = re.sub(r'&[a-z#0-9]+;', '', post['title']['rendered'])
    slug = post['slug']
    status = post['status']
    focus_kw = (post.get('_yoast_wpseo_focuskw') or '').strip() or '(not set)'
    created = datetime.fromisoformat(post['date'].rstrip('Z'))
    modified = datetime.fromisoformat(post['modified'].rstrip('Z'))
    now = datetime.now()
    days_since_modified = (now - modified).days

    print(f"{BOLD}=== Fact-check audit: post {args.post_id} ==={RESET}")
    print(f"  Title:        {title}")
    print(f"  Slug:         {slug}")
    print(f"  Status:       {status}")
    print(f"  Focus kw:     {focus_kw}")
    print(f"  Created:      {created.strftime('%Y-%m-%d')}")
    print(f"  Last modified: {modified.strftime('%Y-%m-%d')} ({days_since_modified} days ago)")

    findings, text = analyze(post['content']['raw'])

    # Stale model names
    print(f"\n{BOLD}--- Stale model / product references ---{RESET}")
    if findings['stale_models']:
        # Dedupe by match string
        seen = set()
        for f in findings['stale_models']:
            if f['match'] in seen:
                continue
            seen.add(f['match'])
            print(f"  {RED}✗{RESET} {f['match']:<22}  {YELLOW}{f['label']}{RESET}")
            print(f"      …{f['context']}…")
    else:
        print(f"  {GREEN}✓{RESET} No known-stale model/product names detected.")

    # Relative time
    print(f"\n{BOLD}--- Relative time references ({len(findings['relative_time'])}) ---{RESET}")
    if findings['relative_time']:
        seen = set()
        for f in findings['relative_time']:
            key = f['match'].lower()
            if key in seen:
                continue
            seen.add(key)
            print(f"  {YELLOW}⚠{RESET} {f['match']:<25}  {f['label']}")
        print(f"  {CYAN}note:{RESET} review for accuracy given draft age ({days_since_modified} days)")
    else:
        print(f"  {GREEN}✓{RESET} No relative time phrases detected.")

    # Pricing
    unique_prices = sorted(set(f['match'] for f in findings['prices']))
    print(f"\n{BOLD}--- Pricing references ({len(unique_prices)} unique) ---{RESET}")
    if unique_prices:
        for p in unique_prices[:15]:
            print(f"  {CYAN}${RESET} {p}")
        if len(unique_prices) > 15:
            print(f"  …and {len(unique_prices)-15} more")
        print(f"  {CYAN}note:{RESET} verify each is current on the vendor's pricing page")
    else:
        print(f"  No specific price references found.")

    # Sibling articles published since draft was created
    print(f"\n{BOLD}--- Sibling publishes since this draft was created ---{RESET}")
    all_posts = api(f"/posts?status=publish&per_page=100&_fields=id,slug,title,date")
    siblings = []
    for p in all_posts:
        pdate = datetime.fromisoformat(p['date'].rstrip('Z'))
        if pdate > created and p['id'] != args.post_id:
            siblings.append((p['id'], p['slug'], pdate))
    if siblings:
        siblings.sort(key=lambda x: x[2])
        for pid, pslug, pdate in siblings:
            in_content = pslug in post['content']['raw']
            mark = f"{GREEN}linked{RESET}" if in_content else f"{YELLOW}not linked{RESET}"
            print(f"  {pdate.strftime('%Y-%m-%d')} → id:{pid:<4} /{pslug:<40} [{mark}]")
        print(f"  {CYAN}note:{RESET} 'not linked' siblings might be relevant link additions")
    else:
        print(f"  No new articles published since this draft was created.")

    # Suggested WebSearches
    print(f"\n{BOLD}--- Suggested WebSearches before publish ---{RESET}")
    primary = focus_kw if focus_kw != '(not set)' else title.split(':')[0].split(' in ')[0]
    print(f"  1. \"{primary} news {datetime.now().strftime('%B %Y')}\" — recent announcements")
    print(f"  2. \"{primary} pricing\" — confirm prices match current vendor info")
    print(f"  3. \"{primary} vs\" — what new competitors or comparisons emerged")
    if days_since_modified > 14:
        print(f"  4. \"{primary} latest update\" — anything major in the {days_since_modified}-day gap")

    # Operator checklist
    print(f"\n{BOLD}--- Pre-publish checklist ---{RESET}")
    print(f"  [ ] Verified focus keyword is still relevant in {datetime.now().strftime('%B %Y')}")
    print(f"  [ ] Ran the suggested WebSearches and reviewed top 5 results for each")
    print(f"  [ ] All stale model / product names corrected")
    print(f"  [ ] Pricing checked against vendor's current public pages")
    print(f"  [ ] No major news in the topic that should be referenced")
    print(f"  [ ] Considered linking newly-published sibling articles where relevant")
    print(f"  [ ] Relative time phrases ('last month', 'recently') still accurate given draft age")

    print()

if __name__ == '__main__':
    main()
