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

علشان تفهم الفرق بين val و var بعمق، لازم تفصل تماماً بين مفهومين في الـ Memory: الـ Reference (المؤشر) والـ Object نفسه في الـ Heap.

val في Kotlin تعني Read-Only Reference؛ يعني بمجرد ما المتغير يشاور على مكان في الـ Heap، مستحيل تخليه يشاور على مكان تاني (Reassignment ممنوع زي final في Java). لكن ده مش معناه أبداً إن الـ Object نفسه بقى Immutable (غير قابل للتعديل)!
- لو كتبت val cart = mutableListOf("Phone")، الـ Reference cart ثابت، بس تقدر تعمل cart.add("Case") عادي جداً لأن الـ Object اللي جوه الـ Heap نوعه MutableList.
- حتى لما تستخدم List<T> في Kotlin، هي بتديك Read-Only Interface فقط، وممكن تكون تحت الغطاء ArrayList عادية وأي مؤشر تاني يقدر يعدل فيها!

في الـ Concurrency، الـ val لا توفر أي Thread-Safety للمحتوى. لو عندك ثريد بيقرأ من val list = mutableListOf() وثريد تاني بيكتب فيها، هيحصل Race Condition و ConcurrentModificationException فوراً.

## Practical walkthrough

في تطبيق تجارة إلكترونية، تخيل كلاس Cart State Holder:
- النهج الخاطئ: كشف val items = mutableListOf<CartItem>() كـ Public Property. أي شاشة تقدر تعمل items.add(newItem) مباشرة من غير ما تعدي على الـ ViewModel، وبالتالي الـ UI مش هيجيلها State Update والـ State هتتشتت بين الشاشات.
- النهج الصحيح: إخفاء الـ Mutable State داخل الـ ViewModel، ونشر Snapshot غير قابل للتعديل:
  private val _items = mutableListOf<CartItem>()
  val items: List<CartItem> get() = _items.toList()
- التحقق: اكتب Unit Test يثبت إن استدعاء add على الـ Mutable List الداخلية بعد أخذ الـ Snapshot مش بيغير القائمة القديمة المعروضة في الـ UI.

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

val prevents rebinding a reference to a new memory address, while var allows reassignment. However, val does not make the referenced object immutable. A val pointing to a MutableList can still have its elements modified, and sharing it across threads requires explicit synchronization or defensive copies.

## Interview answer — structured

In Kotlin, val defines a read-only reference, meaning you cannot reassign that variable once initialized. But it is crucial to remember that val does not guarantee object immutability. If a val references a mutable collection like a MutableList, the object in the heap can still be mutated freely.

In Android ViewModels, if I expose a val MutableList to the UI, other components could modify items directly without triggering state emissions, or concurrent background threads could trigger a ConcurrentModificationException.

My rule in production is to use val by default for all references, keep mutable state private, and expose only immutable data classes or defensive list copies using toList. That separates reference immutability from actual object and state stability.


## Interview answer — deep senior

When discussing val versus var, I evaluate three distinct concerns: reference rebinding, object state mutability, and thread safety. The Kotlin compiler translates a local val into a regular Java local variable without reassignment, and a val property into a private final field with a getter.

However, object mutability is completely orthogonal. A val property pointing to an object with var fields or a mutable collection allows internal state changes. Furthermore, Kotlin's standard List interface is merely a read-only view, not an immutable collection. It omits mutating methods, but if the underlying JVM instance is an ArrayList, another reference with a MutableList interface can modify it concurrently.

In an enterprise Android application, this distinction directly impacts architecture. In a repository or ViewModel, mutating a shared val collection across coroutine dispatchers causes race conditions because val provides no memory visibility or synchronization guarantees. To handle state safely, I encapsulate mutable collections privately and emit immutable snapshots to StateFlow. If defensive copying becomes a performance bottleneck under high-frequency updates, I use Kotlinx persistent collections rather than relaxing encapsulation.


## How to answer in the interview

- **Why:** Distinguish reference reassignment from underlying object mutability and thread safety.
- **How:** Use `val` for read-only references; expose immutable public snapshots (`List<T>`) while keeping mutations private.
- **Trade-offs:** Defensive copying for immutability incurs allocation overhead, while mutable collections risk concurrent modification and state divergence.
- **Failure cases:** Assuming a `val` list cannot be modified, allowing concurrent threads to append items and crash readers with `ConcurrentModificationException`.
- **Production solution:** Encapsulate mutable state in dedicated state holders, emit immutable data classes, and use atomic primitives or Mutex for concurrent updates.

## Deep-dive talking points

Discuss aliases, shallow versus deep immutability, data-class `copy` with mutable members, and the Java memory model for shared mutable state.

## Follow-up questions

- [KOT-25](../kot-25/): **Interviewer:** "Does declaring a shared collection as val protect you from multithreaded race conditions?"
  **Answer:** "No, not at all. val only prevents the pointer itself from being reassigned to a different list instance. If two coroutines running on Dispatchers.Default and Dispatchers.IO concurrently append items to that same list, they will cause memory corruption or a ConcurrentModificationException. Thread safety requires mutual exclusion like Mutex, thread confinement, or immutable data structures."

- [KOT-16](../kot-16/): **Interviewer:** "If an API returns a read-only List, can a caller cast it to MutableList and modify it?"
  **Answer:** "On the JVM, Kotlin's List and MutableList compile down to java.util.List. If the underlying instance is an ArrayList, an unchecked cast to MutableList will technically succeed at runtime. However, doing so violates the API contract. If the implementation returns emptyList() or Collections.unmodifiableList(), that cast will crash with UnsupportedOperationException upon mutation. In production, we never cast read-only lists and enforce lint rules against it."

- **Interviewer:** "What happens if a data class has a val property that holds a mutable list when you call copy()?"
  **Answer:** "copy() only creates a shallow copy of the data class. The new instance receives a copy of the reference pointing to the exact same mutable list in memory. If either instance modifies that list, both instances reflect the change. To keep data classes truly immutable, all nested properties must also be immutable types."

## Self-check rubric

Can you demonstrate legal mutation through `val`, explain why `List` is only read-only, and name one safe shared-state strategy?

## References and reviewed-on date

- [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html) — `val` and `var`.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — read-only versus mutable collection interfaces.

Technically reviewed against primary documentation on 2026-10-13.
