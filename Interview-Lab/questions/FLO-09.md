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

Eagerly starts upstream immediately and never stops; Lazily starts with the first subscriber and stays active permanently; WhileSubscribed(5000) starts with the first subscriber, cancels upstream when subscribers drop to zero after a 5-second grace period, making it the premier choice for battery conservation across Android rotations.

## Interview answer — structured

The `SharingStarted` strategy governs the lifecycle of the upstream flow in `stateIn` and `shareIn`, deciding when collection starts and stops based on subscriber presence.

**SharingStarted.Eagerly** starts collecting from upstream immediately upon creation and never cancels until the parent scope is destroyed, regardless of whether any UI component is observing. It is best for critical background sync tasks that must start immediately.

**SharingStarted.Lazily** defers execution until the first subscriber collects, but once started, it remains active indefinitely even if all subscribers disconnect. It is suitable for expensive one-time caches that should not restart.

**SharingStarted.WhileSubscribed(5000)** is the gold standard for Android UI development. It only activates upstream collection when there is at least one active subscriber. When subscribers drop to zero, it waits 5,000 milliseconds before cancelling the upstream flow. This 5-second window prevents cancelling and restarting expensive network or database queries during configuration changes like screen rotations.

## Interview answer — deep senior

At the technical mechanism level, `WhileSubscribed` monitors the `subscriptionCount` state flow of the underlying `SharedFlow`. When `subscriptionCount.value` transitions from 0 to 1, it starts the upstream collector coroutine. When it drops back to 0, it launches a delay timer:

```kotlin
SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000, replayExpirationMillis = 0)
```

If a new subscriber attaches within the 5,000ms window (which happens during Activity recreation upon screen rotation), the cancellation timer is cancelled and upstream collection continues uninterrupted.

The second parameter, `replayExpirationMillis`, determines when the cached replay buffer is reset. Leaving it at 0 means that when the upstream is cancelled due to inactivity, the cached state is kept. If set to a duration, it evicts stale cached state after the user leaves the screen for an extended period.

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
