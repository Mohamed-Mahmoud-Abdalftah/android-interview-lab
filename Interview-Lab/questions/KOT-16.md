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

## Practical walkthrough

`List<T>` في Kotlin read-only API: caller ما عندوش `add` من النوع ده، لكن ممكن تكون view فوق `MutableList` متشاركة؛ `val view: List<Int> = mutable` مش snapshot. `MutableList` تضيف mutation API، و`ArrayList` implementation معينة تدي random access سريع غالبًا لكن insert في النص مكلف. `Sequence` pipeline lazy بتتستهلك عند terminal operation؛ مش collection محفوظة تلقائيًا، وممكن تعيد شغلها كل مرة. في UI state ابعت `toList()` snapshot لو محتاج ثابت، وجرّب أداء eager List مقابل Sequence حسب حجم input ووجود short-circuit.

## Trade-offs and decision criteria

Return `List` for a stable, finite result; use a defensive copy when callers require a snapshot. Keep `MutableList` private unless mutation is part of the contract. Prefer eager collection operations for small data or repeated reads; sequence can help long chains and early termination on large inputs.

## Failure modes

A repository returns `List` backed by its mutable cache, then mutates the cache while the UI renders, causing surprising changes or concurrent modification. Snapshot or serialize ownership. A sequence over a changing source may yield different results on later iterations.

## Production perspective

A paged product repository emits immutable page snapshots as `List<Product>`. A one-pass import processor uses `Sequence` for a long transformation chain, but measured memory and latency determine whether it is worthwhile.

## Interview answer — short

`List` exposes read operations; `MutableList` adds mutation. `ArrayList` is one mutable implementation. `Sequence` describes a lazy pipeline that runs when consumed. A read-only reference is not necessarily an immutable snapshot, so I choose by ownership and workload.

## Interview answer — structured

I distinguish API surface from storage. Kotlin `List` prevents mutation through that reference, but another alias may still mutate the backing collection. `MutableList` exposes writes, and `ArrayList` is a concrete resizable array with different costs for indexed reads and middle insertions. A `Sequence` is an intermediate lazy view: operations run when a terminal operation consumes it, and repeating consumption can repeat work. For stable UI state I keep mutation private and publish a snapshot. For a large filter-map-first pipeline I consider a sequence; for small collections, direct list operations can be simpler and faster after measurement.

## Interview answer — deep senior

The key question is whether the API promises a stable snapshot or merely a read-only view. Kotlin read-only collections are not deep immutable, and aliases can mutate backing storage. ArrayList offers fast indexed access but shifting costs for middle inserts. Sequence fuses stages per element and can stop early, yet repeated consumption reruns the pipeline, and stateful steps like sorting still buffer. In Android I keep mutable storage private, publish snapshots, and profile large transformations on representative devices. I review these types along two axes: mutation rights and evaluation strategy. `List` removes mutation methods from the caller's view, yet a different alias can still mutate the backing data. `Sequence` defers operators until a terminal operation, often fusing stages and allowing early termination.

For a product list shown in UI, I would keep an `ArrayList` or other mutable implementation private and publish a copied `List` only when the screen needs a stable snapshot. A `List` typed property alone could still point to that same mutable backing object, and nested mutable products could still change. A `Sequence` is not a replacement collection: it runs its pipeline on consumption and may rerun expensive mapping on the next traversal. I would choose it for a large filter-map-first search with early termination, while preferring ordinary eager operations for small lists unless profiling shows a real gain.

## How to answer in the interview

- **Why:** Select the right collection abstraction for mutability contracts, performance, and memory consumption.
- **How:** Use `List` for read-only interfaces, `MutableList`/`ArrayList` for mutable buffers, and `Sequence` for multi-step lazy transformations.
- **Trade-offs:** Standard `Iterable` chains allocate intermediate collections at each step; `Sequence` avoids intermediate allocations but introduces iterator overhead for small lists.
- **Failure cases:** Casting an external `List` to `MutableList` and modifying it, breaking caller immutability assumptions and causing concurrency bugs.
- **Production solution:** Expose read-only `List` publicly, use `toPersistentList()` or defensive copies for state emissions, and switch to `Sequence` only for large or unbounded datasets.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
