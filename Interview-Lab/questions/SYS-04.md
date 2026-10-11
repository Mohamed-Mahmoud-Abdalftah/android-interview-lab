---
id: "SYS-04"
question: "Design an offline-first system with a local source of truth."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 333
editorial_status: "reviewed"
---

# SYS-04

## Original interview question

Design an offline-first system with a local source of truth.

## What the interviewer evaluates

Design offline-first system around local SSOT, versioned sync and durable outbox.

## Explanation in Arabic

نخلي UI تقرأ من Room فقط، والremote sync تحدّث Room transactionally؛ ده يمنع cache وnetwork يتسابقوا على الشاشة. المستخدم يعدّل offline فنحفظ row + outbox operation مع stable ID وbase version في transaction. WorkManager يرسلها لاحقًا، backend يعمل deduplication وversion conflict، وUI تعرض stale/pending/conflicted. لازم نحدد policy لكل domain بدل last-write-wins عمياء.

## Why it matters and how it works

The local database is the UI source, while backend is authoritative for shared state. Sync uses cursors/ETags, transactional page application and outbox IDs. Worker repeats are expected, so server idempotency and status lookup protect writes. Session logout partitions/clears data under privacy requirements.

## Worked example

Conceptual data-flow contract; actual Room/worker types are application-specific.

```kotlin
// UI <- Room Flow <- Repository
// Remote refresh -> validate version -> Room transaction
// User edit -> Room row + outbox transaction -> WorkManager
// Worker -> server with stable operation ID -> acknowledge/resolve conflict
```

## Trade-offs and decision criteria

Offline-first improves resilience and startup but costs schema, conflict UX and storage management. Network-only is simpler when offline is not a requirement. Cache freshness and action safety vary by domain: stale articles can display, stale payment status cannot authorize a new charge.

## Failure modes

Writing local edit without an outbox row loses sync intent. Clearing Room before successful refresh causes blank UI. Retrying a write with new ID can duplicate effects. An old response arriving late can overwrite newer server version.

## Production perspective

A field service app stores forms, photos and outbox rows locally, syncs when constraints allow and shows Pending/Conflict badges. Server assigns versions and provides status; metrics track oldest pending and conflict rate.

## Interview answer — short

“I use Room as the UI source of truth, remote sync as a transactional writer, and a durable outbox for offline edits. Server versions and idempotency resolve retries and conflicts, while UI makes stale and pending states visible.”

## Interview answer — structured

“For offline-first design I separate read and write paths. UI observes Room, so startup works without network. A refresh downloads versioned data and commits it transactionally; it never races a separate network list directly into UI. Edits commit locally with a pending operation ID, and WorkManager later sends them under a server idempotency contract. Conflicts use versions and a domain-specific merge or user decision. The UI labels stale data and pending writes instead of pretending the network is always current. Offline-first improves resilience and startup but costs schema, conflict UX and storage management. Network-only is simpler when offline is not a requirement. Cache freshness and action safety vary by domain: stale articles can display, stale payment status cannot authorize a new charge.”

## Interview answer — deep senior

“I start with authority: Room owns the currently rendered snapshot, while the backend owns shared business truth. A sync engine applies server changes by cursor/version in database transactions, preserving pending edits. Each local edit and outbox record commits together, then a repeat-safe worker sends under a stable ID and reconciles ambiguous responses. Conflict policy depends on data—notes may merge, balances must follow server ledger. Cache TTL and reconnect refresh define freshness; account partitioning and backup policy protect privacy. I test offline startup, out-of-order pages, duplicate worker runs, lost responses, process death after each commit and conflicts from another device. Observability tracks pending age, stale age and sync failure classification. The local database is the UI source, while backend is authoritative for shared state. Sync uses cursors/ETags, transactional page application and outbox IDs. Worker repeats are expected, so server idempotency and status lookup protect writes. Session logout partitions/clears data under privacy requirements. Writing local edit without an outbox row loses sync intent. Clearing Room before successful refresh causes blank UI. Retrying a write with new ID can duplicate effects. An old response arriving late can overwrite newer server version. A field service app stores forms, photos and outbox rows locally, syncs when constraints allow and shows Pending/Conflict badges.”

## Deep-dive talking points

Draw both data paths and the local/remote authority boundary.

## Follow-up questions

- [DAT-07](../dat-07/): What makes it offline-first? **Answer:** local reads plus durable writes and sync/conflict policy.
- [SYS-06](../sys-06/): How combine pagination? **Answer:** Room PagingSource and RemoteMediator with atomic remote keys.

## Self-check rubric

Can I choose SSOT, handle pending writes, version conflicts and process death?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source and sync.
- [Android task scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — restartable work.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
