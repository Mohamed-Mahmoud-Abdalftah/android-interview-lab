---
id: "LEAD-06"
question: "How do you write an RFC/ADR for a major architecture change?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "B"
phase: 5
priority: "P2"
order: 461
editorial_status: "reviewed"
---

# LEAD-06

## Original interview question

How do you write an RFC/ADR for a major architecture change?

## What the interviewer evaluates

- ADR/RFC structure, decision status and implementation consequences.
- Review/revisit trigger rather than a document that merely declares preference.

## Explanation in Arabic

كيف تكتب وثيقة مقترح معماري (RFC - Request for Comments) أو سجل قرار معماري (ADR - Architecture Decision Record) لتغيير جذري في النظام؟

1. ما هو الفرق بين RFC و ADR؟
   - **RFC (Request for Comments)**: وثيقة **استكشافية ونقاشية مفتوحة** تُطرح قبل اتخاذ القرار لجمع آراء واعتراضات واقتراحات الفريق حول مشكلة كبيرة (مثل: "مقترح الانتقال من Groovy إلى Kotlin DSL و Version Catalogs").
   - **ADR (Architecture Decision Record)**: وثيقة **قصيرة وتوثيقية نهائية** تلخص القرار الذي تم الاستقرار عليه وتاريخه وسياقه والبدائل المرفوضة والآثار المترتبة عليه، وتُحفظ داخل مستودع الكود (`docs/adr/`).

2. الهيكل القياسي لوثيقة الـ RFC/ADR:
   - **1. العنوان والحالة (Title & Status)**: مثل `ADR-004: Migrate Image Loading to Coil` (الحالة: Proposed, Accepted, Superceded).
   - **2. السياق والمشكلة (Context & Problem Statement)**: لماذا نحتاج لهذا التغيير الآن؟ ما هي نقاط الألم في الوضع الحالي؟
   - **3. القرار المقترح (Decision / Proposal)**: الحل الهندسي المختار بالتفصيل.
   - **4. البدائل المدروسة ولماذا تم رفضها (Considered Alternatives)**: مقارنة الخيارات الأخرى (مثلاً مقارنة Coil بـ Glide و Fresco).
   - **5. العواقب والمخاطر والآثار الجانبية (Consequences)**: التأثير على حجم الـ APK، وسرعة البناء، وتكلفة تدريب الفريق.
   - **6. خطة الترحيل المرحلية (Rollout & Migration Plan)**: كيفية الانتقال خطوة بخطوة دون تعطيل الإنتاج.

## Practical walkthrough

قالب حقيقي لوثيقة ADR مصممة لمشروع أندرويد:
```markdown
# ADR-012: Adoption of Jetpack DataStore over SharedPreferences

## Status: Accepted
Date: 2026-03-15 | Author: Mohamed Mahmoud | Approvers: Mobile Core Squad

## Context
`SharedPreferences` causes ANRs on the Main Thread during synchronous `apply()`
and `commit()` disk flushes, and lacks transactional type-safety and reactive
Flow support for real-time preference updates.

## Decision
We will adopt `Proto DataStore` backed by Kotlin Serialization and Coroutines Flow
as the standard key-value and typed configuration storage for the application.

## Consequences
### Positive:
- Asynchronous, non-blocking disk I/O on `Dispatchers.IO` eliminates main-thread ANRs.
- Native Kotlin `Flow` integration simplifies reactive state in ViewModels.
- Proto schemas provide compile-time type safety.

### Negative / Trade-offs:
- Requires writing Protobuf schema files (`.proto`).
- Adds ~40KB to compiled APK size.

## Migration Plan
1. Implement `SharedPreferencesMigration` utility to transfer user data automatically on first launch.
2. Deprecate `LegacyPrefsManager` with a Lint warning.
3. Migrate feature modules incrementally over the next 2 sprints.
```

## Why it matters and how it works

An RFC invites alternatives and unresolved questions; an ADR records accepted decision and why. Both should be concise enough to review, linked to measurable outcomes and versioned with code. Superseding an ADR preserves history.

## Worked example

For offline-first checkout, RFC compares in-memory retry, WorkManager-only and Room outbox plus backend idempotency. ADR chooses outbox, names process-death/duplicate-send tests, server contract and rollback compatibility.

