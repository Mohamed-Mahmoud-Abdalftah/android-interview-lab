---
id: "PAT-15"
question: "Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 206
editorial_status: "reviewed"
---

# PAT-15

## Original interview question

Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?

## What the interviewer evaluates

Design multi-provider selection without centralizing every provider behavior in a single factory.

## Explanation in Arabic

لو عندك card/wallet/bank providers، Strategy contract ضيقة تمثل common submission/status semantics. Factory أو DI multibinding يختار adapter المناسب من registered implementations؛ ما تحطش callbacks، retries، UI strings، fraud rules كلها في `PaymentFactory` عملاقة. Shared checkout policy تراجع amount/request ID؛ adapter يترجم SDK، repository يحفظ pending/reconcile مع server. provider جديد يضيف adapter وbinding واختبارات. لو provider مش قادر يحقق نفس contract، افصل capability بدل `if(provider)` جوّه كل method.

## Why it matters and how it works

Strategy isolates interchangeable provider behavior; a factory or registry only selects or constructs it. Separating selection from execution prevents a god-factory and protects stable policy. Common outcome semantics matter more than class names.

## Worked example

JVM routing core; provider adapters and server verification are app-owned. Each strategy must satisfy the same `SubmitOutcome` contract and the repository persists the attempt identity before calling the router.
```kotlin
enum class PaymentMethod { CARD, WALLET }
sealed interface SubmitOutcome {
    data class Accepted(val receiptId: String) : SubmitOutcome
    data class Rejected(val reason: String) : SubmitOutcome
    data class PendingVerification(val attemptId: String) : SubmitOutcome
    data object UnsupportedMethod : SubmitOutcome
}
interface PaymentStrategy {
    val method: PaymentMethod
    suspend fun submit(attemptId: String): SubmitOutcome
}
class PaymentRouter(strategies: Set<PaymentStrategy>) {
    private val byMethod = strategies.associateBy(PaymentStrategy::method)
    init { require(byMethod.size == strategies.size) { "Duplicate payment method" } }
    suspend fun submit(method: PaymentMethod, id: String): SubmitOutcome =
        byMethod[method]?.submit(id) ?: SubmitOutcome.UnsupportedMethod
}
```
The router only selects; authentication, idempotency, redacted telemetry and reconciliation belong to the shared data boundary, with final authority on the server.

## Practical walkthrough

multiple payment providers: UI تبعت `PaymentMethod` وattempt، router صغير يختار `PaymentStrategy` من map محقون؛ كل strategy تنفذ نفس domain contract وتحوّل provider errors لـtyped outcome. Factory لو لازم تنشئ strategy حسب environment/session، لكن ما تخليش factory تعرف auth، UI، analytics، DB، وكل provider details مرة واحدة. shared policies زي idempotency/log redaction/reconciliation في coordinator أو repository boundary، مش copied في كل strategy ولا hidden في router. server يفضل authority. أضف provider جديد باختبار contract مشتركة وtest route unsupported؛ لا تستخدم default provider silently.

## Trade-offs and decision criteria

A simple `when` is enough for a stable two-provider app. A registry scales when providers change, but dynamic registration can hide duplicate keys or missing bindings; validate graph at startup/tests. Avoid reflection discovery without a real need.

## Failure modes

Factory branches on provider for every SDK call and silently maps wallet timeout to failure while card timeout is pending. Duplicate payment retry risk follows. Move mapping into adapters and enforce shared contract tests.

## Production perspective

A commerce app adds a bank transfer provider through one adapter and DI binding, then runs provider contract and backend reconciliation tests. Server holds credentials and authorizes charges.

## Interview answer — short

I separate provider behavior as Strategies from a small Factory or registry that selects one. A god-factory is avoided by keeping SDK translation in adapters and shared payment policy in a separate owner.

## Interview answer — structured

I define a narrow `PaymentStrategy` with common result and cancellation semantics. A router chooses a registered implementation based on an approved method, but it does not contain each provider’s SDK logic. Card, wallet and bank adapters translate their own callbacks. Checkout policy validates amount and request ID, while repository/server reconciliation handles uncertainty. I would test every strategy against the same contract and test the router for unknown or duplicate registrations. A small fixed app might use an explicit switch instead.

## Interview answer — deep senior

The design has three distinct responsibilities: deciding which provider is allowed, selecting an implementation, and executing provider-specific behavior. I keep the factory or registry limited to selection, with strategies handling SDK details and a repository coordinating durable request status. That prevents a giant class with a branch for every method and provider. I define semantic outcomes carefully: timeout means pending verification if the server may have committed; it is not a confirmed decline. Contract tests run across adapters, and server-side idempotency/reconciliation protects business effects. Adding a provider still needs wiring, security review and integration tests. If one provider cannot honor the common contract, I split capabilities or revise policy rather than hiding special cases in the factory.

I would separate selection from execution. A small router or factory maps a supported payment method to an injected Strategy, and each provider implementation returns the same domain outcomes. Shared rules such as stable operation IDs, server-side idempotency, redacted telemetry and reconciliation belong in a coordinator or repository boundary, not copied across provider classes. A god-factory appears when one object knows every SDK, UI flow, token rule and database detail; I keep it limited to choosing a registered implementation. I fail explicitly for an unsupported method rather than silently falling back to a provider. Contract tests run the same success, rejection and uncertain-outcome cases for each strategy, and the server remains authoritative.

## How to answer in the interview

- **Why:** Provider variation should stay local without centralizing every policy.
- **How:** Inject strategies, select by method, return one domain outcome type.
- **Trade-off:** Put shared policy in coordinator, not duplicated strategy code.
- **Failure case:** God-factory or silent fallback to wrong provider.
- **Production solution:** Common contract tests plus explicit unsupported-method outcome.

## Deep-dive talking points

Separate selection, strategy execution, shared policy and server status; test unknown/duplicate registration.

## Follow-up questions

- [PAT-09](../pat-09/): Strategy versus State? **Answer:** provider choice varies execution; checkout state tracks lifecycle.
- [SOL-12](../sol-12/): How does this support OCP? **Answer:** new provider behavior is added behind a stable seam.

## Self-check rubric

Sketch a router and one adapter, then name two responsibilities forbidden in the router.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Strategy and Factory patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository coordination.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-13. Conceptual examples are not device-tested.
