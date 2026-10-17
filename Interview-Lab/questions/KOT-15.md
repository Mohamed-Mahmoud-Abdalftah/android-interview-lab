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

## Concept and technical explanation

Delegation in Kotlin is a first-class language feature that natively operationalizes the software engineering principle of "Composition over Inheritance". It allows an object to forward method invocations or property accesses to a secondary helper instance using the by keyword.

Kotlin provides two distinct forms of delegation:
1. Interface Delegation (Class Delegation): Allows a class to implement an interface by delegating all or part of its public contract to an underlying instance of that interface (`class Decorator(val base: Repository) : Repository by base`). The compiler synthesizes all interface forwarding boilerplate automatically, while allowing developers to override specific methods selectively.
2. Delegated Properties: Abstracts the storage, retrieval, and observation of properties behind a delegate object that provides operator functions getValue and setValue (`val property: Type by Delegate()`). This centralizes cross-cutting concerns such as lazy evaluation, thread synchronization, validation, persistence, and observable change notifications.

## Practical walkthrough (English)

Consider implementing a caching repository decorator and Android ViewModel injection:

Failure Scenario — Misunderstanding Internal Member Polymorphism in Class Delegation:
```kotlin
interface Store {
    fun get(key: String): String
    fun getFormatted(key: String): String = "Val: ${get(key)}"
}

class MemoryStore : Store {
    override fun get(key: String) = "raw_data"
}

// Wrapper delegating to MemoryStore and overriding get()
class LoggingStore(private val inner: Store) : Store by inner {
    override fun get(key: String): String = "logged_${inner.get(key)}"
}

fun main() {
    val store = LoggingStore(MemoryStore())
    // Gotcha: getFormatted() calls MemoryStore.get(), NOT LoggingStore.get()!
    println(store.getFormatted("k")) // Prints: "Val: raw_data", NOT "Val: logged_raw_data"!
}
```
Because the delegate is a separate object with its own instance context, calls inside the delegate do not resolve polymorphically to wrapper overrides.

Production Architecture — Property and Interface Delegation in Android:
```kotlin
// 1. Interface Delegation: Decorator pattern adding telemetry metrics
class MetricsUserRepository(
    private val delegate: UserRepository,
    private val metrics: MetricsTracker
) : UserRepository by delegate {
    override suspend fun getUser(id: String): User {
        metrics.track("fetch_user_start")
        return delegate.getUser(id).also {
            metrics.track("fetch_user_success")
        }
    }
}

// 2. Delegated Properties in Android Jetpack
class ProfileFragment : Fragment() {
    // Delegates ViewModel creation and lifecycle retention to Jetpack's ViewModelLazy
    private val viewModel: ProfileViewModel by viewModels()

    // Observable property delegate updating UI on change
    private var badgeCount: Int by Delegates.observable(0) { _, old, new ->
        if (old != new) updateBadgeUi(new)
    }
}
```

Bytecode Decompilation Verification:
Decompiling interface delegation reveals that kotlinc generates explicit forwarding methods invoking the delegate field:
```java
public final class MetricsUserRepository implements UserRepository {
    private final UserRepository $$delegate_0;

    public Object getUser(String id, Continuation continuation) {
        // Overridden method body
    }

    public Object saveUser(User user, Continuation continuation) {
        // Auto-generated forwarding method:
        return this.$$delegate_0.saveUser(user, continuation); // invokevirtual
    }
}
```
Decompiling a delegated property reveals a private synthetic delegate field:
```java
private final Lazy viewModel$delegate = FragmentViewModelLazyKt.createViewModelLazy(...);
public final ProfileViewModel getViewModel() {
    return (ProfileViewModel)this.viewModel$delegate.getValue();
}
```

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

Delegation implements composition over inheritance using the by keyword. Interface delegation lets a class implement an interface by automatically forwarding calls to an internal instance, allowing selective method overrides. Delegated properties abstract property getters and setters behind a helper object providing getValue and setValue operators. Standard examples include by lazy, observable properties, and Android Jetpack's by viewModels().

## Interview answer — structured

Delegation in Kotlin provides native syntactic support for the decorator and property accessor patterns. Instead of writing tedious manual forwarding methods, the by keyword instructs the compiler to synthesize call redirection automatically.

Interface delegation favors composition over fragile class inheritance. A class implements an interface by wrapping an existing implementation, forwarding the entire API contract by default while allowing engineers to selectively override targeted methods for logging, metrics, or caching. Meanwhile, property delegation encapsulates cross-cutting property logic—such as lazy initialization, validation, and reactive observation—into reusable delegate objects.

In production, property delegation powers essential Android Jetpack features like by viewModels() and Fragment argument bundles.

Senior engineers avoid assuming that internal calls within an interface delegate will dispatch to wrapper overrides, and they utilize property delegates to maintain clean separation between domain models and persistence frameworks.


## Interview answer — deep senior

Decompiling Kotlin delegation to Java bytecode illustrates how kotlinc synthesizes structural patterns at compile time without requiring dynamic proxies or runtime reflection. For interface delegation, the compiler generates a private final field holding the delegate reference (named $$delegate_0) and emits concrete implementation methods for every interface operation not explicitly overridden in the class body. Each generated method performs an invokevirtual or invokeinterface call against the delegate field. This delivers optimal execution speed identical to hand-written forwarding methods, with zero reflection overhead.

However, staff engineers must remain conscious of the self-call dispatch boundary. In classical class inheritance, invoking a member function inside a base method dynamically dispatches to an overridden method in the derived class via the vtable. In interface delegation, the delegate is a completely distinct, standalone object in memory. If a default interface method executes inside the delegate, any calls it makes to other interface methods resolve strictly within the delegate instance itself; they will never polymorphically route back to overrides defined in the delegating wrapper.

Property delegation relies on operator conventions. When declaring val prop: T by Delegate(), kotlinc synthesizes a private final field named prop$delegate. Accessing the property compiles to an invokevirtual call on Delegate.getValue(thisRef, property), where thisRef is the enclosing class instance and property is a synthetic KProperty reflection metadata object (synthesized via PropertyReference1Impl). For var properties, Delegate.setValue(thisRef, property, value) is invoked upon assignment.

In Android system architecture, property delegation is the backbone of lifecycle-safe state. AndroidX libraries employ custom delegates like viewModels() to interact with ViewModelStoreOwner, ensuring that ViewModels survive configuration changes. Similarly, custom property delegates can synchronize preferences with EncryptedSharedPreferences or DataStore seamlessly, providing type-safe, reactive property access across application layers.

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
