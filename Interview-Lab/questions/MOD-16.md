---
id: "MOD-16"
question: "How do you test and publish a reusable Android library/SDK module?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 369
editorial_status: "reviewed"
---

# MOD-16

## Original interview question

How do you test and publish a reusable Android library/SDK module?

## What the interviewer evaluates

- Treat binary API, consumer rules, metadata and variant behavior as product contracts.
- Cover unit, instrumented, consumer-app and compatibility tests.
- Describe reproducible publishing and release artifacts.

## Concept and technical explanation

Testing and publishing an enterprise-grade Android library or SDK module requires balancing API stability, packaging standards, and consumer developer experience:
- Maven Publishing: Configuring the maven-publish Gradle plugin to export release AAR artifacts, POM dependencies, and sources JARs (via publishing { singleVariant("release") { withSourcesJar() } }).
- Consumer ProGuard Rules: Declaring consumerProguardFiles("consumer-rules.pro") so consuming applications automatically inherit necessary keep rules for public API symbols and serialization models without manual consumer configuration.
- Binary Compatibility Validation: Enforcing strict backward compatibility using JetBrains' Binary Compatibility Validator (BCV) plugin, which tracks public API dumps in Git and fails CI if a breaking signature change is introduced.
- Multi-Tiered Testing: Executing local JVM unit tests, headless Compose screenshot tests (using Paparazzi or Roborazzi), and instrumented integration tests against an isolated :sample application module.

## Practical walkthrough (English)

Configuring Maven publishing, consumer rules, and binary validation for an SDK:
```kotlin
// In :library:payment-sdk/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    id("maven-publish")
    alias(libs.plugins.binary.compatibility.validator)
}

android {
    namespace = "com.company.paymentsdk"
    defaultConfig {
        consumerProguardFiles("consumer-rules.pro")
    }
    publishing {
        singleVariant("release") { withSourcesJar() }
    }
}

publishing {
    publications {
        register<MavenPublication>("release") {
            afterEvaluate { from(components["release"]) }
            groupId = "com.company.sdk"
            artifactId = "payment"
            version = "1.4.0"
        }
    }
}
```

## Explanation in Arabic

كيف تختبر وتنشر مكتبة أو SDK أندرويد قابلة لإعادة الاستخدام (Reusable Android Library/SDK Module)؟

1. عقود ومسؤوليات بناء الـ SDK:
   - عندما تبني مكتبة مستقلة (تُوزع كـ AAR أو JAR عبر Maven/Nexus/Artifactory)، فإنك تبني منتجاً عاماً يجب أن يراعي:
     * **الاستقرار الثنائي والتوافق (Binary Compatibility & Semantic Versioning)**: تجنب كسر التوافق مع الإصدارات السابقة (Backward Compatibility).
     * **تقليل الاعتماديات الخارجية (Minimizing Dependencies)**: إذا استخدم الـ SDK مكتبات مثل OkHttp أو Coroutines بنسخ قديمة، فقد يتعارض مع نسخ التطبيق المستضيف (Dependency Hell / NoSuchMethodError).
     * **قواعد الحماية والـ Consumer Proguard Rules**: تضمين ملف `consumer-rules.pro` لحماية الكلاسات العامة من الحذف عند قيام التطبيق المستضيف بتفعيل R8/ProGuard.

2. استراتيجية الاختبار المتكاملة للـ SDK:
   - **Unit Tests على الـ JVM**: اختبار منطق الأعمال الداخلي بشكل معزول وسريع.
   - **Instrumented Tests**: اختبار التفاعل مع عتاد ونظام أندرويد الحقيقي.
   - **Sample Consumer App**: تطبيق أندرويد تجريبي حقيقي داخل نفس الـ Repository يستورد المكتبة ويختبر تجربة المطور (DX) والتكامل الواقعي.
   - **Binary Compatibility Validator (BCV)**: أداة رسمية من JetBrains تفحص الـ Public API للمكتبة وتفشل الـ Build إذا قام مطور بتغيير كسر التوافق دون تغيير رقم الإصدار الأساسي (Major Version).

3. النشر الآلي (Publishing Pipeline):
   - استخدام `maven-publish` plugin لنشر الـ AAR والـ POM و Gradle Module Metadata و Javadoc.

## Practical walkthrough

إعداد نشر مكتبة Android باستخدام maven-publish و consumer-rules:
```kotlin
// 📁 في build.gradle.kts الخاص بموديول المكتبة (:mylibrary):
plugins {
    id("com.android.library")
    id("maven-publish")
    id("org.jetbrains.kotlinx.binary-compatibility-validator") // فحص كسر الـ API في CI
}

android {
    namespace = "com.company.sdk"
    compileSdk = 35
    
    defaultConfig {
        minSdk = 21
        // تضمين قواعد الحماية التي سيطبقها التطبيق المستهلك تلقائياً:
        consumerProguardFiles("consumer-rules.pro")
    }
    
    publishing {
        singleVariant("release") { withSourcesJar(); withJavadocJar() }
    }
}

publishing {
    publications {
        register<MavenPublication>("release") {
            afterEvaluate { from(components["release"]) }
            groupId = "com.company.sdk"
            artifactId = "core-sdk"
            version = "2.1.0"
        }
    }
}
```

## Why it matters and how it works

