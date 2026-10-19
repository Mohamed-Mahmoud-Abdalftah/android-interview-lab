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

Distinguish a read-only binding/property from immutable object state, notice custom getters and collection aliases, and explain why `val` alone does not make shared state thread-safe or Compose state observable.

## Concept and technical explanation

A local `val` is assigned once; a local `var` can be reassigned. For properties, `val` exposes a getter and no public setter through that declaration, while `var` permits assignment through a setter. Neither keyword defines whether an object returned by the property can change. `val items = mutableListOf("A")` cannot be reassigned, but `items.add("B")` is legal. A `val` with a custom getter can also return a newly computed value on every read; there may be no stored backing field.

Kotlin's `List<T>` is a read-only interface, not proof of an immutable collection. Another alias may mutate its backing object. `toList()` can give a separate collection snapshot, but it is shallow: mutable elements are still shared. To publish stable UI values, control ownership, avoid mutable aliases, and emit a new state value when data changes. `StateFlow` and Compose observe state changes according to their own rules; a public `val`, `data class` or read-only `List` does not itself guarantee a Compose stability inference, recomposition, atomicity or thread safety.

## Practical walkthrough (English)

A cart exposes `val items: MutableList<Item>`; a screen can call `clear()` without the ViewModel's validation or a new state emission. A safer owner keeps its mutable list private and returns a copy through `val items: List<Item> get() = backing.toList()`. A test takes a snapshot, adds another item, and verifies the old snapshot remains unchanged. If `Item` itself is mutable, that snapshot still shares each element; a real UI state contract should use immutable elements or copy them too. For concurrent writers, use a serialized owner or appropriate synchronization, not just `val`.

## Explanation in Arabic

`val` في Local Variable معناها Assignment واحدة؛ `var` تسمح بإعادة الإسناد. وفي Property، `val` بتدي Getter من غير Setter من نفس الإعلان، لكن ده مش حكم على محتوى الـ Object. `val items = mutableListOf("A")` ما ينفعش أسند لها List تانية، لكن `items.add("B")` شغالة. كمان Property مكتوبة `val` ومعاها Custom Getter ممكن تحسب قيمة مختلفة في كل قراءة بدل ما تحتفظ بقيمة واحدة.

`List<T>` في Kotlin واجهة Read-only، مش ضمان إن الـ Backing Collection Immutable؛ Alias تانية ممكن تعدلها. `toList()` تعمل نسخة من الـ Collection، لكن النسخ Shallow: لو العناصر نفسها Mutable هتفضل مشتركة. عشان UI State تبقى مفهومة، أحدد مين يملك التعديل وأنشر قيمة جديدة عند التغيير. `val` وحدها لا تضمن Thread Safety ولا إن Compose هتلاحظ Mutation داخل Object قديم.

## Practical walkthrough

Cart State Holder كشفت `val items: MutableList<Item>`؛ الشاشة تقدر تمسحها من غير ما تمر على Validation أو تعمل State Emission. أخلي الـ MutableList خاصة وأعرض `val items: List<Item> get() = backing.toList()`. في Test آخذ Snapshot، أضيف عنصرًا، وأتأكد إن النسخة القديمة فضلت زي ما هي. لو `Item` نفسها Mutable، النسختان لسه بيشتركوا في عناصر قابلة للتغيير. ولو أكتر من Thread هتكتب، أحتاج Owner واحدة أو Synchronization مناسبة؛ كلمة `val` مش هتحل ده.

## Why it matters and how it works

`val` limits reassignment, which often makes code easier to follow. It does not freeze nested data or synchronize access. Ownership and observable state transitions matter when a value is shared with UI or across threads.

## Worked example

This JVM snippet is compiled and exercised by the Kotlin lab. It shows legal mutation through a `val`, and a collection snapshot that stays unchanged after a later append.

```kotlin
class CartStateHolder {
    private val backing = mutableListOf<String>()
    val items: List<String> get() = backing.toList()
    fun add(item: String) { backing.add(item) }
}

fun main() {
    val mutable = mutableListOf("A")
    mutable += "B" // legal even though the binding is val
    check(mutable == listOf("A", "B"))

    val cart = CartStateHolder()
    cart.add("A")
    val oldSnapshot = cart.items
    cart.add("B")
    check(oldSnapshot == listOf("A"))
    check(cart.items == listOf("A", "B"))
}
```

## Trade-offs and decision criteria

Prefer `val` when reassignment is unnecessary; use a local `var` when changing a local value clarifies the algorithm. Defensive copies allocate and are shallow unless elements are immutable. Persistent collections or a single-threaded owner may suit larger shared state. Choose a synchronization strategy for concurrent writes and verify the actual UI state observation path.

## Failure modes

A public `val` exposes a `MutableList`, allowing callers to bypass state transitions. A `List` view backed by the same mutable object changes without a new emission. A data-class `copy()` shares a mutable nested list. Two threads mutate one list and cause a race; a `ConcurrentModificationException` is possible, not guaranteed. A custom `val` getter is assumed constant although it recomputes on every read.

