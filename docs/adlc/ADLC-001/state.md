# ADLC run state — ADLC-001

- key: ADLC-001
- title: Harden the review-analysis system prompt
- created: 2026-07-10
- branch: adlc/ADLC-001-robust-system-prompt
- jira_mode: local
- current_stage: done
- gate1_spec_approved: true
- gate2_push_approved: true
- verify_attempts: 0

## Log
- 2026-07-10 intake: created ticket.md (local mode, no Jira creds); KEY ADLC-001; branch adlc/ADLC-001-robust-system-prompt. → spec
- 2026-07-10 spec: wrote spec.md (prompt-only change to SYSTEM_ROLE + offline pytest). Awaiting Gate 1.
- 2026-07-10 GATE 1: approved by user. → code
- 2026-07-10 code: rewrote SYSTEM_ROLE in prompts.py (grounding, anchored rating+urgency, degenerate-input, injection resistance, language-agnostic). Interface unchanged. → tests
- 2026-07-10 tests: added milestone2/tests/{conftest.py,test_prompts.py} (11 offline tests). → verify
- 2026-07-10 verify: PASS — 11 passed. Wrote verification.md. Awaiting Gate 2.
- 2026-07-10 GATE 2: approved by user (Approve & push). → ship
- 2026-07-10 ship: committed d193153, pushed to origin. Run complete. → done
