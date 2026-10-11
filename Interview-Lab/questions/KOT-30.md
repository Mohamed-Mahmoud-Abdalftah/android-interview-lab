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
@JvmInline value class UserId(val value: String)
```
The interface contract must also state cancellation and dispatcher behavior; this snippet is not a network implementation.

## Trade-offs and decision criteria

Explicit types add declarations but reduce caller guessing. A nullable return is fine for ordinary absence; typed outcome is better when failure categories matter. Defensive copies protect ownership but allocate; for large hot data, consider immutable/persistent structures or single-owner access after profiling.

## Failure modes

A `fun getUsers(): List<User>?` returns null for network failure and an empty list for no users, but callers conflate both and hide an outage. Another API takes a callback that silently escapes and captures an Activity. Document and redesign these contracts before micro-optimizing syntax.

## Production perspective

In a code review for an Android search SDK, inspect example call sites, Java consumers, lifecycle ownership, nullable transport mapping, error categories, cancellation and Main safety. Run allocation/startup traces on minified release with realistic result sizes, then record the measured trade-off.

## Interview answer — short

I review a Kotlin API from the caller: clear names and types, explicit null and error meaning, ownership and lifecycle, then measured allocation cost. I also check Java boundaries and cancellation for suspend APIs.

## Interview answer — structured

First I write a realistic call site and ask whether the API is easy to use correctly. I inspect nullability: does `null` mean absence, or is it hiding a network failure? I check mutable collection ownership, callback lifetime, and coroutine cancellation/main safety. Then I inspect performance only where usage is hot: copies, boxing, reflection, and cross-language calls, using release-mode profiling. I favor a slightly more explicit type if it prevents invalid states or ambiguous errors. I would test the API by writing the caller code first. Can the caller tell missing data from a failed request? Does a returned `List` represent a snapshot or a live view? Can a callback outlive an Activity, and does a suspend function propagate cancellation? Once those contracts are clear, I would profile allocations on the actual hot path, including copies, boxing, reflection, or JNI crossings, rather than optimizing every expression.

## Interview answer — deep senior

I use a checklist anchored in behavior. Names and parameter types should expose units and domain intent; default arguments should not hide unsafe behavior. Nullability is a contract, so platform types are normalized and expected absence is distinct from failure. I review whether returned collections are snapshots, whether callbacks escape, and whether suspend functions preserve cancellation and are main-safe. For performance I identify call frequency and data size, inspect generated code where relevant, and profile minified release builds on target devices. Finally I test representative Kotlin and Java call sites and document binary compatibility when the API is public. My review has four passes. First, I look at names and domain types: identifiers, units, and return values should make invalid calls difficult. Second, I inspect null and error semantics; `null` is appropriate for ordinary absence but not a silent stand-in for an outage, and Java platform types need boundary validation. Fourth, I measure cost where it matters. A value class may box in generics, defensive copies allocate, reflection may affect startup, and inline may bloat DEX.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
