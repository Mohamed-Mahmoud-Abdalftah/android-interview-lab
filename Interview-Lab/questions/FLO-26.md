---
id: "FLO-26"
question: "Your UI must display the most recent state after rotation. What stream type do you use and why?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 139
editorial_status: "reviewed"
---

# FLO-26

## Original interview question

Your UI must display the most recent state after rotation. What stream type do you use and why?

## What the interviewer evaluates

Choose a current-state stream for rotation while distinguishing ViewModel retention from process death.

## Explanation in Arabic

بعد rotation عادي، UI جديدة محتاجة آخر snapshot فورًا؛ `StateFlow` في ViewModel مناسبة لأنها hot وعندها `value` وآخر state للcollector الجديد. الـViewModel غالبًا بيعيش configuration change، لكن process death يمسحه، فلازم نعيد بناء state من SavedStateHandle للمدخلات الصغيرة ومن Room/server للبيانات المهمة. `SharedFlow(replay=0)` مش بديل لحالة حالية.

### Practical walkthrough in Egyptian Arabic

بعد rotation، Screen الجديدة محتاجة آخر `Loading/Ready/Error` فورًا؛ `StateFlow` من ViewModel تعطي current value طالما ViewModel نفس owner وعاشت configuration change. لكن process death مختلف: ViewModel هتتبني تاني، فلازم ID في SavedStateHandle/repository وتعيد تحميل. لا تستخدم SharedFlow(replay=0) لو المطلوب current state.

## Why it matters and how it works

StateFlow replays latest value and equality-conflates state. `stateIn(viewModelScope, started, initial)` can share a repository cold source. Lifecycle-aware collection re-subscribes on new view and immediately renders current state; business durability is separate.

## Worked example

Android ViewModel example assumes DAO emits durable items; `Item`/`ItemDao` are app types.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

data class Item(val id: String)
interface ItemDao { fun observe(): Flow<List<Item>> }
sealed interface ListUiState {
    data object Loading : ListUiState
    data class Ready(val items: List<Item>) : ListUiState
    data class Error(val message: String) : ListUiState
}
class ListViewModel(dao: ItemDao) : ViewModel() {
    val state: StateFlow<ListUiState> = dao.observe()
        .map<List<Item>, ListUiState> { ListUiState.Ready(it) }
        .catch { emit(ListUiState.Error("Could not load items")) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), ListUiState.Loading)
}
// ViewModel survives ordinary rotation; process death recreates it and reloads.
```

## Trade-offs and decision criteria

StateFlow is simple for latest snapshot, but an initial empty list may conflate loading and empty data; use sealed state when needed. A retained ViewModel avoids unnecessary reload on rotation but cannot guarantee state after process death. Persist business data.

## Failure modes

Using replay-zero SharedFlow may leave the new Activity blank until next emission. Keeping a MutableStateFlow only in Activity recreates it with default state. Assuming ViewModel retention across process death loses data.

## Production perspective

A feed ViewModel exposes Room-backed UI state. Rotation resubscribes and gets current value; on process recreation Room repopulates. Search query is restored from SavedStateHandle if needed, while server remains authoritative for account data.

## Interview answer — short

“I use StateFlow in a ViewModel for the latest UI snapshot because a new collector immediately receives the current value. The ViewModel generally survives rotation, but process death requires reconstruction from saved or durable data.”

## Interview answer — structured

“After rotation, a new view collector should not wait for another event to know what to draw. StateFlow stores a current value and replays it immediately. I expose it from a ViewModel that survives ordinary configuration changes and collect with lifecycle awareness. I make the initial state truthful, such as Loading, rather than assuming empty means loaded. For process death, I restore small navigation inputs from SavedStateHandle and rebuild persistent state from Room or the backend.”

## Interview answer — deep senior

“The guarantee is layered. StateFlow provides in-memory latest-state replay to a new collector. ViewModel retention across a normal configuration change keeps the producer and its state, but it does not preserve arbitrary process death. A Room-backed repository provides durable local data, and SavedStateHandle can restore lightweight query/selection inputs; the server remains authoritative where appropriate. `stateIn` can share a cold DAO Flow within the ViewModel, with WhileSubscribed to avoid repeated work. I test rotation for immediate current rendering and process recreation separately for reconstruction. One-shot navigation effects are not modeled as the same replayed state unless consumption is explicitly designed. I would choose StateFlow because the requirement is a current snapshot for a new collector. The ViewModel survives an ordinary configuration change under the correct owner, so the newly created screen can subscribe and immediately observe the latest value. A plain cold Flow might restart expensive work, and a zero-replay SharedFlow has no current state to hand over. I would model Loading, Ready, and Error explicitly and collect with lifecycle awareness. I also draw the boundary around process death: the ViewModel and StateFlow instance are recreated, so a saved ID and durable repository data must rebuild the state. I test rotation and eligible process recreation separately, because success in one does not prove the other.”

## How to answer in the interview

- **Why:** a recreated UI needs current state immediately.
- **How:** ViewModel-owned StateFlow plus lifecycle collector.
- **Trade-off:** process death still requires durable reconstruction.
- **Failure case:** zero-replay event stream leaves blank UI.
- **Production solution:** test rotation and process recreation separately.

## Deep-dive talking points

Distinguish stream replay, ViewModel retention and durable source reconstruction.

## Follow-up questions

- [FLO-05](../flo-05/): Why initial value? **Answer:** StateFlow always has readable current state.
- [FLO-27](../flo-27/): Should navigation be in latest state? **Answer:** only with explicit consumed/destination semantics.

## Self-check rubric

Can I guarantee rotation snapshot, identify process-death gap and choose saved versus durable data?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — latest-value replay.
- [Android ViewModel saved state](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) — recreation limits.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
