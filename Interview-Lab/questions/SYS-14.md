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

## Concept and technical explanation

Scaling mobile engineering across dozens of autonomous product squads requires decoupling codebase dependencies through well-defined API boundaries and architectural contracts. When multiple teams contribute to a monolithic codebase without explicit boundaries, code ownership blurs, merge conflicts escalate, build times balloon, and a breaking change in one domain silently breaks unrelated features. Effective API boundary design splits each domain into a public contract module (:api) and a private implementation module (:impl). The api module exposes pure Kotlin interfaces, domain entities, and navigation contracts with zero platform implementation details. Feature squads depend strictly on external api modules, remaining completely unaware of implementation classes. Dependency injection frameworks like Dagger or Hilt bind interfaces to implementations within the root application module. This architecture enforces clean code ownership, facilitates parallel development, accelerates incremental compilation, and allows teams to refactor internal implementations without impacting peer squads.

## Practical walkthrough (English)

Designing decoupled API contracts and navigation boundaries for multiple feature teams:
```kotlin
// In module :feature:checkout:api (Shared public contract owned by Checkout Squad)
interface CheckoutNavigationApi {
    fun navigateToCheckout(launcher: ActivityResultLauncher<Intent>, cartId: String)
}

interface CheckoutStatusProvider {
    fun observePendingOrdersCount(): Flow<Int>
}

data class CheckoutSession(
    val sessionId: String,
    val cartTotalCents: Long,
    val isEligibleForOneClick: Boolean
)

// In module :feature:checkout:impl (Private implementation hidden from peer squads)
internal class CheckoutNavigationApiImpl @Inject constructor(
    private val appContext: Context
) : CheckoutNavigationApi {
    override fun navigateToCheckout(launcher: ActivityResultLauncher<Intent>, cartId: String) {
        val intent = Intent(appContext, CheckoutActivity::class.java).apply {
            putExtra("EXTRA_CART_ID", cartId)
        }
        launcher.launch(intent)
    }
}

// In module :app (Root composition module binding interfaces to concrete implementations)
@Module
@InstallIn(SingletonComponent::class)
abstract class CheckoutBindingModule {
    @Binds
    @Singleton
    internal abstract fun bindCheckoutNav(impl: CheckoutNavigationApiImpl): CheckoutNavigationApi
}
```

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

We design API boundaries for multiple teams by splitting each feature into an api contract module and an impl private module. Peer teams depend strictly on public interfaces and domain models, hiding internal implementation details and wiring dependencies at the root application layer using Dagger or Hilt.

## Interview answer — structured

Scaling an engineering organization across multiple mobile squads requires decoupling team ownership through strict module contracts.
I establish a clear separation of concerns by dividing every domain into an api module and an impl module.
The api module contains only pure interfaces, immutable data models, and navigation contracts, with zero references to internal libraries or Android Views.
Consuming teams depend exclusively on the api module through Gradle. This prevents peer squads from coupling to internal ViewModels, database entities, or network DTOs.
Concrete implementation classes inside the impl module are marked with Kotlin internal visibility, preventing external access.
The root application module acts as the dependency injection assembler, using Dagger or Hilt to bind concrete implementations to public interface contracts.
This boundary ensures squads can completely refactor their internal database schemas and UI layouts without triggering recompilation or breaking builds across other teams.

## Interview answer — deep senior

From a staff systems architect perspective, establishing cross-team API boundaries is as much an organizational and governance challenge as it is a technical one.
A common failure mode in modularized codebases is the leaky abstraction problem, where network DTOs or database entities are exposed directly in public API contracts. When backend teams alter network payloads, multiple feature teams suffer compilation breakages. We mandate strict model mapping boundaries: network models map to internal domain entities, which map to public contract objects at the module edge.
Navigation between team boundaries presents another architectural hazard. Hardcoded Activity class references create circular module dependencies that break Gradle builds. We solve this by introducing abstract navigation interfaces or URI-based deep link routers registered into a centralized navigation mediator. Feature A requests navigation to Checkout with a payload, and the mediator resolves the destination without Feature A knowing the concrete Activity class.
To prevent breaking changes across dozens of squads, we establish clear API versioning and deprecation policies. When an API contract must change, the owning squad introduces the new method alongside a Deprecated annotation with an explicit ReplaceWith expression and sunset timeline, giving consuming teams time to migrate asynchronously.
Finally, we enforce these architectural boundaries automatically using ArchUnit or Gradle dependency analysis plugins in CI, instantly failing pull requests that attempt to establish unauthorized direct dependencies between private implementation modules.

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
