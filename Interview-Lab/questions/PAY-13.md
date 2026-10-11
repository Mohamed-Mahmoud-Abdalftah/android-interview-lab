---
id: "PAY-13"
question: "A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 483
editorial_status: "reviewed"
---

# PAY-13

## Original interview question

A timeout handler exits the UI before enqueueing a reversal. How do you redesign ownership and ordering?

## What the interviewer evaluates

- Ownership of timeout/reversal beyond an Activity lifecycle.
- Ordering of durable intent before UI exit.

## Explanation in Arabic

لو timeout handler يقفل UI قبل ما يضيف reversal للqueue، process death أو navigation ممكن يضيّع الالتزام المالي. نخلي repository/use case يملك state: في DB transaction يغيّر payment لـ`REVERSAL_PENDING` ويكتب outbox row، وبعد commit يطلع state للـUI فتقدر تقفل. Worker مستقل عن Activity يرسل ويؤكد. UI مجرد observer.

## Why it matters and how it works

Activity lifecycle is too short for financial obligations. A repository transaction establishes durable state and outbox identity before emitting navigation. WorkManager or a terminal service resumes processing after process death, while backend/provider deduplicates repeated sends.

## Worked example

Timeout event enters `resolveTimeout(operationId)`. The use case first records Unknown and, if protocol rules require it, a reversal intent atomically. Only after transaction success does StateFlow expose “pending reversal” and allow navigation. A startup scan repairs missed worker scheduling.

## Trade-offs and decision criteria

Waiting for a durable DB commit slightly delays navigation, which is acceptable for preserving obligation. Enqueueing only a WorkManager request without domain state may not capture original references or guarantee consistent status.

## Failure modes

Coroutine launched in `lifecycleScope` is canceled when the Activity exits before enqueue. Moving it to `viewModelScope` still fails on process death. Persist state before UI completion and test kill between every line.

## Production perspective

Tests assert no navigation completion before DB commit, that reboot resumes the outbox, and that duplicate timeout callbacks create one reversal row. Metrics alert on aging pending reversals.

## Interview answer — short

“The payment repository owns timeout and reversal, not the screen. It atomically persists status and reversal intent before notifying UI to exit; durable background processing and reconciliation finish the obligation.”

## Interview answer — structured

“I move financial state transitions out of the Activity. On timeout the use case writes Unknown or ReversalPending and inserts the outbox intent in one database transaction. Only after commit does it emit a UI state that may navigate away. A durable worker processes the row and the backend/provider handles repeated delivery. `lifecycleScope` or even `viewModelScope` is not enough across process death.”

## Interview answer — deep senior

“I would draw the sequence and place the irreversible UI exit after a durable commit. The repository owns original transaction identity, guarded state transitions and reversal outbox uniqueness; the UI observes state but cannot erase obligations. Worker scheduling is repairable from the DB on startup, because enqueue itself may race with a crash. The remote reversal can be sent more than once after lost acknowledgment, so I preserve stable identity and reconcile. Tests kill the process before commit, after commit, after send and before confirmation, and assert one business reversal intent survives.”

## Deep-dive talking points

Prompt for Activity lifecycle limit, DB-before-navigation ordering, outbox scan and duplicate timeout race.

## Follow-up questions

- [PAY-06](../pay-06/): Which writes are atomic? **Answer:** payment state and reversal intent.
- [PAY-07](../pay-07/): What restarts delivery? **Answer:** durable queue plus worker/startup scan.

## Self-check rubric

Can I identify the race and reassign ownership to durable domain state?

## References and reviewed-on date

- [Android lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — scope lifetimes.
- [Android WorkManager overview](https://developer.android.com/topic/libraries/architecture/workmanager) — persistent work.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
