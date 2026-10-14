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

Version Catalogs (libs.versions.toml) centralize all dependency coordinates and versions in a single type-safe source of truth. Convention plugins (in build-logic) encapsulate repeated Gradle configuration (SDK versions, compiler options, Compose/Hilt setups) into reusable plugins, reducing individual module build scripts to a few declarative lines.

## Interview answer — structured

Managing dozens of Gradle subprojects requires centralizing both dependency versions and build logic.

First, with Version Catalogs (`libs.versions.toml`), centralizes third-party dependency coordinates, plugin identifiers, and version numbers. Gradle automatically generates type-safe DSL accessors (`libs.androidx.core.ktx`). Upgrading a library version across 80 modules requires editing a single line in the catalog, preventing version drift. Finally, convention Plugins (via `build-logic`) encapsulates repeated Gradle configuration patterns into custom composite build plugins written in Kotlin (`AndroidFeatureConventionPlugin`, `AndroidLibraryConventionPlugin`, `JvmLibraryConventionPlugin`).

Instead of copying 50 lines of `android { ... }` blocks, JVM target options, and Compose compiler configurations into every module, a feature module simply applies `plugins { alias(libs.plugins.myapp.android.feature) }`, keeping build scripts minimal, consistent, and maintainable.


## Interview answer — deep senior

Architecturally, custom Convention Plugins are implemented inside an included composite build (typically named `build-logic`) in the project root.

Because `build-logic` is an included build, Gradle compiles it first with full Kotlin DSL type safety and autocompletion before evaluating the main project's task graph. Inside convention plugins, we write clean extension functions that configure common Android blocks:

```kotlin
internal fun Project.configureKotlinAndroid(commonExtension: CommonExtension<*, *, *, *, *, *>) {
    commonExtension.apply {
        compileSdk = 35
        defaultConfig { minSdk = 26 }
        compileOptions {
            sourceCompatibility = JavaVersion.VERSION_17
            targetCompatibility = JavaVersion.VERSION_17
        }
    }
}
```
This eliminates legacy, fragile Groovy scripts and avoids the dreaded `subprojects { ... }` block in `rootProject/build.gradle`, which breaks Gradle Configuration Caching and parallel execution.


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
