---
id: "KOT-17"
question: "Explain lazy sequences versus eager collection operations."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 17
editorial_status: "reviewed"
---

# KOT-17

## Original interview question

Explain lazy sequences versus eager collection operations.

## What the interviewer evaluates

Explain stage ordering, terminal execution, intermediate allocations, and one-shot/side-effect hazards.

## Explanation in Arabic

Collection operators المعتادة eager: كل مرحلة زي `filter` تنتج نتيجة قبل `map` التالية. `Sequence` lazy: العناصر تعدي على مراحل pipeline واحد واحد لما تطلب terminal operation زي `toList` أو `first`. ده ممكن يوفر intermediate lists ويوقف بدري عند `first`، لكن overhead الـiterator والـlambdas ممكن يخليه أبطأ مع قوائم صغيرة. `sorted` حتى داخل Sequence محتاج يجمع العناصر، وside effects جوه `map` مش هتشتغل إلا وقت الاستهلاك وقد تتكرر لو استهلكت sequence تاني.

## Why it matters and how it works

Lazy and eager pipelines have different execution timing and memory profiles. Correctness depends on when source data is read and whether transformations have side effects. Performance depends on input size, pipeline shape, and terminal operation.

## Worked example

Runnable JVM example: only values needed by `firstOrNull` pass through the lazy pipeline.
```kotlin
fun main() {
    val answer = (1..1_000_000).asSequence()
        .map { it * 2 }
        .firstOrNull { it > 20 }
    println(answer) // 22
}
```

## Trade-offs and decision criteria

Eager lists are simple, reusable snapshots and often faster for small inputs. Sequence helps long chains with large data or early stop. A stateful operator like `sorted` materializes internally; a terminal `toList` allocates the final list regardless.

## Failure modes

Code builds `source.asSequence().onEach { saveToDb(it) }` but never consumes it, so no write occurs. Side effects in lazy chains are also repeated if iterated twice. Keep effects explicit and use `forEach` or a transaction, not a hidden mapping stage.

## Production perspective

An import screen filters a large local stream and stops at the first matching record; sequence can reduce work. For a short list of UI chips, eager operators are clearer. Profile on representative devices and avoid processing the entire input on Main.

## Interview answer — short

Eager collection operations execute each stage immediately and can allocate intermediate lists. A Sequence defers work until a terminal operation and processes elements through the pipeline, which helps some large or early-stop cases but adds overhead.

## Interview answer — structured

With a list, `filter().map()` generally creates an intermediate filtered list before mapping. With a Sequence, operations are recorded and run as elements are requested by a terminal operation. That can save allocations and stop early with `first`. It is not universally faster: small inputs, repeated traversal, or stateful steps such as sorting change the economics. I keep transformations pure and measure on the target workload. Suppose I search a million generated values for the first match after mapping. A sequence can stop as soon as that match appears, whereas an eager chain may build full intermediate lists. But if I need a small result list anyway, eager operations may be simpler and faster. I also avoid side effects in a lazy chain because constructing the sequence does not run them and traversing twice may repeat them.

## Interview answer — deep senior

I would trace execution rather than just count chained calls. A lazy pipeline reads source data at consumption time, so mutation between construction and consumption matters. Each traversal can repeat expensive work and side effects. Some operators must buffer, and materializing the final result still allocates. A good candidate is a large source with multiple stateless stages and early termination. I benchmark both approaches and ensure heavy processing is off the UI thread when necessary. The mental model is execution order. Eager `filter().map()` completes the first stage and materializes its result before the second stage. A Sequence records those stages and processes each requested element through them when a terminal operation pulls data. That can reduce peak memory and avoid work with `first`, but every element incurs iterator/lambda machinery, and stateful steps such as sorting still need buffering. A sequence with `onEach { writeToDb() }` does nothing without a terminal operation and may repeat writes if consumed twice. In production I keep transformations pure, make transactions explicit, and compare profiles with the actual collection size and terminal operation on representative devices.

## Deep-dive talking points

Compare horizontal versus vertical evaluation, terminal operators, stateful buffering, sequence reuse, and Android Main-thread budgets.

## Follow-up questions

- [KOT-16](../kot-16/): Is Sequence a stored collection? **Answer:** no; it describes deferred iteration over a source.
- [KOT-07](../kot-07/): What about captured values in sequence lambdas? **Answer:** they are read when the sequence executes, not necessarily when declared.

## Self-check rubric

Predict when `map` runs, name a terminal operation, and give one win and one loss case for lazy processing.

## References and reviewed-on date

- [Kotlin sequences](https://kotlinlang.org/docs/sequences.html) — evaluation order and examples.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
