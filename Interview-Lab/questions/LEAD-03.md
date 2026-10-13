---
id: "LEAD-03"
question: "What is technical debt, and how do you prioritize it?"
topic: "Senior Ownership, Communication & Technical Leadership"
code: "LEAD"
group: "A"
phase: 5
priority: "P2"
order: 458
editorial_status: "reviewed"
---

# LEAD-03

## Original interview question

What is technical debt, and how do you prioritize it?

## What the interviewer evaluates

- Debt as future-change cost caused by design shortcuts or obsolete assumptions.
- Priority by risk, change frequency and measurable return.

## Explanation in Arabic

ما هو الدين التقني (Technical Debt)، وكيف تقنع مدراء المنتج (Product Managers) بتخصيص وقت لسداده وترتيب أولوياته؟

1. ما هو الدين التقني؟
   - هو تكلفة الترقيعات والاختصارات الهندسية السريعة التي تم اتخاذها في الماضي لتسليم ميزة بسرعة للعملاء.
   - مثل القرض المالي: إذا لم تسدد أصل القرض، ستتراكم عليك **الفوائد (Interest)** في صورة: بطء إضافة ميزات جديدة، وتكرار الأعطال في الإنتاج، وبطء وقت البناء، وإحباط المهندسين واستقالتهم.

2. ترجمة الدين التقني للغة الأعمال (Translating Tech Debt to Business Impact):
   - مدير المنتج لا يهتم إذا قلت: "الكود ليس Clean ونريد إعادة كتابته بـ MVI!".
   - **تحدث بلغة الأرقام ومؤشرات الأعمال (Business Metrics)**:
     * بدلاً من "الكود فوضوي": "كل ميزة جديدة في شاشة الدفع تستغرق 3 أسابيع بدلاً من 4 أيام بسبب تشابك الكود القديم (خسارة سرعة بنسبة 70%)".
     * بدلاً من "نريد ترقية Gradle": "بناء التطبيق في الـ CI يستغرق 40 دقيقة، مما يهدر 150 ساعة شهرياً من وقت الفريق (تكلفة رواتب مهدرة)".
     * بدلاً من "نريد إصلاح الـ Memory Leaks": "معدل الـ Crash-free انخفض إلى 98.8% مما يعرض التطبيق لعقوبات Google Play Vitals وفقدان عملاء جدد".

3. استراتيجيات إدارة وسداد الدين التقني:
   - **قاعدة الكشافة (The Boy Scout Rule)**: "اترك الكود أنظف قليلاً مما وجدته" في كل PR.
   - **مخصص الـ 20% (The 20% Tech Debt Budget)**: الاتفاق مع إدارة المنتج على تخصيص 20% من سعة كل Sprint لسداد الديون التقنية والبنية التحتية، مقابل 80% للميزات الجديدة.

## Practical walkthrough

مصفوفة ترتيب أولويات الدين التقني (Tech Debt Prioritization Matrix):
```markdown
| نوع الدين التقني | التأثير التجاري / الأمني | تكرار الحدوث | التكلفة والجهد | الأولوية (Priority) |
|---|---|---|---|---|
| تسريب ذاكرة يسبب كراش OOM في شاشة الشراء | مباشر: خسارة مبيعات فورية | عالي (3% من المستخدمين) | يومان عمل | **P0 (فوري)** |
| مكتبة أمان قديمة معلنة كثغرة CVE | خطر اختراق وسحب من المتجر | محتمل | 3 أيام عمل | **P1 (عاجل)** |
| شاشة قديمة مكتوبة بـ XML معقد | بطء تطوير الميزات الجديدة | متوسط | أسبوع عمل | **P2 (مجدول في سبرنت)** |
| عدم توحيد أسماء الألوان في styles.xml | جمالي وتنظيمي فقط | منخفض | يوم عمل | **P3 (عند التفرغ)** |
```
صياغة اتفاقية Sprint مع الـ Product Manager:
"إذا استثمرنا 3 أيام في هذا الـ Sprint لفصل CheckoutViewModel القديم، سنخفض زمن تسليم ميزة Apple Pay و Google Pay القادمة من شهر إلى أسبوع واحد فقط."

## Why it matters and how it works

Debt can be deliberate with a repayment plan or accidental. A useful backlog item states evidence, consequence and a bounded intervention; vague “rewrite architecture” is hard to prioritize. Incident rate, lead time and defect escape can measure payoff.

## Worked example

Legacy screen directly calls Retrofit and Room. If it changes weekly and causes bugs, introduce repository seam around one flow and add tests before wider extraction. Do not rewrite all screens while a critical token leakage issue remains.

