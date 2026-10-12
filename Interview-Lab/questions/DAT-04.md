---
id: "DAT-04"
question: "Compare REST, GraphQL, and WebSockets at a high level."
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 261
editorial_status: "reviewed"
---

# DAT-04

## Original interview question

Compare REST, GraphQL, and WebSockets at a high level.

## What the interviewer evaluates

Compare resource endpoints, flexible queries and persistent bidirectional connections.

## Explanation in Arabic

`REST` أسلوب API قائم على resources وHTTP methods/cache semantics؛ `GraphQL` العميل يحدد shape للبيانات عبر query/schema لكن لازم server يحكم authorization وquery complexity؛ `WebSocket` اتصال طويل ثنائي الاتجاه للأحداث الحية. اختيار البروتوكول حسب data contract وoffline/cache/operability، مش لأن واحد أحدث. Mobile network بتقطع، فلازم reconnect وsync من مصدر authoritative.

## Why it matters and how it works

HTTP REST can benefit from standard caches, status semantics and simple tooling. GraphQL reduces over/under-fetching for varied screens but adds query governance, persisted query/security and cache complexity. WebSocket provides low-latency push but requires connection lifecycle, heartbeat/reconnect and missed-event recovery.

## Worked example

Conceptual Kotlin transport interface; implementation could use Retrofit HTTP for snapshot and OkHttp WebSocket for hints, with Room as local source.

```kotlin
interface FeedTransport {
    suspend fun snapshot(sinceVersion: Long): FeedPage
    fun liveHints(): kotlinx.coroutines.flow.Flow<Long>
}
// FeedPage and transport implementation are app-owned types;
// a hint triggers versioned snapshot/sync, not blind UI mutation.
```

## Trade-offs and decision criteria

REST is often sufficient for CRUD and easier intermediary caching. GraphQL suits heterogeneous reads but complicates cost control. WebSocket is suitable for timely events, not a durable source of truth by itself. Combine snapshot plus push hints when live updates must recover after disconnect.

## Failure modes

A WebSocket disconnect can miss messages; without cursor/version sync the UI silently diverges. A GraphQL query can request expensive nested data unless server limits it. Assuming POST is cacheable like GET by default is unsafe.

## Production perspective

A chat app reads cached Room messages, syncs versioned pages via HTTPS and uses WebSocket notifications to trigger refresh. Reconnect queries missed messages by cursor; auth and rate limits are enforced server-side.

## Interview answer — short

“REST uses HTTP resource semantics, GraphQL lets clients request a typed data shape, and WebSocket gives persistent bidirectional messages. I choose by access pattern and still design reconnection, caching and server authority.”

## Interview answer — structured

“For straightforward resource CRUD, REST benefits from familiar HTTP methods, status codes and caching. GraphQL is useful when screens need varied related fields, but the server must control authorization, query cost and caching. WebSockets are useful for low-latency updates, yet mobile connections drop and push messages are not durable truth. I often pair a snapshot API and local cache with live hints, then resynchronize by cursor after reconnect.”

## Interview answer — deep senior

“I start with requirements: data shape, update frequency, offline behavior, bandwidth and operational complexity. REST is usually a good baseline for resource APIs and clear retry semantics. GraphQL can reduce over-fetching across many screen shapes but requires query complexity limits and careful normalized caching; authorization cannot be delegated to the client query. WebSocket offers timely two-way updates, but Android lifecycle, Doze and network transitions require reconnect and catch-up. I use server versions/cursors so a missed socket event triggers a reliable HTTPS sync, write authoritative state to Room, and render from local data. Protocol choice does not replace idempotency, conflict resolution or security.”

## Deep-dive talking points

Defend protocol choice against offline, cache, query abuse and reconnect gaps.

## Follow-up questions

- [DAT-08](../dat-08/): How render during disconnect? **Answer:** use a local cache and freshness policy.
- [DAT-07](../dat-07/): Who is source of truth offline? **Answer:** local display state is derived from persistent store; server owns server data.

## Self-check rubric

Can I compare all three, name one failure mode each and design missed-event recovery?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — HTTP resource semantics.
- [OkHttp documentation](https://lysine.dev/okhttp/) — WebSocket transport support.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local truth and sync.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-12; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
