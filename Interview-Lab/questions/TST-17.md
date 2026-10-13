---
id: "TST-17"
question: "What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "B"
phase: 4
priority: "P1"
order: 412
editorial_status: "reviewed"
---

# TST-17

## Original interview question

What are screenshot tests, Baseline Profiles, and Macrobenchmark tests?

## What the interviewer evaluates

- Purpose and limitations of screenshots, Baseline Profiles and Macrobenchmark.
- Correct production-like performance setup.

## Explanation in Arabic

ما هي اختبارات لقطات الشاشة (Screenshot Tests)، والـ Baseline Profiles، واختبارات الـ Macrobenchmark في معايير الجودة الحديثة؟

1. اختبارات لقطات الشاشة (Screenshot / Visual Regression Tests):
   - **فكرتها**: التقاط صورة بكسل-ببكسل (PNG) لكل مكون Composable أو شاشة، ومقارنتها بصورة معتمدة سابقة (Golden Image).
   - **الميزة**: تكشف أي تشوه بصري غير مقصود (مثل تداخل النصوص، اختفاء مسافات الـ Padding، أو أخطاء في الـ Dark Mode وتكبير الخطوط).
   - **المكتبات الرائدة**: **Roborazzi** (تعمل بسرعة فائقة على الـ JVM المحلي عبر Robolectric)، و **Paparazzi**، و **Shot**.

2. ما هي الـ Baseline Profiles؟
   - ملفات قواعد يتم توليدها آلياً تحدد الكلاسات والدوال الأكثر استخداماً في مسارات فتح التطبيق الحرجة (Critical User Journeys).
   - يقوم نظام Android OS عند تثبيت التطبيق بتجميع هذه الدوال مسبقاً (Ahead-Of-Time - AOT)، مما **يسرع زمن فتح التطبيق (Cold Start) بنسبة تصل إلى 40% ويقضي على الـ Jank** في أول تجربة للمستخدم!

3. اختبارات الـ Macrobenchmark:
   - اختبارات رسمية تعمل على أجهزة حقيقية لقياس أداء التطبيق الفعلي ككل: قياس زمن الفتح (`StartupTimingMetric`) ومعدل سلاسة الإطارات أثناء التمرير (`FrameTimingMetric`).

## Practical walkthrough

