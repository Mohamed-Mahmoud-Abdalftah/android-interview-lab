---
id: "MEM-09"
question: "Can a ViewModel or coroutine leak memory? How?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "A"
phase: 1
priority: "P1"
order: 64
editorial_status: "reviewed"
---

# MEM-09

## Original interview question

Can a ViewModel or coroutine leak memory? How?

## What the interviewer evaluates

- Avoid the blanket claim that `viewModelScope` makes all memory ownership safe.
- Identify captured View/Activity references and jobs launched in longer-lived scopes.
- Explain cancellation, callback cleanup, and retention-path verification.

## Concept and technical explanation

Both ViewModels and coroutines can leak memory when their lifecycles and reference scopes are improperly managed. A ViewModel is designed to outlive an Activity or Fragment across configuration changes, retained by the ViewModelStoreOwner. If a ViewModel holds a direct or indirect reference to an Activity, Fragment, View, or ViewBinding (for instance, via a listener or callback interface), that reference prevents the destroyed Activity from being garbage collected across rotations. Coroutines leak memory when launched in scopes that outlive the host component—such as GlobalScope, an unmanaged CoroutineScope, or a long-running background dispatcher—while capturing the outer Activity or Fragment reference in their closure or suspension state machine. Until the coroutine completes or is explicitly cancelled, the entire captured UI hierarchy is retained in heap memory.

## Practical walkthrough (English)

Demonstrating ViewModel and coroutine leak scenarios and their remediation:
```kotlin
// Leaky ViewModel: Holding a View reference and unmanaged coroutine:
class LeakyOrderViewModel : ViewModel() {
    var orderView: View? = null // Leaks view across rotation!

    fun startPolling() {
        // Leaks outer class and runs indefinitely if not cancelled:
        CoroutineScope(Dispatchers.IO).launch {
            while (true) {
                delay(5000)
                updateUi() // Captures outer class reference
            }
        }
    }
}

// Safe ViewModel: Using StateFlow and viewModelScope:
class SafeOrderViewModel(private val repository: OrderRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<OrderUiState>(OrderUiState.Loading)
    val uiState: StateFlow<OrderUiState> = _uiState.asStateFlow()

    fun startPolling() {
        // Automatically cancelled when onCleared() is invoked:
        viewModelScope.launch {
            repository.pollOrders()
                .collect { orders -> _uiState.value = OrderUiState.Success(orders) }
        }
    }
}
```
Using viewModelScope ensures that all active child jobs are automatically cancelled when the ViewModel is destroyed in onCleared(), freeing all captured references.

## Explanation in Arabic

هل يمكن للـ ViewModel أو الـ Coroutine تسريب الذاكرة؟ وكيف يحدث ذلك؟

1. تسريب الذاكرة عبر الـ ViewModel:
   - الـ `ViewModel` مصمم ليعيش أطول من الـ Activity الفردية؛ فهو يبقى حياً أثناء تدوير الشاشة (Configuration Change) ويتم التخلص منه فقط عند استدعاء `onCleared()`.
   - إذا قمت بتخزين مرجع مباشر لـ `Activity` أو `View` أو `Fragment` داخل الـ ViewModel، فإن الـ ViewModel سيمنع الـ GC من تحرير الـ Activity القديمة أثناء التدوير، مما يسبب تسريباً صريحاً!

2. تسريب الذاكرة عبر الـ Coroutines:
   - الـ Coroutine التي تعمل في نطاق غير مرتبط بدورة الحياة (مثل `GlobalScope` أو نطاق لا يتم إلغاؤه) تظل نشطة في الخلفية.
   - إذا كانت هذه الـ Coroutine تلتقط (captures) مرجعاً ضمنياً لـ Activity أو كائن واجهة داخل الـ lambda الخاص بها، أو إذا كانت معلقة (suspended) في انتظار استجابة شبكة بطيئة أو Flow غير منتهٍ، فإن الـ Continuation الخاص بها سيحتفظ بمرجع النشاط حياً على الـ Heap إلى أجل غير مسمى.

