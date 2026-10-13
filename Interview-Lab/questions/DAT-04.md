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

مقارنة معمارية رفيعة المستوى بين بروتوكولات الاتصال في Android:
REST و GraphQL و WebSockets، ومتى تختار كل منها؟

1. REST (Representational State Transfer):
   - **كيف يعمل**: يعتمد على موارد محددة (Resources) عبر عناوين URL (`/users/123/orders`) ودوال HTTP القياسية (GET, POST, PUT, DELETE).
   - **المميزات**: معيار عالمي، سهل الفهم، ممتاز في التخزين المؤقت (HTTP Caching عبر ETag و Cache-Control)، واستقرار فائق.
   - **العيوب**: مشكلة الـ Over-fetching (جلب بيانات زائدة لا تحتاجها الشاشة) والـ Under-fetching (الحاجة لطلب 3 endpoints متتالية لعرض شاشة واحدة).

2. GraphQL:
   - **كيف يعمل**: نقطة اتصال موحدة (`/graphql`) يرسل فيها العميل استعلاماً دقيقاً (Query) يحدد فيه شكل الحقول التي يحتاجها فقط.
   - **المميزات**: يحل مشكلة الـ Over/Under-fetching تماماً. مثالي للشاشات المعقدة التي تجمع بيانات من جداول متعددة في طلب واحد.
   - **العيوب في الموبايل**: يفقد ميزة الـ Standard HTTP Caching لأن كل الطلبات ترسل كـ `POST`، ويتطلب مكتبات خاصة (مثل Apollo Kotlin)، وصعوبة إدارة حماية وتعقيد الاستعلامات على السيرفر.

3. WebSockets:
   - **كيف يعمل**: اتصال ثنائي الاتجاه دائم (Persistent Full-Duplex TCP Connection).
   - **المميزات**: تبادل بيانات فوري بدون Overhead لترويسات HTTP في كل رسالة.
   - **متى يُستخدم**: للتطبيقات الحية (Live Chat، التداول المالي الفوري، تتبع حركة السائق على الخريطة في تطبيقات التوصيل).
   - **التحديات في الموبايل**: استهلاك عالي للبطارية إذا لم يُدار بحذر، وانقطاع الاتصال المتكرر عند تحول الهاتف بين شبكة Wi-Fi وبيانات الجوال، مما يتطلب بروتوكول إعادة اتصال ومزامنة دائم.

## Practical walkthrough

جدول المقارنة واتخاذ القرار الهندسي بين البروتوكولات الثلاثة:
```text
┌───────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┐
│ المعيار       │ REST                     │ GraphQL (Apollo)         │ WebSockets (OkHttp WS)   │
├───────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤
│ نوع الاتصال   │ طلب/استجابة (Stateless)  │ طلب/استجابة (Stateless)  │ اتصال دائم (Full-Duplex) │
│ الكاش التلقائي│ ✅ مدعوم بـ HTTP Caching  │ ❌ يتطلب Normalized Cache│ ❌ غير مدعوم             │
│ حجم البيانات  │ قد يحتوي على Overfetching│ ✅ الحقول المطلوبة فقط   │ ✅ بيانات خام خفيفة      │
│ استهلاك بطارية│ منخفض جداً               │ منخفض                    │ يحتاج إدارة دقيقة للـ Ping│
│ أفضل استخدام  │ CRUD، دفع، مستندات، ملفات│ شاشات لوحات تحكم وتجارة  │ شات، تتبع تاكسي، ألعاب   │
└───────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

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

REST uses standard resource endpoints and excels at HTTP caching for typical CRUD apps. GraphQL uses a single endpoint with client-specified queries, eliminating over-fetching for complex data dashboards. WebSockets provide persistent, bidirectional TCP connections for low-latency real-time apps like chat and live vehicle tracking.

## Interview answer — structured

Choosing between REST, GraphQL, and WebSockets is driven by data velocity, client flexibility, and caching requirements:

1. **REST (Standard Resource APIs)**: Best for standard CRUD domains, file uploads, and high-cacheability resources. It leverages native HTTP semantics (status codes, ETags, CDN edge caching). Its weakness on mobile is over-fetching (wasting cellular data on unneeded fields) and under-fetching (making chained requests for relational data).

2. **GraphQL (Client-Driven Relational Queries)**: Best for rich, multi-entity consumer dashboards (e.g. an e-commerce feed joining user, cart, promotions, and reviews in a single query). The client asks for exact fields, saving mobile bandwidth. However, because all queries use HTTP `POST`, standard HTTP/CDN caching is lost, requiring specialized normalized caching engines (Apollo Kotlin).

3. **WebSockets (Full-Duplex Real-Time Streams)**: Best for low-latency bidirectional push streams (instant messaging, live bidding, multiplayer games, continuous telemetry). Rather than polling REST endpoints, the server pushes events instantly over an open TCP socket. Mobile implementations must manage heartbeat pings, reconnect state machines, and battery life.

## Interview answer — deep senior

When architecting **WebSockets on Android**, mobile operating system constraints dictate strict lifecycle governance:

1. **Doze Mode & Radio State**: Keeping a raw WebSocket open prevents the cellular radio from dropping from full power (DCH) to low-power idle state, rapidly draining battery. In background states, the OS can terminate TCP sockets without firing `onClosing()`. Robust apps close WebSockets when the app enters `ON_STOP`, falling back to Firebase Cloud Messaging (FCM) high-priority push notifications for background delivery.

2. **The Reconnection State Machine**: Cellular handoffs (switching from Wi-Fi to 5G) drop sockets silently. The Android client must implement an active Ping/Pong heartbeat (e.g. `OkHttpClient.Builder().pingInterval(30, TimeUnit.SECONDS)`) and an exponential backoff reconnect policy that reconciles missed events by querying a REST/Room sync cursor upon reconnect.

## How to answer in the interview

- **Why:** Match transport to shape, freshness and offline requirements.
- **How:** Contrast REST resources, GraphQL selection and WebSocket streams.
- **Trade-offs:** Count server complexity, battery and cache design.
- **Failure cases:** Lost socket events or unbounded GraphQL query cost.
- **Production solution:** Keep Room/HTTP snapshot authoritative and reconcile stream gaps.

## Deep-dive talking points

Defend protocol choice against offline, cache, query abuse and reconnect gaps.

## Follow-up questions

- **Interviewer:** "Can you use HTTP/2 Server-Sent Events (SSE) instead of WebSockets?"
  **Answer:** "Yes. If communication is strictly unidirectional from server to client (e.g. live sports scores or stock tickers), SSE is lighter, runs over standard HTTP, and handles auto-reconnect natively."

- **Interviewer:** "How does Apollo Kotlin manage caching for GraphQL?"
  **Answer:** "It provides a Normalized Cache that parses response objects by their `id` or `__typename`, storing entities in SQLite to provide reactive Flow queries similar to Room."

## Self-check rubric

Can I compare all three, name one failure mode each and design missed-event recovery?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — HTTP resource semantics.
- [OkHttp documentation](https://lysine.dev/okhttp/) — WebSocket transport support.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local truth and sync.

Technically reviewed against primary documentation on 2026-10-13.
