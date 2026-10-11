---
id: "KOT-03"
question: "Explain Kotlin null safety, safe calls, Elvis operator, and the not-null assertion operator."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 3
editorial_status: "reviewed"
---

# KOT-03

## Original interview question

Explain Kotlin null safety, safe calls, Elvis operator, and the not-null assertion operator.

## What the interviewer evaluates

Explain nullable types and each operator precisely, including when `!!` is an explicit crash choice.

## Explanation in Arabic

Kotlin بتميّز `String` عن `String?` في الـtype system. `?.` تشغّل العضو فقط لو القيمة مش null وإلا ترجع null؛ `?:` تحدد fallback لو الطرف الشمال null؛ `!!` تقول للـcompiler “اعتبرها non-null” وتعمل NPE لو كانت null فعلًا. استخدام `?: return` أو error domain واضح غالبًا أفضل من سلسلة `!!`. لكن Java platform types، casts، وتهيئة properties ممكن تخرق الضمانات المعتادة، فلا تعتبر null safety حصانة مطلقة.

## Why it matters and how it works

The type checker makes absence visible at API boundaries. Safe calls can compose nullable results, while Elvis chooses recovery or early exit. The not-null assertion transfers the risk to runtime. Model expected absence separately from malformed or failed data; null is not always a suitable error channel.

## Worked example

Runnable JVM function: an absent or blank token returns `null`; the caller must choose an explicit fallback.
```kotlin
fun normalizedToken(raw: String?): String? =
    raw?.trim()?.takeIf { it.isNotEmpty() }

fun label(raw: String?): String = normalizedToken(raw) ?: "Guest"
```

## Trade-offs and decision criteria

Use nullable return for ordinary absence, a sealed result for distinct failures, and a non-null type when absence is invalid. Safe-call chains are concise but can hide which hop was null. `!!` is acceptable only when a proved invariant is close and failure should crash clearly; `requireNotNull` can name that invariant.

## Failure modes

A Retrofit/Java boundary may expose `String!` with uncertain nullability. Assigning it directly to non-null and dereferencing can throw. Validate at the boundary. Another mistake is using `?: emptyList()` for a failed database read, making an outage look like a genuine empty dataset.

## Production perspective

A profile repository maps nullable transport fields to a validated domain model. Optional nickname stays nullable; required account ID produces a typed validation error if missing. The UI sees either valid state or a visible error rather than silently accepting corrupt data.

## Interview answer — short

Kotlin distinguishes nullable and non-nullable types. `?.` safely accesses a nullable receiver, `?:` supplies a fallback, and `!!` throws if the value is null. I keep expected absence explicit and validate Java or network boundaries.

## Interview answer — structured

Nullability is encoded in the Kotlin type, so a `String?` needs a check before use. A safe call returns null if the receiver is null; Elvis chooses a fallback or early return. `!!` suppresses the compiler warning but creates a runtime NPE risk. I use null for normal absence, typed errors for failures with meaning, and inspect platform types from Java because their null contract may be unknown. Consider a profile endpoint: a missing optional nickname can reasonably stay nullable, while a missing required account ID is a validation failure that should be surfaced. I might use `?.` to normalize the nickname and `?:` to choose display text, but I would not turn a database outage into an empty profile by default. At a Java or JSON boundary, I validate once before constructing non-null domain models. That keeps the rest of the app's null contracts honest.

## Interview answer — deep senior

The compiler performs smart casts after stable null checks and propagates nullable results through safe calls. That makes API contracts readable, but it does not validate untrusted JSON or unannotated Java code. I normalize such data once at the boundary and avoid spreading `!!` through the app. If absence is exceptional, a precondition with a useful message or a domain error carries better information. I also avoid swallowing failures into default values when the UI needs to distinguish empty from unavailable. There are several layers to null safety. Safe calls propagate absence; Elvis makes the fallback explicit; `!!` deliberately defers the failure to runtime. That still leaves interop and initialization hazards: platform types from Java, `lateinit` before assignment, explicit assertions, and malformed external data. For a production API I decide whether absence is normal. If it is, a nullable return is fine; if callers need cause and recovery, I use a typed outcome. I avoid long safe-call chains when they hide which field was missing. Tests cover nulls from transport and Java mocks, and diagnostics retain a useful error rather than silently substituting a plausible but false default.

## Deep-dive talking points

Compare smart casts, platform types, safe casts, `lateinit` failure, and why a nullable return differs from a typed failure result.

## Follow-up questions

- [KOT-23](../kot-23/): Why can a Java call defeat null safety? **Answer:** unannotated Java values become platform types with unknown null contract.
- [KOT-19](../kot-19/): When is `Result` better than `T?`? **Answer:** when callers need a cause or recovery category, not just absence.

## Self-check rubric

Explain all three operators, give a legitimate nullable return, and diagnose one path to a runtime NPE despite Kotlin typing.

## References and reviewed-on date

- [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html) — nullable types and operators.
- [Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html) — platform types.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
