---
id: "SOL-17"
question: "A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 188
editorial_status: "reviewed"
---

# SOL-17

## Original interview question

A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?

## What the interviewer evaluates

Recognize a likely LSP violation while allowing legitimately optional contracts.

## Explanation in Arabic

`UnsupportedOperationException` من subclass لmethod موجودة في base علامة قوية إن subtype مش قادرة تلتزم بالcontract. لو `Storage.save()` promised للكل و`ReadOnlyStorage.save()` ترمي، caller لازم يعرف النوع ويتجنب method؛ substitution فشلت. ممكن الحل `ReadableStorage` و`WritableStorage` منفصلين (ISP) أو composition/Capability flag واضح. لكن لو base contract مصرح صراحة إن العملية optional أو method default ممكن ترمي لمدخلات معينة، الحكم يعتمد على الوعد الحقيقي؛ ما تقولش كل throw في subtype LSP violation تلقائيًا.

## Why it matters and how it works

LSP is judged by behavioral expectations for valid calls. An unsupported operation often means the base abstraction promised too much. Narrow capabilities can let clients request exactly what they need.

## Worked example

Conceptual Kotlin: `interface Reader { suspend fun read(id: String): Data? }` and `interface Writer { suspend fun save(data: Data) }`; a read-only cache implements only `Reader`. A writable store implements both. Callers needing `save` depend on `Writer`, not a broad `Storage`.

## Trade-offs and decision criteria

Splitting interfaces adds types but makes capabilities explicit. A documented partial operation can be valid in some APIs, though callers must handle its result and it may be less ergonomic. Avoid subclass checks as the primary design.

## Failure modes

A UI expects all repositories to support refresh; a local-only subclass throws when the refresh button is tapped. The crash appears only in one build variant. Contract tests reveal the mismatch; redesign interface or UI capability selection.

## Production perspective

A document app has read-only shared files and editable local files. It exposes read and write capabilities separately, and UI derives whether Edit is available from the actual domain permission, not a subclass name.

## Interview answer — short

A subclass throwing `UnsupportedOperationException` for a valid base operation is a likely LSP violation: callers can no longer substitute it safely. I narrow the contract or split capabilities, while checking what the base actually promises.

## Interview answer — structured

LSP is about behavior, not signatures. If callers are promised that any `Storage` can save, a read-only subclass that throws for every save breaks that promise. The caller now needs a subtype check, which signals the abstraction is wrong. I would separate read and write capabilities or use composition so clients request only supported behavior. I also inspect the documented contract; an operation explicitly optional for all implementations changes the analysis. One option is to model the operation as a result such as `Unsupported` for all implementations, if unsupported is genuinely part of the domain contract. Otherwise, capability interfaces make compile-time promises stronger: a caller needing save accepts `Writer` only.

## Interview answer — deep senior

The strongest clue is that a client must ask “which subclass did DI give me?” before making a valid call. That means the base type no longer captures a reliable behavior. I write contract tests against each implementation with valid inputs, cancellation and failure paths. If one cannot support a method, I split the interface by capabilities or return an explicit domain outcome when unavailability is a legitimate case. I do not automatically label every thrown exception an LSP violation: invalid input or a documented transient failure may be part of the contract. `UnsupportedOperationException` for a normally valid operation is different. In Android, this matters for provider adapters and screen base classes, where hidden special cases cause production-only crashes. For Android adapters I include threading and cancellation in the behavioral contract. A supposedly replaceable SDK wrapper that blocks Main or ignores cancellation may technically return the same value while still breaking caller expectations. Contract tests should exercise valid operations across implementations, with integration tests for device-specific behavior. I avoid broad interfaces that require no-op methods. If an operation is optional by design, I state that explicitly and make the UI adapt to the capability, rather than letting a runtime exception reveal it unexpectedly.

## Deep-dive talking points

Contrast invalid input failure with unsupported valid operation; design capability interfaces and contract tests.

## Follow-up questions

- [SOL-04](../sol-04/): What is the behavioral test? **Answer:** every subtype honors valid base expectations.
- [SOL-05](../sol-05/): Which other principle helps? **Answer:** ISP can split read and write capabilities.

## Self-check rubric

State the base promise, classify a thrown case correctly, and redesign a read-only subtype.

## References and reviewed-on date

- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — substitution.
- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — override mechanics.

Technically reviewed against the linked primary design/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