تنفيذ اختبار Screenshot باستخدام Roborazzi واختبار Macrobenchmark لقياس سرعة التشغيل:
```kotlin
// 1. اختبار Screenshot حديث باستخدام Roborazzi و Compose على الـ JVM المحلي:
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class PaymentCardScreenshotTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun paymentCard_rendersAccurately_inDarkAndLightMode() {
        composeRule.setContent {
            AppTheme(darkTheme = true) {
                PaymentCard(cardNumber = "**** 4321", balance = "$1,250.00")
            }
        }

        // التقاط لقطة الشاشة ومقارنتها تلقائياً بالصورة المرجعية المخزنة:
        composeRule.onRoot().captureRoboImage("screenshots/payment_card_dark.png")
    }
}

// 2. اختبار Macrobenchmark لقياس زمن الـ Cold Start على جهاز حقيقي:
@RunWith(AndroidJUnit4::class)
class ColdStartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun measureColdStartup() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

## Why it matters and how it works

Baseline Profiles are generated from representative interactions and shipped with the app/library for ahead-of-time optimization. Macrobenchmark runs outside the target app process and requires appropriate benchmarkable build configuration. Screenshot goldens depend on device/font/theme and need controlled environment.

## Worked example

For a product list, capture screenshot goldens at light/dark and RTL; generate profile for cold launch plus first scroll; benchmark startup and frame timing on a representative low-end device across repeated iterations. Compare with a baseline and inspect allocation traces before optimizing.

## Trade-offs and decision criteria

Profiles can improve startup at install/runtime but add maintenance when navigation changes. Macrobenchmarks are slower and noisy; use stable hardware and repeated measurements. Screenshot tests catch appearance but not semantics or functional correctness.

## Failure modes

A team updates a Baseline Profile and claims success without measuring startup. Run Macrobenchmark before/after. A screenshot test fails because font rendering changed on CI; pin the rendering environment and review intentional changes.

## Production perspective

Use release-like benchmark variants, controlled thermal/battery state and representative devices. Gate large regressions with statistical tolerance, not a single noisy measurement.

## Interview answer — short

Screenshot tests capture and pixel-diff rendered UI against baseline golden images to catch visual regressions. Baseline Profiles pre-compile critical execution paths at install time via AOT compilation to eliminate launch jank. Macrobenchmark tests measure real-world startup latency and scroll frame metrics on physical devices.

## Interview answer — structured

Modern Android reliability and performance testing relies on three specialized verification technologies:

1. **Screenshot / Visual Regression Tests (Roborazzi / Paparazzi)**:
   - Render Composables off-screen and compare output PNGs pixel-by-pixel against committed golden reference images. They catch unintended regressions in theme inheritance, text truncation across dynamic font scales, and RTL mirror alignments in seconds on the JVM.

2. **Baseline Profiles**:
   - Human-readable specifications of classes and methods compiled during app installation using Android Runtime (ART) Ahead-Of-Time (AOT) compilation. By pre-compiling critical user paths (app startup, feed scrolling), Baseline Profiles eliminate runtime JIT interpretation pauses, improving cold launch speed by 30–40%.

3. **Macrobenchmark Testing**:
   - Black-box performance testing running against non-debuggable release builds on physical hardware. Uses Android OS trace instrumentation to measure `StartupTimingMetric` (Time to Initial Display) and `FrameTimingMetric` (measuring 90th/99th percentile frame drops during fast scrolling lists).

## Interview answer — deep senior

From an engineering platform and release infrastructure perspective, incorporating these tools requires dedicated pipeline stages:

1. **CI Screenshot Differential Reporting**: When a visual regression occurs, CI should not merely fail the build. Integrate tools (like GitHub Action artifact reports) that generate an HTML visual diff carousel showing the original Golden, the Candidate, and an overlay diff highlighting mismatched pixels in red.

2. **Baseline Profile Automation**: Configure AGP's Baseline Profile Gradle plugin (`androidx.baselineprofile`). Schedule automated monthly Macrobenchmark profiling runs in CI that traverse critical user journeys, generate fresh `baseline-prof.txt` rules, and commit them directly to the repository before major releases.

3. **Device Requirements for Benchmarks**: Never run Macrobenchmark on standard emulators or debug builds. ART compiles debuggable builds with optimizations disabled, skewing measurements. Always execute benchmarks on real, rooted or userdebug physical devices pinned at stable thermal CPU frequencies.

## How to answer in the interview

- **Why:** visual, compilation and runtime performance regressions need different evidence.
- **How:** map screenshot, Baseline Profile and Macrobenchmark to one scrolling screen.
- **Trade-off:** richer performance measurement costs devices and repeated runs.
- **Failure case:** one emulator timing number is treated as universal.
- **Production solution:** controlled release-like benchmark plus correctness checks.

## Deep-dive talking points

Prompt for three tool purposes, release-like benchmark, representative profile path and measurement uncertainty.

## Follow-up questions

- **Interviewer:** "Why is Roborazzi faster than traditional on-device screenshot testing?"
  **Answer:** "Roborazzi runs on the host JVM using Robolectric's native graphics engine, generating and comparing screenshots in seconds without booting an Android emulator."

- **Interviewer:** "What is the difference between Time to Initial Display and Time to Full Display in Macrobenchmark?"
  **Answer:** "Initial Display measures when the first frame renders; Full Display measures when asynchronous network data completes and reportFullyDrawn() is called."

## Self-check rubric

Choose a screenshot golden for layout, a Baseline Profile for hot-path compilation, and Macrobenchmark for startup/frame measurement. Define device, build variant, metric and baseline before claiming an improvement.

## References and reviewed-on date

- [Android Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) — profile purpose.
- [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) — measurement guidance.

Technically reviewed against primary documentation on 2026-10-13.
