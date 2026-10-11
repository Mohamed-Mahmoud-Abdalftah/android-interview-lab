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

الـ`ViewModel` يعيش أطول من Activity instance أثناء rotation، لذلك لو خزّن `View` أو `Activity` أو binding مباشرة ممكن يمسك الشاشة القديمة. الـcoroutine كمان ممكن تحتفظ بكل variables الملتقطة وهي شغالة أو معلقة؛ لو شغّلتها في `GlobalScope` أو application scope بدون حدّ عمر، تقدر تحتفظ بـscreen reference بعد إغلاقها. `viewModelScope` يتلغى عند `onCleared`، لكن ما يمنعش leak لو ViewModel نفسه مسجل listener بدون unregister، أو احتفظ بكائن UI خلال فترة بقائه. اربط شغل الـview بـ`viewLifecycleOwner`، وخلي ViewModel يحتفظ بـstate وIDs لا بـViews.

## Why it matters and how it works

Coroutines are objects with continuations and captured references. Cancellation ends appropriately scoped work cooperatively; blocking work or child jobs detached into a longer scope may outlive the screen. A ViewModel is retained across ordinary configuration changes, so an Activity reference in it keeps the old instance alive. A hot Flow collected forever in an application scope can similarly keep a UI callback alive. Examine the scope, captured objects, and registration lifetime.

## Worked example

Bad design: a ViewModel stores `lateinit var binding: ScreenBinding` and launches a retry loop in `GlobalScope` that calls `binding.status.text = ...`. Correct design: ViewModel exposes `StateFlow<ScreenState>` from `viewModelScope`; the Fragment collects with `viewLifecycleOwner.repeatOnLifecycle(STARTED)` and renders into its current binding. The latter is an architecture sketch; omit the full AndroidX imports and Fragment wiring here rather than presenting it as standalone compilable code.

## Trade-offs and decision criteria

`viewModelScope` fits screen-level data loading across rotation, while a view's animation or UI callback belongs to view lifecycle. Work that must survive screen closure belongs to a repository or durable scheduler, but it should receive IDs and immutable data, not Activity references. A cached Context should be application-scoped only if the API supports it.

## Failure modes

An unbounded retry loop captures Activity and keeps it alive. A suspended coroutine retains a large response while waiting indefinitely. `NonCancellable` or blocking code prevents timely cleanup. A ViewModel's registered listener is never removed in `onCleared`. Diagnose with a heap path through a continuation or callback, cancel/close at the owner boundary, and retest repeated navigation.

## Production perspective

For a search screen, ViewModel owns query and results, while Fragment owns rendering and binding. Search jobs cancel when superseded, and a repository-level sync receives only a query ID. Leak tests open/close the screen repeatedly; coroutine debug information and heap dumps help identify lingering jobs and captured views. Monitor memory slope after release.

## Interview answer — short

“Yes. A ViewModel can retain an Activity or View across rotation, and a long-lived coroutine can capture screen objects. Correct scopes, cancellation, and cleanup matter; `viewModelScope` alone is not a universal leak shield.”

## Interview answer — structured

“A ViewModel outlives a particular Activity instance on configuration change, so it should hold state and repository references, not binding or Activity. A coroutine continuation can retain captured objects until it completes or is cancelled. `viewModelScope` cancels when the ViewModel clears, but detached jobs or external listeners can still outlive it. I bind view rendering to the Fragment view lifecycle, keep durable work in a suitable longer-lived owner with data-only inputs, and use heap paths to verify that closed screens are released.”

## Interview answer — deep senior

“I inspect ownership across three lifetimes: view, screen ViewModel, and application or durable work. A ViewModel surviving rotation must not hold the old Activity or its binding. A coroutine captures variables in its continuation, so even a suspended job can retain a large graph; `GlobalScope` or an application scope is especially risky for a UI callback. `viewModelScope` gives structured cancellation at `onCleared`, yet cancellation is cooperative and does not unregister arbitrary external listeners. I expose immutable UI state, collect it with the view lifecycle, cancel superseded requests, and remove listeners explicitly. If an operation must continue after navigation, I move it to a repository or worker with stable IDs instead of a View. I confirm the fix with repeatable navigation, job inspection, and a heap retaining path.”

## Deep-dive talking points

Discuss three ownership lifetimes, continuation capture, cooperative cancellation, detached jobs, listener cleanup, and heap paths.

## Follow-up questions

- Does `viewModelScope` cancel at rotation? **Answer:** normally no; the ViewModel is retained for the same logical screen and clears when its owner is finished.
- Can a suspended coroutine retain memory? **Answer:** yes; its continuation can hold captured references until completion or cancellation.
- Where should a Fragment binding live? **Answer:** with the Fragment view lifecycle, cleared at `onDestroyView`, not in the ViewModel.

## Self-check rubric

Explain retention through ViewModel and continuation, choose scopes for view/screen/durable work, and verify cleanup with a heap path.

## References and reviewed-on date

- [ViewModel overview](https://developer.android.com/topic/libraries/architecture/viewmodel) — screen owner lifetime.
- [Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — scope and cancellation ownership.
- [Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle) — view lifecycle boundary.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. The architecture sketch was not Android-compiled.
