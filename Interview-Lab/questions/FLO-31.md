---
id: "FLO-31"
question: "How do you choose SharingStarted for battery, correctness, and subscription behavior?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 144
editorial_status: "reviewed"
---

# FLO-31

## Original interview question

How do you choose SharingStarted for battery, correctness, and subscription behavior?

## What the interviewer evaluates

Choose SharingStarted using battery cost, freshness and subscriber transitions.

## Concept and technical explanation

Converting cold upstream Flows into hot StateFlows or SharedFlows via stateIn or shareIn requires selecting a SharingStarted strategy that balances battery efficiency, resource cleanup, and configuration change resilience.
SharingStarted controls the activation and cancellation lifecycle of the upstream flow producer coroutine based on downstream subscriber counts.
The Kotlin coroutines library provides three primary strategies: SharingStarted.Eagerly starts upstream production immediately upon invocation and never terminates, maintaining active connections regardless of subscriber presence; SharingStarted.Lazily starts upstream production only after the first subscriber attaches and persists indefinitely thereafter; and SharingStarted.WhileSubscribed(stopTimeoutMillis) activates upstream production upon the first subscriber and gracefully cancels upstream work when subscriber count drops to zero after a configurable timeout.
Configuring WhileSubscribed(5000) provides the Android standard: the 5-second grace period accommodates transient UI recreations (device rotation) without re-executing upstream queries, while reliably tearing down network sockets, hardware sensors, and Room database observers when the app moves to the background.

## Practical walkthrough (English)

Balancing battery efficiency and configuration change survival using SharingStarted:
```kotlin
class LiveFeedViewModel(
    private val locationRepository: LocationRepository,
    private val configRepository: ConfigRepository
) : ViewModel() {
    // 1. Production Standard for UI State: WhileSubscribed(5000)
    // Cancels GPS hardware in background, survives screen rotation!
    val locationState: StateFlow<LocationUiState> = locationRepository.observeGps()
        .map { LocationUiState.Success(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5000),
            initialValue = LocationUiState.Loading
        )

    // 2. Application-wide configuration: Lazily
    // Fetches once when first screen opens, cached forever in ViewModel:
    val appConfig: StateFlow<AppConfig> = configRepository.observeConfig()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.Lazily,
            initialValue = AppConfig.Default
        )
}
```

## Explanation in Arabic

اختيار استراتيجية `SharingStarted` المناسبة لتحقيق التوازن بين استهلاك البطارية والصحة البرمجية وسلوك الاشتراكات:

1. شجرة القرار الهندسي (Engineering Decision Tree):
   - **هل التدفق يمثل UI State في ViewModel ويعرض على الشاشة؟**
     * الإجابة دائماً: **`SharingStarted.WhileSubscribed(5_000L)`**.
     * **لماذا؟** يوقف التدفق في الـ Background لتوفير البطارية، ومهلة الـ 5 ثوانٍ تحافظ على استمرار التدفق أثناء تدوير الشاشة بدون إعادة تشغيل.

   - **هل التدفق يمثل Cache عالمي مشترك (Singleton / App Scope) لا نريد إعادة حسابه؟**
     * الإجابة: **`SharingStarted.Lazily`**.
     * **لماذا؟** ينتظر حتى تطلبه أول شاشة، وبمجرد تشغيله يظل حياً في الذاكرة لتستفيد منه كل الشاشات اللاحقة بدون تكرار الحساب.

   - **هل التدفق يمثل عملية حيوية يجب أن تبدأ فوراً حتى لو لم ينظر إليها أحد؟**
     * الإجابة: **`SharingStarted.Eagerly`**.
     * **لماذا؟** يبدأ فوراً مع إنشاء الكلاس، مثل: جلب وتجهيز إعدادات الأمان والتشفير عند بدء التطبيق.

## Practical walkthrough

تطبيق عملي لتوزيع الاستراتيجيات في تطبيق حقيقي:
```kotlin
// 1. شاشة UI عادية -> WhileSubscribed(5000):
val userProfile: StateFlow<UserProfile> = repository.observeUser()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000L), UserProfile.Empty)

// 2. كاش أسعار العملات في Singleton Repository -> Lazily:
@Singleton
class CurrencyRepository(api: CurrencyApi, appScope: CoroutineScope) {
    val exchangeRates = api.streamRates()
        .shareIn(appScope, SharingStarted.Lazily, replay = 1)
}

// 3. مراقبة حالة اتصال الإنترنت للتطبيق كله -> Eagerly:
@Singleton
class NetworkMonitor(context: Context, appScope: CoroutineScope) {
    val isOnline = observeNetworkConnectivity(context)
        .stateIn(appScope, SharingStarted.Eagerly, initialValue = true)
}
```

## Why it matters and how it works

`WhileSubscribed(stopTimeoutMillis, replayExpirationMillis)` controls stop and cache reset; stateIn can reset to initial value after replay expiration. A source may need reconnection/authentication on restart. Correctness of a continuous audit feed cannot depend on UI subscribers; run such work in a durable owner instead.

## Worked example

Android ViewModel illustration assumes source is cold Flow and initial Loading is a truthful state.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*

