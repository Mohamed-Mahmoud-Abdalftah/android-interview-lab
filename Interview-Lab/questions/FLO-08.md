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

stateIn converts a cold Flow into a hot StateFlow with an initial value and latest-state retention (.value); shareIn converts a cold Flow into a hot SharedFlow with configurable replay cache. Both share a single upstream execution across multiple collectors within a specified CoroutineScope.

## Interview answer — structured

`stateIn` and `shareIn` are the standard conversion operators used to transform cold, lazy flows into hot, multicasting streams within a specific `CoroutineScope`.

I use **`stateIn`** when transforming data sources into UI state. It converts any upstream cold flow into a `StateFlow`. It requires an `initialValue` so synchronous access via `.value` is immediately available, retains the latest emission, and conflates updates to suppress identical values.

I use **`shareIn`** when broadcasting event or data streams to multiple subscribers without state semantics. It converts a cold flow into a `SharedFlow`, allows configuring `replay = N` to determine how many past emissions new subscribers receive, and does not require an initial value.

Both operators take a `SharingStarted` strategy, which controls precisely when the upstream cold flow begins executing and when it cancels to save device battery.

## Interview answer — deep senior

Under the hood, both operators launch a single sharing coroutine inside the provided `CoroutineScope`. This coroutine acts as a bridge: it collects from the upstream cold flow once, and fans out each emitted item to an internal `StateFlowImpl` or `SharedFlowImpl`.

The magic lies in how they manage the upstream subscription. When using cold streams like Room DAO queries or Bluetooth scanners, executing them continuously when the user minimizes the app drains battery. By pairing `stateIn` with `SharingStarted.WhileSubscribed(5000)`, the operator tracks active downstream subscribers via reference counting (`subscriptionCount`). When the last collector unsubscribes, it waits 5 seconds (to tolerate screen rotation) and then cancels the upstream collection coroutine, releasing hardware and database locks.

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
