---
id: SYS-004
title: Offline notes sync design
module: 08-Mobile-System-Design
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-003, PRO-001]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/architecture/data-layer/offline-first
  - https://developer.android.com/training/data-storage/room
  - https://developer.android.com/topic/architecture/data-layer
example_paths: []
question_ids: [SYS-Q016, SYS-Q017, SYS-Q018, SYS-Q019, SYS-Q020]
---

# SYS-004 — Offline notes sync design

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Local database source of truth تخلي UI تقرأ فورًا. writes تتسجل mutation identity/outbox وتتزامن لاحقًا. conflict policy لازم تعتمد على domain: last-write، field merge، version reject، أو user resolution. tombstones مهمة للحذف.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Local database source of truth تخلي UI تقرأ فورًا. writes تتسجل mutation identity/outbox وتتزامن لاحقًا. conflict policy لازم تعتمد على domain: last-write، field merge، version reject، أو user resolution. tombstones مهمة للحذف.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
api.save(note); dao.save(note)
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync.</p>

```kotlin
db.transaction { dao.savePending(note); outbox.enqueue(mutation) }
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> UI observes local canonical state while sync updates it through transactions.</p>

**English, 20 seconds:** “UI observes local canonical state while sync updates it through transactions.”

**English, 60–90 seconds:** “UI observes local canonical state while sync updates it through transactions. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync. I would implement this policy: transaction تجمع local write وoutbox، operation IDs idempotent، versions واضحة، reconcile يحافظ على draft والدليل. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Source of truth under a production failure.** UI observes local canonical state while sync updates it through transactions.
2. **Explain Durable outbox under a production failure.** Persist mutation and local state atomically so process death cannot lose intent.
3. **Explain Conflict policy under a production failure.** Choose per-domain semantics and preserve both evidence and user intent when automatic merge is unsafe.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع SYS-Q016 إلى SYS-Q020، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-043](../Real-World-Scenarios/SCN-043-sys-004-offline-notes-sync-design.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
