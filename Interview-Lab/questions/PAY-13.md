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

## Practical walkthrough

الترتيب الصح: timeout event يدخل use case، DB transaction تحفظ `Unknown` وreversal obligation لو القواعد تطلبها، وبعد commit الـUI تتنقل. لو navigation حصلت قبل commit، Activity تختفي ومعاها coroutine ويمكن الالتزام يضيع. worker من DB، وstartup scan يصلح missed scheduling.

## Why it matters and how it works

Activity lifecycle is too short for financial obligations. A repository transaction establishes durable state and outbox identity before emitting navigation. WorkManager or a terminal service resumes processing after process death, while backend/provider deduplicates repeated sends.

## Worked example

Timeout event enters `resolveTimeout(operationId)`. The use case first records Unknown and, if protocol rules require it, a reversal intent atomically. Only after transaction success does StateFlow expose “pending reversal” and allow navigation. A startup scan repairs missed worker scheduling.

### Kotlin/Android sketch

```kotlin
// Inside repository; returns only after local obligation commits.
suspend fun onTimeout(operationId: String): PaymentState = db.withTransaction {
    val attempt = attempts.get(operationId)
    if (attempt.state.isFinal) return@withTransaction attempt.state
    attempts.markUnknown(operationId)
    if (protocol.requiresReversal(attempt)) {
        reversals.insertIfAbsent(attempt.stableReversalIntent())
    }
    PaymentState.Unknown
}
// Imports: androidx.room.withTransaction. Network send happens after commit.
// isFinal/stableReversalIntent and DAOs are app-defined.
// UI can navigate after this suspend function completes.
```

## Trade-offs and decision criteria

Waiting for a durable DB commit slightly delays navigation, which is acceptable for preserving obligation. Enqueueing only a WorkManager request without domain state may not capture original references or guarantee consistent status.

## Failure modes

Coroutine launched in `lifecycleScope` is canceled when the Activity exits before enqueue. Moving it to `viewModelScope` still fails on process death. Persist state before UI completion and test kill between every line.

## Production perspective

Tests assert no navigation completion before DB commit, that reboot resumes the outbox, and that duplicate timeout callbacks create one reversal row. Metrics alert on aging pending reversals.

## Interview answer — short

“I move timeout handling into a repository transaction and expose the next UI state only after the reversal obligation is committed. Navigation is an observer of durable progress, not the owner of the reversal.”

## Interview answer — structured

“I move financial state transitions out of the Activity. On timeout the use case writes Unknown or ReversalPending and inserts the outbox intent in one database transaction. Only after commit does it emit a UI state that may navigate away. A durable worker processes the row and the backend/provider handles repeated delivery. `lifecycleScope` or even `viewModelScope` is not enough across process death. A failed local transaction means the UI cannot claim the reversal was queued.”

## Interview answer — deep senior

“I would draw the sequence and place the irreversible UI exit after a durable commit. The repository owns original transaction identity, guarded state transitions and reversal outbox uniqueness; the UI observes state but cannot erase obligations. Worker scheduling is repairable from the DB on startup, because enqueue itself may race with a crash. The remote reversal can be sent more than once after lost acknowledgment, so I preserve stable identity and reconcile. Tests kill the process before commit, after commit, after send and before confirmation, and assert one business reversal intent survives. Timeout event enters `resolveTimeout(operationId)`. Metrics alert on aging pending reversals. I test the exact crash boundary between timeout notification and navigation to prove the obligation survives. I make the timeout handler call a use case that owns the database transaction. It records Unknown and, only if the acquirer protocol requires it, inserts a reversal intent with a stable identity. Only after commit does it publish a state from which the Activity may navigate away. Worker scheduling occurs afterward, and a startup scan handles the small window where the database committed but enqueue was missed. If the transaction fails, the UI cannot claim the obligation was queued; it should show a recoverable error and keep the operation visible. I test a process kill before commit, after commit, and after send but before acknowledgment to prove the order is safe.”

## How to answer in the interview

- **Why:** Activity lifetime is shorter than a financial obligation.
- **How:** commit state and outbox before emitting a navigation-ready state.
- **Trade-off:** the UI may wait for a small local commit before exiting.
- **Failure case:** handler navigates away before queue insertion.
- **Production solution:** repository ownership, worker from durable rows, and crash-window tests.

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
