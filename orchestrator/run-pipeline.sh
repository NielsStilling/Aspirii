#!/usr/bin/env bash
# =============================================================================
# AI Blog Pipeline Orchestrator
# Runs the full Scout → Analyst → Writer → Editor → Publisher pipeline
# Usage:
#   ./orchestrator/run-pipeline.sh              # Full pipeline
#   ./orchestrator/run-pipeline.sh scout        # Single agent
#   ./orchestrator/run-pipeline.sh auditor      # Monthly audit
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Directories
AGENTS_DIR="$PROJECT_ROOT/agents"
CONFIG_DIR="$PROJECT_ROOT/config"
WORKSPACE_DIR="$PROJECT_ROOT/workspace"
DATA_DIR="$PROJECT_ROOT/data"

# Pipeline files
TOPICS_FILE="$WORKSPACE_DIR/topics.json"
BRIEF_FILE="$WORKSPACE_DIR/brief.json"
DRAFT_FILE="$WORKSPACE_DIR/draft.json"
FINAL_FILE="$WORKSPACE_DIR/final.json"
REJECTION_FILE="$WORKSPACE_DIR/rejection.json"
PUBLISH_LOG="$WORKSPACE_DIR/publish-log.json"
ERRORS_FILE="$PROJECT_ROOT/errors.json"

# Config
MAX_WRITER_RETRIES=2
MAX_AGENT_RETRIES=2
RETRY_BACKOFF_BASE=5  # seconds

# Load environment
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# =============================================================================
# Logging
# =============================================================================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1"
}

