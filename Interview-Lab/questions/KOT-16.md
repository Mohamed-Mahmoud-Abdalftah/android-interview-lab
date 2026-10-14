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

المقارنة بين `List` و `MutableList` و `ArrayList` و `Sequence` بتكشف فهمك الحقيقي للـ Collections والـ Memory والـ API Design في Kotlin:

1. `List<T>` (Read-Only Interface):
   - في Kotlin، `List` هي **Read-Only Interface** وليست Immutable Collection بالمعنى الصارم. هي لا تحتوي على دوال تعديل (`add`, `remove`).
   - **نقطة جوهرية:** الكائن الفعلي اللي في الـ Heap ممكن يكون `MutableList` متخفي وراء واجهة `List`. لو كود تاني معاه reference لنفس الكائن وعدل فيه، قراءتك هتتغير!
   - علشان تضمن Immutability حقيقية، لازم تعمل defensive copy (زي `toList()` أو تستخدم Persistent Collections).

2. `MutableList<T>` (Mutable Interface):
   - بتورث من `List<T>` وبتضيف دوال التعديل (`add`, `clear`, `remove`). دي واجهة مش Implementation.

3. `ArrayList<T>` (Concrete Implementation):
   - هو الـ Class الفعلي المبني على Resizable Array في الـ JVM (`java.util.ArrayList`).
   - بيدي O(1) random access بالقراءة والكتابة بالـ Index، لكن إضافة عناصر في البداية أو المنتصف بتكلف O(N) بسبب إزاحة العناصر، وتكبير المصفوفة عند امتلاء الـ Capacity بيكلف O(N) allocation و copy.

4. `Sequence<T>` (Lazy Stream Pipeline):
   - مش مخزن عناصر في الـ Heap أصلاً! هو Pipeline من العمليات الكسولة (Lazy Evaluation).
   - بينفذ العمليات element-by-element (Vertical processing) ومش هيعمل أي حسابات إلا لما تنادي **Terminal Operation** (زي `toList()`, `first()`, `count()`).
   - بيمنع إنشاء Intermediate Lists في الذاكرة عند عمل عدة transformations متتالية.

## Practical walkthrough

في شاشة عرض قائمة الطلبات (Order History):
- عندنا 10,000 طلب جايين من Cache، وعايزين نفلتر الطلبات المكتملة، ناخد أول 5، ونحولهم لـ UI Model.
- **النهج الخاطئ مع Collections عادية:**
  `orders.filter { it.isCompleted }.map { it.toUiModel() }.take(5)`
  الكود ده هيعمل Loop كاملة على الـ 10,000 عنصر وينشئ New List في الـ Heap للـ filter، ثم New List ثانية للـ map، وبعدين ياخد 5! إهدار كبير للـ RAM والـ GC.
- **النهج الصحيح مع Sequence:**
  `orders.asSequence().filter { it.isCompleted }.map { it.toUiModel() }.take(5).toList()`
  الـ Sequence هيمشي عنصر بعنصر: يفحص الطلب، لو مكتمل يحوله لـ UI Model، وأول ما يجمع 5 عناصر يوقف فوراً بدون ما يلمس باقي الـ 9,995 طلب!
- **Defensive Copying في الـ ViewModel:**
  private val _items = ArrayList<Item>()
  val items: List<Item> get() = _items.toList() // Defensive snapshot يمنع الـ Race Condition

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

List is a read-only interface with no mutation methods; MutableList adds mutation methods like add and remove; ArrayList is the concrete resizable-array implementation under the hood; and Sequence is a lazy evaluation pipeline that processes elements one-by-one without creating intermediate heap collections.

## Interview answer — structured

