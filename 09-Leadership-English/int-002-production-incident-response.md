---
id: INT-002
title: Production incident response
module: 09-Leadership-English
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-004, PRO-005]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://sre.google/sre-book/managing-incidents/
  - https://sre.google/workbook/incident-response/
  - https://developer.android.com/topic/performance/vitals
example_paths: []
question_ids: [INT-Q011, INT-Q012, INT-Q013, INT-Q014, INT-Q015]
---

# INT-002 — Production incident response

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Incident response هدفها تقلل ضرر وتتعلم: detect، scope، mitigate، diagnose، recover، follow-up. severity من user impact مش صوت أعلى شخص. افصل timeline facts عن hypotheses، وخلي owner للقرار والتواصل.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Incident response هدفها تقلل ضرر وتتعلم: detect، scope، mitigate، diagnose، recover، follow-up. severity من user impact مش صوت أعلى شخص. افصل timeline facts عن hypotheses، وخلي owner للقرار والتواصل.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
investigateUntilCertain()
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن.</p>

```kotlin
if (materialRegression && rollbackAvailable) rollback()
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Quantify affected users, functions, versions, geographies, and data/security impact.</p>

**English, 20 seconds:** “Quantify affected users, functions, versions, geographies, and data/security impact.”

**English, 60–90 seconds:** “Quantify affected users, functions, versions, geographies, and data/security impact. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: الفريق يقضي ساعات في root cause بينما crash rate بتزيد وعنده rollback آمن. I would implement this policy: حدد incident commander، rollback/flag حسب threshold، حافظ على evidence، واكتب action items بowner وdeadline وverification. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Severity and scope under a production failure.** Quantify affected users, functions, versions, geographies, and data/security impact.
2. **Explain Mitigation before certainty under a production failure.** Use a reversible rollback or flag when impact is material, while preserving evidence for diagnosis.
3. **Explain Incident roles under a production failure.** One owner coordinates decisions, communications, operations, and a shared factual timeline.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع INT-Q011 إلى INT-Q015، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-047](../Real-World-Scenarios/SCN-047-int-002-production-incident-response.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
