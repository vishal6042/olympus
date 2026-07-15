"""Offline unit tests for the curated Few-Shot exemplar corpus (FEW_SHOT_EXAMPLES).

These tests isolate the exemplar-corpus invariants (ADLC-002 AC1-AC4) from the prompt-string
tests in test_prompts.py. They assert on the example *data* only — no network, no LLM. The
sys.path shim in conftest.py makes `examples` and `schema` importable.
"""
from examples import FEW_SHOT_EXAMPLES
from schema import ReviewAnalysis

# The 6 core retail categories named in SYSTEM_ROLE.
CORE_CATEGORIES = {"fit", "color", "quality", "delivery", "price", "sizing"}

# Aspect-name tokens that signal a defect/damage and therefore High urgency (AC4).
DEFECT_TERMS = ("defect", "damage", "damaged", "broken", "torn")


def _aspect_sentiments(example):
    return [a["sentiment"] for a in example["analysis"]["aspects"]]


def _aspect_names(example):
    return [a["aspect"] for a in example["analysis"]["aspects"]]


# --- AC1: coverage & polarity -----------------------------------------------
def test_examples_count_and_polarity():
    assert len(FEW_SHOT_EXAMPLES) >= 5, "need at least 5 curated examples"

    # >= 2 examples must be genuinely mixed: >=1 Positive AND >=1 Negative aspect.
    mixed = [
        ex for ex in FEW_SHOT_EXAMPLES
        if "Positive" in _aspect_sentiments(ex) and "Negative" in _aspect_sentiments(ex)
    ]
    assert len(mixed) >= 2, f"need >=2 mixed-sentiment examples, found {len(mixed)}"

    ratings = [ex["analysis"]["estimated_rating"] for ex in FEW_SHOT_EXAMPLES]
    assert 5 in ratings, "need at least one strongly-positive (rating 5) example"
    assert 1 in ratings, "need at least one strongly-negative (rating 1) example"


# --- AC2: multi-aspect demonstration & category coverage --------------------
def test_examples_multiaspect_and_category_coverage():
    multi = [ex for ex in FEW_SHOT_EXAMPLES if len(ex["analysis"]["aspects"]) >= 3]
    assert len(multi) >= 2, f"need >=2 examples with >=3 aspects, found {len(multi)}"

    all_names = {name.lower() for ex in FEW_SHOT_EXAMPLES for name in _aspect_names(ex)}
    covered = CORE_CATEGORIES & all_names
    assert len(covered) >= 5, (
        f"aspect union must cover >=5 of {sorted(CORE_CATEGORIES)}; covered {sorted(covered)}"
    )


# --- AC3: every example validates against the ReviewAnalysis schema ---------
def test_examples_schema_valid():
    for i, ex in enumerate(FEW_SHOT_EXAMPLES):
        model = ReviewAnalysis(**ex["analysis"])
        assert 1 <= model.estimated_rating <= 5, f"example {i}: rating out of range"
        assert model.overall_sentiment in ("Positive", "Negative", "Neutral")
        assert model.urgency in ("High", "Medium", "Low")
        for aspect in model.aspects:
            assert aspect.sentiment in ("Positive", "Negative", "Neutral")
        # reasoning is a CoT-only output field; exemplars keep it empty (ticket note).
        assert ex["analysis"].get("reasoning", "") == "", f"example {i}: reasoning must be empty"


# --- AC4: semantic consistency (STRICT exemplar convention) -----------------
def test_examples_semantic_consistency():
    seen_all_positive = 0
    seen_all_negative = 0
    seen_mixed_or_neutral = 0
    seen_defect = 0

    for i, ex in enumerate(FEW_SHOT_EXAMPLES):
        analysis = ex["analysis"]
        sents = _aspect_sentiments(ex)
        assert sents, f"example {i}: exemplars must list at least one aspect"
        has_pos = "Positive" in sents
        has_neg = "Negative" in sents
        has_neu = "Neutral" in sents
        overall = analysis["overall_sentiment"]
        rating = analysis["estimated_rating"]
        urgency = analysis["urgency"]

        if has_pos and has_neg:  # mixed
            seen_mixed_or_neutral += 1
            assert overall == "Neutral", f"example {i}: mixed must be Neutral, got {overall}"
            assert rating == 3, f"example {i}: mixed must be rating 3, got {rating}"
        elif has_pos and not has_neg and not has_neu:  # all Positive
            seen_all_positive += 1
            assert overall == "Positive", f"example {i}: all-positive must be Positive"
            assert rating >= 4, f"example {i}: all-positive must be rating >=4, got {rating}"
            assert urgency == "Low", f"example {i}: all-positive must be Low urgency"
        elif has_neg and not has_pos and not has_neu:  # all Negative
            seen_all_negative += 1
            assert overall == "Negative", f"example {i}: all-negative must be Negative"
            assert rating <= 2, f"example {i}: all-negative must be rating <=2, got {rating}"
        elif has_neu and not has_pos and not has_neg:  # all Neutral
            seen_mixed_or_neutral += 1
            assert overall == "Neutral", f"example {i}: all-neutral must be Neutral"
            assert rating == 3, f"example {i}: all-neutral must be rating 3, got {rating}"
        else:
            raise AssertionError(
                f"example {i}: aspect sentiments {sents} do not fall into a defined "
                "exemplar bucket (all-pos / all-neg / mixed / all-neutral)"
            )

        # Any defect/damage aspect => High urgency, regardless of bucket.
        names = " ".join(_aspect_names(ex)).lower()
        if any(term in names for term in DEFECT_TERMS):
            seen_defect += 1
            assert urgency == "High", f"example {i}: defect/damage aspect must be High urgency"

    # Make sure the rules were actually exercised (not vacuously passing).
    assert seen_all_positive >= 1, "no all-positive example exercised the AC4 rule"
    assert seen_all_negative >= 1, "no all-negative example exercised the AC4 rule"
    assert seen_mixed_or_neutral >= 2, "expected >=2 mixed/neutral examples"
    assert seen_defect >= 1, "no defect/damage example exercised the High-urgency rule"