## Production perspective

A ViewModel can keep `MutableStateFlow<UiState>` private and expose `StateFlow<UiState>`, emitting fresh state values with controlled updates. The state should avoid hidden mutable aliases. Compose stability and skipping depend on the actual parameter types and compiler behavior; inspect reports and measure if performance matters. Do not infer safety or guaranteed recomposition from `val` alone.

## Interview answer — short

`val` means I cannot reassign that local binding or property through its declaration; `var` allows reassignment. It does not make the object immutable. A `val` holding a `MutableList` still allows `add()`, and a read-only `List` can be backed by a mutable object. For UI state, I control mutation and publish fresh values rather than assume `val` gives thread safety or observable changes.

## Interview answer — structured

I separate assignment from object state. A local `val` is assigned once; a `var` can be assigned again. For a property, `val` exposes a getter without a setter, but a custom getter may compute a different value each time. A `val` referencing a `MutableList` still lets me change its contents.

In a cart screen, exposing `val items: MutableList<Item>` lets the UI modify the cart behind the ViewModel's back. I keep mutable state private and publish a new state value when the cart changes. If I return `backing.toList()`, a previous list snapshot stays unchanged after adding another item; that is only a shallow copy, so I also consider whether each `Item` is mutable. A read-only `List` type alone cannot promise that its backing object will never change.

`val` also gives no general concurrency guarantee. If multiple threads mutate shared contents, I need an owner or synchronization. In Compose and StateFlow, I make changes observable through their state mechanisms rather than mutate a hidden list in place. I use `val` by default for clarity and use `var` where local reassignment is genuinely useful.

## Interview answer — deep senior

The keyword controls assignment at the declaration site. A local `val` has one assignment; a local `var` can be reassigned. A property declared `val` has a getter contract but no setter through that property. It may use a backing field, or a custom getter may compute every time. So even the claim that every `val` returns the same reference is false. Similarly, a `val` can hold a mutable object or a data class can have a `val` that points to a mutable list. `copy()` of that data class is shallow, so old and new instances can share mutable nested data.

For collections, Kotlin separates `List<T>` from `MutableList<T>` at the API level. A `List` lets that caller read, but an alias with mutable access can still change the underlying object. `toList()` can isolate the collection structure after a later append, while mutable element objects remain shared. I choose the ownership contract explicitly: private mutation with fresh snapshots, immutable element models, or persistent collections where their costs make sense.

At a concurrency boundary, `val` does not synchronize mutations of the referenced object or make compound updates atomic. A race can produce lost updates or inconsistent reads; a specific exception is not guaranteed. A serialized owner, `Mutex`, or an atomic state update may be appropriate depending on the system. Likewise, Compose stability is not inferred simply from `val` fields: collection types and module boundaries affect inference, and state must be changed through observable mechanisms. StateFlow can suppress an equal value, so mutating a list in place can leave collectors with no useful new signal.

In an interview I would demonstrate `val list = mutableListOf(...)` followed by `list.add(...)`, then show a ViewModel that keeps mutation private and emits a fresh `UiState`. I would mention the cost of copying large lists and measure actual Compose behavior before declaring an optimization. The durable principle is controlled ownership and observable state, not a blanket “immutable because val” rule.

## How to answer in the interview

Show one legal mutation through `val`, contrast it with reassignment, mention custom getters and read-only `List` aliases, then explain how a ViewModel publishes fresh state with an explicit owner.

## Deep-dive talking points

Local binding versus property getter; backing fields; shallow data-class `copy`; read-only collection aliases; snapshot cost; concurrent mutation; StateFlow emissions and Compose stability.

## Follow-up questions

- **Interviewer:** "Can `val timestamp get() = now()` change between reads?"
  **Answer:** "Yes. The getter runs on each access and may return a new value; the declaration has no setter but need not store one constant value."

- **Interviewer:** "Does `List<Item>` guarantee immutable contents?"
  **Answer:** "No. It is a read-only interface for that caller. Another alias may mutate the backing list, and its element objects may also be mutable."

- **Interviewer:** "Does `val` make a shared list thread-safe?"
  **Answer:** "No. It restricts reassignment of that binding, not operations on the list. Shared mutation needs ownership or synchronization."

## Self-check rubric

Demonstrate mutable contents behind `val`, explain a changing custom getter, distinguish a read-only view from a snapshot, and describe one safe state-owner strategy.

## References and reviewed-on date

- [Kotlin basic syntax](https://kotlinlang.org/docs/basic-syntax.html) — local `val` and `var`.
- [Kotlin properties](https://kotlinlang.org/docs/properties.html) — getters and backing fields.
- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — read-only and mutable interfaces.
- [Compose stability](https://developer.android.com/develop/ui/compose/performance/stability) — stability is more than `val` and ordinary collections may be unstable.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
