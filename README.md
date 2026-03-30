# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Recent improvements make scheduling more reliable and easier to maintain:

- Faster task repository lookups by storing tasks by `task_id` internally
- More consistent update behavior when task IDs change
- Cleaner repository method documentation for easier onboarding and debugging
- Existing scheduling behavior preserved and verified by passing tests

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

These tests cover core scheduler behavior, including:

- Sorting correctness (tasks ordered by time and deterministic tie-breakers)
- Recurrence logic (daily and weekly task completion creating follow-up instances)
- Conflict detection (overlapping tasks and duplicate start times)
- Filtering and repository behavior (pet/category/due-date filtering and task storage updates)

Confidence Level: ★★★★☆ (4/5)

Rationale: Unit tests are currently passing in the project environment (15 passed), and they validate key scheduling paths and common edge cases. Remaining risk is primarily around integration with the Streamlit UI and real user input flows.
