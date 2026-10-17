---
id: "FLO-09"
question: "Compare SharingStarted.Eagerly, Lazily, and WhileSubscribed."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "A"
phase: 1
priority: "P1"
order: 122
editorial_status: "reviewed"
---

# FLO-09

## Original interview question

Compare SharingStarted.Eagerly, Lazily, and WhileSubscribed.

## What the interviewer evaluates

Compare eager, lazy and subscriber-driven sharing including restart and resource tradeoffs.

## Concept and technical explanation

The SharingStarted strategy parameter in stateIn and shareIn governs the precise execution lifecycle of the upstream cold flow subscription, dictating when data production commences and terminates based on collector presence.
SharingStarted.Eagerly starts upstream collection immediately upon instantiation of the sharing coroutine and executes indefinitely until the parent CoroutineScope terminates, regardless of whether any UI subscriber ever collects the stream.
SharingStarted.Lazily defers upstream execution until the very first subscriber attaches, but once activated, it remains executing permanently even if all subscribers subsequently detach.
SharingStarted.WhileSubscribed(stopTimeoutMillis, replayExpirationMillis) provides the standard Android UI lifecycle strategy. It activates upstream production only when at least one active subscriber is observing, and introduces a configurable grace period (typically 5,000 milliseconds) when the subscriber count drops to zero. This 5-second window prevents wasteful upstream cancellation and restart cycles during transient configuration changes like screen rotations, while ensuring physical resources such as network sockets, database query observers, and hardware sensors are cleanly shut down when the screen is placed in the background.

## Practical walkthrough (English)

Configuring sharing strategies in an Android ViewModel:
```kotlin
class LiveScoresViewModel(private val repository: ScoresRepository) : ViewModel() {
    // Standard Android presentation strategy:
    // Survives screen rotation without restarting, stops 5s after app backgrounds
    val matchScores: StateFlow<MatchUiState> = repository.observeLiveScores()
        .map { MatchUiState.Live(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
            initialValue = MatchUiState.Loading
        )

    // Eager background sync: runs continuously while ViewModel is alive
    val unreadBadgeCount: StateFlow<Int> = repository.observeUnreadCount()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.Eagerly,
            initialValue = 0
        )
}
```

## Explanation in Arabic

المقارنة بين استراتيجيات `SharingStarted` في `stateIn` و `shareIn` هي جوهر الحفاظ على موارد الهاتف والبطارية في أندرويد:

1. `SharingStarted.Eagerly` (البدء الفوري المستمر):
   - يبدأ البث فوراً بمجرد إنشاء الـ ViewModel في الذاكرة.
   - **لا يتوقف أبداً** حتى لو لم يكن هناك أي مستمع، وحتى لو خرج المستخدم من الشاشة وظل الـ ViewModel حياً في الـ Backstack!
   - **الاستخدام:** البيانات الحيوية جداً التي يجب أن تظل محدثة في الخلفية دائماً، ولكن يجب الحذر منه لتجنب إهدار البطارية.

2. `SharingStarted.Lazily` (البدء الكسول مع أول مستمع):
   - لا يبدأ حتى يشترك أول مستمع (First Subscriber).
   - **بمجرد أن يبدأ، لا يتوقف أبداً!** حتى لو ألغى كل المستمعين اشتراكاتهم لاحقاً.

3. `SharingStarted.WhileSubscribed(stopTimeoutMillis)` (الاستراتيجية الذهبية لأندرويد):
   - يبدأ العمل فقط عندما يكون هناك مستمع نشط على الشاشة.
   - **يتوقف ويلغي الـ Upstream تلقائياً** عندما يغادر آخر مستمع الشاشة بعد انتهاء مهلة الـ Timeout (عادة 5 ثوانٍ).
   - **لماذا 5 ثوانٍ (5_000L)؟** لتغطية وقت تدوير الشاشة (Configuration Change)؛ حتى لا نلغي طلب الشبكة أو استعلام الداتابيز ونعيده من الصفر أثناء تدوير الشاشة!

## Practical walkthrough

مقارنة عملية في استهلاك البطارية والشبكة:
```kotlin
class FeedViewModel(private val feedRepository: FeedRepository) : ViewModel() {
    
    // ✅ الاستراتيجية الصحيحة بنسبة 100% في Android:
    val feedState: StateFlow<FeedUiState> = feedRepository.observeLiveFeed()
        .map { FeedUiState.Success(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000L),
            initialValue = FeedUiState.Loading
        )
}
```
لو المستخدم وضع التطبيق في الخلفية (Background): بعد 5 ثوانٍ يتم إيقاف `observeLiveFeed()` وتوفير بطارية الجهاز. لو فتح التطبيق مجدداً، يعود البث تلقائياً.

## Why it matters and how it works

`SharingStarted` controls the sharing coroutine, not whether a hot flow instance exists. With WhileSubscribed, stop timeout reduces churn; replay expiration can reset replay cache, and stateIn resets to its initial value when configured expiration elapses. Match policy to freshness, connection cost and security/session scope.

## Worked example

