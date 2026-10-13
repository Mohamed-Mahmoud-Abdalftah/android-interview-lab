---
id: "DAT-21"
question: "Design a paginated news feed that opens instantly and syncs when online."
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 278
editorial_status: "reviewed"
---

# DAT-21

## Original interview question

Design a paginated news feed that opens instantly and syncs when online.

## What the interviewer evaluates

Design instant paginated news with Room-backed Paging and online sync.

## Explanation in Arabic

لـnews feed تفتح فورًا، UI تقرأ Room PagingSource، و`RemoteMediator` يجيب صفحات من network ويكتب articles + remote keys transactionally. cached rows تظهر offline مع `updatedAt` وstale indicator؛ عند الاتصال نعمل refresh من server version/cursor، ونحافظ على stable IDs عشان القائمة ما تقفزش أو تكرر. أخطاء الشبكة ما تمسحش cache.

## Why it matters and how it works

Pager produces PagingData from Room; mediator loads remote pages and commits keys with rows. A refresh policy determines when cached data is stale. WorkManager can prefetch under constraints, while UI collection can trigger on-demand loads. Backend cursor stability matters when stories are inserted or reordered.

## Worked example

Conceptual Paging 3 repository; DAO, mediator and model types are application-specific.

```kotlin
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import kotlinx.coroutines.flow.Flow

fun news(dao: NewsDao, mediator: NewsMediator): Flow<PagingData<Article>> =
    Pager(PagingConfig(pageSize = 30), remoteMediator = mediator) {
        dao.pagingSource()
    }.flow
```

## Practical walkthrough

news feed تفتح بسرعة لو UI تقرأ Room PagingSource من أول لحظة، والـRemoteMediator تعمل refresh لما online حسب TTL/gesture. خزّن articles والremote keys وfreshness metadata في transaction، واستخدم server cursor/snapshot بدل offset لو feed تتغير باستمرار. لو refresh فشلت، ما تمسحش cached rows؛ اعرض stale age وload-state retry. لو append رجّعت duplicate article، primary key/upsert يثبت القائمة. لو user فتح article offline، data كاملة ولا بس card summary؟ صمّم ده من الأول. اختبر cold launch offline، process death أثناء append، inserts جديدة تغير ترتيب feed، وحذف/تعديل server rows.

## Trade-offs and decision criteria

Room-backed paging gives instant offline content but adds storage and key migration work. Network-only paging is simpler but opens empty offline. Prefetch improves startup at battery/network cost; respect user data policies.

## Failure modes

An offset API on a changing feed can skip/duplicate stories when new items arrive. Clearing cache before successful refresh flashes empty UI. Failing to persist keys with rows can make APPEND repeat pages after process death.

## Production perspective

A news app shows cached headlines immediately, starts conditional refresh when online, stores pages and cursors in one transaction, and labels stale content. Tests cover offline launch, new articles inserted at top, repeated pages and crash during refresh.

## Interview answer — short

“I use Room as the immediate UI source, Paging 3 for bounded lists and RemoteMediator to fetch/version pages into Room. I preserve cache on refresh errors, store remote keys atomically and show freshness.”

## Interview answer — structured

“The feed’s first frame should come from local storage, not wait for network. A Room PagingSource gives cached pages to Pager. RemoteMediator fetches fresh pages when needed and writes articles plus remote keys in a transaction, so the UI sees one consistent local source. I use stable IDs and a server cursor contract to avoid duplicates when the feed changes. Offline or refresh failure leaves cached news visible with an updated-at label; retry is explicit.”

## Interview answer — deep senior

I would design the server pagination contract before the UI adapter. Opaque cursors or snapshot versions are safer than offsets for a changing news feed. Locally, articles, remote keys and freshness metadata are stored transactionally; Room invalidation drives the PagingSource. On launch, cached rows render immediately, while RemoteMediator refreshes according to TTL or user action. Network errors affect load state, not existing cached rows. I may prefetch with WorkManager under network/battery constraints, but the UI remains usable without it. Tests simulate top insertions, duplicate pages, cursor expiration, process death between fetch and commit, and offline startup.

I would start from the user promise: the feed renders cached headlines immediately and becomes fresher when connected. Room is the UI source through a PagingSource, while RemoteMediator fetches pages and stores articles, remote keys, and freshness metadata transactionally. For a changing news list, a cursor or snapshot contract is safer than offsets that shift under new inserts. I do not clear last-good rows when refresh fails; load state reports the error while the user can still browse. Stable IDs make duplicate page delivery harmless. I also decide whether opening an article offline requires full body storage or only cached summary, then test that explicit experience across process death and reconnect.

## How to answer in the interview

- **Why:** Instant launch and offline reading need local paging.
- **How:** Room PagingSource renders; mediator refreshes rows and keys transactionally.
- **Trade-offs:** Cursor/snapshot contract versus simpler but shifting offsets.
- **Failure cases:** Blank feed on failed refresh or duplicate page rows.
- **Production solution:** Stale indicator, retry load state and offline/article tests.

## Deep-dive talking points

Draw Page API → mediator → Room → UI and describe cursor/invalidation behavior.

## Follow-up questions

- [DAT-13](../dat-13/): What does RemoteMediator own? **Answer:** remote loads and atomic persistence of rows/keys.
- [DAT-08](../dat-08/): Which cache policy fits fast open? **Answer:** stale-while-revalidate with visible freshness.

## Self-check rubric

Can I show instant local page, atomic keys, stable cursor and offline error UX?

## References and reviewed-on date

- [Android Paging network/database guide](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — RemoteMediator.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
