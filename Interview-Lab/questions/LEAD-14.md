---
id: "LEAD-14"
question: "You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "C"
phase: 5
priority: "P2"
order: 469
editorial_status: "reviewed"
---

# LEAD-14

## Original interview question

You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?

## What the interviewer evaluates

- First 90 days as discovery, risk reduction and incremental delivery.
- Coverage quality and team trust rather than big rewrite.

## Explanation in Arabic

استلمت قيادة مشروع أندرويد قديم (Legacy App) يعاني من انعدام الاختبارات وتكرار الأخطاء وتذمر المطورين. ما هي خطتك الإستراتيجية لأول 90 يوماً (First 90-Day Plan)؟

1. الفخ القاتل الذي يقع فيه المطورون الجدد:
   - الحماس الزائد في الأسبوع الأول والمطالبة بإعادة كتابة التطبيق بالكامل من الصفر (The Total Rewrite Trap)!
   - إعادة الكتابة توقف تطوير ميزات الشركة لشهور، وتعيد إنتاج نفس الأخطاء القديمة، وتفشل في 80% من الحالات.
   - النهج الهندسي الناضج يعتمد على **الاستقرار أولاً، والتحسين المرحلي التدريجي (Strangler Fig Pattern)**.

2. خطة الـ 90 يوماً الاستراتيجية:
   - **الأيام 1 - 30 (الاستكشاف، القياس، وتأمين البيئة - Listen, Observe & Measure)**:
     * الجلوس مع المطورين وفريق المنتج لفهم نقاط الألم وأولويات العمل.
     * إنشاء **أدوات المراقبة (Observability Baseline)**: ضبط Crashlytics و Android Vitals لمعرفة أماكن تكرار الكراشات بدقة.
     * تثبيت بيئة الـ CI: إصلاح الاختبارات المتقلبة وتسريع البناء البارد.
     * إقرار **قاعدة الكشافة (Boy Scout Rule)**: إلزام المطورين بعدم لمس أي ملف دون كتابة اختبار بسيط له وترتيبه.
   - **الأيام 31 - 60 (وضع المعايير وتأمين التغييرات الجديدة - Guard & Standardize)**:
     * تطبيق مبدأ **"Test-Driven Bug Fixing"**: أي Bug جديد يُكتشف يُمنع إصلاحه إلا بعد كتابة Unit Test فاشل يثبت المشكلة أولاً ثم إصلاح الكود ليمر الاختبار.
     * تفعيل أدوات الفحص الساكن (Spotless + Detekt) مع Baseline لمنع دخول أي ديون تقنية جديدة للفرع الرئيسي.
     * كتابة أول ADR يحدد المعمارية الرسمية للميزات الجديدة (مثل Clean Architecture مع Compose و Coroutines).
   - **الأيام 61 - 90 (التطوير المعماري ومضاعفة السرعة - Modernize & Accelerate)**:
     * بدء تجزئة أول موديول معيب وعزله (Modularization via Strangler Fig).
     * تفعيل الـ Remote Build Cache لتقليل وقت التجميع في الـ CI بنسبة 50%.
     * استعراض الإنجازات بالأرقام أمام الإدارة: ارتفاع الـ Crash-free من 97% إلى 99.5%، وتسريع وقت تسليم الميزات الجديدة.

## Practical walkthrough

خارطة طريق خطة الـ 90 يوماً التنفيذية (90-Day Execution Roadmap):
```markdown
### خارطة طريق الـ 90 يوماً لإنقاذ وترقية تطبيق Legacy Android:

| المرحلة الزمنية | الأهداف والأنشطة الرئيسية | مؤشرات النجاح المستهدفة (OKRs) |
|---|---|---|
| **الشهر 1: الملاحظة والتأمين**<br>(الأيام 1-30) | - تدقيق الاعتماديات والمكتبات المهجورة.<br>- قياس زمن الـ CI ومعدل الكراش الحقيقي.<br>- جلسات 1:1 مع المهندسين وفريق المنتج.<br>- وقف نزيف الأخطاء عبر Boy Scout rule. | - تقرير شامل بحالة الديون التقنية.<br>- لوحة قياس Vitals حية ومفعلة.<br>- صفر اختبارات متقلبة في الـ CI. |
| **الشهر 2: البوابات والمعايير**<br>(الأيام 31-60) | - فرض Unit Tests إجبارية لأي إصلاح Bug.<br>- تفعيل Detekt & Android Lint baselines.<br>- إقرار ADR للميزات الجديدة.<br>- تدريب الفريق على Compose و Coroutines. | - تغطية 100% لجميع الأخطاء الجديدة بتستات.<br>- انخفاض الـ Escaped Bugs بنسبة 40%.<br>- تسليم أول ميزة بالمعمارية الجديدة. |
| **الشهر 3: التحديث والتسريع**<br>(الأيام 61-90) | - تجزئة أكثر موديول مسبب للكراشات.<br>- تفعيل Gradle Remote Build Cache.<br>- توثيق الإنجازات في مراجعة ربع سنوية. | - ارتفاع Crash-free من 97.2% إلى 99.5%.<br>- خفض زمن بناء CI من 35 إلى 10 دقائق.<br>- ارتفاع مؤشر رضا المهندسين. |
```

