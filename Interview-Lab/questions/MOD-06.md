---
id: "MOD-06"
question: "What are Dynamic Feature Modules / Play Feature Delivery?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "A"
phase: 4
priority: "P1"
order: 359
editorial_status: "reviewed"
---

# MOD-06

## Original interview question

What are Dynamic Feature Modules / Play Feature Delivery?

## What the interviewer evaluates

- Explain install-time versus on-demand feature delivery through App Bundles.
- Address download failure, offline need and runtime entry points.
- Distinguish dynamic delivery from ordinary modularization.

## Explanation in Arabic

ما هي موديولات الميزات الديناميكية (Dynamic Feature Modules - DFMs) و Play Feature Delivery في Android؟

1. المفهوم والهدف الأساسي:
   - في الوضع الطبيعي، يتم تنزيل التطبيق ككتلة واحدة بجميع شاشاته وميزاته عند تثبيته من Google Play.
   - **Dynamic Feature Modules (DFMs)**: تتيح تجزئة التطبيق إلى أجزاء منفصلة يتم تنزيلها عند الطلب (On-Demand Delivery) أو تنزيلها بشروط معينة (Conditional Delivery بناءً على الدولة أو العتاد).
   - **أمثلة واقعية**: ميزة الواقع المعزز (AR Mode) في تطبيق تجارة إلكترونية، أو ميزة مسح المستندات بـ OCR، أو ميزة دعم العملاء عبر الفيديو.

2. أنواع تسليم الميزات في Play Feature Delivery:
   - **Install-time**: يتم تنزيله تلقائياً مع التطبيق الأساسي ولكنه مقسم في APK Split مستقل.
   - **On-demand**: لا يُنزل مع التطبيق! عند ضغط المستخدم على زر 'تجربة الواقع المعزز'، يقوم التطبيق بطلب التنزيل من Google Play عبر `SplitInstallManager` وعرض شريط تقدم للمستخدم.
   - **Conditional**: يتم تنزيله فقط للأجهزة التي تدعم إمكانيات عتادية محددة (مثل توافر مستشعر معين أو في بلدان محددة).

3. التحديات والمخاطر الهندسية:
   - **انعكاس التبعية (Inverted Dependency)**: الـ DFM يعتمد على `:app`، بينما `:app` لا يعتمد عليه، مما يعقد الـ DI والـ Navigation.
   - **فشل التنزيل في وضع عدم الاتصال (Offline & Network Failures)**: ماذا لو انقطع النت أثناء تنزيل الميزة؟ يجب تصميم تجربة مستخدم تعالج الفشل وإعادة المحاولة بأمان.

## Practical walkthrough

كيفية طلب تنزيل ميزة ديناميكية عند الطلب باستخدام SplitInstallManager:
```kotlin
class DynamicFeatureLauncher(private val context: Context) {
    private val splitInstallManager = SplitInstallManagerFactory.create(context)

    fun launchAugmentedRealityFeature(onReady: () -> Unit, onError: (String) -> Unit) {
        val moduleName = "feature_augmented_reality"

        // 1. التحقق مما إذا كانت الميزة مثبتة مسبقاً:
        if (splitInstallManager.installedModules.contains(moduleName)) {
            onReady()
            return
        }

        // 2. طلب التنزيل من Google Play عند الطلب (On-Demand Request):
        val request = SplitInstallRequest.newBuilder()
            .addModule(moduleName)
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { sessionId ->
                // الاستماع لحالة التنزيل والتثبيت عبر SplitInstallStateUpdatedListener
            }
            .addOnFailureListener { exception ->
                onError(exception.localizedMessage ?: "Download failed")
            }
    }
}
```

## Why it matters and how it works

An App Bundle lets Play generate device-targeted APKs and deliver configured feature splits. On-demand installation requires an asynchronous request before code/resources are available. The feature depends on the base app, which affects graph visibility and Hilt integration. Delivery rules and Play environment shape actual availability, so local sideload behavior is insufficient proof.

## Worked example

