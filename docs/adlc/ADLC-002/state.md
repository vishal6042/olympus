# ADLC state — ADLC-002

- key: ADLC-002
- title: improve other prompts used in few shot, cot
- created: 2026-07-15
- branch: adlc/ADLC-002-improve-other-prompts-used-in-few
- jira_mode: local
- current_stage: done
- gate1_spec_approved: true
- gate2_push_approved: true
- verify_attempts: 1

## Log
- 2026-07-15 init: run created for ADLC-002
- 2026-07-15 gate1: approved by user
- 2026-07-15 GATE 1: approved (strict AC4, add damaged-item 6th example). → code
- 2026-07-15 code: examples.py — added 6th example (wrong/damaged Denim Jacket → Negative/1/High, defect+quality aspects). prompts.py — few_shot_messages framing now names mixed sentiment + multiple aspects per review and aspect balancing; cot_messages Step 3 cites anchored 1-5 scale, Step 4 cites High/Medium/Low tiers. Offline sanity check passed (6 examples). → tests
- 2026-07-15 tests: added tests/test_examples.py (AC1-AC4: count/polarity, multiaspect+category coverage, schema-valid, strict semantic consistency) and 2 tests in test_prompts.py (AC5 few_shot_framing_and_embeds_all_examples, AC6 cot_steps_mapped_to_schema). AC7 covered by existing ADLC-001 tests. Full offline suite green: 17 passed. → verify
- 2026-07-15 verify: full offline pytest suite (ADLC-001 + ADLC-002) run via .venv python from milestone2/ — 17 passed in 0.01s, 0 failed. py_compile of prompts.py + examples.py OK. AC1-AC7 each covered by a passing test. verification.md written. → ship
- 2026-07-15 gate2: approved by user
- 2026-07-15 ship: committed 6302011
- 2026-07-15 ship: pushed adlc/ADLC-002-improve-other-prompts-used-in-few
