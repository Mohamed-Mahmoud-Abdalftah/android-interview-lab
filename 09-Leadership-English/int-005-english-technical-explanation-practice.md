---
id: INT-005
title: English technical explanation practice
module: 09-Leadership-English
tier: Core
estimated_minutes: 65
prerequisite_ids: [KOT-001]
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
  - https://kotlinlang.org/docs/coroutines-overview.html
example_paths: []
question_ids: [INT-Q021, INT-Q022, INT-Q023, INT-Q024, INT-Q025]
---

# INT-005 — English technical explanation practice

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">الإجابة القوية لها structure: direct answer، mechanism، example، trade-off، evidence. English البسيطة الدقيقة أحسن من vocabulary كبيرة مبهمة. لو مش عارف، حدّد known/unknown وخطة تحقق.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>الإجابة القوية لها structure: direct answer، mechanism، example، trade-off، evidence. English البسيطة الدقيقة أحسن من vocabulary كبيرة مبهمة. لو مش عارف، حدّد known/unknown وخطة تحقق.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
It depends... [five minutes later]
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية.</p>

```kotlin
My default is X because Y. I would choose Z when condition C changes.
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Give the decision and one reason without losing the key boundary.</p>

**English, 20 seconds:** “Give the decision and one reason without losing the key boundary.”

**English, 60–90 seconds:** “Give the decision and one reason without losing the key boundary. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: إجابة خمس دقايق تبدأ تاريخ الموضوع ومتوصلش للقرار، أو ادعاء أرقام وخبرة مش حقيقية. I would implement this policy: استخدم 20/90/180 ثانية، سجل نفسك، شيل filler، وراجع هل جاوبت السؤال وقلت assumptions. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Twenty-second answer under a production failure.** Give the decision and one reason without losing the key boundary.
2. **Explain Ninety-second depth under a production failure.** Add mechanism, concrete example, failure path, and trade-off.
3. **Explain Clarifying questions under a production failure.** Ask about scale, lifetime, consistency, and constraints before overcommitting.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع INT-Q021 إلى INT-Q025، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-049](../Real-World-Scenarios/SCN-049-int-005-english-technical-explanation-practice.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
