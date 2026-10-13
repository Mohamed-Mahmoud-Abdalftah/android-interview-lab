---
id: "DAT-08"
question: "What are cache-first, network-first, and stale-while-revalidate strategies?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 265
editorial_status: "reviewed"
---

# DAT-08

## Original interview question

What are cache-first, network-first, and stale-while-revalidate strategies?

## What the interviewer evaluates

Compare cache-first, network-first and stale-while-revalidate from freshness and latency constraints.

## Explanation in Arabic

`cache-first` يعرض cache لو صالحة ويقلل latency/network، لكن ممكن يبقى stale. `network-first` يحاول network الأول ثم يرجع cache عند الفشل، مناسب لما freshness مهمة بس loading أبطأ. `stale-while-revalidate` يعرض cached snapshot فورًا ويعمل refresh في الخلفية ويحدثها؛ لازم UI تعرف هل البيانات stale أو pending. اختيار السياسة يختلف بين أخبار، أسعار، وpayment status.

## Why it matters and how it works

Cache validity depends on TTL, server validators such as ETag, invalidation events and per-record versioning. Network-first needs a bounded deadline and offline fallback. Stale-while-revalidate needs one local source of truth so remote result does not race a separate UI channel.

## Worked example

Conceptual repository contract; caller observes Room and asks for refresh separately.

```kotlin
import kotlinx.coroutines.flow.Flow

interface FeedCache {
    fun observe(): Flow<CachedFeed> // includes fetchedAt and stale flag
    suspend fun refreshIfNeeded(force: Boolean = false)
}
// Remote refresh writes Room transactionally; UI does not merge two lists.
```

## Practical walkthrough

cache-first تعرض local data فورًا ثم refresh حسب freshness policy؛ network-first تحاول remote قبل fallback محلي، فممكن تقلل staleness لكن تزيد انتظار المستخدم؛ stale-while-revalidate تعرض cached snapshot مع تحديث في الخلفية. مش كل data ينفع لها stale: news cards ممكن، available balance أو authorization قبل action لا. خزّن `fetchedAt` وserver version/ETag، واضبط invalidation لما account يتبدل أو write تغير row. لو refresh فشل، سيب last-good rows واعرض stale indicator بدل تمسح الشاشة. استخدم clock injected للاختبار، وافتكر TTL وحده ما يمنع old response overwriting newer version.

## Trade-offs and decision criteria

Cache-first is fast and economical; network-first favors freshness at latency cost; stale-while-revalidate improves perceived speed but can briefly show outdated data. For security-critical or financial status, verify current server authority before committing an action.

## Failure modes

A timestamp-only TTL can be wrong after clock changes; use server validators/versions where possible. Showing old stock or price as current can mislead users. Concurrent refreshes can arrive out of order and overwrite newer cache without version checks.

## Production perspective

A news feed displays cached stories immediately with an updated-at label and refreshes in background. Checkout price instead requests a fresh server quote with expiry and cannot transact on stale cached price.

## Interview answer — short

“Cache-first favors speed and bandwidth, network-first favors freshness with fallback, and stale-while-revalidate shows cached data immediately while refreshing. I choose from domain freshness requirements and expose staleness clearly.”

## Interview answer — structured

“I define what ‘fresh’ means for each screen. Cache-first serves valid local data and avoids network. Network-first attempts current server data but falls back to cache when offline. Stale-while-revalidate renders local content instantly and asynchronously updates the same database source. News content can tolerate labeled stale data; checkout pricing needs a fresh server quote. I use TTL plus server versions or validators, handle out-of-order refresh and keep error/stale state visible.”

## Interview answer — deep senior

A cache strategy is not just ordering two calls; it is a correctness contract. I specify maximum tolerated age, whether stale data may drive actions, and how invalidation works. Cache-first reduces startup and battery cost but risks hidden staleness. Network-first can block UX on a weak connection, so I set a deadline and explicit fallback. Stale-while-revalidate is excellent for browsable feeds if remote updates commit transactionally into Room, which remains the one UI source. I use server ETags/versions where available, suppress older refresh results, label stale/pending state and test offline startup and clock anomalies. Financial or security-sensitive state requires authoritative confirmation before irreversible action.

I would first define what “fresh enough” means for the feature. Cache-first prioritizes startup and battery, network-first prioritizes current data but needs a bounded fallback, and stale-while-revalidate renders the local snapshot while refreshing it. A news feed can tolerate a stale label; a payment balance or authorization decision usually needs a server check before action. I store freshness metadata and server versions, partition by account, and ensure an old response cannot overwrite newer data. If refresh fails, I keep last-good rows and surface their age. The production test covers offline launch, slow network, account switch, and out-of-order responses.

## How to answer in the interview

- **Why:** Cache policy is a product correctness choice, not only call order.
- **How:** Contrast first render and refresh behavior of all three strategies.
- **Trade-offs:** Set tolerated age per feature and bound network-first wait.
- **Failure cases:** Hidden stale balance or older response overwriting newer rows.
- **Production solution:** Use freshness/version metadata and retain last-good data on failure.

## Deep-dive talking points

Define TTL/ETag/version, out-of-order refresh and stale-action safety.

## Follow-up questions

- [DAT-17](../dat-17/): How invalidate cache? **Answer:** TTL, server validators/versions and explicit mutation/session events.
- [DAT-21](../dat-21/): Which strategy fits news? **Answer:** show cached feed immediately, then revalidate.

## Self-check rubric

Can I choose all three by domain, label stale data and prevent old refresh overwrite?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — cached local reads and refresh.
- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — conditional request semantics.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
