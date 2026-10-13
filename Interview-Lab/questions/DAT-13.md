---
id: "DAT-13"
question: "How would you implement Paging 3 and RemoteMediator?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 270
editorial_status: "reviewed"
---

# DAT-13

## Original interview question

How would you implement Paging 3 and RemoteMediator?

## What the interviewer evaluates

Design Paging 3 with Room source, RemoteMediator keys and refresh transaction.

## Explanation in Arabic

`Paging 3` تقسم البيانات صفحات بدل تحميل feed كله. للـoffline-first، `Pager` يستخدم Room `PagingSource` للـUI، و`RemoteMediator` يقرر متى يجيب صفحات من API ويكتب rows وremote keys في Room transaction. UI ما تعرضش response network مباشرة؛ Room تفضل source. لازم نميز REFRESH/APPEND/PREPEND، endOfPagination، invalidation، وأخطاء load state.

## Why it matters and how it works

RemoteMediator coordinates remote load with local database; stable item IDs and remote keys/cursors prevent duplicate or missing pages. On REFRESH decide whether to clear/replace within a transaction while preserving user-owned pending edits. `cachedIn(viewModelScope)` shares PagingData across configuration changes within ViewModel lifetime.

## Worked example

Conceptual Android Paging repository; FeedDao and FeedMediator are app types, and page size is illustrative.

```kotlin
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import kotlinx.coroutines.flow.Flow

fun feed(dao: FeedDao, mediator: FeedMediator): Flow<PagingData<FeedItem>> =
    Pager(
        config = PagingConfig(pageSize = 30),
        remoteMediator = mediator,
        pagingSourceFactory = { dao.pagingSource() },
    ).flow
```

## Practical walkthrough

Paging 3 مع Room: UI تقرأ `PagingSource` من DAO، و`RemoteMediator` يجيب pages من server ويكتب rows + remote keys في DB transaction. `REFRESH` لازم يحدد هل يمسح cache الحالية أو يحتفظ بيها لو fetch فشل؛ امسح فقط بعد success حسب policy. `APPEND` استخدم cursor/keys stable، واحمي من duplicate pages عبر primary key/upsert مناسب. لو feed بتتغير كتير، offset pagination ممكن تفوّت/تكرر عناصر؛ server cursor/snapshot يساعد. `loadState` يميز loading/error/end، والـcached rows تفضل ظاهرة offline. اختبر empty page، duplicate IDs، process restart، وrefresh مع pending edits.

## Trade-offs and decision criteria

Paging controls memory/network demand but adds remote-key and invalidation complexity. A network-only PagingSource may be simpler for ephemeral data; Room plus mediator is preferable when offline startup and a single local truth matter.

## Failure modes

Using offset keys on a changing server list can duplicate/skip items; cursor/version contracts are safer. Clearing tables outside a transaction can flash empty UI. An error load state must offer retry without wiping cached rows.

## Production perspective

A news app opens cached Room articles instantly, appends pages via server cursor, and commits rows plus keys together. Refresh labels stale data until successful; tests cover offline startup, repeated APPEND and reordered server items.

## Interview answer — short

“Paging 3 loads bounded pages. For offline-first I use Room as PagingSource and RemoteMediator to fetch and transactionally store remote pages and keys. UI reads Room, and I handle load states, stable IDs and refresh carefully.”

## Interview answer — structured

“A Pager produces PagingData. If offline support matters, Room supplies the PagingSource and a RemoteMediator fetches from the API when needed, then writes entities and remote keys in one transaction. That keeps the UI’s source of truth local. I define REFRESH and APPEND behavior, use server cursor/version semantics rather than fragile offsets on changing feeds, and surface loading/error states with retry. `cachedIn(viewModelScope)` helps avoid repeating paging work across ordinary configuration changes.”

## Interview answer — deep senior

Paging is a consistency problem as well as a memory optimization. The mediator needs a stable pagination contract from the backend, preferably opaque cursors or versions. On refresh, replacing rows and keys must be atomic; on append, duplicate page delivery should be harmless through stable primary keys. I preserve offline cached rows if a network refresh fails and do not erase pending user edits. The UI observes Room PagingData and displays load state separately. I test empty pages, duplicated cursors, reordered items, app restart, offline mode and cancellation. A network-only source is acceptable when offline persistence is not required, but it does not meet an instant offline feed requirement.

I treat Paging as a persistence and consistency design, not just a RecyclerView optimization. The UI pages from Room; RemoteMediator fetches from the network and writes items plus remote keys to that database. A refresh should not clear last-good data before a failed request, and appends should tolerate duplicate delivery through stable keys. For a changing news feed I prefer cursor or snapshot semantics over naive offsets, subject to the backend contract. I store rows and keys in one local transaction, expose load states, and keep cached content available offline. I test empty and duplicate pages, scrolling after refresh, and process restart before trusting pagination behavior.

## How to answer in the interview

- **Why:** Large feeds need bounded loading with consistent cached pages.
- **How:** Room PagingSource reads; RemoteMediator fetches and transacts rows/keys.
- **Trade-offs:** Choose cursor/snapshot semantics for changing lists when available.
- **Failure cases:** Erasing cache on failed refresh or duplicate/shifted pages.
- **Production solution:** Test load states, restart, empty pages and offline scroll.

## Deep-dive talking points

Trace REFRESH/APPEND, key storage, cursor stability and cached failure behavior.

## Follow-up questions

- [DAT-21](../dat-21/): How open news instantly? **Answer:** Room-backed PagingSource with RemoteMediator refresh.
- [DAT-12](../dat-12/): Why transaction? **Answer:** page rows and remote keys must commit together.

## Self-check rubric

Can I identify source of truth, persist keys atomically and test changing server order?

## References and reviewed-on date

- [Android Paging network/database guide](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — RemoteMediator pattern.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
