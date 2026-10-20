---
id: "KOT-07"
question: "What are higher-order functions and lambdas?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 7
editorial_status: "reviewed"
---

# KOT-07

## Original interview question

What are higher-order functions and lambdas?

## What the interviewer evaluates

Define function values and higher-order functions, including capture and cost implications.

## Concept and technical explanation

A higher-order function accepts or returns a function value; a lambda is one syntax for creating such a value. A function type such as (Int) -> Boolean describes its parameter and result contract. A lambda can capture variables from the surrounding scope. On Kotlin/JVM, implementation details depend on the compiler backend, target, whether the lambda is inlined, and whether it captures state. Mutable captured locals may require a reference wrapper in generated code. Neither every capture nor every call guarantees a new heap allocation. An inline function can inline eligible lambda bodies at the call site, often removing function-object and call overhead, but code size can grow and crossinline/noinline or escaping values change the result.

## Practical walkthrough (English)

Consider filtering and transforming a stream of customer transactions in an Android banking screen:

Failure Scenario — Memory Leaks via Variable Capture in Async Lambdas:
```kotlin
class TransactionListActivity : AppCompatActivity() {
    private val repository = TransactionRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Anti-pattern: Lambda capturing outer Activity context in long-lived async callback
        repository.observeTransactions { transactions ->
            // Implicit capture of this@TransactionListActivity
            updateUi(transactions) 
        }
    }
}
```
If the Activity is destroyed during a screen rotation while the repository retains the callback, the entire Activity instance is leaked in memory.

Production Architecture — Clean Higher-Order Composition and Lifecycle Scoping:
```kotlin
// Pure higher-order domain filter without lifecycle leaks
fun <T> List<T>.filterAndTransform(
    predicate: (T) -> Boolean,
    transform: (T) -> String
): List<String> = this.filter(predicate).map(transform)

// In ViewModel: Safe collection using structured concurrency
class TransactionViewModel(private val repository: TransactionRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<List<String>>(emptyList())
    val uiState: StateFlow<List<String>> = _uiState.asStateFlow()

    fun loadTransactions(minAmount: Double) {
        viewModelScope.launch {
            val result = repository.getTransactions().filterAndTransform(
                predicate = { it.amount >= minAmount },
                transform = { "Tx #${it.id}: $${it.amount}" }
            )
            _uiState.value = result
        }
    }
}
```

Bytecode Decompilation Verification:
A representative non-inlined Kotlin/JVM higher-order function accepts a function interface parameter:
```java
public static final Object firstMatching(List items, Function1 accept) {
    // accept.invoke(item) is executed via interface dispatch
}
```
One possible JVM lowering of a captured mutable local is:
```java
final IntRef counter = new IntRef();
counter.element = 0;
// Lambda receives counter and mutates counter.element on the heap
```

## Explanation in Arabic

الـ higher-order function هي دالة بتاخد دالة كـ parameter أو بترجع دالة؛ والـ lambda طريقة مختصرة تكتب بيها الدالة دي. نوع زي `(Int) -> Boolean` يوضح المدخل والنتيجة.

الـ lambda ممكن تمسك قيمة من النطاق اللي حواليها. لو مسكت `Activity` واتخزنت كـ callback عمره أطول من الشاشة، الشاشة هتفضل موجودة في الذاكرة. أما من ناحية الأداء، ما ينفعش نقول إن كل lambda بتتحول لكلاس جديد أو إن كل capture بيعمل allocation في كل مرة؛ ده بيعتمد على نسخة المترجم، الـ target، والـ inlining وطريقة استخدام القيمة. `var` محلي متاخد داخل lambda ممكن يحتاج wrapper زي `Ref.IntRef` في بعض تمثيلات JVM.

دوال المكتبة `map` و`filter` inline في حالات شائعة، لكن ده مش معناه إن شغل التحويل نفسه مجاني. قِس الأداء الحقيقي قبل ما تغيّر API واضح لمجرد توقع تكلفة lambda.

## Practical walkthrough

افترض إن `Activity` سجّلت callback في `Repository` طويل العمر، والـ callback بينادي `updateUi()` على الشاشة. بعد دوران الشاشة، الـ Repository ممكن يفضل ماسك النسخة القديمة. الحل إنك تلغي التسجيل في الوقت المناسب، أو تعرض البيانات كـ `Flow` وتجمعها داخل نطاق lifecycle مناسب، وتخلي الـ `ViewModel` يحتفظ بحالة الشاشة من غير مرجع مباشر للـ `Activity`.

لو بتستخدم `filter` و`map` لمعالجة قائمة، ابدأ بالحل الواضح. لو profiler أظهر تكلفة فعلية في مسار ساخن، قارن التنفيذ مع حلقة مباشرة، وراجع حجم القوائم وتكرار الاستدعاء. ما تحوّلش كل دالة higher-order إلى `inline` بلا قياس؛ نسخ جسم الدالة في كل موضع ممكن يكبر الكود.

## Why it matters and how it works

Functions as values allow behavior to be composed without subclass boilerplate. Captures preserve access to surrounding state, which is powerful but changes lifetime and sometimes allocation. A higher-order API should say whether it calls the callback immediately, stores it, or invokes it multiple times.

## Worked example

Runnable JVM example; the predicate is called synchronously for each candidate.
```kotlin
fun <T> firstMatching(items: List<T>, accept: (T) -> Boolean): T? =
    items.firstOrNull(accept)

fun main() {
    val limit = 10
    println(firstMatching(listOf(3, 12, 8)) { it > limit })
}
```

