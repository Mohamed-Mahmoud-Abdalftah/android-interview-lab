---
id: PRO-002
title: HTTP, timeouts, retries and token refresh
module: 06-Production-Engineering
tier: Core
estimated_minutes: 65
prerequisite_ids: [COR-003, ARC-003]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/training/basics/network-ops/connecting
  - https://square.github.io/okhttp/features/interceptors/
  - https://datatracker.ietf.org/doc/html/rfc9110
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [PRO-Q011, PRO-Q012, PRO-Q013, PRO-Q014, PRO-Q015]
---

# PRO-002 — HTTP, timeouts, retries and token refresh

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">HTTP failure لازم يتصنف: DNS/connect/read timeout، status، parse، cancellation، أو unknown side-effect outcome. retry مش default؛ تحتاج safe/idempotent operation وbackoff/jitter وحد أقصى. token refresh لازم single-flight وتتجنب loops.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>HTTP failure لازم يتصنف: DNS/connect/read timeout، status، parse، cancellation، أو unknown side-effect outcome. retry مش default؛ تحتاج safe/idempotent operation وbackoff/jitter وحد أقصى. token refresh لازم single-flight وتتجنب loops.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
catch (e: Exception) { retry() }
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

```kotlin
retryDecision(method, attempt, status, hasIdempotencyKey)
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Connect, read, call, and application deadlines have different meanings and ownership.</p>

**English, 20 seconds:** “Connect, read, call, and application deadlines have different meanings and ownership.”

**English, 60–90 seconds:** “Connect, read, call, and application deadlines have different meanings and ownership. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين. I would implement this policy: اعمل authenticator/refresh coordinator واحد، idempotency key للside effects، صنّف statuses، واحفظ unknown outcome للمصالحة. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Timeout taxonomy under a production failure.** Connect, read, call, and application deadlines have different meanings and ownership.
2. **Explain Retry safety under a production failure.** Retry only classified transient failures and only when operation semantics are safe or idempotent.
3. **Explain Token refresh single-flight under a production failure.** Concurrent 401 responses share one refresh result and avoid recursive authentication loops.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع PRO-Q011 إلى PRO-Q015، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

حل [LAB-029](../Coding-Challenges/LAB-029-pro-002-http-timeouts-retries-and-token-refresh.md) وراجع الاختبار المرتبط.

حلّل [SCN-037](../Real-World-Scenarios/SCN-037-pro-002-http-timeouts-retries-and-token-refresh.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
