# GPT-5.5 Is Out: Better Coding, Doubled API Pricing, and a Six-Week Cycle

OpenAI released GPT-5.5 on April 23, 2026 — six weeks after GPT-5.4 shipped. The internal codename is "Spud," which is roughly as corporate as it sounds. The model is faster, scores higher on every public benchmark OpenAI cares about, and costs twice as much per token in the API. If you read only one of those facts, the doubled pricing is the one that matters most for how you use it.

I haven't run my own benchmarks yet — the model is five days old as I write this. What I can do is tell you what's actually different, what the trade-offs look like on paper, and where this lands relative to [Claude Opus 4.7](/claude-opus-47-release), which Anthropic shipped just one week earlier.

## What's actually new

GPT-5.5 is OpenAI's first natively omnimodal frontier model. Previous versions stitched together separate pipelines for text, image, audio, and tool use; this one runs them through a unified architecture. In practice, that should mean faster context-switching across modalities and fewer of the failure modes where the model "forgets" an image you uploaded three turns ago. It's not a marketing trick — Anthropic and Google have been on unified architectures for a while, and OpenAI catching up here matters.

The benchmark numbers OpenAI is leading with:

- **Terminal-Bench 2.0:** 82.7%, currently the highest score from any publicly available model
- **SWE-Bench Pro:** 58.6% on real-world GitHub issue resolution
- **GDPval:** matches or beats industry professionals in 84.9% of comparisons across 44 occupations
- **MRCR v2 at 1M tokens:** 74.0%, up from GPT-5.4's 36.6% — a real jump in long-context recall

The MRCR result is the most interesting one to me. Long-context recall has been the dirty secret of every "1M token" announcement — most models advertise the window but degrade badly past 200K. Doubling the recall score in one release is a step forward, not a marketing stunt.

OpenAI also claims [GPT-5.5 uses 40% fewer tokens per Codex task](https://openai.com/index/introducing-gpt-5-5/) than GPT-5.4. That's the framing they're using to justify the price increase, which we'll get to.

## The pricing story

API pricing for gpt-5.5 starts at $5 per million input tokens and $30 per million output tokens. The previous version, gpt-5.4, was $2.50/$15. Exactly double on both ends.

For gpt-5.5-pro, OpenAI is asking $30/$180 per million — a tier roughly competitive with Claude Opus 4.7 ($15/$75) but more expensive on output, which is where most workflows actually burn tokens.

OpenAI's argument is that the effective cost increase is around 20% once you factor in token efficiency: the model uses fewer tokens to accomplish the same task, so per-task cost is lower than the per-token doubling implies. This is technically defensible. It's also exactly the kind of math that gets tested by reality the moment you run it on a workload that matters.

If you're pricing this against Claude — and you should be, especially for [business use cases where the comparison is constant](/chatgpt-for-business-2026) — Sonnet 4.6 at $3/$15 is now meaningfully cheaper than gpt-5.5 for almost everything that isn't a hard reasoning task. Opus 4.7 at $15/$75 is half the cost of gpt-5.5-pro for similar-tier workloads.

## How it stacks up vs Claude Opus 4.7

The two flagship models from the two leading labs released within a week of each other. The differentiation matters.

Opus 4.7 is the better choice when the work is genuinely complex reasoning — multi-step legal or financial analysis, hard architectural code reviews, document synthesis where the model has to hold a lot in mind simultaneously. The reasoning quality bump from Opus 4.6 to 4.7 was real, and Anthropic's pricing didn't move.

GPT-5.5 looks, on paper, like the better choice for agentic coding workloads where you're using Codex or building agent chains that hit multiple tools. The Terminal-Bench 2.0 lead and the omnimodal architecture matter most when an agent needs to switch between writing code, reading a screenshot, parsing a PDF, and calling a tool — all in the same task chain. GDPval at 84.9% is impressive but I'd want to see independent reproductions before treating it as gospel.

For a deeper comparison of the two models' ChatGPT and Claude product lines, [our 2026 head-to-head writeup](/claude-vs-chatgpt-2026) is the place to start.

## What I'd actually do with this

If you're already paying for ChatGPT Plus, Pro, or an Enterprise tier, you have GPT-5.5 already. Use it. There's no decision to make.

If you're a developer paying API costs, the calculation is harder. Three honest scenarios:

**Scenario 1: You're running a high-volume coding agent pipeline.** GPT-5.5 might genuinely net out cheaper than 5.4 once you factor in the 40% token-efficiency claim. Worth A/B testing on a real workload over a week before switching.

**Scenario 2: You're running general-purpose chat or document workflows.** Claude Sonnet 4.6 is now markedly cheaper than gpt-5.5 for similar quality. The reason to stay on OpenAI is integration depth (Custom GPTs, Codex, the Assistants API), not price.

**Scenario 3: You need the absolute best on a hard reasoning task.** Run both gpt-5.5-pro and Opus 4.7 on the same prompts. Opus 4.7 is half the price for similar results in my prior testing on document analysis, and I'd expect the same to hold here. But run the test yourself.

## The bigger picture

The release cadence is the actual story. GPT-5.4 in mid-March, GPT-5.5 six weeks later, and OpenAI explicitly framing this as a "new class of intelligence." Anthropic shipped Opus 4.7 a week ago. Google has Gemini 3 in late beta. The frontier labs are now releasing roughly monthly, and the differentiation is narrowing on raw benchmark scores while pricing diverges sharply.

What that means for [the 2026 model landscape](/the-5-best-ai-models-in-2026-and-when-to-use-each-one): the question is no longer "which model is best." It's "which model fits which workflow at which price point." GPT-5.5 didn't change that. It just made the pricing column look less favorable for OpenAI.

I'll do my own testing this week. If anything in the public benchmarks doesn't hold up in real workloads, this gets a follow-up.

---

**Sources:**
- [Introducing GPT-5.5 (OpenAI)](https://openai.com/index/introducing-gpt-5-5/)
- [GPT-5.5 System Card (OpenAI)](https://openai.com/index/gpt-5-5-system-card/)
- [OpenAI releases GPT-5.5 (TechCrunch)](https://techcrunch.com/2026/04/23/openai-chatgpt-gpt-5-5-ai-model-superapp/)
