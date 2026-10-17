---
id: "SOL-11"
question: "How would you replace a giant BaseActivity with smaller composable behaviors?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 182
editorial_status: "reviewed"
---

# SOL-11

## Original interview question

How would you replace a giant BaseActivity with smaller composable behaviors?

## What the interviewer evaluates

Replace a giant inheritance hub with optional capabilities while preserving lifecycle and behavior.

## Concept and technical explanation

Replacing a bloated BaseActivity with smaller composable behaviors embodies the composition over inheritance principle and Interface Segregation. A monolithic BaseActivity acts as an anti-pattern God Class that accumulates analytics tracking, toolbar setup, permission handling, loading dialogs, network connectivity monitoring, and dependency injection ceremony. Instead of forcing every screen to inherit this heavy baggage, senior engineers decompose these orthogonal concerns into focused DefaultLifecycleObserver classes, ActivityResultContract delegates, custom view components, or Jetpack Compose composition wrappers.

## Practical walkthrough (English)

Decomposing a God BaseActivity into decoupled lifecycle observers and delegates:
```kotlin
// BAD ANTI-PATTERN: God BaseActivity forces all screens to inherit bloated baggage
abstract class GodBaseActivity : AppCompatActivity() {
    fun trackScreenView() { /* analytics */ }
    fun showLoadingDialog() { /* dialog */ }
    fun monitorNetwork() { /* broadcast receiver */ }
    fun requestCameraPermission() { /* permission logic */ }
}

// ARCHITECTURAL BEST PRACTICE: Standalone lifecycle-aware behavioral delegates
class AnalyticsTrackerDelegate(
    private val screenName: String,
    private val analytics: AnalyticsService
) : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        analytics.trackScreen(screenName)
    }
}

class NetworkMonitorDelegate(
    private val context: Context,
    private val onConnectionChanged: (Boolean) -> Unit
) : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) { /* register network callback */ }
    override fun onStop(owner: LifecycleOwner) { /* unregister network callback */ }
}

// Clean Activity composed of only the behaviors it actually needs
class UserProfileActivity : AppCompatActivity() {
    private val analyticsTracker by lazy { AnalyticsTrackerDelegate("ProfileScreen", getAnalyticsService()) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(analyticsTracker)
        // Screen only subscribes to behaviors it genuinely requires
    }
}
```

## Explanation in Arabic

كيف تستبدل كلاس `BaseActivity` ضخم وعملاق بسلوكيات تركيبية صغيرة (Small Composable Behaviors)؟

1. تشريح الـ BaseActivity العملاق (The God Base Class):
   - يحتوي عادة على: تتبع التحليلات (Analytics tracking)، فحص الاتصال بالإنترنت (Network observer)، شريط الأدوات (Toolbar setup)، مؤشر التحميل العام (Global Progress Dialog)، وإدارة أذونات النظام (Permission handling).
   - كل الشاشات مجبرة على وراثة كل هذا التعقيد حتى لو كانت شاشة بسيطة لا تحتاج شيئاً منه!

2. استراتيجية التفكيك إلى سلوكيات تركيبية (Modular Decomposition):
   - **السلوك 1: مراقبة دورة الحياة عبر LifecycleObserver**:
     * سحب فحص الجلسة والتحليلات إلى كلاسات تنفذ `DefaultLifecycleObserver`.
     * الـ Activity تقوم فقط بـ `lifecycle.addObserver(analyticsObserver)`.
   - **السلوك 2: تفويض واجهة المستخدم عبر Jetpack Compose**:
     * استبدال كود الـ Toolbar والـ Loading بـ Composable Reusable Scaffolds (`AppScaffold`).
   - **السلوك 3: إدارة الأذونات عبر Activity Result APIs**:
     * استخدام `registerForActivityResult` المدمج كـ Component مستقل.

## Practical walkthrough

تفكيك BaseActivity عملاق إلى كلاسات LifecycleObservers ومكونات Compose:
```kotlin
// 1. سلوك تتبع التحليلات معزول كمراقب لدورة الحياة:
class AnalyticsLifecycleObserver(private val tracker: AnalyticsTracker) : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        tracker.logScreenVisit(owner.javaClass.simpleName)
    }
}

// 2. سلوك فحص الاتصال معزول كمراقب شبكة:
class NetworkMonitorObserver(private val networkMonitor: NetworkMonitor) : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) { networkMonitor.start() }
    override fun onStop(owner: LifecycleOwner) { networkMonitor.stop() }
}

// 3. النشاط أصبح نظيفاً تماماً بدون أي وراثة من BaseActivity مخصص:
@AndroidEntryPoint
class OrderActivity : ComponentActivity() {
    @Inject lateinit var analyticsObserver: AnalyticsLifecycleObserver
    @Inject lateinit var networkObserver: NetworkMonitorObserver

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate()
        // تركيب السلوكيات بنعومة واستقلالية:
        lifecycle.addObserver(analyticsObserver)
        lifecycle.addObserver(networkObserver)

        setContent {
            AppScaffold(title = "Orders") {
                OrderScreenContent()
            }
        }
    }
}
```

## Why it matters and how it works

