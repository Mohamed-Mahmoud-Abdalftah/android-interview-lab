---
id: "MEM-19"
question: "What are cold start, warm start, and hot start?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "B"
phase: 1
priority: "P1"
order: 74
editorial_status: "reviewed"
---

# MEM-19

## Original interview question

What are cold start, warm start, and hot start?

## What the interviewer evaluates

- Distinguish process and Activity state at launch, with correct examples.
- Separate time to initial display from fully usable content.
- Benchmark each mode consistently and preserve correct state restoration.

## Concept and technical explanation

Android defines three distinct application launch states characterized by system process availability, Activity back stack residency, and initialization cost. A Cold Start occurs when the application process does not exist in Linux memory (for example, on first launch after device reboot, after the user force-stops the app, or after the OS kills the process due to memory pressure). In a cold start, the OS must fork a new process from Zygote, initialize the Android Runtime, load DEX bytecodes, invoke ContentProviders declared in the manifest, instantiate the Application class and execute `Application.onCreate()`, instantiate the entry Activity, inflate the view hierarchy or invoke initial Composable functions, perform measure and layout passes, and draw the initial frame to the screen. A Warm Start occurs when the application process is already resident in memory, but the target Activity must be re-created from scratch (such as when the system killed the Activity to reclaim memory while the user was in another app, or when the user navigates back to the app with a recreation intent). Warm starts bypass Zygote process creation and `Application.onCreate()`, but still incur Activity creation, dependency injection, and UI inflation overhead. A Hot Start occurs when both the application process and the Activity instance are already resident in memory and the activity is simply brought to the foreground from the back stack. The system only needs to invoke `onRestart()`, `onStart()`, and `onResume()`, rendering the existing view tree with zero inflation or process initialization latency.

## Practical walkthrough (English)

