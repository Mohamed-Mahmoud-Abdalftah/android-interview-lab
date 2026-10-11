---
id: UI-006
title: Revision: UI tests and DSA
module: 05-Views-Compose
tier: Core
estimated_minutes: 65
prerequisite_ids: [UI-002, UI-005]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/ui/compose/testing
  - https://developer.android.com/training/testing/fundamentals
  - https://kotlinlang.org/docs/collections-overview.html
example_paths: []
question_ids: [UI-Q026, UI-Q027, UI-Q028, UI-Q029, UI-Q030]
---

# UI-006 — Revision: UI tests and DSA

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">UI test تختبر behavior من semantics/user surface، unit test تختبر reducer، screenshot تختبر pixels ضمن حدود. اختار أقل طبقة تثبت الخطر. DSA sliding window تحتاج invariant عن محتوى النافذة، مش nested loops مخفية.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>UI test تختبر behavior من semantics/user surface، unit test تختبر reducer، screenshot تختبر pixels ضمن حدود. اختار أقل طبقة تثبت الخطر. DSA sliding window تحتاج invariant عن محتوى النافذة، مش nested loops مخفية.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
Thread.sleep(1000); onNodeWithText("Done")
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof.</p>

```kotlin
injectState(Success); onNodeWithTag(RESULT).assertIsDisplayed()
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Put pure state transitions in unit tests and reserve device tests for framework and user integration.</p>

**English, 20 seconds:** “Put pure state transitions in unit tests and reserve device tests for framework and user integration.”

**English, 60–90 seconds:** “Put pure state transitions in unit tests and reserve device tests for framework and user integration. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: اختبار يعتمد على text متغيرة وترتيب زمني وsleep، أو screenshot تعتبر accessibility proof. I would implement this policy: استخدم stable semantics بحذر، controlled state، idling/scheduler مناسب، واختبر reducer سريعًا ثم journey حرجة على Android. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain UI test pyramid under a production failure.** Put pure state transitions in unit tests and reserve device tests for framework and user integration.
2. **Explain Semantics selectors under a production failure.** Select by stable meaning, not incidental layout hierarchy or translated display text.
3. **Explain Accessibility assertions under a production failure.** Semantics tests catch labels and actions, while TalkBack and visual checks cover additional behavior.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع UI-Q026 إلى UI-Q030، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-036](../Real-World-Scenarios/SCN-036-ui-006-revision-ui-tests-and-dsa.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
