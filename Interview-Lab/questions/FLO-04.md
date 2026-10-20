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

## Concept and technical explanation

Choose by behavior rather than treating all `Flow` values as cold. A producer built with `flow {}` is usually cold and executes its upstream for each collection; `StateFlow` and `SharedFlow` are hot implementations of the same Flow interface. StateFlow holds a current value, requires an initial value, and conflates equal updates. SharedFlow broadcasts with configurable replay, buffering, and overflow, but has no `.value` property. LiveData is an Android lifecycle-aware observable holder. Its `observe(owner)` delivery follows the owner's active state; `setValue` is main-thread-only, while `postValue` can be called from a background thread. Flow collection in Android UI needs explicit lifecycle-aware APIs such as `repeatOnLifecycle` or `collectAsStateWithLifecycle`. Migration should preserve one source of truth rather than automatically replacing every LiveData use.

## Practical walkthrough (English)

A repository source can be adapted to a ViewModel state, then collected with Android lifecycle awareness. `ItemDao`, `Item`, and `UiState` are application types.

```kotlin
class ItemsViewModel(dao: ItemDao) : ViewModel() {
    val uiState: StateFlow<UiState> = dao.observeItems()
        .map<List<Item>, UiState> { UiState.Ready(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}

@Composable
fun ItemsScreen(viewModel: ItemsViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    RenderItems(state)
}
```

A View-based screen would collect inside `repeatOnLifecycle(Lifecycle.State.STARTED)`. Keep a LiveData adapter only at a legacy boundary when needed.

## Explanation in Arabic

بدل ما تحفظ جدول أسماء، اسأل أربع حاجات: **مين بيشغّل المصدر؟ هل لازم أحدث قيمة فورًا؟ هل الرسالة تتبث لكل الموجودين؟ وهل Android lifecycle بيدير المشترك؟**

`Flow` واجهة عامة؛ مصدر `flow {}` المعتاد cold، وكل جمع ممكن يشغّل الـ upstream مرة. `StateFlow` hot ويحمل قيمة حالية بـ `.value` وinitial value، مناسب لحالة الشاشة. `SharedFlow` hot ويبث للمشتركين مع `replay` وbuffer قابلين للضبط؛ مافيش له `.value` حتى لو `replay = 1`، لكن فيه `replayCache`.

`LiveData` holder مرتبط بـ Android: `observe(owner)` يراعي الـ lifecycle. `setValue` لازم على main، لكن `postValue` ينفع من background. Flow في الواجهة لا يتوقف تلقائيًا عند STOP؛ استخدم `repeatOnLifecycle` أو `collectAsStateWithLifecycle`.

## Practical walkthrough

مسار عملي في شاشة منتجات:
```kotlin
// الـ DAO يقدّم مصدرًا يُجمع عند الطلب.
val products: Flow<List<Product>> = dao.observeProducts()

// الـ ViewModel يحفظ أحدث حالة للواجهة.
val uiState: StateFlow<ProductsUiState> = products
    .map<List<Product>, ProductsUiState> { ProductsUiState.Ready(it) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), ProductsUiState.Loading)
```
في Compose اجمع `uiState.collectAsStateWithLifecycle()`، وفي Views اجمع داخل `repeatOnLifecycle(Lifecycle.State.STARTED)`. لو شاشة XML قديمة بتقرأ `LiveData`، استخدم adapter عند حدّ الشاشة مؤقتًا مع مصدر حقيقة واحد. `SharedFlow` ممكن لبث tick مؤقت، لكن نتيجة شراء لازم تتخزن كحالة مسترجعة.

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

A `flow {}` source is usually cold and re-executes per collection, although `Flow` is also implemented by hot types. StateFlow is a hot current-state holder with an initial value and `.value`; SharedFlow is a configurable broadcast without `.value`. LiveData is an Android lifecycle-aware holder. UI collection of Flow needs `repeatOnLifecycle` or `collectAsStateWithLifecycle`, while LiveData `observe(owner)` uses the LifecycleOwner.

