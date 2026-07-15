# Spec — ADLC-002: Improve Few-Shot and Chain-of-Thought prompts

## Problem
Milestone-2's review analyzer offers three methods (`zero_shot`, `few_shot`, `cot`) built on the
ADLC-001-hardened `SYSTEM_ROLE`. The Few-Shot method's teaching value lives in the curated
`FEW_SHOT_EXAMPLES` (`examples.py`) and the framing text that introduces them; the CoT method's
quality lives in the Step 1–4 reasoning instructions appended to the role. Both areas are thin and
lack regression protection: nothing guarantees the exemplars stay mixed-sentiment, multi-aspect,
schema-valid, and semantically consistent with the ADLC-001 rating/urgency anchors, and nothing
guarantees the CoT steps keep mapping onto every `ReviewAnalysis` field.

## Goals / Non-goals
- **Goals:** Curate/expand `FEW_SHOT_EXAMPLES` so the AC1–AC4 invariants hold with margin; strengthen
  `few_shot_messages` framing (explicit mixed/multi-aspect cue, renders *every* example); sharpen the
  `cot_messages` Step 1–4 instructions to reference each schema field and the `reasoning` output; lock
  it all with offline pytest.
- **Non-goals:** `SYSTEM_ROLE` (ADLC-001, unchanged), `zero_shot_messages`, `messaging.py`,
  `reports.py`, `schema.py`, the `PROMPT_BUILDERS`/`METHOD_LABELS` keys, the `[(system),(human)]`
  return shape, and any live-LLM calls.

## Current state
- `few_shot_messages` (prompts.py:60) starts `[SYSTEM_ROLE, <one-sentence mixed-sentiment cue>]` then
  loops `FEW_SHOT_EXAMPLES` appending `Review:`, optional `Product context:`, and
  `Analysis: <json.dumps(analysis)>` for each — so it already embeds *all* examples, and the review is
  carried into the human turn. Existing test only checks example `[0]` is embedded.
- `cot_messages` (prompts.py:77) appends "Think step by step… `reasoning` field" + Step 1 (identify
  aspects) / Step 2 (per-aspect sentiment) / Step 3 (overall sentiment + 1–5 rating) / Step 4
  (urgency), then "Put your step-by-step explanation in `reasoning`". Covers the fields but Step 3/4
  don't cite the anchored scale/tiers.
- Current 5 examples: (1) fit+/color− mixed→Neutral/3/Medium; (2) fabric+/fit+/delivery+ →Positive/5/
  Low; (3) quality−/defect− →Negative/1/High; (4) material+/price+/sizing−/delivery− mixed→Neutral/3/
  Medium; (5) overall(Neutral)→Neutral/3/Low. Union already covers all 6 core aspects; two examples
  have ≥3 aspects; two are mixed. They already satisfy AC1–AC4 — this run hardens them and adds
  regression tests rather than fixing a defect.

## Approach
1. **Examples (examples.py):** Keep the 5, add 1 curated example for margin and clearer teaching — a
   strongly-positive multi-aspect review (fit+/color+/price+ →Positive/5/Low) or a second defect case
   (wrong/damaged item →Negative/1/High). Re-verify every example against the AC4 rule below and keep
   `reasoning=""` on all (per ticket note; reasoning is a CoT-only output field). No aspect name
   invented beyond what its review text supports (grounding).
2. **Few-Shot framing (few_shot_messages):** Reword the intro so it explicitly names *mixed sentiment*
   and *multiple aspects per review* and states that overall sentiment/rating balance the aspects
   (aligning exemplars to the ADLC-001 anchors). Preserve the loop that renders every example's JSON;
   keep `SYSTEM_ROLE` as the exact prefix and the review in the human turn.
3. **CoT steps (cot_messages):** Keep Step 1→4 order and wording that (1) identifies aspects, (2)
   assigns per-aspect sentiment, (3) weighs aspects for overall sentiment + the anchored 1–5 rating,
   (4) sets urgency by the High/Medium/Low tiers; keep the explicit instruction to record the
   step-by-step explanation in the `reasoning` field. `SYSTEM_ROLE` stays the exact prefix.

