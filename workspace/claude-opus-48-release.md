# Claude Opus 4.8 Is Out: Better Coding, Mythos-Grade Honesty, and a 3x Cheaper Fast Mode

**Meta description:** Claude Opus 4.8 releases today with a 69.2% SWE-Bench Pro score, 4x fewer unremarked code flaws, and a fast mode that costs 3x less. Here's what actually changed.

---

Anthropic released Claude Opus 4.8 today. It's faster, more accurate on agentic coding tasks, and — according to Anthropic's own alignment assessments — closer to Mythos-grade honesty than any model they've shipped to the public before. All at the same price as Opus 4.7.

That combination is worth paying attention to. For context on where this fits in the broader model picture, our [guide to the best AI models in 2026](/the-5-best-ai-models-in-2026-and-when-to-use-each-one/) covers where each model sits across all the major providers.

---

## The benchmark numbers, plainly stated

Opus 4.8 scores 69.2% on SWE-Bench Pro, Anthropic's standard for agentic coding difficulty. That's up from 64.3% on [Opus 4.7](/claude-opus-47-release/), and ahead of GPT-5.5 (58.6%) and Gemini 3.1 Pro (54.2%) on the same test. On the Super-Agent benchmark — a multi-step autonomous task evaluation — it's the only model to complete every case end-to-end.

On Humanity's Last Exam, the multidisciplinary reasoning benchmark designed to stump frontier models: 49.8% without tool use, 57.9% with tools. Both are improvements on Opus 4.7 and ahead of the named competitors.

Computer use is the strongest result. Opus 4.8 scores 84% on Online-Mind2Web, which evaluates web navigation and browser-agent tasks. That's a clear lead over both Opus 4.7 and GPT-5.5. Knowledge work score moves from 1753 to 1890.

The one exception: GPT-5.5 still leads on the terminal-coding benchmark. It's a narrow edge, but it exists.

---

## The honesty improvement matters more than the benchmark gap

The benchmark improvements are meaningful, but the bigger story in today's release is what Anthropic is calling "alignment at Mythos scale."

Opus 4.8 is approximately four times less likely than Opus 4.7 to let flaws in its own code pass without flagging them. In agentic workflows — where the model runs autonomously across a long task without human checkpoints — that matters significantly more than raw benchmark scores. A model that catches its own mistakes is a fundamentally different tool than one that quietly continues with faulty assumptions.

Anthropic describes misaligned behavior rates in Opus 4.8 as "similar to Claude Mythos Preview," their most safety-focused model currently in restricted testing. The prosocial trait scores — measures of things like supporting user autonomy, being honest about uncertainty, and avoiding unsupported claims — are at their highest recorded levels for any public Claude release.

We covered the [Claude Mythos preview](/claude-mythos-preview-anthropic-cybersecurity/) when it first became available. The alignment work being described today tracks with what early Mythos testers reported: the model is more likely to flag what it doesn't know, less likely to paper over gaps in its own output. For teams running Claude in production agentic pipelines, this is the improvement that will show up most in practice.

---

## Fast mode: 3x cheaper, 2.5x faster

Opus 4.8's fast mode runs at 2.5x the standard speed and costs three times less than fast mode on previous Opus models. Base pricing hasn't changed from Opus 4.7.

The practical implication: tasks that previously required choosing between Sonnet's speed and cost versus Opus's capability now have a middle path. Fast mode Opus 4.8 is roughly comparable to Sonnet on cost while delivering Opus-level quality on most tasks. For developers running high-frequency agentic pipelines, this changes the economics of using the flagship model.

---

## Dynamic workflows and the effort control panel

Two features shipping alongside the model:

**Dynamic workflows** — currently in research preview for [Claude Code](/claude-code-what-it-can-do-2026/) — let Claude run multiple subagents simultaneously on a task. Rather than sequential steps, you get parallel execution. For complex coding jobs where independent subtasks can run at the same time, this cuts total wall time. Not universally available yet, but Claude Code users can request access.

**Effort control** is a user-facing panel that lets you dial how much compute Claude allocates per response — a slider between "quick answer" and "thorough analysis." For teams using Claude via API, this will eventually map to explicit effort levels in requests.

Neither feature is fully launched, but both point in the same direction: more user control over the resource-quality tradeoff rather than a single fixed operating point.

---

## What this signals about Mythos

Anthropic confirmed today that Mythos-class models are coming to general availability "in the coming weeks." Opus 4.8 appears to be closing that gap from the public side — shipping with near-Mythos alignment scores on honesty and prosocial behaviour, while the Mythos model itself works through safety validation with a small number of partner organisations.

The pattern suggests Anthropic is shipping alignment improvements in layers: features validated in Mythos get backported to the public model as confidence grows. It's a more cautious approach than shipping everything at once. It also means Opus 4.8 today has capabilities that required Mythos-preview access a few weeks ago.

---

## Who should actually update their stack

**If you're currently on Opus 4.7:** the upgrade argument is clear for agentic coding use cases. The SWE-Bench Pro improvement (64.3% → 69.2%) is measurable, the honesty gains are practical in multi-step tasks, and the fast mode cost drop is immediate. Same API call, meaningfully better output.

**If you're using Sonnet 4.6 for cost reasons:** re-run the math. Fast mode Opus 4.8 has changed the cost profile significantly. You may now get Opus-quality output on more tasks without the cost penalty that made Sonnet the default.

**If you're waiting for Mythos:** Opus 4.8 ships today with Mythos-grade alignment on the measures that matter most for agentic reliability. The capability ceiling will be higher on full Mythos, but the safety improvements are already here.

We'll update our [Sonnet 4.6 vs Opus comparison](/claude-sonnet-vs-opus-46/) with Opus 4.8 numbers once we've run the standard task set.

---

Pricing is unchanged from Opus 4.7. Claude Opus 4.8 is available now via the Anthropic API, claude.ai, and as of today, through GitHub Copilot.
