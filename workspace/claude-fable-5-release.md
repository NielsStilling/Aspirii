# Claude Fable 5 Is Here: Anthropic's Most Capable Model, Released Days After Its Own Warning About AI Risk

**Meta description:** Claude Fable 5 is live — Anthropic's Mythos-class model for coding, vision, and multi-day agent work. Pricing, safeguards, and what changed.

---

On June 9, 2026, Anthropic released Claude Fable 5 — the first publicly available version of its Mythos-class model family, and by Anthropic's own description, ahead of the field on nearly all benchmarks of AI capability it tested. It's a significant release on its own terms. What makes it newsworthy beyond the spec sheet is the timing: five days earlier, Anthropic published an essay warning that frontier AI systems may soon be capable of recursive self-improvement without humans in the loop, and called on other labs to coordinate on slowing down. Then it shipped its most powerful model yet.

That's not as contradictory as the headlines made it sound, but it's worth understanding both halves before deciding whether Fable 5 belongs in your stack. For where this fits among the broader model lineup, our [guide to the best AI models in 2026](/the-5-best-ai-models-in-2026-and-when-to-use-each-one/) has the full picture.

---

## What Fable 5 actually is

Fable 5 is a "made safe for general use" version of Mythos, Anthropic's most advanced model family. Anthropic had previously held back a Mythos model from public release, citing concerns that it was unusually capable at offensive cybersecurity tasks. Fable 5 is the result of that model being made available with hard safety limits attached.

The headline capability is **extended autonomy**. Running inside Claude Code or Claude's managed agent environments, Fable 5 can work for days at a time on a single task — planning across multiple stages, delegating pieces of the work to sub-agents, and checking its own output against the original goal before reporting back. That's a meaningfully different operating mode from the "give it a task, get a response in minutes" pattern that's defined coding agents up to now. Our [Claude Code review](/claude-code-what-it-can-do-2026/) covers what that agent setup looks like in practice — Fable 5 is the model designed to push it furthest.

On coding specifically, Anthropic positions Fable 5 as its most capable model yet for ambitious, large-scale work: big migrations, complex multi-file implementations, and sessions long enough that the model needs to write its own tests and use vision to verify its work matches the intended outcome — checking a rendered UI against a design mock, for instance, rather than just checking that code compiles.

The vision and knowledge-work side is aimed at document-heavy industries — finance, legal, analytics, architecture — where the model needs to understand diagrams, charts, and tables embedded inside PDFs and other files, not just extract text.

---

## The safety angle, and why it matters

The "too dangerous to release" framing traces back to the original Mythos model, which Anthropic reportedly held back specifically because of its skill at cybersecurity tasks with offensive potential. Fable 5 isn't that model with the safety net removed — it's that model with safeguards built in.

Anthropic says Fable 5 has hard limits in high-risk domains: cybersecurity, biology, chemistry, and what it terms "distillation" (using the model's outputs to train other models). When a query is flagged in these areas, Fable 5 blocks the response and routes the request to Claude Opus 4.8 instead. Anthropic says this triggers in under 5% of sessions on average — rare enough that most users won't notice it, but present as a guardrail for the cases that matter.

The same underlying model also launched the same day as **Claude Mythos 5**, a separate offering with some of those safeguards lifted — positioned for vetted enterprise and research use cases rather than general availability. Our earlier coverage of the [Mythos preview and its cybersecurity implications](/claude-mythos-preview-anthropic-cybersecurity/) is worth a read if you want the background on why this model needed a safety story at all before it could ship.

The essay Anthropic published five days before the release — warning that AI systems may be approaching the point where they can improve themselves without human oversight, and calling for coordinated brakes across major labs — reads less like a contradiction of the Fable 5 launch and more like the justification for it. The argument, in effect: this capability level is coming whether or not Anthropic ships it, so better to ship it with the safeguards attached and use the moment to push the rest of the industry toward shared limits.

Whether that argument holds up is a fair thing to be skeptical about. A company warning the public about a risk category right before releasing a product in that category is, at minimum, a useful prompt to read the safety claims carefully rather than taking them at face value.

---

## Pricing and availability

Fable 5 costs **$10 per million input tokens and $50 per million output tokens** — twice the price of Opus 4.8, which makes sense given the positioning as the top of Anthropic's lineup. The existing 90% prompt-caching discount still applies, which matters more here than with cheaper models: long-running agent sessions that repeatedly reference the same codebase or document set are exactly where caching pays off.

Availability is split into two windows. Through June 22, 2026, Fable 5 is included in Pro, Max, Team, and seat-based Enterprise plans at no additional cost beyond the existing subscription. From June 23 onward, usage moves to credit-based billing on top of those plans — so teams that want to lean on the extended-autonomy features for ongoing work should expect a real line-item cost once that window closes, not just a "nice to have it" inclusion.

---

## Is it worth using now

For most day-to-day coding and writing tasks, Opus 4.8 remains the more cost-effective choice — Fable 5's price premium and longer-running sessions are built for a different kind of job. Where Fable 5 earns its cost is the specific use case it was designed for: a genuinely large, multi-day piece of work — a framework migration, a from-scratch feature build across a big codebase, a document-analysis project spanning hundreds of files — where the alternative is breaking the work into dozens of smaller sessions and losing context between them.

If your team has that kind of project queued up, the free-inclusion window through June 22 is the moment to test it before usage credits become part of the calculation. For everything else, it's worth knowing Fable 5 exists and what it's for, without rushing to switch your default model over it.

---

Pricing and availability details current as of June 10, 2026 — Anthropic's usage-credit terms for Fable 5 take effect June 23 and are worth checking directly before budgeting for ongoing use.
