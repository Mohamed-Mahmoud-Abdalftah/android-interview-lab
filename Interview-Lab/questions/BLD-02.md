---
id: "BLD-02"
question: "What are build types, product flavors, variants, and source sets?"
topic: "Gradle, AGP, R8, Signing & Release Engineering"
code: "BLD"
group: "A"
phase: 4
priority: "P1"
order: 376
editorial_status: "reviewed"
---

# BLD-02

## Original interview question

What are build types, product flavors, variants, and source sets?

## What the interviewer evaluates

- Explain dimensions and cross-product composition.
- Describe source-set merge priority and variant-specific tests.
- Avoid confusing debug/release with customer or environment flavor.

## Concept and technical explanation

The Android Gradle Plugin structures multi-target releases across four foundational build abstractions:
- Build Types: Configure technical packaging, compilation, and optimization parameters for different deployment phases (e.g., debug vs release). They control code minification and shrinking (R8), debuggability flags, signing configurations, and applicationIdSuffix properties (e.g., .debug).
- Product Flavors: Represent distinct functional, commercial, or environmental variations of the app (e.g., free vs paid, or staging vs production). Flavors are organized under flavorDimensions to prevent naming collisions.
- Build Variants: The Cartesian product combining every configured product flavor across all dimensions with every build type. For example, two dimensions with two flavors each combined with two build types yields eight distinct build variants (e.g., demoStagingRelease).
- Source Sets: Directory structures (such as src/main, src/debug, src/demo, and src/demoStagingRelease) containing code and resources. AGP merges manifests hierarchically, overrides XML resources and assets by variant priority, but enforces strict class-path exclusivity where Java/Kotlin classes with identical fully-qualified names cannot coexist across overlapping active source sets.

## Practical walkthrough (English)

Configuring flavor dimensions, build types, and examining source set overrides:
```kotlin
android {
    flavorDimensions += listOf("environment", "tier")

    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
        }
        create("production") {
            dimension = "environment"
        }
        create("free") {
            dimension = "tier"
            buildConfigField("Boolean", "SHOW_ADS", "true")
        }
        create("premium") {
            dimension = "tier"
            buildConfigField("Boolean", "SHOW_ADS", "false")
        }
    }

    buildTypes {
        getByName("debug") {
            isDebuggable = true
            isMinifyEnabled = false
        }
        getByName("release") {
            isDebuggable = false
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

// Resulting build variants matrix:
// 1. stagingFreeDebug, stagingFreeRelease
// 2. stagingPremiumDebug, stagingPremiumRelease
// 3. productionFreeDebug, productionFreeRelease
// 4. productionPremiumDebug, productionPremiumRelease
```

## Explanation in Arabic

ما هي الـ Build Types، والـ Product Flavors، والـ Build Variants، والـ Source Sets في أندرويد وكيف تتكامل معاً؟

1. أنواع البناء (Build Types):
   - تحدد **كيفية بناء التطبيق وتجهيزه تقنياً** (Build & Packaging Characteristics).
   - أشهر نوعين هما: `debug` (مفتوح للـ Debugging، غير مشوش، موقع بمفتاح تجريبي) و `release` (مغلق، مشوش عبر R8، مصغر الحجم، موقع بمفتاح إنتاج رسمي).

2. نكهات المنتج (Product Flavors):
   - تحدد **الميزات والخصائص التجارية الموجهة للمستخدم أو البيئة** (Product Features & Branding).
   - أمثلة: `free` مقابل `paid`، أو البيئات: `dev`, `staging`, `prod` (مع تغيير الـ Base URL والـ Application ID).
   - تُجمع النكهات تحت أبعاد صريحة (`flavorDimensions = listOf("environment", "tier")`).

3. متغيرات البناء (Build Variants):
   - هي **حاصل الضرب الديكارتي (Cartesian Product)** لكل Flavor مع كل Build Type.
   - مثال: نكهتان (`free`, `paid`) × نوعان (`debug`, `release`) = 4 Variants:
     `freeDebug`, `freeRelease`, `paidDebug`, `paidRelease`.

4. مجموعات المصادر (Source Sets):
   - مجلدات الكود والموارد المخصصة لكل Variant.
   - الأولوية في دمج الموارد والكود: `src/freeDebug/` تتفوق على `src/free/` التي تتفوق على `src/debug/` التي تتفوق على الكود المشترك في `src/main/`.

## Practical walkthrough

