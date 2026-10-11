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

“I distinguish HTTP transport caching from the app’s Room-backed domain cache. Cache-Control/ETag can reduce network cost, while local rows need explicit freshness metadata and invalidation triggers. A single TTL is too blunt: offline browse may tolerate stale articles, but authorization, stock and money require authoritative checks before action. I partition cache by account, clear or replace it on logout, version rows so older refreshes cannot overwrite newer ones, and revalidate on reconnect/foreground. Device wall clocks can change, so I do not rely on them alone for security decisions. Tests cover clock skew, out-of-order responses, account switch and offline staleness.”

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

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