**AC4 ambiguity — chosen convention:** the ticket flags "mixed vs. a mostly-positive rating-4
exemplar." We adopt the strict, testable rule for *exemplars only*: an example is **mixed** iff it has
≥1 `Positive` and ≥1 `Negative` aspect → `overall_sentiment=Neutral`, `estimated_rating==3`. We
deliberately do **not** ship a rating-4 "mostly positive, minor issue" exemplar, so the AC4 invariant
stays unambiguous. The rating-4 anchor still exists in `SYSTEM_ROLE` for the live model; exemplars use
the clear-cut 5/3/1 anchors. all-Positive→sentiment Positive & rating≥4 & urgency Low; all-Negative→
sentiment Negative & rating≤2; any defect/damage aspect→urgency High; all-Neutral→Neutral & rating 3.

## Files to change
- `milestone2/examples.py` — curate/extend `FEW_SHOT_EXAMPLES` (justified: the exemplar corpus is the
  Few-Shot method's entire teaching signal).
- `milestone2/prompts.py` — reword `few_shot_messages` framing + `cot_messages` steps only.
- `milestone2/tests/test_examples.py` — **new** (justified: isolates exemplar-corpus invariants AC1–AC4
  from prompt-string tests, keeps ADLC-001 `test_prompts.py` untouched).
- `milestone2/tests/test_prompts.py` — add AC5/AC6 method tests; ADLC-001 SYSTEM_ROLE tests unchanged.

## Test plan (offline pytest, no network — matches conftest.py sys.path shim)
| AC | Test | Assertion |
|----|------|-----------|
| AC1 | `test_examples_count_and_polarity` | `len(FEW_SHOT_EXAMPLES)>=5`; ≥2 examples have ≥1 Positive & ≥1 Negative aspect; ≥1 with rating 5, ≥1 with rating 1 |
| AC2 | `test_examples_multiaspect_and_category_coverage` | ≥2 examples with ≥3 aspects; union of aspect names hits ≥5 of {fit,color,quality,delivery,price,sizing} |
| AC3 | `test_examples_schema_valid` | `ReviewAnalysis(**ex["analysis"])` constructs for every example (ratings 1–5, enum labels valid) |
| AC4 | `test_examples_semantic_consistency` | classify each by aspect sentiments; assert all-Pos→Positive/≥4/Low, all-Neg→Negative/≤2, mixed or all-Neutral→Neutral/==3, any `defect`/damage aspect→High |
| AC5 | `test_few_shot_framing_and_embeds_all_examples` | system startswith/contains `SYSTEM_ROLE`; framing text mentions "mixed" & "aspect"; `json.dumps(ex["analysis"])` present for **every** example; review in human turn |
| AC6 | `test_cot_steps_mapped_to_schema` | system startswith `SYSTEM_ROLE`; `Step 1..Step 4` present & ordered; steps reference aspect / sentiment / rating(1–5)+overall / urgency; `"reasoning"` mentioned |
| AC7 | `test_registry_keys_unchanged`, `test_builders_return_system_and_human_pairs`, `test_all_methods_build_without_error` (existing) + full ADLC-001 SYSTEM_ROLE suite | keys `{zero_shot,few_shot,cot}` unchanged; each builder returns `[(system),(human)]` with review in human turn; all build on `""` without error; ADLC-001 tests still green |

Every AC1–AC7 maps to ≥1 test; no criterion is untestable offline.

## Risks / rollback
- **Exemplar drift** from adding an example could break AC4 — the AC4 test is the guardrail. Rollback
  is reverting `examples.py`/`prompts.py` (prompt-only, no schema/config/interface change).
- **Wording tests too strict** vs. minor rephrasing — assert on intent keywords ("mixed", "Step N",
  field names), matching the ADLC-001 test style.
- **Out of scope, must stay intact:** `SYSTEM_ROLE`, `zero_shot_messages`, `messaging.py`,
  `reports.py`, `schema.py`, registry keys, and the `(role, content)` message-pair shape.

## Open questions
1. AC4 convention above forbids a rating-4 "mostly positive, minor issue" exemplar. Confirm this is
   acceptable (keeps the invariant clean) vs. wanting such an exemplar with a relaxed AC4 test.
2. Add a 6th example (my lean: yes, a wrong/damaged-item High-urgency case for defect margin) or keep
   the corpus at 5? Both satisfy the ACs.
