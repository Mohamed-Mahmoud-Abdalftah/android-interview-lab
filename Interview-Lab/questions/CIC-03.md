---
id: "CIC-03"
question: "What are build artifacts and release tracks?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "A"
phase: 4
priority: "P2"
order: 422
editorial_status: "reviewed"
---

# CIC-03

## Original interview question

What are build artifacts and release tracks?

## What the interviewer evaluates

- APK/AAB, mappings, test reports and provenance.
- Internal/closed/open/production tracks and artifact promotion.

## Explanation in Arabic

ما هي مخرجات البناء (Build Artifacts) ومسارات الإطلاق (Release Tracks) في تطوير تطبيقات أندرويد؟

1. مخرجات البناء (Build Artifacts):
   - **Android App Bundle (AAB)**: حزمة النشر الرسمية لـ Google Play. لا تُثبت مباشرة على الأجهزة، بل يقوم متجر جوجل بتقسيمها عبر Dynamic Delivery لتوليد Split APKs خاصة بكل جهاز بناءً على شاشته ومعالجه ولغته، مما يوفر 20–30% من الحجم.
   - **APK (Universal / Split)**: حزمة التطبيق القابلة للتثبيت المباشر (`.apk`). تُستخدم للاختبارات الداخلية وسيرفرات الـ QA و Firebase App Distribution.
   - **ملف الخرائط (mapping.txt)**: ينتجه R8/ProGuard أثناء عمل Shrinking & Obfuscation. ضروري جداً لفك تشفير الـ Stacktraces المبهمة (De-obfuscation) في Firebase Crashlytics.
   - **ملفات الـ Baseline Profiles (`baseline.prof`)**: مخرجات يتم تضمينها داخل التطبيق لتوجيه نظام ART لترجمة الكود الهام إلى لغة الآلة مسبقاً (AOT) لتسريع وقت التشغيل بنسبة تصل لـ 30%.

2. مسارات الإطلاق (Release Tracks) على Google Play Console:
   - **Internal Testing**: حتى 100 مختبر داخلي. الإطلاق فوري (بدون مراجعة متجر تقريباً، بضع دقائق).
   - **Closed Testing (Alpha/Beta)**: قوائم بريد محددة أو مجموعات Google Groups لاختبار ميزات محددة قبل الطرح العام.
   - **Open Testing (Public Beta)**: يمكن لأي مستخدم على المتجر الانضمام للبيتا دون موافقة مسبقة.
   - **Production (مع Staged Rollout)**: النسخة العامة المتاحة للملايين، ويتم طرحها تدريجياً بنسب تصاعدية (مثلاً: 1% -> 5% -> 20% -> 50% -> 100%).

## Practical walkthrough

إعداد Gradle لتوليد مخرجات البناء ونسخ الـ mapping.txt آلياً للأرشفة:
```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

// مهمة أتمتة لأرشفة ملف الـ mapping.txt الناتج مع رقم النسخة:
tasks.register<Copy>("archiveMappingFile") {
    dependsOn("minifyReleaseWithR8")
    from(layout.buildDirectory.dir("outputs/mapping/release"))
    into(layout.projectDirectory.dir("release-artifacts/mappings"))
    include("mapping.txt")
    rename { "mapping-v${android.defaultConfig.versionName}.txt" }
}
```

## Why it matters and how it works

An AAB is a publishing format from which Google Play serves device-specific APKs. Tracks control audience and rollout, not source branches. Mapping/native symbols must match the exact binary for useful crash analysis.

## Worked example

Build AAB from commit X, store SHA-256, mapping and test evidence; upload to internal testing, run smoke tests, then promote the same version to a small production percentage. If a regression appears, halt rollout and fix-forward under platform constraints.

## Trade-offs and decision criteria

Internal track speeds feedback but has narrower device coverage. Production staged rollout reduces blast radius but cannot undo updates already installed; plan backend feature gates and data migration compatibility.

## Failure modes

Rebuilding a “same version” from a different commit invalidates test evidence and mapping. Uploading debug APK instead of release AAB misses R8/ABI behavior. Preserve immutable artifact identity.

## Production perspective

