# ADLC-002: Improve Few-Shot and Chain-of-Thought prompts for review analysis

- **Status:** To Do
- **Type:** Task
- **Mode:** local
- **Created:** 2026-07-15

## Description

Milestone 2 (ChicStyle "Real-Time Retail Feedback Intelligence") exposes three prompting
methods for its review-analysis system: `zero_shot`, `few_shot`, and `cot`
(`milestone2/prompts.py`). ADLC-001 already hardened the shared `SYSTEM_ROLE` (grounding,
anchored rating scale, urgency tiers, degenerate-input fallback, prompt-injection resistance,
multilingual). This run improves the two method-specific prompts that build on top of it.

**Problem / why:** The Few-Shot method's teaching value depends entirely on the curated
examples in `milestone2/examples.py` and the framing text that introduces them; the
Chain-of-Thought method's quality depends on the explicit reasoning-step instructions appended
to the system role. Today those two areas are thin: the few-shot examples must reliably
demonstrate mixed sentiment and multi-aspect extraction and must themselves be internally
consistent (aspect sentiments agreeing with the stated overall sentiment and rating, ratings
within the ADLC-001 scale, urgency matching the tiers), and the CoT reasoning steps should map
cleanly onto every field of the `ReviewAnalysis` schema so the model produces reliable
structured output. Weak or inconsistent exemplars teach the wrong behavior, and vague reasoning
steps produce sloppy `reasoning` text and mis-weighted ratings.

**Goal:** Strengthen the Few-Shot prompt (its framing and/or the curated examples) and the
Chain-of-Thought prompt (its reasoning-step instructions) to improve mixed-sentiment handling,
multi-aspect extraction, and reliable structured output — while keeping the ADLC-001 hardening
and the public interface intact.

## Scope

**In scope**
- `milestone2/examples.py`: content, count, coverage, and internal consistency of
  `FEW_SHOT_EXAMPLES`.
- `milestone2/prompts.py`: the `few_shot_messages` framing text and the `cot_messages`
  reasoning-step instructions.
- Offline unit tests under `milestone2/tests/` asserting the criteria below.

**Out of scope**
- `SYSTEM_ROLE` hardening (owned by ADLC-001 — must remain unchanged / intact).
- `zero_shot_messages` behavior.
- `milestone2/messaging.py` (customer message) and `milestone2/reports.py` (retail report).
- Any change to the `ReviewAnalysis` schema, the `PROMPT_BUILDERS` / `METHOD_LABELS` registry
  keys, or the `(role, content)` message-pair return shape.
- Live Azure OpenAI / LLM calls — every acceptance criterion must be checkable offline.

## Acceptance criteria

- [ ] **AC1 — Few-Shot example coverage.** `FEW_SHOT_EXAMPLES` contains at least 5 examples,
  including at least 2 that demonstrate *mixed sentiment* (the same example has at least one
  `Positive` and at least one `Negative` aspect), and the set collectively covers at least one
  strongly-positive (rating 5) and at least one strongly-negative (rating 1) example.
- [ ] **AC2 — Multi-aspect demonstration.** At least 2 examples contain 3 or more distinct
  aspects, and across all examples the union of aspect names covers the core retail categories
  named in `SYSTEM_ROLE` (fit, color, quality, delivery, price, sizing) — at least 5 of those 6
  appear.
- [ ] **AC3 — Examples are internally consistent (schema-valid).** Every example's `analysis`
  validates against the `ReviewAnalysis` pydantic model (ratings 1–5, sentiment/urgency use the
  fixed enum labels), and each aspect uses a valid `Sentiment` label.
- [ ] **AC4 — Examples are internally consistent (semantics).** For every example: an
  all-`Positive`-aspect analysis has `overall_sentiment=Positive` and `estimated_rating>=4`; an
  all-`Negative`-aspect analysis has `overall_sentiment=Negative` and `estimated_rating<=2`; a
  mixed or all-`Neutral` analysis has `overall_sentiment=Neutral` and `estimated_rating==3`. Any
  example with a defect/damage aspect (e.g. `defect`) has `urgency=High`, and any all-positive
  example has `urgency=Low`.
- [ ] **AC5 — Few-Shot framing renders all examples with mixed-sentiment cue.** `few_shot_messages`
  still prefixes the unchanged `SYSTEM_ROLE`, its framing text explicitly mentions mixed /
  multiple-aspect sentiment, and the built system prompt embeds the rendered JSON `analysis` of
  every example in `FEW_SHOT_EXAMPLES` (not just the first).
- [ ] **AC6 — CoT enumerates reasoning steps mapped to schema.** `cot_messages` appends its
  reasoning instructions after the unchanged `SYSTEM_ROLE`, enumerates steps `Step 1`..`Step 4`
  in order, and those steps explicitly reference identifying aspects, per-aspect sentiment, the
  1–5 rating / overall sentiment, and urgency; the instructions direct the model to record the
  explanation in the `reasoning` field.
- [ ] **AC7 — Interface and ADLC-001 hardening intact.** `PROMPT_BUILDERS` /
  `METHOD_LABELS` keys are unchanged, every builder returns a 2-element `[(system,...),(human,...)]`
  list carrying the review into the human turn, all builders run without error on empty input,
  and the existing ADLC-001 `SYSTEM_ROLE` tests still pass (grounding, rating anchors, urgency
  tiers, degenerate input, injection resistance, multilingual).

## Notes

- All criteria are verifiable by offline unit tests in `milestone2/tests/` (see existing
  `test_prompts.py` pattern — imports `prompts` / `examples`, asserts on string content and
  validates example dicts against `ReviewAnalysis`; no network).
- AC4 encodes the mixed/neutral rule as `estimated_rating==3`, matching the ADLC-001 rating
  scale anchor "3 = mixed or neutral". If a future example intentionally deviates (e.g. mostly
  positive with a minor negative → rating 4), the test/AC should be refined during spec — noted
  as a mild ambiguity in what counts as "mixed."
- Keep example `reasoning` fields empty (`""`); reasoning is a CoT-only output field per the
  schema, so exemplars should not populate it.
