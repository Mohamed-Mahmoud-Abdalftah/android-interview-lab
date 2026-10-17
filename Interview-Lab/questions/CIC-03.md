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

## Concept and technical explanation

Android build artifacts represent the compiled deliverables of a build variant, while release tracks define progressive distribution rings connecting compilation to end users:
- Core Android Build Artifacts:
  1. Android App Bundle (.aab): The official distribution format for Google Play. Contains compiled DEX, resources, and native binaries. Enables Google Play Dynamic Delivery to generate optimized Split APKs tailored to device screen density, CPU architecture (ABI), and language, saving 20-30% download size.
  2. APK (.apk): Standalone installable package used for local development debugging, internal QA sideloading, and enterprise distribution via Firebase App Distribution.
  3. R8 / ProGuard Mapping File (mapping.txt): Generated during release shrinking. Translates obfuscated class and method tokens back to original source lines. Required by Crashlytics and Google Play for de-obfuscation.
  4. Baseline Profiles (baseline.prof): Pre-compiled rules guiding ART ahead-of-time (AOT) compilation to boost cold startup speed and scroll frame rates.
- Google Play Release Tracks:
  - Internal Testing Track: Instant distribution to up to 100 designated internal testers with virtually zero review latency.
  - Closed (Alpha/Beta) Track: Controlled cohorts of specific user groups or organizations.
  - Open Track: Broad public beta accessible directly on the store.
  - Production Track: General public consumer release with staged rollout percentages (1% to 100%).
- Principle of Artifact Immutability: Build and sign once; promote the identical binary across tracks without recompiling.

## Practical walkthrough (English)

Automated mapping file archival and release artifact configuration:
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

// Gradle task to archive release mapping files paired with version code:
tasks.register<Copy>("archiveReleaseMetadata") {
    dependsOn("minifyReleaseWithR8")
    from(layout.buildDirectory.dir("outputs/mapping/release"))
    into(layout.projectDirectory.dir("release-metadata"))
    include("mapping.txt")
    rename { "mapping-v${android.defaultConfig.versionCode}.txt" }
}
```

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

Build artifacts are compiled deliverables including AAB bundles for Google Play Dynamic Delivery, installable APKs for internal QA, mapping.txt for R8 crash de-obfuscation, and baseline profiles for startup acceleration. Release tracks are tiered distribution rings spanning Internal testing, Closed alpha cohorts, Open beta testing, and Staged Production rollouts.

## Interview answer — structured

Build artifacts and release tracks represent the compiled deliverables and progressive distribution channels connecting code compilation to end users.
On the artifact side, the Android App Bundle is the required publishing format for Google Play. It enables Dynamic Delivery, generating optimized Split APKs per device to reduce download sizes. In contrast, universal APKs serve as standalone binaries for local debugging and QA distribution via Firebase App Distribution. Critical accompanying artifacts include the R8 mapping.txt file, which is required by Crashlytics to de-obfuscate release stack traces, and Baseline Profiles that guide ahead-of-time compilation for instant application startup.
On the distribution side, Google Play Console provides tiered release tracks. The Internal track enables immediate distribution to team members without store review delays. Closed and Open tracks allow testing with controlled user cohorts and public beta testers. Finally, the Production track serves the general public using staged rollouts to monitor performance and contain regressions. Across all tracks, we enforce artifact immutability, ensuring the identical binary tested in staging is promoted to production without recompilation.

## Interview answer — deep senior

From an enterprise release governance and build architecture standpoint, managing build deliverables requires strict adherence to artifact immutability and observability pairing.
A critical anti-pattern observed in immature release pipelines is compiling one binary for QA testing and compiling a second binary for store deployment. Recompiling across environments introduces non-deterministic timestamp discrepancies, subtle dependency drift, and untested bytecode variations. High-performing mobile organizations build and sign a single immutable release Android App Bundle once, promote it through Internal, Closed, and Open tracks, and finally push that exact artifact to production.
Utilizing the Android App Bundle unlocks Google Play Dynamic Delivery and App Slicing. Rather than forcing users to download a bloated universal package containing every screen density from mdpi to xxxhdpi and native libraries across multiple architectures, the Play Store generates a minimal base APK with architecture and language splits tailored to the user device, reducing download friction and uninstalls.
Equally vital is the automated pairing of build metadata. When R8 obfuscates code, classes and line numbers are rewritten into short tokens. If the release pipeline fails to archive mapping.txt and upload it to Firebase Crashlytics via the uploadCrashlyticsSymbolFileRelease task, field crashes appear as unreadable minified traces, paralyzing incident response.
By coupling immutable AAB artifacts, automated Crashlytics symbol ingestion, and staged production rollout cadences, platform teams achieve safe, observable, and reproducible app delivery.

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
