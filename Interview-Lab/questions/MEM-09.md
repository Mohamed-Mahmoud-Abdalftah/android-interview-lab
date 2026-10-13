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

Yes. A ViewModel leaks memory if it retains references to Views, Activities, or Fragments across configuration changes. A coroutine leaks memory if launched in an unbound scope like `GlobalScope` or left suspended while capturing a transient Context or View reference. Using `viewModelScope` and observing unidirectional data flows via `StateFlow` prevents these leaks.

## Interview answer — structured

Yes, both ViewModels and coroutines can leak memory if lifecycle boundaries are violated.

A `ViewModel` is scoped to survive configuration changes. If it stores a reference to an Activity, Fragment, View, or an Activity-bound callback, that transient UI component remains pinned in the heap when the user rotates the device or navigates away. To prevent this, ViewModels must strictly expose state unidirectionally via `StateFlow` or `LiveData` and never hold UI references. If a Context is mandatory, `AndroidViewModel` should be used to restrict access to `applicationContext`.

Similarly, a coroutine leaks memory when launched in an unmanaged scope—such as `GlobalScope` or an uncancelled custom `CoroutineScope`. If that coroutine suspends indefinitely (such as awaiting a long network request or observing a cold flow) and captures a reference to a View or Activity within its lambda closure, the underlying `Continuation` object acts as an active GC Root pinning the entire UI graph in memory. Using `viewModelScope` and `lifecycleScope` ensures automatic cooperative cancellation when the host lifecycle terminates.

## Interview answer — deep senior

Under the hood, Kotlin coroutines compile suspension points into state machines where local variables and captured closures are stored inside a heap-allocated `Continuation` object. If a coroutine is suspended waiting on a non-cancelling callback or an uncompleted `CompletableDeferred`, ART's GC traverses: Active Thread -> Event Loop / CoroutineDispatcher -> Continuation -> Captured Outer Scope (Activity/View). This creates a persistent leak even if the coroutine isn't actively doing CPU work.

Another subtle leak occurs with `suspendCancellableCoroutine` if developers forget to install `invokeOnCancellation { ... }` when wrapping legacy asynchronous SDKs. If the coroutine scope cancels, but the underlying third-party listener remains registered, the callback retains the resumed continuation indefinitely.

In production testing, we verify coroutine cleanup by ensuring unit tests run with `runTest` and that `StandardTestDispatcher` detects uncompleted child jobs, and we use LeakCanary to detect stranded `DispatchedContinuation` instances.

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
