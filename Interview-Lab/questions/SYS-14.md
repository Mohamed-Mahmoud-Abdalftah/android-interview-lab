---
id: "SYS-14"
question: "How do you design API boundaries for multiple teams?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 343
editorial_status: "reviewed"
---

# SYS-14

## Original interview question

How do you design API boundaries for multiple teams?

## What the interviewer evaluates

Define stable API boundaries and ownership contracts for multiple teams.

## Explanation in Arabic

كيف تصمم حدود الـ APIs والتعاقدات (API Boundaries and Contracts) لتطبيق كبير تعمل عليه فرق متعددة؟

1. تحدي العمل عبر فرق متعددة (Multiple Teams & Distributed Ownership):
   - عندما تعمل فرق متعددة (Mobile, Web, Backend, Payments, Search) دون تعاقدات واضحة، تتكرر المشاكل: تغييرات مفاجئة في الـ JSON، بطء التطوير لانتظار انتهاء الـ Backend، وتعارض في نماذج البيانات.

2. المعمارية التعاقدية (Contract-First Design):
   - **Contract-First قبل كتابة الكود**: الاتفاق على مواصفات الـ API (عبر OpenAPI/Swagger أو Protobuf) واعتمادها قبل أن يبدأ أي فريق في كتابة الكود.
   - **توليد الـ Mocks التلقائية**: استخدام ملفات الـ Schema لتشغيل Mock Servers (مثل Prism أو WireMock) تتيح لفريق الموبايل تطوير واختبار الميزة بالكامل دون انتظار انتهاء الـ Backend.

3. معمارية الـ BFF (Backend-for-Frontend):
   - **مشكلة الـ Microservices في الموبايل**: استدعاء 5 خدمات منفصلة لعرض شاشة واحدة يستهلك شبكة الهاتف وبطاريته.
   - **الحل**: طبقة BFF مخصصة للموبايل تقوم بتجميع البيانات وتفصيلها (Aggregating & Shaping) لتناسب الشاشات المحمولة تماماً، مما يقلل عدد الطلبات وحجم البايتات المنقولة.

4. عزل النماذج داخل التطبيق (Data Layer Decoupling):
   - لا تجعل كلاسات الـ DTO (الـ Network Models) تتسرب إلى الـ UI! لكل طبقة نماذجها الخاصة، ويتم استخدام Mappers صريحة لعزل الـ UI عن أي تغييرات تطرأ على الـ API.

## Practical walkthrough

عزل نماذج الشبكة (DTOs) عن الـ Domain Entities واستخدام Mappers صريحة لحماية الواجهة من تقلبات الـ API:
```kotlin
// 1. نموذج الشبكة الخارجي المربوط بالـ API Contract (عرضة للتغيير من فرق الـ Backend):
@JsonClass(generateAdapter = true)
data class OrderNetworkDto(
    @Json(name = "order_id") val id: String,
    @Json(name = "total_cents") val totalAmount: Long,
    @Json(name = "status_code") val statusCode: String,
    @Json(name = "created_at_epoch") val timestamp: Long
)

// 2. نموذج الـ Domain المستقر والمعزول تماماً عن الـ Framework:
data class Order(
    val id: String,
    val formattedTotal: String,
    val status: OrderStatus,
    val date: LocalDate
)

// 3. Mapper صريح يمتص التغييرات ويمنع كسر الـ UI:
fun OrderNetworkDto.toDomain(): Order {
    return Order(
        id = this.id,
        formattedTotal = "$%.2f".format(this.totalAmount / 100.0),
        status = when (this.statusCode) {
            "PAID" -> OrderStatus.CONFIRMED
            "SHIPPED" -> OrderStatus.IN_TRANSIT
            else -> OrderStatus.PENDING
        },
        date = Instant.ofEpochMilli(this.timestamp).atZone(ZoneId.systemDefault()).toLocalDate()
    )
}
```

## Why it matters and how it works

An API boundary includes types, threading, errors, cancellation, security and compatibility, not just an interface name. Prefer stable domain concepts over exposing Retrofit DTOs or Room entities. Review cross-team changes with consumers and measure dependency graph/rebuild impact.

## Worked example

Conceptual Kotlin API owned by payments team; implementation stays hidden.

