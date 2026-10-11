---
id: INT-001
title: Capstone integration and tests
module: 09-Leadership-English
tier: Core
estimated_minutes: 65
prerequisite_ids: [ARC-005, UI-006, PRO-006]
learning_outcomes:
  - Explain the contract from first principles in Egyptian Arabic
  - Trace a production failure and reject a tempting wrong fix
  - Give concise and deep spoken interview answers
  - Design relevant tests and state the evidence boundary
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/architecture/recommendations
  - https://developer.android.com/topic/architecture/data-layer/offline-first
  - https://developer.android.com/training/testing/fundamentals
example_paths: []
question_ids: [INT-Q006, INT-Q007, INT-Q008, INT-Q009, INT-Q010]
---

# INT-001 — Capstone integration and tests

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation. السؤال في المقابلة هيضغط على السبب، الـtrade-off، وإزاي تثبت إن الإصلاح صح؛ اسم pattern لوحده مش إجابة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Capstone تجمع offline notes: UI state holder، repository/local source، outbox worker، auth session، sync conflict، وobservability. integration معناها contracts تتوصل وتفشل بوضوح، مش كل classes في module واحدة.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">ارسم input وstate owner والـboundary والoutput. حدد إيه guarantee موثقة وإيه implementation detail. لو في side effect خارجي، اكتب identity وretry/ordering policy؛ لو في UI أو process lifetime، اكتب restoration/cancellation path.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>التتبع</th></tr></thead><tbody><tr><td>1</td><td>حدد المالك والـinput والعقد قبل اختيار pattern.</td></tr><tr><td>2</td><td>Capstone تجمع offline notes: UI state holder، repository/local source، outbox worker، auth session، sync conflict، وobservability. integration معناها contracts تتوصل وتفشل بوضوح، مش كل classes في module واحدة.</td></tr><tr><td>3</td><td>اكسر happy path بالـfailure الأساسية: save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</td></tr><tr><td>4</td><td>طبّق القرار واكتب evidence: عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح.</td></tr></tbody></table>

## مثال بسيط وProduction حقيقي

```kotlin
state = Saved; repository.save(note)
```

<p dir="rtl" lang="ar"><strong>ليه غلط:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

```kotlin
repository.saveDurably(note); state = SavedPendingSync
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح. في production أضف operation identity وprivacy-safe observability وrollback signal مناسبين للموضوع.</p>

## Wrong and corrected implementation — Code review

<p dir="rtl" lang="ar">راجع الكود على خمس محاور: ownership، ordering، failure، cancellation/restoration، وtestability. متقبلش catch واسع أو global mutable state أو retry غير محدودة كحل سريع. اطلب test تفشل على النسخة الغلط وتنجح على contract المصححة.</p>

## إمتى أستخدمه وإمتى لأ؟ — Alternatives and trade-offs

<p dir="rtl" lang="ar">عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح. قارن البديل الأبسط، تكلفة التشغيل والصيانة، وسلوك الفشل. القرار يتغير لو durability أو consistency أو privacy أو latency requirement اتغيرت؛ قول الشرط اللي يخليك تغيّر رأيك.</p>

## Tests and failure cases

- Happy path plus the first intermediate state.
- The named production failure with controlled inputs.
- Duplicate, stale, malformed, cancellation, and process/restart cases where relevant.
- A negative test for the tempting wrong implementation.
- Device or integration evidence for claims that a pure JVM model cannot prove.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة 20 ثانية:</strong> UI sends intent, repository commits local truth, outbox syncs, and session scopes account data.</p>

**English, 20 seconds:** “UI sends intent, repository commits local truth, outbox syncs, and session scopes account data.”

**English, 60–90 seconds:** “UI sends intent, repository commits local truth, outbox syncs, and session scopes account data. My design starts from ownership and the required guarantee. I trace the normal path, then force the main failure: save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation. I would implement this policy: عرّف end-to-end acceptance paths، اختبر pure + database + worker contracts، وسجل Android SDK blocker بوضوح. Finally, I would add a regression test at the narrowest boundary and an integration or rollout signal for behavior that the local JVM suite cannot prove.”

## Senior follow-ups

1. **Explain Capstone boundaries under a production failure.** UI sends intent, repository commits local truth, outbox syncs, and session scopes account data.
2. **Explain Test portfolio under a production failure.** Use reducer unit tests, persistence migration tests, worker integration, and UI journeys for distinct risks.
3. **Explain Failure injection under a production failure.** Force process death, network loss, conflict, account switch, duplicate work, and stale completion.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">الـmisconception الأساسية إن اسم الـAPI أو الـpattern يضمن correctness. راجع INT-Q006 إلى INT-Q010، جاوب من غير فتح model answer، وبعدها قارن contract والfailure والevidence. المصادر الرسمية متراجعة بتاريخ 2026-10-11.</p>

اكتب test matrix وحدد بوضوح ما يحتاج Android/device evidence.

حلّل [SCN-046](../Real-World-Scenarios/SCN-046-int-001-capstone-integration-and-tests.md).

**Evidence limit:** `tested` means the linked pure Kotlin contract ran on JVM. Android, device, backend, and production claims remain integration evidence, not inferred success.