## Why it matters and how it works

A legacy system has hidden contracts in code, production behavior and people. Prioritize incidents, frequently changed paths and irreversible risks. Stabilizing CI and observability improves later refactors. Incremental seams allow tests around behavior before changing structure.

## Worked example

Days 1–30: reproduce release build and top crashes, map checkout state/data ownership. Days 31–60: add lost-response and Room migration tests, fix a frequent crash and document API contract. Days 61–90: extract one repository boundary, stage rollout and compare metrics.

## Trade-offs and decision criteria

A broad rewrite may simplify architecture eventually but risks regression and halts delivery. Small repairs can accumulate without a target design; use an ADR and metrics to keep direction.

## Failure modes

Raising nominal coverage from 20% to 80% with mocked implementation tests does not catch payment duplicates. Choose behavior and boundary tests based on production incidents. Avoid blaming prior team without understanding constraints.

## Production perspective

Present baseline, high-risk plan and measurable wins to product/team. Keep release cadence, mentor owners and revisit roadmap after evidence from first changes.

## Interview answer — short

Structure your first 90 days into three distinct 30-day horizons: Days 1–30 focuses on listening, establishing observability baselines, and stabilizing the CI pipeline; Days 31–60 institutes quality gates, mandatory test-driven bug fixes, and ADR architectural standards; Days 61–90 executes targeted modular refactoring via the Strangler Fig pattern and celebrates quantifiable stability gains.

## Interview answer — structured

Rescuing an inherited legacy codebase requires a disciplined, structured 30-60-90 day framework that builds team trust before touching core architecture.

First, **Days 1–30: Listen, Observe, and Establish Baselines**. Next, with Avoid the Rewrite Trap, reject calls for an immediate ground-up rewrite. Understand business domain history and developer friction through 1-on-1 discovery interviews.
Additionally, with Telemetry & Baseline Observability, audit Google Play Vitals and Crashlytics. Measure key operational baselines: crash-free user rate, cold startup latency, and CI execution times. With Pipeline Hygiene, fix broken CI scripts and stabilize flaky tests so developers regain confidence in automated gates.
**Days 31–60: Standardize Quality Gates & Prevent New Debt**. With Test-Driven Defect Resolution, enforce an uncompromising team policy: no production bug is fixed without an accompanying automated test that reproduces the failure before applying the fix.
With Automated Linters with Baselines, introduce Spotless and Detekt with baseline files to freeze legacy technical debt and reject any new violations. With Architectural Standards (ADR), author an ADR codifying the architectural standard (e.g. MVI + Compose) mandated for all net-new screens.
**Days 61–90: Modernize, Accelerate, and Demonstrate ROI**. With Strangler Fig Refactoring, extract the most volatile legacy god-class into an isolated, tested module behind a clean interface.
With Build Performance, implement Gradle build caching and parallel execution to halve CI feedback loops. Finally, with Quantifiable Executive Reporting, present leadership with measurable wins: crash-free rate improved to 99.5%, defect turnaround times reduced, and developer velocity restored.


## Interview answer — deep senior

From an organizational change management and cultural perspective, leadership determines adoption.

First, with Winning Hearts and Minds Before Refactoring Code, when a new lead arrives and immediately criticizes existing code, legacy team members become defensive. Acknowledge that the legacy code generated the company's revenue and kept the business alive. Position refactoring as empowering the team with modern tooling rather than correcting past mistakes. Next, with Tackling the Worst Pain Point First, identify the single recurring issue that causes developers the most daily frustration (e.g., an unpredictable 45-minute CI build or a flaky database migration). Fixing that single issue in your first 3 weeks earns immediate technical credibility and unlocks team buy-in for future architectural standards.
Finally, with Incremental strangler fig vs Big Bang, emphasize continuous value delivery. By isolating legacy screens behind feature flags and swapping them incrementally, the product continues shipping user features every sprint while health metrics climb steadily.


## How to answer in the interview

- **Why:** legacy risk must be located before rewriting.
- **How:** baseline, fix one vertical slice, expand.
- **Trade-off:** incremental safety versus rewrite appeal.
- **Failure case:** coverage target misses critical path.
- **Production solution:** measure defects and ship reversible slices.

## Deep-dive talking points

Prompt for discovery evidence, safety net, bounded seam, baseline metrics and team ownership.

## Follow-up questions

- **Interviewer:** "Why is demanding a complete app rewrite in your first month a major red flag for leadership?"
  **Answer:** "Because it halts product delivery for months, carries massive business risk, and disregards years of hard-won edge case solutions embedded in the legacy code."

- **Interviewer:** "What is 'Test-Driven Bug Fixing' and why is it vital for legacy projects?"
  **Answer:** "Writing a failing test that reproduces the bug before touching the code, ensuring the bug is truly understood and preventing it from ever regressing."

## Self-check rubric

Prioritize a 90-day baseline, high-risk bug containment, seams and targeted tests, then incremental refactors. Define metrics and avoid promising a full rewrite before understanding production.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation principles.
- [Android testing overview](https://developer.android.com/training/testing) — safety net design.

Technically reviewed against primary documentation on 2026-10-13.
