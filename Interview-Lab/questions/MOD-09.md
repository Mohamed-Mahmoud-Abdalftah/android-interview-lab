---
id: "MOD-09"
question: "How should feature modules communicate without direct coupling?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 362
editorial_status: "reviewed"
---

# MOD-09

## Original interview question

How should feature modules communicate without direct coupling?

## What the interviewer evaluates

Identify whether communication is navigation, shared domain data, or a result. Choose an app mediator or contract according to the relationship, pass small IDs, and explain lifecycle and result ownership without mandating API/impl modules for every feature.

## Concept and technical explanation

Sibling feature modules can communicate through an app-owned navigation coordinator, a shared data repository, or a narrow API contract where multiple consumers need one. A catalog feature can request `CheckoutRoute(productId)` without importing checkout UI; checkout loads current data by ID. An API/implementation split is useful for a stable shared boundary but is not mandatory for every feature, and a direct feature dependency is not universally forbidden. Shared event streams require explicit delivery and replay semantics; they are not a durable source of truth.

## Practical walkthrough (English)

Catalog emits a route containing a product ID. The app navigation graph resolves checkout. Checkout loads current price and stock from an owning repository. On completion, checkout returns an order ID through an appropriate result channel or persists order state for later observation. Passing a mutable cart across navigation risks stale data and fragile restoration after process recreation.

## Explanation in Arabic

لما Catalog تفتح Checkout، غالبًا هي محتاجة تعلن نية التنقل ومعرّف الـ Product، مش تستورد `CheckoutActivity` أو `CheckoutViewModel`. الـ app module اللي تملك Navigation Graph تقدر تبقى Mediator بين الاثنين. Checkout تقرأ الـ ID وتحمّل السعر والمخزون من Repository صاحبة البيانات. لو في Contract بيستخدمه أكتر من Consumer، ممكن تستخرجه لـ API Module صغيرة. لكن تقسيم كل Feature إلى `api` و`impl` مش قاعدة إجبارية، ووجود Dependency مباشرة بين Features مش كارثة تلقائية لو العلاقة واضحة ومافيش Cycle. مشاركة بيانات دائمة تكون من Data Layer، ونتيجة Checkout تحتاج مسار نتيجة أو حالة محفوظة موثوقة حسب Lifecycle، مش Global Event Bus بلا Ownership.

## Practical walkthrough

في Catalog، ضغط Checkout يطلع `CheckoutRoute(productId)` من Contract بسيطة. الـ app navigator يحولها لوجهة Checkout. Checkout تستقبل ID وتجيب التفاصيل الحالية من `ProductRepository`؛ ما تعتمدش على Cart Object mutable اتبعتت عبر Navigation. لو الطلب خلص، Checkout تعرض Order ID أو تكتب النتيجة في Repository موثوقة، وCatalog تحدث نفسها لما ترجع أو تراقب البيانات. اختبر التنقل والعودة وProcess Recreation لأن النتيجة اللحظية ممكن تضيع لو اعتمدت على Event لا يُعاد بثها.

## Why it matters and how it works

A mediator or narrow contract keeps UI implementation details local and makes data ownership explicit. It may reduce coupling, but extra API modules and app wiring have costs. Decide from actual cohesion and dependency edges, not an assumption that every split improves build time.

## Worked example

This runnable Kotlin/JVM contract shows a catalog action emitting a small route. The app can supply the real navigation callback.

```kotlin
data class CheckoutRoute(val productId: String)
class CatalogActions(private val openCheckout: (CheckoutRoute) -> Unit) {
    fun onBuy(productId: String) {
        require(productId.isNotBlank())
        openCheckout(CheckoutRoute(productId))
    }
}
fun main() {
    val opened = mutableListOf<CheckoutRoute>()
    CatalogActions(opened::add).onBuy("p-42")
    check(opened.single() == CheckoutRoute("p-42"))
}
```

## Trade-offs and decision criteria

