---
id: "DAT-07"
question: "What is an offline-first application?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 264
editorial_status: "reviewed"
---

# DAT-07

## Original interview question

What is an offline-first application?

## What the interviewer evaluates

Define offline-first read/write paths, local truth, sync and conflict behavior.

## Explanation in Arabic

Offline-first يعني التطبيق يقدم وظيفة مفيدة من local data حتى لو الشبكة ضعيفة أو غايبة. UI تقرأ من Room كـlocal source of truth، والremote refresh تكتب فيها؛ writes تتسجل pending محليًا وتتصالح مع server لاحقًا. ده مش مجرد cache: لازم freshness, conflict policy, retry, process-death recovery وأمان البيانات يتحددوا بوضوح.

## Why it matters and how it works

The server remains authoritative for server-owned records, while the local database is authoritative for what UI currently displays. A sync worker drains durable pending operations with stable IDs. Version/cursor metadata handles out-of-order updates; the UI exposes stale/pending/error states rather than pretending all data is current.

## Worked example

Conceptual repository interfaces; app types are omitted because storage and server contracts are product-specific.

```kotlin
import kotlinx.coroutines.flow.Flow

interface OfflineNotes {
    fun observe(): Flow<List<Note>>
    suspend fun editLocally(id: String, text: String)
    suspend fun synchronizePending()
}
// editLocally commits Note plus pending operation in one local transaction.
```

## Trade-offs and decision criteria

Local-first reads improve startup and resilience but add sync complexity and storage/security responsibility. Network-first can be simpler for non-critical ephemeral data. Conflicts require domain rules: server-wins, merge, or user resolution, not a blanket last-write-wins assumption.

## Failure modes

If the app shows cached prices without a stale label, users can act on invalid terms. If a pending edit is not persisted before navigation, process death loses it. A retry without stable operation ID can apply the same write twice.

## Production perspective

A field-inspection app saves forms and attachments locally with Pending status, displays them immediately and uses WorkManager to sync. Server versions detect conflicts; the user gets a resolution screen where automatic merge is unsafe. Telemetry tracks pending age.

## Interview answer — short

“Offline-first reads from a local source of truth, persists user edits as pending operations, and synchronizes with server authority when possible. It must define freshness, conflicts and retry recovery, not merely cache responses.”

## Interview answer — structured

“I design the read and write paths separately. The UI observes Room so it can open instantly offline; refresh downloads versioned data and commits it to Room. A user edit is saved locally with a pending operation ID before the UI acknowledges it. WorkManager can send pending operations under network constraints, with idempotent server handling. I surface stale and pending status and choose conflict rules from the domain, because blindly overwriting local or remote data can lose user work.”

## Interview answer — deep senior

“Offline-first is an end-to-end consistency design. The local database is the UI’s current source, but the backend remains authoritative for shared data. I use stable IDs, server versions/cursors and transactional local writes so a user action and its pending sync record cannot diverge. Workers can retry after process death, which requires server idempotency and reconciliation of ambiguous responses. I explicitly model freshness and conflicts; text notes might merge or ask the user, while payment balances cannot be client-merged. I test airplane mode, reconnect, duplicate worker runs, out-of-order responses and app crashes at each state transition.”

## Deep-dive talking points

Draw local read, pending write and server reconciliation paths, including conflict decisions.

## Follow-up questions

- [DAT-15](../dat-15/): How sync offline edits? **Answer:** durable pending operations with stable IDs and conflict/version handling.
- [DAT-16](../dat-16/): Who resolves divergence? **Answer:** domain-specific version and merge policy.

## Self-check rubric

Can I name local and server authority, persist pending work and define freshness/conflict UX?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source and queued writes.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
