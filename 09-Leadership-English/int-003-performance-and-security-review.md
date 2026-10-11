---
id: INT-003
title: Performance and security review
module: 09-Leadership-English
tier: Core
estimated_minutes: 65
prerequisite_ids: [PRO-003, PRO-005]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://owasp.org/www-project-mobile-application-security/
  - https://developer.android.com/privacy-and-security/keystore
  - https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview
example_paths: []
question_ids: [INT-Q016, INT-Q017, INT-Q018, INT-Q019, INT-Q020]
---

# INT-003 — Performance and security review

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Senior review ترتب المخاطر من evidence وتأثير واحتمال. performance optimization من baseline، security من assets/trust boundaries/abuse. ما تخلطش secret obfuscation بتفويض server.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Senior review ترتب المخاطر من evidence وتأثير واحتمال. performance optimization من baseline، security من assets/trust boundaries/abuse. ما تخلطش secret obfuscation بتفويض server.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
val key = "hardcoded-secret"
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK.</p>

```kotlin
val keyAlias = keystoreBackedAlias
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Rank by user impact, exploitability or frequency, evidence confidence, and reversibility.</p>

**English, 20 seconds:** “Rank by user impact, exploitability or frequency, evidence confidence, and reversibility.”

**English, 60–90 seconds:** “Rank by user impact, exploitability or frequency, evidence confidence, and reversibility. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: الفريق يسرّع startup بإزالة auth check، أو يشفر token بمفتاح ثابت داخل APK. I would implement this policy: اعمل threat/performance budgets، اختبر release-like، أصلح أعلى risk، وحط regression gate وrollout monitoring. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Risk prioritization under a production failure.** Rank by user impact, exploitability or frequency, evidence confidence, and reversibility.
2. **Explain Trust boundaries under a production failure.** Map external intents, network, storage, IPC, WebView, vendor SDKs, and backend authority.
3. **Explain Release-like performance under a production failure.** Measure representative journeys and percentiles on controlled release builds.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع INT-Q016 إلى INT-Q020، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-048](../Real-World-Scenarios/SCN-048-int-003-performance-and-security-review.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
