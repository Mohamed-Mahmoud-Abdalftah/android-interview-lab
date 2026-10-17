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

## Concept and technical explanation

In modern Android architecture, retaining and restoring the most recent UI state across configuration changes (such as device rotation) without re-triggering expensive background work mandates StateFlow.
Device rotation destroys and recreates the visual View hierarchy (Activity or Fragment) while the hosting ViewModel remains preserved in memory. When the recreated UI attaches to data streams in onStart, it requires an immediate state emission representing the latest valid screen data.
StateFlow satisfies this architectural requirement through three native mechanisms: first, it maintains an explicit replay cache of size 1 (replay = 1), ensuring that newly subscribed UI observers immediately receive the latest snapshot upon collection; second, it provides a synchronous, thread-safe .value property, allowing immediate non-suspending state reads during Compose initial composition or view binding; third, it applies state conflation via structural equality checks (Any.equals), discarding redundant identical emissions to prevent unnecessary UI re-rendering and recomposition cycles.

## Practical walkthrough (English)

Preserving and restoring UI state across configuration changes with StateFlow:
```kotlin
class ProductDetailsViewModel(
    private val repository: ProductRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val productId: String = checkNotNull(savedStateHandle["productId"])

    // Private mutable state backing property:
    private val _uiState = MutableStateFlow<ProductDetailsUiState>(ProductDetailsUiState.Loading)
    // Exposed as read-only StateFlow to the UI:
    val uiState: StateFlow<ProductDetailsUiState> = _uiState.asStateFlow()

    init {
        loadProduct()
    }

    private fun loadProduct() {
        viewModelScope.launch {
            _uiState.value = ProductDetailsUiState.Loading
            try {
                val details = repository.fetchProduct(productId)
                _uiState.value = ProductDetailsUiState.Success(details)
            } catch (e: Exception) {
                _uiState.value = ProductDetailsUiState.Error(e.message ?: "Failed to load")
            }
        }
    }
}
```

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

We use StateFlow because it retains the latest state in a replay cache of size one, delivering it instantly to recreated UI components upon rotation. It supports synchronous value reads and automatically conflates identical updates to eliminate redundant recompositions.

## Interview answer — structured

Managing screen rotation requires a hot stream that preserves state across Activity destruction and recreation.

StateFlow is designed specifically as a single-source-of-truth state holder. Because ViewModels outlive configuration changes, housing a StateFlow inside the ViewModel guarantees that cached data remains intact while the visual hierarchy rebinds.

In production, cold Flows are unsuitable because each new collector re-triggers upstream database queries or network requests from scratch, causing flickering spinners and wasted bandwidth. Similarly, SharedFlow with default settings discards emissions when collectors detach during rotation.
As for lifecycle integration, StateFlow emits its current value immediately to the new observer without latency. Paired with collectAsStateWithLifecycle, StateFlow seamlessly restores UI state upon rotation while safely suspending collection when the app moves to the background.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines.flow, StateFlow is implemented as a specialized SharedFlow variant where replay is locked to 1 and onBufferOverflow is locked to BufferOverflow.DROP_OLDEST. It stores its current state directly in a volatile memory reference, ensuring that reading .value is an atomic, non-suspending, O(1) operation.
When an Activity rotates, the previous collector scope is cancelled in onStop, decrementing the StateFlow subscriber counter. When the new Activity reaches onStart, collectAsStateWithLifecycle or repeatOnLifecycle resubscribes. The StateFlow immediately routes its cached head element to the new subscriber slot, restoring the complete UI layout before the first frame renders.
Crucially, StateFlow enforces automatic conflation using structural equality (oldState == newState). If the ViewModel assigns an identical state instance, StateFlow skips emission entirely, preventing wasted Compose recomposition passes and View re-bindings.
In large-scale production architectures, StateFlow serves as the single source of truth driving Jetpack Compose rendering. Because Compose functions can recompose dozens of times per second, StateFlow's internal equality checks eliminate redundant layout passes, ensuring smooth 120Hz frame rates across all modern high-refresh-rate Android devices.
Compared to legacy LiveData, StateFlow is pure Kotlin multiplatform-compatible, deterministic, and supports comprehensive reactive transformations (map, combine, filter) without requiring Android main-thread dispatcher constraints during repository updates.
Staff engineers expose state strictly via read-only interfaces: maintaining a private MutableStateFlow and exposing asStateFlow() guarantees unidirectional data flow integrity across architecture boundaries.

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