```kotlin
interface PaymentsApi {
    suspend fun status(operationId: String): PaymentStatus
    fun observe(operationId: String): kotlinx.coroutines.flow.Flow<PaymentStatus>
}
// :feature:checkout depends on API; :data:payments implements it;
// :app composes binding. No checkout -> payments implementation edge.
```

## Trade-offs and decision criteria

Narrow contracts improve autonomy but may require more coordination for genuinely shared workflows. Too many tiny API modules increase configuration overhead. Concrete dependency can be fine inside one team/feature; abstraction is useful where ownership or volatility differs.

## Failure modes

Passing Room Entity across module boundary couples UI to schema migration. A cyclic dependency blocks builds and ownership. A shared `CommonUtils` module grows into a bottleneck. An API changed without migration plan breaks old feature builds.

## Production perspective

A commerce org assigns catalog, checkout and payments team owners, uses stable payment status API, publishes compatibility tests and reviews schema changes. CI enforces acyclic graph and tracks affected build targets.

## Interview answer — short

Design cross-team API boundaries using contract-first schemas like OpenAPI or Protobuf, deploy a Backend-for-Frontend (BFF) layer to aggregate chatty microservices into mobile-optimized payloads, and decouple network DTOs from internal domain entities using explicit mapping boundaries.

## Interview answer — structured

Establishing clean API boundaries across distributed engineering teams prevents communication bottlenecks and contract drift.

First, **Contract-First Design & Parallel Development**. Next, mobile and backend teams negotiate the API contract (OpenAPI 3.0 or Protocol Buffers) during sprint planning before implementation begins.
CI generates type-safe client models and stubbed mock servers (e.g. WireMock, Prism), enabling mobile teams to build and verify features against accurate mocks without waiting for backend deployments. **The Backend-for-Frontend (BFF) Pattern**.
Microservices architectures fragment data across domain services (User, Orders, Inventory, Recommendations). Direct client-to-microservice communication causes cellular radio drain, high latency, and fragile error handling. A mobile-specific BFF aggregates multiple microservices server-side, returning a single tailored response payload matching the client screen layout.
**Strict Domain Layer Isolation**. Finally, never leak API DTOs directly into UI Composables or ViewModels. Maintain explicit mapping layers (`NetworkDto -> DomainEntity -> UiState`). If the backend team renames a field, only the single mapping function requires modification; UI layers remain unaffected.


## Interview answer — deep senior

From an organizational scaling perspective, robust API boundaries require automated contract verification.

First, with Consumer-Driven Contract Testing (Pact), implement contract testing where the mobile client publishes its schema expectations to a central Pact broker. Before the backend team deploys an API change, their CI pipeline runs contract tests against the mobile schema to verify that no expected fields were broken or removed. Next, with Tolerant Reader Pattern, mobile JSON parsers (Moshi / Kotlinx Serialization) must ignore unknown properties (`ignoreUnknownKeys = true`). If the backend adds new fields for other platforms, older mobile versions parse the payload without throwing deserialization exceptions.
Finally, with Deprecation Strategy & Graceful Decommissioning, backends must never alter existing field data types. When deprecating fields, mark them `@Deprecated` in contracts, support them concurrently for at least 12 months, and monitor mobile version usage metrics before hard field removal.


## How to answer in the interview

- **Why:** shared boundaries let teams change internals independently.
- **How:** publish narrow domain APIs with explicit semantics and ownership.
- **Trade-off:** contracts require versioning and coordination.
- **Failure case:** leaking wire DTOs couples every feature to backend changes.
- **Production solution:** consumer contract tests, migration notes, and measured adoption.

## Deep-dive talking points

Walk one cross-team contract from type definition to runtime binding and rollout.

## Follow-up questions

- **Interviewer:** "What is the Tolerant Reader Pattern?"
  **Answer:** "A design practice where clients parse only the fields they care about and safely ignore unrecognized keys, allowing backends to evolve schemas without breaking older apps."

- **Interviewer:** "Why is GraphQL or BFF preferred over direct REST calls in mobile architectures?"
  **Answer:** "It eliminates over-fetching and under-fetching by allowing the mobile client to request precisely the fields needed for the active viewport in a single HTTP round-trip."

## Self-check rubric

Can I define owner, error/lifecycle contract, compatibility tests and dependency direction?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module APIs and ownership.
- [Android architecture guide](https://developer.android.com/topic/architecture) — SSOT and layers.

Technically reviewed against primary documentation on 2026-10-13.
