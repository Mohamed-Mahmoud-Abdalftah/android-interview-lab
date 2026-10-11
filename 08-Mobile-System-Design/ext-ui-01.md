---
id: EXT-UI-01
title: UI
module: 08-Mobile-System-Design
tier: Advanced
estimated_minutes: 90
prerequisite_ids: [UI-006]
learning_outcomes:
  - Explain advanced mechanisms without mixing platform layers
  - Diagnose a realistic failure and defend a trade-off
  - Answer specialist follow-ups with evidence boundaries
status: reviewed
code_verification: not_applicable
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/develop/ui/compose/mental-model
  - https://developer.android.com/develop/ui/compose/performance
  - https://developer.android.com/guide/topics/ui/accessibility
  - https://developer.android.com/develop/ui/compose/layouts/adaptive
example_paths: []
question_ids: [EUI-Q001, EUI-Q002, EUI-Q003, EUI-Q004, EUI-Q005, EUI-Q006, EUI-Q007, EUI-Q008, EUI-Q009, EUI-Q010]
---

# EXT-UI-01 — UI deep interview reference

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">UI deep dive تربط rendering pipeline وstate snapshots وlayout/draw وinput/semantics. الأداء والaccessibility والadaptive behavior contracts متداخلة: optimization ماينفعش تكسر focus أو state restoration. ابدأ user journey وقياس frame بدل micro tweak.</p>

## Mechanism and execution trace

<p dir="rtl" lang="ar">ارسم الطبقات والـowners بالترتيب، وحدد contract كل boundary والartifact أو state قبلها وبعدها. بعدين أدخل failure في boundary واحدة وتتبع propagation وcleanup وevidence. ما تنقلش guarantee من JVM لـAndroid أو من client لـserver من غير مصدر واختبار مناسب.</p>

### 1. Frame pipeline

<p dir="rtl" lang="ar">Input, state change, composition, layout, draw, and GPU work contribute different evidence to a slow frame.</p>
### 2. Snapshot state

<p dir="rtl" lang="ar">Compose snapshots coordinate state reads and writes; mutable non-observable data can bypass invalidation.</p>
### 3. Stability contract

<p dir="rtl" lang="ar">Stable means observable public behavior will not change unexpectedly; false annotations can hide updates.</p>
### 4. Custom layout

<p dir="rtl" lang="ar">Measure children under constraints, choose size, and place consistently without repeated expensive work.</p>
### 5. Lazy list identity

<p dir="rtl" lang="ar">Stable keys preserve item identity and state across insertion, removal, and reorder.</p>
### 6. Nested scroll

<p dir="rtl" lang="ar">Coordinate gesture consumption and ownership instead of stacking independent scroll containers blindly.</p>
### 7. Semantics merging

<p dir="rtl" lang="ar">Expose one meaningful control or structured descendants without duplicate announcements.</p>
### 8. Focus restoration

<p dir="rtl" lang="ar">Preserve logical focus across adaptive layout changes and avoid trapping keyboard or accessibility navigation.</p>
### 9. Edge-to-edge

<p dir="rtl" lang="ar">Handle insets by ownership and avoid applying the same inset multiple times.</p>
### 10. UI benchmark

<p dir="rtl" lang="ar">Use macrobenchmark/frame evidence on release-like builds and verify visual and accessibility behavior after optimization.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar">الحل الغلط هو استخدام الاسم أو abstraction كإجابة نهائية من غير lifetime وfailure وsecurity/evidence. التصحيح يبدأ contract صغيرة، يختبر boundary، ويضيف complexity بس لما requirement أو قياس يبررها.</p>

## Tests and failure cases

- Trace valid, malformed, duplicate, stale, cancellation/restart, and boundary-size cases.
- Use release/device/backend evidence for claims outside pure Kotlin.
- Reject one plausible shortcut and explain the invariant it violates.

## Interview explanation

<p dir="rtl" lang="ar"><strong>الإجابة المختصرة:</strong> Input, state change, composition, layout, draw, and GPU work contribute different evidence to a slow frame.</p>

**English:** “Input, state change, composition, layout, draw, and GPU work contribute different evidence to a slow frame. I would trace the ownership and failure boundaries, compare one viable alternative, and verify the claim with the artifact, test, or production signal that actually observes that layer.”

## Senior follow-ups

1. **What assumption is most dangerous?** custom component سريعة بصريًا لكن semantics مفقودة، أو state تضيع لما layout تتحول list-detail.
2. **What evidence belongs to this layer?** Use the actual artifact, controlled test, device trace, or backend record; do not infer across layers.
3. **When would you choose a simpler design?** When scale, durability, or isolation requirements do not justify the added operational cost.

## Misconceptions and revision

<p dir="rtl" lang="ar">راجع الأسئلة EUI-Q001 إلى EUI-Q010. جاوب direct answer ثم mechanism ثم failure ثم test. المحتوى specialist ومش بديل عن vendor/device evidence.</p>
