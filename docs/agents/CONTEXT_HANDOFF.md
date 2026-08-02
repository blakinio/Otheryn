# Agent Context Handoff

## Principle

Chat history is disposable. Git state, the active task checkpoint, the live PR, and deterministic validation evidence are durable state.

A continuation agent must be able to resume without reading the previous conversation.

## Contract revision

Checkpoint structure remains version 1. Policy revision 2 is backward-compatible and adds task statuses `waiting` and `completed`, validation result `NOT_APPLICABLE`, and a formal distinction between task status and terminal invocation result. Existing valid version 1 checkpoints remain valid.

Checkpoint task statuses:

```text
investigating | implementing | validating | ready | waiting | blocked | completed
```

Terminal invocation results:

```text
DONE | WAITING | BLOCKED | ROTATE
```

`ROTATE` is never a task status. Before returning it, persist `ready`, `waiting`, or `blocked` with one concrete `next_action`.

## Portable continuation flow

For every substantial task:

1. Keep one compact `## Context checkpoint` in the active task record.
2. Update it after material discoveries, file changes, validation or CI changes, branch, head or PR changes, blockers, and before session replacement.
3. Validate it with `python tools/agents/checkpoint.py <task-path> --require-checkpoint`.
4. Generate the next-agent prompt with `python tools/agents/resume.py --task <task-path>`.
5. The next agent verifies only live state that can invalidate `next_action`, then continues from that action.

Do not pass the previous chat transcript to the next agent.

## Checkpoint schema

```yaml
checkpoint_version: 1
updated_at: YYYY-MM-DDTHH:MM:SSZ
head: <commit-sha-or-UNKNOWN>
branch: <branch>
pr: <number-or-none>
status: investigating|implementing|validating|ready|waiting|blocked|completed
context_routes:
  - <task-relevant route or none>
owned_paths:
  - <path/glob>
proven:
  - <fact backed by source/tool/test evidence>
derived:
  - <explicit conclusion derived from proven facts>
unknown:
  - <unresolved fact>
conflicts:
  - <authoritative evidence conflict>
first_failure:
  marker: <first unmet invariant/check or none>
  evidence: <artifact/log/test/source reference or none>
rejected_hypotheses:
  - <hypothesis>: <disproving evidence>
changed_paths:
  - <path>
validation:
  - command: <command/workflow/job>
    result: PASS|FAIL|BLOCKED|NOT_RUN|NOT_APPLICABLE
    evidence: <short reference; concrete reason required for NOT_APPLICABLE>
blockers:
  - <blocker or none>
next_action: <exactly one concrete next step>
```

Use `waiting` for an external event with no active worker, `blocked` for a real decision, permission, safety, resource, or exhausted-repair barrier, `ready` when a fresh session can execute `next_action`, and `completed` only after closeout gates pass.

Omit irrelevant historical detail. Keep exact references instead of chronological narration.

## Resume contract

The generated resume prompt carries only task and checkpoint identity, branch, head, PR, status, evidence states, first failure, changed paths, validation, blockers, one `NEXT_ACTION`, and compact operating rules.

The continuation agent must not repeat a full preflight when the checkpoint agrees with current live state. Re-run broad discovery only after a material external state change, a long interruption or session replacement, or evidence that durable state conflicts with live state.

## Anti-bloat

Do not put full logs, full diffs, whole source files, old chat transcripts, repeated CI history, whole-repository inventories, or superseded hypotheses into checkpoints or resume prompts.

`tools/agents/checkpoint.py` enforces compactness ceilings. Collapse superseded history into the current conclusion and exact evidence reference.

## Handoff quality gate

A handoff is complete only when the next agent can answer without asking:

- Which branch, head, and PR are current?
- What is proven, derived, unknown, or conflicting?
- What failed first, if anything?
- Which paths changed?
- What validation ran and what was the result?
- What task status applies?
- What blocker remains?
- What is the single next action?
