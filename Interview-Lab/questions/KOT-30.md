---
id: "KOT-30"
question: "How would you review a Kotlin API for readability, null safety, and allocation cost?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 30
editorial_status: "reviewed"
---

# KOT-30

## Original interview question

How would you review a Kotlin API for readability, null safety, and allocation cost?

## What the interviewer evaluates

Present a repeatable API review: semantic clarity, null contracts, ownership, interop, and measured allocations.

## Explanation in Arabic

مراجعة Kotlin API أبدأها من use case عند caller: الاسم واضح؟ parameters وreturn types بيعبّروا عن domain؟ هل null معناها “مفيش نتيجة” ولا failure؟ لو في أكتر من outcome، sealed result أو error type أوضح من `Boolean`/`null`. راجع ownership: هل `List` snapshot ولا view mutable؟ هل callback بيتخزن أو بيتنادى فورًا؟ هل suspend function main-safe وبتحترم cancellation؟ بعدها راجع تكلفة hot path: copying collections، boxing value classes، reflection، lambdas، وJNI crossings—لكن قِس release build بدل التخمين. في Java boundary افحص platform types والتوقيع اللي Java شايفه.

## Why it matters and how it works

An API is consumed many more times than it is written. Clear contracts reduce misuse; null safety and ownership avoid runtime defects; allocation work matters only in actual performance-sensitive paths.

## Worked example

Illustrative API redesign: replace ambiguous `String?` with explicit outcome.
```kotlin
sealed interface Lookup {
    data class Found(val displayName: String) : Lookup
    data object Missing : Lookup
    data class Unavailable(val retryAfterSeconds: Int?) : Lookup
}
interface UserDirectory { suspend fun find(id: UserId): Lookup }
@JvmInline value class UserId(val value: String) {
    init { require(value.isNotBlank()) { "User ID must not be blank" } }
}
```
The interface contract must also state cancellation and dispatcher behavior; this snippet is not a network implementation.

## Practical walkthrough

في API review، بص على `find(id: String): String?`: هل `id` user ولا order؟ وهل `null` يعني missing ولا network failure؟ بدّلها بـ`UserId` validated و`Lookup.Found/Missing/Unavailable` لو caller محتاج يميّز. بعدين راجع concurrency contract لـ`suspend fun`: هل بتعمل blocking I/O؟ مين يملك cancellation؟ لو return list، هل هي snapshot ولا mutable alias؟ للكلفة، ما تحكمش من syntax: افحص allocations في hot path أو serialization loop بـprofiler، وقارن release build. أخيرًا اختبر Java interop لو API public، وأضف tests للnull/error/cancellation بدل الاكتفاء بـhappy path.

## Trade-offs and decision criteria

Explicit types add declarations but reduce caller guessing. A nullable return is fine for ordinary absence; typed outcome is better when failure categories matter. Defensive copies protect ownership but allocate; for large hot data, consider immutable/persistent structures or single-owner access after profiling.

## Failure modes

A `fun getUsers(): List<User>?` returns null for network failure and an empty list for no users, but callers conflate both and hide an outage. Another API takes a callback that silently escapes and captures an Activity. Document and redesign these contracts before micro-optimizing syntax.

## Production perspective

In a code review for an Android search SDK, inspect example call sites, Java consumers, lifecycle ownership, nullable transport mapping, error categories, cancellation and Main safety. Run allocation/startup traces on minified release with realistic result sizes, then record the measured trade-off.

## Interview answer — short

I review a Kotlin API in layers: clear names and domain types, explicit null and error meaning, ownership of mutable state, and measured allocation cost. For a suspending API I also document cancellation and blocking behavior. I verify public interop and release performance.

## Interview answer — structured

I begin with the caller’s question: can the signature tell them what to pass and how to handle every outcome? An ambiguous `find(String): String?` hides both ID meaning and whether null means absent data or a failure, so I prefer a validated ID and a named outcome when those distinctions matter. I then check mutable aliases, thread ownership, and cancellation behavior; `suspend` alone does not promise non-blocking work. For allocation cost I profile a representative release path instead of judging a scope-function chain by appearance. Finally, I test Java callers, serialization boundaries, and failure cases before publishing the API.

## Interview answer — deep senior

I use a checklist anchored in behavior. Names and parameter types should expose units and domain intent; default arguments should not hide unsafe behavior. Nullability is a contract, so platform types are normalized and expected absence is distinct from failure. I review whether returned collections are snapshots, whether callbacks escape, and whether suspend functions preserve cancellation and are main-safe. For performance I identify call frequency and data size, inspect generated code where relevant, and profile minified release builds on target devices. Finally I test representative Kotlin and Java call sites and document binary compatibility when the API is public.

I would review a real signature such as `suspend fun find(id: String): String?`. The ID type is ambiguous and null conflates not found with unavailable, so I would consider a validated `UserId` and a sealed Lookup outcome. I would then state whether the function can block, how cancellation propagates, and whether returned collections are snapshots or aliases. Allocation review comes after measuring a hot path: a value class may box in generics, a sequence may repeat work, and defensive copies may allocate. I test malformed inputs, Java call sites, and release traces before accepting the API, while keeping simple cases simple.

## How to answer in the interview

- **Why:** Ensure team APIs are idiomatic, maintainable, allocation-conscious, and resilient against runtime defects.
- **How:** Conduct code reviews assessing nullability contracts, collection mutability, scope function readability, and allocation efficiency under Android runtime constraints.
- **Trade-offs:** Over-optimizing syntax with clever idioms often harms readability and onboarding for mid-level team members.
- **Failure cases:** Approving PRs with ambiguous platform types, unnecessary `lateinit` properties, or unconstrained lambdas capturing UI contexts.
- **Production solution:** Establish team API style guides, enforce automated Detekt/ktlint rules in CI, and benchmark critical data paths using Jetpack Macrobenchmark.

## Deep-dive talking points

Discuss caller-first review, domain type design, null/error taxonomy, ownership, lifecycle, Java ABI, release profiling and compatibility.

## Follow-up questions

- [KOT-21](../kot-21/): Where might a value class allocate? **Answer:** nullable, generic, or interface use sites may require boxing.
- [KOT-23](../kot-23/): What Java boundary needs review? **Answer:** platform nullability, generated signatures, and callback lifetime.
- [KOT-27](../kot-27/): Should inline be automatic for performance? **Answer:** no; measure code-size and runtime effects.

## Self-check rubric

Review a sample API for ambiguous null, mutable ownership, cancellation and one measured allocation risk; propose a clearer signature.

## References and reviewed-on date

- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html) — API readability and platform-type guidance.
- [Android performance guide](https://developer.android.com/topic/performance) — measurement context.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
