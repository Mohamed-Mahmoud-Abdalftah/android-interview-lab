---
id: PRO-004
title: Gradle, AGP 9, D8/R8 and signing
module: 06-Production-Engineering
tier: Core
estimated_minutes: 65
prerequisite_ids: [KOT-006]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/build/releases/past-releases/agp-9-0-0-release-notes
  - https://developer.android.com/build/shrink-code
  - https://developer.android.com/studio/build/build-variants
  - https://developer.android.com/studio/publish/app-signing
example_paths: []
question_ids: [PRO-Q016, PRO-Q017, PRO-Q018, PRO-Q019, PRO-Q020]
---

# PRO-004 — Gradle, AGP 9, D8/R8 and signing

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Gradle يحسب task graph، AGP يبني Android variants، Kotlin compiler تنتج bytecode/IR outputs، D8 يحول لـDEX، وR8 يعمل shrinking/optimization/obfuscation حسب pipeline. signing تثبت publisher key مش أمان business logic.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Gradle يحسب task graph، AGP يبني Android variants، Kotlin compiler تنتج bytecode/IR outputs، D8 يحول لـDEX، وR8 يعمل shrinking/optimization/obfuscation حسب pipeline. signing تثبت publisher key مش أمان business logic.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
-keep class ** { *; }
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

```kotlin
-keepclassmembers class * { @com.example.JsonName <fields>; }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Explain source to class files, DEX, packaged artifact, signing, installation, and ART execution without merging the stages.</p>

**English, 20 seconds:** “Explain source to class files, DEX, packaged artifact, signing, installation, and ART execution without merging the stages.”

**English, 60–90 seconds:** “Explain source to class files, DEX, packaged artifact, signing, installation, and ART execution without merging the stages. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig. I would implement this policy: ثبت compatibility من docs، ابن release في CI، اختبر mapping/retrace/startup، واستخدم أضيق keep rules. signing keys خارج repo بصلاحيات محدودة. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Build pipeline under a production failure.** Explain source to class files, DEX, packaged artifact, signing, installation, and ART execution without merging the stages.
2. **Explain Compatibility matrix under a production failure.** Verify Gradle, AGP, Kotlin, JDK, and Compose compiler compatibility from current official tables.
3. **Explain R8 keep rules under a production failure.** Keep reflection or JNI entry points narrowly and verify release behavior plus mapping artifacts.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع PRO-Q016 إلى PRO-Q020، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-038](../Real-World-Scenarios/SCN-038-pro-004-gradle-agp-9-d8-r8-and-signing.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