3. الحلول القياسية في Production:
   - في الـ ViewModel: لا تخزن أي مرجع للـ View إطلاقاً؛ استخدم StateFlow و SharedFlow لتمرير البيانات للأعلى، واجعل الـ View هو الذي يراقب.
   - إذا كنت بحاجة لـ Context في الـ ViewModel، استخدم `AndroidViewModel(application)` للوصول لـ Application Context فقط.
   - في الـ Coroutines: اربط كل عملية بـ `viewModelScope` أو `lifecycleScope`. هذه النطاقات تلغي جميع المهام الفرعية تلقائياً عند انتهاء دورة الحياة.

## Practical walkthrough

أمثلة توضح التسريب في ViewModel و Coroutine وحلولها:
```kotlin
// ❌ كود خاطئ: تسريب Activity عبر ViewModel و Coroutine طويلة الأمد:
class BadViewModel : ViewModel() {
    var listener: ((String) -> Unit)? = null // إذا كان الـ listener لامبدا من Activity يمسك this!

    fun startListening() {
        // GlobalScope لا يتم إلغاؤه مع ViewModel، ويمسك reference للـ ViewModel والـ listener:
        GlobalScope.launch {
            val data = repository.streamData()
            listener?.invoke(data)
        }
    }
}

// ✅ كود سليم هندسياً: مبني على StateFlow و viewModelScope:
class GoodViewModel(private val repository: DataRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadData() {
        // viewModelScope يلغي الكوروتين تلقائياً داخل onCleared():
        viewModelScope.launch {
            repository.streamData()
                .catch { emit(UiState.Error(it)) }
                .collect { _uiState.value = UiState.Success(it) }
        }
    }
}
```

## Why it matters and how it works

Coroutines are objects with continuations and captured references. Cancellation ends appropriately scoped work cooperatively; blocking work or child jobs detached into a longer scope may outlive the screen. A ViewModel is retained across ordinary configuration changes, so an Activity reference in it keeps the old instance alive. A hot Flow collected forever in an application scope can similarly keep a UI callback alive. Examine the scope, captured objects, and registration lifetime.

## Worked example

Bad design: a ViewModel stores `lateinit var binding: ScreenBinding` and launches a retry loop in `GlobalScope` that calls `binding.status.text = ...`. Correct design: ViewModel exposes `StateFlow<ScreenState>` from `viewModelScope`; the Fragment collects with `viewLifecycleOwner.repeatOnLifecycle(STARTED)` and renders into its current binding. The latter is an architecture sketch; omit the full AndroidX imports and Fragment wiring here rather than presenting it as standalone compilable code.

