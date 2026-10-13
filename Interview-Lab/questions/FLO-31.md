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

Choose WhileSubscribed(5000) for ViewModel UI states to conserve battery in the background while surviving configuration changes; choose Lazily for shared application-scoped caches that should initialize on first access and stay cached; choose Eagerly for critical process-wide monitoring that must start immediately upon creation.

## Interview answer — structured

Choosing the right `SharingStarted` strategy is an exercise in balancing battery conservation, memory retention, and UI latency across three architectural tiers:

1. **`WhileSubscribed(5000)` for ViewModel UI State:** This is the default standard for feature screens. It activates upstream collection only when UI collectors are active. When the user backgrounds the app, it cancels upstream after a 5-second grace period to save battery, but survives screen rotation without re-fetching. It is essential for offline-first Room or network observation flows.

2. **`Lazily` for In-Memory Shared Caches:** In singleton repositories or domain services, `Lazily` delays expensive upstream initialization until the very first consumer requests the data. Once started, it remains active in memory, caching emissions for all subsequent app features without redundant restarts.

3. **`Eagerly` for Mission-Critical Infrastructure:** For application-wide monitors that must begin capturing state immediately upon app launch—such as monitoring network connectivity flags or device security posture—`Eagerly` ensures the flow is immediately active before any UI subscribes.

## Interview answer — deep senior

The battery implications of these choices are profound in production Android vitals. If an engineer naively defaults to `SharingStarted.Eagerly` in a ViewModel, and that ViewModel observes an upstream location flow or a continuous Room database query, that query will run indefinitely in the background whenever that screen is in the backstack! Over hundreds of thousands of users, this results in significant battery drain and elevated uninstallation rates.

By implementing `WhileSubscribed(5000)`: The 5-second timer is specifically calibrated to Android OS lifecycle timings. An Activity recreation during rotation typically takes between 100ms and 500ms. A 5,000ms timeout provides a 10x safety margin, guaranteeing zero flow thrashing during rotation while reliably shutting down within 5 seconds when the user navigates away or presses the home button.

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
