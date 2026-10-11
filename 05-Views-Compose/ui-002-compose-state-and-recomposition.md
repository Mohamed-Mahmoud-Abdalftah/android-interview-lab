---
id: UI-002
title: Compose state and recomposition
module: 05-Views-Compose
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-002]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/ui/compose/state
  - https://developer.android.com/develop/ui/compose/mental-model
  - https://developer.android.com/develop/ui/compose/performance/stability
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [UI-Q006, UI-Q007, UI-Q008, UI-Q009, UI-Q010]
---

# UI-002 — Compose state and recomposition

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Composition تصف UI من state؛ recomposition تعيد تنفيذ composables اللي قرأت state اتغيرت، ومش معناها إعادة رسم كل الشاشة. state hoisting يفصل value وevents، والاستقرار يؤثر على إمكانية skip لكنه مش هدف يتزور بـannotations.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Composition تصف UI من state؛ recomposition تعيد تنفيذ composables اللي قرأت state اتغيرت، ومش معناها إعادة رسم كل الشاشة. state hoisting يفصل value وevents، والاستقرار يؤثر على إمكانية skip لكنه مش هدف يتزور بـannotations.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
items.add(newItem) // same unobserved mutable list
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition.</p>

```kotlin
items = items + newItem // publish a new immutable state
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Compose tracks observable state reads and schedules affected scopes when values change.</p>

**English, 20 seconds:** “Compose tracks observable state reads and schedules affected scopes when values change.”

**English, 60–90 seconds:** “Compose tracks observable state reads and schedules affected scopes when values change. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. I would implement this policy: استخدم immutable observable state، ارفعها لأقرب owner مشترك، خلي composition بلا side effects، وقِس recomposition قبل optimization. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain State reads and invalidation under a production failure.** Compose tracks observable state reads and schedules affected scopes when values change.
2. **Explain State hoisting under a production failure.** Hoist state as value plus events to the lowest common owner that needs coordination.
3. **Explain Immutable collections under a production failure.** Publishing immutable snapshots makes equality and change ownership auditable.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع UI-Q006 إلى UI-Q010، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

حل [LAB-027](../Coding-Challenges/LAB-027-ui-002-compose-state-and-recomposition.md) وراجع الاختبار المرتبط.

حلّل [SCN-032](../Real-World-Scenarios/SCN-032-ui-002-compose-state-and-recomposition.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
