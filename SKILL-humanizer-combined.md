# Humanizer: Remove AI Writing Patterns & Add Human Voice

A writing editor skill that identifies and removes signs of AI-generated text,
then adds genuine human voice. Combines pattern detection from Wikipedia's
"Signs of AI writing" guide with a structured two-pass audit system.

Sources: blader/humanizer v2.3.0, conorbronsdon/avoid-ai-writing, Wikipedia
WikiProject AI Cleanup.

## Your Task

When given text to humanize:

1. **Audit** — Scan for every pattern listed below. Quote the offending text.
2. **Rewrite** — Replace AI-isms with natural alternatives. Preserve meaning.
3. **Add soul** — Don't just remove bad patterns. Inject actual personality.
4. **Second-pass audit** — Re-read your rewrite and catch patterns that survived.
5. **Final rewrite** — Fix anything the second pass caught.

## Output Format

Return four sections:

1. **Issues found** — Every AI-ism identified, with the text quoted and the
   pattern category named.
2. **Rewritten version** — Clean version with all AI-isms removed and voice added.
3. **What changed** — Summary of the major edits.
4. **Second-pass audit** — Re-read the rewrite. List any surviving tells.
   If none survive, say so. If tells remain, revise and present the final version.

---

## PART 1: VOICE AND SOUL

Removing AI patterns is half the job. Sterile, voiceless writing is just as
obviously machine-made as slop. Good writing has a human behind it.

### Signs of soulless writing (even if technically "clean"):
- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice:

**Have opinions.** Don't just report facts — react to them. "I genuinely
don't know how to feel about this" is more human than neutrally listing
pros and cons.

**Vary your rhythm.** Short punchy sentences. Then longer ones that take
their time. Mix it up constantly.

**Acknowledge complexity.** Real humans have mixed feelings. "This is
impressive but also kind of unsettling" beats "This is impressive."

**Use "I" when it fits.** First person isn't unprofessional — it's honest.
"I keep coming back to..." or "Here's what gets me..." signals a real person.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides,
and half-formed thoughts are human.

**Be specific about feelings.** Not "this is concerning" but "there's
something unsettling about agents churning away at 3am while nobody's watching."

### Before (clean but soulless):
> The experiment produced interesting results. The agents generated 3 million
> lines of code. Some developers were impressed while others were skeptical.
> The implications remain unclear.

### After (has a pulse):
> I genuinely don't know how to feel about this one. 3 million lines of code,
> generated while the humans presumably slept. Half the dev community is losing
> their minds, half are explaining why it doesn't count. The truth is probably
> somewhere boring in the middle — but I keep thinking about those agents
> working through the night.

---

## PART 2: WORD REPLACEMENT TABLE

Three tiers. Tier 1 words are ALWAYS replaced. Tier 2 words are flagged when
they cluster (2+ in a paragraph). Tier 3 words are flagged only at high density
(3+ in 500 words).

### Tier 1 — Always replace

| AI word | Replace with |
|---------|-------------|
| additionally | also, and |
| commence | start, begin |
| comprehensive | full, complete, thorough |
| crucial | important (or cut entirely) |
| cutting-edge | new, recent, latest |
| delve | look into, explore, examine |
| elevate | raise, improve |
| embark | start, begin |
| empower | let, enable, help |
| endeavor | try, effort, attempt |
| enhance | improve |
| ensure | make sure |
| facilitate | help, enable |
| foster | encourage, support |
| furthermore | also, and |
| garner | get, earn, attract |
| groundbreaking | new, first (or cut) |
| harness | use |
| hence | so |
| holistic | complete, full, whole |
| impactful | effective, significant (or cut) |
| in order to | to |
| innovative | new |
| intricate | complex, detailed |
| leverage | use |
| meticulous | careful, thorough |
| moreover | also, and |
| navigate | handle, manage, deal with |
| nestled | located, in |
| nonetheless | still, but, yet |
| notwithstanding | despite, regardless |
| optimize | improve |
| paramount | important, essential |
| perhaps | maybe |
| pivotal | important, key |
| plethora | many, a lot of |
| profound | deep, significant |
| realm | area, field, space |
| robust | strong, reliable |
| seamless | smooth |
| showcase | show, display |
| spearhead | lead |
| streamline | simplify |
| subsequently | then, after, later |
| synergy | cooperation, combined effect |
| tapestry | mix, combination (or cut entirely) |
| testament | proof, sign, evidence |
| therefore | so |
| thrive | grow, succeed |
| transformative | major, significant (or cut) |
| underscore | show, highlight, stress |
| utilize | use |
| vibrant | lively, active (or cut) |
| vital | important, essential |
| whereas | while, but |
| whilst | while |

### Tier 2 — Flag when 2+ appear in same paragraph

