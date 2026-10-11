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

`viewModelScope` عمره مرتبط بالـViewModel وبيتعمله cancel لما الـViewModel يتشال نهائيًا؛ دوران الشاشة العادي غالبًا بيحتفظ بنفسه. `lifecycleScope` مرتبط بـLifecycleOwner زي Activity أو Fragment، وبيتوقف عند `DESTROYED`. الـapplication scope مملوك للتطبيق وبننشئه فقط لشغل محتاج يعيش بعد الشاشة، لكنه لا ينجو من قتل process.

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

“`viewModelScope` owns ViewModel work, `lifecycleScope` owns a LifecycleOwner, and a custom application scope owns in-process application work. I use lifecycle-aware collection for UI streams. None of these scopes guarantees survival after process death.”

## Interview answer — structured

“I choose a scope by the lifetime of the work. `viewModelScope` is for requests and state tied to a ViewModel; it is cancelled when that ViewModel clears. A Fragment view collector belongs to `viewLifecycleOwner.lifecycleScope`, often under `repeatOnLifecycle(STARTED)`, so it stops collection when the UI is not active. A custom application scope is appropriate for work that should outlive one screen but remain in process; it needs explicit ownership and failure handling. Work that must recover after process death needs persisted state and a scheduler such as WorkManager.”

## Interview answer — deep senior

“I distinguish three lifetimes. A retained ViewModel generally survives an ordinary configuration change but is cleared when its navigation/screen owner is gone; `viewModelScope` then cancels. An Activity or Fragment lifecycle scope cancels at destruction, but starting a collector once in it does not automatically stop emissions at STOP. For views I use the view lifecycle and `repeatOnLifecycle`, or Compose lifecycle-aware state collection. An injected application scope can run in-process tasks beyond a screen, with an explicit SupervisorJob and exception policy, yet the OS may kill that process. For a critical upload or payment reconciliation I first persist an operation identifier, then schedule restartable work and expose progress through state, treating UI coroutines only as observers.”

## Deep-dive talking points

Trace configuration change, navigation removal, Fragment view recreation, STOP/START and process death separately.

## Follow-up questions

- [FLO-22](../flo-22/): How does collection stop at STOP? **Answer:** `repeatOnLifecycle` cancels and restarts its child block as lifecycle state changes.
- [COR-30](../cor-30/): Who owns critical persistence? **Answer:** durable storage and an application-level scheduling mechanism, not a disappearing ViewModel.

## Self-check rubric

Can I name cancellation point for each scope, explain view lifecycle collection, and state the process-death recovery plan?

## References and reviewed-on date

- [Android lifecycle coroutines](https://developer.android.com/topic/libraries/architecture/coroutines) — ViewModel and lifecycle scopes, repeatOnLifecycle.
- [Android coroutines guidance](https://developer.android.com/kotlin/coroutines) — main-safe architecture.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
