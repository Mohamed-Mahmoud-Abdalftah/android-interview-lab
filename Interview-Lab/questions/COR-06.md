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

## Concept and technical explanation

These scopes differ by who owns the work. `viewModelScope` is cancelled when the ViewModel is cleared and usually survives a configuration change while the same ViewModel is retained. `lifecycleScope` follows an Activity or Fragment lifecycle; for view collection in a Fragment, use `viewLifecycleOwner.lifecycleScope` and `repeatOnLifecycle` so the collection is cancelled below the chosen state and restarted on return. A custom application scope can own work beyond one screen, but only while the process remains alive. WorkManager persists scheduled work across app restarts and device reboots subject to its constraints and platform scheduling. It is not a guarantee that a remote operation completed exactly once or by a fixed deadline.

## Practical walkthrough (English)

A chat screen sends a message, then the user navigates away. The first decision is whether tapping Send means only "start a request" or "accept a message for eventual delivery." For the latter, save a pending message with a stable ID locally before showing it as queued, then schedule a worker to send it. The worker retries according to the product's policy and reconciles with server status using that ID. It may run later, and the backend must handle duplicate attempts.

`viewModelScope` can own the screen's immediate state update and submission request. `viewLifecycleOwner.lifecycleScope` can collect the message list while the view is visible. An application scope is appropriate for in-process work that may finish after navigation but can be lost if the process dies. None of these scopes alone makes remote delivery durable. If saving the pending record fails, the UI should report that the message was not queued.

## Explanation in Arabic

الفرق بين الـ Scopes هو مين مالك الشغل وإمتى عمره ينتهي. `viewModelScope` مرتبطة بالـ ViewModel؛ غالباً بتكمل عبر تدوير الشاشة لو نفس الـ ViewModel اتحفظت، وبتتلغى لما الـ ViewModel تتشال. `lifecycleScope` مرتبطة بعمر Activity أو Fragment. في Fragment بجمع بيانات الـ UI باستخدام `viewLifecycleOwner.lifecycleScope` و`repeatOnLifecycle` علشان الجمع يقف تحت حالة `STARTED` ويرجع لما الشاشة تظهر.

الـ Application Scope ممكن تكمل بعد التنقل بين الشاشات، لكنها في الذاكرة وبتنتهي مع الـ process. لو الشغل لازم يُعاد جدولته بعد موت التطبيق أو إعادة تشغيل الجهاز، أستخدم WorkManager مع حالة محفوظة. ده مش وعد إن السيرفر استلم العملية مرة واحدة أو في وقت محدد؛ لازم أتعامل مع التكرار وحالات الفشل.

## Practical walkthrough

لو المستخدم ضغط إرسال رسالة وخرج من الشاشة، أسأل الأول: هل مجرد بدء الإرسال كفاية، ولا لازم نحفظ نية الإرسال؟ لو مطلوب تسليم قابل للاستئناف، أحفظ رسالة pending بمعرّف ثابت محلياً، وبعد نجاح الحفظ أجدول Worker يرسلها ويتابع حالتها مع السيرفر. الـ ViewModel تملك تحديث الشاشة الفوري، و`viewLifecycleOwner.lifecycleScope` تراقب القائمة أثناء ظهور الـ View. الـ Application Scope تنفع لشغل داخل الـ process فقط. لو فشل الحفظ، أعرض إن الرسالة ما اتحطتش في الطابور؛ ما أوهمش المستخدم إنها اتبعت.

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

I choose the scope by who should own the work. `viewModelScope` owns screen work and usually survives rotation with the ViewModel. A view's `lifecycleScope` owns UI collection and stops when that view is destroyed. An injected application scope can outlive navigation, but not process death. For work that must be rescheduled after a restart, I use a durable record and WorkManager.

## Interview answer — structured

I start with the lifetime the product needs. If I am loading data for one screen, `viewModelScope` is a good owner: it normally survives a configuration change with the ViewModel and is cancelled when that ViewModel is cleared. The UI can collect its state with the view's `lifecycleScope` and `repeatOnLifecycle`, so collection stops when the view is below `STARTED` and restarts when it returns.

For work that should continue after leaving the screen but only needs the current process, I would use an explicitly injected application scope with an error policy. It still disappears if Android kills the process. If the user taps Send and we promise the message is queued, I would first persist a pending message with a stable ID, then use WorkManager for retryable delivery. The UI should say queued until the server confirms it.

The trade-off is that WorkManager gives durable scheduling, not an exact completion time or exactly-once server effects. The backend needs an idempotent request or status lookup, and the app needs an honest failure or retry state.

## Interview answer — deep senior

`viewModelScope` belongs to a ViewModel instance, not to a particular rendered view. A configuration change usually keeps that instance, so the scope and its child jobs continue. Removing the ViewModel clears it and signals cancellation. A navigation graph can change the owner: a ViewModel scoped to a graph may outlive one destination, while a destination-scoped ViewModel may not. I would check the actual owner rather than say every screen exit cancels every ViewModel job.

For a Fragment's UI collectors I use `viewLifecycleOwner.lifecycleScope`, not the Fragment's longer-lived lifecycle scope if the collector touches the view. `repeatOnLifecycle(STARTED)` cancels and restarts its block as visibility changes. A plain `launch` does not pause automatically at `STOP`. That matters for expensive hot streams and for avoiding attempts to render into a destroyed view.

An application scope has no persistence guarantee. I would inject it only for operations whose owner is truly the process and define how uncaught child errors are observed. A `SupervisorJob` keeps one child failure from cancelling unrelated children, but it does not log or recover the failure by itself.

For a queued message or upload that should resume after process death, I persist the operation and schedule WorkManager. Its scheduling respects constraints, backoff, and platform limits; it cannot promise a fixed deadline or exactly-once remote effects. I would use a stable operation ID, make the backend idempotent or query its status, and test navigation, process restart, duplicate attempts, and a permanently failing request.

## How to answer in the interview

- **Why:** scope choice determines who can stop work.
- **How:** tie rendering to the view lifecycle, screen state to the ViewModel, and in-process shared work to an explicit application owner.
- **Trade-off:** longer scopes retain more work and need error handling.
- **Failure case:** collecting against a destroyed Fragment view.
- **Production solution:** repeat collection at STARTED and persist restartable operations.

## Deep-dive talking points

Trace configuration change, navigation removal, Fragment view recreation, STOP/START and process death separately.

## Follow-up questions

- **Interviewer:** "The user rotated the phone. Which work survives?"
  **Answer:** "A ViewModel retained for that owner keeps its `viewModelScope` work. A view collector tied to the old Fragment view is cancelled and the new view starts its own collection. I would check the actual ViewModel owner before promising survival."

- **Interviewer:** "Would an application scope guarantee that a message sends after the app is killed?"
  **Answer:** "No. Its jobs live only in that process. For a queued message, I would persist the pending record and schedule WorkManager, then reconcile the server result with a stable ID."

- **Interviewer:** "Does WorkManager mean the user will receive the message exactly once?"
  **Answer:** "No. It schedules and retries work, but the network and server can produce an unknown outcome or duplicate attempts. I need idempotency or status lookup on the backend and a visible queued, sent, or failed state in the app."

## Self-check rubric

Can I name cancellation point for each scope, explain view lifecycle collection, and state the process-death recovery plan?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — ViewModel and lifecycle scopes, repeatOnLifecycle.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main-safe architecture.

- [WorkManager scheduling](https://developer.android.com/develop/background-work/background-tasks/persistent) — persistent scheduling, constraints, and retries.
Technically reviewed against primary documentation on 2026-10-17.
