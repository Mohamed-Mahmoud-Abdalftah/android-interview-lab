---
id: UI-004
title: Navigation ownership and back stack
module: 05-Views-Compose
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-002, UI-002]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/guide/navigation
  - https://developer.android.com/develop/ui/compose/navigation
  - https://developer.android.com/guide/navigation/design
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [UI-Q016, UI-Q017, UI-Q018, UI-Q019, UI-Q020]
---

# UI-004 — Navigation ownership and back stack

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Navigation state لها owner وback stack entries بهويات وsaved state. مرّر IDs صغيرة بدل objects، وحمّل البيانات من source of truth. singleTop/popUpTo يغيروا stack semantics؛ deep links entry points لازم تتختبر زي launcher.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Navigation state لها owner وback stack entries بهويات وsaved state. مرّر IDs صغيرة بدل objects، وحمّل البيانات من source of truth. singleTop/popUpTo يغيروا stack semantics؛ deep links entry points لازم تتختبر زي launcher.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
navigate("detail/$jsonObject")
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death.</p>

```kotlin
navigate(Route.Detail(itemId))
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> The navigation host owns ordered entries; screens should request navigation rather than mutate hidden globals.</p>

**English, 20 seconds:** “The navigation host owns ordered entries; screens should request navigation rather than mutate hidden globals.”

**English, 60–90 seconds:** “The navigation host owns ordered entries; screens should request navigation rather than mutate hidden globals. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: نفس detail route تتضاف مرتين مع نفس ID، أو object كبيرة في arguments تبقى stale بعد process death. I would implement this policy: استخدم typed route contract، validate external routes، قرر singleTop/popUpTo من UX، واختبر Back عبر launch/deep link/notification. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Back-stack ownership under a production failure.** The navigation host owns ordered entries; screens should request navigation rather than mutate hidden globals.
2. **Explain Typed arguments under a production failure.** Pass stable identifiers and reload current data instead of serializing domain objects into routes.
3. **Explain singleTop semantics under a production failure.** singleTop prevents an equal destination at the top, not duplicates elsewhere or stale arguments.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع UI-Q016 إلى UI-Q020، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

حل [LAB-028](../Coding-Challenges/LAB-028-ui-004-navigation-ownership-and-back-stack.md) وراجع الاختبار المرتبط.

حلّل [SCN-034](../Real-World-Scenarios/SCN-034-ui-004-navigation-ownership-and-back-stack.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
