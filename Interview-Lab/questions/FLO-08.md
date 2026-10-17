---
id: "FLO-08"
question: "What are stateIn and shareIn?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 121
editorial_status: "reviewed"
---

# FLO-08

## Original interview question

What are stateIn and shareIn?

## What the interviewer evaluates

Explain conversion of cold streams into hot shared state or broadcast, including scope and replay.

## Concept and technical explanation

The stateIn and shareIn operators in Kotlin coroutines are transformative bridging mechanisms that convert cold, on-demand flows into hot, multicasting streams within a defined CoroutineScope. Cold flows execute independently from scratch for every collector, which causes severe resource duplication when multiple components collect shared database queries or network feeds. The shareIn operator converts a cold flow into a hot SharedFlow, multicasting upstream emissions across multiple subscribers while configuring replay cache size and buffer overflow strategies. The stateIn operator converts a cold flow into a hot StateFlow, enforcing state-holder invariants by requiring an initial value, conflating identical updates, and maintaining a single-item replay cache for immediate snapshot retrieval. Both operators accept a SharingStarted policy parameter governing when upstream production activates and ceases based on subscriber presence.

## Practical walkthrough (English)

Converting a cold database flow into hot presentation streams:
```kotlin
class ProductCatalogViewModel(private val repository: ProductRepository) : ViewModel() {
    // 1. stateIn: Converts cold Flow into hot StateFlow for UI state rendering
    val catalogState: StateFlow<CatalogUiState> = repository.observeProducts()
        .map { CatalogUiState.Success(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000), // Grace period for rotation
            initialValue = CatalogUiState.Loading // Immediate fallback state
        )

    // 2. shareIn: Converts cold Flow into hot SharedFlow for broadcast events
    val stockAlerts: SharedFlow<StockAlert> = repository.observeGlobalStockAlerts()
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.Lazily, // Starts when first subscriber arrives, stays active
            replay = 1 // Keeps the latest alert for new screens
        )
}
```

## Explanation in Arabic

المشغلان `stateIn` و `shareIn` هما جسر التحويل من الـ Cold Flows إلى الـ Hot Streams:

1. ما الذي يفعله `stateIn`؟
   - يحول أي Cold Flow إلى **Hot StateFlow**.
   - **يتطلب 3 معاملات:**
     * `scope`: نطاق الـ Coroutine الذي سيعيش فيه الـ Flow (عادة `viewModelScope`).
     * `started`: استراتيجية بدء وإيقاف البث (`SharingStarted.WhileSubscribed`, `Eagerly`, `Lazily`).
     * `initialValue`: القيمة الابتدائية الإلزامية التي تعرض فوراً قبل اكتمال أول تدفق.
   - النتيجة: StateFlow يحمل دائماً `.value` ويعمل له Conflation.

2. ما الذي يفعله `shareIn`؟
   - يحول أي Cold Flow إلى **Hot SharedFlow** متعدد المستمعين (Multicaster).
   - **المعاملات:** `scope`, `started`, و `replay` (كم قيمة سابقة يتم الاحتفاظ بها للمستمعين الجدد).
   - لا يشترط قيمة ابتدائية، ولا يقوم بعمل conflation للقيم المتطابقة.

3. متى نستخدم كل منهما؟
   - استخدم `stateIn` لتمثيل **حالة الشاشة (UI State)** المأخوذة من Room أو DataStore.
   - استخدم `shareIn` لبث **أحداث أو إشعارات** مشتركة لعدة شاشات في نفس الوقت.

## Practical walkthrough

تحويل Room Cold Flow إلى UI StateFlow في الـ ViewModel:
```kotlin
class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    
    // repository.getUsers() ترجع Cold Flow<List<User>> من Room DB.
    // نحولها لـ StateFlow باستخدام stateIn:
    val usersUiState: StateFlow<List<User>> = repository.getUsers()
        .map { it.filter { user -> user.isActive } }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000L),
            initialValue = emptyList()
        )
}
```
النتيجة: لا يتم إطلاق استعلام Room إلا عندما تكون الشاشة مرئية وتستمع للـ Flow، ويتم مشاركة البيانات بين كل المكونات بدون تكرار.

## Why it matters and how it works

Sharing launches an upstream collection coroutine in the supplied scope. `stateIn(scope, started, initial)` holds a current value; `shareIn(scope, started, replay)` has configurable replay. Multiple downstream collectors then share one upstream run while sharing is active. Restart and replay behavior depend on start policy and cache rules.

## Worked example

