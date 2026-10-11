---
id: ARC-005
title: Modules, contracts and ADRs
module: 04-Architecture-DI
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-001, ARC-003]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/modularization
  - https://developer.android.com/topic/architecture
  - https://developer.android.com/topic/architecture/recommendations
example_paths: []
question_ids: [ARC-Q021, ARC-Q022, ARC-Q023, ARC-Q024, ARC-Q025]
---

# ARC-005 — Modules, contracts and ADRs

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">الموديول boundary للownership والاعتماد والبناء، مش folder تجميلي. contract ضيقة تقلل معرفة المستهلك بالتنفيذ. ADR تسجل context والخيارات والقرار والنتائج عشان الفريق يراجع reasoning بدل ما يحفظ النتيجة.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>الموديول boundary للownership والاعتماد والبناء، مش folder تجميلي. contract ضيقة تقلل معرفة المستهلك بالتنفيذ. ADR تسجل context والخيارات والقرار والنتائج عشان الفريق يراجع reasoning بدل ما يحفظ النتيجة.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
featureA -> featureB -> featureA
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل.</p>

```kotlin
featureA -> contracts <- featureB
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> A useful boundary groups code that changes together and exposes a small stable contract.</p>

**English, 20 seconds:** “A useful boundary groups code that changes together and exposes a small stable contract.”

**English, 60–90 seconds:** “A useful boundary groups code that changes together and exposes a small stable contract. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: feature modules متشابكة bidirectional، وكل تعديل يبني التطبيق كله، والـADR تقول استخدمنا Clean Architecture من غير context أو بدائل. I would implement this policy: اقسم حسب change ownership وpublic API، امنع cycles، قِس build graph، واكتب ADR بقرار قابل للنقض وconsequences واضحة. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Module boundary under a production failure.** A useful boundary groups code that changes together and exposes a small stable contract.
2. **Explain Dependency direction under a production failure.** Features depend on contracts or shared foundations, not on each other's internal implementations.
3. **Explain Public API control under a production failure.** Internal implementation stays hidden so refactors do not ripple across the graph.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع ARC-Q021 إلى ARC-Q025، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-030](../Real-World-Scenarios/SCN-030-arc-005-modules-contracts-and-adrs.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