# =============================================================================
# Error handling
# =============================================================================
record_error() {
    local agent="$1"
    local message="$2"
    local timestamp
    timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

    if [[ ! -f "$ERRORS_FILE" ]]; then
        echo '{"errors": []}' > "$ERRORS_FILE"
    fi

    # Append error using a temp file (portable JSON append)
    local tmp
    tmp=$(mktemp)
    python3 -c "
import json, sys
with open('$ERRORS_FILE') as f:
    data = json.load(f)
data['errors'].append({
    'timestamp': '$timestamp',
    'agent': '$agent',
    'message': '''$message'''
})
with open('$tmp', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null && mv "$tmp" "$ERRORS_FILE" || rm -f "$tmp"
}

# =============================================================================
# Run a single agent with retries
# =============================================================================
run_agent() {
    local agent_name="$1"
    local skill_file="$2"
    local prompt="$3"
    local retries=0

    while [[ $retries -le $MAX_AGENT_RETRIES ]]; do
        log "Running $agent_name (attempt $((retries + 1))/$((MAX_AGENT_RETRIES + 1)))..."

        if claude -p "$prompt" \
            --system-prompt "$(cat "$skill_file")" \
            --output-format json \
            --max-turns 25 \
            2>"$WORKSPACE_DIR/${agent_name}-stderr.log"; then
            log_success "$agent_name completed."
            return 0
        fi

        retries=$((retries + 1))
        if [[ $retries -le $MAX_AGENT_RETRIES ]]; then
            local backoff=$((RETRY_BACKOFF_BASE * retries))
            log "  $agent_name failed. Retrying in ${backoff}s..."
            sleep "$backoff"
        fi
    done

    log_error "$agent_name failed after $((MAX_AGENT_RETRIES + 1)) attempts."
    record_error "$agent_name" "Failed after $((MAX_AGENT_RETRIES + 1)) attempts"
    return 1
}

# =============================================================================
# Agent runners
# =============================================================================

run_scout() {
    log "=== SCOUT: Finding today's topic ==="

    local skill="$AGENTS_DIR/scout/SKILL-scout-agent-v2.md"
    local prompt="You are the Scout agent. Find the single most valuable article to publish next.

INPUTS:
- Article plan: $(cat "$CONFIG_DIR/article-plan.json")
- RSS feeds config: $(cat "$CONFIG_DIR/rss-feeds.json")
- Dedup index: $(cat "$DATA_DIR/dedup-index.json")
- Published posts: $(cat "$DATA_DIR/published-posts-index.json")

$(if [[ -f "$DATA_DIR/audit-reports/$(date '+%Y-%m' -d 'last month')-audit-report.json" ]]; then
    echo "- Latest audit report: $(cat "$DATA_DIR/audit-reports/$(date '+%Y-%m' -d 'last month')-audit-report.json")"
else
    echo "- No audit report available yet."
fi)

OUTPUT: Write your output as valid JSON to $TOPICS_FILE following the schema in workspace/schemas/topics-schema.json.
Output ONLY the JSON file. Do not output anything else."

    run_agent "scout" "$skill" "$prompt"
}

run_analyst() {
    log "=== ANALYST: Building research brief ==="

    if [[ ! -f "$TOPICS_FILE" ]]; then
        log_error "No topics.json found. Run scout first."
        return 1
    fi

    # Check for no_action
    local mode
    mode=$(python3 -c "import json; print(json.load(open('$TOPICS_FILE'))['mode'])" 2>/dev/null)
    if [[ "$mode" == "no_action" ]]; then
        log "Scout returned no_action. Skipping pipeline."
        return 0
    fi

    local skill="$AGENTS_DIR/analyst/SKILL-analyst-agent-v2.md"
    local prompt="You are the Analyst agent. Build a complete research brief for the Writer.

INPUTS:
- Scout's topic: $(cat "$TOPICS_FILE")
- Published posts index: $(cat "$DATA_DIR/published-posts-index.json")
- Article plan (for cluster context): $(cat "$CONFIG_DIR/article-plan.json")

TASK:
1. Read ALL source URLs from the Scout's topic.
2. Search the web for 3-5 additional sources to fill gaps.
3. Classify the search intent.
4. Map internal links (outbound + inbound).
5. Generate 2-3 experience seeds with specific numbers.
6. Build a section-by-section outline.
7. Extract FAQ questions from 'People Also Ask'.

OUTPUT: Write your output as valid JSON to $BRIEF_FILE following the schema in workspace/schemas/brief-schema.json.
Output ONLY the JSON file. Do not output anything else."

    run_agent "analyst" "$skill" "$prompt"
}

run_writer() {
    log "=== WRITER: Drafting blog post ==="

    if [[ ! -f "$BRIEF_FILE" ]]; then
        log_error "No brief.json found. Run analyst first."
        return 1
    fi

    local skill="$AGENTS_DIR/writer/SKILL-writer-agent-v3.md"
    local humanizer="$AGENTS_DIR/writer/SKILL-humanizer-combined.md"

    local rejection_context=""
    if [[ -f "$REJECTION_FILE" ]]; then
        rejection_context="

PREVIOUS REJECTION: The Editor rejected your last draft. Here is their feedback:
$(cat "$REJECTION_FILE")

Address ALL of the Editor's feedback in this revision."
    fi

    local prompt="You are the Writer agent. Write a complete blog post from the research brief.

INPUTS:
- Research brief: $(cat "$BRIEF_FILE")

REFERENCE (anti-AI rules — follow these strictly):
$(cat "$humanizer")
${rejection_context}

TASK:
1. Write the full blog post in markdown following the brief's outline.
2. Apply ALL humanizer rules — no AI-detectable patterns.
3. Embed experience seeds naturally (1 per 500 words minimum).
4. Include opinions (1 per 200 words minimum).
5. Use ALL outbound internal links from the brief.
6. Include FAQ section if brief provides faq_questions.
7. Vary sentence length, paragraph length, section structure.

OUTPUT: Write your output as valid JSON to $DRAFT_FILE following the schema in workspace/schemas/draft-schema.json.
Output ONLY the JSON file. Do not output anything else."

    run_agent "writer" "$skill" "$prompt"
}

run_editor() {
    log "=== EDITOR: Four-pass quality review ==="

    if [[ ! -f "$DRAFT_FILE" ]]; then
        log_error "No draft.json found. Run writer first."
        return 1
    fi

    # Clean up any previous rejection
    rm -f "$REJECTION_FILE"

    local skill="$AGENTS_DIR/editor/SKILL-editor-agent-v3.md"
    local prompt="You are the Editor agent. Run your four-pass review on the Writer's draft.

INPUTS:
- Writer's draft: $(cat "$DRAFT_FILE")
- Research brief (for fact-checking): $(cat "$BRIEF_FILE")
- Published posts index (for cannibalisation): $(cat "$DATA_DIR/published-posts-index.json")
- Article plan (for cluster verification): $(cat "$CONFIG_DIR/article-plan.json")

TASK — Four passes:
1. HUMANISATION AUDIT — structural patterns, sentence variance, opinion density, experience injections, blacklist phrases, summary blocks.
2. FACT-CHECK — every pricing figure, model name, version, date against brief sources.
3. SEO SYSTEMS CHECK — cluster fit, cannibalisation, internal link integrity, intent match.
4. ON-PAGE SEO — title/meta limits, keyword placement, FAQ, featured snippets, schema readiness.

DECISION:
- If the draft passes all checks (with minor edits): output to $FINAL_FILE as accepted JSON.
- If the draft fails critical checks: output to $REJECTION_FILE as rejected JSON with specific guidance.

Follow the schema in workspace/schemas/final-schema.json.
Output ONLY the JSON file. Do not output anything else."

    run_agent "editor" "$skill" "$prompt"
}

run_publisher() {
    log "=== PUBLISHER: Deploying to WordPress ==="

    if [[ ! -f "$FINAL_FILE" ]]; then
        log_error "No final.json found. Run editor first."
        return 1
    fi

    # Verify it was accepted
    local status
    status=$(python3 -c "import json; print(json.load(open('$FINAL_FILE'))['status'])" 2>/dev/null)
    if [[ "$status" != "accepted" ]]; then
        log_error "final.json status is not 'accepted'. Cannot publish."
        return 1
    fi

    local skill="$AGENTS_DIR/publisher/SKILL-publisher-agent-v2.md"
    local prompt="You are the Publisher agent. Deploy the accepted post to WordPress.

INPUTS:
- Accepted post: $(cat "$FINAL_FILE")
- WordPress URL: ${WORDPRESS_URL:-NOT_SET}
- WordPress Username: ${WORDPRESS_USERNAME:-NOT_SET}
- Article plan: $(cat "$CONFIG_DIR/article-plan.json")
- Published posts index: $(cat "$DATA_DIR/published-posts-index.json")

TASK:
1. Convert markdown to clean HTML.
2. Generate featured image via DALL-E 3 (prompt in frontmatter).
3. Publish to WordPress via REST API.
4. Apply schema markup (Article + FAQPage/HowTo as needed).
5. Execute post_publish_actions (backlink existing posts, update pillar).
6. Submit all modified URLs to IndexNow.
7. Generate social teasers (LinkedIn + Twitter).
8. Update article-plan.json with published status.
9. Update published-posts-index.json and dedup-index.json.

OUTPUT: Write your output as valid JSON to $PUBLISH_LOG following the schema in workspace/schemas/publish-log-schema.json.
Also update these data files:
- $DATA_DIR/published-posts-index.json
- $DATA_DIR/dedup-index.json
- $CONFIG_DIR/article-plan.json (mark article as published)

Output ONLY the JSON file. Do not output anything else."

    run_agent "publisher" "$skill" "$prompt"
}

run_auditor() {
    log "=== AUDITOR: Monthly SEO health check ==="

    local skill="$AGENTS_DIR/auditor/SKILL-auditor-agent-v1.md"
    local report_file="$DATA_DIR/audit-reports/audit-report-$(date '+%Y-%m').json"

    local prev_report=""
    local prev_file="$DATA_DIR/audit-reports/audit-report-$(date '+%Y-%m' -d 'last month').json"
    if [[ -f "$prev_file" ]]; then
        prev_report="- Previous audit report: $(cat "$prev_file")"
    fi

    local prompt="You are the Auditor agent. Run the monthly SEO health check.

INPUTS:
- Published posts index: $(cat "$DATA_DIR/published-posts-index.json")
- Article plan: $(cat "$CONFIG_DIR/article-plan.json")
${prev_report}

TASK — Six audits:
1. Cluster completeness (planned vs published)
2. Ranking performance (rising/stable/declining/page 2/zero traffic)
3. Keyword cannibalisation detection
4. Internal link health (orphans, broken, weak anchors)
5. Content freshness (stale pricing, deprecated models, old stats)
6. Cluster expansion signals

Note: If Google Search Console and GA4 credentials are not available, work with the published posts index and article plan to produce what analysis you can. Flag that GSC/GA4 data was unavailable.

OUTPUT: Write your output as valid JSON to $report_file following the schema in workspace/schemas/audit-report-schema.json.
Output ONLY the JSON file. Do not output anything else."

    run_agent "auditor" "$skill" "$prompt"
}

# =============================================================================
# Full pipeline with Editor rejection loop
# =============================================================================

run_full_pipeline() {
    log "=========================================="
    log "  AI Blog Pipeline — Full Run"
    log "=========================================="

    # Step 1: Scout
    run_scout || { log_error "Pipeline stopped at Scout."; return 1; }

    # Check if scout found anything
    local mode
    mode=$(python3 -c "import json; print(json.load(open('$TOPICS_FILE'))['mode'])" 2>/dev/null)
    if [[ "$mode" == "no_action" ]]; then
        log "Scout found no topic to publish. Pipeline complete (no action)."
        return 0
    fi

    # Step 2: Analyst
    run_analyst || { log_error "Pipeline stopped at Analyst."; return 1; }

    # Step 3 & 4: Writer → Editor loop (max retries)
    local writer_attempts=0
    while [[ $writer_attempts -lt $((MAX_WRITER_RETRIES + 1)) ]]; do
        writer_attempts=$((writer_attempts + 1))
        log "--- Writer/Editor cycle $writer_attempts/$((MAX_WRITER_RETRIES + 1)) ---"

        # Step 3: Writer
        run_writer || { log_error "Pipeline stopped at Writer."; return 1; }

        # Step 4: Editor
        run_editor || { log_error "Pipeline stopped at Editor."; return 1; }

        # Check Editor verdict
        if [[ -f "$FINAL_FILE" ]]; then
            local status
            status=$(python3 -c "import json; print(json.load(open('$FINAL_FILE'))['status'])" 2>/dev/null)
            if [[ "$status" == "accepted" ]]; then
                log_success "Editor accepted the draft!"
                break
            fi
        fi

        if [[ -f "$REJECTION_FILE" ]]; then
            if [[ $writer_attempts -lt $((MAX_WRITER_RETRIES + 1)) ]]; then
                log "Editor rejected draft. Sending back to Writer with feedback..."
            else
                log_error "Editor rejected draft $writer_attempts times. Pipeline paused for human review."
                record_error "editor" "Draft rejected $writer_attempts times. Human review required."
                return 1
            fi
        fi
    done

    # Step 5: Publisher
    run_publisher || { log_error "Pipeline stopped at Publisher."; return 1; }

    log "=========================================="
    log_success "Pipeline complete! Post published."
    log "=========================================="
}

# =============================================================================
# Main
# =============================================================================

# Ensure workspace directory exists
mkdir -p "$WORKSPACE_DIR" "$DATA_DIR/audit-reports"

case "${1:-full}" in
    scout)     run_scout ;;
    analyst)   run_analyst ;;
    writer)    run_writer ;;
    editor)    run_editor ;;
    publisher) run_publisher ;;
    auditor)   run_auditor ;;
    full)      run_full_pipeline ;;
    *)
        echo "Usage: $0 {scout|analyst|writer|editor|publisher|auditor|full}"
        echo ""
        echo "  full       Run the complete pipeline (default)"
        echo "  scout      Find today's topic"
        echo "  analyst    Build research brief from topics.json"
        echo "  writer     Write draft from brief.json"
        echo "  editor     Review draft.json (accept or reject)"
        echo "  publisher  Publish final.json to WordPress"
        echo "  auditor    Monthly SEO health audit"
        exit 1
        ;;
esac