Release manifest links commit, variant, versionCode, signing identity, artifact hash, mapping and track history. Telemetry segments crashes and payment failures by version/device cohort.

## Interview answer — short

Build artifacts are the compiled deliverables of a build: AAB for Play Store distribution, APKs for direct testing, mapping.txt for R8 crash de-obfuscation, and baseline profiles for startup speed. Release tracks in Google Play Console are tiered delivery rings: Internal (fast team testing), Closed (controlled cohorts), Open (public beta), and Production (staged rollout to general users).

## Interview answer — structured

Build artifacts and release tracks form the operational pipeline connecting local compilation to production delivery.

First, **Core Android Build Artifacts**. Next, an Android App Bundle (.aab) is the mandatory distribution format for Google Play. Enables Dynamic Delivery where Google Play generates device-optimized Split APKs tailored to screen density, language, and CPU architecture (ABI).
Additionally, with APK (.apk), standalone installable packages primarily built for local development, QA testing, and distribution via Firebase App Distribution. With ProGuard / R8 Mapping File (`mapping.txt`), crucial metadata that maps obfuscated class and method names back to original Kotlin source lines. Without uploading this to Crashlytics or Play Console, stack traces remain unreadable.
With Baseline Profile (`baseline.prof`), compiled profile rules that guide ART ahead-of-time compilation for instant app startup. **Google Play Release Tracks**.
With Internal Testing Track, fast-tracked to up to 100 authorized testers, bypassing deep review gates in minutes. With Closed (Alpha/Beta) Track, targeted tester pools for feature validation.
With Open Track, broad public opt-in beta testing. Finally, a Production Track is the general consumer release channel, configured with staged percentage rollouts (1% to 100%) to mitigate blast radius.


## Interview answer — deep senior

From an architectural release management standpoint, artifact immutability and track promotion are fundamental.

First, an Artifact Immutability is a fundamental CI/CD anti-pattern is compiling one artifact for QA testing and recompiling another binary for production. High-performing teams compile a single signed release AAB once, promote it through Internal -> Beta -> Production tracks without rebuilding. Recompiling introduces timestamp drift, dependency version discrepancies, and untracked code changes. Next, with Dynamic Delivery & App Slicing, distributing raw Universal APKs inflates download sizes by bundling multiple densities (hdpi to xxxhdpi) and CPU ABIs (armeabi-v7a, arm64-v8a, x86_64). Google Play uses the AAB to serve minimal split APKs, reducing data usage and uninstallation rates.
Finally, with Automated Crashlytics Symbol Uploading, cI workflows must integrate the Firebase Crashlytics Gradle plugin (`uploadCrashlyticsSymbolFileRelease`) or Play Developer API to guarantee that every release artifact is strictly paired with its corresponding obfuscation mapping in observability tools.


## How to answer in the interview

- **Why:** release evidence must map to exact bytes.
- **How:** attach commit, variant, digest, mapping and track.
- **Trade-off:** artifact retention versus reproducible incident analysis.
- **Failure case:** wrong mapping makes crash stack unreadable.
- **Production solution:** promote one verified AAB and keep provenance.

## Deep-dive talking points

Prompt for AAB/splits, matching mapping, immutable promotion, installed-version rollback limit.

## Follow-up questions

- **Interviewer:** "What happens if you release an app without uploading mapping.txt to Crashlytics?"
  **Answer:** "Crash reports show obfuscated symbols like `a.b.c(SourceFile:1)` making it impossible to identify the culprit line or method in production."

- **Interviewer:** "Why shouldn't you recompile the app when moving from Beta to Production track?"
  **Answer:** "Recompiling violates artifact immutability and risks shipping untested bytecode differences; the exact binary validated by QA must be promoted."

## Self-check rubric

Name the AAB/APK, mapping file, symbols and test reports as versioned artifacts; distinguish internal, closed, open and production tracks; explain how one artifact retains provenance.

## References and reviewed-on date

- [Android App Bundle](https://developer.android.com/guide/app-bundle) — distribution format.
- [Play publishing overview](https://developer.android.com/studio/publish) — release tracks.

Technically reviewed against primary documentation on 2026-10-13.