## Trade-offs and decision criteria

A lambda is concise for one behavior; an interface or named class is clearer when there are multiple operations, identity, or long-lived lifecycle. Function references can be readable but still require checking capture and dispatch semantics. Inlining may remove call overhead but duplicates body bytecode.

## Failure modes

A repository retains a screen callback that captures an Activity; the Activity remains reachable after rotation. Prefer lifecycle-owned collection or remove the listener. Another failure is assuming a callback runs once when an API may retry or invoke it concurrently; document invocation rules.

## Production perspective

A validation pipeline accepts small predicates and applies them synchronously. For asynchronous search, a ViewModel collects a Flow in `viewModelScope` rather than registering an unowned callback that can outlive the screen.

## Interview answer — short

A higher-order function is a function that takes other functions as parameters or returns a function. A lambda expression is an anonymous function literal that can be stored and passed as a value. Under the hood on the JVM, lambdas compile to instances of FunctionN interfaces or are inlined at the call site. A mutable captured local may use a shared Ref wrapper in Kotlin/JVM, depending on lowering and whether the lambda escapes.

## Interview answer — structured

Higher-order functions treat behavior as a first-class citizen, allowing developers to parameterize algorithms dynamically. A lambda expression provides concise syntax for anonymous functions, making data transformations like filtering, mapping, and folding straightforward and expressive.

Passing functions enables composable, declarative code architectures. In Android, standard Jetpack libraries utilize higher-order functions extensively, from coroutine dispatchers and Flow operators to Jetpack Compose UI component slots. Instead of implementing bulky callback interfaces, an interactor simply accepts a function type such as suspend () -> Result.

In production, the critical danger lies in lambda closures capturing surrounding state. When a lambda captures an Activity, Fragment, or ViewModel reference and is passed to an asynchronous long-lived source, it leads to severe memory leaks.

Senior engineers avoid capturing mutable state across thread boundaries, leverage lifecycle-aware coroutine scopes for asynchronous observation, and use inline functions selectively when their semantics and measured costs justify them.


## Interview answer — deep senior

Function values on Kotlin/JVM commonly use function interfaces, but exact lowering is an implementation detail that varies by compiler version and target. Non-capturing lambdas may be reused; capturing lambdas may require objects when they escape, while inline call sites can avoid creating a function object for eligible parameters. Capturing a mutable local can require a shared reference wrapper in generated JVM code so both scopes observe mutations. These are possibilities to inspect with bytecode or a profiler, not universal allocation rules.

A more important Android correctness issue is lifetime. A callback retained by a process-long repository can keep an Activity alive if it captures the Activity. Remove the listener, bind collection to the UI lifecycle, or expose a cold Flow with lifecycle-aware collection. A ViewModel can own screen state, but should not retain the Activity.

Inline functions copy eligible function bodies and lambdas into call sites, which can remove function-object and invoke overhead and enable certain non-local returns. The body still performs its real work, may allocate inside it, and inlining can increase generated code size. noinline retains a function value, while crossinline restricts non-local control flow. Use inlining for small higher-order APIs where its semantics and measured benefits justify it; avoid a blanket claim about ART garbage collection or guaranteed zero allocations.

## How to answer in the interview

- **Why:** Enable clean functional composition, event handling, and customizable algorithms.
- **How:** Pass lambdas and function references (`(T) -> R`) as parameters, inlining eligible lambda bodies where appropriate.
- **Trade-offs:** Function values that escape may need objects and captured state; the exact allocations depend on compiler lowering and call site.
- **Failure cases:** Storing a lambda that captures an `Activity` reference inside a long-lived singleton, leaking the entire UI context.
- **Production solution:** Inline short utility functions, clear stored callbacks in lifecycle teardown (`onDestroy`), or prefer lifecycle-aware listeners and Flow streams.

## Deep-dive talking points

Explain function types, closure capture, stored callbacks, invocation contracts, inline and escape analysis.

## Follow-up questions

- **Interviewer:** "What is SAM conversion, and how does Kotlin handle it differently between Java and Kotlin interfaces?"
  **Answer:** "SAM (Single Abstract Method) conversion allows a lambda to be passed wherever an interface with a single abstract method is expected. For Java interfaces like Runnable or View.OnClickListener, Kotlin automatically performs SAM conversion. For Kotlin interfaces, you must explicitly declare the interface as a `fun interface` to enable SAM conversion from a lambda."

- [KOT-12](../kot-12/): **Interviewer:** "If higher-order functions cause allocations, why shouldn't we mark every function as `inline`?"
  **Answer:** "Inlining copies the entire bytecode of the function and its lambdas to every call site. Inlining large functions at many call sites can increase generated code size; inspect the output and measure before generalizing. Inlining should only be used for small functions that take lambdas as parameters."

- **Interviewer:** "How does capturing a mutable `var` inside a lambda work under the hood?"
  **Answer:** "One common Kotlin/JVM lowering captures a shared Ref wrapper for a mutable local, such as `Ref.IntRef` or `Ref.ObjectRef`. The lambda captures a final reference to this wrapper, mutating the field inside it."

## Self-check rubric

Write a higher-order predicate function, explain capture, and identify a lifecycle leak from a stored callback.

## References and reviewed-on date

- [Kotlin lambdas](https://kotlinlang.org/docs/lambdas.html) — function types, higher-order functions, and closures.
- [Kotlin inline functions](https://kotlinlang.org/docs/inline-functions.html) — inline behavior.

Technically reviewed against primary documentation on 2026-10-19.
