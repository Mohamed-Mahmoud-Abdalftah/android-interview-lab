---
id: ARC-004
title: Hilt scopes, qualifiers and DI tests
module: 04-Architecture-DI
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-003]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/training/dependency-injection/hilt-android
  - https://developer.android.com/training/dependency-injection/hilt-testing
  - https://developer.android.com/training/dependency-injection/hilt-android#component-lifetimes
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [ARC-Q016, ARC-Q017, ARC-Q018, ARC-Q019, ARC-Q020]
---

# ARC-004 — Hilt scopes, qualifiers and DI tests

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">DI بتفصل إنشاء dependencies عن استخدامها، والscope عقد lifetime مش performance annotation. object أقصر عمرًا مينفعش يتخزن جوه owner أطول. qualifier بيفرق bindings من نفس type، والاختبار لازم يقدر يستبدل boundary من غير service locator خفي.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>DI بتفصل إنشاء dependencies عن استخدامها، والscope عقد lifetime مش performance annotation. object أقصر عمرًا مينفعش يتخزن جوه owner أطول. qualifier بيفرق bindings من نفس type، والاختبار لازم يقدر يستبدل boundary من غير service locator خفي.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
@Singleton class SessionCache(var userId: String)
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test.</p>

```kotlin
@ActivityRetainedScoped class SessionOwner @Inject constructor()
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state.</p>

**English, 20 seconds:** “Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state.”

**English, 60–90 seconds:** “Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: Singleton ماسكة session/user object فتسرّب بيانات حساب قديم بعد logout، أو binding غلط توصل production endpoint في test. I would implement this policy: ارسم ownership graph، اختار أضيق scope تحقق المشاركة المطلوبة، استخدم qualifiers بأسماء معنى، واختبر replacement والlogout/recreation. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Hilt component lifetimes under a production failure.** Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state.
2. **Explain Qualifier design under a production failure.** Qualifiers distinguish semantic bindings such as Authenticated and Public clients, not arbitrary implementation names.
3. **Explain Accidental singleton session under a production failure.** Logout must invalidate account state; process-wide caches need keys or explicit clearing and must not capture screen owners.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع ARC-Q016 إلى ARC-Q020، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

حل [LAB-026](../Coding-Challenges/LAB-026-arc-004-hilt-scopes-qualifiers-and-di-tests.md) وراجع الاختبار المرتبط.

حلّل [SCN-029](../Real-World-Scenarios/SCN-029-arc-004-hilt-scopes-qualifiers-and-di-tests.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
