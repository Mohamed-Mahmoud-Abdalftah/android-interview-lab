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

## Concept and technical explanation

In Kotlin, the distinction between val and var represents the difference between reference reassignment constraints and object mutability. A val declares a read-only variable whose reference cannot be reassigned once initialized, corresponding directly to a final reference in Java bytecode. Conversely, a var declares a mutable variable whose reference can be reassigned to point to different instances over its operational lifetime.

Crucially, declaring a reference with val does NOT guarantee immutability of the underlying object residing on the heap. If a val references an internally mutable data structure, such as a MutableList or a class with var properties, callers can mutate the internal state of that object freely without changing the reference itself. Furthermore, a custom getter on an interface or class property declared as val can evaluate to a different object on every single invocation, breaking referential constancy. True architectural immutability requires both read-only references and deeply immutable data structures.

## Practical walkthrough (English)

Consider an e-commerce shopping cart state holder in an Android ViewModel:

Failure Scenario — Leaking Internal Mutability:
```kotlin
class CartViewModel : ViewModel() {
    // Exposing a val that references a mutable data structure
    val items: MutableList<CartItem> = mutableListOf()
    
    fun addItem(item: CartItem) {
        items.add(item) // Consumers observe mutations bypassing StateFlow
    }
}
```
A consumer in the UI can invoke viewModel.items.clear() directly, bypassing business validation and desynchronizing the UI state from architectural flows.

Production Architecture — Immutable State Snapshots:
Expose read-only collections backed by private mutable state, ensuring state transitions produce fresh snapshots:
```kotlin
class CartViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<List<CartItem>>(emptyList())
    val uiState: StateFlow<List<CartItem>> = _uiState.asStateFlow()

    fun addItem(item: CartItem) {
        _uiState.update { current -> current + item }
    }
}
```

Bytecode Decompilation Verification:
Decompiling a class with a val property reveals a private field marked with final and a synthetic getter without a setter:
```java
private final List items;
@NotNull
public final List getItems() { return this.items; }
```
Conversely, a var property generates both a non-final field and a public synthetic setter public final void setItems(@NotNull List value).

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

The keyword val creates a read-only reference that cannot be reassigned once bound, compiling to a final reference on the JVM. In contrast, var declares a mutable reference that can be reassigned. Declaring a val does not make an object immutable; if it points to a mutable object like a MutableList, the internal state can still be modified. True immutability requires both a read-only reference and an immutable object graph.

## Interview answer — structured

Val and var govern reference assignability rather than heap object mutability. When declaring a variable with val, the Kotlin compiler forbids reassignment once initialized, mirroring the Java final keyword at the bytecode level. Meanwhile, var permits mutating the reference to point to another object altogether.

Engineers frequently conflate read-only references with deep immutability. Assigning a mutable collection to a val prevents pointing that variable to another collection, but callers can still invoke mutating operations on the existing heap object. In addition, a property val with a custom getter can compute and return distinct instances across sequential accesses, which means val does not even guarantee identical results.

In production, especially with Jetpack Compose and reactive StateFlow architectures, shallow immutability causes severe bugs such as missed recompositions and state races.

Senior engineers enforce deep immutability by exposing read-only List interfaces, backing them with private MutableStateFlow streams, and relying on immutable data classes with copy operations for predictable state emissions.


## Interview answer — deep senior

Decompiling val and var declarations to Java bytecode reveals how the Kotlin compiler enforces immutability semantics on the JVM. At class scope, a val property generates a private final backing field and a synthetic public getter. Because no setter bytecode is emitted, external classes cannot alter the reference. In contrast, a var property generates a non-final private field alongside both getter and setter methods.

However, when a val property defines a custom getter without a backing field, such as val currentTime get() = System.currentTimeMillis(), the compiler generates no backing field whatsoever. Instead, every invocation translates to an invokevirtual instruction calling the getter method, returning dynamic values each time. Therefore, assuming that a val guarantees an unchanging value across invocations is a serious architectural fallacy.

At the memory and concurrency boundary, reference immutability plays a decisive role in multithreaded safety. Under the Java Memory Model, JVM final fields guarantee safe publication across threads without explicit synchronization once the constructor completes. When multiple coroutines or background threads read a shared state object constructed solely of val properties referencing immutable data classes, the runtime guarantees memory visibility without risk of observing partially initialized state or encountering data races.

Conversely, mutating internal state of an object held by a val reference across concurrent coroutines without synchronization introduces race conditions and cache incoherence. In high-performance Android architectures, we pair val references with persistent collections or defensive snapshots via toList, ensuring that UI state emissions are immutable value carriers that Compose can compare structurally with zero mutation side effects.

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
