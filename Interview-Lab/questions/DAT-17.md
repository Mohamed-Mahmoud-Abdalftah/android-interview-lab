---
id: "DAT-17"
question: "How do you manage caching expiration and invalidation?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 274
editorial_status: "reviewed"
---

# DAT-17

## Original interview question

How do you manage caching expiration and invalidation?

## What the interviewer evaluates

Set cache expiry and invalidation by data semantics, server validators and session changes.

## Explanation in Arabic

Expiration مش TTL ثابت لكل حاجة. نحدد max age حسب domain، ونستخدم server version/ETag أو `Last-Modified` لإعادة التحقق، ونبطل cache عند mutation, logout أو tenant switch. UI تعرض fetchedAt/stale marker لو المحتوى قديم. محتوى أخبار يتحمل دقائق؛ entitlement أو سعر دفع يحتاج server confirmation قبل فعل حساس.

## Why it matters and how it works

Use monotonic elapsed time for in-process scheduling and persisted server timestamps/validators carefully across reboot and clock changes. HTTP cache headers can govern transport cache, while Room application cache needs its own invalidation policy. Generation/version checks prevent late old refresh from overwriting a newer row.

## Worked example

Conceptual cache metadata; version is a server token, not a client clock.

```kotlin
data class CachedRow<T>(
    val value: T,
    val serverVersion: String,
    val fetchedAtEpochMs: Long,
)
fun isExpired(row: CachedRow<*>, nowEpochMs: Long, ttlMs: Long): Boolean =
    nowEpochMs - row.fetchedAtEpochMs >= ttlMs
// Also invalidate on mutation/session switch and revalidate with server version.
```

## Practical walkthrough

cache expiration لازم تميز transport cache بـHTTP headers عن domain rows في Room. `Cache-Control/ETag` تقلل network requests، لكن local `fetchedAt`/server version تحدد UX freshness. TTL بالساعة الجهاز ممكن يتأثر بتغيير clock؛ لو محتاج ضمان قوي استخدم server version/validation أو monotonic timing للجلسة، واتعامل مع offline case صراحة. عند write أو logout، invalidate affected keys/account partition بدل `clearAll` عشوائي. لو refresh response قديمة وصلت بعد جديدة، قارن version قبل الكتابة. balance أو permission لا تعتمد على stale row قبل action؛ news headline يمكن تعرضها مع age label.

## Trade-offs and decision criteria

TTL is simple and available offline but can be wrong after device clock changes. Server validators reduce payload but need endpoint support. Push invalidation is timely but unreliable during disconnect, so periodic/reconnect revalidation remains necessary.

## Failure modes

A cache keyed only by URL can leak prior user data after account switch. A late response for old version can overwrite new state. Relying on push notifications alone misses updates while offline. Treat unknown freshness as stale rather than silently fresh.

## Production perspective

A catalog caches pages with server versions and fetchedAt, revalidates on app foreground/reconnect, and invalidates edited items immediately. Checkout asks the server for a fresh quote with expiry before payment. Metrics track cache hit rate and stale age.

## Interview answer — short

“I define freshness per data type, use TTL plus server validators where available, invalidate on mutations and session changes, and prevent older responses overwriting newer data. Sensitive actions verify current server state.”

## Interview answer — structured

“Cache expiry is a product decision. A news feed can show labeled stale content for fast startup, while a payment quote must be fresh. I store fetched time and server version/ETag, revalidate conditionally, and invalidate on writes, logout or tenant changes. Network push hints are useful but cannot be the only invalidation mechanism because mobile connections drop. I also guard against out-of-order refresh responses and device clock changes.”

## Interview answer — deep senior

I distinguish HTTP transport caching from the app’s Room-backed domain cache. Cache-Control/ETag can reduce network cost, while local rows need explicit freshness metadata and invalidation triggers. A single TTL is too blunt: offline browse may tolerate stale articles, but authorization, stock and money require authoritative checks before action. I partition cache by account, clear or replace it on logout, version rows so older refreshes cannot overwrite newer ones, and revalidate on reconnect/foreground. Device wall clocks can change, so I do not rely on them alone for security decisions. Tests cover clock skew, out-of-order responses, account switch and offline staleness.

I separate wire caching from application state. HTTP validators such as ETag can save bandwidth, while Room rows need product-specific freshness metadata and invalidation rules. A single TTL is inadequate: a news card can be shown stale with a label, but a balance or permission must be revalidated before a sensitive action. I partition rows by account, invalidate related data after writes, and reject an older server version arriving after a newer response. Device wall-clock changes also make naïve age checks unreliable, so I test clock skew and offline startup. On refresh failure I keep the last-good snapshot when the feature allows it rather than clearing the screen.

## How to answer in the interview

- **Why:** Freshness is domain-specific and account-specific.
- **How:** Distinguish HTTP validators from Room metadata and invalidation.
- **Trade-offs:** Show stale low-risk content, revalidate sensitive actions.
- **Failure cases:** Clock-skew TTL, old response overwrite, cross-account cache leak.
- **Production solution:** Version checks, account partitioning and explicit stale UI.

## Deep-dive talking points

Define per-domain max age, account partitioning, validators and race-safe refresh.

## Follow-up questions

- [DAT-08](../dat-08/): Which cache strategy displays stale then updates? **Answer:** stale-while-revalidate.
- [DAT-16](../dat-16/): How avoid stale overwrite? **Answer:** server version/precondition and conflict policy.

## Self-check rubric

Can I set freshness by domain, invalidate session data and handle out-of-order updates?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — conditional requests.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — cache freshness.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
