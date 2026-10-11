---
id: SYS-005
title: Messaging and realtime tracking design
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 65
prerequisite_ids: [COR-004, PRO-002, SYS-004]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/background-work/background-tasks
  - https://firebase.google.com/docs/cloud-messaging/concept-options
  - https://developer.android.com/topic/architecture/data-layer/offline-first
example_paths: []
question_ids: [SYS-Q021, SYS-Q022, SYS-Q023, SYS-Q024, SYS-Q025]
---

# SYS-005 — Messaging and realtime tracking design

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Realtime mobile design تجمع push كwake hint، socket/stream أثناء foreground، REST catch-up، local ordered store، وserver sequence. delivery قد تتكرر وتتأخر وتتقطع؛ exactly-once end-to-end ادعاء محتاج تضييق شديد.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Realtime mobile design تجمع push كwake hint، socket/stream أثناء foreground، REST catch-up، local ordered store، وserver sequence. delivery قد تتكرر وتتأخر وتتقطع؛ exactly-once end-to-end ادعاء محتاج تضييق شديد.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
onPush { append(payload.message) }
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

```kotlin
onSignal { syncAfter(lastServerSequence) }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> A push is a delivery hint; fetch or reconcile canonical data and handle duplicates.</p>

**English, 20 seconds:** “A push is a delivery hint; fetch or reconcile canonical data and handle duplicates.”

**English, 60–90 seconds:** “A push is a delivery hint; fetch or reconcile canonical data and handle duplicates. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل. I would implement this policy: استخدم event IDs/sequence، dedupe، gap detection، bounded reconnect، presence/freshness، وprivacy/retention للlocation. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Push as signal under a production failure.** A push is a delivery hint; fetch or reconcile canonical data and handle duplicates.
2. **Explain Ordering and gaps under a production failure.** Use server sequence or cursor, detect gaps, and backfill before presenting a complete history.
3. **Explain Reconnect policy under a production failure.** Backoff with jitter, network awareness, token refresh, and one active connection owner.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع SYS-Q021 إلى SYS-Q025، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-044](../Real-World-Scenarios/SCN-044-sys-005-messaging-and-realtime-tracking-design.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