## Trade-offs and decision criteria

Too much documentation delays delivery; too little hides trade-offs. Scale depth to risk and cross-team impact. A one-page ADR may be enough for a localized choice, while a payment protocol change needs more detailed sequence/failure analysis.

## Failure modes

An ADR lacks rejected alternatives, so future team repeats debate; or says “exactly once via WorkManager,” an inaccurate guarantee. Review against implementation and update when assumptions change.

## Production perspective

Keep decision index, owner and review trigger. During rollout compare predicted metrics with actual unknown-payment age and incident rate; supersede decision if evidence changes.

## Interview answer — short

An RFC gathers collaborative team feedback on major architectural proposals before commitment, while an ADR records the accepted decision, rationale, context, rejected alternatives, and consequences within the repository. A strong document clearly defines the problem, contrasts alternatives, states trade-offs, and details an incremental migration plan.

## Interview answer — structured

RFCs and ADRs establish institutional memory and collaborative alignment for significant engineering changes:

1. **RFC vs. ADR Distinction**:
   - **RFC (Request for Comments)**: A collaborative exploration document published early in the ideation cycle to solicit feedback, unearth blind spots, and align cross-functional stakeholders on complex architectural shifts.
   - **ADR (Architecture Decision Record)**: An immutable, version-controlled historical record stored directly in the repository (`/docs/adr/ADR-005.md`) capturing what was decided, why, and what trade-offs were accepted.

2. **Essential Architectural Document Sections**:
   - **Status & Metadata**: (Proposed, Accepted, Deprecated, Superceded) with author and approver timestamps.
   - **Context & Problem Statement**: Explicit business and technical motivations driving the change.
   - **The Decision**: Crisp specification of the chosen architectural pattern, library, or protocol.
   - **Considered Alternatives**: Rigorous comparison table explaining why alternative options were rejected.
   - **Consequences (Positive and Negative)**: Honest accounting of benefits alongside accepted trade-offs (e.g. build time penalties, learning curves).
   - **Staged Migration Plan**: Incremental rollout strategy avoiding big-bang migrations.

## Interview answer — deep senior

From an engineering governance and consensus building angle, leading an RFC requires stakeholder empathy:

1. **The Pre-RFC Socialization Phase**: Never publish a massive 15-page RFC as a surprise to the team. Socialize the core thesis with key senior influencers, platform leads, and QA directors through casual 1-on-1 discussions first. Addressing core anxieties in advance guarantees a constructive, calm public RFC review.

2. **Timeboxing the RFC Lifecycle**: Open-ended architectural debates cause analysis paralysis. Set an explicit deadline (e.g. 10 business days for comments). At the deadline, the technical lead synthesizes feedback, resolves remaining dissenting opinions with a documented rationale, and transitions the RFC into an accepted ADR.

3. **Living ADR Hygiene**: When architectural paradigms evolve (e.g. replacing RxJava with Kotlin Coroutines), do not edit the historical ADR to rewrite the past. Author a new ADR (`ADR-024`) that formally references and **supercedes** the old record (`ADR-003: Supercedes ADR-001`), maintaining an authentic genealogical record of codebase evolution.

## How to answer in the interview

- **Why:** decisions outlive their authors.
- **How:** record context, options, choice and migration.
- **Trade-off:** document cost versus future clarity.
- **Failure case:** pattern name replaces failure analysis.
- **Production solution:** owner, test evidence and rollback trigger.

## Deep-dive talking points

Prompt for RFC versus ADR, alternative evidence, failure table, cross-team signoff and supersession.

## Follow-up questions

- **Interviewer:** "Why should you never edit an existing accepted ADR when technology changes years later?"
  **Answer:** "Because an ADR is an immutable historical record of why a choice was made under past constraints; new choices must be recorded in a new ADR that explicitly supercedes the old one."

- **Interviewer:** "What is the danger of not timeboxing an RFC discussion?"
  **Answer:** "The team enters analysis paralysis, endlessly debating theoretical trade-offs without committing to execution."

## Self-check rubric

Write context, options, decision, consequences and rollback triggers for one architecture ADR; identify stakeholders and evidence that would justify revisiting the decision.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — architectural boundaries.
- [Android offline-first](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable decision example.

Technically reviewed against primary documentation on 2026-10-13.
