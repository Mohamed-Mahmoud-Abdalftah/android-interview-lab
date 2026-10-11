---
id: "SYS-12"
question: "How do you make a reusable Android SDK with a stable public API?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 341
editorial_status: "reviewed"
---

# SYS-12

## Original interview question

How do you make a reusable Android SDK with a stable public API?

## What the interviewer evaluates

Design reusable Android SDK with narrow stable API, lifecycle ownership and compatibility tests.

## Explanation in Arabic

SDK عامة لازم API صغيرة واضحة لا تسرّب Activity أو تفاصيل transport، وتعرّف threading, cancellation, errors وresource ownership. ننشر semantic versions ونحدد minSdk/AGP/Kotlin compatibility وconsumer R8 rules لو reflection/JNI. نختبر sample app debug/release، API binary compatibility، Java/Kotlin callers، process death حسب الحاجة، ومين مسؤول عن secrets؛ SDK client مش موثوق لسر server.

## Why it matters and how it works

Public API changes impose compatibility burden; use interfaces/data types cautiously and keep implementation internal. Avoid global singleton state that crosses users or leaks Context. Lifecycle-sensitive operations should accept an owner or expose suspend/Flow APIs with explicit cancellation. Provide dependency injection or factory configuration without forcing host architecture.

## Worked example

Conceptual Kotlin public contract with closeable client; implementation is hidden and must document callback dispatcher.

```kotlin
interface PaymentsClient : AutoCloseable {
    suspend fun status(operationId: String): PaymentStatus
    fun observe(operationId: String): kotlinx.coroutines.flow.Flow<PaymentStatus>
}
interface PaymentsClientFactory {
    fun create(config: PaymentsConfig): PaymentsClient
}
// Public types/config must remain compatible; backend owns authorization.
```

## Trade-offs and decision criteria

A small API is harder to customize but easier to maintain; exposing many internals creates binary-break and R8 risk. Bundling dependencies can increase app size/conflicts. A stable SDK may need adapter modules for Compose/Views rather than forcing either on all hosts.

## Failure modes

Leaking an Activity Context from a singleton SDK causes memory leaks. Public `inline` functions or data classes can create unexpected binary/source compatibility constraints. Reflection without consumer rules may crash only in release. Embedded API secrets can be extracted.

## Production perspective

A payments SDK publishes core Kotlin API, optional UI adapter, consumer R8 rules and a sample app. CI tests min/max supported versions, release minification, cancellation and malicious input. Operational docs specify backend idempotency and status recovery.

## Interview answer — short

“I expose a narrow documented contract with explicit lifecycle, threading, errors and versioning. I keep implementation internal, test binary/release compatibility and ship consumer R8 rules when needed. The backend—not SDK code—enforces security.”

## Interview answer — structured

“A reusable SDK is a product with a compatibility promise. I design a small public API that does not expose host Activities or internal transport types, document which calls suspend and who owns cancellation, and let the host inject configuration. I publish semantic versions, support a defined Android/Kotlin range and test both Kotlin and Java consumers. Release builds need R8 testing and consumer rules for reflective code. I keep secrets and authorization on the backend, because any APK-embedded value can be extracted. Bundling dependencies can increase app size/conflicts.”

## Interview answer — deep senior

“I would set the public contract before coding: inputs, outputs, error taxonomy, thread/coroutine behavior, ownership and shutdown. Public ABI changes are expensive, so implementation details stay internal and cross-cutting adapters are optional artifacts. A client may expose suspend/Flow calls but must define whether collecting twice starts two requests and how cancellation affects transport. I avoid retaining Activity references, document DI/factory configuration and test with host apps across supported minSdk, Kotlin/AGP versions and R8 minification. Consumer keep rules are shipped only when required by reflection/JNI, then verified in release. I publish API diffs and migration notes, and I never pretend a mobile SDK can securely hold a server secret or guarantee payment idempotency alone. Embedded API secrets can be extracted.”

## Deep-dive talking points

Trace public ABI, lifecycle, host integration, release shrinker and security authority.

## Follow-up questions

- [MOD-16](../mod-16/): How publish library? **Answer:** versioned artifact with compatibility/release tests and consumer rules.
- [BLD-07](../bld-07/): What are consumer rules? **Answer:** shrinker rules packaged for apps consuming a library.

## Self-check rubric

Can I specify API/lifecycle contracts, test host release builds and protect backend secrets?

## References and reviewed-on date

- [Android library publishing](https://developer.android.com/build/publish-library) — artifacts and consumers.
- [Android architecture guide](https://developer.android.com/topic/architecture) — ownership boundaries.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
