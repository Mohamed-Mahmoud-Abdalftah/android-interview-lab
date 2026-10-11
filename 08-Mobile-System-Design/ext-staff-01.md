---
id: EXT-STAFF-01
title: System design
module: 08-Mobile-System-Design
tier: Advanced
estimated_minutes: 90
prerequisite_ids: [INT-006]
learning_outcomes:
  - Explain advanced mechanisms without mixing platform layers
  - Diagnose a realistic failure and defend a trade-off
  - Answer specialist follow-ups with evidence boundaries
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/architecture
  - https://developer.android.com/topic/modularization
  - https://sre.google/sre-book/service-level-objectives/
example_paths: []
question_ids: [STF-Q001, STF-Q002, STF-Q003, STF-Q004, STF-Q005, STF-Q006, STF-Q007, STF-Q008, STF-Q009, STF-Q010]
---

# EXT-STAFF-01 — System design deep interview reference

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Staff-level design يربط product outcomes وorg ownership وevolution. المطلوب مش أكبر diagram؛ المطلوب seams تقلل blast radius، migration قابلة للرجوع، SLO/observability، وقرار واضح تحت uncertainty. فرّق local optimum عن تكلفة النظام والفريق.</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">ارسم الطبقات والـowners بالترتيب، وحدد contract كل boundary والartifact أو state قبلها وبعدها. بعدين أدخل failure في boundary واحدة وتتبع propagation وcleanup وevidence. ما تنقلش guarantee من JVM لـAndroid أو من client لـserver من غير مصدر واختبار مناسب.</p>

### 1. Requirement shaping

<p dir="rtl" lang="ar">Turn vague scale and reliability claims into measurable user journeys, constraints, and non-goals.</p>
### 2. Architecture evolution

<p dir="rtl" lang="ar">Use seams, strangler migration, compatibility, and rollback instead of a big-bang rewrite.</p>
### 3. Ownership model

<p dir="rtl" lang="ar">Assign decision, operation, data, and incident ownership across team boundaries.</p>
### 4. SLO and error budget

<p dir="rtl" lang="ar">Tie reliability targets to user outcomes and use budget to balance change velocity and risk.</p>
### 5. Blast-radius control

<p dir="rtl" lang="ar">Partition releases, data, accounts, and dependencies so one failure has bounded impact.</p>
### 6. Migration governance

<p dir="rtl" lang="ar">Define dual-read/write risks, reconciliation, cutover criteria, and rollback evidence.</p>
### 7. Platform product thinking

<p dir="rtl" lang="ar">A shared platform needs real consumers, support model, adoption metrics, and escape hatches.</p>
### 8. Decision under uncertainty

<p dir="rtl" lang="ar">State assumptions, reversible probes, leading risks, and the trigger to revisit.</p>
### 9. Cross-team disagreement

<p dir="rtl" lang="ar">Make trade-offs and evidence visible, decide with an owner, and document dissent without paralysis.</p>
### 10. Operational design

<p dir="rtl" lang="ar">Include dashboards, alerts, runbooks, privacy, capacity, failure injection, and deprecation from the start.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar">الحل الغلط هو استخدام الاسم أو abstraction كإجابة نهائية من غير lifetime وfailure وsecurity/evidence. التصحيح يبدأ contract صغيرة، يختبر boundary، ويضيف complexity بس لما requirement أو قياس يبررها.</p>

## Tests and failure cases

- Trace valid, malformed, duplicate, stale, cancellation/restart, and boundary-size cases.
- Use release/device/backend evidence for claims outside pure Kotlin.
- Reject one plausible shortcut and explain the invariant it violates.

## Interview explanation

<p dir="rtl" lang="ar"><strong>الإجابة المختصرة:</strong> Turn vague scale and reliability claims into measurable user journeys, constraints, and non-goals.</p>

**English:** “Turn vague scale and reliability claims into measurable user journeys, constraints, and non-goals. I would trace the ownership and failure boundaries, compare one viable alternative, and verify the claim with the artifact, test, or production signal that actually observes that layer.”

## Senior follow-ups

1. **What assumption is most dangerous?** فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users.
2. **What evidence belongs to this layer?** Use the actual artifact, controlled test, device trace, or backend record; do not infer across layers.
3. **When would you choose a simpler design?** When scale, durability, or isolation requirements do not justify the added operational cost.

## Misconceptions and revision

<p dir="rtl" lang="ar">راجع الأسئلة STF-Q001 إلى STF-Q010. جاوب direct answer ثم mechanism ثم failure ثم test. المحتوى specialist ومش بديل عن vendor/device evidence.</p>
