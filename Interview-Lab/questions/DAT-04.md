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

## Concept and technical explanation

Mobile applications employ different network communication paradigms depending on interaction semantics, latency, and data topology:
- REST (Representational State Transfer):
  * Architectural Style: Stateless, resource-centric over HTTP/1.1 or HTTP/2.
  * Strengths: Universal standard, leverages battle-tested HTTP caching (ETags, Cache-Control), robust CDN distribution, and simple tooling.
  * Weaknesses: Prone to over-fetching (receiving unneeded fields) and under-fetching (requiring waterfall requests across multiple endpoints).
- GraphQL:
  * Architectural Style: Query-language driven over a single HTTP POST endpoint.
  * Strengths: Eliminates over-fetching and under-fetching by allowing the client to declare the exact schema shape required. Excellent for complex, deeply nested relational dashboards.
  * Weaknesses: Breaks standard HTTP-level caching because all requests hit a single URL via POST; shifts query parsing and complexity costs to both server and client (Apollo Android runtime); difficult CDN edge caching.
- WebSockets:
  * Architectural Style: Persistent, bidirectional, full-duplex TCP connection established via an HTTP Upgrade handshake.
  * Strengths: Ultra-low latency framing without HTTP header overhead. Ideal for real-time streaming, chat applications, financial order books, and collaborative whiteboards.
  * Weaknesses: Demands active connection management, heartbeat ping/pong frames to keep NAT gateways open, complex client reconnection state machines, and higher battery consumption if not managed carefully.

## Practical walkthrough (English)

Architectural matrix and client integration comparison:
```kotlin
// 1. REST with Retrofit: Resource-oriented, standard HTTP caching
interface RestOrderApi {
    @GET("orders/{id}")
    suspend fun getOrder(@Path("id") id: String): OrderDto
}

// 2. GraphQL with Apollo: Declarative field selection
val response = apolloClient.query(GetOrderSummaryQuery(id = "123")).execute()

// 3. WebSocket with OkHttp: Real-time bidirectional streaming
val ws = okHttpClient.newWebSocket(
    Request.Builder().url("wss://stream.example.com/orders").build(),
    object : WebSocketListener() {
        override fun onMessage(webSocket: WebSocket, text: String) {
            liveOrderUpdates.tryEmit(parseOrderUpdate(text))
        }
        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
            // Reconnection logic
        }
    }
)
```

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

REST is a resource-oriented stateless standard leveraging HTTP caching and CDNs but susceptible to over-fetching. GraphQL provides precise declarative field querying over a single endpoint at the cost of HTTP caching complexity. WebSockets establish persistent, full-duplex TCP connections for ultra-low latency real-time bidirectional streaming at higher battery cost.

## Interview answer — structured

Choosing between REST, GraphQL, and WebSockets depends on data access patterns, caching needs, and latency requirements.
First, REST is the industry standard for resource-based operations. It excels at leveraging native HTTP caching, ETags, and global CDNs. However, mobile clients frequently suffer from over-fetching unneeded payload data or under-fetching, requiring multiple roundtrips to assemble a screen.
Second, GraphQL addresses under-fetching by allowing mobile clients to request exact schema fields across relations in a single roundtrip. While powerful for complex views, it bypasses standard HTTP caching and increases client parsing complexity.
Third, WebSockets enable low-latency, full-duplex communication over a long-lived TCP connection. They are the ideal choice for real-time messaging, financial tickers, and live tracking, though they require sophisticated heartbeat and reconnection logic to preserve battery life.

## Interview answer — deep senior

In large-scale Android system design, picking the correct networking paradigm is a tradeoff between network roundtrip efficiency, battery longevity, and caching infrastructure.
REST remains our default for standard CRUD and content feeds. Its seamless compatibility with HTTP status codes, Cache-Control headers, and CDN edge caching offloads massive traffic from origin servers, providing instant localized responses for global users.
GraphQL shines in heterogeneous mobile screens, such as an e-commerce checkout page that requires customer details, inventory statuses, shipping estimates, and payment methods.
Rather than executing four sequential REST calls that drain radio power, an Apollo GraphQL query fetches the exact composite graph in a single roundtrip.
However, because GraphQL queries execute as POST requests against a single /graphql endpoint, conventional HTTP caching proxies become ineffective; mobile teams must implement client-side normalized caches like Apollo's Normalized Cache.
WebSockets solve an entirely different problem: push-based real-time interactivity.
Instead of battery-draining polling, a single TCP socket delivers sub-millisecond updates for chat or live order dispatch.
However, keeping a mobile WebSocket alive requires aggressive power management: sending application-level ping/pong heartbeats to prevent cellular carrier NAT timeouts, pausing the socket when the app enters the background, and falling back to push notifications via FCM to prevent OS background execution kills.
Additionally, we design hybrid offline synchronizers where WebSockets broadcast lightweight entity invalidation notifications, prompting the mobile client to pull incremental Delta updates via optimized REST or GraphQL endpoints to conserve bandwidth.

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
