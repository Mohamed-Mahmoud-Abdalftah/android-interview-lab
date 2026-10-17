---
id: "MOD-12"
question: "How do version catalogs and convention plugins reduce config duplication?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 365
editorial_status: "reviewed"
---

# MOD-12

## Original interview question

How do version catalogs and convention plugins reduce config duplication?

## What the interviewer evaluates

- Distinguish centralized dependency coordinates from reusable build logic.
- Explain one-source configuration with override/variant limits.
- Verify changes on actual modules and avoid hiding complexity.

## Concept and technical explanation

In large multi-module Android codebases spanning dozens of modules, duplicating compiler options, SDK versions, and dependency declarations across individual build.gradle.kts files creates severe maintenance debt and configuration drift. Two complementary Gradle mechanisms resolve this:
- Gradle Version Catalogs (gradle/libs.versions.toml): Centralizes all dependency coordinates, plugin identifiers, and version declarations into a single declarative file. It generates type-safe, auto-completing accessors (e.g., libs.androidx.compose.ui, libs.plugins.android.library) across all build scripts, eliminating string-literal version duplication and easing mass library upgrades.
- Gradle Convention Plugins (via build-logic composite build): Reusable custom Gradle plugins that encapsulate shared build logic and architectural standards (e.g., configuring Android SDK levels, Java/Kotlin toolchains, Compose compiler flags, and code quality linters in one place). Feature modules apply single-line convention plugins instead of copy-pasting hundreds of lines of build setup.

## Practical walkthrough (English)

Centralizing build configurations with Version Catalogs and custom Convention Plugins:
```toml
# gradle/libs.versions.toml
[versions]
compose = "1.7.0"
compileSdk = "35"

[libraries]
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

```kotlin
// build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
class AndroidFeatureConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) = with(target) {
        with(pluginManager) {
            apply("com.android.library")
            apply("org.jetbrains.kotlin.android")
        }
        extensions.configure<LibraryExtension> {
            compileSdk = 35
            defaultConfig { minSdk = 26 }
        }
        dependencies {
            add("implementation", project(":core:designsystem"))
        }
    }
}

// In feature/checkout/build.gradle.kts: Clean two-line configuration!
plugins {
    id("company.android.feature")
}
```

## Explanation in Arabic

كيف تقلل ملفات كتالوج الإصدارات (Version Catalogs) و Convention Plugins تكرار إعدادات Gradle في المشاريع النمطية؟

1. المشكلة في المشاريع الكبيرة بدون هذه الأدوات:
   - تطبيق يحتوي على 60 موديولاً: كل ملف `build.gradle.kts` يكرر 40 سطراً من الإعدادات: `compileSdk = 35`, `minSdk = 26`, إعدادات `kotlinCompilerExtensionVersion`, إعدادات `JavaVersion.VERSION_17`, وتكرار نسخ المكتبات.
   - إذا أردت ترقية نسخة Compose أو Kotlin، تضطر لتعديل 60 ملفاً يدوياً، مع خطر عدم توافق النسخ في بعض الموديولات.

2. دور الـ Version Catalog (`gradle/libs.versions.toml`):
   - **مصدر موحد للحقيقة (Single Source of Truth)** لجميع إصدارات المكتبات والـ Plugins.
   - يوفر Type-Safe Accessors تلقائياً في Gradle: بدلاً من نصوص سحرية `implementation("androidx.compose.ui:ui:1.7.0")`، تكتب `implementation(libs.androidx.compose.ui)` مع إكمال تلقائي في الـ IDE.

3. دور الـ Convention Plugins (في مجلد `build-logic`):
   - تحويل كود إعدادات Gradle المتكرر إلى Plugins مخصصة وقابلة لإعادة الاستخدام:
     * `com.example.android.feature`: يطبق تلقائياً مكتبة أندرويد، و Compose، و Hilt، ونسخ الـ SDK.
     * `com.example.jvm.library`: يطبق إعدادات Kotlin النقي لموديولات الـ Domain.
   - يتقلص ملف `build.gradle.kts` الخاص بكل موديول من 50 سطراً إلى 5 أسطر فقط!

## Practical walkthrough

المقارنة بين ملف build.gradle.kts التقليدي وملف نظيف مدعوم بـ Convention Plugins:
```kotlin
// ❌ في السابق: 40 سطراً مكررة في كل موديول من الـ 60 موديولاً:
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("kotlin-kapt")
}
android {
    compileSdk = 35
    defaultConfig { minSdk = 26 }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17 }
    buildFeatures { compose = true }
    // ... 30 سطراً أخرى مكررة!
}

// ✅ مع Convention Plugins و Version Catalog: ملف build.gradle.kts في 5 أسطر فقط!
plugins {
    alias(libs.plugins.example.android.feature) // يطبق كل ما سبق تلقائياً!
}

