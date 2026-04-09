# LLM Pricing in Q1 2026: What Actually Changed and Where Your Money Goes

Six months ago, GPT-4o was the default. Now it's pulled from ChatGPT entirely. Claude Opus dropped from $15 to $5 per million input tokens in under a year. Gemini 2.0 Flash gets shut down in June. If you picked a model stack last year and haven't re-evaluated since, you're almost certainly overpaying.

I spent the last two weeks rebuilding our internal model routing after realising we were still sending classification tasks to Claude Sonnet — at $3 per MTok input — when Mistral Small could handle them at $0.075. Same accuracy on our eval set. That's a 40x cost difference we were just eating.

So here's where things actually stand right now, across the five providers that matter.

## OpenAI is still the default. That's both their strength and their problem.

GPT-5.4 at $2.50/$15 per MTok is the current flagship. Strong on agentic coding, multi-step reasoning, and anything where you need the model to plan and execute across multiple tool calls. The ecosystem advantage is real — more third-party integrations, more fine-tuning tooling, more StackOverflow answers when something breaks.

But OpenAI's deprecation pace is brutal. GPT-4o, GPT-4.1, GPT-4.1 mini, and o4-mini were all pulled from ChatGPT on February 13, 2026. That's four models in a single day. If you're building production systems on OpenAI, you need a migration plan that isn't "we'll deal with it when it breaks." Because it will break, and the migration window keeps shrinking.

The legacy GPT-4.1 is still in the API at $2/$8 with a 1M token context window — solid value if you don't need the latest reasoning capabilities and you can tolerate the deprecation risk. At the budget end, GPT-5 nano at $0.05/$0.40 is cheap enough for classification at scale, though I wouldn't trust it with anything that requires nuance.

No free API tier. For a company that wants developers building on their platform, that's a strange gap.

## Claude's pricing shift has been the most interesting story this quarter

Anthropic slashed Opus pricing by 3x. Opus 4.6 now costs $5/$25 per MTok — down from the original Opus 4 at $15/$75. That's not a minor adjustment. That's Anthropic saying "we want Opus in production workloads, not just demos."

Sonnet 4.6 at $3/$15 is where most teams should start. It punches above its weight on coding benchmarks and handles agentic workflows well. We've been running it as our primary model for content analysis — the quality-to-cost ratio is hard to beat at this tier.

Where Claude gets genuinely interesting for cost optimisation: the Batch API gives you a flat 50% discount across all models, and prompt caching drops read costs to 10% of base input pricing. If you're running batch workflows or prompts with a lot of shared system context, the effective per-token cost drops way below the sticker price.

The catch? No native audio or video input. Text and images only. If your pipeline needs to process meeting recordings or video content, Claude simply can't do it. That's not a minor limitation for some workloads — it's a dealbreaker.

## Google is playing a completely different pricing game

Gemini 2.5 Pro at $1.25/$10 gives you a 1M context window with full multimodal — text, code, images, audio, video. Less than half the cost of Claude Sonnet for a model that genuinely competes on quality benchmarks.

This is where I'd start for any new project that doesn't have an existing model commitment. The free tier in Google AI Studio covers Flash models with rate limits, which is enough for prototyping, internal tools, and low-traffic production apps. OpenAI and Anthropic offer nothing comparable.

Gemini 2.5 Flash at $0.30/$2.50 handles mid-tier work. Flash-Lite at $0.10/$0.40 is absurdly cheap — 50x less on input than Claude Opus. We tested Flash-Lite on our ticket categorisation pipeline last month. Accuracy was 91% versus Sonnet's 94%. For a task where a 3% difference doesn't matter and you're processing 200K tickets a day, that price gap is worth roughly $1,800/month.

One thing to watch: pricing jumps above 200K tokens. Gemini 2.5 Pro scales from $1.25 to $2.50 per MTok input past that threshold. If you're working with long documents, run the maths on your actual context sizes before committing. And Gemini 2.0 Flash gets deprecated June 1 — if you're on it, start migrating to 2.5 Flash or the newer Gemini 3 Flash now, not in May.

## Mistral and Meta are solving different problems than you think

I'm grouping these because the use case is the same: high-volume, cost-sensitive workloads where you need tokens to be as close to free as possible.

Mistral Large 3 at $0.50/$1.50 with a 256K context window is open-weight and runs on EU infrastructure. If your compliance team has opinions about data sovereignty — and if you're working with Danish or European clients, they probably do — this matters more than benchmark scores.

Mistral Small 3.2 at $0.075/$0.20 is the real story though. For extraction, classification, routing — the kind of structured tasks where you process millions of tokens daily — it's roughly 65x cheaper on input than Claude Opus. Not the same quality tier. Doesn't need to be. When you're classifying support tickets into 12 categories, you don't need a model that can write poetry.

Meta's Llama 3.3 70B is free weights under the community license. Self-hosting on a single H100 runs about $50/month in electricity versus thousands in API fees for equivalent throughput. The economics are compelling if — and this is a big if — you have the GPU infrastructure and the ops team to run it. For a small team, the infrastructure overhead can quietly exceed what you'd spend on API calls. I've seen it happen twice. Both times the team underestimated the monitoring and patching burden.

Llama is text-only. No image, no audio. And the 128K context window has a practical ceiling closer to 80-90K — community benchmarks show 15-20% accuracy drops on retrieval tasks above that range. The newer Llama 4 Scout and Maverick models push context to 10M tokens, but they're early. I wouldn't build production systems on them yet.

## So what do you actually pick?

Stop trying to find the "best" model. That framing produces bad decisions.

For complex reasoning and coding agents, Claude Opus 4.6 or GPT-5.4. The flagship tier exists for a reason and the quality difference on hard problems is measurable. Don't cheap out on the tasks that actually matter.

For general enterprise workloads, Gemini 2.5 Pro or Claude Sonnet 4.6. Gemini wins on price, Claude wins on coding quality. Pick based on your primary workload.

For high-volume structured tasks, Gemini Flash-Lite, Mistral Small 3.2, or GPT-5 nano. At these volumes, per-token cost is the only metric that matters. Test all three on your actual data, pick the cheapest one that clears your quality bar, and move on.

For data sovereignty, Mistral Large 3 for managed simplicity or Llama for full control on your own hardware.

The right answer for most organisations isn't one model. It's two or three — a flagship for the hard stuff, a mid-tier workhorse for daily operations, and a budget model for the volume work. Route your traffic accordingly.

One more thing. Every price and model version in this post will be wrong within three months. Build your architecture so swapping models is a config change, not a rewrite.

Need help evaluating which LLM stack fits your organisation? We help Danish businesses build practical AI workflows — not theoretical ones. Get in touch for a free assessment.

Next up: a deep dive into each of these models individually — what they're actually good at, where they fall apart, and which specific workloads each one fits best.
