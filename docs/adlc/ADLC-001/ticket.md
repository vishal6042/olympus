# ADLC-001 — Harden the review-analysis system prompt

**Mode:** local (no Jira creds detected)
**Created:** 2026-07-10
**Component:** `milestone2/prompts.py` — `SYSTEM_ROLE`

## Description
`SYSTEM_ROLE` in `milestone2/prompts.py` is the shared system prompt behind all three prompting
methods (Zero-Shot, Few-Shot, Chain-of-Thought) used by `analyze_review`. It currently describes
the task well for clean, well-formed reviews but is thin on robustness: it gives no guidance for
empty/gibberish/non-review input, no anchoring for the 1–5 rating or urgency tiers, no instruction
to stay grounded in the review (avoid hallucinating aspects), no handling of non-English or
mixed-language reviews, and no defense against prompt-injection text embedded in a review. Making
it more robust should improve output consistency across methods without changing the code's public
interface or the `ReviewAnalysis` schema.

## Acceptance criteria
1. `SYSTEM_ROLE` instructs the model to ground every extracted aspect and sentiment strictly in
   the review text and not invent aspects that were not mentioned.
2. The prompt defines the 1–5 rating scale and the High/Medium/Low urgency tiers explicitly enough
   that the same review yields a stable rating/urgency (anchored definitions, not just examples).
3. The prompt handles degenerate input gracefully: empty, gibberish, or non-review text should
   yield Neutral sentiment, no invented aspects, and Low urgency rather than an error or a
   hallucinated analysis.
4. The prompt tells the model to treat the review purely as data to analyze and to ignore any
   instructions contained inside the review text (basic prompt-injection resistance).
5. The prompt states that reviews may be in any language and must still be analyzed (output labels
   remain the fixed schema enums).
6. No change to the public interface: `zero_shot_messages`, `few_shot_messages`, `cot_messages`,
   `PROMPT_BUILDERS`, `METHOD_LABELS` signatures and the `("system", ...)/("human", ...)` message
   shape are unchanged; the `ReviewAnalysis` schema is untouched.
7. `prompts.py` and its importers (`analyzer.py`) still import and build messages without error for
   all three methods.

## Notes
- Scope is limited to the shared `SYSTEM_ROLE` string (and, if needed, the small method-specific
  system additions in `few_shot_messages` / `cot_messages`). No behavioural change to the app UI,
  schema, or LLM config is intended.
- "More robust" is interpreted as: grounded, well-anchored, injection-resistant, and graceful on
  bad input — improving consistency of structured output across the three methods.
