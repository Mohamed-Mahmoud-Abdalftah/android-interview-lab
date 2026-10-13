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

## Practical walkthrough

لو `val cartItems = mutableListOf<Item>()` موجودة في ViewModel، reference نفسها ثابتة بس أي caller ماسك القائمة يقدر يعمل `add`. وده معناه إن UI ممكن تشوف state اتغير من غير state emission. خلي القائمة private، ولما تنشر state ابعت snapshot زي `items.toList()` أو immutable model حسب احتياجك. حتى snapshot من list مش deep copy للعناصر المتغيرة؛ لو `Item` فيها mutable fields لازم تعالجها. ولو فيه كتابتين من threads مختلفة، `val` ما يعملش synchronization: حدّد owner واحد للتحديث أو lock/actor حسب الـinvariant.

## Trade-offs and decision criteria

Use `val` by default to limit reassignment, but choose immutable data and controlled state transitions when consumers need stable snapshots. Copying a large collection has cost; persistent collections or confinement may be useful. `var` is legitimate for local loop state or a synchronized private field.

## Failure modes

A ViewModel exposes `val items: List<Item>` while retaining and mutating its `MutableList`. A consumer can observe changing contents without a new state emission. Publish a fresh list snapshot, or use a properly synchronized state holder; never infer thread safety from `val`.

## Production perspective

In an inventory screen, repository updates produce immutable `InventoryUiState(items = fetched.toList())`. The ViewModel exposes a read-only state stream. Concurrent writers use one serialized owner or atomic state update, and tests verify that old snapshots remain unchanged.

## Interview answer — short

`val` prevents rebinding a variable; `var` allows rebinding. Neither makes the referenced object immutable. A `val` pointing to a mutable list can still change, and sharing that list across threads needs a separate concurrency strategy.

## Interview answer — structured

I separate binding, object mutability, and thread safety. `val` fixes which reference a property holds, while `var` allows assigning another value. A `val MutableList` can still be edited through that reference or an alias, and even a read-only `List` may be backed by mutable storage. In a ViewModel I keep mutable state private and publish stable snapshots or immutable state models. If several threads can update it, I also define serialization or locking; `val` provides no atomicity. I would test that observers receive a new state when content changes.

## Interview answer — deep senior

I would review three separate axes: can the variable be rebound, can the object graph mutate, and can multiple threads access it safely. `val` answers only the first. A supposedly read-only collection may wrap mutable backing storage; even a defensive copy can contain mutable elements. In an Android state holder I favor immutable models and atomic updates. When copy cost matters, I measure and choose an appropriate persistent data structure or single-writer model, not a blanket rule against `var`. I would ask what exactly is meant by immutable. `val` freezes one binding after initialization; it says nothing about nested objects, aliases, or concurrent access. A Kotlin `List` only removes mutation methods from that reference, while the source may still change.

Imagine a cart state holder with `val items = mutableListOf<Item>()`. Another caller can append to it, and a UI observer might never receive a new state value; a concurrent reader can also see an inconsistent iteration. I would keep that list private, update through one owner or an atomic state operation, and publish a snapshot or immutable model. If copying every update is costly, I would measure it and choose a suitable persistent collection or single-writer boundary. The interview point is that rebinding, deep mutability, and thread safety are three independent contracts.

## How to answer in the interview

- **Why:** Distinguish reference reassignment from underlying object mutability and thread safety.
- **How:** Use `val` for read-only references; expose immutable public snapshots (`List<T>`) while keeping mutations private.
- **Trade-offs:** Defensive copying for immutability incurs allocation overhead, while mutable collections risk concurrent modification and state divergence.
- **Failure cases:** Assuming a `val` list cannot be modified, allowing concurrent threads to append items and crash readers with `ConcurrentModificationException`.
- **Production solution:** Encapsulate mutable state in dedicated state holders, emit immutable data classes, and use atomic primitives or Mutex for concurrent updates.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
