---
id: "FLO-28"
question: "A flow combines cached Room data with remote refresh. Who is source of truth?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 141
editorial_status: "reviewed"
---

# FLO-28

## Original interview question

A flow combines cached Room data with remote refresh. Who is source of truth?

## What the interviewer evaluates

Design offline-first cache plus remote refresh with one local source of truth.

## Explanation in Arabic

لو Room data مع remote refresh، الـUI تقرأ من Room Flow كمصدر محلي للحقيقة المعروضة. الـrefresh تجيب remote ثم تكتب Room داخل transaction؛ Room تطلع snapshot جديدة. ما نعملش `combine` مباشر لقائمتين مختلفتين ونخلي UI تخمّن مين الأصح. السيرفر يفضل authoritative لبياناته، ومع النزاعات نحتاج version/ETag وقواعد merge محددة.

### Practical walkthrough in Egyptian Arabic

في offline-first list، Room هي source of truth المعروضة؛ remote refresh تجيب data وتكتبها transaction في Room، وبعدها Room Flow تصدر snapshot جديدة. لو UI جمعت remote response مباشرة وفي نفس الوقت Room، ممكن تعرض ترتيبين أو data قديمة. احتفظ بـsync status منفصلة، وحدد conflict policy ووقت refresh. اختبر offline ثم reconnect.

## Why it matters and how it works

Expose `Flow<List<Entity>>` from DAO and a separate suspend refresh/sync operation. The network response is validated and committed transactionally before UI observes it. Offline writes need queued operations and conflict resolution. Stale state should carry freshness metadata, not silently masquerade as current.

## Worked example

Conceptual Android repository; DAO and API are app-owned types. Room transaction is required around related table updates.

```kotlin
import kotlinx.coroutines.flow.Flow

class FeedRepository(private val dao: FeedDao, private val api: FeedApi) {
    val items: Flow<List<FeedItem>> = dao.observeItems()
    suspend fun refresh() {
        val remote = api.fetchItems()
        dao.replaceAllTransactionally(remote)
    }
}
```

## Trade-offs and decision criteria

Local source gives immediate offline rendering and a single UI path, but may be stale. Remote-only rendering can show fresh data sooner but complicates consistency/offline behavior. Define TTL, invalidation, conflicts and errors; never overwrite pending local edits blindly.

## Failure modes

Combining cached and remote lists without a merge rule can duplicate or revert items. A network timeout after a server write leaves uncertain status. If refresh replaces Room in multiple non-transactional steps, UI can observe an inconsistent partial snapshot.

## Production perspective

A messaging inbox observes Room and runs a worker to fetch updates. Rows have server IDs and versions; transaction applies a consistent batch. UI marks stale/offline state, while queued outgoing messages have stable operation IDs and reconciliation.

## Interview answer — short

“The UI should observe one local source of truth, usually Room. Remote refresh validates data and updates the database transactionally; Room emits new snapshots. I define freshness and conflict rules because a Flow combine cannot invent consistency.”

## Interview answer — structured

“For an offline-first screen, I expose a Room Flow as the UI data source and run remote refresh separately. Successful network responses are validated and committed in a database transaction; collectors then receive the updated local snapshot. The server remains authoritative for server-owned fields, while the local database owns the displayable offline snapshot. I include freshness/error state so cached data is not mistaken for current data, and I plan how pending local edits and conflicts are resolved.”

## Interview answer — deep senior

“I avoid a dual-source UI where cached and remote lists race each other. Room is the single local source consumed by the screen, and refresh is a side operation that writes a versioned batch into it. That makes rotation and offline startup deterministic. Server authority and client display state are different: remote version/ETag and operation IDs govern merge and conflict decisions. I perform related updates in one transaction, preserve pending local writes, and surface stale status when refresh fails. For process death, a durable worker resumes sync; for repeated network writes, the backend deduplicates logical operations. Tests cover offline startup, stale cache, out-of-order refresh, conflict and crash during batch apply. I would make the read path unambiguous: the UI observes Room, and a refresh operation updates Room from the server. That makes local storage the immediate source of truth for display and supports offline rendering. The server may remain authoritative for business rules, so conflict resolution and freshness policy are still explicit. I do not emit a remote list directly to the UI while also collecting cached rows, because the two paths can disagree and flicker. I model refresh status separately from content and persist writes transactionally. When the network fails, cached data remains visible with a stale or error indicator rather than becoming an empty screen. I test offline launch, refresh, conflict, and process restart.”

## How to answer in the interview

- **Why:** two read paths create inconsistent UI.
- **How:** refresh remote into Room, then observe Room Flow.
- **Trade-off:** stale cache needs freshness and conflict policy.
- **Failure case:** direct remote emission fights cached state.
- **Production solution:** offline/reconnect and transaction tests.

## Deep-dive talking points

Draw network-to-Room-to-UI flow; distinguish local display truth from server authority and pending writes.

## Follow-up questions

- [FLO-13](../flo-13/): Can combine ensure consistency? **Answer:** no, it only pairs latest emissions.
- [COR-30](../cor-30/): How resume refresh after process death? **Answer:** persist work intent and schedule restartable sync.

## Self-check rubric

Can I name one UI source, transact updates, expose staleness and resolve conflicts?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth and sync.
- [Android Flow guide](https://developer.android.com/kotlin/flow) — DAO stream use.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