Measuring real startup readiness using `reportFullyDrawn()`:
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                if (state is UiState.Success) {
                    renderData(state.data)
                    // Signals to the OS and Play Vitals that all critical asynchronous content is rendered:
                    // This completes the Time to Full Display (TTFD) benchmark:
                    reportFullyDrawn()
                }
            }
        }
    }
}
```
In this implementation, the system logs two critical launch milestones in Logcat: the initial frame display (`Displayed com.example.app/.MainActivity: +450ms`, representing Time to Initial Display or TTID) and the full data render (`Fully drawn com.example.app/.MainActivity: +920ms`, representing Time to Full Display or TTFD). Calling `reportFullyDrawn()` ensures that automated Macrobenchmark suites and Google Play Console Android Vitals record true usable startup performance rather than measuring an empty loading skeleton.

## Explanation in Arabic

الفرق بين أنواع بدء تشغيل التطبيق: التشغيل البارد (Cold Start)، والدافئ (Warm Start)، والساخن (Hot Start):

1. التشغيل البارد (Cold Start):
   - **الحالة**: عملية التطبيق (App Process) غير موجودة في الذاكرة نهائياً (إما بعد إعادة تشغيل الهاتف، أو بعد إنهاء العملية بواسطة المستخدم أو النظام).
   - **ما يحدث داخلياً**: النظام يقوم بإنشاء العملية من البداية عبر `Zygote.fork()`، وتحميل كلاسات التطبيق (ClassLoading)، وإنشاء كائن `Application` وتنفيذ `onCreate()`، ثم إنشاء الـ `Activity` وتنفيذ `onCreate() -> onStart() -> onResume()`، ثم قياس ورسم الشاشة الأولى.
   - **الوقت المتوقع**: هو الأطول دائماً (عادة بين 1 إلى 3 ثوانٍ).

2. التشغيل الدافئ (Warm Start):
   - **الحالة**: عملية التطبيق (Process) لا تزال موجودة في الذاكرة، لكن الـ Activity دُمرت وتجب إعادة إنشائها.
   - **أمثلة**: المستخدم غادر التطبيق وضغط على زر الرجوع (Back)، أو قتلت الـ Activity بسبب تغيير اتجاه الشاشة (Configuration Change) أو نقص ذاكرة النشاط.
   - **ما يحدث**: يتخطى النظام إنشاء الـ Process وكائن الـ Application، ويبدأ مباشرة من إنشاء الـ Activity واستعادة حالتها (`savedInstanceState`).

3. التشغيل الساخن (Hot Start):
   - **الحالة**: عملية التطبيق والنشاط لا يزالان موجودين بالكامل في الذاكرة ولم يتم تدميرهما.
   - **أمثلة**: المستخدم ضغط على زر Home ثم فتح التطبيق مجدداً بعد ثوانٍ.
   - **ما يحدث**: يجلب النظام النشاط من الخلفية إلى المقدمة مباشرة، مستدعياً `onRestart() -> onStart() -> onResume()` دون أي إعادة إنشاء للـ Views أو الـ Application، وهو الأسرع على الإطلاق (أقل من بضع مئات من المللي ثانية).

## Practical walkthrough

استدعاء `reportFullyDrawn()` لقياس اكتمال التحميل الحقيقي للواجهة (Time to Full Display):
```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                if (state is UiState.Success) {
                    renderData(state.data)
                    // إبلاغ النظام بأن التطبيق جاهز ومحمل بالكامل بالبيانات:
                    // هذا يُسجل في Logcat ويُحسب في Android Vitals و Macrobenchmark بدقة:
                    reportFullyDrawn()
                }
            }
        }
    }
}
```

## Why it matters and how it works

Cold launch includes process creation, application initialization, Activity creation, inflation/composition, and first draw. Warm launch avoids process start but still creates an Activity. Hot launch resumes an existing Activity/process, though callbacks and redraw work remain. System and benchmark definitions focus on starting state, so document test setup. Correctness includes restoring route and session after cold launch rather than only minimizing the first-frame metric.

## Worked example

Benchmark an order app with three conditions: force-stop/kill process then launch for cold; keep process but remove Activity for warm; leave Activity stopped then return for hot. Record time to initial display and to meaningful order content, with identical cache and network conditions. Move nonessential analytics initialization out of the first-frame path while preserving authentication and route restoration. This is a proposed experiment, not a measured outcome.

## Trade-offs and decision criteria

Deferring work can improve initial display but may delay first interaction or hide errors, so measure fully drawn/interactive state as well. Aggressive caching speeds warm paths but increases memory and staleness. Baseline Profiles can help code execution on cold paths, but not a slow server. A splash screen must not conceal a broken restoration flow.

## Failure modes

A benchmark accidentally reuses process and calls the result cold. A startup optimization removes essential session validation and briefly exposes private UI. A fast blank frame improves TTID while TTFD worsens. Blocking ContentProvider or Application initialization still delays cold start even after Activity code is optimized. Examine trace and startup mode explicitly.

## Production perspective

Track startup metrics by mode, device tier, release, and entry source. Use Macrobenchmark with controlled `StartupMode` and production-sized state, and trace provider/Application/Activity work. Define separate budgets for first frame and usable content. After improvements, verify notification/deep-link cold entry and process-death restoration still work.

## Interview answer — short

A Cold Start creates a new Linux process from Zygote, executing Application and Activity initialization from scratch. A Warm Start reuses an existing app process but must recreate the Activity and inflate its UI. A Hot Start brings an existing, resident Activity from the background back to the foreground, requiring only lifecycle resumption callbacks.

## Interview answer — structured

Understanding Android launch states is essential for diagnosing startup latency and setting realistic performance budgets.

A Cold Start is the most expensive state because no process exists in memory. The operating system must fork a new process from Zygote, initialize the Android Runtime, execute ContentProviders, run `Application.onCreate()`, instantiate the launch Activity, inflate the view tree, and render the first frame.

In production, a Warm Start represents a partial launch lifecycle. The Linux process and Application singleton are already resident in memory, but the target Activity was destroyed and must be recreated. While this bypasses process initialization, it still incurs Activity creation, dependency injection, and layout inflation latency.

A Hot Start is the fastest launch condition because both the process and the Activity instance remain intact in memory. The system simply brings the Activity window to the foreground, invoking `onStart()` and `onResume()`.
Optimizing startup requires separating Time to Initial Display from Time to Full Display by deferring non-essential initialization and calling `reportFullyDrawn()` once interactive data is rendered.


## Interview answer — deep senior

At the Linux kernel and platform runtime layer, a Cold Start initiates with an IPC Binder transaction to `ActivityManagerService` (or `ActivityTaskManagerService` in modern Android). AMS communicates with the Zygote daemon via a local Unix domain socket, requesting a fork of the zygote process. Because Zygote has pre-loaded core framework classes and pre-warmed graphics assets, the forked process inherits clean memory pages via copy-on-write (COW). Once forked, the process initializes the `ActivityThread`, creates the Main Looper, and invokes `LoadedApk.makeApplication()`.
Crucially, all ContentProviders declared in the AndroidManifest are initialized sequentially on the Main Thread prior to `Application.onCreate()`. In modern modularized codebases, third-party SDKs frequently exploit empty ContentProviders for zero-code auto-initialization, severely degrading cold start times before a single line of app code executes. This makes the Jetpack App Startup library vital for coalescing multiple initializers into a single component.
Measuring cold launch latency requires distinguishing between TTID and TTFD. Time to Initial Display represents the duration from process launch until SurfaceFlinger presents the very first frame (often a placeholder, theme window background, or skeleton screen). Time to Full Display, triggered by `Activity.reportFullyDrawn()`, measures when asynchronous data fetching and UI population conclude, giving the user an interactive surface. Android Vitals enforces a bad behavior threshold of 5 seconds for cold start and 2 seconds for warm start.
Senior staff engineers audit cold starts using Perfetto System Traces and Macrobenchmark with `StartupMode.COLD`. In the trace, we inspect thread slices between `bindApplication` and the first `Choreographer.doFrame`. Any class loading spikes, synchronized disk reads, or Dagger/Hilt dependency graph instantiations during this window are prioritized for lazy initialization or background coroutine dispatch.

## How to answer in the interview

- **Why:** Define process and Activity state for each launch mode.
- **How:** Measure TTID and meaningful TTFD separately.
- **Trade-off:** Deferral can improve first paint while delaying useful content.
- **Failure case:** Comparing cold with hot creates a false win.
- **Production solution:** Control launch conditions and trace the actual critical path.

## Deep-dive talking points

Discuss process/Activity state, TTID versus TTFD, startup setup, Application/provider work, and restoration correctness.

## Follow-up questions

- **Interviewer:** "Why is synchronous SDK initialization in a ContentProvider bad for Cold Start?"
  **Answer:** "All `ContentProvider.onCreate()` methods are executed synchronously on the main thread before `Application.onCreate()`. If multiple third-party SDKs install automatic ContentProviders doing heavy work, cold startup stalls before user code even executes."

- **Interviewer:** "How does Splash Screen API (Android 12+) interact with Cold Start?"
  **Answer:** "The SplashScreen API displays a system-controlled window background icon immediately upon process fork, masking the latency of class loading and `Application.onCreate()` until the app draws its first frame."

## Self-check rubric

Define three modes, distinguish TTID and TTFD, configure a fair comparison, and protect cold-entry correctness.

## References and reviewed-on date

- [App startup time](https://developer.android.com/topic/performance/issues/launch-time) — cold/warm/hot definitions.
- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — StartupMode measurement.

Technically reviewed against primary documentation on 2026-10-13.