## Trade-offs and decision criteria

Repaying debt improves future velocity and reliability but consumes current feature capacity. A rewrite can introduce new defects; incremental strangler-style changes often reduce risk. Some harmless old code should remain.

## Failure modes

Team labels every disliked pattern “debt” and plans a six-month rewrite without baseline metrics. Instead tie each item to a customer/engineering cost and define completion criteria.

## Production perspective

Keep debt register with owner, impact, evidence and next touchpoint; reserve capacity for high-leverage repairs and revisit after incidents. Security debt may block release regardless of roadmap.

## Interview answer — short

Technical debt is the accrued engineering cost of past shortcuts that compounds interest in slower velocity and higher defect rates. Prioritize it by quantifying its business impact (lost revenue from crashes, developer hours wasted on slow CI, sprint velocity drops) and negotiate a standing 20% sprint capacity allocation dedicated to ongoing remediation.

## Interview answer — structured

Managing technical debt requires framing engineering hygiene in terms of business velocity and risk mitigation:

1. **Translate Technical Problems to Business Metrics**:
   - Product Managers do not prioritize abstract purity. Translate debt into business impact:
     - 'Refactoring the payment module' becomes: 'Our checkout failure rate is 2.4% due to legacy state race conditions, directly losing \$40,000 monthly in gross merchandise value.'
     - 'Updating Gradle build scripts' becomes: 'CI takes 45 minutes per PR, delaying release cycles and wasting 20 engineering hours weekly.'

2. **Categorize and Prioritize Debt**:
   - Evaluate debt using an Impact vs. Effort matrix:
     - **High Impact, Low Effort (Quick Wins)**: Immediate priority.
     - **High Impact, High Effort (Strategic Refactors)**: Requires dedicated architectural epics.
     - **Low Impact, Low Effort**: Resolved organically via Boy Scout rule.
     - **Low Impact, High Effort**: Explicitly ignored or deprioritized.

3. **Establish a Standing Capacity Agreement**:
   - Negotiate a fixed 80/20 capacity split with product leadership: 80% dedicated to product feature delivery, 20% strictly allocated to architectural health, tooling, dependency upgrades, and test coverage.

## Interview answer — deep senior

From an engineering leadership and organizational health standpoint, distinguishing debt types prevents toxic cycles:

1. **Prudent vs. Reckless Debt (Martin Fowler's Debt Quadrant)**:
   - Not all tech debt is bad. **Prudent deliberate debt** (taking a known shortcut to hit a regulatory launch date with an immediate plan to refactor) is a valid business tool. **Reckless inadvertent debt** (sloppy code produced by lack of design standards or testing) poisons the codebase. Leaders celebrate prudent trade-offs while ruthlessly eliminating reckless practices.

2. **The Refactor-Rewrite Fallacy**: A classic junior mistake is requesting a complete ground-up app rewrite ('Let's throw away the legacy app and rewrite it in Compose!'). Rewrites take 3x longer than estimated, halt product delivery, and re-introduce obscure bugs that the legacy app solved over 5 years. Senior leaders advocate for incremental in-place strangler-fig pattern refactorings.

3. **Visualizing Debt in Sprint Boards**: Tag debt items explicitly with a `tech-debt` label in Jira/Linear and track cycle times. If the ratio of bugs to features climbs above 30%, freeze feature development for a stabilization sprint.

## How to answer in the interview

- **Why:** debt consumes future speed or reliability.
- **How:** measure cost and prioritize by impact.
- **Trade-off:** cleanup investment versus feature capacity.
- **Failure case:** large rewrite lacks release slices.
- **Production solution:** small verified migration with outcome metric.

## Deep-dive talking points

Prompt for definition, impact/frequency scoring, incremental repair and measurable payoff.

## Follow-up questions

- **Interviewer:** "Why is the Strangler Fig pattern preferred over a full ground-up app rewrite?"
  **Answer:** "Because it incrementally replaces legacy components one by one behind interfaces, allowing continuous product delivery without the extreme risk of a monolithic rewrite."

- **Interviewer:** "What is the 'Boy Scout Rule' in software engineering?"
  **Answer:** "Always leave the code you touch a little cleaner than you found it, gradually paying down technical debt during routine feature work."

## Self-check rubric

Describe debt as a future cost tied to a real constraint; rank it by risk, frequency and migration cost; reserve a measurable slice of delivery for the highest-value item.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — maintainable separation.
- [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html) — build debt measurement.

Technically reviewed against primary documentation on 2026-10-13.
