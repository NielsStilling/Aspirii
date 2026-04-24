#!/usr/bin/env python3
"""Pre-flight audit for WordPress posts before publishing.

Runs editor-skill checks and strips broken internal links (that point to drafts
or non-existent slugs) so publishing a post never leaves 404s behind.

Usage:
    python3 orchestrator/preflight_audit.py <post_id>                # audit only
    python3 orchestrator/preflight_audit.py <post_id> --strip        # audit + strip + post
    python3 orchestrator/preflight_audit.py <post_id> --strip --dry  # audit + show strips, no post

Exit codes:
    0  all green (safe to publish)
    1  warnings (broken links or rule violations — review before publish)
    2  WordPress / network error
"""
import argparse
import base64
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# --- env loading ---
def load_env():
    env = {}
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print(f"error: {env_path} not found", file=sys.stderr)
        sys.exit(2)
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

def api(path, method='GET', data=None, retries=4):
    body = json.dumps(data).encode() if data else None
    url = f"{WP}/wp-json/wp/v2{path}"
    for i in range(retries + 1):
        try:
            r = urllib.request.Request(url, data=body, headers=H, method=method)
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if i == retries:
                print(f"error: WordPress API failed — {e}", file=sys.stderr)
                sys.exit(2)
            time.sleep(2 ** (i + 1))

# --- config ---
TIER1_BLACKLIST = set('''
additionally commence comprehensive crucial cutting-edge delve elevate embark
empower endeavor enhance ensure facilitate foster furthermore garner
groundbreaking harness hence holistic impactful innovative intricate leverage
meticulous moreover navigate nestled nonetheless notwithstanding optimize
paramount pivotal plethora profound realm robust seamless showcase spearhead
streamline subsequently synergy tapestry testament therefore thrive
transformative underscore utilize vibrant vital whereas whilst
'''.split())

PILLAR_SLUGS = {
    'ai-tools': 'best-ai-tools-2026',
    'ai-models': 'the-5-best-ai-models-in-2026-and-when-to-use-each-one',
    'claude': 'claude-ai-2026-complete-guide',
}

# --- slug resolver ---
_slug_cache = {}

def resolve_slug_status(slug):
    """Return the post status for a given slug, or 'unknown' if no match.

    Status values: publish, draft, private, future, pending, unknown.
    Results are cached within the script's run.
    """
    if slug in _slug_cache:
        return _slug_cache[slug]
    for status in ('publish', 'draft,private,future,pending'):
        r = api(f'/posts?slug={slug}&status={status}&_fields=id,slug,status&per_page=5')
        if r:
            s = r[0]['status']
            _slug_cache[slug] = s
            return s
    _slug_cache[slug] = 'unknown'
    return 'unknown'

# --- audits ---
def extract_internal_links(content):
    """Return a list of (url, slug, anchor_text, full_tag) for every internal link.

    Internal = starts with '/' or points to the aspirii.com domain. Category,
    tag, and author archive links are skipped (they always exist).
    """
    site_host = re.sub(r'^https?://', '', WP).rstrip('/')
    links = []
    for m in re.finditer(r'<a\s+[^>]*href="([^"]+)"[^>]*>([^<]*)</a>', content, re.I):
        url, anchor = m.group(1), m.group(2)
        full_tag = m.group(0)
        # Normalise
        if url.startswith(f'https://{site_host}') or url.startswith(f'http://{site_host}'):
            url = url.split(site_host, 1)[1]
        elif url.startswith('http'):
            continue  # external
        elif not url.startswith('/'):
            continue
        # Skip taxonomy / archive URLs
        if url.startswith(('/category/', '/tag/', '/author/', '/page/')) or url.rstrip('/') == '':
            continue
        # Extract slug (strip leading slash, trailing slash, query, fragment)
        slug = url.lstrip('/').split('?')[0].split('#')[0].rstrip('/')
        if '/' in slug:
            continue  # nested path, skip
        links.append((url, slug, anchor, full_tag))
    return links

