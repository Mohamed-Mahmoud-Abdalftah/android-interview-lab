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

Cold Start starts from scratch: the OS forks the process from Zygote, initializes the Application object, and creates the Activity. Warm Start reuses an existing process but recreates the destroyed Activity. Hot Start simply brings an existing in-memory Activity and process to the foreground via `onRestart()` and `onResume()`, making it instantaneous.

## Interview answer — structured

The distinction between startup types hinges on whether the application process and Activity instance already reside in RAM.

First, a Cold Start is the process does not exist. The OS must fork a new process from Zygote, allocate memory, initialize runtime classes, instantiate the `Application` class, run `Application.onCreate()`, instantiate the launch `Activity`, inflate the layout, and complete the initial draw pass. It is the most expensive launch state and must be optimized aggressively. Next, a Warm Start is the application process is still resident in RAM, but the Activity was destroyed (for instance, via back navigation or memory trimming). The system skips process and Application creation, jumping directly into Activity recreation and state restoration (`savedInstanceState`).
Finally, with Hot Start, both the application process and Activity remain fully initialized in memory (e.g. The user pressed Home and immediately returned). The OS merely brings the Activity to the foreground, invoking `onRestart()`, `onStart()`, and `onResume()` without recreating views, making it virtually instantaneous.

In production, Google Play Vitals monitors Cold Starts targeting under **5 seconds** (ideally <1.5s), Warm starts under **2 seconds**, and Hot starts under **1.5 seconds**.


## Interview answer — deep senior

Under the hood, optimizing Cold Start requires minimizing work done in `Application.onCreate()`. Third-party SDK initializations (analytics, crash reporting, ads, feature flags) should not run synchronously on the main thread during startup. Using Jetpack **App Startup** allows libraries to share a single `ContentProvider` and define explicit dependency graphs, enabling asynchronous or on-demand initialization.

Another critical milestone is the difference between **Time to Initial Display (TTID)** and **Time to Full Display (TTFD)**. TTID is the timestamp when the first visual frame is drawn (often a skeleton or splash screen). TTFD occurs when the screen has finished populating asynchronous data, marked explicitly by calling `activity.reportFullyDrawn()`. Android Vitals and Macrobenchmark use `reportFullyDrawn()` as the true golden metric for cold start quality.


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
