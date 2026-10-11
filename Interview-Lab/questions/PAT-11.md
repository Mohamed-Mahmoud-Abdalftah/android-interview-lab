---
id: "PAT-11"
question: "Where might Builder be useful in API or SDK design?"
topic: "Design Patterns"
code: "PAT"
group: "B"
phase: 2
priority: "P1"
order: 202
editorial_status: "reviewed"
---

# PAT-11

## Original interview question

Where might Builder be useful in API or SDK design?

## What the interviewer evaluates

Use Builder for complex validated configuration and discuss immutable result and failure on missing required values.

## Explanation in Arabic

Builder مفيدة لما SDK client عنده optional settings كتير: base URL، timeouts، interceptors، certificate/pinning policy حسب threat model. `build()` تتأكد إن required config موجودة وتطلع immutable object. Kotlin named/default parameters أحيانًا تخلي constructor كفاية، فلا تعمل Builder لموديل فيه fieldين. Builder لازم تمنع invalid combinations، وماتسمحش duplicate interceptors أو mutable config بعد البناء من غير قصد. وفي Android ما تحطش Activity context في client طويل العمر.

## Why it matters and how it works

Builder separates staged configuration from a constructed product and can enforce invariants at build time. It is especially useful for Java-facing SDKs and large optional configuration sets. Kotlin language features reduce some need for it.

## Worked example

Conceptual Kotlin:
```kotlin
class ClientConfig private constructor(val endpoint: String, val timeoutMs: Long) {
    class Builder {
        var endpoint: String? = null
        var timeoutMs: Long = 5_000
        fun build(): ClientConfig {
            val url = requireNotNull(endpoint)
            require(timeoutMs > 0)
            return ClientConfig(url, timeoutMs)
        }
    }
}
```
A real SDK also validates URL scheme and uses immutable interceptor copies.

## Trade-offs and decision criteria

Builder provides readable staged configuration and Java ergonomics but adds class/API surface. Kotlin `data class` or named parameters may suffice for simple immutable config. Prefer a factory if only choosing among implementations.

## Failure modes

`build()` accepts an empty endpoint, then failures appear only on the first network call. Validate early with clear errors. A builder that shares a mutable interceptor list with the client allows post-build mutation; copy it.

## Production perspective

A telemetry SDK builds a client from application context and validated endpoint/timeouts. Tests cover default values, invalid inputs and immutability; sensitive credentials are obtained at runtime from a trusted backend flow.

## Interview answer — short

Builder assembles an object through configuration steps and validates it before creation. It is useful for complex SDK clients and Java callers; a simple Kotlin constructor with named parameters may be clearer for small models.

## Interview answer — structured

I reach for Builder when construction has many optional settings or dependent validation. An SDK client might require an endpoint, positive timeout and compatible interceptors; `build()` can reject invalid combinations and return an immutable client. Kotlin named arguments reduce the need for a builder when configuration is small. I also review lifetime: a long-lived client should use application-scoped dependencies, not retain an Activity. Tests cover defaults, invalid input and post-build mutation.

## Interview answer — deep senior

A good Builder improves correctness, not just call-site style. It can collect options in stages, make required fields explicit, and validate cross-field constraints before an expensive client exists. I would design an immutable product and ensure the builder does not leak mutable collections into it. For Android SDKs, I review context scope, timeout defaults, callback executors and security options; a builder must not silently accept an HTTP endpoint where TLS is required. If the object has only two required fields, a constructor or factory is simpler and easier to maintain. For Java-facing APIs, builders can be more ergonomic than Kotlin default arguments, which Java does not see directly. I test the invalid configurations that production incidents would expose.

## Deep-dive talking points

Compare builder with Kotlin named constructor, validate dependent options and post-build immutability.

## Follow-up questions

- [PAT-03](../pat-03/): How differs from Factory? **Answer:** Builder configures one complex product over steps; Factory selects/creates a product.
- [KOT-23](../kot-23/): Why might Java SDK prefer Builder? **Answer:** Java callers lack Kotlin named/default arguments directly.

## Self-check rubric

Define two required settings, one cross-field rule, and a test proving immutable built configuration.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Builder pattern.
- [Kotlin functions](https://kotlinlang.org/docs/functions.html) — default/named arguments alternative.

Technically reviewed against the linked primary publisher/language/Android guidance on 2026-10-11. Conceptual examples are not device-tested.