A giant base class couples every child to unrelated hooks and shared lifecycle assumptions. Composition exposes only needed capabilities and makes ownership testable. Incremental migration limits regressions.

## Worked example

Conceptual flow: `CatalogActivity` receives `ToolbarController` and `AnalyticsObserver`; `CameraActivity` receives only analytics. Both may extend the framework `ComponentActivity`, but neither has to implement an unsupported `setupToolbar()`. The analytics observer registers and unregisters at documented lifecycle points.

## Trade-offs and decision criteria

Composition adds wiring and possibly small interfaces. A tiny stable base helper can remain if every child truly uses it and the contract is sound. Avoid replacing one giant base with a giant service locator.

## Failure modes

BaseActivity holds a View binding and global analytics callback after Activity recreation, leaking the old screen. Moving code without lifecycle review preserves the leak. Contract tests and LeakCanary/device checks may be needed for actual device behavior.

## Production perspective

A media app migrates toolbar screens first, then permission flows, while keeping old base compatibility temporarily. Each release verifies recreation and back navigation. After all callers move, the base is removed.

## Interview answer — short

We replace a giant BaseActivity by decomposing its responsibilities into small, focused lifecycle observers and behavioral delegates. Instead of forcing all screens into an inheritance hierarchy with unwanted analytics, permission, and network boilerplate, we create dedicated classes implementing DefaultLifecycleObserver. Activities then plug in only the specific behaviors they require using lifecycle.addObserver or Kotlin class delegation, eliminating rigid coupling and making each capability independently testable on the JVM.

## Interview answer — structured

Eliminating a monolithic BaseActivity is a critical architectural milestone in modernizing Android codebases.
In legacy Android development, BaseActivity became the default repository for any reusable UI logic. Over time, it accumulated analytics trackers, permission request managers, network status observers, progress dialog helpers, and authentication checkers. This violated the Single Responsibility Principle and forced child screens into rigid inheritance coupling, often breaking Liskov Substitution when child activities had to override unwanted base methods with empty implementations.
To dismantle this anti-pattern, we categorize base behaviors and isolate each into a dedicated delegate.
First, lifecycle-bound operations like analytics screen tracking and sensor listeners are moved into classes implementing DefaultLifecycleObserver, registered explicitly via lifecycle.addObserver in the child activity.
Second, interactive workflows like camera permissions or file picking are migrated to Jetpack ActivityResultContracts injected or declared at the call site.
Third, UI chrome such as top app bars and loading indicators are encapsulated inside reusable Jetpack Compose layout containers or custom view components.
This compositional model ensures activities declare only the exact behaviors they need, keeping inheritance trees flat and modular.

## Interview answer — deep senior

Under the hood, dismantling BaseActivity directly addresses classloader performance, Dalvik method dispatch overhead, and testability boundaries in modern Android runtime environments.
When a monolithic BaseActivity defines dozens of open methods and lifecycle overrides, every single derived Activity inherits an inflated virtual method table (v-table). The Android ART runtime must maintain these expanded dispatch tables in memory, increasing class verification time upon initial APK startup and reducing CPU cache locality during polymorphic dispatch.
Furthermore, BaseActivity creates a hidden coupling hazard in multi-module architectures. Because BaseActivity typically lives in a common core UI module, that module must import analytics SDKs, network connectivity managers, and authentication repositories. This pulls heavy infrastructure dependencies into the core module, forcing every feature module to recompile whenever an underlying tracking library updates.
By transitioning to standalone DefaultLifecycleObserver components, each delegate resides in its respective domain or feature module. A feature screen simply attaches the delegates it requires.
From a testing perspective, testing an Activity tied to BaseActivity requires launching an instrumentation test runner or Robolectric shadow environment to satisfy all inherited dependencies. With delegates, engineers write lightning-fast JVM unit tests verifying that the delegate accurately handles lifecycle callbacks without ever instantiating an Android Activity context, ensuring resilient continuous integration pipelines.

## How to answer in the interview

- **Why:** Describe usage inventory.
- **How:** show staged extraction.
- **Trade-offs:** admit migration wiring.
- **Failure cases:** flag lifecycle duplicate callbacks.
- **Production solutions:** close with recreation tests and change-locality check..

## Deep-dive talking points

Plan an incremental migration, assign lifecycle owners, and identify an LSP violation hidden by base hooks.

## Follow-up questions

- **Interviewer:** "What is `DefaultLifecycleObserver` and why is it preferred over overriding Activity methods?"
  **Answer:** "It provides callbacks (`onStart`, `onResume`, `onDestroy`) that decoupled components can observe directly, removing the need for subclasses to call `super.onStart()`."

- **Interviewer:** "How does removing `BaseActivity` improve incremental build times?"
  **Answer:** "In multi-module projects, modifying `BaseActivity` forces Gradle to recompile every single feature module that inherits from it. Modular delegates localize recompilations to the modified component only."

## Self-check rubric

List three base responsibilities, one lifecycle leak, and a two-step migration with parity checks.

## References and reviewed-on date

- [Android app architecture](https://developer.android.com/topic/architecture) — component lifecycle and separation of concerns.
- [Kotlin delegation](https://kotlinlang.org/docs/delegation.html) — composition helper.

Technically reviewed against primary documentation on 2026-10-13.
