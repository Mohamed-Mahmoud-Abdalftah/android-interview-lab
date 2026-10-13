---
id: "COR-06"
question: "Compare viewModelScope, lifecycleScope, and custom application-level scopes."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "A"
phase: 1
priority: "P1"
order: 87
editorial_status: "reviewed"
---

# COR-06

## Original interview question

Compare viewModelScope, lifecycleScope, and custom application-level scopes.

## What the interviewer evaluates

Whether the candidate understands screen versus lifecycle versus application ownership and process-death limits.

## Explanation in Arabic

المقارنة بين `viewModelScope` و `lifecycleScope` والـ Custom Application Scopes هي جوهر إدارة الـ Lifecycles في Android الحديث:

1. الـ `viewModelScope`:
   - مربوط بدورة حياة الـ **ViewModel**.
   - بينشأ تلقائياً مع الـ ViewModel، وبيتم إلغاؤه تلقائياً في `onCleared()` لما الـ ViewModel ينتهي تماماً.
   - **ميزة جوهرية:** بيعيش ويفضل شغال عبر الـ **Configuration Changes** (زي تدوير الشاشة من Portrait لـ Landscape). لو عملية تحميل شغالة في `viewModelScope` والمستخدم دور الشاشة، العملية مش هتتلغي ولا هتبدأ من الأول!
   - ده المكان الطبيعي لـ 90% من Business Operations والـ Data Fetching الخاصة بالـ UI.

2. الـ `lifecycleScope`:
   - مربوط بدورة حياة **Activity أو Fragment أو Composable**.
   - بيتم إلغاؤه فوراً بمجرد تدمير الـ Activity (`onDestroy`).
   - بيموت مع الـ Configuration Change! لو بدأت عملية تحميل فيه ودورت الشاشة، العملية هتتلغي وتضيع.
   - مخصص فقط للأشياء المرتبطة مباشرة بالـ UI View، زي تشغيل Navigation Animation أو التعامل مع Dialogs.

3. الـ Custom Application-Level Scope:
   - نطاق مخصص مربوط بدورة حياة **التطبيق ككل (Application Process)**.
   - بننشئه بـ `CoroutineScope(SupervisorJob() + Dispatchers.Default)` داخل Application class أو كـ Singleton في Hilt.
   - بيستخدم للعمليات الحرجة التي **يجب ألا تضيع حتى لو المستخدم قفل الشاشة فوراً**، زي: حفظ مسودة الطلب في Database، إرسال إحصائيات الدفع، أو مزامنة التوكن.

## Practical walkthrough

سيناريو عملي يوضح الفروق بدقة:
1. **المستخدم بيكتب تعليق ويضغط 'إرسال':**
   - حفظ التعليق في قاعدة البيانات المحلية: نستخدم **ApplicationScope**، حتى لو المستخدم خرج من التطبيق فوراً بعد الضغط، التعليق يتسجل وميضيعش.
2. **تحميل تفاصيل المنشور والصور:**
   - نستخدم **viewModelScope**، لأننا لو دورنا الشاشة، العملية تفضل مستمرة وتعرض النتيجة للـ ViewModel بدون تكرار الطلب.
3. **عرض Tooltip إرشادي يختفي بعد 3 ثوانٍ:**
   - نستخدم **lifecycleScope**، لأن لو الشاشة اتقفلت أو دورنا الجهاز، الـ Tooltip القديم والـ View انتهت ومش عايزين نحدث View ميتة.

## Why it matters and how it works

AndroidX supplies the first two scopes with suitable Main-oriented context and cancellation hooks. For repeated UI collection use `repeatOnLifecycle` rather than assuming `lifecycleScope.launch` pauses at STOP. A custom application scope needs an injected owner, SupervisorJob/failure policy and shutdown control; it is memory lifetime, not durable execution.

## Worked example

Android snippet assumes AndroidX lifecycle ViewModel KTX, lifecycle runtime KTX, and a `StateFlow<UiState>` named `state`.

```kotlin
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class ProfileViewModel : ViewModel() {
    fun refresh() = viewModelScope.launch { /* call repository */ }
}
// In a Fragment's onViewCreated:
// viewLifecycleOwner.lifecycleScope.launch {
//     viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
//         state.collect { render(it) }
//     }
// }
```

## Trade-offs and decision criteria

Choose `viewModelScope` for screen state transformations, the view lifecycle scope for view-bound collection, and an application scope for owned in-process work. Choose WorkManager plus persistent input/state when work must survive process death. An application scope increases retention and must handle exceptions explicitly.

## Failure modes