Android ViewModel example assumes DAO returns a cold `Flow<List<Item>>`; Item/Dao are app types.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class FeedViewModel(dao: FeedDao) : ViewModel() {
    val items: StateFlow<List<Item>> = dao.observeItems()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
```

## Trade-offs and decision criteria

Use stateIn if callers need a current state; shareIn if replay/broadcast needs differ. Sharing saves repeated upstream work but retains data in the chosen scope and can add a buffer. `WhileSubscribed` may restart upstream; Eagerly can waste resources when nobody observes.

## Failure modes

Sharing a user-specific feed in an application scope can replay stale or sensitive data after logout. Assuming `shareIn(replay=0)` stores events for absent subscribers loses them. An initial empty list can confuse loading with empty success.

## Production perspective

A repository shares a costly location subscription in a session scope while multiple screens are active. A feed ViewModel uses stateIn for rendering. Session invalidation cancels the old scope and clears derived state.

## Interview answer — short

stateIn and shareIn convert cold flows into hot streams within a CoroutineScope. shareIn produces a SharedFlow that multicasts emissions across multiple collectors with custom replay. stateIn produces a StateFlow that holds a current value, requires an initial state, and conflates updates. Both use SharingStarted strategies to control upstream execution lifecycles.

## Interview answer — structured

StateIn and shareIn are conversion operators that transform cold flows into hot, multicasting streams.

Cold flows execute redundantly for every collector. To share a single upstream connection across multiple UI collectors without duplicating network requests or database queries, we bridge the cold stream into a CoroutineScope using these operators.

In production, we use stateIn when the stream represents UI state. It requires an initial value, maintains a single-item replay cache, conflates identical states, and exposes a synchronous value getter. Conversely, we use shareIn when transforming continuous event streams where customized replay sizes or buffer capacities are required without enforcing an initial state.

Both operators take a SharingStarted strategy. The gold standard for Android UI is SharingStarted.WhileSubscribed(5000), which activates upstream production only while subscribers exist, adding a five-second buffer to bridge screen rotations without tearing down the upstream flow.


## Interview answer — deep senior

Under the hood, stateIn and shareIn instantiate a specialized CoroutineScope subscription pipeline that collects the cold upstream flow and forwards emissions into an internal Channel-backed buffer. The execution is governed entirely by the SharingStarted policy.
When SharingStarted.Eagerly is configured, the operator launches the upstream collection immediately upon instantiation, keeping the upstream flow alive until the parent CoroutineScope terminates, regardless of whether any subscriber ever collects it. SharingStarted.Lazily defers upstream execution until the very first subscriber attaches, but once started, never suspends even if all subscribers detach.
SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis) implements the most sophisticated lifecycle control. It monitors the active subscriber count in the underlying AbstractSharedFlow. When the subscriber count transitions from zero to one, it launches the upstream collection job. When the subscriber count drops back to zero (such as during Activity onStop or screen rotation), it starts a cancellation timer set to stopTimeoutMillis. If a new subscriber arrives before the timeout expires (e.g., the Activity recreates in landscape within 300ms), the cancellation is aborted, preserving upstream database locks and socket connections. If the timer elapses, the upstream coroutine is cancelled, releasing physical resources and saving battery.
Staff engineers enforce stateIn with WhileSubscribed(5000) at presentation boundaries to bridge cold repository queries into battery-efficient, lifecycle-resilient UI state.

## How to answer in the interview

- **Why:** repeated cold collection can duplicate work.
- **How:** choose current state via stateIn or broadcast via shareIn.
- **Trade-off:** scope and start policy affect resources.
- **Failure case:** global sharing leaks work or wrong replay loses state.
- **Production solution:** count upstream starts through lifecycle transitions.

## Deep-dive talking points

Trace upstream subscription count, replay, start policy and scope cancellation.

## Follow-up questions

- **Interviewer:** "Why is the 5-second timeout in `WhileSubscribed(5000)` important?"
  **Answer:** "During an Android configuration change (like screen rotation), the old Activity/Fragment destroys its view (unsubscribes) and the new view is created and resubscribes within a few hundred milliseconds. A 5-second grace period prevents tearing down and immediately restarting the upstream network or database flow during rotation."

- **Interviewer:** "What happens if you use `stateIn` with `SharingStarted.Eagerly`?"
  **Answer:** "The upstream flow starts collecting immediately upon ViewModel instantiation and never stops until the ViewModel is destroyed, even if no UI component is observing the state."

- **Interviewer:** "Can you call `stateIn` without providing an `initialValue`?"
  **Answer:** "Only if using the 2-argument overload of `stateIn(scope)`, which is a suspending function that waits for the first upstream emission before returning the StateFlow. In a ViewModel property initializer, you must use the 3-argument non-suspending overload with an explicit `initialValue`."

## Self-check rubric

Can I select stateIn/shareIn, name an owner, explain replay and predict restart?

## References and reviewed-on date

- [Kotlin stateIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/state-in.html) — state conversion.
- [Kotlin shareIn API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html) — sharing.

Technically reviewed against primary documentation on 2026-10-13.
