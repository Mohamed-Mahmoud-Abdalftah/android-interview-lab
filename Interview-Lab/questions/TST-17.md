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

## Concept and technical explanation

Screenshot tests, Baseline Profiles, and Macrobenchmark tests represent three distinct advanced quality and performance disciplines in modern Android engineering. Screenshot testing (using frameworks such as Roborazzi, Paparazzi, or Shot) captures visual renderings of UI components or full screens and compares them pixel-by-pixel against versioned golden master images, detecting unintended visual regressions, typography clipping, and layout shifts. Baseline Profiles are human-readable ART compilation rules bundled into the APK that instruct Android's Ahead-Of-Time (AOT) and Profile-Guided Optimization (PGO) compiler to pre-compile critical execution paths—such as app startup, authentication, and core list scrolling—during app installation, slashing cold startup times by 30-40% and eliminating initial JIT compilation jank. Macrobenchmark tests execute black-box performance measurements on physical production-like devices without mocking, quantifying real-world frame timing, UI stutter, and cold, warm, or hot startup durations in release builds.

## Practical walkthrough (English)

Implementing screenshot tests, Baseline Profile generation, and Macrobenchmark measurements:
```kotlin
// 1. Screenshot testing a Compose component with Roborazzi
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class PaymentCardScreenshotTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun paymentCard_verifiedState_matchesGoldenImage() {
        composeTestRule.setContent {
            PaymentCard(
                accountNumber = "**** 4242",
                isVerified = true,
                status = CardStatus.ACTIVE
            )
        }

        // Captures screenshot and validates against golden image in source control
        composeTestRule.onRoot().captureRoboImage("golden_payment_card_verified.png")
    }
}

// 2. Baseline Profile generator for app startup and list scrolling
@RunWith(AndroidJUnit4::class)
class AppStartupBaselineProfileGenerator {
    @get:Rule
    val baselineRule = BaselineProfileRule()

    @Test
    fun generateAppStartupProfile() = baselineRule.collect(
        packageName = "com.example.banking",
        profileBlock = {
            // Cold start the application
            pressHome()
            startActivityAndWait()

            // Scroll the main transaction feed to capture JIT hotspots
            val feed = device.findObject(By.res("transaction_list"))
            feed.fling(Direction.DOWN)
            device.waitForIdle()
        }
    )
}

// 3. Macrobenchmark measuring cold startup timing with Baseline Profiles enforced
@RunWith(AndroidJUnit4::class)
class StartupMacrobenchmarkTest {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun measureColdStartupWithBaselineProfile() = benchmarkRule.measureRepeated(
        packageName = "com.example.banking",
        metrics = listOf(StartupTimingMetric(), FrameTimingMetric()),
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

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

We use screenshot tests to capture UI components and assert pixel-perfect parity against golden images, catching unintended visual shifts. Baseline Profiles generate ART compilation rules that pre-compile critical user flows during installation, eliminating JIT jank and boosting startup by up to 40%. Macrobenchmark tests run on physical devices in release mode to measure real black-box frame timing and cold startup latency, guaranteeing production performance.

## Interview answer — structured

Modern Android engineering relies on three specialized testing pillars to safeguard user experience, visual fidelity, and runtime performance.
Screenshot testing operates at the UI presentation layer.
Using tools like Roborazzi or Paparazzi, screenshot tests render composables in isolated JVM or instrumentation environments, comparing the resulting bitmap against reference golden files stored in git.
This catches regressions in font scaling, dark mode, RTL layouts, and unexpected padding adjustments that semantic assertions miss.
Baseline Profiles address Android's runtime compilation bottleneck.
Because Android's ART uses a hybrid of JIT and AOT compilation, unprofiled apps suffer from frame drops during initial user interactions while code interprets.
A Baseline Profile generator records which DEX methods and classes are executed during app launch and list scrolling, packaging these rules into the APK so the OS pre-compiles them upon installation.
Macrobenchmark tests provide rigorous empirical validation of this performance.
Running on physical devices with release minification enabled, Macrobenchmark repeatedly boots the application, measuring StartupTimingMetric and FrameTimingMetric under realistic thermal conditions.
Senior engineers combine these three disciplines to maintain flawless UI designs alongside peak runtime speed.

## Interview answer — deep senior

Under the hood, these three specialized testing tools interact directly with Android's OS rendering pipeline, Ahead-of-Time compilation architecture, and Linux kernel tracing subsystems.
Screenshot testing via Roborazzi leverages Robolectric's native graphics engine (Skia) to rasterize Compose draw commands directly into PNG byte arrays on the desktop host, eliminating physical emulator overhead while achieving 100% deterministic pixel-perfect validation across theme variations.
Baseline Profiles manipulate ART's Profile-Guided Optimization (PGO) pipeline.
When the generator executes, it instruments the ART runtime via adb commands, dumping raw profman profile files containing method indexes and class descriptors into an assets directory.
When Google Play delivers the APK, the device installer invokes dex2oat to pre-compile these profiled methods directly into native ELF binary machine instructions (OAT files), bypassing the JIT interpreter completely during the critical first cold launch.
Macrobenchmark operates via the Jetpack Benchmark library using Android OS Perfetto tracing and simpleperf profiler hooks under the hood.
To produce reliable metrics, it enforces strict device requirements: disabling CPU thermal throttling when possible, requiring a non-debuggable release build, and executing kill-and-restart cycles to flush Android OS page caches.
By comparing CompilationMode.None against CompilationMode.Partial(BaselineProfileMode.Require), engineering teams quantify the exact millisecond startup reduction and jank-free frame percentile directly in continuous integration reporting.

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
