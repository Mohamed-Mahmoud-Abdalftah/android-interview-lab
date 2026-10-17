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

## Concept and technical explanation

Governing large-scale technical evolutions through Requests for Comments (RFCs) and Architecture Decision Records (ADRs) ensures asynchronous alignment, structured evaluation, and durable institutional memory:
- RFC vs ADR Distinction:
  - Request for Comments (RFC): A collaborative, exploratory document used *before* a decision is finalized to solicit feedback, explore alternatives, align cross-functional teams, and establish consensus.
  - Architecture Decision Record (ADR): An immutable, version-controlled document capturing a *finalized* architectural choice, recording the context, decision, consequences, and compliance requirements for future engineers.
- Anatomy of a Production-Grade RFC:
  1. Summary & Problem Statement: Clear, jargon-free explanation of the architectural bottleneck and business impact.
  2. Goals vs Non-Goals: Explicit boundary setting to prevent scope creep (e.g., "Goal: Migrate network layer to Ktor; Non-Goal: Rewrite the UI in Compose").
  3. Proposed Architecture & System Design: Class diagrams, data flow models, and concrete Kotlin API contracts.
  4. Alternatives Considered & Rejected: Objective analysis of competing options and explicit rationale for why they were dismissed.
  5. Migration, Rollout, and Rollback Plan: Phased rollout steps, feature-flag mechanics, deprecation schedules, and backout triggers.
  6. Security, Privacy, and Performance Impact: Metrics, memory implications, cold-start latency, and battery impact.
- The Michael Nygard ADR Schema:
  - Context -> Decision -> Status (Proposed, Accepted, Deprecated, Superseded) -> Consequences (Positive, Negative, Neutral).

## Practical walkthrough (English)

Standard Architecture Decision Record (ADR) template in Markdown:
```markdown
# ADR-007: Migration from Legacy XML View System to Jetpack Compose

## Status
Accepted (Date: 2026-10-17)

## Context
Our Android application currently uses a mixed View-binding and Data-binding XML architecture.
Fragment rendering benchmarks show high view-inflation latencies (averaging 42ms on budget devices).
Furthermore, maintaining duplicate UI state between custom views and ViewModels has caused 28% of our UI state synchronization bugs over the past two quarters.
Google has transitioned modern Android UI development to Jetpack Compose.

## Decision
We will adopt Jetpack Compose for all new feature development and migrate existing high-churn screens opportunistically during planned redesigns.
We strictly prohibit writing new XML layout files starting with Sprint 42.

## Consequences
### Positive
- Declarative unidirectional data flow directly consuming ViewModel StateFlow.
- Measured 35% reduction in UI boilerplate code.
- Eliminates fragment view-inflation overhead, reducing screen transition jank.

### Negative / Accepted Trade-offs
- Cold startup time increases slightly (~80ms) due to Compose runtime classloading; mitigated via Baseline Profiles.
- Team learning curve requires 3 internal training brown bags on recomposition optimization.

## Reversal / Exit Criteria
If Compose runtime regressions cause crash-free sessions to dip below 99.8% on low-end Android Go hardware and cannot be resolved within 30 days, new screen migration will pause and fall back to classic Views.
```

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

Write an RFC before a decision to build consensus by defining goals, non-goals, proposed designs, rejected alternatives, and rollback plans. Once agreed, capture the outcome in an immutable ADR detailing context, status, consequences, and accepted trade-offs, preserving institutional memory in Git.

## Interview answer — structured

Driving major architectural changes successfully requires structured technical documentation through RFCs and ADRs.
An RFC, or Request for Comments, is authored before a decision is finalized. It frames the problem statement, defines explicit goals and non-goals to prevent scope creep, presents the proposed architecture with concrete Kotlin contracts, and thoroughly evaluates rejected alternatives. Crucially, it outlines a phased migration and rollback plan.
Once the engineering team reaches consensus, the decision is immortalized as an Architecture Decision Record, or ADR.
Following the Nygard template, an ADR is an immutable document committed to Git. It records the organizational context, the decision taken, its current status, and both positive and negative consequences.
This disciplined workflow transforms subjective architectural debates into collaborative engineering reviews while ensuring that future team members understand the mechanical rationale and trade-offs behind foundational decisions.

## Interview answer — deep senior

From an engineering governance, distributed organization scaling, and technical strategy perspective, RFCs and ADRs are essential instruments for establishing architectural velocity and institutional memory.
In growing engineering teams, architectural decisions made in informal chats or private meetings create organizational misalignment, duplicate efforts, and toxic debates when new engineers join and wonder why a legacy choice was made. Senior leaders eliminate this dysfunction by institutionalizing asynchronous decision-making.
The process begins with an RFC. A well-crafted RFC is rigorous and concise. It leads with a sharp problem statement and draws strict boundaries via Goals and Non-Goals.
It provides comprehensive architectural diagrams and illustrative Kotlin code snippets, allowing reviewers to evaluate the ergonomic developer experience.
A vital section is Alternatives Considered: if you propose adopting Ktor, you must document why Retrofit, OkHttp, and gRPC were evaluated and rejected. The RFC must specify the migration strategy, demonstrating how the system will transition incrementally without breaking production releases, supported by feature flags and automated metric alarms.
Once the RFC review window concludes and stakeholders align, the outcome is recorded as an Architecture Decision Record in the repository docs/adr directory.
Using the classic Nygard structure, the ADR captures the immutable snapshot: context, decision, and balanced consequences, explicitly recording accepted liabilities such as build time penalties or training curves. This documentation serves as a permanent architectural lighthouse, preventing circular re-litigation of settled engineering choices.

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
