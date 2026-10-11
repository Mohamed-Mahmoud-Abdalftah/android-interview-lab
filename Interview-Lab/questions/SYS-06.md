---
id: "SYS-06"
question: "Design caching, pagination, and remote synchronization."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 335
editorial_status: "reviewed"
---

# SYS-06

## Original interview question

Design caching, pagination, and remote synchronization.

## What the interviewer evaluates

Combine cache, Paging 3 and remote sync with stable keys and freshness.

## Explanation in Arabic

نستخدم Room كـlocal SSOT، `PagingSource` منها تعرض صفحات فورًا، و`RemoteMediator` يجيب صفحات server ويكتب rows + cursor keys transactionally. cache policy تحدد TTL/stale indicator ووقت refresh، وoutbox منفصلة للlocal writes. لازم server pagination contract يكون stable (cursor/version)، وإلا offset مع feed متغير يكرر/يسقط عناصر.

## Why it matters and how it works

PagingData is a UI window over local rows, not a substitute for sync correctness. RemoteMediator handles REFRESH/APPEND and invalidates Room source via committed changes. Version checks reject out-of-order refresh. WorkManager can prefetch, while UI on-demand loads remain responsive.

## Worked example

Conceptual Kotlin graph; types are app-owned except Paging APIs.

```kotlin
// Backend cursor pages -> RemoteMediator
// RemoteMediator -> Room transaction(items + remoteKeys)
// Room PagingSource -> Pager.flow -> ViewModel.cachedIn(viewModelScope)
// UI renders cached rows and load/freshness state.
```

## Trade-offs and decision criteria

Local-first paging gives instant offline scrolling but adds key schema and migration complexity. Network-only PagingSource is simpler if offline is unnecessary. Prefetch uses battery/data and should respect constraints. Cache invalidation must preserve pending user edits.

## Failure modes

Clearing rows before successful refresh produces blank UI. Storing remote keys after rows in a separate transaction can repeat pages after crash. A late stale response can overwrite newer content. Treating load error as a reason to delete cache harms offline UX.

## Production perspective

A news/social feed opens from Room, refreshes pages by opaque cursor, marks stale age and uses stable article IDs. Sync writes server versions; WorkManager prefetches only under acceptable network constraints. Tests cover reordering, cursor expiry, offline restart and duplicate page.

## Interview answer — short

“I use Room as the UI source, PagingSource for bounded local pages and RemoteMediator for remote pages and keys in one transaction. A versioned cache policy exposes staleness, and outbox handles writes separately.”

## Interview answer — structured

“The architecture has one render path: Room PagingSource to Pager to UI. RemoteMediator fetches pages and stores rows plus remote keys atomically, so a failed network refresh leaves cached content intact. Server cursors and stable IDs handle insertions/reordering better than naive offsets. I attach fetched/version metadata and show stale or load-error state. For user edits I use a separate durable outbox and conflict policy rather than letting a page refresh overwrite pending changes.”

## Interview answer — deep senior

“I would first negotiate backend pagination semantics: opaque cursors, snapshot versions or stable ordering. Without that, no client operator can prevent duplicate/skipped items in a changing feed. Locally, Room is the display source; `RemoteMediator` owns fetch and transactional item/key updates, and PagingSource invalidation updates the UI. Refresh policy uses TTL, conditional requests and explicit stale indicators, while failed refresh preserves old rows. Pending local writes are partitioned from server-owned fields and reconciled by version. I test APPEND after new top insertions, duplicate pages, cursor invalidation, process death between fetch/commit and offline startup. I measure first-content latency, cache hit rate and data usage. Version checks reject out-of-order refresh.”

## Deep-dive talking points

Trace page key lifecycle and distinguish UI windowing from sync correctness.

## Follow-up questions

- [DAT-13](../dat-13/): What does RemoteMediator do? **Answer:** fetch and persist remote pages/keys.
- [DAT-17](../dat-17/): How judge freshness? **Answer:** domain TTL plus server validators and invalidation triggers.

## Self-check rubric

Can I preserve cache on error, store keys atomically and handle changing server order?

## References and reviewed-on date

- [Android Paging network/database](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — mediator architecture.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
