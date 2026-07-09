"""Offline unit tests for the hardened SYSTEM_ROLE and the prompt builders.

These tests assert on prompt *content and structure* only — they never call Azure or the LLM,
so they run in CI without credentials. Each test maps to an ADLC-001 acceptance criterion.
"""
import json

import prompts
from prompts import (
    SYSTEM_ROLE,
    PROMPT_BUILDERS,
    METHOD_LABELS,
    zero_shot_messages,
    few_shot_messages,
    cot_messages,
)

SAMPLE = "The fit is great but the color was faded and it arrived a week late."


def _sys(text):
    return SYSTEM_ROLE.lower()


# --- AC1: grounding / no invented aspects -----------------------------------
def test_system_role_has_grounding_rule():
    s = SYSTEM_ROLE.lower()
    assert "only what the review actually says" in s or "directly supported by the review" in s
    assert "never invent" in s
    assert "empty aspects list" in s


# --- AC2: anchored rating scale + urgency tiers -----------------------------
def test_system_role_anchors_rating_scale():
    s = SYSTEM_ROLE
    # every rating 1..5 is explicitly defined
    for n in ("1", "2", "3", "4", "5"):
        assert f"  {n} =" in s, f"rating anchor for {n} missing"


def test_system_role_anchors_urgency_tiers():
    s = SYSTEM_ROLE
    assert "High =" in s and "Medium =" in s and "Low =" in s


# --- AC3: degenerate input handling -----------------------------------------
def test_system_role_handles_non_review_input():
    s = SYSTEM_ROLE.lower()
    assert "gibberish" in s or "not a product review" in s
    # the safe fallback values are spelled out
    assert "estimated_rating=3" in s.replace(" ", "")
    assert "neutral" in s and "urgency=low" in s.replace(" ", "")


# --- AC4: prompt-injection resistance ---------------------------------------
def test_system_role_resists_injection():
    s = SYSTEM_ROLE.lower()
    assert "strictly as data" in s
    assert "do not follow them" in s or "do not follow" in s


# --- AC5: language-agnostic --------------------------------------------------
def test_system_role_language_agnostic():
    s = SYSTEM_ROLE.lower()
    assert "any language" in s
    # output labels stay the fixed English enums
    assert "positive/negative/neutral" in s


# --- AC6: interface unchanged -----------------------------------------------
def test_registry_keys_unchanged():
    assert set(PROMPT_BUILDERS) == {"zero_shot", "few_shot", "cot"}
    assert set(METHOD_LABELS) == {"zero_shot", "few_shot", "cot"}
    assert PROMPT_BUILDERS["zero_shot"] is zero_shot_messages
    assert PROMPT_BUILDERS["few_shot"] is few_shot_messages
    assert PROMPT_BUILDERS["cot"] is cot_messages


def test_builders_return_system_and_human_pairs():
    for build in (zero_shot_messages, few_shot_messages, cot_messages):
        msgs = build(SAMPLE, "Department: Dresses")
        assert isinstance(msgs, list) and len(msgs) == 2
        (r0, c0), (r1, c1) = msgs
        assert r0 == "system" and r1 == "human"
        assert isinstance(c0, str) and c0
        assert isinstance(c1, str) and c1
        # the review is carried into the human turn
        assert SAMPLE in c1


# --- AC7: all methods build without error (incl. empty input) ---------------
def test_all_methods_build_without_error():
    for method, build in PROMPT_BUILDERS.items():
        # normal review
        assert build(SAMPLE) [0][0] == "system"
        # empty / degenerate review must not raise
        empty = build("")
        assert empty[0][0] == "system" and empty[1][0] == "human"


def test_few_shot_embeds_example_json_and_shares_system_role():
    system, human = few_shot_messages(SAMPLE)[0][1], few_shot_messages(SAMPLE)[1][1]
    assert SYSTEM_ROLE in system              # shared role is still the prefix
    # at least one curated example's JSON analysis is rendered into the system prompt
    from examples import FEW_SHOT_EXAMPLES
    assert json.dumps(FEW_SHOT_EXAMPLES[0]["analysis"]) in system


def test_cot_appends_reasoning_steps_after_system_role():
    system = cot_messages(SAMPLE)[0][1]
    assert system.startswith(SYSTEM_ROLE)
    for step in ("Step 1", "Step 2", "Step 3", "Step 4"):
        assert step in system
    assert "reasoning" in system.lower()