dependencies {
    implementation(projects.core.designsystem)
    implementation(projects.domain.order)
}
// ترقية إصدار الـ SDK أو المكتبات تتم الآن بتعديل رقم واحد فقط في libs.versions.toml!
```

## Why it matters and how it works

Catalog aliases centralize dependency and plugin coordinates for a multi-project build. Convention plugins package Gradle configuration logic as reusable, typed build logic and make module scripts smaller. A change to a shared convention or catalog can fan out across the graph, so its compatibility and performance impact should be checked with representative modules and variants.

## Worked example

`:feature:orders` applies `company.android.feature` and declares `implementation(libs.androidx.lifecycle.runtimeCompose)`. The convention sets Android/Kotlin toolchain, common test tasks and Compose options once; the catalog pins coordinates. A payment SDK remains a direct dependency of checkout rather than being added by the generic convention to all features.

## Trade-offs and decision criteria

Centralization reduces drift but can create a high-impact change point. Separate narrow conventions for library, feature and app modules rather than one plugin with many conditionals. Catalogs improve discoverability, yet version conflicts still require dependency insight and compatibility tests.

## Failure modes

Every module applies a giant convention that brings unnecessary plugins and slows configuration. A catalog alias is updated without checking AGP/Kotlin compatibility. A feature adds a needed direct dependency only to the catalog, so compile still fails. Build logic silently overrides a module's release settings.

## Production perspective

Version build logic, review catalog updates, run a representative module and full app variant in CI, and profile configuration time. Document supported override points and keep module scripts declarative.

## Interview answer — short

Version catalogs centralize all library versions and plugin IDs in a single declarative TOML file, generating type-safe accessors across the project. Convention plugins encapsulate repetitive build logic, SDK versions, and compiler flags in custom Gradle plugins inside a build-logic composite build, reducing module build scripts to concise, standardized declarations.

## Interview answer — structured

Managing build configurations across dozens of Gradle subprojects requires eliminating copy-pasted build scripts to prevent configuration drift.
Gradle Version Catalogs solve the dependency coordination problem.
By consolidating all dependency coordinates, plugin IDs, and version numbers into gradle/libs.versions.toml, the entire engineering team shares a single source of truth.
Gradle generates type-safe accessors like libs.retrofit, giving developers auto-completion and compile-time verification when adding dependencies.
Convention plugins solve the build logic duplication problem.
Using a composite build typically named build-logic, we author custom plugins that configure standard build conventions.
For instance, an AndroidFeatureConventionPlugin configures the Android library plugin, Kotlin toolchains, Compose compiler options, and baseline testing dependencies.
Individual feature modules apply this single convention plugin, reducing their build.gradle.kts files from fifty lines of boilerplate to a clean, declarative configuration.

## Interview answer — deep senior

As Android codebases scale past thirty modules, build script divergence becomes a major engineering bottleneck.
Teams copy-paste build scripts, leading to inconsistent compileSdk versions, mismatched Kotlin compiler options, missing ProGuard configurations, and configuration cache invalidations.
We solve this systematically through the combination of Version Catalogs and Convention Plugins implemented via composite builds.
The Version Catalog in gradle/libs.versions.toml acts as our immutable dependency manifest.
It categorizes versions, libraries, and bundles, providing type-safe Kotlin DSL accessors that eliminate error-prone string literals and ensure atomic, synchronized upgrades of related libraries like Jetpack Compose or KotlinX Coroutines.
To eliminate build configuration duplication, we construct an independent build-logic project included via includeBuild in settings.gradle.kts.
Unlike the legacy buildSrc directory which invalidates the build cache for the entire project upon every single edit, a composite build operates as an isolated Gradle project with its own cache lifecycle.
Within build-logic, we author lightweight, composable convention plugins.
For example, company.android.library configures compileSdk, minSdk, JVM toolchains, and freeCompilerArgs; company.android.compose attaches the Compose compiler extension and standard UI test dependencies; and company.android.feature bundles both while injecting common :core modules.
Feature build.gradle.kts files become purely declarative, often requiring under ten lines of code.
This architecture guarantees absolute configuration consistency, simplifies enterprise-wide upgrades, and preserves maximum build caching performance across our continuous integration pipeline.

## How to answer in the interview

- **Why:** duplicate config drifts across modules.
- **How:** centralize versions and true conventions.
- **Trade-off:** consistency versus hidden magic.
- **Failure case:** plugin injects unused SDK everywhere.
- **Production solution:** profile build and keep dependency local.

## Deep-dive talking points

Compare catalog aliases, convention behavior, direct dependencies, build logic tests and configuration cost.

## Follow-up questions

- **Interviewer:** "Why is `subprojects { ... }` considered an anti-pattern in modern Gradle?"
  **Answer:** "It couples projects together imperatively, breaking Gradle Configuration Cache, Isolated Projects, and parallel configuration."

- **Interviewer:** "Can convention plugins configure dependencies as well as build options?"
  **Answer:** "Yes. An `AndroidFeatureConventionPlugin` can automatically add common dependencies like Hilt, Compose, and core testing libraries to all feature modules."

## Self-check rubric

Show one catalog alias and one convention, name a direct module dependency, and define CI evidence.

## References and reviewed-on date

- [Gradle version catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html) — aliases and versions.
- [Gradle convention plugins](https://docs.gradle.org/current/userguide/sharing_build_logic_between_subprojects.html) — reusable build logic.

Technically reviewed against primary documentation on 2026-10-13.