A rarely used document-scanning feature is on demand. The app shows the scan entry point, requests installation on tap, presents progress and retry, and opens the scan route only after success. If the user is offline and has not installed it, the app offers a fallback explanation; essential receipt viewing stays installed locally.

## Trade-offs and decision criteria

Initial download size may shrink, but entry latency and failure states increase. Install-time delivery retains availability yet may not lower initial bytes. Dynamic features complicate testing, DI, navigation, localization/resource management and analytics. Use them when measured size/usage benefit outweighs operational cost.

## Failure modes

Navigation references a class before installation. An offline user cannot reach a required workflow. A feature relies on app Hilt aggregation unsupported by its compile direction. QA tests only debug builds where the module is always present. Installation cancellation leaves a spinner forever.

## Production perspective

Measure feature usage, package size and install success/latency. Test Play delivery modes, offline/cancel/retry, process recreation during install, and correct routing after updates. Include feature-install telemetry without logging sensitive data.

## Interview answer — short

Dynamic Feature Modules enable modular delivery via Android App Bundles, downloading non-critical features on-demand after initial app install. They reduce initial APK download size, support conditional delivery by country or hardware, but introduce inverted dependencies, runtime download failure handling, and classloader complexity.

## Interview answer — structured

Dynamic Feature Modules (DFMs) leverage Google Play Feature Delivery to modularize app distribution rather than just code compilation.

Key mechanisms:
1. **Delivery Modes**: Modules can be configured as **Install-time** (packaged as separate splits), **On-demand** (downloaded in the background only when the user triggers that specific flow), or **Conditional** (installed based on user country, minimum SDK, or hardware device features like camera sensors).
2. **Initial Download Reduction**: Heavy, infrequently used features—such as KYC facial scanning, AR viewers, or complex PDF report generators—are removed from the base APK, significantly boosting Play Store install conversion rates by reducing initial download size.

However, DFMs introduce serious engineering complexity: Gradle dependencies are inverted (`:dfm` depends on `:app`), feature access requires asynchronous download UI states via `SplitInstallManager`, and features cannot be accessed offline if they haven't been downloaded yet.

## Interview answer — deep senior

Under the hood, dynamic delivery relies on **Android APK Splits and SplitCompat**.

When Google Play installs a base APK on Android 5.0+ (API 21+), the OS mounts additional split APKs directly into the application process. However, when a split is installed dynamically while the app process is **already running**, Android cannot automatically update the running app's classloader and asset path. Developers must call `SplitCompat.installActivity(context)` inside the Activity's `attachBaseContext()` to merge the newly downloaded split's Dex files and native `.so` libraries into the live ClassLoader.

Furthermore, navigation to DFMs cannot use direct Kotlin class references (`Intent(this, DfmActivity::class.java)`), because `:app` does not have compile-time visibility of `:dfm`. Instead, you must navigate via explicit class reflection, string deep links, or Android Jetpack Navigation dynamic feature artifacts.

## How to answer in the interview

- **Why:** delivery boundary differs from source boundary.
- **How:** choose install-time/on-demand by usage.
- **Trade-off:** smaller initial install versus runtime dependency.
- **Failure case:** offline user cannot open critical feature.
- **Production solution:** test delivery and fallback.

## Deep-dive talking points

Discuss bundle splits, delivery modes, install state machine, offline requirements, DI bridge and telemetry.

## Follow-up questions

- **Interviewer:** "What happens if a user is offline when attempting to open an on-demand dynamic feature?"
  **Answer:** "The installation request will fail immediately; the UI must gracefully display an offline warning and prevent the flow from crashing."

- **Interviewer:** "Can Dynamic Feature Modules contain native C/C++ libraries?"
  **Answer:** "Yes, native `.so` libraries in DFMs are packaged inside the split APK and dynamically linked when SplitCompat installs the module."

## Self-check rubric

Choose a candidate feature, justify delivery, model install failure, and name integration tests.

## References and reviewed-on date

- [Play Feature Delivery overview](https://developer.android.com/guide/playcore/feature-delivery) — delivery modes.
- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — dynamic feature caveat.

Technically reviewed against primary documentation on 2026-10-13.
