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

Build types configure packaging and debugging attributes (debug vs release), product flavors configure feature sets and branding (free vs paid), build variants are the Cartesian product of both (e.g. freeRelease), and source sets provide variant-specific code and resource overlays resolved hierarchically over src/main.

## Interview answer — structured

The Android build variant matrix organizes compilation targets into distinct operational axes:

1. **Build Types (How it is built)**:
   - Dictate technical packaging configurations: debuggability (`isDebuggable`), code optimization and obfuscation (`isMinifyEnabled`), resource shrinking, signing configurations, and symbols stripping.

2. **Product Flavors (What is built)**:
   - Dictate business and environment differentiation. Grouped by `flavorDimensions` (e.g., `environment` for dev/staging/prod; `distribution` for gms/hms). They configure `applicationIdSuffix`, specific `buildConfigField` parameters, and feature toggles.

3. **Build Variants (The Output Permutations)**:
   - The Cartesian product of every dimension flavor multiplied by build types. For example, 2 environments (`dev`, `prod`) × 2 types (`debug`, `release`) yields 4 runnable variants: `devDebug`, `devRelease`, `prodDebug`, `prodRelease`.

4. **Source Sets (Resource & Code Overlays)**:
   - Dedicated directory structures (e.g., `src/devDebug/`, `src/dev/`, `src/main/`). The Gradle resource merger merges files hierarchically: variant-specific assets override flavor-specific assets, which in turn override `src/main/` defaults.

## Interview answer — deep senior

From an enterprise release and build-velocity viewpoint, managing the variant matrix requires defensive configuration:

1. **Variant Filter Optimization**: Creating 3 flavor dimensions with 3 flavors each generates $3 \times 3 \times 2 = 18$ variants. Gradle evaluates tasks for every variant, blowing up configuration time. Filter out useless permutations using `variantFilter { if (name == "demoStagingRelease") setIgnore(true) }` to drastically reduce sync and build times.

2. **Code Discrepancies Across Source Sets**: While resources merge automatically, Kotlin/Java source files in source sets do not merge; they conflict. If a class `Logger.kt` is placed in `src/debug/`, it cannot exist in `src/main/` or a duplicate class compilation error occurs. Keep `src/main/` clean and use interfaces with dependency injection rather than duplicating classes across variant source sets.

3. **Dynamic Manifest Placeholders**: Inject variant-specific deep link schemes, authorities, and API keys using `manifestPlaceholders = mapOf("authDomain" to "dev.auth.com")` rather than maintaining separate `AndroidManifest.xml` files per flavor.

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
