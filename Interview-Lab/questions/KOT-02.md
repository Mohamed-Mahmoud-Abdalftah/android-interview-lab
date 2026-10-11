---
id: "KOT-02"
question: "What is the difference between val and var? Does val guarantee immutability?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 2
editorial_status: "reviewed"
---

# KOT-02

## Original interview question

What is the difference between val and var? Does val guarantee immutability?

## What the interviewer evaluates

Separate reference reassignment from object mutability, and recognize concurrency implications of both.

## Explanation in Arabic

`val` يمنع إعادة إسناد الـreference بعد التهيئة؛ `var` يسمح بإسناد قيمة جديدة. ده مش معناه إن object جوّه `val` بقى immutable. `val items = mutableListOf(...)` يفضل ممكن نعمل له `add`، وأي alias شايف نفس الـlist. حتى `List<T>` في Kotlin read-only interface مش ضمان deep immutability أو thread safety. خليك واضح بين reference ثابت، snapshot غير قابل للتعديل، وownership يمنع مشاركة mutable state.

## Why it matters and how it works

The compiler rejects reassignment to a local `val`, which simplifies reasoning about that binding. It does not freeze the object graph. A `var` can be safe when local and confined; a shared `val` that references mutable data can race. APIs should expose read-only views or copies as appropriate and document ownership.

## Worked example

Runnable JVM illustration; `val` binds the same mutable list throughout.
```kotlin
fun main() {
    val items = mutableListOf("A")
    items += "B" // legal mutation
    // items = mutableListOf("C") // compiler error
    println(items) // [A, B]
}
```

## Trade-offs and decision criteria

Use `val` by default to limit reassignment, but choose immutable data and controlled state transitions when consumers need stable snapshots. Copying a large collection has cost; persistent collections or confinement may be useful. `var` is legitimate for local loop state or a synchronized private field.

## Failure modes

A ViewModel exposes `val items: List<Item>` while retaining and mutating its `MutableList`. A consumer can observe changing contents without a new state emission. Publish a fresh list snapshot, or use a properly synchronized state holder; never infer thread safety from `val`.

## Production perspective

In an inventory screen, repository updates produce immutable `InventoryUiState(items = fetched.toList())`. The ViewModel exposes a read-only state stream. Concurrent writers use one serialized owner or atomic state update, and tests verify that old snapshots remain unchanged.

## Interview answer — short

`val` prevents rebinding a variable; `var` permits reassignment. Neither determines whether the referenced object can mutate. A `val` holding a `MutableList` is mutable through that reference and is not automatically thread-safe.

## Interview answer — structured

I default to `val` because a stable binding is easier to reason about. But `val list = mutableListOf()` still allows adding elements, and aliases can mutate it too. Kotlin `List` is a read-only interface, not a deep immutable guarantee. For UI state I publish a new immutable snapshot, and for shared data I add confinement or synchronization. A local `var` can be perfectly fine when it has a clear owner. For example, a `val` holding a mutable list can still accept `add`, and another reference to that list can change it too. In a UI state API I would keep mutable storage private and publish a fresh snapshot, then use a serialized writer or atomic transformation when multiple producers exist. That separates readability, immutability, and synchronization instead of conflating them.

## Interview answer — deep senior

I would review three separate axes: can the variable be rebound, can the object graph mutate, and can multiple threads access it safely. `val` answers only the first. A supposedly read-only collection may wrap mutable backing storage; even a defensive copy can contain mutable elements. In an Android state holder I favor immutable models and atomic updates. When copy cost matters, I measure and choose an appropriate persistent data structure or single-writer model, not a blanket rule against `var`. I would ask what exactly is meant by immutable. `val` freezes one binding after initialization; it says nothing about nested objects, aliases, or concurrent access. A Kotlin `List` only removes mutation methods from that reference, while the source may still change. A data-class copy is shallow, so nested mutable members can remain shared across snapshots. When a ViewModel emits state, I prefer immutable members and a new state value so equality and rendering are predictable. If multiple coroutines update a counter or list, I guard the whole read-modify-write operation, not just individual calls. A local `var` can improve an algorithm if its ownership is obvious. I would document whether an API returns a snapshot or a live view, because that contract matters more than the keyword on one property.

## Deep-dive talking points

Discuss aliases, shallow versus deep immutability, data-class `copy` with mutable members, and the Java memory model for shared mutable state.

## Follow-up questions

- [KOT-25](../kot-25/): Is a shared `val MutableList` thread-safe? **Answer:** no; binding stability supplies no synchronization.
- [KOT-16](../kot-16/): Does Kotlin `List` prove immutable storage? **Answer:** no; it exposes read-only operations but backing data may change.

## Self-check rubric

Can you demonstrate legal mutation through `val`, explain why `List` is only read-only, and name one safe shared-state strategy?

## References and reviewed-on date

- [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html) — `val` and `var`.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — read-only versus mutable collection interfaces.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
