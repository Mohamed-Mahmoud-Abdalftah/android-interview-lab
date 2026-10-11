---
id: UI-005
title: Adaptive UI, RTL, a11y and performance
module: 05-Views-Compose
tier: Core
estimated_minutes: 65
prerequisite_ids: [UI-001, UI-002]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/ui/compose/layouts/adaptive
  - https://developer.android.com/guide/topics/ui/accessibility
  - https://developer.android.com/develop/ui/compose/performance
  - https://developer.android.com/guide/topics/resources/localization
example_paths: []
question_ids: [UI-Q021, UI-Q022, UI-Q023, UI-Q024, UI-Q025]
---

# UI-005 — Adaptive UI, RTL, a11y and performance

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Adaptive UI تتصرف حسب available space/posture مش اسم الجهاز. RTL تحتاج logical start/end وعزل code LTR. accessibility contract تشمل semantics وfocus وtouch target وfont scale. الأداء يقاس frames ومراحل العمل، مش إحساس المطور.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Adaptive UI تتصرف حسب available space/posture مش اسم الجهاز. RTL تحتاج logical start/end وعزل code LTR. accessibility contract تشمل semantics وfocus وtouch target وfont scale. الأداء يقاس frames ومراحل العمل، مش إحساس المطور.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
Modifier.padding(left = 16.dp)
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes.</p>

```kotlin
Modifier.padding(start = 16.dp)
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Choose layouts from available window space and content needs, preserving state across layout changes.</p>

**English, 20 seconds:** “Choose layouts from available window space and content needs, preserving state across layout changes.”

**English, 60–90 seconds:** “Choose layouts from available window space and content needs, preserving state across layout changes. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: layout ثابتة تنهار عند 200% font، icon اتجاهها غلط في RTL، أو تحسين يخفي semantics عشان يقلل nodes. I would implement this policy: اختبر window sizes وRTL/font scale/TalkBack، استخدم semantics meaningful، وقِس jank قبل وبعد على build ممثلة. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Adaptive breakpoints under a production failure.** Choose layouts from available window space and content needs, preserving state across layout changes.
2. **Explain RTL correctness under a production failure.** Use logical directions and isolate code, numbers, and icons whose meaning is directional.
3. **Explain Accessibility semantics under a production failure.** Expose role, label, state, action, focus order, and sufficiently large targets without duplicate noise.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع UI-Q021 إلى UI-Q025، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-035](../Real-World-Scenarios/SCN-035-ui-005-adaptive-ui-rtl-a11y-and-performance.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
