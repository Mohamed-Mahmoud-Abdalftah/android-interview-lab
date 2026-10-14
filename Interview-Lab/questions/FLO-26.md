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

عرض أحدث حالة للواجهة بعد تدوير الشاشة (Displaying the most recent state after rotation) هو الوظيفة الأساسية التي صُمم من أجلها `StateFlow`:

1. ما هو نوع الـ Stream المطلوب ولماذا؟
   - **النوع المطلوب هو: `StateFlow<UiState>`**.
   - **السبب 1 (State Retention):** الـ StateFlow يحتفظ دائماً بآخر قيمة تم إصدارها في الذاكرة (`.value`). عندما يتم تدوير الشاشة وتدمير الـ Activity القديمة وإنشاء Activity جديدة، تشترك الـ Activity الجديدة في الـ StateFlow فتستلم القيمة الأخيرة فوراً في نفس الفريم (Instantaneous restore).
   - **السبب 2 (No Re-execution):** لأنه Hot Stream، لا يعيد تشغيل استعلام قاعدة البيانات أو طلب الشبكة من الصفر (على عكس Cold Flow الذي سيبدأ من البداية عند كل تدوير).
   - **السبب 3 (Conflation):** لو الحالة لم تتغير، لن يسبب Recomposition غير ضروري.

2. لماذا لا نستخدم SharedFlow أو Cold Flow؟
   - Cold Flow سيعيد إرسال طلب الشبكة عند كل تدوير للشاشة!
   - SharedFlow بـ `replay = 0` لن يرسل أي شيء للشاشة الجديدة بعد التدوير، وستظل الشاشة فارغة أو بيضاء!

## Practical walkthrough

النمط المتبع في الـ Production:
```kotlin
class DashboardViewModel(private val repository: DashboardRepository) : ViewModel() {
    
    // نحول تدفق البيانات إلى StateFlow يحتفظ بالحالة عبر التدوير:
    val uiState: StateFlow<DashboardUiState> = repository.observeDashboardData()
        .map { DashboardUiState.Success(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000L), // 5 ثوانٍ تكفي التدوير وزيادة
            initialValue = DashboardUiState.Loading
        )
}
```
عندما يدور المستخدم الهاتف من عمودي لأفقي: يتم إغلاق الـ Activity القديمة، وإنشاء الجديدة، وتشترك في `uiState`، فتستلم `DashboardUiState.Success` المحفوظ في الكاش في صفر ثانية بدون أي شاشة تحميل أو وميض.

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

Use StateFlow. Because StateFlow is a hot stream that retains its latest value (.value) in memory and replays it immediately to new subscribers, the newly recreated Activity/Composable after rotation receives the exact current UI state instantly without re-fetching from the network or database.

## Interview answer — structured

To display the most recent UI state immediately after screen rotation, the required stream primitive is **`StateFlow`**.

When an Android device rotates, the Activity is destroyed and recreated. Because the ViewModel survives configuration changes, any state retained in the ViewModel is preserved in memory.

StateFlow is tailor-made for this scenario.

First, it is a **hot stream** that holds the most recent state in its `.value` property. Finally, when the newly created Activity or Composable subscribes, StateFlow immediately replays that latest cached state, allowing the UI to render the complete screen instantly on its very first frame.

If you used a plain cold Flow, the new Activity would trigger a fresh execution of the flow, repeating database reads or network calls. If you used a SharedFlow with `replay = 0`, the new Activity would receive nothing and render an empty blank screen.


## Interview answer — deep senior

Architecturally, pairing `StateFlow` with `SharingStarted.WhileSubscribed(5000)` in `stateIn()` is what makes this robust: During rotation, the old Activity's `repeatOnLifecycle` or `collectAsStateWithLifecycle` unbinds, dropping `subscriptionCount` to 0. The 5-second buffer prevents the ViewModel from cancelling the upstream repository flow. When the new Activity binds within a few hundred milliseconds, `subscriptionCount` jumps back to 1. StateFlow delivers the cached state immediately without missing a beat.

In Jetpack Compose, the UI consumes it via:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

Compose reads the cached value on initial composition, preventing any flash of an empty state or loading spinner.


## How to answer in the interview

- **Why:** a recreated UI needs current state immediately.
- **How:** ViewModel-owned StateFlow plus lifecycle collector.
- **Trade-off:** process death still requires durable reconstruction.
- **Failure case:** zero-replay event stream leaves blank UI.
- **Production solution:** test rotation and process recreation separately.

## Deep-dive talking points

Distinguish stream replay, ViewModel retention and durable source reconstruction.

## Follow-up questions

- **Interviewer:** "What if the process is killed by the OS due to low memory instead of a rotation?"
  **Answer:** "StateFlow in memory is lost on process death. For states that must survive process death (like draft forms or navigation arguments), persist critical fields into `SavedStateHandle` using `savedStateHandle.getStateFlow(key, initialValue)`."

- **Interviewer:** "Can you use `SharedFlow(replay = 1)` instead of `StateFlow`?"
  **Answer:** "Conceptually yes, but `StateFlow` is superior for UI state because it enforces non-nullable initial state, provides synchronous `.value` access, and includes built-in equality suppression via `equals()`."

- **Interviewer:** "Why is `LiveData` also capable of surviving rotation?"
  **Answer:** "Because `LiveData` also caches its latest value (`mValue`) in memory and dispatches it to active observers upon lifecycle start. However, StateFlow is preferred because it is pure Kotlin Multiplatform and integrates with coroutines seamlessly."

## Self-check rubric

Can I guarantee rotation snapshot, identify process-death gap and choose saved versus durable data?

## References and reviewed-on date

- [Kotlin StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) — latest-value replay.
- [Android ViewModel saved state](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) — recreation limits.

Technically reviewed against primary documentation on 2026-10-13.
