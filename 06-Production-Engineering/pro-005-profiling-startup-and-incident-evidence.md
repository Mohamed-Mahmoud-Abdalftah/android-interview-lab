---
id: PRO-005
title: Profiling, startup and incident evidence
module: 06-Production-Engineering
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-004]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview
  - https://developer.android.com/topic/performance/tracing
  - https://developer.android.com/topic/performance/vitals/render
  - https://developer.android.com/topic/performance/baselineprofiles/overview
example_paths: []
question_ids: [PRO-Q021, PRO-Q022, PRO-Q023, PRO-Q024, PRO-Q025]
---

# PRO-005 — Profiling, startup and incident evidence

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">ابدأ metric وscenario وbuild قبل profiler. startup cold/warm/hot لهم definitions مختلفة، وjank frame deadlines، والذاكرة تشمل allocation/retention. incident evidence لازم تربط version/cohort/timeline من غير PII.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>ابدأ metric وscenario وbuild قبل profiler. startup cold/warm/hot لهم definitions مختلفة، وjank frame deadlines، والذاكرة تشمل allocation/retention. incident evidence لازم تربط version/cohort/timeline من غير PII.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم Macrobenchmark/Perfetto/profileable release-like build، قارن distributions وbaseline، وحدد rollback threshold قبل rollout.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
measureDebugOnce()
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression.</p>

```kotlin
benchmarkReleaseLike(iterations = 20, startupMode = COLD)
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم Macrobenchmark/Perfetto/profileable release-like build، قارن distributions وbaseline، وحدد rollback threshold قبل rollout. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم Macrobenchmark/Perfetto/profileable release-like build، قارن distributions وbaseline، وحدد rollback threshold قبل rollout. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> Name the user journey, metric, percentile, device class, build, and competing cause before collecting data.</p>

**English, 20 seconds:** “Name the user journey, metric, percentile, device class, build, and competing cause before collecting data.”

**English, 60–90 seconds:** “Name the user journey, metric, percentile, device class, build, and competing cause before collecting data. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: debug profile تقيلة اتاخدت مرة واتعممت على release، أو average startup خبت tail regression. I would implement this policy: استخدم Macrobenchmark/Perfetto/profileable release-like build، قارن distributions وbaseline، وحدد rollback threshold قبل rollout. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Measurement question under a production failure.** Name the user journey, metric, percentile, device class, build, and competing cause before collecting data.
2. **Explain Startup modes under a production failure.** Cold creates process, warm may reuse process, and hot reuses Activity; compare matching scenarios.
3. **Explain Perfetto trace reading under a production failure.** Follow main thread, binder, I/O, scheduling, and frames in one timeline rather than isolated logs.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع PRO-Q021 إلى PRO-Q025، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-039](../Real-World-Scenarios/SCN-039-pro-005-profiling-startup-and-incident-evidence.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
