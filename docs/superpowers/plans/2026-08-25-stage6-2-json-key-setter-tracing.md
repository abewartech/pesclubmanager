# Stage 6.2 JSON Key-To-Setter Tracing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only Stage 6.2 static mapper that correlates player JSON keys with native field candidates, setters, offsets, and confidence scores.

**Architecture:** Add one Python CLI that joins existing Stage 4 artifacts. It extracts `PrepareDataFromJson*` addresses from key records, indexes native offset metadata, emits JSON/CSV/new-field reports, and documents confidence without claiming unavailable runtime or hook evidence.

**Tech Stack:** Python standard library only: `argparse`, `csv`, `json`, `re`, `collections`, and `pathlib`.

---

### Task 1: Red Assertion

**Files:**
- Create: `tests/stage6_2_json_key_mapping_assert.py`

- [ ] Write a command-level test that expects the Stage 6.2 script to produce `player_json_key_mapping.json`.
- [ ] Run it before implementation and confirm it fails because the script is missing.

### Task 2: Static Mapper

**Files:**
- Create: `scripts/s6_02_trace_json_key_setters.py`

- [ ] Load Stage 4 JSON key records, Stage 4 key/offset map, and offset metadata.
- [ ] Resolve `PrepareDataFromJson*` addresses from key records.
- [ ] Derive setter names from offset metadata when writes are available.
- [ ] Score confidence as `HIGH`, `MEDIUM`, `LOW`, or `UNKNOWN`.
- [ ] Write requested Stage 6 outputs.

### Task 3: Report And Verification

**Files:**
- Create: `reports/stage6_json_key_mapping_report.md`

- [ ] Run py_compile for the script and assertion file.
- [ ] Run the assertion script.
- [ ] Run the Stage 6.2 mapper.
- [ ] Confirm outputs are read-only analysis artifacts.

### Self-Review

- Spec coverage: covers requested Stage 6.2 artifacts, confidence scoring, and static-only scope.
- Placeholder scan: no unresolved implementation placeholders remain.
- Type consistency: output filenames and confidence names match the design.