This Android sketch assumes `ScreenState` and `repository.load()` exist. The ViewModel exposes data rather than a `View` or `Activity`; AndroidX lifecycle dependencies are required and the snippet is illustrative.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class ReceiptViewModel(private val repository: ReceiptRepository) : ViewModel() {
    private val _state = MutableStateFlow<ScreenState>(ScreenState.Loading)
    val state: StateFlow<ScreenState> = _state

    fun load(id: String) = viewModelScope.launch {
        _state.value = ScreenState.Ready(repository.load(id))
    }
}
```

A real app defines error and cancellation states and collects `state` from the current view lifecycle.

## Trade-offs and decision criteria

`viewModelScope` fits screen-level data loading across rotation, while a view's animation or UI callback belongs to view lifecycle. Work that must survive screen closure belongs to a repository or durable scheduler, but it should receive IDs and immutable data, not Activity references. A cached Context should be application-scoped only if the API supports it.

## Failure modes

An unbounded retry loop captures Activity and keeps it alive. A suspended coroutine retains a large response while waiting indefinitely. `NonCancellable` or blocking code prevents timely cleanup. A ViewModel's registered listener is never removed in `onCleared`. Diagnose with a heap path through a continuation or callback, cancel/close at the owner boundary, and retest repeated navigation.

## Production perspective

For a search screen, ViewModel owns query and results, while Fragment owns rendering and binding. Search jobs cancel when superseded, and a repository-level sync receives only a query ID. Leak tests open/close the screen repeatedly; coroutine debug information and heap dumps help identify lingering jobs and captured views. Monitor memory slope after release.

## Interview answer — short

ViewModels leak memory if they hold references to Activities, Views, or callbacks that outlive configuration changes. Coroutines leak memory when launched in non-lifecycle scopes like GlobalScope or unmanaged scopes while capturing UI references in their execution closures. To prevent leaks, ViewModels must expose state via Flow without holding View references, and coroutines must use viewModelScope or repeatOnLifecycle.

## Interview answer — structured

Neither ViewModels nor coroutines are inherently immune to memory leaks; leaks occur when their operational lifetimes exceed the lifespan of the components they reference. A Jetpack ViewModel is intentionally preserved across configuration changes inside the ViewModelStore. If a ViewModel holds a reference to an Activity, Fragment, or View—either directly or through an anonymous callback—that reference pins the destroyed screen in memory across device rotation until the ViewModel itself is cleared.

Coroutines introduce leak risks through execution closures. When a coroutine is launched in GlobalScope or a custom unmanaged CoroutineScope, its underlying continuation captures the enclosing class instance. If that coroutine performs a long network request, delays indefinitely, or blocks on I/O, the captured Activity cannot be garbage collected for the entire duration of the job.

In production, observing flows in the UI without lifecycle awareness causes background collection to continue even when the screen is hidden.

Developers must bind all ViewModel work to viewModelScope, decouple UI interactions through unidirectional StateFlow, and collect flows in the UI using repeatOnLifecycle.


## Interview answer — deep senior

Under the hood, Kotlin coroutine compilation provides deep insights into why uncancelled coroutines leak memory. When the Kotlin compiler processes a suspend function or coroutine builder, it transforms the code into a state machine implementing the Continuation interface. This generated continuation object maintains references to local variables, execution state labels, and an implicit reference to the outer class instance (this$0) if any outer member is accessed. Active worker threads in dispatchers like Dispatchers.Default and Dispatchers.IO act as active GC Roots. As long as a coroutine job is active, suspended, or waiting for a delay timer, the dispatcher thread holds the continuation, which in turn holds the enclosing class.

If that enclosing class is an Activity or Fragment, the entire view hierarchy and context graph remain anchored to the thread pool GC Root. In Jetpack Architecture Components, viewModelScope mitigates this by binding a SupervisorJob to the ViewModel. When the user permanently finishes the Activity, ViewModelStore.clear() invokes ViewModel.onCleared(), which immediately cancels the underlying CoroutineContext and unregisters active continuation callbacks. In the UI layer, collecting a cold Flow or hot SharedFlow inside lifecycleScope.launch without repeatOnLifecycle keeps the collector running while the app is in the background, consuming CPU and retaining views. By wrapping UI collections in viewLifecycleOwner.repeatOnLifecycle with Lifecycle.State.STARTED, Android suspends and cancels collector coroutines automatically whenever the view moves below the started state, eliminating both background thread leaks and UI update crashes.

## How to answer in the interview

- **Why:** Explain three distinct lifetime scopes.
- **How:** Expose state and collect against the current view lifecycle.
- **Trade-off:** Longer scopes can preserve work but also retain captures.
- **Failure case:** A noncooperative job may outlive screen cancellation.
- **Production solution:** Test navigate-away and inspect retained views and stale updates.

## Deep-dive talking points

Discuss three ownership lifetimes, continuation capture, cooperative cancellation, detached jobs, listener cleanup, and heap paths.

## Follow-up questions

- **Interviewer:** "Can `repeatOnLifecycle` leak if called from `lifecycleScope` incorrectly?"
  **Answer:** "No, `repeatOnLifecycle` cancels its internal coroutine block automatically whenever the lifecycle falls below the specified state (like `STARTED`), stopping collection and dropping active emission references."

- **Interviewer:** "What is the consequence of passing an Activity Context into `AndroidViewModel` constructor via casting?"
  **Answer:** "It leaks the Activity immediately across configuration changes because `ViewModelStore` retains the `AndroidViewModel` instance while the Activity is destroyed and recreated."

## Self-check rubric

Explain retention through ViewModel and continuation, choose scopes for view/screen/durable work, and verify cleanup with a heap path.

## References and reviewed-on date

- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — screen owner lifetime.
- [Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — scope and cancellation ownership.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — view lifecycle boundary.

Technically reviewed against primary documentation on 2026-10-13.
