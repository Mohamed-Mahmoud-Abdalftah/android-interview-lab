---
id: ARC-006
title: Revision: architecture code review and DSA
module: 04-Architecture-DI
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-002, ARC-003]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/architecture/recommendations
  - https://developer.android.com/topic/architecture/data-layer
  - https://kotlinlang.org/docs/collections-overview.html
example_paths: []
question_ids: [ARC-Q026, ARC-Q027, ARC-Q028, ARC-Q029, ARC-Q030]
---

# ARC-006 — Revision: architecture code review and DSA

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">مراجعة architecture تبدأ من invariants وdata ownership وfailure path، مش أسماء layers. في DSA نفس المهارة: عرّف contract وinvariant وبعدين اختار structure. الـreview الجيدة تفرّق blocker correctness عن preference.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>مراجعة architecture تبدأ من invariants وdata ownership وfailure path، مش أسماء layers. في DSA نفس المهارة: عرّف contract وinvariant وبعدين اختار structure. الـreview الجيدة تفرّق blocker correctness عن preference.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
// Looks clean, ship it
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.</p>

```kotlin
// Verify owner, failure, conflict, cancellation, and tests
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Trace input, state owner, side effects, failures, and observability before discussing naming.</p>

**English, 20 seconds:** “Trace input, state owner, side effects, failures, and observability before discussing naming.”

**English, 60–90 seconds:** “Trace input, state owner, side effects, failures, and observability before discussing naming. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy. I would implement this policy: اكتب observation وتأثير واقتراح واختبار، واطلب evidence للtrade-off. في live coding اشرح invariant وcomplexity وحدود input. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Architecture review order under a production failure.** Trace input, state owner, side effects, failures, and observability before discussing naming.
2. **Explain Review severity under a production failure.** A blocker protects correctness or security; a suggestion improves maintainability without pretending urgency.
3. **Explain Repository conflict review under a production failure.** Offline writes need durable identity, ordering, retry, and conflict policy before sync implementation details.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع ARC-Q026 إلى ARC-Q030، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-031](../Real-World-Scenarios/SCN-031-arc-006-revision-architecture-code-review-and-dsa.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
