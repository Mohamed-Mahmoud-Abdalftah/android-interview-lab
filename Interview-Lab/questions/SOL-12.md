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

## Trade-offs and decision criteria

For two fixed methods, an explicit `when` can be clearer. A strategy registry earns its cost when variation is frequent or provider code is large. Keep selection policy explicit; dynamic reflection discovery is not necessary for OCP.

## Failure modes

One adapter maps a timeout to `Rejected` while another maps it to `Pending`, breaking substitutability and retry safety. Define shared semantics and contract tests. Another failure is putting provider secrets in APK; backend owns them.

## Production perspective

A wallet app routes card and bank methods through adapters, persists request IDs, and reconciles uncertain outcomes with server. Provider-specific metrics are labeled without logging sensitive details.

## Interview answer — short

Strategy supports OCP by moving provider-specific behavior behind a stable contract, so a new provider adds an adapter and wiring instead of edits throughout checkout. I still test shared result semantics and server authority.

## Interview answer — structured

I define what is truly common: request ID, supported operation, typed outcome and cancellation behavior. The checkout policy depends on that contract, while card or wallet adapters translate SDK calls. A provider can be added through an implementation plus DI/registry wiring and tests, rather than scattered `when` branches. That is strategic extension, not a promise of zero edits. If providers differ too much to honor one contract, I split capabilities rather than force a misleading interface. The router should not make authorization decisions from a client-side `method` string alone. The backend must approve the method and the request. I would also persist request identity so a timeout can be reconciled instead of blindly submitting again.

## Interview answer — deep senior

OCP helps when provider variation is a recurring change axis. I keep validation, duplicate-submit policy and server reconciliation outside the strategies, so adapters cannot quietly redefine business rules. Each strategy maps its SDK’s callbacks into the same semantic outcomes: confirmed rejection, pending uncertainty, and confirmed status after server verification. I run contract tests against every implementation, including timeout, cancellation and duplicate callback behavior. Registration still changes when adding a provider, and product/security review still applies. If one provider cannot satisfy the shared contract, LSP warns that the abstraction is too broad. A small app with two stable providers may use an explicit switch instead. The measure is whether a new provider changes only the adapter and composition boundary rather than many screens. The interface design is where OCP meets LSP. Each provider can differ internally, but the shared `PaymentOutcome` must mean the same thing to checkout. If one SDK reports a timeout after the server may have committed, its adapter must not fabricate a final rejection. I would define contract tests across all providers, then instrument production with correlation IDs and safe metrics. New provider work still includes DI registration, server configuration, fraud and compliance checks. An extension seam isolates code changes; it does not remove operational obligations.

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

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
