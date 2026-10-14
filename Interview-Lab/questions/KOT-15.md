---
id: "KOT-15"
question: "What is delegation? Compare interface delegation and delegated properties."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 15
editorial_status: "reviewed"
---

# KOT-15

## Original interview question

What is delegation? Compare interface delegation and delegated properties.

## What the interviewer evaluates

Separate interface implementation forwarding from property access delegation and discuss ownership.

## Explanation in Arabic

الـ Delegation (التفويض) في Kotlin بيمثل تطبيق أصيل لمبدأ "Composition over Inheritance"، وعندنا نوعين رئيسيين:

1. تفويض الواجهات (Interface Delegation بـ `by`):
   - بيسمح لك تعمل Decorator Pattern بسطر واحد بدون كتابة Boilerplate تفويض لكل دالة يدوياً.
   - `class LoggingRepository(private val inner: Repository) : Repository by inner`
   - المترجم بيولد تلقائياً كل دوال `Repository` وبيخليها تنادي `inner.method()`. وأي دالة محتاج تغير سلوكها بتعمل لها `override` فقط!

2. تفويض الخصائص (Property Delegation بـ `by`):
   - بيسمح بتفويض قراءة (`getValue`) أو كتابة (`setValue`) المتغير لكائن خارجي (Delegate Object).
   - أمثلة شهيرة: `by lazy`، و `by Delegates.observable` (للرد على تغير القيمة)، و `by viewModels()` في أندرويد، و `by remember { mutableStateOf() }` في Jetpack Compose.

في الـ Bytecode، المترجم بيولد حقل مخفي (Synthetic Field) اسمه `prop$delegate`، وكل قراءة بتتحول لاستدعاء `delegate.getValue(this, ::prop)`.

## Practical walkthrough

في شاشات أندرويد:
- تفويض الـ ViewModels: `val viewModel: UserViewModel by viewModels()` بيفوض إنشاء وإدارة دورة حياة الـ ViewModel لـ Android Jetpack `ViewModelLazy`.
- تفويض المراقبة: `var count: Int by Delegates.observable(0) { prop, old, new -> updateBadge(new) }` بيحدث الـ UI تلقائياً كل ما القيمة تتغير.
- تفويض الـ SharedPreferences: نقدر نعمل Custom Delegate يخزن ويقرأ من الـ DataStore أو الشيرد بريفرنسز تلقائياً بدون تكرار كود الحفظ والقراءة في كل مكان.

## Why it matters and how it works

Interface delegation favors composition over hand-written forwarding. Property delegation abstracts storage or computation of a property. Both hide generated calls, so understanding which object owns state and when it is initialized is essential.

## Worked example

JVM example: wrapper forwards `read` while replacing `label`.
```kotlin
interface Store { fun read(): String; fun label(): String }
class MemoryStore : Store {
    override fun read() = "value"
    override fun label() = "memory"
}
class LoggingStore(private val delegate: Store) : Store by delegate {
    override fun label() = "wrapped ${delegate.label()}"
}
fun main() = println(LoggingStore(MemoryStore()).label())
```

## Trade-offs and decision criteria

Use interface delegation when most methods should forward unchanged; write explicit forwarding when behavior must be audited per method. Use property delegates for consistent access semantics such as lazy initialization or observable state, but avoid magic that hides expensive I/O in a getter.

## Failure modes

A wrapper overrides `label` and assumes calls made inside the delegate’s `read` will dispatch to the wrapper override. The delegate is a separate object, so that assumption fails. Another risk is a property delegate retaining a View after its lifecycle ends.

## Production perspective

A metrics wrapper delegates a storage interface and overrides selected methods to record latency. It documents which calls are instrumented and uses constructor-injected, lifecycle-appropriate storage. Sensitive fields are excluded from logs.

## Interview answer — short

Delegation implements composition over inheritance natively. Interface delegation allows a class to implement an interface by delegating all method calls to an internal instance. Property delegation delegates getter and setter logic to a separate object implementing getValue and setValue, powering features like by lazy, by viewModels, and Compose state.

## Interview answer — structured

Kotlin natively supports the delegation pattern for both interfaces and properties using the by keyword.

Interface delegation enables clean decorators without boilerplate: by writing class AnalyticsRepo(inner: Repo) : Repo by inner, the compiler automatically forwards all interface methods to inner, letting me override only the methods I want to intercept.

Property delegation delegates a property's getter and setter to a delegate object implementing getValue and setValue. This powers fundamental Android utilities like by lazy for deferred initialization, by viewModels() for lifecycle-scoped ViewModel acquisition, and Jetpack Compose's mutableStateOf delegates.

It promotes separation of concerns by encapsulating repetitive state or storage logic in reusable delegate classes.


## Interview answer — deep senior

Under the hood, property delegation relies on operator conventions. For a read-only val, the delegate class must implement an operator function: operator fun getValue(thisRef: Any?, property: KProperty<*>): T. For a var, it must also provide operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T).

The compiler generates a private backing field for the delegate named property$delegate and replaces all property reads with delegate.getValue(this, KProperty). Starting in modern Kotlin versions, if the delegate does not utilize the KProperty metadata, the compiler optimizes away the KProperty allocation to eliminate reflection overhead.

Interface delegation compiles by generating forwarding methods for every interface member in the implementing class. However, an important caveat is that delegated methods do not have polymorphic access to the outer decorator class: inside the delegate, this refers to the delegate instance, not the wrapper. In production Android codebases, we use custom property delegates for DataStore persistence and Fragment lifecycle binding cleanup.


## How to answer in the interview

- **Why:** Prefer composition over inheritance by delegating interface implementations or property storage.
- **How:** Use class delegation (`class SecureRepo(base: Repo) : Repo by base`) and property delegates (`by lazy`, `by Delegates.observable`, custom delegates).
- **Trade-offs:** Class delegation only delegates interface methods; internal calls within the delegate cannot see overrides in the delegating class.
- **Failure cases:** Accessing a delegated property before its backing mechanism is configured, or writing heavy side-effects inside property delegate getters.
- **Production solution:** Use interface delegation for transparent decorator patterns (e.g., adding logging or caching), and custom property delegates for reusable Android preference or bundle bindings.

## Deep-dive talking points

Explain generated forwarding, wrapper override behavior, `getValue`/`setValue`, delegate lifetime and testing.

## Follow-up questions

- **Interviewer:** "How does `by Delegates.observable` work, and when would you use it?"
  **Answer:** "`Delegates.observable` takes an initial value and a lambda callback `(property, oldValue, newValue) -> Unit`. Every time the property is assigned a new value, the delegate executes the callback. It is useful for lightweight internal state changes or updating a UI badge when an in-memory counter changes."

- **Interviewer:** "Does using property delegates impact memory and performance?"
  **Answer:** "Yes, slightly. Each delegated property allocates an additional backing delegate object on the heap, and accessing the property involves a method call indirection (`getValue`). For typical UI components or ViewModels, the overhead is negligible, but inside hot rendering loops or tight mathematical routines, plain primitive fields are preferred."

- **Interviewer:** "What happens if a class overrides a method that is also delegated via interface delegation `by inner`?"
  **Answer:** "The explicit class override takes precedence. The compiler generates the overriding implementation in the class body, and external calls execute your overridden method instead of forwarding to the `inner` delegate."

## Self-check rubric

Give an example of each delegation form, predict an override/internal-call result, and name a lifecycle risk.

## References and reviewed-on date

- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — interface forwarding.
- [Kotlin delegated properties](https://kotlinlang.org/docs/delegated-properties.html) — property delegate protocol.

Technically reviewed against primary documentation on 2026-10-13.