An AAR packages code, resources and manifest contributions, while publishing metadata describes dependencies and variants. A library's internal tests cannot detect every consumer integration failure: an accidentally hidden API type, missing consumer keep rule or manifest conflict may appear only when another app compiles or shrinks it. Binary compatibility matters because consumers may upgrade independently.

## Worked example

A camera SDK exposes `CameraSession` and bundles a ContentProvider and a reflection-based codec. Its CI runs unit and emulator tests, compiles a separate sample app against the published artifact, checks merged manifest authority, and launches a minified release variant. A version upgrade test verifies clients can use the documented API without importing SDK internals.

## Trade-offs and decision criteria

Consumer-app tests cost build time but catch integration failures early. A broad public API is convenient initially but hard to evolve. Strict semantic versioning requires binary/source compatibility discipline; Android resource names and manifest behavior also need migration notes. Publishing snapshots speeds feedback but must not be confused with signed releases.

## Failure modes

Library tests pass but consumer compilation fails due to missing `api` dependency. R8 removes a reflective class in release. Manifest merge conflicts with host authority. Published POM differs from local project dependency behavior. A private key or token enters the artifact or CI logs.

## Production perspective

Automate API diff checks, dependency metadata inspection, sample-app debug/release builds and artifact provenance. Stage the publication, verify retrieval from the repository, and keep rollback/deprecation guidance for consumers.

## Interview answer — short

Publishing an Android library requires configuring the maven-publish plugin to generate AAR and sources artifacts, embedding consumerProguardFiles to protect public API symbols automatically in consuming apps, and using the Binary Compatibility Validator to prevent breaking changes. Testing combines JVM unit tests, screenshot tests, and sample app integration suites.

## Interview answer — structured

Building and publishing a reusable Android library module requires distinct engineering practices compared to building an application.
First, we configure the maven-publish Gradle plugin inside the library module, specifying Maven coordinates, POM metadata, and publishing singleVariant release with attached sources JARs.
Second, we define consumer ProGuard rules using consumerProguardFiles.
These rules are automatically bundled inside the exported AAR, instructing the consumer's R8 shrinker to preserve our public API signatures without requiring developers to write custom rules.
Third, we enforce binary compatibility using JetBrains' Binary Compatibility Validator plugin.
This tool dumps public API signatures into a tracked text file in Git, failing CI builds if an engineer accidentally alters or removes a public method signature without a major version bump.
Finally, testing combines JVM unit tests, Paparazzi screenshot tests for UI components, and an isolated sample application that validates real-world integration.

## Interview answer — deep senior

Engineering an internal or commercial Android SDK demands treating your public API surface as an immutable contract.
Unlike an application where refactoring is internal, breaking an SDK's Application Binary Interface breaks builds for external partner teams.
Our publishing architecture centers on three robust pillars: deterministic packaging, automated consumer protection, and strict ABI governance.
In build configuration, we utilize the modern android.publishing DSL with singleVariant release and withSourcesJar, exporting release components via maven-publish to our internal Nexus or Artifactory repository.
We embed consumer-rules.pro using consumerProguardFiles.
This ensures that when consumer apps run R8, our public entry points, reflective serializers, and native JNI bindings are preserved automatically, preventing catastrophic ClassNotFoundException crashes in production client apps.
To enforce semantic versioning programmatically, we integrate JetBrains' Binary Compatibility Validator plugin into our CI pipeline.
The tool maintains an api/payment-sdk.api dump in version control.
If a pull request deletes a public parameter, changes a return type, or alters nullability without an explicit API dump update, the build fails immediately.
Our verification pipeline runs JVM unit tests for business logic, Roborazzi screenshot verification for custom UI widgets, and automated instrumented tests running inside a companion :sample app module, guaranteeing that every published AAR is production-tested prior to release.

## How to answer in the interview

- **Why:** library contract extends beyond source code.
- **How:** test AAR consumer and release shrinker.
- **Trade-off:** stable API versus evolution freedom.
- **Failure case:** consumer strips reflected class.
- **Production solution:** publish sample and binary compatibility checks.

## Deep-dive talking points

Discuss AAR/metadata, public ABI, consumerProguardFiles, manifest merge, sample app, provenance and versioning.

## Follow-up questions

- **Interviewer:** "What is the difference between `proguardFiles` and `consumerProguardFiles` in an Android library?"
  **Answer:** "`proguardFiles` configures obfuscation for the library itself during its build; `consumerProguardFiles` bundles rules packaged inside the AAR for the client app to apply during its build."

- **Interviewer:** "Why should SDK public APIs use explicit visibility modifiers (`explicitApi()`)?"
  **Answer:** "Kotlin's `explicitApi()` compiler mode forces developers to explicitly declare `public` or `internal` and return types on all declarations, preventing accidental leakage of internal implementation details."

## Self-check rubric

Name artifact contracts, test layers, a release-only failure, and publishing verification.

## References and reviewed-on date

- [Create an Android library](https://developer.android.com/studio/projects/android-library) — AAR and module behavior.
- [Gradle Maven publishing](https://docs.gradle.org/current/userguide/publishing_maven.html) — artifact metadata.
- [R8 and library keep rules](https://developer.android.com/topic/performance/app-optimization/library-optimization) — consumer configuration.

Technically reviewed against primary documentation on 2026-10-13.