def plain_text_and_words(content):
    """Return (plain text, word list) with scripts stripped and entities collapsed."""
    clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', clean)
    text = re.sub(r'&[a-z]+;|&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text, text.split()

def first_link_position_pct(content):
    """Return the word-position percentage of the first internal link, or None."""
    clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    marked = re.sub(r'<a\s+[^>]*href="([^"]+)"[^>]*>', r'§§LINK§§\1§§LINK§§', clean, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', marked)
    text = re.sub(r'&[a-z]+;|&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    for i, w in enumerate(words):
        if '§§LINK§§' in w:
            return (i / len(words) * 100) if words else None
    return None

def tier1_blacklist_hits(text):
    low = text.lower()
    hits = []
    for w in TIER1_BLACKLIST:
        n = len(re.findall(r'\b' + re.escape(w) + r'\b', low))
        if n:
            hits.append((w, n))
    return hits

# --- reporting ---
GREEN = '\033[32m'; RED = '\033[31m'; YELLOW = '\033[33m'; RESET = '\033[0m'; BOLD = '\033[1m'

def ok(msg): print(f"  {GREEN}✓{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}⚠{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('post_id', type=int, help='WordPress post ID')
    ap.add_argument('--strip', action='store_true', help='Strip broken internal links and post back')
    ap.add_argument('--dry', action='store_true', help='Show what --strip would change without posting')
    args = ap.parse_args()

    post = api(f"/posts/{args.post_id}?context=edit")
    title = post['title']['rendered']
    slug = post['slug']
    status = post['status']
    content = post['content']['raw']
    orig_content = content
    text, words = plain_text_and_words(content)

    print(f"{BOLD}=== Pre-flight audit: post {args.post_id} ==={RESET}")
    print(f"  Title:  {title}")
    print(f"  Slug:   {slug}")
    print(f"  Status: {status}")
    print(f"  Words:  {len(words)}")
    print()

    # --- Link integrity ---
    print(f"{BOLD}--- Link integrity ---{RESET}")
    links = extract_internal_links(content)
    broken = []
    if not links:
        warn("No internal links found")
    else:
        for url, link_slug, anchor, tag in links:
            s = resolve_slug_status(link_slug)
            if s == 'publish':
                ok(f"{url}  ({s})")
            elif s == 'unknown':
                fail(f"{url}  (slug not found — will 404)")
                broken.append((url, link_slug, anchor, tag))
            else:
                fail(f"{url}  ({s} — will 404)")
                broken.append((url, link_slug, anchor, tag))

    # --- Editor skill checks ---
    print()
    print(f"{BOLD}--- Editor skill checks ---{RESET}")
    issues = 0

    # Word count (800-2000 target)
    if 800 <= len(words) <= 2000:
        ok(f"Word count: {len(words)} (target 800-2000)")
    elif len(words) < 800:
        warn(f"Word count: {len(words)} (below 800 — may be too thin)"); issues += 1
    else:
        warn(f"Word count: {len(words)} (above 2000 — editor rule: tighten to ≤95%)"); issues += 1

    # First link position
    pct = first_link_position_pct(content)
    if pct is None:
        warn("No internal links at all"); issues += 1
    elif pct <= 30:
        ok(f"First internal link at {pct:.1f}% (rule: top 30%)")
    else:
        fail(f"First internal link at {pct:.1f}% (exceeds top 30% rule)"); issues += 1

    # Pillar link presence
    internal_slugs = {link_slug for _, link_slug, _, _ in links}
    pillars_linked = [name for name, pillar_slug in PILLAR_SLUGS.items() if pillar_slug in internal_slugs]
    if pillars_linked:
        ok(f"Pillar link(s) present: {', '.join(pillars_linked)}")
    else:
        warn(f"No pillar link found (expected one of: {', '.join(PILLAR_SLUGS.values())})"); issues += 1

    # Yoast focus keyword + metadesc
    focus = (post.get('_yoast_wpseo_focuskw') or '').strip()
    metadesc = (post.get('_yoast_wpseo_metadesc') or '').strip()
    if focus:
        ok(f"Yoast focus keyword: {focus!r}")
    else:
        warn("Yoast focus keyword not set"); issues += 1
    if metadesc:
        if len(metadesc) <= 155:
            ok(f"Yoast meta description set ({len(metadesc)} chars)")
        else:
            warn(f"Yoast meta description too long ({len(metadesc)} chars, max 155)"); issues += 1
    else:
        warn("Yoast meta description not set"); issues += 1

    # Tier 1 blacklist
    hits = tier1_blacklist_hits(text)
    if not hits:
        ok("No Tier 1 blacklist words")
    else:
        fail(f"Tier 1 blacklist hits: {sum(n for _, n in hits)}  ({', '.join(f'{w}×{n}' for w, n in hits)})")
        issues += 1

    # --- Summary ---
    print()
    print(f"{BOLD}--- Summary ---{RESET}")
    print(f"  Broken internal links: {len(broken)}")
    print(f"  Editor skill warnings: {issues}")

    # --- Optional strip ---
    if args.strip and broken:
        print()
        print(f"{BOLD}--- Stripping broken links ---{RESET}")
        for url, link_slug, anchor, tag in broken:
            if tag in content:
                content = content.replace(tag, anchor, 1)
                print(f"  stripped: {url}  →  plain text {anchor!r}")
            else:
                warn(f"  tag not found to strip: {url}")
        if content != orig_content:
            if args.dry:
                print(f"\n[dry run] would POST update (content {len(orig_content)} → {len(content)} chars, {len(content)-len(orig_content):+d})")
            else:
                api(f"/posts/{args.post_id}", method='POST', data={'content': content})
                print(f"\n  POST update applied. Content {len(orig_content)} → {len(content)} chars.")

    exit_code = 0
    if broken or issues:
        exit_code = 1
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
