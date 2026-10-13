---
id: "MEM-26"
question: "How would you create measurable performance budgets and regression tests?"
topic: "Memory Management, ANR & Performance"
code: "MEM"
group: "C"
phase: 1
priority: "P1"
order: 81
editorial_status: "reviewed"
---

# MEM-26

## Original interview question

How would you create measurable performance budgets and regression tests?

## What the interviewer evaluates

- Define user-journey metrics, device cohorts, conditions, and tail thresholds.
- Combine deterministic benchmarks with field monitoring and explicit correctness gates.
- Avoid flaky absolute thresholds on shared CI hardware or gaming the first-frame metric.

## Explanation in Arabic

كيفية إنشاء ميزانيات أداء قابلة للقياس (Performance Budgets) واختبارات منع التراجع (Regression Tests):

1. ما هي ميزانية الأداء (Performance Budget)؟
   - هي حدود رقمية صارمة متفق عليها هندسياً لا يُسمح لأي كود جديد بتجاوزها.
   - أمثلة على الميزانيات العملية في تطبيقات Android الاحترافية:
     * **Cold Startup**: أقل من 1.2 ثانية على جهاز مرجعي متوسط (Pixel 4a أو ما يوازيه).
     * **Frame Timing / Jank**: أقل من 2% من الفريمات تتجاوز 16ms أثناء سكرول القائمة الرئيسية.
     * **Memory Footprint**: ألا يتجاوز استهلاك الذاكرة الأساسي (Baseline PSS) 150MB.
     * **APK / AAB Size**: ألا تزيد حزمة التطبيق عن 25MB، مع حد أقصى للزيادة لكل PR لا يتعدى 200KB.

2. أتمتة اختبارات منع التراجع (Regression Testing in CI/CD):
   - استخدام **Jetpack Macrobenchmark**: تشغيل سيناريوهات القياس آلياً في CI على Physical Device Farm.
   - دمج فحص حجم الـ APK عبر **Diffuse** أو أداة تحليل الحزم: مقارنة الـ PR الحالي مع فرع `main`.
   - استخدام **LeakCanary in Instrumentation Tests**: تشغيل مسار المستخدم والتأكد من خلوه تماماً من أي تسريب ذاكرة قبل دمج الكود.

3. مراقبة الإنتاج وإغلاق الحلقة (Production Observability):
   - ربط مؤشرات Android Vitals و Firebase Performance بـ Alerting System (مثل PagerDuty / Slack).
   - تطبيق نظام الفحص المرحلي (Phased Rollouts): إيقاف طرح التحديث إذا تجاوز معدل الـ ANRs أو الـ Crashes العتبة المتفق عليها.

## Practical walkthrough

كتابة اختبار Macrobenchmark يفرض ميزانية أداء صارمة ويمنع التراجع في CI:
```kotlin
@RunWith(AndroidJUnit4::class)
class StartupPerformanceTest {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun coldStartupBudget_mustBeUnder1200ms() {
        benchmarkRule.measureRepeated(
            packageName = "com.example.app",
            metrics = listOf(StartupTimingMetric()),
            iterations = 5,
            startupMode = StartupMode.COLD
        ) {
            pressHome()
            startActivityAndWait()
        }
        // يتم جمع مقاييس زمن التشغيل ومقارنتها تلقائياً مع ميزانية الأداء في خط أنابيب CI
    }
}
```

## Why it matters and how it works

A budget turns “fast enough” into a repeatable product contract. Startup, rendering, memory, energy, and stability have different units and populations. Macrobenchmark runs app-level journeys and emits metrics/traces; unit or Microbenchmark tests isolate small algorithms. Field signals reveal devices and behavior the lab may miss. Compare distributions and tail values, not only a best run, and treat a regression as a hypothesis for investigation rather than automatically suppressing a failing threshold.

## Worked example

For a catalog app, set a documented budget for cold TTID and meaningful product-grid readiness on a mid-range physical device; set slow-frame percentile for a scripted 100-row scroll and a post-navigation retained-memory ceiling. Run controlled Macrobenchmark repetitions on a release-like build with fixed offline fixture data, archive traces, and compare against a baseline. An illustrative budget might alert on a material p95 regression rather than a 1 ms difference; actual thresholds must come from measured product baselines, not this example.

## Trade-offs and decision criteria

Strict fixed thresholds are easy to gate but can be flaky across thermals or CI machines; statistical comparison and dedicated devices reduce noise. A broad field percentile reflects users but changes with device mix, so segment cohorts. More metrics improve coverage but increase maintenance; prioritize critical journeys and explicit ownership. A test that warms caches may be valid for warm use but cannot substitute for cold-start coverage.