Collecting UI flow in `Fragment.lifecycleScope` rather than `viewLifecycleOwner.lifecycleScope` can keep work across destroyed views. A `lifecycleScope.launch` collector alone can continue while UI is STOPPED. A custom scope without a Job owner can leak resources and hide exceptions.

## Production perspective

An upload screen queues a durable upload request in a local table and WorkManager; its ViewModel observes progress. Rotating the screen preserves the ViewModel where applicable, leaving the screen cancels observation, and process death still permits rescheduling from persisted work.

## Interview answer — short

viewModelScope is bound to ViewModel lifecycle and survives configuration changes, making it ideal for business logic and UI data loading; lifecycleScope is bound to Activity/Fragment view lifecycles and cancels on onDestroy/rotation, suited for view-only animations; and custom application scopes survive screen teardowns for critical persistence operations.

## Interview answer — structured

Choosing the right coroutine scope in Android comes down to matching the task's longevity with the component's architectural lifecycle.

**viewModelScope** is tied to the ViewModel's lifecycle. Its critical strength is that it survives configuration changes like screen rotations. It automatically cancels its work only when the ViewModel is permanently cleared in `onCleared()`. This makes it the primary default for feature business logic, repository interactions, and UI data loading.

**lifecycleScope** is tied directly to an Activity or Fragment's LifecycleOwner. It is cancelled immediately when the view is destroyed in `onDestroy()`. Because configuration changes destroy the view, tasks launched in `lifecycleScope` are cancelled upon rotation. It should strictly be reserved for view-specific operations, such as UI animations or view-binding interactions.

**Custom application-level scopes** are singletons tied to the `Application` process lifecycle, typically injected via Hilt using `SupervisorJob()`. We use this for critical, fire-and-forget operations that must not be interrupted when a user navigates away, such as syncing an offline order to Room or logging a critical payment transaction.

## Interview answer — deep senior

From an architectural governance standpoint, misusing scopes causes severe production bugs. If developers launch network requests in `lifecycleScope`, rotating the phone terminates the coroutine midway, wasting bandwidth and requiring a fresh network call on recreation. Conversely, if developers launch view-modifying operations inside a custom application scope, it creates hard memory leaks by capturing View or Activity references in closures, preventing garbage collection.

When designing an application-level scope for Hilt/Dagger: ```kotlin
@Provides
@Singleton
@ApplicationScope
fun provideAppScope(): CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
```
Notice the explicit use of `SupervisorJob()`: if a routine fails with an uncaught exception, `SupervisorJob` ensures that other unrelated background jobs running in the application scope are not cancelled. Finally, for long-running background tasks that must survive process death or device reboots—like uploading heavy media—neither of these scopes is sufficient; those require WorkManager.

## How to answer in the interview

- **Why:** scope choice determines who can stop work.
- **How:** tie rendering to the view lifecycle, screen state to the ViewModel, and in-process shared work to an explicit application owner.
- **Trade-off:** longer scopes retain more work and need error handling.
- **Failure case:** collecting against a destroyed Fragment view.
- **Production solution:** repeat collection at STARTED and persist restartable operations.

## Deep-dive talking points

Trace configuration change, navigation removal, Fragment view recreation, STOP/START and process death separately.

## Follow-up questions

- **Interviewer:** "Why not use `repeatOnLifecycle` inside `viewModelScope`?"
  **Answer:** "`repeatOnLifecycle` is an extension function designed for `LifecycleOwner` (Activities, Fragments, Composables) to collect UI flows safely while the UI is at least in a given state (e.g., STARTED) and pause collection when in the background. The ViewModel has no UI lifecycle state, so flow collection in the UI layer belongs in `lifecycleScope.launch { repeatOnLifecycle(...) }`."

- **Interviewer:** "What happens to a coroutine in `viewModelScope` if the Android OS kills the app process due to low memory?"
  **Answer:** "Process death terminates the entire OS Linux process instantly. Neither `onCleared()` nor coroutine cancellation hooks run. State that must survive process death must be saved using `SavedStateHandle` or persisted to disk."

- **Interviewer:** "Can you use `viewModelScope` inside a Jetpack Compose Composable?"
  **Answer:** "You can access the ViewModel instance and invoke its methods which use `viewModelScope` internally. However, for launching coroutines directly within the Composable itself, you should use `rememberCoroutineScope()`, which cancels when the Composable leaves composition."

## Self-check rubric

Can I name cancellation point for each scope, explain view lifecycle collection, and state the process-death recovery plan?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — ViewModel and lifecycle scopes, repeatOnLifecycle.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main-safe architecture.

Technically reviewed against primary documentation on 2026-10-13.