Android ViewModel example assumes `source` is a cold Flow of immutable UiState and initial value is truthful.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class StatusViewModel(source: Flow<String>) : ViewModel() {
    val status = source.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        "loading",
    )
}
```

## Trade-offs and decision criteria

Eagerly lowers first-subscriber wait but consumes battery/network before demand. Lazily avoids initial idle work but does not stop after subscribers leave. WhileSubscribed saves resources yet can restart a costly source. Use a small stop timeout to span transient lifecycle gaps when appropriate.

## Failure modes

Assuming Lazily stops on background can leave a socket active for the entire ViewModel lifetime. Setting WhileSubscribed stop timeout to zero can reconnect on every brief STOP/START. A long replay cache may show stale user data after session change.

## Production perspective

A live score screen uses WhileSubscribed with a short grace window to survive rotation without reconnect, while a session owner cancels sharing at logout. Metrics count reconnects and battery cost; tests simulate subscriber transitions.

## Interview answer — short

SharingStarted controls when upstream collection starts and stops in stateIn and shareIn. Eagerly starts immediately and never stops; Lazily starts with the first subscriber and runs forever; WhileSubscribed with a 5000ms timeout activates only while UI subscribers exist and waits five seconds before cancelling, bridging screen rotations while preserving battery in the background.

## Interview answer — structured

The SharingStarted policy dictates the lifetime and execution boundary of the upstream coroutine in stateIn and shareIn.

Each policy strikes a different balance between freshness and resource consumption. Eagerly starts upstream production the instant the ViewModel is instantiated, ignoring subscriber presence completely. We reserve it for critical background sync tasks that must start immediately.

In production, Lazily defers execution until the initial subscriber attaches, but continues running even after all subscribers detach. This makes it suitable for immutable caches that should warm up on demand without restarting.

WhileSubscribed with a five-second timeout is the definitive gold standard for Android presentation layers. When UI collectors transition to zero during screen rotation, the five-second countdown prevents tearing down expensive database or WebSocket connections. If the user navigates away or backgrounds the app, the timer elapses and cancels upstream production, stopping battery drain and radio activity.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines, WhileSubscribed is implemented by observing the subscriptionCount StateFlow of the underlying SharedFlow instance. When subscriptionCount transitions from zero to one, WhileSubscribed emits SharingCommand.START, instructing the sharing loop to launch the upstream collector coroutine.
When subscriptionCount drops back to zero, such as when an Activity invokes onStop and unbinds its repeatOnLifecycle block, WhileSubscribed emits a command sequence: it introduces a delay of stopTimeoutMillis, followed by SharingCommand.STOP. If a new subscriber arrives before the timer completes—which reliably happens during Activity recreation within 300 milliseconds—subscriptionCount rises back to one, aborting the pending cancellation timer and keeping the upstream connection intact.
The second configuration parameter, replayExpirationMillis, governs cache freshness. Setting replayExpirationMillis to zero preserves the cached state indefinitely during pauses. Supplying a non-zero timeout resets the replay cache to initialValue once the timeout elapses, preventing the UI from showing stale financial data when the user returns after thirty minutes.
Additionally, in automated unit testing, test dispatchers pause virtual time; developers must call advanceTimeBy(5001) to simulate subscriber detachment and verify that the upstream sharing job was cancelled cleanly as expected.
Staff engineers pair WhileSubscribed(5000) with collectAsStateWithLifecycle in Jetpack Compose or repeatOnLifecycle in Views. Using plain collectAsState fails to decrement subscriptionCount in the background, keeping WhileSubscribed running perpetually and defeating battery conservation.

## How to answer in the interview

- **Why:** start policy controls upstream lifetime and resource use.
- **How:** compare zero-subscriber and return paths.
- **Trade-off:** battery versus warm state and restart cost.
- **Failure case:** Eagerly runs a sensor offscreen or WhileSubscribed stops required work.
- **Production solution:** measure starts and test rotation gaps.

## Deep-dive talking points

Explain subscription transitions, replay expiration, rotation grace and session logout.

## Follow-up questions

- **Interviewer:** "What happens if you use `WhileSubscribed()` without a timeout parameter (i.e. timeout = 0)?"
  **Answer:** "If timeout is 0, the upstream flow cancels instantly the millisecond the Activity is destroyed during rotation. A fraction of a second later when the new Activity recreates and collects, the flow starts over from scratch, triggering duplicate network requests and UI flickering."

- **Interviewer:** "Can you unit test `WhileSubscribed(5000)` deterministically?"
  **Answer:** "Yes. When testing with `runTest` and Turbine, `testScheduler` skips the 5,000ms delay virtually with `advanceTimeBy(5001)`, allowing you to verify that upstream collection halted."

- **Interviewer:** "Does `WhileSubscribed` work if the UI collects using plain `collectAsState()` in Compose?"
  **Answer:** "`collectAsState()` does not pause collection when the app is in the background, so `subscriptionCount` never drops to 0 while the composition is active. You must use `collectAsStateWithLifecycle()` to ensure subscribers drop to 0 when the app is backgrounded."

## Self-check rubric

Can I predict start/stop for all three, explain timeout, and identify a correctness risk on restart?

## References and reviewed-on date

- [Kotlin SharingStarted API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/) — policy semantics.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — lifecycle use.

Technically reviewed against primary documentation on 2026-10-13.