## Failure modes

An emulator test on a shared runner fails randomly due to host load. A team optimizes TTID by drawing a blank shell while TTFD regresses. A memory test compares snapshots before GC in one build and after GC in another. A budget omits low-RAM devices where OOMs occur. Tests should specify setup, cleanup, process state, compilation, dataset, and acceptable variance.

## Production perspective

Establish baseline distributions from controlled devices and Android vitals cohorts. Version the benchmark journeys with feature changes and archive trace artifacts for failures. Gate clear regressions, investigate ambiguous ones, and verify a fix in staged rollout by release and device tier. Pair performance budgets with correctness assertions for rendered data, auth, and navigation.

## Interview answer — short

To enforce performance budgets, I define explicit numeric thresholds for cold start (<1.2s), jank rate (<2%), memory baseline, and APK size. We automate regression tests in CI using Macrobenchmark on physical testbeds, compare binary deltas using tools like Diffuse, and enforce blocking PR checks alongside production Android Vitals alerts.

## Interview answer — structured

Establishing performance budgets transforms performance from an afterthought into a measurable engineering contract.

1. **Defining Explicit Numeric Budgets**: In an enterprise Android app, we define contracts around four core pillars:
   - **Startup Latency**: Cold start < 1,200ms, Warm start < 800ms on reference mid-tier hardware.
   - **Render Smoothness**: Frame drop rate < 2% and zero frozen frames (>700ms) during standard user flows.
   - **Memory Retained Size**: Process baseline PSS < 160MB, with 0 detected leaks.
   - **Binary Size**: Max APK download size of 30MB, with PR budget capped at +250KB.

2. **Automating CI Regression Testing**: We integrate **Jetpack Macrobenchmark** running on a dedicated physical device farm (or Firebase Test Lab). Macrobenchmark measures startup timing and frame duration over multiple iterations, generating JSON results that compare pull requests against the target branch.

3. **Gating & Tooling**: We use **Diffuse** in GitHub Actions to comment detailed DEX, resource, and asset size diffs on every PR. If a benchmark exceeds budget thresholds by >5%, the CI build fails automatically.

## Interview answer — deep senior

Under the hood, executing reliable performance tests in CI requires eliminating thermal and CPU throttling noise. Running Macrobenchmark requires a rooted physical test device configured with locked CPU clock frequencies (`adb shell stop; adb shell setprop ...`) to ensure stable run-to-run variance under 2%.

For memory regression testing, we utilize LeakCanary's instrumentation test runner (`LeakAssertions.assertNoLeaks()`). Running UI journeys via Espresso or UI Automator finishes with an automated leak check that dumps heap and fails the test if any destroyed Activity or View remains retained.

Finally, in production, we close the feedback loop using Firebase Performance Monitoring and Google Play Vitals API. If an incremental rollout in production breaches the ANR threshold (>0.47%) or cold launch SLA, an automated webhook halts the phased release in Google Play Console.

## How to answer in the interview

- **Why:** Choose user journeys and observable metrics.
- **How:** Fix device, build, data, and repetitions for comparisons.
- **Trade-off:** Strict thresholds catch regressions but can be noisy.
- **Failure case:** One run or emulator-only result can mislead.
- **Production solution:** Archive traces and use field cohorts to calibrate gates.

## Deep-dive talking points

Discuss journey selection, TTID/TTFD, frame tails, reproducibility, CI noise, correctness assertions, and field cohort comparison.

## Follow-up questions

- **Interviewer:** "How do you handle variance and flaky results in performance CI tests?"
  **Answer:** "We run Macrobenchmark tests for 5-10 iterations, take the median (50th percentile) and 95th percentile metrics, lock CPU clocks on dedicated physical test devices, and allow a minor margin of tolerance (e.g. ±3%) before failing the build."

- **Interviewer:** "What is the tool Diffuse and how does it prevent app bloat?"
  **Answer:** "Diffuse is an open-source APK/AAB diffing tool by Jake Wharton that breaks down byte changes across DEX code, resources, assets, and compression, giving PR reviewers an exact view of what contributed to size increases."

## Self-check rubric

Specify a journey and metric, control the environment, handle variance, retain correctness gates, and verify field impact.

## References and reviewed-on date

- [Macrobenchmark overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — full-journey tests and traces.
- [Measure app performance](https://developer.android.com/topic/performance/measuring-performance) — metric selection and tracing.
- [Android vitals](https://developer.android.com/games/optimize/vitals) — field quality signals.

Technically reviewed against primary documentation on 2026-10-13.
