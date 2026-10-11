---
id: SYS-006
title: Revision: design review and concurrency
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 65
prerequisite_ids: [SYS-001, SYS-004]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/architecture
  - https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html
example_paths: []
question_ids: [SYS-Q026, SYS-Q027, SYS-Q028, SYS-Q029, SYS-Q030]
---

# SYS-006 — Revision: design review and concurrency

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">System design interview تبدأ requirements وscale/failure/privacy، ثم state owners وAPIs/data flow، وبعدها alternatives. concurrency review تحدد shared state وatomic boundary وordering بدل قول thread-safe عامة.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>System design interview تبدأ requirements وscale/failure/privacy، ثم state owners وAPIs/data flow، وبعدها alternatives. concurrency review تحدد shared state وatomic boundary وordering بدل قول thread-safe عامة.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
synchronized(lock) { remote.call() }
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy.</p>

```kotlin
val decision = mutex.withLock { readAndReserve() }; remote.call(decision)
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Clarify users, latency, offline, consistency, privacy, abuse, and failure priorities before components.</p>

**English, 20 seconds:** “Clarify users, latency, offline, consistency, privacy, abuse, and failure priorities before components.”

**English, 60–90 seconds:** “Clarify users, latency, offline, consistency, privacy, abuse, and failure priorities before components. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: مرشح يرسم boxes من غير offline/auth/failure، أو يضيف lock حول network call فيعمل convoy. I would implement this policy: قدّم design أساسي وبديل، اذكر bottleneck/rollout/observability، واستخدم serialization أو atomic DB transaction عند boundary الصحيحة. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Requirement discovery under a production failure.** Clarify users, latency, offline, consistency, privacy, abuse, and failure priorities before components.
2. **Explain State ownership under a production failure.** Every mutable state has one authority, update path, persistence level, and conflict policy.
3. **Explain Concurrency boundary under a production failure.** Protect the smallest shared transition and avoid holding locks across slow external work.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع SYS-Q026 إلى SYS-Q030، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-045](../Real-World-Scenarios/SCN-045-sys-006-revision-design-review-and-concurrency.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
