---
id: UI-003
title: Compose effects and lifecycle collection
module: 05-Views-Compose
tier: Core
estimated_minutes: 65
prerequisite_ids: [UI-002, COR-004]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/ui/compose/side-effects
  - https://developer.android.com/develop/ui/compose/lifecycle
  - https://developer.android.com/kotlin/flow/stateflow-and-sharedflow
example_paths: []
question_ids: [UI-Q011, UI-Q012, UI-Q013, UI-Q014, UI-Q015]
---

# UI-003 — Compose effects and lifecycle collection

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Effect API تربط side effect بعمر composition ومفاتيحها. LaunchedEffect تلغي وتعيد التشغيل لما key تتغير. DisposableEffect تعمل cleanup. rememberUpdatedState يسمح effect طويلة تشوف callback حديثة من غير restart. lifecycle collection توقف استهلاك UI حسب owner.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Effect API تربط side effect بعمر composition ومفاتيحها. LaunchedEffect تلغي وتعيد التشغيل لما key تتغير. DisposableEffect تعمل cleanup. rememberUpdatedState يسمح effect طويلة تشوف callback حديثة من غير restart. lifecycle collection توقف استهلاك UI حسب owner.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
LaunchedEffect(Unit) { load(userId) }
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED.</p>

```kotlin
LaunchedEffect(userId) { load(userId) }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Keys define effect identity; a change cancels the old coroutine and starts a new one.</p>

**English, 20 seconds:** “Keys define effect identity; a change cancels the old coroutine and starts a new one.”

**English, 60–90 seconds:** “Keys define effect identity; a change cancels the old coroutine and starts a new one. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED. I would implement this policy: اختار key تمثل identity الحقيقية، افصل producer عن collector، واختبر restart/cleanup مع تغيير key وlifecycle. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain LaunchedEffect keys under a production failure.** Keys define effect identity; a change cancels the old coroutine and starts a new one.
2. **Explain DisposableEffect cleanup under a production failure.** Register and unregister the same observer at a lifecycle-aware boundary.
3. **Explain rememberUpdatedState under a production failure.** Keep a long-lived effect while reading the latest callback or value without an unnecessary restart.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع UI-Q011 إلى UI-Q015، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-033](../Real-World-Scenarios/SCN-033-ui-003-compose-effects-and-lifecycle-collection.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
