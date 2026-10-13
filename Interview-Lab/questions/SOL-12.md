---
id: "SOL-12"
question: "How does strategy-based payment routing support OCP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 183
editorial_status: "reviewed"
---

# SOL-12

## Original interview question

How does strategy-based payment routing support OCP?

## What the interviewer evaluates

Use provider strategy to isolate variation while stating what remains in shared payment policy.

## Explanation in Arabic

Strategy-based routing مفيدة لما providers عندهم SDKs مختلفة لكن checkout عنده policy مشتركة: validate amount، request ID، server confirmation. `PaymentStrategy` ضيقة تعرف `submit` ونتيجة typed، وكل provider adapter يترجم callbacks والأخطاء. router يختار implementation من registry/DI حسب server-approved method. provider جديد يضيف adapter وbinding واختبارات من غير تعديل logic في عشر شاشات؛ ده OCP بشكل عملي. بس لو provider عنده semantics مختلفة جدًا، ما تجبرهوش على contract كاذب؛ راجع LSP أو افصل capabilities.

## Why it matters and how it works

Strategies isolate interchangeable algorithms behind a stable caller contract. Shared policy remains in the orchestration layer; provider-specific SDK mapping stays in adapters. Adding an implementation still needs registration and verification.

## Worked example

Conceptual Kotlin:
```kotlin
interface PaymentStrategy {
    val method: String
    suspend fun submit(request: PaymentRequest): PaymentOutcome
}
data class PaymentRequest(val minor: Long, val requestId: String)
sealed interface PaymentOutcome { data class Pending(val id: String): PaymentOutcome; data class Rejected(val code: String): PaymentOutcome }
```
Server status must later confirm completion; this snippet is a contract, not a transaction implementation.

## Practical walkthrough

في payment routing، `when(provider)` داخل checkout policy مع كل SDK جديد هيخلط قرار البيع مع تفاصيل providers. خلي `PaymentStrategy` تقدم `submit` ونتيجة واضحة، والrouter يختار الاستراتيجية المسجلة بناءً على method معروف. الإضافة غالبًا adapter وbinding واختبارات؛ policy يفضل ثابت. لكن متقولش إن OCP يمنع تعديل registration أو إنه يضمن صحة الدفع. كل strategy لازم تلتزم بمعنى `Pending` و`Rejected`، والbackend هو اللي يؤكد final status. اختبر duplicate tap وtimeout وunknown status عشان تكتشف اختلاف implementations مبكرًا.

## Trade-offs and decision criteria

For two fixed methods, an explicit `when` can be clearer. A strategy registry earns its cost when variation is frequent or provider code is large. Keep selection policy explicit; dynamic reflection discovery is not necessary for OCP.

## Failure modes

One adapter maps a timeout to `Rejected` while another maps it to `Pending`, breaking substitutability and retry safety. Define shared semantics and contract tests. Another failure is putting provider secrets in APK; backend owns them.

## Production perspective

A wallet app routes card and bank methods through adapters, persists request IDs, and reconciles uncertain outcomes with server. Provider-specific metrics are labeled without logging sensitive details.

## Interview answer — short

Strategy supports OCP by moving provider-specific behavior behind a stable contract, so a new provider adds an adapter and wiring instead of edits throughout checkout. I still test shared result semantics and server authority.

## Interview answer — structured

I define what is truly common: request ID, supported operation, typed outcome and cancellation behavior. The checkout policy depends on that contract, while card or wallet adapters translate SDK calls. A provider can be added through an implementation plus DI/registry wiring and tests, rather than scattered `when` branches. That is strategic extension, not a promise of zero edits. If providers differ too much to honor one contract, I split capabilities rather than force a misleading interface. The router should not make authorization decisions from a client-side `method` string alone. The backend must approve the method and the request.

## Interview answer — deep senior

OCP helps when provider variation is a recurring change axis. I keep validation, duplicate-submit policy and server reconciliation outside the strategies, so adapters cannot quietly redefine business rules. Each strategy maps its SDK’s callbacks into the same semantic outcomes: confirmed rejection, pending uncertainty, and confirmed status after server verification. I run contract tests against every implementation, including timeout, cancellation and duplicate callback behavior. Registration still changes when adding a provider, and product/security review still applies. If one provider cannot satisfy the shared contract, LSP warns that the abstraction is too broad. A small app with two stable providers may use an explicit switch instead. A strategy boundary keeps provider-specific SDK mapping out of checkout policy. The router selects an implementation using a validated payment method, and each strategy returns the same outcome vocabulary. A new provider adds an adapter and composition binding; it should not require rewriting eligibility rules. The trade-off is indirection and the danger that a common interface hides different provider semantics. I would use contract tests for rejection, pending, cancellation, and timeout, then provider-specific integration tests. I also keep an idempotency key and server-confirmed final state in the transaction flow. Strategy design supports local extension, but it cannot itself guarantee payment correctness.

## How to answer in the interview

- **Why:** Identify stable checkout policy.
- **How:** walk through adapter and router.
- **Trade-offs:** mention indirection.
- **Failure cases:** flag semantic mismatch and timeouts.
- **Production solutions:** finish with contract tests and server confirmation..

## Deep-dive talking points

Define strategy contract, shared policy, provider mapping, selection, contract tests and server reconciliation.

## Follow-up questions

- [SOL-03](../sol-03/): What does OCP protect? **Answer:** stable policy against repeated provider-specific edits.
- [SOL-04](../sol-04/): What if an adapter cannot honor outcome semantics? **Answer:** the strategy contract violates substitutability and should be refined.

## Self-check rubric

Add a third provider on paper and count which files change; include timeout and cancellation contract tests.

## References and reviewed-on date

- [Robert C. Martin, Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — adapter/repository boundary.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
