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

فرق كثيرة تحتاج حدود واضحة: مين يملك domain data، مين يقدر يغيرها، وما هي public API والـSLO. feature modules تتواصل عبر interfaces/navigator contracts لا concrete implementation؛ :app يركّب DI. نستخدم versioned DTO/backend schemas، contract tests، deprecation window وownership docs. لا نرمي كل شيء في `core/common` لأن أي تغيير يكسر كل الفرق ويبطيء builds.

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

“I assign one owner and a narrow stable contract to each capability. Features depend on APIs rather than another team’s implementation, while the app composes bindings. Contract tests and compatibility windows protect parallel development.”

## Interview answer — structured

“A team boundary should make changes predictable. I define who owns each data type and mutation, then expose a small API describing outcomes, errors and lifecycle behavior. A checkout feature should depend on a payments contract, not its Room tables or Retrofit DTOs. The app composition root binds implementations. Contract tests run against providers and consumers, and breaking changes use versioning/deprecation windows. I keep shared core small and measure build graph and review bottlenecks before adding abstraction.”

## Interview answer — deep senior

“At scale, an interface alone is insufficient; the contract must specify threading/main safety, cancellation, result freshness, security authority, error taxonomy and compatibility. I separate public domain types from private wire/database models. The owning team publishes tests and migration notes, and consumers pin compatible versions when release trains differ. An acyclic dependency graph prevents feature-to-feature implementation coupling, while the app wiring layer resolves implementations through DI. I avoid both extremes: a monolithic common module that recompiles everything and hundreds of trivial modules that create coordination overhead. I track API churn, build impact and incident ownership as signals of boundary quality.”

## Deep-dive talking points

Walk one cross-team contract from type definition to runtime binding and rollout.

## Follow-up questions

- [MOD-09](../mod-09/): How features communicate? **Answer:** narrow contracts/event or navigation APIs with app composition.
- [SYS-19](../sys-19/): Why measure graph? **Answer:** API churn and dependencies drive rebuild and team coupling.

## Self-check rubric

Can I define owner, error/lifecycle contract, compatibility tests and dependency direction?

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module APIs and ownership.
- [Android architecture guide](https://developer.android.com/topic/architecture) — SSOT and layers.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