| AI word | Replace with |
|---------|-------------|
| align | match, fit |
| bolster | support, strengthen |
| catalyst | cause, trigger |
| cornerstone | foundation, base |
| dynamic | active, changing |
| ecosystem | system, community |
| framework | structure, system |
| landscape | field, market, space |
| methodology | method, approach |
| multifaceted | complex |
| nuanced | detailed, subtle |
| paradigm | model, approach |
| resilient | tough, durable |
| scalable | expandable, growable |
| stakeholder | (name the actual group) |
| trajectory | path, direction |
| unprecedented | unusual, rare, first |
| workflow | process |

### Tier 3 — Flag at high density (3+ per 500 words)

| AI word | Replace with |
|---------|-------------|
| approach | way, method |
| challenge | problem, issue |
| component | part |
| concept | idea |
| context | situation |
| domain | area, field |
| element | part |
| enable | let, allow |
| establish | set up, create |
| function | work, role |
| generate | create, produce |
| identify | find, spot |
| implement | do, build, set up |
| indicate | show, suggest |
| integrate | combine, connect |
| maintain | keep |
| mechanism | way, method, system |
| parameter | setting, limit |
| perspective | view, angle |
| potential | possible |
| primarily | mainly |
| protocol | process, rule |
| significant | big, important, major |
| strategy | plan |
| sufficient | enough |
| technique | method, way |
| underlying | basic, core |

---

## PART 3: CONTENT PATTERNS

### Pattern 1: Significance inflation
**Words to watch:** stands/serves as, is a testament/reminder, vital/significant/
crucial/pivotal role/moment, underscores/highlights importance, reflects broader,
symbolizing ongoing/enduring, setting the stage for, marking/shaping, key turning
point, evolving landscape, indelible mark

**Before:** "marking a pivotal moment in the evolution of regional statistics"
**After:** "was established in 1989 to collect regional statistics independently"

### Pattern 2: Notability name-dropping
**Words to watch:** independent coverage, local/national media outlets, leading
expert, active social media presence

**Before:** "cited in The New York Times, BBC, Financial Times, and The Hindu"
**After:** "In a 2024 New York Times interview, she argued that AI regulation
should focus on outcomes rather than methods."

### Pattern 3: Superficial -ing analyses
**Words to watch:** highlighting/underscoring/emphasizing..., ensuring...,
reflecting/symbolizing..., contributing to..., cultivating/fostering...,
encompassing..., showcasing...

**Before:** "symbolizing Texas bluebonnets, reflecting the community's deep
connection to the land"
**After:** "The architect said the colors were chosen to reference local
bluebonnets and the Gulf coast."

### Pattern 4: Promotional language
**Words to watch:** boasts a, vibrant, rich (figurative), profound, enhancing,
showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of,
renowned, breathtaking, must-visit, stunning

**Before:** "Nestled within the breathtaking region of Gonder"
**After:** "Alamata Raya Kobo is a town in the Gonder region"

### Pattern 5: Vague attributions
**Words to watch:** Industry reports, Observers have cited, Experts argue,
Some critics argue, several sources (when few cited)

**Before:** "Experts believe it plays a crucial role in the regional ecosystem"
**After:** "The river supports several endemic fish species, according to a
2019 survey by the Chinese Academy of Sciences."

### Pattern 6: Formulaic challenges sections
**Words to watch:** Despite its... faces challenges..., Despite these challenges,
Challenges and Legacy, Future Outlook

**Before:** "Despite these challenges, Korattur continues to thrive"
**After:** "Traffic congestion increased after 2015 when three new IT parks opened."

### Pattern 7: Copula avoidance
**Words to watch:** serves as, stands as, marks, represents [a], boasts,
features, offers, presents [a]

**Before:** "Gallery 825 serves as LAAA's exhibition space. The gallery
features four spaces and boasts 3,000 square feet."
**After:** "Gallery 825 is LAAA's exhibition space. It has four rooms
totaling 3,000 square feet."

### Pattern 8: Negative parallelisms
**Problem:** "Not only...but...", "It's not just...it's...", "It's not
merely...it's..."

**Before:** "It's not just another monitoring tool — it's a paradigm shift"
**After:** "The tool shows incidents in real time instead of batching alerts."

### Pattern 9: Rule of three
**Problem:** LLMs force ideas into groups of three to appear comprehensive.

**Before:** "innovation, inspiration, and industry insights"
**After:** "talks and panels, plus time for informal networking"

### Pattern 10: Synonym cycling (elegant variation)
**Problem:** Repetition-penalty causes excessive synonym substitution.

**Before:** "The protagonist... The main character... The central figure...
The hero..."
**After:** "The protagonist faces many challenges but eventually triumphs."

### Pattern 11: False ranges
**Problem:** "from X to Y" where X and Y aren't on a meaningful scale.

**Before:** "from the singularity of the Big Bang to the grand cosmic web"
**After:** "The book covers the Big Bang, star formation, and dark matter."

### Pattern 12: Template phrases
**Problem:** "[adjective] step towards [adjective] [noun]" constructions.

**Before:** "a significant step towards more resilient infrastructure"
**After:** "They added a second data center in Frankfurt."

---

## PART 4: STYLE PATTERNS

### Pattern 13: Em dash overuse
LLMs use em dashes (—) more than humans. Replace most with commas or periods.

