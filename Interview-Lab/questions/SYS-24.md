---
id: "SYS-24"
question: "How would you design for poor connectivity and intermittent power loss?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 353
editorial_status: "reviewed"
---

# SYS-24

## Original interview question

How would you design for poor connectivity and intermittent power loss?

## What the interviewer evaluates

Design for poor connectivity and intermittent power loss with durable state and honest UX.

## Explanation in Arabic

نتعامل مع network loss وpower/process death كحالة عادية: UI تقرأ local Room، writes تُقبل فقط بعد local transaction مع outbox ID، والworker تعيد المحاولة عند connectivity تحت قيود OS. server versions/idempotency تحمي من duplicate/out-of-order، وUI تعرض stale, pending, conflict, unknown بدل نجاح كاذب. نختبر kill عند كل boundary، low storage ووقت الجهاز الخاطئ.

## Why it matters and how it works

Use bounded local storage and cleanup that never deletes unacknowledged operations. Network timeouts create ambiguous remote outcomes; reconcile by stable ID. A battery/power loss can interrupt file/database migration or upload, so use transactional writes, checksums and resumable protocols. Cache TTL is domain-specific.

## Worked example

Conceptual persistent state model; implementation spans Room, WorkManager and server.

```kotlin
sealed interface SyncState {
    data object LocalPending : SyncState
    data object Sending : SyncState
    data object UnknownRemote : SyncState
    data class Confirmed(val version: String) : SyncState
    data class Conflict(val serverVersion: String) : SyncState
}
```

## Trade-offs and decision criteria

Offline-first adds storage and conflict complexity but preserves usefulness. A network-only app is simpler where offline action is not required. Background scheduling saves battery but may delay completion; product promises should describe Pending rather than exact time.

## Failure modes

A request can reach server before power loss; resending with new key duplicates write. Deleting cached rows before refresh creates blank offline UI. A partial file move can corrupt data without journal/verification. Unbounded retry can drain battery.

## Production perspective

A field inspection app saves forms/attachments locally, resumes uploads by acknowledged chunk, reconciles server status after restart and shows stale/pending badges. Support sees operation IDs; tests simulate airplane mode, force-stop, reboot, low battery and disk full.

## Interview answer — short

“I persist user intent before network work, render from local storage, use repeat-safe background sync and reconcile ambiguous server outcomes. UI distinguishes stale, pending and confirmed state; tests kill the app at each transition.”

## Interview answer — structured

“Poor connectivity changes the architecture. The UI should work from a local source of truth and label stale data. An edit commits to Room with an outbox row before the user sees Saved; WorkManager later syncs under network constraints. Each operation has a stable ID, and the backend enforces idempotency and versions. A timeout becomes Unknown until status reconciliation. For large uploads, I persist server-acknowledged offsets. I test process death, power loss and disk-full behavior as normal paths rather than exceptional afterthoughts. Offline-first adds storage and conflict complexity but preserves usefulness. A network-only app is simpler where offline action is not required. Background scheduling saves battery but may delay completion; product promises should describe Pending rather than exact time. A field inspection app saves forms/attachments locally, resumes uploads by acknowledged chunk, reconciles server status after restart and shows stale/pending badges.”

## Interview answer — deep senior

“I design around crash consistency. Every accepted user action has a durable local record and operation identity; no in-memory coroutine is the only copy. Remote calls can commit while responses are lost, so retries use the same key and query authoritative status. Room transactions protect local invariants, WorkManager supplies restartable attempts under flexible OS timing, and server versions resolve conflicts. Cached data has freshness metadata, and UI never labels an uncertain payment or sync as success. Large files use resumable chunks and verified offsets. I bound queues/retries to protect disk and battery, test kill/reboot/airplane mode at every state transition and monitor oldest Pending age. Use bounded local storage and cleanup that never deletes unacknowledged operations. Network timeouts create ambiguous remote outcomes; reconcile by stable ID. A battery/power loss can interrupt file/database migration or upload, so use transactional writes, checksums and resumable protocols. A request can reach server before power loss; resending with new key duplicates write. Deleting cached rows before refresh creates blank offline UI. A partial file move can corrupt data without journal/verification. Unbounded retry can drain battery. A field inspection app saves forms/attachments locally, resumes uploads by acknowledged chunk, reconciles server status after restart and shows stale/pending badges. Support sees operation IDs; tests simulate airplane mode, force-stop, reboot, low battery and disk full.”

## Deep-dive talking points

Trace power loss before/after local commit, remote commit and acknowledgement.

## Follow-up questions

- [DAT-07](../dat-07/): What is offline-first? **Answer:** local read and durable write paths with sync/conflict policy.
- [BG-08](../bg-08/): How retry after exit? **Answer:** WorkManager drains persisted outbox under constraints.

## Self-check rubric

Can I preserve accepted intent, reconcile unknown outcome and test power-loss windows?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source and sync.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable work.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
