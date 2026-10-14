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

To build and publish a reusable Android SDK, enforce strict semantic versioning and binary compatibility via JetBrains Binary Compatibility Validator. Bundle consumer ProGuard rules via consumer-rules.pro, test against a sample consumer app in the repo, and publish release AARs with POM metadata and sources via the maven-publish Gradle plugin.

## Interview answer — structured

Building an enterprise-grade reusable Android SDK requires treating the library as a self-contained product with strict stability contracts.

First, with Consumer ProGuard Rules (`consumer-rules.pro`), libraries must ship ProGuard rules that are automatically applied to consuming applications. This ensures that the SDK's public interfaces, JNI native bindings, and serialization models are not stripped or mangled when client apps run R8. Next, with Binary Compatibility Governance, use JetBrains' **Binary Compatibility Validator (BCV)** plugin in CI. It maintains an API dump file (`.api`) in Git. If a pull request modifies a public method signature or removes an overload, BCV fails the build unless the change is explicitly approved and versioned under SemVer rules.
Additionally, with Testing Pyramid, comprehensive JVM unit tests, instrumented tests on Firebase Test Lab, and an included **Sample App** module that consumes the library exactly like a third-party developer. Finally, with Publishing Pipeline, configure the `maven-publish` plugin to emit release AARs, Javadoc JARs, Sources JARs, and Gradle Module Metadata (`.module`) to a secure Maven repository (Nexus/Artifactory/MavenCentral).


## Interview answer — deep senior

When engineering production SDKs, the greatest technical pitfall is **Transitive Dependency Pollution**.

If your SDK depends on `OkHttp 4.9.0` and a host application depends on `OkHttp 5.0.0-alpha`, Gradle's conflict resolution selects the higher version, which may contain breaking binary changes that crash your SDK. Conversely, if your SDK bundles an internal library via `implementation`, the host app might experience duplicate class conflicts.

To safeguard a commercial SDK.

First, minimize external dependencies; prefer pure Kotlin standard library and platform Android APIs wherever possible. Finally, if heavy third-party libraries (like Protocol Buffers or JSON parsers) are mandatory, use **Bytecode Shading / Relocation (via Shadow plugin or Jarjar)** to rename packages (e.g. `com.google.protobuf` -> `com.company.sdk.internal.protobuf`), insulating your SDK from host app version conflicts.


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