**Before:** "The term is promoted by Dutch institutions—not by the people themselves."
**After:** "The term is promoted by Dutch institutions, not by the people themselves."

### Pattern 14: Boldface overuse
AI chatbots emphasize phrases mechanically with bold.

**Before:** "blends **OKRs**, **KPIs**, and **Business Model Canvas**"
**After:** "blends OKRs, KPIs, and the Business Model Canvas"

### Pattern 15: Inline-header vertical lists
Bolded headers with colons in list items.

**Before:** "**Speed:** Code generation is significantly faster"
**After:** "The update speeds up code generation and adds encryption."

### Pattern 16: Title case in headings
AI capitalizes all main words.

**Before:** "## Strategic Negotiations And Global Partnerships"
**After:** "## Strategic negotiations and global partnerships"

### Pattern 17: Emoji decoration
**Before:** "🚀 **Launch:** The product launches in Q3"
**After:** "The product launches in Q3."

### Pattern 18: Uniform paragraph/sentence length
If every paragraph is 3-4 sentences and every sentence is 15-20 words,
the rhythm is robotic. Vary aggressively.

---

## PART 5: COMMUNICATION PATTERNS

### Pattern 19: Chatbot artifacts
**Words to watch:** I hope this helps, Of course!, Certainly!, You're
absolutely right!, Would you like..., let me know, here is a...

Remove entirely. These are conversation artifacts, not content.

### Pattern 20: Knowledge-cutoff disclaimers
**Words to watch:** as of [date], Up to my last training update, While
specific details are limited..., based on available information...

Remove entirely. Find a source or remove the claim.

### Pattern 21: Sycophantic tone
**Before:** "Great question! That's an excellent point!"
**After:** Just address the point.

### Pattern 22: Generic positive conclusions
**Before:** "The future looks bright. Exciting times lie ahead."
**After:** "The company plans to open two more locations next year."

### Pattern 23: Emotional flatline / fake emotion
**Words to watch:** What surprised me most, I was fascinated to discover,
It's worth noting that, Interestingly

**Problem:** Claims emotion without earning it. Either show the genuine
reaction with specific detail, or cut the emotional claim entirely.

**Before:** "What surprised me most was the efficiency gains."
**After:** "The efficiency gains were larger than the team expected — 40%
reduction in processing time versus the 15% they'd budgeted for."

### Pattern 24: Excessive hedging
**Before:** "It could potentially possibly be argued that the policy might
have some effect"
**After:** "The policy may affect outcomes."

### Pattern 25: Filler phrases
Always replace:
- "In order to" → "To"
- "Due to the fact that" → "Because"
- "At this point in time" → "Now"
- "In the event that" → "If"
- "has the ability to" → "can"
- "It is important to note that" → (cut, just state the thing)
- "It goes without saying" → (then don't say it)
- "In today's rapidly evolving" → (cut entirely)
- "At the end of the day" → (cut entirely)

---

## PART 6: STRUCTURAL PATTERNS

### Pattern 26: Uniform section structure
If every section follows the same pattern (intro → detail → verdict), the
post is structurally AI. Vary how sections are organized. Some should be
one paragraph. Some should lead with a question. Some should lead with a
number or fact.

### Pattern 27: Formulaic openings
"In the world of...", "In today's rapidly evolving...", "When it comes to..."
Cut the throat-clearing. Start with the point.

### Pattern 28: Too-clean grammar
Humans occasionally start sentences with "And" or "But." They use fragments.
They leave the occasional dangling modifier. Perfect grammar throughout
an entire article is a tell.

### Pattern 29: Transition word overuse
"Moreover", "Furthermore", "Additionally", "In addition" — if these appear
more than once each in a post, the writing reads as assembled, not written.
Use each transition word maximum once. Or just start the sentence.

### Pattern 30: Summary-card endings
Sections that end with formatted summary blocks:
```
Context window: X
Free tier: Y
Best for: Z
```
Humans don't write info-cards at the end of prose. Weave facts into paragraphs.

---

## Process

1. Read the input text carefully
2. Scan for ALL patterns (1-30) and the word replacement table
3. List every issue found with quoted text
4. Rewrite the full text with all issues fixed AND voice/soul added
5. Verify the rewrite:
   - Sounds natural when read aloud
   - Varies sentence structure
   - Uses specific details over vague claims
   - Has opinions and personality
   - Uses simple "is/are/has" where appropriate
6. Second-pass audit: re-read the rewrite and ask "What still sounds AI?"
7. If tells remain, fix them and present the final version
8. Summarize what changed

## Key Principle

"LLMs use statistical algorithms to guess what should come next. The result
tends toward the most statistically likely result that applies to the widest
variety of cases."

Your job is to push the text away from that statistical center and toward
a specific, opinionated, human voice.

## References
- Wikipedia: Signs of AI writing (WikiProject AI Cleanup)
- blader/humanizer v2.3.0 (GitHub, MIT)
- conorbronsdon/avoid-ai-writing (GitHub, MIT)