## Interview answer — structured

I compare producer execution, current value, broadcast, and lifecycle. A cold builder such as `flow {}` runs for each collector, making it useful for repository streams whose cost and caching are understood. StateFlow is hot, retains a current snapshot, requires an initial value, and suppresses equal updates. SharedFlow is hot multicast with configurable replay and buffering; even when replay is positive it exposes `replayCache`, not a `value` property.

LiveData is an Android lifecycle-aware observable. `observe(owner)` delivers when the owner is active. `setValue` is main-thread-only; `postValue` schedules delivery on main from a background caller. By contrast, collecting StateFlow or any Flow in the UI does not pause automatically at STOP. Use `repeatOnLifecycle` in Views or `collectAsStateWithLifecycle` in Compose. In a migration, keep one source of truth and adapt at a legacy boundary rather than maintaining two competing state owners.

## Interview answer — deep senior

The first correction is that `Flow<T>` is an interface, not a coldness annotation. A `flow {}` builder normally runs once per terminal collection, while StateFlow and SharedFlow implement Flow with hot collection semantics. That affects cost and cancellation: separate DAO or callbackFlow collections can create separate upstream work, while `stateIn` and `shareIn` can share one active upstream according to an owning scope and `SharingStarted` policy.

StateFlow answers “what is the state now?” through its initial and current `value`; newcomers receive the latest snapshot, and slow collectors can skip intermediate updates. SharedFlow answers a configurable broadcast question. `replay` caches values for newcomers and `extraBufferCapacity` provides room for slow active subscribers. It never exposes `.value`, even with `replay = 1`. Neither is durable after process death without an external source. LiveData remains useful at Android legacy boundaries. Its `observe(LifecycleOwner)` handles active and inactive observers. `setValue` must run on main; `postValue` can be called on a background thread and coalesces posts before main executes them.

For UI collection, I use `collectAsStateWithLifecycle` in Compose or `repeatOnLifecycle(STARTED)` in Views. A bare `lifecycleScope.launch { flow.collect { render(it) } }` may continue rendering after STOP. I choose one repository source of truth, adapt only where a legacy screen needs LiveData, and verify rotation, STOP/START, and process recreation. The correct migration decision is based on behavior and risk, not a rule that LiveData must be removed everywhere.

## How to answer in the interview

- **Why:** API names hide different lifetime and replay contracts.
- **How:** compare cold/hot, initial value, lifecycle, and errors.
- **Trade-off:** migration adapters add complexity.
- **Failure case:** parallel LiveData and StateFlow owners diverge.
- **Production solution:** one source of truth and rotation tests.

## Deep-dive talking points

Map each abstraction to producer/consumer lifecycle, replay semantics and migration boundary.

## Follow-up questions

- **Interviewer:** "Is every `Flow<T>` cold?"
  **Answer:** "No. `flow {}` is a cold producer, while StateFlow and SharedFlow are hot Flow implementations."
- **Interviewer:** "Does `SharedFlow(replay = 1)` expose `.value`?"
  **Answer:** "No. It exposes `replayCache`; only StateFlow has the current-value contract."
- **Interviewer:** "Can LiveData be updated from a background thread?"
  **Answer:** "`setValue` must run on main, but `postValue` can be called from background and schedules main-thread delivery."
- **Interviewer:** "Why use lifecycle-aware Flow collection in Compose?"
  **Answer:** "Plain collection does not automatically stop at Android STOP; `collectAsStateWithLifecycle` follows the chosen lifecycle state."

## Self-check rubric

Can I choose a stream for changing data, current state and broadcast, and explain Android lifecycle collection?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — stream semantics.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — UI integration.

- [Android LiveData API](https://developer.android.com/reference/androidx/lifecycle/LiveData) — lifecycle observation and setValue/postValue.

Technically reviewed against primary documentation on 2026-10-19.
