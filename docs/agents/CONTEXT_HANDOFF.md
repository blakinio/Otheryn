# Agent Context Handoff

## Principle

Chat history is disposable. Git state, the active task checkpoint, the live PR and deterministic validation evidence are durable state. A continuation agent must be able to resume without reading the previous conversation.

## Portable continuation flow

For every substantial task:

1. Keep one compact `## Context checkpoint` in the active task record.
2. Update it after material discoveries, file changes, validation/CI changes, branch/head/PR changes, blockers, and before session replacement.
3. Validate it with `python tools/agents/checkpoint.py <task-path> --require-checkpoint`.
4. Generate the next-agent prompt with `python tools/agents/resume.py --task <task-path>`.
5. The next agent verifies only live state that can invalidate `next_action`, then continues from that action.

Do not pass the previous chat transcript to the next agent.

## Checkpoint schema

Use checkpoint version 1 with: `updated_at`, `head`, `branch`, `pr`, `status`, `context_routes`, `owned_paths`, `proven`, `derived`, `unknown`, `conflicts`, `first_failure`, `rejected_hypotheses`, `changed_paths`, `validation`, `blockers`, and exactly one concrete `next_action`.

Validation results are `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Evidence states are `PROVEN`, `DERIVED`, `UNKNOWN`, and `CONFLICT`.

## Resume contract

The generated prompt carries only the checkpoint evidence needed to continue. Do not repeat a full preflight when checkpoint and live state agree. Re-run broad discovery only after material external state change, long interruption/session replacement, or evidence that durable state conflicts with live state.

## Anti-bloat

Do not put full logs, full diffs, whole source files, old chat transcripts, repeated CI history, whole-repository inventories, or superseded hypotheses into checkpoints or resume prompts. `tools/agents/checkpoint.py` enforces compactness ceilings.

## Handoff quality gate

The next agent must know the current branch/head/PR, evidence state, first failure, changed paths, validation, blockers, and the single next action without asking the previous agent.