The core distinction is between interfaces, implementations, and evaluation strategies. List is Kotlin's read-only interface—it exposes accessors but no mutation methods. Importantly, it is read-only, not strictly immutable, meaning the underlying instance could still be mutated by another reference. MutableList extends List and adds modification APIs. ArrayList is the concrete JVM class implementing MutableList, backed by a dynamic array offering O(1) indexed reads. Sequence, on the other hand, is not a collection at all; it is a lazy pipeline. Instead of executing transformations eagerly and allocating intermediate lists on the heap, a Sequence processes elements vertically one-by-one only when a terminal operation like toList() or first() is called. I use standard eager collections for small, in-memory lists because the iterator overhead of Sequences is unnecessary. But for multi-step pipelines on large datasets, or where short-circuiting like take(n) applies, Sequences prevent GC pressure.


## Interview answer — deep senior

From an architectural and memory standpoint, returning List<T> from a public API signals that callers cannot mutate the collection. However, in concurrent environments, simply upcasting a private MutableList to List does not provide thread safety. If a background coroutine calls add() while a UI thread iterates the read-only view, you risk a ConcurrentModificationException. In production, I expose a defensive copy using toList() or an immutable snapshot via kotlinx.collections.immutable.

When comparing ArrayList to Sequence, we analyze heap allocations and CPU cache locality. Standard eager collection operations like filter and map generate intermediate java.util.ArrayList allocations at every step. If you chain three transformations on a list of 5,000 items, you allocate three separate lists on the heap, triggering Gen0/Gen1 GC sweeps.

Sequences avoid intermediate allocations by composing Iterator wrappers. However, each transformation step wraps an Iterator object and invokes a function reference, adding slight indirection and call overhead. If the list is small—under a few hundred items—eager processing is actually faster because of CPU cache locality and zero iterator indirection. Sequences shine when the dataset is large, the transformation chain has multiple stages, or an early terminal operation like find or take can short-circuit before processing the entire source.


## How to answer in the interview

- **Why:** Select the right collection abstraction for mutability contracts, performance, and memory consumption.
- **How:** Use `List` for read-only interfaces, `MutableList`/`ArrayList` for mutable buffers, and `Sequence` for multi-step lazy transformations.
- **Trade-offs:** Standard `Iterable` chains allocate intermediate collections at each step; `Sequence` avoids intermediate allocations but introduces iterator overhead for small lists.
- **Failure cases:** Casting an external `List` to `MutableList` and modifying it, breaking caller immutability assumptions and causing concurrency bugs.
- **Production solution:** Expose read-only `List` publicly, use `toPersistentList()` or defensive copies for state emissions, and switch to `Sequence` only for large or unbounded datasets.

## Deep-dive talking points

Discuss covariance of `List`, invariance of mutable containers, sequence terminal operations, intermediate collections and stateful operators.

## Follow-up questions

- **Interviewer:** "If List<T> is read-only, can the underlying elements still be modified?"
  **Answer:** "Yes. First, if the element type T is mutable (for example, a class with var properties), callers can mutate element fields even through a read-only List. Second, if the List is just a cast of a MutableList, any holder of the mutable reference can add or remove elements, reflecting changes in the read-only view. True immutability requires immutable elements and a defensive copy."

- **Interviewer:** "Why not use Sequences everywhere by default if they avoid intermediate allocations?"
  **Answer:** "Because Sequences have per-element iterator overhead and function call indirection. For small collections, allocating a tiny intermediate array is faster and has better CPU cache locality than the boxing and iterator state-machine machinery of Sequences. Furthermore, Sequences cannot be indexed directly with O(1) random access without converting them back to a List."

- **Interviewer:** "How does kotlinx.collections.immutable differ from standard Kotlin toList()?"
  **Answer:** "Standard toList() creates a full defensive copy, which is an O(N) allocation and copy. Kotlinx Immutable Collections use persistent data structures (like Hash Array Mapped Tries). Modifications create a new version sharing most of the memory tree with the old version (structural sharing) in O(log N) time, making them ideal for Jetpack Compose state stability without copying overhead."

## Self-check rubric

Differentiate all four types, explain a snapshot versus view, and give one case where Sequence adds overhead.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection interfaces.
- [Kotlin sequences](https://kotlinlang.org/docs/sequences.html) — lazy processing.

Technically reviewed against primary documentation on 2026-10-13.