class SensorViewModel(source: Flow<String>) : ViewModel() {
    val reading = source.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        "loading",
    )
}
```

## Trade-offs and decision criteria

WhileSubscribed saves resources but can miss source changes when disconnected; a state source must provide current snapshot on reconnect. Eagerly costs idle resources. Lazily avoids pre-use cost but does not stop after use. Tune grace from measured rotation/background patterns.

## Failure modes

A sensor shared Eagerly in application scope can drain battery all day. WhileSubscribed on a transaction audit process can stop required recording when UI leaves. Replay after logout can expose stale user data if scope is not reset.

## Production perspective

A live exercise screen uses WhileSubscribed and a 5-second grace to avoid Bluetooth reconnect on rotation; a separate service owns any legally required continuous measurement. Session logout cancels sharing, and metrics track active connection time/reconnects.

## Interview answer — short

WhileSubscribed(5000) is the Android production standard, cancelling upstream sources when the app enters the background while surviving 5-second rotation pauses. Eagerly starts immediately and never stops; Lazily starts on first subscription and never stops, suited for global configs.

## Interview answer — structured

Choosing a SharingStarted strategy governs when upstream data producers start and stop executing.

SharingStarted.Eagerly launches upstream collection immediately upon instantiation and runs indefinitely. This wastes battery and memory by maintaining database cursors and network connections even before any UI screen subscribes.

In production, SharingStarted.Lazily waits for the first subscriber before launching, remaining active for the remainder of the CoroutineScope. It is ideal for one-time initialization data or app-wide configurations that should never re-trigger.
As for UI state pipelines, SharingStarted.WhileSubscribed(stopTimeoutMillis = 5000) is the industry standard. When the UI enters the background and collectors cancel via repeatOnLifecycle, the subscriber count drops to zero. WhileSubscribed waits 5 seconds: if the Activity was simply rotating, resubscription happens within milliseconds without restarting upstream work; if the app was backgrounded, it cancels upstream collection, powering down GPS radios and network sockets.


## Interview answer — deep senior

Under the hood in SharingStarted.kt, WhileSubscribed is implemented as a Flow operator observing the StateFlow's subscriptionCount. When subscriptionCount transitions from 0 to 1, WhileSubscribed emits SharingCommand.START to the sharing coroutine. When subscriptionCount drops back to 0, WhileSubscribed emits a delayed SharingCommand.STOP after the configured stopTimeoutMillis delay, followed optionally by SharingCommand.RESET_BUFFER if replayExpirationMillis elapses.
This 5000ms delay solves the fundamental Android configuration change dilemma. When an Activity rotates, onStop cancels the old collector, dropping subscriptionCount to zero. Approximately 100 to 300 milliseconds later, the new Activity reaches onStart and attaches a new collector, incrementing subscriptionCount back to 1. Because this transition occurs well within the 5000ms grace period, the stop timeout timer is cancelled, and upstream database or network connections continue running smoothly without re-executing.
Conversely, if the user presses the Home button, the app remains in the background past 5 seconds. The timer expires, triggering SharingCommand.STOP. This cancels the upstream coroutine, allowing Room database query observers and LocationManager listeners to tear down cleanly and enter low-power sleep mode.
In complex feature modules with multiple interdependent streams, WhileSubscribed coordinates lifecycle states cleanly, avoiding memory retention and preventing zombie coroutine background execution across all application layers.
Staff engineers ban Eagerly for screen-level ViewModels, mandating WhileSubscribed(5000) to ensure compliance with Google Play battery consumption vitals.

## How to answer in the interview

- **Why:** subscription policy affects resource use and first-value correctness.
- **How:** map sensor, warm app source, and durable task to owners.
- **Trade-off:** battery versus restart latency.
- **Failure case:** UI subscribers accidentally control required business work.
- **Production solution:** measure starts, replay expiry, and battery.

## Deep-dive talking points

Trace first subscriber, last subscriber, grace timeout, replay reset and logout.

## Follow-up questions

- **Interviewer:** "Why not set `stopTimeoutMillis` to 10 minutes just to be safe?"
  **Answer:** "Setting it to 10 minutes defeats battery conservation. The upstream network and database sensors will continue running in the user's pocket for 10 full minutes after leaving the screen, draining device battery."

- **Interviewer:** "What is `replayExpirationMillis` in `WhileSubscribed`?"
  **Answer:** "It configures when the replay cache expires after all subscribers leave. By default (0), the cache is kept forever. Setting it to e.g. 60,000ms evicts the cached state if the user stays away for longer than a minute, forcing a fresh load on return."

- **Interviewer:** "Can you implement a custom `SharingStarted` strategy?"
  **Answer:** "Yes. `SharingStarted` is an interface with a `command(subscriptionCount: StateFlow<Int>): Flow<SharingCommand>` function. You can emit `SharingCommand.START` and `SharingCommand.STOP` based on custom business rules or network states."

## Self-check rubric

Can I justify a policy from cost/correctness, predict restart and define session invalidation?

## References and reviewed-on date

- [Kotlin SharingStarted API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-sharing-started/) — start/stop and replay expiration.

Technically reviewed against primary documentation on 2026-10-13.
