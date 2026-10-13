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

Replace a giant `BaseActivity` by decomposing its responsibilities into small, lifecycle-aware delegates implementing `DefaultLifecycleObserver` (for analytics and session timeouts), modern `ActivityResultContracts` (for permissions), and reusable Compose `AppScaffold` wrappers (for UI loading and toolbars).

## Interview answer — structured

Dismantling a monolithic `BaseActivity` requires migrating from inheritance-based coupling to modular lifecycle composition.

A typical bloated `BaseActivity` agglomerates multiple orthogonal concerns:
1. Screen analytics and tracking.
2. Network connectivity monitoring.
3. Global loading spinners and error dialogs.
4. Runtime permissions management.
5. Theme/Toolbar setup.

**The Modular Replacement Architecture**:
- **Lifecycle Concerns**: Extracted into self-contained classes implementing `DefaultLifecycleObserver` (e.g. `AnalyticsObserver`, `SessionTimeoutObserver`). Activities attach them via `lifecycle.addObserver(observer)`, allowing components to manage their own setup and teardown without overriding Activity lifecycle methods.
- **System & Permissions Concerns**: Handled via Jetpack `registerForActivityResult(ActivityResultContracts.RequestPermission())` hoisted into standalone delegates or Compose state holders.
- **Visual / UI Concerns**: Replaced by declarative Compose layout wrappers (e.g. `AppScaffold(showBackButton = true) { ... }`), keeping UI decorations purely functional.

Activities inherit strictly from standard Android `ComponentActivity` or `AppCompatActivity`, eliminating the custom base class entirely.

## Interview answer — deep senior

Under the hood, Android Jetpack was deliberately designed to render `BaseActivity` obsolete. Before Jetpack `LifecycleOwner`, activities were the only place that received `onStart()` or `onResume()`, forcing developers to dump cross-cutting logic into `BaseActivity.onResume()`. With `DefaultLifecycleObserver`, any plain Kotlin class can observe an Activity's lifecycle safely.

Furthermore, eliminating `BaseActivity` unlocks **Gradle modularization**. When every feature activity inherits from `BaseActivity` located in a common module, every feature module is circularly coupled to that base module's compilation classpath. By using composition, feature modules depend only on standard AndroidX APIs, drastically speeding up parallel compilation.

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
