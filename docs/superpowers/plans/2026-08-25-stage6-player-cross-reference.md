# Stage 6 Player Cross-Reference Implementation Plan

> **Status: ✅ COMPLETED** — Delivered: `scripts/s6_01_cross_reference_player_schema.py`, `reports/stage6_player_cross_reference.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only Stage 6 utility that measures coverage between normalized player records and native evidence.

**Architecture:** Add one Python CLI script that loads Stage 5 normalized players and Stage 4 mapping data, flattens observed player fields, classifies each field into coverage buckets, and writes JSON/CSV/report artifacts.

**Tech Stack:** Python standard library only: `argparse`, `csv`, `json`, `collections`, and `pathlib`.

---

### Task 1: Red Test

**Files:**
- Create: `tests/stage6_cross_reference_assert.py`

- [ ] Add a command-level assertion script that runs Stage 6 on the Stage 5 fixture output and expects coverage counts.
- [ ] Run it before implementation and confirm it fails because `scripts/s6_01_cross_reference_player_schema.py` is missing.

### Task 2: Cross-Reference Script

**Files:**
- Create: `scripts/s6_01_cross_reference_player_schema.py`

- [ ] Load normalized players and Stage 4 key map.
- [ ] Flatten player sections into observed keys.
- [ ] Classify keys into `observed_with_offset`, `observed_without_offset`, `observed_unmapped`, and `native_unobserved`.
- [ ] Write JSON, CSV, and Markdown report outputs.

### Task 3: Verification

**Files:**
- Modify: `reports/stage6_player_cross_reference.md`

- [ ] Run `python -m py_compile .\scripts\s6_01_cross_reference_player_schema.py .\tests\stage6_cross_reference_assert.py`.
- [ ] Run `python .\tests\stage6_cross_reference_assert.py`.
- [ ] Confirm the report records the fixture coverage counts and keeps editor/patching out of scope.

### Self-Review

- Spec coverage: plan covers inputs, outputs, coverage buckets, read-only safety, and verification.
- Placeholder scan: no placeholder tasks remain.
- Type consistency: bucket names match the design and planned outputs.
