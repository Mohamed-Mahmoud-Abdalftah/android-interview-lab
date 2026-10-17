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

## Concept and technical explanation

Rescuing and stabilizing a legacy codebase plagued by low test coverage and frequent crashes requires a phased, telemetry-driven 90-day execution framework:
- The Anti-Pattern of the Egotistical Rewrite:
  - Inexperienced leads immediately declare: "This code is terrible; we must freeze features and rewrite from scratch!"
  - Rewrites discard years of accumulated bug fixes and domain edge-case wisdom, halting business revenue and frequently leading to failed projects.
- The Structured 90-Day Staged Plan:
  1. Days 1–30: Listen, Instrument & Establish Baselines:
     - Audit production telemetry: integrate Google Play Vitals, Datadog, or Crashlytics to quantify crash-free rates and top 10 stack traces.
     - Build a rock-solid CI pipeline: automate Gradle build compilation, linting, and baseline test execution.
     - Listen to developers, product managers, and support tickets to map pain points without refactoring code yet.
  2. Days 31–60: Contain the Bleeding & Build Safety Nets:
     - Enforce the Boy Scout Rule: mandate that any touched code must have accompanying unit or integration tests.
     - Introduce Characterization / Golden Master Tests around critical revenue paths (e.g., Login and Checkout) to lock in existing behavior before refactoring.
     - Fix top 5 crashes responsible for 80% of user failures (Pareto Principle).
     - Deploy Feature Flags to safely gate upcoming migrations.
  3. Days 61–90: Incremental Modernization & Velocity Acceleration:
     - Execute an incremental refactoring of the highest-churn, lowest-stability feature module into clean Architecture.
     - Codify architecture standards via living ADRs and custom Detekt lint rules.
     - Publish a quantified scorecard demonstrating improved crash-free rate and developer velocity to leadership.

## Practical walkthrough (English)

Characterization Test pattern locking in legacy behavior before refactoring in Kotlin:
```kotlin
// Characterization Test: Captures existing legacy behavior (even quirks) as a safety net
class LegacyCheckoutCharacterizationTest {

    private val legacyService = LegacyCheckoutEngine()

    @Test
    fun `capture and assert baseline legacy checkout behavior across edge cases`() {
        // Assert exact legacy output for nominal inputs
        val standardResult = legacyService.calculateDiscount(
            cartTotal = 100.0,
            couponCode = "SAVE10",
            isVip = false
        )
        assertEquals(10.0, standardResult.discountAmount, 0.001)

        // Lock in known legacy quirk: null coupon code returns 0.0 without throwing NPE
        val nullCouponResult = legacyService.calculateDiscount(
            cartTotal = 100.0,
            couponCode = null,
            isVip = true
        )
        assertEquals(5.0, nullCouponResult.discountAmount, 0.001)
    }
}

// 90-Day Executive Milestone Review:
// - Days 1-30: Automated CI established; Play Vitals showed 98.2% crash-free rate.
// - Days 31-60: Top 5 crashes resolved; Characterization tests protected Checkout.
// - Days 61-90: Crash-free sessions lifted to 99.85%; PR cycle time reduced by 35%.
```

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

Execute a structured 90-day stabilization plan avoiding premature rewrites. Spend days 1–30 measuring baselines and building CI pipelines, days 31–60 writing characterization tests around critical paths and fixing top crashes, and days 61–90 incrementally refactoring high-churn modules behind feature flags while proving measurable ROI in crash-free sessions.

## Interview answer — structured

Inheriting a fragile, untested legacy application requires a disciplined, telemetry-driven ninety-day turnaround strategy rather than an emotional rewrite.
During Days 1 to 30, the focus is observation and measurement. We establish empirical baselines using Crashlytics and Google Play Vitals, identify top crash clusters, and construct an automated CI/CD pipeline to ensure build repeatability without altering production code.
During Days 31 to 60, we build safety nets. We fix the top five crashes responsible for the majority of user friction. Before refactoring, we author characterization tests around critical revenue paths like checkout, capturing existing behavior as a regression barrier. We introduce remote feature flags and enforce the Boy Scout Rule.
During Days 61 to 90, we execute incremental refactoring on the highest-churn module, migrating it to modern Clean Architecture.
We publish a clear scorecard demonstrating improved crash-free rates and reduced build times, proving sustainable technical ROI.

## Interview answer — deep senior

From an engineering leadership, technical debt remediation, and organizational transformation perspective, inheriting a troubled legacy codebase is a critical leadership crucible that tests strategic patience and tactical execution.
The most catastrophic mistake an incoming technical leader can make is succumbing to the rewrite delusion: declaring the inherited codebase unsalvageable and halting feature development for six months. This halts business momentum, discards edge-case wisdom embedded in the legacy code, and almost always results in a new system that reproduces old bugs.
Senior leaders execute a phased 30-60-90 day stabilization roadmap.
Phase 1 (Days 1 to 30) is dedicated to instrumentation and discovery. We establish continuous integration pipelines with automated build checks and integrate robust telemetry to record our baseline crash-free rate, cold launch latency, and ANR metrics. We interview engineers and product managers to map high-churn pain points.
Phase 2 (Days 31 to 60) focuses on stabilization and safety nets. Applying the Pareto Principle, we remediate the top five crashes causing eighty percent of user impact. Crucially, we wrap high-risk legacy modules in Characterization Tests—black-box regression tests that capture existing inputs and outputs without worrying about internal code aesthetics. We establish feature flagging infrastructure to decouple deployment from release.
Phase 3 (Days 61 to 90) delivers incremental modernization. We select a single, high-churn vertical slice—such as the user profile or payment module—and refactor it into clean, modular Kotlin components, demonstrating the new architectural blueprint to the team.
We institutionalize standards via Architecture Decision Records and custom Detekt rules.
At the ninety-day mark, we present an executive scorecard showing that crash-free sessions increased from ninety-eight percent to ninety-nine point nine percent and developer PR cycle time dropped by a third, earning long-term trust across the organization.

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