App mediation keeps destination wiring central but grows app composition. API modules help a stable contract with multiple consumers but add project overhead. Deep links suit entry points that require their URI semantics and validation; they are not a universal replacement for internal navigation. An event flow needs ownership and delivery rules, especially for results.

## Failure modes

Passing a mutable cart object can restore stale price after process death. A SharedFlow with no collector can lose a result; replay may repeat a one-shot action. Direct imports of feature implementations may create a cycle or leak UI internals. Prefer IDs, owned repositories, and explicit result semantics.

## Production perspective

Document navigation, data, and result owners. Test app-level routes, invalid IDs, Back behavior, and process recreation. Inspect Gradle dependency edges for cycles and measure build impact before claiming a performance gain.

## Interview answer — short

First decide whether features need navigation, shared data, or a result. For navigation, catalog can emit `CheckoutRoute(productId)` and an app mediator opens checkout; checkout reloads current data by ID. A shared repository owns durable data. A separate API module helps a stable contract but is not required for every feature, and a global event bus is not a default answer.

## Interview answer — structured

If catalog opens checkout, it need not import `CheckoutViewModel` or screen implementation. It emits a route with `productId`; the app module that owns navigation maps it to checkout. Checkout loads current price and stock from an owning repository rather than receiving a mutable cart object.

A small API module can hold a stable contract used by several features, but splitting every feature into API and implementation adds wiring. A direct dependency is not forbidden in every design; the questions are whether it leaks internals, makes a cycle, or causes unwanted change propagation.

For checkout completion, choose a result channel or durable repository state according to what the result means. An uncollected SharedFlow event can be lost, and careless replay can repeat an action. I would test Back and process recreation as well as the initial navigation.

## Interview answer — deep senior

Separate three relationships: a navigation request, shared domain data, and the result of checkout. Android modularization guidance shows an app mediator owning the navigation graph. Catalog supplies a destination and product ID; checkout obtains authoritative state from the repository. Small IDs are easier to restore and keep current than passing an entire mutable cart across feature boundaries.

Where several consumers need a stable contract, extract a small API module and keep implementation details behind it. But every feature does not require an API/impl pair. A direct dependency inside a cohesive area may be reasonable if its direction is clear and it does not introduce a cycle. DI can wire a navigator or repository, but it does not define the right boundary for you.

The data layer owns durable cart and order state. If checkout returns a one-shot UI result, choose a result path that fits the navigation lifecycle; if the order outcome must survive process death, persist and query it. A global SharedFlow without collectors can drop a result, while replay can trigger duplicates. Deep links can serve external entry points but require argument validation and distinct semantics from internal routes.

In production I would test app composition, route arguments, Back stack, and process recreation. I would inspect dependency edges for cycles and measure actual build impact rather than assume each new module speeds Gradle.

## How to answer in the interview

- **Classify:** navigation, shared data, or result.
- **Example:** catalog emits a product ID; app mediates checkout navigation.
- **State:** repository owns current product and order data.
- **Trade-off:** API module only for a useful shared boundary.
- **Failure:** event loss or stale mutable navigation argument.

## Deep-dive talking points

App navigation mediator, stable IDs, repository source of truth, selective API/impl split, result delivery, SharedFlow replay, deep-link validation, and Gradle dependency cycles.

## Follow-up questions

- **Interviewer:** "Why not pass the full cart in navigation?"
  **Answer:** "It may be mutable or stale, and restoration after process death is harder. Pass an ID and load current state from its owner."

- **Interviewer:** "Are direct sibling feature dependencies always forbidden?"
  **Answer:** "No. Evaluate cohesion, cycles, and exposed implementation details. Extract a contract or use app mediation when independence matters."

## Self-check rubric

Identify communication type and owner, pass an ID, describe result behavior after Back/process recreation, and give a non-dogmatic module boundary decision.

## References and reviewed-on date

- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — app mediation, contracts, and IDs.
- [Android Navigation](https://developer.android.com/guide/navigation) — navigation graphs and destinations.

Technically reviewed against Android primary documentation on 2026-10-19.
