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

## Concept and technical explanation

Understanding the distinctions between List, MutableList, ArrayList, and Sequence is fundamental to writing memory-efficient and idiomatic Kotlin code. In Kotlin's standard library, List is a read-only covariant interface (List<out E>). It exposes query operations such as size, get, and iterator, but completely omits mutation methods like add, set, or remove. Crucially, List is a read-only view rather than an immutable collection; the underlying instance on the heap may still be a mutable collection held by another reference. MutableList extends List to introduce in-place mutation methods, remaining an invariant interface (MutableList<E>). ArrayList is the concrete resizable-array implementation on the JVM (aliasing java.util.ArrayList), providing constant-time indexed random access while incurring O(N) array reallocation and copy costs when expanding capacity. In stark contrast, Sequence is not an in-memory collection container at all. Instead, it represents a lazy streaming pipeline that evaluates elements vertically one by one, deferring all intermediate transformations until an explicit terminal operation is executed.

## Practical walkthrough (English)

Consider an e-commerce order history screen displaying the top five completed orders from an in-memory dataset of 10,000 cached records. Under a standard eager collection approach, writing `orders.filter { it.isCompleted }.map { it.toUiModel() }.take(5)` triggers horizontal evaluation. The filter stage iterates across all 10,000 items and allocates an intermediate ArrayList on the heap. Next, the map stage allocates a second intermediate ArrayList of thousands of items before take(5) finally extracts five elements, causing substantial garbage collection churn on Android. With a Sequence pipeline, writing `orders.asSequence().filter { it.isCompleted }.map { it.toUiModel() }.take(5).toList()` transforms execution into vertical processing. Each element passes through filter and map sequentially, and as soon as five matching items satisfy the predicate, the terminal operation terminates immediately without touching the remaining 9,995 items. In a ViewModel, exposing internal mutable lists safely requires defensive copying: `private val _items = ArrayList<Item>(); val items: List<Item> get() = _items.toList()`, ensuring concurrent callers receive an isolated snapshot.

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

List is a read-only interface with no mutation methods; MutableList extends it to add modification operations like add and remove; ArrayList is the concrete JVM dynamic-array implementation offering constant-time indexed lookups; and Sequence is a lazy pipeline that processes elements vertically one by one without allocating intermediate heap collections, making it optimal for multi-step transformations on large datasets.

## Interview answer — structured

The fundamental distinction in Kotlin lies between read-only interfaces, mutable interfaces, concrete implementations, and lazy stream evaluation. In Kotlin, List is a read-only interface that exposes accessors without mutation methods, though it is important to remember it represents a read-only view rather than guaranteed immutability.

MutableList extends List to provide modification APIs, while ArrayList is the concrete JVM class backed by a dynamic array offering constant-time indexed reads and amortized appends.

In production, standard collection transformations execute eagerly, allocating a brand-new intermediate collection at every step of a pipeline. If you chain multiple filters and maps over thousands of items, this eager horizontal execution creates intense garbage collection pressure on the Android runtime.

Sequence replaces eager evaluation with lazy vertical processing. Intermediate operations wrap iterators without performing work until a terminal operation triggers evaluation, allowing short-circuiting operations like take or first to avoid redundant computations entirely.


## Interview answer — deep senior

Under the hood on ART and the JVM, Kotlin's collection hierarchy maps directly to standard Java collection classes via compiler intrinsics without boxing overhead. When Kotlin compiles a List or MutableList, both interfaces erase to java.util.List in the generated bytecode. The Kotlin compiler enforces read-only semantics purely at compile time by hiding mutation methods in the symbol table; in decompiled Java bytecode, a Kotlin List is indistinguishable from a mutable java.util.List, which is why an unprincipled cast to MutableList can bypass compiler safety. Regarding memory allocation and cache locality, standard collection transformations compile down to tight loops over contiguous array memory. For small collections containing fewer than a few hundred items, eager operations outperform sequences because contiguous memory layout maximizes CPU L1 and L2 cache line hits, and the tiny temporary array allocation is quickly collected in Gen0 garbage collection. Sequences introduce an abstraction penalty. Each intermediate transformation step instantiates an iterator wrapper object such as FilteringSequence or TransformingSequence. Evaluating elements requires repeated virtual method invocations of hasNext and next, adding call indirection and preventing loop unrolling optimizations. However, when processing large datasets or unindexed streams, this indirection cost is dwarfed by the massive memory savings of avoiding multi-megabyte intermediate heap allocations. In concurrent Android architectures, simply upcasting a private MutableList to a public List property does not provide thread safety. If a background coroutine mutates the backing instance while the main thread iterates the read-only reference, the runtime throws a ConcurrentModificationException. In high-performance enterprise codebases, we mitigate this by using persistent data structures from kotlinx.collections.immutable, which provide structural sharing with logarithmic update complexity and guarantee compose compiler stability.

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
