---
id: "KOT-16"
question: "What is the difference between List, MutableList, ArrayList, and Sequence?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 16
editorial_status: "reviewed"
---

# KOT-16

## Original interview question

What is the difference between List, MutableList, ArrayList, and Sequence?

## What the interviewer evaluates

Distinguish read-only and mutable interfaces, concrete array-backed implementation, and lazy processing.

## Explanation in Arabic

`List<T>` في Kotlin read-only API للقراءة، مش وعد إن backing storage immutable. `MutableList<T>` تضيف mutation operations. `ArrayList<T>` implementation معيّنة مبنية على array وتناسب random access وتضيف عناصر غالبًا بكفاءة amortized، لكن insert في النص يحرك عناصر. `Sequence<T>` مش collection مخزّنة؛ pipeline كسول من operations بيتنفّذ عند terminal operation، وقد يعيد computation في كل iteration. الاختيار حسب ownership، حجم البيانات، ونمط المرور، مش “Sequence أسرع دائمًا”.

## Why it matters and how it works

A return type communicates what callers may do. Exposing `List` prevents mutation through that interface, while a copied immutable snapshot guards against backing changes. Sequence defers transformation and can avoid intermediate lists, but adds per-element iterator and lambda overhead.

## Worked example

JVM illustration: `asSequence()` defers mapping until `toList()`.
```kotlin
fun main() {
    val source: MutableList<Int> = arrayListOf(1, 2, 3)
    val view: List<Int> = source
    val result = view.asSequence().filter { it > 1 }.map { it * 2 }.toList()
    println(result) // [4, 6]
}
```

## Trade-offs and decision criteria

Return `List` for a stable, finite result; use a defensive copy when callers require a snapshot. Keep `MutableList` private unless mutation is part of the contract. Prefer eager collection operations for small data or repeated reads; sequence can help long chains and early termination on large inputs.

## Failure modes

A repository returns `List` backed by its mutable cache, then mutates the cache while the UI renders, causing surprising changes or concurrent modification. Snapshot or serialize ownership. A sequence over a changing source may yield different results on later iterations.

## Production perspective

A paged product repository emits immutable page snapshots as `List<Product>`. A one-pass import processor uses `Sequence` for a long transformation chain, but measured memory and latency determine whether it is worthwhile.

## Interview answer — short

`List` is read-only to callers, `MutableList` allows mutation, `ArrayList` is a concrete mutable implementation, and `Sequence` is a lazy processing abstraction. I choose based on API ownership, snapshot needs, and measured pipeline cost.

## Interview answer — structured

I expose `List` when callers should read elements, but I remember the backing object may still be mutable. `MutableList` is a mutation contract; `ArrayList` is one implementation with array-backed trade-offs. `Sequence` builds a lazy pipeline and runs it at a terminal operation, often avoiding intermediate collections but adding overhead. For small UI lists, eager operations are usually clearer; for large one-pass pipelines, I measure both. For example, I would return a `List<Product>` from a repository because callers should not mutate its result, but if it aliases my mutable cache, I still need to decide whether that is a live view or a snapshot. An `ArrayList` is a useful concrete implementation for indexed access, not an ideal public return type by default. A `Sequence` is a pipeline rather than stored data and can repeat work when consumed again.

## Interview answer — deep senior

The key question is whether the API promises a stable snapshot or merely a read-only view. Kotlin read-only collections are not deep immutable, and aliases can mutate backing storage. ArrayList offers fast indexed access but shifting costs for middle inserts. Sequence fuses stages per element and can stop early, yet repeated consumption reruns the pipeline, and stateful steps like sorting still buffer. In Android I keep mutable storage private, publish snapshots, and profile large transformations on representative devices. I review these types along two axes: mutation rights and evaluation strategy. `List` removes mutation methods from the caller's view, yet a different alias can still mutate the backing data. `Sequence` defers operators until a terminal operation, often fusing stages and allowing early termination. It is not necessarily faster: small lists may pay more iterator overhead, a sorted sequence buffers, and iterating twice can recompute. For Android UI state I generally publish an immutable snapshot with a stable equality contract; for a large one-pass import I may use a sequence and measure memory and latency. API type choice should document ownership, not leak a mutable implementation accidentally.

## Deep-dive talking points

Discuss covariance of `List`, invariance of mutable containers, sequence terminal operations, intermediate collections and stateful operators.

## Follow-up questions

- [KOT-17](../kot-17/): When can lazy processing save work? **Answer:** early termination after chained operations on a large source.
- [KOT-25](../kot-25/): Is a read-only view thread-safe? **Answer:** no, not if backing storage mutates concurrently.

## Self-check rubric

Differentiate all four types, explain a snapshot versus view, and give one case where Sequence adds overhead.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection interfaces.
- [Kotlin sequences](https://kotlinlang.org/docs/sequences.html) — lazy processing.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
