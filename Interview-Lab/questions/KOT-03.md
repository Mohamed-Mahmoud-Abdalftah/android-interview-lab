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

## Practical walkthrough

اعتبر قيمة `token` جاية من Java SDK أو JSON field: `raw?.trim()?.takeIf { it.isNotEmpty() }` بيرجع `null` لو مفيش قيمة صالحة، و`?:` لازم يعبّر عن fallback مقصود. في authentication ما تستبدلش missing token بـ`"guest"` وتكمّل الطلب؛ ارجع failure واضح أو اطلب login. `!!` مناسب فقط لو عندك invariant متحقق ومخالفتها تستاهل crash، والأفضل غالبًا `requireNotNull` برسالة واضحة عند boundary. الـsafe call تمنع dereference للـnull لكنها ما تتحققش من business validity زي expiry أو blank text.

## Trade-offs and decision criteria

Use nullable return for ordinary absence, a sealed result for distinct failures, and a non-null type when absence is invalid. Safe-call chains are concise but can hide which hop was null. `!!` is acceptable only when a proved invariant is close and failure should crash clearly; `requireNotNull` can name that invariant.

## Failure modes

A Retrofit/Java boundary may expose `String!` with uncertain nullability. Assigning it directly to non-null and dereferencing can throw. Validate at the boundary. Another mistake is using `?: emptyList()` for a failed database read, making an outage look like a genuine empty dataset.

## Production perspective

A profile repository maps nullable transport fields to a validated domain model. Optional nickname stays nullable; required account ID produces a typed validation error if missing. The UI sees either valid state or a visible error rather than silently accepting corrupt data.

## Interview answer — short

Kotlin marks nullable values with `?`. A safe call propagates null, and Elvis supplies a deliberate fallback or early return. `!!` asserts non-null and can crash. I validate external values before turning them into a non-null domain contract.

## Interview answer — structured

The key distinction is between a type guarantee and a valid business value. A nullable `String?` forces me to handle absence; `?.` safely continues only when present, and `?:` lets me return an error or choose a justified default. `!!` converts uncertainty into a possible runtime exception, so I reserve it for a proven invariant and prefer explicit validation at Java or parsing boundaries. For an auth token, I would not silently default a missing value: I would return an authentication failure, then verify expiry and scope separately. Kotlin’s null checks reduce a class of bugs but do not validate the content.

## Interview answer — deep senior

The compiler performs smart casts after stable null checks and propagates nullable results through safe calls. That makes API contracts readable, but it does not validate untrusted JSON or unannotated Java code. I normalize such data once at the boundary and avoid spreading `!!` through the app. If absence is exceptional, a precondition with a useful message or a domain error carries better information. I also avoid swallowing failures into default values when the UI needs to distinguish empty from unavailable.

For a token from an unannotated Java SDK, I would first assign to `String?`, trim and validate it, and return a named authentication failure if it is absent. `raw?.trim()` only protects the dereference; it does not prove the token is nonblank, unexpired, or authorized. `?: "guest"` would be dangerous if it silently turns an authentication fault into a different account path. I reserve `!!` for a genuinely enforced invariant and explain the crash if it is violated. A unit test should cover null, blank, malformed, and valid input at that boundary.

## How to answer in the interview

- **Why:** Move nullability checks to compile time to eliminate avoidable null dereferences.
- **How:** Combine safe calls (`?.`), Elvis operator (`?:`), and smart casting to handle absent values gracefully.
- **Trade-offs:** Overusing default fallbacks with Elvis (`?: 0`) can mask critical business errors and conceal missing data defects.
- **Failure cases:** Using not-null assertion (`!!`) on nullable fields, causing fatal runtime crashes upon receiving incomplete backend responses.
- **Production solution:** Enforce typed domain models, validate network and database payloads at system boundaries, and reserve `!!` only for test assertions or provable invariants.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
