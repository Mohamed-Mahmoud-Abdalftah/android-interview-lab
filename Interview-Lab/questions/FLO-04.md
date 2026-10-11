---
id: "FLO-04"
question: "Compare Flow, StateFlow, SharedFlow, and LiveData."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 117
editorial_status: "reviewed"
---

# FLO-04

## Original interview question

Compare Flow, StateFlow, SharedFlow, and LiveData.

## What the interviewer evaluates

Choose among cold Flow, StateFlow, SharedFlow and LiveData with lifecycle and interoperability implications.

## Explanation in Arabic

`Flow` interface لstream async وغالبًا cold، كل collector يشغّل upstream. `StateFlow` hot وبها قيمة حالية؛ `SharedFlow` hot broadcast مع replay/buffer قابلين للضبط. `LiveData` lifecycle-aware observable من AndroidX مناسبة للتعامل مع code قديم، لكنها أقل ملاءمة لعمليات Flow الغنية خارج UI. نوع الـstream وحده لا يوقف collection في UI؛ نحتاج lifecycle-aware collector.

## Why it matters and how it works

Use Flow for repository streams/operators, StateFlow for ViewModel state snapshots, SharedFlow for specified broadcast contracts, LiveData where Android lifecycle-native APIs or legacy integration demand it. StateFlow/SharedFlow collectors remain active until their coroutine is cancelled, so use repeatOnLifecycle or collectAsStateWithLifecycle.

## Worked example

Conceptual ViewModel code with AndroidX lifecycle and coroutines; DAO returns `Flow<List<Item>>`, and `Item` is an application type.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class ItemsViewModel(dao: ItemDao) : ViewModel() {
    val items: StateFlow<List<Item>> = dao.observe()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
// ItemDao and Item are app-owned types.
```

## Trade-offs and decision criteria

Flow gives composable transformations but each cold collection may repeat work. StateFlow provides latest state but conflates equal updates. SharedFlow provides flexible broadcast but needs explicit loss/replay policy. LiveData automatically respects LifecycleOwner observation but may be the right bridge for existing UI.

## Failure modes

Collecting StateFlow with bare `lifecycleScope.launch` can continue while the UI is stopped. Using LiveData as an event queue can replay undesired effects on observer recreation. Converting types without identifying producer ownership can duplicate sources.

## Production perspective

A mixed XML/Compose application keeps repository data as Flow, exposes screen state via StateFlow, uses lifecycle-aware collection in both UI stacks, and adapts to LiveData only at a legacy boundary. A transaction state remains durable in Room.

## Interview answer — short

“Flow is usually a cold stream; StateFlow is hot current state; SharedFlow is a hot configurable broadcast; LiveData is lifecycle-aware Android observable. I choose by state, event and lifecycle contract, not by popularity.”

## Interview answer — structured

“A repository often exposes Flow because transformations and cancellation compose well. A ViewModel can convert that to StateFlow for an always-readable UI snapshot, with an owner scope and start policy. SharedFlow is useful when I explicitly choose replay and buffering for broadcasts; it is not automatically a reliable event queue. LiveData remains useful for legacy Android observers and has lifecycle-aware observation built in. StateFlow collection itself does not pause with UI lifecycle, so I use the appropriate lifecycle-aware collection API. Flow gives composable transformations but each cold collection may repeat work. StateFlow provides latest state but conflates equal updates. SharedFlow provides flexible broadcast but needs explicit loss/replay policy. LiveData automatically respects LifecycleOwner observation but may be the right bridge for existing UI.”

## Interview answer — deep senior

“I would not equate all four types. Flow is an asynchronous stream interface whose typical builders are cold; an expensive upstream may run per collector. StateFlow is a specialized hot SharedFlow with one current value and equality-based conflation. SharedFlow is a broadcast primitive with configurable replay and subscriber buffering. LiveData integrates observer activity with LifecycleOwner and can be a practical interoperability boundary in a mature app. For Compose or Views, I keep repository Flow independent of UI, derive StateFlow in a ViewModel, and collect only while active. One-shot effects require explicit delivery semantics; persistent business outcomes should be modeled as durable state. I test rotation, stopped UI and multiple collectors. Use Flow for repository streams/operators, StateFlow for ViewModel state snapshots, SharedFlow for specified broadcast contracts, LiveData where Android lifecycle-native APIs or legacy integration demand it. StateFlow/SharedFlow collectors remain active until their coroutine is cancelled, so use repeatOnLifecycle or collectAsStateWithLifecycle. Collecting StateFlow with bare `lifecycleScope.launch` can continue while the UI is stopped. Using LiveData as an event queue can replay undesired effects on observer recreation. Converting types without identifying producer ownership can duplicate sources. A mixed XML/Compose application keeps repository data as Flow, exposes screen state via StateFlow, uses lifecycle-aware collection in both UI stacks, and adapts to LiveData only at a legacy boundary.”

## Deep-dive talking points

Map each abstraction to producer/consumer lifecycle, replay semantics and migration boundary.

## Follow-up questions

- [FLO-03](../flo-03/): Which are hot? **Answer:** StateFlow and SharedFlow instances are hot.
- [FLO-22](../flo-22/): How collect safely? **Answer:** repeatOnLifecycle in Views or collectAsStateWithLifecycle in Compose.

## Self-check rubric

Can I choose a stream for changing data, current state and broadcast, and explain Android lifecycle collection?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — stream semantics.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — UI integration.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
