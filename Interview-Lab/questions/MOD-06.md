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

## Concept and technical explanation

Dynamic Feature Modules (DFMs) and Google Play Feature Delivery allow Android applications to separate features into isolated modules that can be downloaded conditionally, deferred in the background, or retrieved on demand at runtime via the Google Play Core library (SplitInstallManager). Unlike standard library modules where the base application module depends on the feature, DFMs invert the Gradle dependency direction: the dynamic feature module declares a dependency on the base :app module (via implementation(project(":app"))), while the :app module declares dynamicFeatures = [":feature:ondemand"]. This structural inversion means the base APK cannot directly reference dynamic feature classes at compile time. Cross-boundary navigation requires reflection, dynamic service locator registries, or deep link URIs. DFMs reduce the initial app download size dramatically, but introduce operational complexity: network latency during downloads, offline error handling, and Play Core testing requirements.

## Practical walkthrough (English)

Configuring dynamic delivery and loading a feature on-demand using SplitInstallManager:
```kotlin
// feature/scanner/build.gradle.kts
plugins {
    alias(libs.plugins.android.dynamic.feature)
}
dependencies {
    implementation(project(":app"))
}

// Requesting on-demand download at runtime in the base app:
fun downloadAndLaunchScanner(context: Context) {
    val splitInstallManager = SplitInstallManagerFactory.create(context)
    val request = SplitInstallRequest.newBuilder()
        .addModule("scanner")
        .build()

    splitInstallManager.startInstall(request)
        .addOnSuccessListener { sessionId ->
            // Module downloaded! Launch via explicit component reflection or deep link
            val intent = Intent().setClassName(context, "com.example.scanner.ScannerActivity")
            context.startActivity(intent)
        }
        .addOnFailureListener { exception ->
            // Handle network failure, insufficient disk space, or offline state
        }
}
```

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

Dynamic Feature Modules enable Play Feature Delivery, allowing apps to download features on-demand, conditionally by device spec, or deferred in the background. They invert the standard Gradle dependency direction because the dynamic module depends on the app module. This slashes initial install size but requires handling runtime network download latency, offline failures, and reflection-based navigation.

## Interview answer — structured

Dynamic Feature Modules provide an advanced packaging mechanism through Google Play Feature Delivery to optimize application install size.
Standard Android modules are compiled directly into the base APK, forcing all users to download every feature upon initial install.
With dynamic features, secondary or specialized capabilities like augmented reality viewers, heavy document scanners, or onboarding wizards are isolated into separate delivery units.
These units can be downloaded on-demand when the user opens the feature, conditionally based on device hardware like camera features or country, or deferred silently in the background.
Architecturally, dynamic modules invert the Gradle dependency graph: the dynamic feature module depends on the base app module, while the base app specifies the dynamic module in its build configuration.
Because the base app cannot see dynamic classes at compile time, navigation must be decoupled through deep links, reflection, or dynamic dependency injection.
Teams must build robust UI states to handle download progress, network disconnections, and storage errors.

## Interview answer — deep senior

From an engineering and product perspective, Dynamic Feature Modules represent a trade-off between initial user acquisition conversion rates and runtime operational complexity.
Google Play data shows that for every six megabytes added to initial APK download size, install conversion rates drop by roughly one percent.
By offloading niche or heavy features into dynamic modules, we keep our initial download size well below cellular network warning thresholds.
However, the architectural cost of dynamic delivery is profound due to Gradle dependency inversion.
In conventional builds, :app imports features.
In dynamic delivery, the dynamic module applies com.android.dynamic-feature and imports :app as an implementation dependency, while :app lists the module inside dynamicFeatures.
This inversion breaks direct compile-time code references from the base APK.
To open a dynamic feature screen, we cannot invoke a standard Intent referencing the Activity class literal.
We must either navigate via deep link URIs, register interface providers in a dynamic service registry upon split loading, or invoke classes reflectively after SplitInstallManager signals successful installation.
Furthermore, dynamic features require SplitCompat.install(context) initialization in Application and Activity contexts to resolve resources correctly.
Production engineering demands designing comprehensive fallback user flows: displaying progress indicators during download, handling network failures gracefully without stranding the user, and mocking SplitInstallManager during local automated testing using FakeSplitInstallManager.

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
