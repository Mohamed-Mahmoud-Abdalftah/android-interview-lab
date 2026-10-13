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

Android library غالبًا تنتج AAR، لكن release ليست ملف AAR وحده: public API، dependency metadata، resources/manifest merge، consumer R8 rules، minSdk ونسخ التوافق كلها عقود للمستهلك. اختبر logic على JVM، platform behavior على جهاز/محاكي، ثم sample consumer app يبني debug/release مع minification للتأكد من التبعيات والـmanifest/keep rules. انشر artifact وmetadata عبر Gradle publishing إلى repository موثوق، وثبت version semantic قدر الإمكان، واحتفظ بrelease notes وchecksums/signing إن لزم.

## Practical walkthrough

Android library reusable تحتاج public API واضح، consumer R8 rules، manifest merging آمن، versioning وsample consumer minified build. اختبر Kotlin/JVM logic، instrumentation للAndroid contract، وخروج AAR/Maven metadata. SDK يملك transitive deps بحذر، وينشر changelog وmigration. لا تعتبر module tests وحدها إثبات compatibility مع app حقيقية.

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

“I test an Android library in isolation and in a separate consuming app, including minified release, then publish AAR plus correct metadata and versioned API contract.”

## Interview answer — structured

“I define the SDK's public API and supported Android/AGP range, then run JVM logic tests and device tests for platform behavior. A separate consumer app resolves the published AAR, builds release with R8, validates manifest merge and exercises key flows. I review consumer keep rules and `api` dependencies, check binary/API changes, and publish with reproducible version, metadata and release notes. Internal module tests alone cannot prove consumer integration.”

## Interview answer — deep senior

“A reusable Android library is a product boundary. Its AAR contains code, resources and manifest contributions, but consumers also rely on dependency metadata, public ABI, minimum platform support and behavior under shrinking. I test the core logic on the JVM and Android-specific paths on devices, then build a separate sample consumer from the artifact as it will actually be published. That catches a dependency accidentally declared internal although its type appears in the API, a conflicting provider authority, or R8 removing a class accessed through reflection. I run both debug and minified release variants, inspect the merged manifest and consumer rules, and consider binary/API compatibility when bumping versions. The publishing pipeline records artifact hashes and source revision, uses protected credentials, and verifies the artifact can be fetched from the target repository. Release notes cover behavioral and migration changes, not just version numbers. I avoid a huge public surface because every exposed type becomes a compatibility obligation. If a bug is found, consumers need a clear fixed version or deprecation path rather than a silently replaced artifact.”

## How to answer in the interview

- **Why:** library contract extends beyond source code.
- **How:** test AAR consumer and release shrinker.
- **Trade-off:** stable API versus evolution freedom.
- **Failure case:** consumer strips reflected class.
- **Production solution:** publish sample and binary compatibility checks.

## Deep-dive talking points

Discuss AAR/metadata, public ABI, consumerProguardFiles, manifest merge, sample app, provenance and versioning.

## Follow-up questions

- Why build a separate consumer app? **Answer:** it exercises published metadata, API visibility and integration behavior missing from internal tests.
- What release-only risk does R8 introduce? **Answer:** reflective/JNI/serialization entry points can be removed or renamed without correct rules.
- Does an AAR alone describe dependencies? **Answer:** no; publication metadata is needed for transitive dependency resolution.

## Self-check rubric

Name artifact contracts, test layers, a release-only failure, and publishing verification.

## References and reviewed-on date

- [Create an Android library](https://developer.android.com/studio/projects/android-library) — AAR and module behavior.
- [Gradle Maven publishing](https://docs.gradle.org/current/userguide/publishing_maven.html) — artifact metadata.
- [R8 and library keep rules](https://developer.android.com/topic/performance/app-optimization/library-optimization) — consumer configuration.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. SDK compatibility policy is project-specific.