تكوين Flavors و Build Types وأبعاد النكهات وتخصيص الـ Source Sets في build.gradle.kts:
```kotlin
android {
    flavorDimensions += listOf("environment", "monetization")

    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            buildConfigField("String", "BASE_URL", "\"https://dev.api.example.com\"")
        }
        create("prod") {
            dimension = "environment"
            buildConfigField("String", "BASE_URL", "\"https://api.example.com\"")
        }
        create("free") {
            dimension = "monetization"
        }
        create("pro") {
            dimension = "monetization"
            applicationIdSuffix = ".pro"
        }
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

## Why it matters and how it works

AGP creates a variant for each valid combination of build type and flavor dimensions and merges relevant source sets. More dimensions multiply variants and build/CI cost. Variant-specific resources and manifests can override common values according to priority, which affects authorities, endpoints and app labels. Signing and optimization may differ from debug and expose release-only faults.

## Worked example

An app has `demo`/`full` flavor and `debug`/`release` type, yielding four variants. `src/main` has shared UI, `src/demo` supplies demo branding, and `src/fullRelease` supplies a publication-only provider authority. CI checks `fullRelease` merged manifest and minified startup, because `demoDebug` cannot prove the publication artifact.

## Trade-offs and decision criteria

Flavors support meaningful product/environment differences but can cause a variant explosion. Separate runtime configuration from compile-time flavor only when security and operational behavior allow. Repeated source-set overrides make logic hard to trace; keep differences explicit and small.

## Failure modes

A production endpoint is assumed because debug uses it, while release flavor overrides it. A provider authority differs after manifest merge. One dimension multiplies test matrix unexpectedly. A secret is embedded in `src/prod` and extracted from the app. A release-only minification bug is never exercised.

## Production perspective

List supported variants and source-set priorities, test the published combination, inspect merged manifest/resources, and track variant matrix size. Use server-side secrets and protected CI signing, not source-set secrecy.

## Interview answer — short

Build types configure packaging and optimization settings like debugging and minification. Product flavors customize functional or environmental variations like staging versus production. Build variants represent the Cartesian product combining each flavor and build type. Source sets define hierarchical directories that merge code, resources, and manifests according to variant priority.

## Interview answer — structured

Configuring complex Android applications requires understanding the modular matrix composed of build types, product flavors, variants, and source sets.
First, build types define technical packaging properties for distinct development stages, configuring R8 minification, debuggability, signing configurations, and applicationId suffixes such as debug or release.
Second, product flavors customize application features, branding, or server environments along defined flavor dimensions, such as creating demo versus full versions or internal versus production endpoints.
Third, build variants represent the Cartesian product combining every configured flavor across dimensions with each build type, such as demoInternalRelease.
Fourth, source sets structure the project directory hierarchy. AGP merges manifests, XML resources, and assets according to strict priority where variant-specific source sets override flavor-specific sets, which in turn override the main codebase.

## Interview answer — deep senior

Architecting multi-tenant or enterprise Android repositories requires mastering how Gradle and AGP compute build variants and merge source sets.
Build types govern packaging and optimization flags: the debug build enables debugging and disables R8 to preserve fast compilation, whereas release enforces R8 shrinking, obfuscation, and production signing.
Product flavors allow teams to maintain distinct versions of an application from a single codebase: we declare flavor dimensions such as environment (staging, production) and distribution (googlePlay, amazon).
AGP multiplies these dimensions against build types to compute the build variant matrix: two environments times two distributions times two build types yields eight distinct build variants.
Source sets provide the physical folder structure corresponding to this matrix.
Understanding AGP's merging rules is essential for production stability.
Manifest files merge hierarchically using the Manifest Merger tool, where variant-specific manifests take precedence over flavor manifests, and flavor manifests override src/main/AndroidManifest.xml.
Resources such as XML strings and drawables follow an identical override precedence.
However, Kotlin and Java source files cannot overlap: defining a class with the same fully-qualified name in both src/main and a flavor source set results in a duplicate class compilation error, requiring engineers to place polymorphic implementations in separate flavor source sets or extract shared logic into dedicated feature modules.

## How to answer in the interview

- **Why:** variant combinations change shipped behavior.
- **How:** state build type, flavor and source precedence.
- **Trade-off:** matrix coverage versus build cost.
- **Failure case:** debug-only config hides release gap.
- **Production solution:** assert critical release variant.

## Deep-dive talking points

Discuss cross-product, source-set priority, manifest override, variant explosion, secrets and release tests.

## Follow-up questions

- **Interviewer:** "Can two different flavors define different applicationId values?"
  **Answer:** "Yes, either by setting distinct applicationId values or using applicationIdSuffix (e.g., .dev) to allow installing both side-by-side on one device."

- **Interviewer:** "What happens if a string resource with the same key exists in both src/main and src/flavor/res?"
  **Answer:** "The flavor-specific resource overrides the main resource during the AAPT2 resource merging phase."

## Self-check rubric

Derive a four-variant matrix, trace one override, and name a release-only failure.

## References and reviewed-on date

- [Configure build variants](https://developer.android.com/build/build-variants) — dimensions and source-set priority.
- [Android build structure](https://developer.android.com/build/android-build-structure) — project layout.

Technically reviewed against primary documentation on 2026-10-13.
