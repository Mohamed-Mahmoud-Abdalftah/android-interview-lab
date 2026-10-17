#!/usr/bin/env python3
"""
Elevation script for LEAD questions: LEAD-09 to LEAD-15.
Topic: Senior Ownership, Communication & Technical Leadership (LEAD)
Phase 5, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "القيادة التقنية والتواصل وملكية المشاريع الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# LEAD-09: How do you run an incident postmortem without blame?
# ==========================================
DATA["LEAD-09"] = {
    "concept_en": """Conducting a blameless postmortem transforms operational failures into systemic organizational resilience by assuming well-intentioned engineers made reasonable choices given the information available:
- The SRE Axiom of Blamelessness (John Allspaw / Google SRE):
  - Human error is a symptom of a flawed system, not the root cause.
  - Punishing individuals breeds concealment, secrecy, and fear, destroying incident visibility and guaranteeing identical failures recur.
- The 5-Stage Postmortem Operating Model:
  1. Timeline Construction (The First 24 Hours):
     - Piece together an objective, timestamped narrative from Slack incident channels, Datadog alerts, Google Play Console Vitals spikes, and commit hashes.
  2. The 5 Whys Root-Cause Analysis:
     - Drill past surface symptoms to discover systemic weaknesses.
     - Example: Crash occurred -> Coroutine swallowed exception -> Lacked custom CoroutineExceptionHandler -> No automated lint check existed -> Architectural review lacked concurrency rubric.
  3. Action Items (SMART & Systemic):
     - Every finding must produce a prioritized JIRA ticket with an assigned owner and completion deadline.
     - Prioritize systemic prevention (automated lint rules, canary stages, circuit breakers) over fragile human procedural admonishments (\"engineers must be more careful\").
  4. Dissemination & Knowledge Sharing:
     - Publish the postmortem document internally across engineering teams to prevent duplicate mistakes in adjacent product domains.""",
    "walkthrough_en": """Blameless Postmortem Template and Automated CI Guard in Kotlin:
```markdown
# Incident Postmortem: Outage-2026-10-12 (Android Checkout Crash Spike)

## Executive Summary
On October 12 at 14:15 UTC, release v4.2.0 caused a 4.2% crash spike on Android 11 devices during checkout.
Root cause: A missing null check on an optional backend payload triggered a NullPointerException.
Impact: 1,240 checkout attempts failed before the phased rollout was halted at 14:45 UTC.

## Chronological Timeline (UTC)
- 13:30: Staged rollout promoted to 10% on Google Play.
- 14:15: Datadog triggers automated alert: Crash-free sessions dropped below 99.0%.
- 14:25: Mobile incident team assembled; root-cause identified in BillingAddress.kt.
- 14:45: Rollout halted via Google Play Console; backend enabled fallback payload.
- 15:30: Hotfix v4.2.1 built, verified via automated tests, and submitted for review.

## Systemic Root Cause (5 Whys)
1. Why did the app crash? -> Kotlin non-null type encountered a null JSON field.
2. Why was it null? -> Backend rolled out an optional field without mobile schema alignment.
3. Why didn't unit tests catch it? -> Test fixtures only used complete mock payloads.
4. Why wasn't contract testing run? -> Pact contract verification was not mandatory in CI.
5. Why wasn't rollout halted sooner? -> Automated Play Console halting was not configured.

## Systemic Action Items
1. [P0]: Add Kotlinx Serialization @Serializable default fallback values (Owner: Sarah).
2. [P0]: Integrate automated Pact contract testing gate into backend CI (Owner: Dave).
3. [P1]: Configure Datadog automated webhook to pause Google Play rollouts (Owner: Alex).
```""",
    "short_en": """Run a blameless postmortem by focusing on system flaws rather than human error. Establish a timestamped timeline, conduct a 5 Whys root-cause inquiry to uncover architectural weaknesses, and generate assigned, automated action items like lint checks and canary halts, sharing learnings openly to foster psychological safety and team resilience.""",
    "structured_en": """Conducting an effective, blameless postmortem transforms operational failures into permanent systemic improvements.
The foundation of blamelessness is acknowledging that engineers act in good faith based on the context they had; punishing individuals only incentivizes teams to conceal errors.
We run postmortems using a structured four-stage process.
First, we construct an objective chronological timeline using server logs, crash spikes, and deployment records.
Second, we facilitate a collaborative Five Whys inquiry, digging past surface mistakes to discover systemic vulnerabilities in our testing, deployment, or monitoring layers.
Third, we generate concrete, prioritized action items that enforce systemic defenses—such as automated CI lint rules, contract testing, or automated canary halts—rather than relying on human vigilance.
Finally, we publish the postmortem across the engineering organization, cultivating psychological safety and institutional resilience.""",
    "deep_senior_en": """From an engineering leadership, site reliability engineering, and organizational culture standpoint, the postmortem is the definitive litmus test of an engineering team\'s maturity.
When an outage strikes, low-maturity organizations seek a scapegoat, asking \"Who wrote this bug?\" This punitive reaction induces organizational paralysis, causing engineers to delay releases, hide mistakes, and resist refactoring fragile legacy systems.
Senior leaders enforce radical blamelessness, championed by John Allspaw: if an engineer fat-fingers a release or forgets a null check, the fault lies entirely with the deployment infrastructure that permitted an unchecked manual error to reach production.
We initiate the postmortem within twenty-four hours while memories are fresh. We assemble the timeline from immutable telemetry: git commit logs, Slack incident channels, and Google Play Console vitals.
During the retrospective, we conduct a Five Whys analysis. If an unhandled coroutine exception caused an ANR spike, we do not stop at \"add a try-catch.\" We ask why the architectural template lacked an injected CoroutineExceptionHandler, why the pull request checklist did not flag unconfined scopes, and why staging smoke tests failed to exercise edge-case latency.
The output of the postmortem is a set of SMART preventative action items. We prioritize automated structural guards: writing a custom Detekt rule, adding automated canary halt webhooks in Datadog, or introducing consumer-driven contract tests. By sharing the completed review openly across the engineering department, we turn operational pain into permanent organizational strength.""",
    "meta_ar": {
        "id": "LEAD-09",
        "questionAr": "كيف تدير جلسة مراجعة وتحليل للحوادث التقنية (Incident Postmortem) دون توجيه اللوم للأفراد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "ثقافة المراجعة الخالية من اللوم الشخصي (Blameless Culture)، تحليل الأسباب الجذرية عبر أسلوب الأسئلة الخمس (5 Whys)، استخلاص بنود عمل وقائية مؤتمتة (Action Items)، وترسيخ الأمان النفسي المؤسسي.",
        "concept_ar": "ترتكز إدارة جلسات مراجعة وتحليل الحوادث التقنية (Incident Postmortem) دون توجيه اللوم على مبدأ أن الأخطاء البشرية هي أعراض لخلل في المنظومة وليست السبب الجذري: فالمهندس المخطئ اتخذ قراره بناءً على المعطيات المتاحة له في تلك اللحظة؛ ومعاقبته تدمر الأمان النفسي وتدفع الفريق لإخفاء الأخطاء وتكرار الكوارث. وتعتمد الجلسة الناجحة على 4 خطوات: أولاً، بناء جدول زمني موثق بالأدلة من السجلات والتنبيهات خلال 24 ساعة من الحادث؛ ثانياً، تطبيق أسلوب 'الأسئلة الخمس' (5 Whys) للغوص تحت السطح واكتشاف الفجوات المعمارية ونقاط الضعف في الفحص الآلي؛ ثالثاً، استخراج خطة عمل وقائية مؤتمتة (Action Items) ذات أولوية ومسؤولين محددين (مثل إضافة فحص آلي في CI أو قاطع أعطال سحابي) بدلاً من الوعود البشرية الساذجة كـ 'سنكون أكثر حذراً'؛ رابعاً، نشر التقرير بشفافية في المؤسسة لتعميم الاستفادة ومنع تكرار العطل في الفرق الأخرى.",
        "walkthrough_ar": """قالب توثيق مراجعة الحوادث التقنية الخالية من اللوم بصيغة Markdown:
```markdown
# تقرير مراجعة الحادث التقني: عطل شاشة الدفع في التحديث 4.2.0

## ملخص الحادث والأثر
في 12 أكتوبر الساعة 14:15 بتوقيت غرينتش، تسبب التحديث في ارتفاع الكراشات بنسبة 4.2% على أندرويد 11.
السبب الجذري: حقل اختياري في بيانات الـ JSON أرجع قيمة null فتسبب في NullPointerException.
الأثر: فشل 1,240 محاولة دفع قبل إيقاف النشر التدريجي في الساعة 14:45.

## الجدول الزمني للأحداث (Chronology)
- 13:30: رفع نسبة التحديث التدريجي إلى 10% على Google Play.
- 14:15: إطلاق تنبيه آلي من Datadog بهبوط نسبة الجلسات السليمة عن 99%.
- 14:25: اجتماع فريق الطوارئ وتحديد الخلل في كائن BillingAddress.kt.
- 14:45: إيقاف التحديث على المتجر وتفعيل الخادم لوضع الاستجابة البديلة.
- 15:30: بناء تحديث طوارئ 4.2.1 واختباره آلياً ورفعه للاعتماد.

## الأسباب الجذرية (تحليل الأسئلة الخمس 5 Whys)
1. لماذا انهار التطبيق؟ -> واجه كود كوتلن قيمة null في حقل غير مهيأ لاستقبالها.
2. لماذا كانت null؟ -> أضاف فريق الخوادم حقلاً جديداً دون تحديث عقد الـ API المشترك.
3. لماذا لم تكشفها اختبارات الوحدة؟ -> كانت بيانات الاختبار الوهمية ترسل الحقل دائماً.
4. لماذا لم تعمل اختبارات العقود؟ -> لم تكن اختبارات Pact إلزامية قبل دمج كود الخادم.
5. لماذا تأخر إيقاف التحديث؟ -> لم يكن هناك ربط آلي بين تنبيهات Datadog وإيقاف المتجر.

## خطة العمل الوقائية المؤتمتة
1. [أولوية قصوى]: إلزام استخدام قيم افتراضية لكافة حقول الـ JSON في كوتلن (المسؤول: سارة).
2. [أولوية قصوى]: جعل اختبارات العقود Pact شرطاً إلزامياً لدمج كود الخادم في CI (المسؤول: داود).
3. [أولوية متوسطة]: برمجة Webhook لإيقاف تحديثات المتجر آلياً عند هبوط الاستقرار (المسؤول: علي).
```""",
        "why_it_matters_ar": "توجيه اللوم للأفراد يدمر الشفافية ويدفع المهندسين لإخفاء الكوارث خوفاً من العقاب ويضمن تكرار نفس الانهيار في المستقبل.",
        "worked_example_ar": "تسبب مطور في كراش أوقف الدفع لساعة؛ بدلاً من لومه، عقدنا مراجعة واكتشفنا غياب اختبارات الـ Null Safety، فبنينا قاعدة Lint مخصصة منعت تكرار الخطأ تماماً في 20 شاشة أخرى.",
        "trade_offs_ar": "عقد جلسة المراجعة وتوثيقها يستغرق نصف يوم عمل؛ لكنه يبني حصانة برمجية مؤسسية تحمي ملايين الدولارات من خسائر التوقف المفاجئ.",
        "failure_modes_ar": "أخطر الأخطاء هو تحويل الجلسة إلى محاكمة شخصية والبحث عن كبش فداء، أو كتابة توصيات غير قابلة للقياس مثل 'ضرورة انتباه المراجعين'.",
        "production_perspective_ar": "في الشركات التقنية العالمية الكبرى، يُحتفى بالمهندس الذي يعترف بعطل في الإنتاج وتُكافأ شجاعته لأنها كشفت ثغرة في دفاعات النظام.",
        "how_to_answer_ar": "ابدأ ببيان فلسفة اللوم المنظومي وليس الفردي، واشرح مراحل الجلسة الأربع (الجدول الزمني، الأسئلة الخمس، الإجراءات الوقائية، ونشر المعرفة)، واعرض نموذج خطة العمل المؤتمتة.",
        "talking_points_ar": "المراجعة الخالية من اللوم Blameless Postmortem، فلسفة جوجل وإتسي SRE، تحليل الأسئلة الخمس 5 Whys، الأمان النفسي، وبنود العمل المؤتمتة Preventative Action Items.",
        "follow_ups_ar": "كيف تتصرف إذا حاول أحد المدراء التنفيذيين الضغط في الجلسة لمعاقبة المهندس الذي أطلق التحديث المنهار؟",
        "self_check_ar": "هل أكدت على غياب اللوم الشخصي، وشرحت منهجية 5 Whys، وأكدت على أن تكون خطة العمل مؤتمتة في خط الـ CI وليست وعوداً بشرية؟",
        "references_ar": f"- [John Allspaw: Blameless PostMortems and a Just Culture](https://codeascraft.com/2012/05/22/blameless-postmortems/) — المقال التاريخي التأسيسي لثقافة المراجعة الخالية من اللوم في شركة Etsy.\n- [Google SRE Book: Postmortem Culture - Learning from Failure](https://sre.google/sre-book/postmortem-culture/) — الدليل الرسمي لشركة جوجل لإدارة ثقافة ما بعد الحوادث وتحويل الأعطال إلى مناعة مؤسسية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """ندير جلسة مراجعة الحوادث دون لوم بالانطلاق من مبدأ أن الخطأ البشري هو عرض لضعف في النظام وليس سبباً جذرياً له. نبني جدولاً زمنياً موثقاً للأحداث، ونحلل الأسباب بأسلوب الأسئلة الخمس 5 Whys لكشف الفجوات المعمارية، ونلزم الفريق بإجراءات وقائية مؤتمتة مثل قواعد Lint ووقف التحديثات آلياً، وننشر التقرير لتعميم الفائدة وتكريس الأمان النفسي.""",
        "best_answer_ar": """ترتكز الإدارة الاحترافية لجلسات مراجعة الحوادث التقنية على ترسيخ ثقافة التعلم المؤسسي الخالي تماماً من اللوم الشخصي.
ينطلق القائد التقني من قاعدة هندسية راسخة: المطورون يعملون بحسن نية وفق المعلومات المتاحة لهم، والبحث عن كبش فداء يدمر الأمان النفسي ويدفع الفريق للتستر على الأخطاء وتكرار الكوارث.
وتُدار الجلسة عبر أربع مراحل منضبطة:
نبدأ أولاً ببناء جدول زمني تسلسلي موثق بالأدلة والسجلات وتنبيهات الخوادم لرسم مسار الحادث بدقة.
ثم نطبق أسلوب الأسئلة الخمس 5 Whys للغوص عميقاً وراء الأسباب السطحية، والبحث عن الثغرات التي سمحت بمرور الكود دون فحص آلي في بيئات الاختبار.
بعد ذلك نستخلص خطة عمل وقائية مؤتمتة تُسند لمهندسين بمهام وتواريخ محددة؛ مركزين على حماية النظام برمجياً عبر قواعد فحص جديدة واختبارات عقود وربط تنبيهات الأعطال بوقف التحديثات آلياً، بدلاً من التوصيات الشفهية الساذجة.
وأخيراً ننشر التقرير بشفافية لكافة فرق الشركة لتعميم المعرفة وتأصيل المناعة التقنية.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وهندسة موثوقية النظم SRE، تعد جلسة مراجعة الحوادث المقياس الحقيقي لنضج المؤسسة التقنية واستدامتها.
في الفرق الهشة، يتحول وقوع العطل إلى محاكمة تفتيشية تبحث عمن كتب السطر البرمجي المسبب للمشكلة، وهي ثقافة عقيمة تصيب الفريق بالشلل وتدفع المطورين للتردد في التطوير وتأخير الإطلاقات خشية العقاب.
ويقضي القائد التقني على هذا التراجع بتبني فلسفة جون ألسباو: إذا استطاع مطور إسقاط بيئة الإنتاج بخطأ بسيط، فإن الخلل الجوهري يكمن في البنية التحتية وآليات النشر المؤتمتة التي افتقرت لصمامات الأمان وعزلت الكود عن الفحص الرشيد.
نعقد الجلسة خلال أربع وعشرين ساعة لضمان استحضار التفاصيل، ونبني السردية من السجلات الرقمية الثابتة في خطوط الـ CI ولوحات المراقبة.
وخلال تحليل الأسئلة الخمس، لا نتوقف عند معالجة الكراش محلياً؛ بل نسأل لماذا سمحت أدوات الـ Lint بوجود نداءات غير آمنة، ولماذا لم ترصد اختبارات الدخان العطل قبل النشر العام، ولماذا تأخرت التنبيهات في رصد تدهور تجربة المستخدم.
ويتمخض الاجتماع عن بنود عمل وقائية ذكية SMART تعزز دفاعات النظام تلقائياً؛ مثل برمجة قواعد فحص مخصصة في Detekt، وبرمجة خطافات آلية توقف نشر التحديث في متجر جوجل فور هبوط معدل الاستقرار.
وعند تعميم هذه الدروس بشفافية وامتنان لمن ساهم في كشف الثغرة، نرسخ ثقافة هندسية شجاعة تحول العثرات العابرة إلى حصانة تقنية دائمة تحمي مستقبل الشركة."""
    }
}

# ==========================================
# LEAD-10: How do you decide build versus buy for third-party libraries/SDKs?
# ==========================================
DATA["LEAD-10"] = {
    "concept_en": """Deciding whether to build a custom solution or integrate a third-party library/SDK requires evaluating Total Cost of Ownership (TCO), core competency differentiation, security attack surface, and long-term maintenance overhead:
- The Build vs Buy Matrix:
  - Buy (or Adopt Open Source): Best for commodity, highly regulated, or complex domain problems outside the company's core value proposition (e.g., Video transcoding, Map rendering, Payment gateway tokenization, Analytics).
  - Build: Best for core business differentiators, proprietary algorithmic logic, highly specialized UI experiences, or when external solutions introduce unacceptable binary size or regulatory risks.
- The 5-Pillar Decision Framework:
  1. Core Competency & Strategic Value:
     - Does this feature represent our unique intellectual property (IP) and competitive advantage? If yes -> Build. If it is a generic utility -> Buy/Adopt.
  2. Total Cost of Ownership (TCO):
     - \"Free\" open source is never free: TCO includes initial integration effort, ongoing library upgrades, breaking API migrations, and dependency debugging.
     - Commercial SDKs entail annual licensing, per-user pricing tiers, and vendor lock-in risks.
  3. Security, Privacy, and Supply Chain Risk:
     - What permissions does the SDK demand? Does it harvest user data, violate GDPR/COPPA, or inject malicious ads (supply-chain vulnerabilities)?
  4. Platform Health and Binary Footprint:
     - Is the library actively maintained? What is the impact on APK/AAB download size and method count? Does it support 16KB page sizes and modern Android OS versions?
  5. Exit Strategy & Abstraction Portability:
     - Can the library be isolated behind an internal interface (Adapter pattern) so it can be swapped out if the vendor changes pricing or goes bankrupt?""",
    "walkthrough_en": """Formalizing a Build vs Buy evaluation rubric in Kotlin:
```kotlin
data class SdkEvaluationScorecard(
    val libraryName: String,
    val isCoreDifferentiator: Boolean, // If true, strongly favors BUILD
    val downloadSizeKbytes: Int,       // Impact on APK size
    val annualLicenseCostUsd: Double,
    val maintenanceHealthScore: Int,   // 1 to 10 (commit frequency, issue resolution)
    val securityRiskScore: Int,        // 1 to 10 (track record, permission demands)
    val customBuildDaysEstimated: Int
) {
    val recommendation: String
        get() = when {
            isCoreDifferentiator -> "BUILD: Strategic core intellectual property."
            securityRiskScore > 7 -> "REJECT: Critical supply chain / privacy security risk."
            downloadSizeKbytes > 10_000 -> "EVALUATE BUILD: Binary size impact exceeds acceptable budget."
            maintenanceHealthScore < 4 -> "BUILD: Vendor library appears abandoned."
            else -> "BUY / ADOPT: Wrap behind internal Domain Adapter interface."
        }
}

// Architectural Rule: Always isolate third-party SDKs behind an internal domain wrapper
interface AnalyticsTrackerPort {
    fun trackScreen(name: String)
}

// Vendor Adapter: Insulates the codebase from vendor lock-in
class MixpanelAnalyticsAdapter(private val mixpanelSdk: MixpanelAPI) : AnalyticsTrackerPort {
    override fun trackScreen(name: String) {
        mixpanelSdk.track("screen_view", JSONObject().put("screen", name))
    }
}
```""",
    "short_en": """Decide build versus buy by evaluating core business competency, total cost of ownership, security and privacy compliance, and binary footprint impact. Buy commodity infrastructure like payments or analytics, wrapping them behind internal domain interfaces to prevent vendor lock-in. Build custom solutions for core algorithmic differentiators and proprietary business logic.""",
    "structured_en": """Deciding whether to build an internal component or integrate a third-party SDK requires a disciplined evaluation of business value and operational risk.
Our evaluation is anchored in five dimensions.
First, we assess core competency: if the capability represents our primary product differentiator, we build it internally to retain complete strategic control; generic commodity utilities, such as push notifications or map rendering, favor buying or adopting established open-source libraries.
Second, we calculate Total Cost of Ownership, weighing upfront commercial licensing against the ongoing engineering overhead of maintaining and updating custom code.
Third, we evaluate security and privacy, scrutinizing third-party code for supply-chain vulnerabilities, intrusive background data harvesting, and regulatory compliance under GDPR.
Fourth, we analyze platform health, auditing binary size inflation, active maintenance, and compatibility with modern Android OS releases.
Finally, whenever we adopt an external SDK, we enforce an architectural requirement to wrap it behind an internal domain interface, insulating our codebase from vendor lock-in and pricing shifts.""",
    "deep_senior_en": """From an engineering strategy, technology economics, and enterprise risk management perspective, the build-versus-buy decision represents a long-term capital allocation commitment.
A frequent anti-pattern among engineering teams is \"Not Invented Here\" (NIH) syndrome, where developers reinvent commodity utilities like image loaders, spending months debugging caching heuristics while starving core business features. The opposing anti-pattern is indiscriminate library addiction, where teams import dozens of unvetted third-party SDKs to save trivial development hours, bloating APK sizes and introducing catastrophic supply-chain attack vectors.
Senior leaders apply a rigorous evaluation rubric. We begin with strategic differentiation: if the software represents the company\'s secret sauce—such as a proprietary offline-first synchronization engine or an automated trading algorithm—we mandate an internal build to maintain intellectual property ownership and performance sovereignty.
For commodity functions like video streaming or crash telemetry, we evaluate Total Cost of Ownership. Open-source is never free; it incurs integration friction, dependency conflicts, and the cost of upgrading when Android OS breaks binary compatibility.
We conduct thorough security and privacy reviews: inspecting SDK manifest permissions, verifying whether native libraries adhere to 16KB memory page alignment, and auditing background network beacons to prevent illegal tracking under GDPR and COPPA.
Crucially, when we buy or adopt an external tool, we enforce strict architectural decoupling. We isolate the third-party dependency behind a domain interface adhering to the Ports and Adapters pattern. The vendor symbol never escapes its adapter module. If the vendor changes its pricing tiers, suffers a catastrophic outage, or is acquired, we can swap the provider in days without rewriting a single line of business logic.""",
    "meta_ar": {
        "id": "LEAD-10",
        "questionAr": "كيف تتخذ قرار البناء الذاتي مقابل الشراء أو استخدام حزم خارجية (Build vs Buy) للمكتبات وحزم الـ SDK؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "مصفوفة اتخاذ القرار (Build vs Buy Matrix)، التكلفة الإجمالية للملكية (TCO)، الميزة التنافسية الجوهرية (Core Competency)، أمان سلاسل التوريد والخصوصية، وتطويق الحزم خلف واجهات مجردة لمنع الارتهان (Vendor Lock-in).",
        "concept_ar": "يتطلب اتخاذ قرار البناء الذاتي مقابل الشراء أو تبني حزم ومكتبات خارجية (Build vs Buy) موازنة استراتيجية دقيقة بين التكلفة الإجمالية للملكية (TCO)، والميزة التنافسية للشركة، ومخاطر الأمان والارتهان للموردين: الخطوة الأولى هي تقييم الميزة التنافسية الجوهرية (Core Competency)؛ فإذا كانت الميزة تمثل صلب القيمة التجارية للشركة وخوارزمياتها المميزة فإن بناؤها ذاتياً إلزامي لضمان السيطرة الكاملة على الملكية الفكرية، أما الميزات العامة الشائعة (مثل الخرائط، ومعالجة المدفوعات، وتحليلات البيانات) فالشراء أو تبني مكتبة قياسية هو الخيار الأمثل. وتعتمد مصفوفة التقييم على 5 معايير: أولاً، التكلفة الإجمالية للملكية (TCO)؛ فالمكتبات المجانية ليست مجانية في الواقع بل تفرض تكاليف صيانة وترقيات مستمرة؛ ثانياً، الأمان وسلاسل التوريد وفحص أذونات الحزمة وتوافقها مع الخصوصية (GDPR)؛ ثالثاً، صحة الحزمة وحجمها الإضافي على الـ APK وتوافقها مع أحدث إصدارات أندرويد؛ رابعاً، استراتيجية الخروج بتطويق أي حزمة خارجية خلف واجهة مجردة (Adapter Pattern) لتسهيل استبدالها لاحقاً دون المساس بكود التطبيق.",
        "walkthrough_ar": """مصفوفة تقييم حزم الـ SDK وعزلها خلف واجهة مجردة لمنع الارتهان بكوتلن:
```kotlin
// مصفوفة تقييم الحزم الخارجية لاتخاذ قرار البناء أو الشراء
data class SdkEvaluationScorecard(
    val libraryName: String,
    val isCoreDifferentiator: Boolean, // هل تمثل صلب الميزة التنافسية للمشروع؟
    val downloadSizeKbytes: Int,       // الأثر على حجم ملف الـ APK
    val annualLicenseCostUsd: Double,
    val maintenanceHealthScore: Int,   // نشاط الصيانة وسرعة حل المشكلات من 1 إلى 10
    val securityRiskScore: Int         // تقييم المخاطر الأمنية وتتبع البيانات
) {
    val decision: String
        get() = when {
            isCoreDifferentiator -> "بناء ذاتي (BUILD): تمثل صلب الملكية الفكرية الاستراتيجية."
            securityRiskScore > 7 -> "رفض قاطع: خرق أمني يهدد خصوصية بيانات المستخدمين."
            downloadSizeKbytes > 10_000 -> "دراسة البناء: حجم الحزمة ضخم جداً ويثقل التطبيق."
            maintenanceHealthScore < 4 -> "بناء ذاتي: المكتبة مهجورة ولا تحظى بتحديثات دورية."
            else -> "شراء / تبني خارجي (BUY): مع إلزام عزلها خلف واجهة وسيطة."
        }
}

// قاعدة معمارية ذهبية: عزل أي حزمة خارجية خلف واجهة برمجية داخلية (Domain Port)
interface AnalyticsTrackerPort {
    fun trackEvent(name: String)
}

// محول البنية التحتية لعزل حزمة التحليلات الخارجية ومنع الارتهان (Vendor Lock-in)
class ExternalAnalyticsAdapter(private val vendorSdk: MixpanelAPI) : AnalyticsTrackerPort {
    override fun trackEvent(name: String) {
        vendorSdk.track(name, JSONObject())
    }
}
```""",
        "why_it_matters_ar": "الاستسهال في دمج حزم خارجية مشبوهة يضخم حجم التطبيق ويعرض بيانات المستخدمين للاختراق ويرهن مصير الشركة لمورد خارجي قد يرفع أسعاره فجأة.",
        "worked_example_ar": "فكر الفريق في بناء مشغل فيديو مخصص استغرق شهرين من العمل؛ أقنعهم القائد التقني بتبني ExoPlayer/Media3 وتخصيص الجهد لبناء خوارزمية توصية الفيديوهات التي تضاعف أرباح الشركة.",
        "trade_offs_ar": "الشراء يوفر شهوراً من وقت التطوير الأولي؛ لكنه يفرض اشتراكات دورية ويحد من إمكانية التخصيص الكامل ويتطلب حماية التطبيق من أخطاء المورد.",
        "failure_modes_ar": "أخطر الأخطاء هو متلازمة 'لم يُصنع هنا' (NIH Syndrome) وإعادة اختراع العجلة ببناء كل شيء ذاتياً، أو دمج SDKs خارجية في قلب الشاشات مباشرة دون عزل.",
        "production_perspective_ar": "في الشركات الكبرى، يُحظر دمج أي SDK خارجي إلا بعد فحص أمني وتدقيق قانوني للتأكد من خلوه من أي برمجيات تتبع غير مصرح بها.",
        "how_to_answer_ar": "ابدأ ببيان الفرق بين الميزة التنافسية والبنية التحتية العامة، واشرح مفهوم التكلفة الإجمالية TCO، وفصّل معايير الأمان وحجم الـ APK، واختم بعزل الحزم خلف Adapters لمنع الارتهان.",
        "talking_points_ar": "مصفوفة البناء أو الشراء Build vs Buy، الميزة التنافسية Core Competency، التكلفة الإجمالية TCO، متلازمة NIH Syndrome، أمان سلاسل التوريد، والارتهان للمورد Vendor Lock-in.",
        "follow_ups_ar": "كيف تقنع الإدارة ببناء ميزة ذاتياً عندما يصرون على شراء أداة خارجية رخيصة وغير آمنة؟",
        "self_check_ar": "هل فرقت بين صلب ميزة التطبيق والأدوات العامة، وذكرت كلفة الصيانة المستمرة، وأكدت على عزل الحزم خلف Interfaces؟",
        "references_ar": f"- [Martin Fowler: Build vs Buy](https://martinfowler.com/) — المرجع الهندسي الكلاسيكي لتقييم الجدوى الاقتصادية والمعمارية لقرارات البناء والشراء.\n- [Google Play: Understanding SDK requirements and Privacy](https://developer.android.com/google/play/requirements/sdk) — الإرشادات الرسمية لشركة جوجل لتقييم أمان حزم الطرف الثالث وحماية خصوصية المستخدمين.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نقرر البناء الذاتي للميزات التي تمثل صلب الميزة التنافسية والملكية الفكرية للمشروع لضمان السيطرة التامة عليها، بينما نشتري أو نتبنى حزماً قياسية للمهام العامة الشائعة مثل الخرائط ومعالجة الفيديو والتحليلات. ونقيم التكلفة الإجمالية للملكية TCO وأمان سلاسل التوريد وأثر حجم الـ APK، مع إلزام عزل أي حزمة خارجية خلف واجهة مجردة لمنع الارتهان للمورد.""",
        "best_answer_ar": """يرتكز قرار البناء الذاتي مقابل الشراء على تقييم هندسي واستراتيجي دقيق يوازن بين تعظيم القيمة التجارية وإدارة المخاطر التشغيلية.
تتمثل نقطة الانطلاق في تحديد الميزة التنافسية الجوهرية للشركة؛ فإذا كانت الوظيفة البرمجية تمثل صلب الابتكار التجاري وخوارزميات العمل الحصرية، نبنيها ذاتياً لضمان الاحتفاظ بالملكية الفكرية والتحكم الكامل في الأداء.
أما الخدمات العامة المشتركة مثل مشغلات الفيديو أو بوابات الدفع أو الخرائط، فالشراء أو تبني مكتبات مفتوحة المصدر ناضجة يوفر شهوراً من العمل غير المجدي.
وتخضع الحزم الخارجية لمصفوفة تقييم شاملة تحسب التكلفة الإجمالية للملكية بما فيها أعباء التحديثات وتوافق أندرويد، وتدقق في أمان سلاسل التوريد لمنع تسريب بيانات المستخدمين، وتفحص أثرها على حجم الـ APK.
والقاعدة المعمارية الصارمة هي تطويق أي حزمة خارجية معتمدة خلف واجهة وسيطة بنمط Adapter لعزل منطق الأعمال وتسهيل استبدال المورد مستقبلاً دون تكلفة.""",
        "deep_answer_ar": """من منظور الاستراتيجية الهندسية واقتصاديات البرمجيات المؤسسية، يمثل قرار البناء أو الشراء تخصيصاً استراتيجياً لرأس المال البشري والتقني للشركة.
تعاني الفرق الهندسية من انحرافين متناقضين: متلازمة 'لم يُصنع هنا' حيث يهدر المطورون شهوراً في إعادة بناء أدوات شائعة كمحمل الصور لتحقيق متعة شخصية على حساب أهداف الشركة، أو الاندفاع الأعمى لدمج عشرات الحزم الخارجية غير المفحوصة لتوفير ساعات عمل بسيطة، مما يورط التطبيق في أحجام ضخمة وثغرات أمنية كارثية.
ويتعامل القائد التقني مع المسألة بحيادية واعية؛ فيحدد أولاً ما إذا كانت الوظيفة تقع في صميم التمايز التجاري للشركة، مثل خوارزميات التسعير اللحظي أو محركات المزامنة غير المتصلة؛ فهنا يكون البناء الداخلي استثماراً حتمياً في أصول الشركة.
أما للبنى التحتية العامة، فنحسب التكلفة الإجمالية للملكية؛ فالأدوات المفتوحة المصدر تفرض كلفة صيانة خفية تشمل ترقيات التبعيات ومشاكل التوافق مع إصدارات أندرويد الحديثة وقيود محاذاة صفحات الذاكرة 16KB.
كما ندقق في الأذونات وشروط الخصوصية لضمان الامتثال للوائح الدولية.
وعند الاستقرار على الشراء أو التبني، نطبق عزلاً معمارياً صارماً؛ فنلزم المطورين بوضع الحزمة خلف واجهة نطاق نقية Ports & Adapters، مما يمنع تسرب رموز المكتبة للشاشات، ويتيح للشركة التبديل بين مزودي الخدمات في أيام معدودة عند تغير الأسعار أو توقف الدعم الفني."""
    }
}

# ==========================================
# LEAD-11: A team disagrees about MVVM vs MVI. How do you lead a decision based on constraints?
# ==========================================
DATA["LEAD-11"] = {
    "concept_en": """Resolving architectural stalemates between MVVM and MVI requires moving past subjective dogma and anchoring the decision in empirical constraints, UI complexity, and team capabilities:
- Deconstructing the Ideological Conflict:
  - MVVM (Model-View-ViewModel): Multiple observable StateFlow streams, lightweight boilerplate, minimal object allocation, intuitive mental model, but risks race conditions and fragmented UI state.
  - MVI (Model-View-Intent): Strict single immutable State object, explicit Intent/Event stream, unidirectional data flow (UDF), high traceability and time-travel debugging, but introduces verbose boilerplate and memory churn from continuous state copy allocations.
- The 4-Step Leadership Consensus Framework:
  1. Depolarize the Room:
     - Reframe the disagreement from \"Which pattern is objectively superior?\" to \"Which set of trade-offs best matches our specific screens, scale, and performance constraints?\"
  2. Map Screen Complexity to Pattern Fitness:
     - MVI shines in complex, multi-stream, highly interactive flows with tight concurrency constraints (e.g., Checkout funnels, Live audio editing, Financial trading screens).
     - MVVM excels in standard CRUD, dashboard, and settings screens where rapid iteration and minimal boilerplate are paramount.
  3. Run an Empirical Timeboxed Spike (The POC Shootout):
     - Have proponents implement the identical non-trivial screen in both paradigms.
     - Measure concrete metrics: lines of boilerplate, recomposition counts in Compose, memory allocations via Memory Profiler, and test ergonomics.
  4. Establish Pragmatic Hybrid Standards:
     - Unify the team around a \"Pragmatic UDF\" standard: single immutable `UiState` via `StateFlow` (leveraging MVI's predictability) paired with simple ViewModel functions for events (retaining MVVM's simplicity).""",
    "walkthrough_en": """Leading architectural consensus with a Pragmatic UDF pattern in Kotlin:
```kotlin
// The Pragmatic Compromise: Combines MVI's predictable state with MVVM's ergonomic simplicity
data class ProductListUiState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val errorMessage: String? = null
)

class ProductListViewModel(
    private val getProductsUseCase: GetProductsUseCase
) : ViewModel() {

    // MVI STRENGTH: Single immutable source of truth for the entire UI
    private val _uiState = MutableStateFlow(ProductListUiState(isLoading = true))
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    // MVVM STRENGTH: Direct, readable function calls instead of bloated Sealed Intent hierarchies
    fun onRefreshTriggered() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val result = getProductsUseCase()
            _uiState.update { current ->
                when (result) {
                    is Result.Success -> current.copy(isLoading = false, products = result.data)
                    is Result.Failure -> current.copy(isLoading = false, errorMessage = result.error)
                }
            }
        }
    }
}
```""",
    "short_en": """Lead the MVVM versus MVI decision by neutralizing ideological dogma and grounding the choice in screen complexity and team constraints. Run an empirical proof-of-concept to measure memory allocations and boilerplate, mapping MVI to complex transactional flows and MVVM to standard screens, or unify the team around a pragmatic Unidirectional Data Flow compromise.""",
    "structured_en": """Resolving architectural disagreements between MVVM and MVI requires depolarizing the debate and focusing on concrete engineering constraints.
Dogmatic debates over architectural patterns waste team energy. A senior leader re-centers the conversation on the specific needs of the product and team.
We analyze the architectural trade-offs objectively. MVVM offers lower boilerplate, less memory allocation churn, and an intuitive learning curve, but can lead to fragmented state across multiple observables. MVI provides uncompromising state predictability and effortless debugging through a single immutable state and explicit intents, but introduces significant boilerplate and continuous copy allocations.
To reach consensus, we run a timeboxed spike where both patterns implement the same feature, measuring boilerplate, Compose recomposition efficiency, and test readability.
Frequently, the optimal leadership solution is establishing a pragmatic hybrid standard: adopting MVI\'s single immutable UiState data class while preserving MVVM\'s readable ViewModel event functions, achieving predictability without verbosity.""",
    "deep_senior_en": """From an engineering leadership, organizational psychology, and Android presentation architecture perspective, arbitrating architectural debates is a masterclass in driving consensus through empirical evidence rather than authority.
When engineering teams splinter into rival camps debating MVVM versus MVI, the conflict is rarely about code—it is about competing engineering values. One group prioritizes developer velocity and simplicity; the other prioritizes mathematical predictability and state immutability. An authoritarian decision by the lead creates resentment and passive resistance.
A senior leader de-escalates the tension by establishing an empirical decision matrix. We acknowledge the validity of both viewpoints and define the operational constraints: our team\'s familiarity with unidirectional data flow, the performance profile of low-end target hardware, and the complexity spectrum of our screens.
To eliminate subjective conjecture, we commission a two-day comparative spike. Two engineers build the identical complex checkout screen using both architectures. We profile the implementations using the Android Studio Allocation Tracker and Compose Layout Inspector.
The data illuminates the trade-offs: MVI provides flawless state replayability for complex checkout steps, but generates noticeable heap churn due to constant data class copying. MVVM compiles faster and requires fifty percent fewer lines of code, but suffers from state synchronization edge cases when multiple StateFlows emit asynchronously.
With data in hand, we guide the team toward a pragmatic Unidirectional Data Flow (UDF) standard that captures the best of both worlds: a single immutable UiState data class exposed via StateFlow (honoring MVI\'s predictability), paired with idiomatic ViewModel public methods for handling user actions (honoring MVVM\'s simplicity). Documenting this consensus in an ADR solidifies team unity and elevates codebase consistency.""",
    "meta_ar": {
        "id": "LEAD-11",
        "questionAr": "اختلف أعضاء الفريق بين اعتماد نمط MVVM ونمط MVI. كيف تقود اتخاذ القرار بناءً على القيود الهندسية والواقعية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدارة الخلافات المعمارية في الفريق، تفكيك المقارنة بين MVVM وMVI بنزاهة، الاعتماد على البيانات عبر النماذج المقارنة (Spike POC)، والوصول لحل توفيقي عملي (Pragmatic UDF).",
        "concept_ar": "يتطلب حسم الخلاف المعماري بين نمطي MVVM وMVI تجريد النقاش من التعصب الأيديولوجي وإعادة توجيهه نحو القيود الواقعية وطبيعة الشاشات وخبرات الفريق: يكمن الخلاف في أن مؤيدي MVVM يبحثون عن البساطة وقلة الكود وسرعة الإنجاز مع خفة استهلاك الذاكرة؛ بينما يبحث مؤيدو MVI عن الحتمية المطلقة والتتبع الدقيق وسهولة تصحيح الأخطاء عبر حالة واحدة غير قابلة للتغيير وتدفق أحادي (UDF)، رغم كثرة الكود المكرر وتكلفة استنساخ الكائنات. ويقود القائد التقني الحسم عبر 4 خطوات: أولاً، نزع فتيل التعصب بتحويل السؤال من 'أيهما أفضل؟' إلى 'أي المقايضات أنسب لمشروعنا الحالي؟'؛ ثانياً، تقسيم الشاشات حسب التعقيد (فالمعاملات المالية المعقدة تناسبها MVI، بينما شاشات العرض البسيطة تناسبها MVVM)؛ ثالثاً، إجراء تجربة عملية محددة زمنياً (Spike) لبناء نفس الشاشة بالنمطين وقياس أداء الذاكرة وعدد الأسطر؛ رابعاً، توحيد الفريق حول حل توفيقي براغماتي يجمع أفضل ما في الاثنين: كائن حالة واحد مجمع `UiState` لضمان الحتمية (جوهر MVI)، مع دوال عادية واضحة في الـ ViewModel لتفادي تضخم الكود (جوهر MVVM).",
        "walkthrough_ar": """تطبيق الحل التوفيقي البراغماتي (Pragmatic UDF) الجامع لمزايا MVVM وMVI في كوتلن:
```kotlin
// الحل التوفيقي: حالة واحدة مجمعة (ميزة MVI) مع دوال صريحة ومباشرة (ميزة MVVM)
data class ProductListUiState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val errorMessage: String? = null
)

class ProductListViewModel(
    private val getProductsUseCase: GetProductsUseCase
) : ViewModel() {

    // جوهر قوة MVI: مصدر أحادي غير قابل للتغيير يمثل كامل الشاشة بدقة
    private val _uiState = MutableStateFlow(ProductListUiState(isLoading = true))
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    // جوهر قوة MVVM: دوال واضحة وقابلة للقراءة بدلاً من صياغة كائنات Intent معقدة
    fun onRefreshTriggered() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val result = getProductsUseCase()
            _uiState.update { current ->
                when (result) {
                    is Result.Success -> current.copy(isLoading = false, products = result.data)
                    is Result.Failure -> current.copy(isLoading = false, errorMessage = result.error)
                }
            }
        }
    }
}
```""",
        "why_it_matters_ar": "الجدال المعماري العقيم يستهلك طاقة الفريق ويخلق انقسامات داخلية ويعطل إنجاز الميزات ويجعل قاعدة الكود مشتتة بين عدة أنماط متنافرة.",
        "worked_example_ar": "انقسم الفريق حول الشاشات؛ بنينا شاشة سلة الشراء بالنمطين؛ أظهر الفحص أن MVI أسهل في تتبع أخطاء الدفع فاعتمدناه لمسار الشراء، بينما اعتمدنا نمط UDF المبسط لباقي الشاشات وتوافق الجميع.",
        "trade_offs_ar": "MVI يقدم حتمية مطلقة لكنه يولد كائنات كثيرة في الذاكرة؛ بينما MVVM سريع ومباشر لكنه قد يشتت الحالة بين عدة متغيرات؛ والحل البراغماتي يوازن بينهما.",
        "failure_modes_ar": "أخطر الأخطاء هو فرض قرار ديكتاتوري من القائد دون إقناع الفريق بالأدلة، أو ترك كل مطور يكتب بنمطه الخاص مما يدمر اتساق الكود.",
        "production_perspective_ar": "في تطبيقات أندرويد الحديثة مع Jetpack Compose، تتبنى الفرق العالمية نمط UDF البراغماتي كحل قياسي معتمد وموصى به رسمياً من جوجل.",
        "how_to_answer_ar": "ابدأ ببيان أسباب الخلاف وفلسفة كل نمط، واشرح كيفية نزع فتيل التعصب، ثم اعرض فكرة الـ Spike والقياس العملي، واختم بالحل التوفيقي البراغماتي Pragmatic UDF.",
        "talking_points_ar": "نمط MVVM مقابل MVI، التدفق الأحادي للبيانات UDF، كائن الحالة الموحد UiState، استهلاك الذاكرة Copy allocations، النموذج التجريبي المقارن Spike، والحل التوفيقي البراغماتي.",
        "follow_ups_ar": "كيف يؤثر تكرار استخدام copy() في MVI على استهلاك الذاكرة وعمليات الـ Garbage Collection في الأجهزة الضعيفة؟",
        "self_check_ar": "هل تجنبت الانحياز لنمط معين، وشرحت مميزات وعيوب كل نمط بنزاهة، وطرحت الحل التوفيقي العملي المدعوم بكود كوتلن؟",
        "references_ar": f"- [Android Developers: Guide to app architecture - UI Layer](https://developer.android.com/topic/architecture/ui-layer) — الدليل الرسمي لهندسة واجهات أندرويد واعتماد التدفق الأحادي للبيانات UDF.\n- [Hannes Dorfmann: Reactive Apps with Model-View-Intent](https://hannesdorfmann.com/android/mosby3-mvi-1/) — السلسلة الهندسية التأسيسية التي أدخلت نمط MVI لعالم تطوير أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نقود حسم الخلاف بنزع فتيل التعصب الأيديولوجي والتركيز على قيود المشروع وطبيعة الشاشات وخبرة الفريق. نجري تجربة عملية Spike لبناء نفس الشاشة بالنمطين وقياس حجم الكود والذاكرة وسهولة الاختبار، ونوجه الفريق نحو حل توفيقي براغماتي يجمع بين كائن الحالة الموحد من MVI ودوال الأحداث المباشرة البسيطة من MVVM.""",
        "best_answer_ar": """يتطلب حل الخلافات المعمارية حول أنماط العرض مثل MVVM وMVI قيادة تقنية واعية تجرد الحوار من الجدال النظري وتعيده إلى أرض الواقع والبيانات.
ينطلق القائد من تحليل موضوعي للمقايضات؛ فنمط MVVM يوفر سرعة في الإنجاز وكوداً أقل واستهلاكاً ضئيلاً للذاكرة لكنه قد يشتت الحالة بين تدفقات متعددة، بينما يوفر نمط MVI حتمية تامة وتتبعاً دقيقاً للأخطاء بحالة واحدة مجمعة لكنه يستهلك ذاكرة إضافية ويولد كوداً مكرراً.
ولحسم الخلاف بطريقة علمية تبني التوافق، نطلق مهمة استكشافية مصغرة لبناء شاشة معقدة بالنمطين وقياس زمن التجميع، واستهلاك الذاكرة، وسهولة كتابة اختبارات الوحدة.
وغالباً ما يقود هذا التحليل الموضوعي إلى اعتماد نموذج توفيقي براغماتي يوصى به في Jetpack Compose؛ يعتمد على كائن حالة موحد غير قابل للتعديل UiState يمثل كامل الشاشة اقتباساً من قوة MVI، مع إدارته عبر دوال مباشرة وسهلة القراءة في الـ ViewModel اقتباساً من بساطة MVVM، مما يوحد الفريق خلف معيار معماري متزن.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وعلم النفس المؤسسي وإدارة الفرق التقنية، يعد التحكيم في الخلافات المعمارية اختباراً دقيقاً للقدرة على بناء التوافق بالأدلة الموضوعية لا بالسلطة الإدارية الجافة.
فالخلاف بين MVVM وMVI في جوهره صراع بين قيمتين هندسيتين مشروعتين: فريق يعلي من شأن البساطة والإنتاجية السريعة، وفريق يقدس الحتمية الرياضية والأمان ضد أخطاء التزامن. والفرض القسري لأحد النمطين من القائد يخلق مقاومة سلبية ويضعف الروح المعنوية للفريق.
ويقود القائد التقني الحوار بحكمة عبر إرساء مصفوفة تقييم محايدة تستند إلى قيود المشروع: إمكانيات أجهزة المستخدمين الاقتصادية، ومستوى تعقيد الشاشات، ومنحنى التعلم لأعضاء الفريق.
ولإنهاء الجدال الشفهي، ننفذ نموذجاً مقارناً ليومين؛ حيث يُبنى مسار دفع معقد بالنمطين، وتُفحص النتيجة بمحلل الذاكرة ومراقب إعادة التركيب في Compose.
تكشف الأرقام الحقائق بوضوح: يثبت MVI كفاءة مذهلة في تتبع خطوات الدفع المعقدة، لكنه يسبب إجهاداً في الذاكرة لكثرة استنساخ الكائنات؛ بينما يوفر MVVM نصف حجم الكود ويستهلك ذاكرة أقل، لكنه يعاني من بعض ثغرات تزامن الحالات.
وبناءً على هذه البراهين، نوجه الفريق نحو صياغة معيار موحد نطلق عليه UDF البراغماتي؛ نلزم فيه الشاشة بالاعتماد على كائن حالة موحد وحصري UiState عبر StateFlow لضمان الحتمية وسهولة الاختبار، مع استبدال التسلسل الهرمي لكائنات الـ Intent بدوال برمجية عادية ومباشرة في الـ ViewModel.
نوثق هذا الاتفاق في مستند ADR دائم، ليخرج الفريق موحداً خلف معمارية تجمع الأمان والإنتاجية بانسجام تام."""
    }
}

# ==========================================
# LEAD-12: Tell me about a production incident you owned and how you prevented recurrence.
# ==========================================
DATA["LEAD-12"] = {
    "concept_en": """Answering production incident ownership questions requires demonstrating calmness under pressure, structured incident commanding, decisive technical triage, and permanent systemic remediation:
- The Senior STAR Incident Narrative:
  - Situation: A high-stakes production failure affecting real users and business revenue (e.g., a thundering-herd retry storm after an authentication token expiration during peak traffic).
  - Task: Establish incident command, stop active bleeding, stabilize customer experience, coordinate cross-functional communication, and execute root-cause remediation.
  - Action:
    1. Immediate Mitigation (Stop the Bleed): Halt the Google Play phased rollout, toggle an emergency remote config kill-switch to degrade non-essential features, and coordinate with backend SRE to shed load.
    2. Tactical Root Cause Analysis: Isolate the defect using Android Profiler and Datadog telemetry: an aggressive, un-jittered OkHttp retry interceptor overwhelmed the auth switch when 401 tokens expired simultaneously.
    3. Emergency Patch & Deployment: Implement an exponential backoff with randomized jitter and token deduplication, verify via automated tests, and deploy a hotfix build.
  - Result & Permanent Prevention:
    - Restored 99.95% crash-free sessions within 45 minutes of discovery.
    - Conducted a blameless postmortem resulting in two permanent systemic guards: an automated custom Detekt lint rule banning synchronous retry loops, and a mandatory chaos-engineering load test verifying client token expirations prior to future releases.""",
    "walkthrough_en": """Resilient client-side token refresh and exponential backoff interceptor in Kotlin:
```kotlin
// Tactical remediation: Preventing thundering-herd token storms via Mutex and backoff
class TokenRefreshAuthenticator(
    private val tokenApi: TokenApiService,
    private val sessionManager: SessionManager
) : Authenticator {

    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent infinite loops if 401 persists
        if (responseCount(response) >= 3) return null

        val failedToken = response.request.header("Authorization")

        return runBlocking {
            refreshMutex.withLock {
                val currentToken = sessionManager.getAccessToken()

                // If another concurrent thread already refreshed the token, reuse it directly
                val validToken = if (currentToken != failedToken && currentToken != null) {
                    currentToken
                } else {
                    // Execute single-flight refresh with backoff jitter
                    val newToken = tokenApi.refreshToken(sessionManager.getRefreshToken())
                    sessionManager.saveAccessToken(newToken)
                    newToken
                }

                response.request.newBuilder()
                    .header("Authorization", "Bearer $validToken")
                    .build()
            }
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}
```""",
    "short_en": """Own a production incident by establishing calm incident command, halting active rollouts, and deploying remote kill-switches to stabilize users. Isolate root causes using telemetry, coordinate hotfixes with cross-functional teams, and prevent recurrence permanently by codifying systemic guards like automated lint checks and chaos testing during blameless postmortems.""",
    "structured_en": """Managing a production incident requires decisive leadership, rapid containment, and permanent systemic prevention.
Using the STAR framework, the response centers on a real-world scenario, such as an authentication retry storm that triggered a thundering-herd backend outage.
My immediate action as incident commander was containing the damage: pausing the staged Google Play rollout and toggling a remote config feature flag to throttle client retries.
Simultaneously, I established clear cross-functional communication channels with backend, product, and customer support leads.
Once telemetry localized the defect to a non-jittered retry loop in our networking layer, I authored a targeted fix incorporating exponential backoff and mutex-locked token refresh, verifying it with automated tests before releasing an expedited hotfix.
Crucially, I led a blameless postmortem that institutionalized permanent guards: adding an automated CI lint rule that prohibits unconstrained network retries and integrating chaos token-expiry tests into our staging deployment pipeline.""",
    "deep_senior_en": """From an engineering leadership, crisis management, and site reliability perspective, handling high-severity production outages reveals a leader\'s true technical composure and operational judgment.
During a major shopping holiday, our mobile app experienced a severe cascading failure. When the backend authentication service restarted, thousands of mobile clients received simultaneous 401 Unauthorized errors. Because our networking layer lacked jittered backoff, two hundred thousand devices launched concurrent token refresh requests every two seconds, creating a self-inflicted Distributed Denial of Service (DDoS) storm that crippled the backend auth cluster and caused rapid mobile battery drain and UI freezing.
Assuming the role of Incident Commander, my priority was operational containment over finger-pointing.
First, I ordered an immediate halt to our Google Play rollout and activated a Firebase Remote Config emergency kill-switch, instructing active client apps to enter a degraded guest mode and backing off refresh intervals to sixty seconds. This reduced inbound traffic by ninety percent, allowing the backend infrastructure to recover.
Second, I mobilized a focused war room, maintaining a transparent status log for executive stakeholders and support agents.
Third, I designed the technical remediation: rewriting the OkHttp Authenticator using a Kotlin Mutex to coalesce concurrent refresh requests into a single-flight operation and injecting randomized exponential jitter to smooth reconnect traffic.
After verifying the patch through rigorous network simulation tests, we shipped an expedited hotfix within three hours.
Finally, I facilitated a blameless postmortem. We converted our findings into permanent structural defenses: writing a custom Detekt rule banning un-throttled retry interceptors, and adding a mandatory automated Chaos Monkey test in staging that randomly expires tokens under simulated peak concurrency. This ensured that our systems emerged far more resilient than before the outage.""",
    "meta_ar": {
        "id": "LEAD-12",
        "questionAr": "حدثني عن واقعة عطل فني في بيئة الإنتاج (Production Incident) توليت قيادتها وكيف منعت تكرارها نهائياً؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القيادة والهدوء تحت الضغط، تطبيق نموذج STAR في سرد الحوادث الواقعية، إدارة الأزمات وإيقاف النشر (Incident Command & Containment)، والحل الجذري المؤتمت لمنع تكرار العطل.",
        "concept_ar": "تتطلب الإجابة عن تجربة قيادة عطل فني في بيئة الإنتاج (Production Incident) استخدام نموذج STAR باحترافية لإبراز رباطة الجأش تحت الضغط، والقيادة التشغيلية السريعة لاحتواء العطل، والقدرة على ابتكار حلول وقائية مؤتمتة تمنع تكراره نهائياً: تبدأ القصة بتوصيف الموقف (Situation)؛ مثل عطل تسببت فيه عاصفة إعادة المحاولة (Retry Storm) عند انتهاء صلاحية رموز تسجيل الدخول بالتزامن مع ذروة استخدام التطبيق مما أغرق الخوادم وجمد الشاشات. وتتمثل المهمة (Task) في قيادة غرفة الطوارئ، ووقف النزيف فوراً، وحماية تجربة المستخدم، والتنسيق الشفاف مع فرق الخوادم والدعم الفني. وتتضمن الإجراءات (Actions): إيقاف النشر التدريجي على المتجر فوراً، وتفعيل قاطع الأعطال السحابي (Remote Config) لتخفيف الضغط، وكتابة حل جذري يعتمد على دمج الطلبات المتزامنة (Mutex) والتراجع الأسي العشوائي (Jitter). وتنتهي النتائج (Results) باستعادة الاستقرار خلال 45 دقيقة، وإجراء مراجعة خالية من اللوم تمخضت عن إضافة فحص آلي في Lint واختبارات فوضى مؤتمتة (Chaos Testing) لمنع تكرار الخطأ نهائياً.",
        "walkthrough_ar": """كود المعالجة الجذرية لمنع عواصف إعادة المحاولة وحماية الخوادم في كوتلن:
```kotlin
// المعالجة الجذرية للعطل: دمج طلبات تحديث الرمز المتزامنة عبر Mutex لمنع إغراق الخادم
class TokenRefreshAuthenticator(
    private val tokenApi: TokenApiService,
    private val sessionManager: SessionManager
) : Authenticator {

    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        // منع الحلقات المفرغة إذا استمر الخطأ 401
        if (responseCount(response) >= 3) return null

        val failedToken = response.request.header("Authorization")

        return runBlocking {
            refreshMutex.withLock {
                val currentToken = sessionManager.getAccessToken()

                // إذا قام خيط متزامن آخر بتحديث الرمز مسبقاً، نستخدمه فوراً دون اتصال جديد
                val validToken = if (currentToken != failedToken && currentToken != null) {
                    currentToken
                } else {
                    // تحديث مفرد للرمز مع تراجع أسي عشوائي (Jitter)
                    val newToken = tokenApi.refreshToken(sessionManager.getRefreshToken())
                    sessionManager.saveAccessToken(newToken)
                    newToken
                }

                response.request.newBuilder()
                    .header("Authorization", "Bearer $validToken")
                    .build()
            }
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) { count++; prior = prior.priorResponse }
        return count
    }
}
```""",
        "why_it_matters_ar": "الحوادث الفنية في الإنتاج تختبر القيادة الحقيقية للمهندس؛ والارتباك أو إلقاء اللوم يدمر استقرار المنظومة ويكبد الشركة ملايين الدولارات.",
        "worked_example_ar": "تسببت حلقة إعادة محاولة في استنزاف بطاريات 50 ألف مستخدم؛ قدت غرفة الطوارئ، وفعلت قاطع أعطال سحابي هدأ الطلبات خلال 10 دقائق، ثم أطلقنا تحديثاً يحتوي على Jitter حل المشكلة للأبد.",
        "trade_offs_ar": "تفعيل قاطع الأعطال يعطل ميزات فرعية للمستخدمين مؤقتاً؛ لكنه ينقذ النظام الرئيسي من الانهيار التام ويمنع خروج التطبيق عن الخدمة.",
        "failure_modes_ar": "أخطر الأخطاء أثناء الأزمات هو التسرع في دفع كود عشوائي للإنتاج دون اختبار مما يضاعف العطل، أو الانشغال بالبحث عن المخطئ بدلاً من احتواء الحادث.",
        "production_perspective_ar": "في كبرى الشركات، يقاس نجاح إدارة الحادث بـ MTTR (متوسط زمن استعادة الخدمة) وبناء أدوات دفاع آلية في الـ CI تمنع تكرار نفس السيناريو مستقبلاً.",
        "how_to_answer_ar": "طبق نموذج STAR بدقة: ابدأ بحادث حقيقي مؤثر، واشرح دورك كقائد للحادث واحتواء النزيف أولاً بوقف النشر وRemote Config، ثم اشرح الحل التقني، واختم بالحماية الآلية الدائمة.",
        "talking_points_ar": "نموذج STAR، قيادة الحوادث Incident Commander، وقف النزيف Containment، قواطع الأعطال Remote Config، عواصف إعادة المحاولة Retry Storms، والتراجع الأسي مع Jitter.",
        "follow_ups_ar": "كيف تدير التواصل مع الإدارة التنفيذية وخدمة العملاء أثناء العطل لتهدئة القلق دون تشتيت فريق الطوارئ؟",
        "self_check_ar": "هل استخدمت نموذج STAR، وأكدت على احتواء العطل أولاً قبل البرمجة، وذكرت إجراءات وقائية مؤتمتة منعت تكراره نهائياً؟",
        "references_ar": f"- [Google SRE: Managing Incidents](https://sre.google/sre-book/managing-incidents/) — الدليل العالمي لإدارة حوادث الإنتاج والقيادة التقنية أثناء الأزمات البرمجية.\n- [AWS Architecture: Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — المرجع الهندسي لتصميم خوارزميات التراجع الأسي وتفادي عواصف السحب المتزامن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """قدت معالجة عطل إنتاج ناتج عن عاصفة إعادة محاولة متزامنة أغرقت الخوادم بتطبيق نموذج STAR. قمت فوراً باحتواء العطل كقائد للحادث بإيقاف النشر التدريجي على المتجر وتفعيل قاطع أعطال سحابي لتهدئة حركة البيانات، ثم صممت حلاً يعتمد على التراجع الأسي العشوائي Jitter ودمج الطلبات عبر Mutex، ومنعنا تكراره نهائياً بإضافة قواعد فحص آلي في الـ CI واختبارات فوضى مستمرة.""",
        "best_answer_ar": """تتطلب قيادة حوادث الإنتاج الحرجة هدوءاً وثباتاً تحت الضغط مع سرعة في احتواء الأثر ومنهجية وقائية تمنع تكرار الخلل.
أجيب عن هذا السؤال مستخدماً نموذج STAR؛ ففي أحد مواسم التسوق الكبرى، تعرض التطبيق لخلل تسلسلي ناتج عن انتهاء صلاحية رموز المصادقة بالتزامن مع توقف مؤقت للخادم، فقامت آلاف الهواتف بإعادة إرسال طلبات متزامنة في نفس الثانية، مما تسبب في عاصفة بيانات أغرقت خوادم الهوية وجمدت الشاشات.
وتوليت فوراً قيادة غرفة الطوارئ؛ فبدأت بوقف النزيف أولاً بإيقاف النشر التدريجي على Google Play وتفعيل قاطع أعطال سحابي عبر Remote Config لتحويل الطلبات إلى وضع القراءة فقط ورفع فترة الانتظار، مما خفض الضغط بنسبة 90% ومكن الخوادم من التعافي.
وبالتوازي، نسقت قنوات التواصل مع فرق الإدارة والدعم الفني، وكتبت حلاً تقنياً يعتمد على دمج طلبات التحديث عبر Mutex وتطبيق التراجع الأسي العشوائي Jitter لمنع التزامن.
وبعد التحقق الصارم، أطلقنا التحديث الطارئ بنجاح، وعقدنا مراجعة خالية من اللوم أثمرت عن إضافة فحص آلي في Lint يمنع أي إعادة محاولة دون تراجع، واختبارات فوضى مؤتمتة في بيئة الاختبار لضمان عدم تكرار الحادث نهائياً.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وإدارة الأزمات التقنية وموثوقية النظم SRE، تكشف حوادث الإنتاج الكبرى عن النضج القيادي والاتزان النفسي للمهندس تحت وطأة الضغوط التشغيلية.
في أحد مواسم الذروة التجارية، واجه تطبيقنا انهياراً تسلسلياً حرجاً؛ فعند إعادة تشغيل خادم المصادقة، استقبلت مئات الآلاف من الهواتف خطأ أربعمائة وواحد في نفس اللحظة. ونظراً لغياب التراجع العشوائي في معترض الشبكة القديم، شنت الأجهزة هجوماً متزامناً شل البنية التحتية بالكامل وتسبب في استنزاف بطاريات هواتف المستخدمين وتجمد الشاشات.
وبصفتي قائداً للحادث، كان تركيزي الأساسي منصباً على احتواء الخطر وليس البحث عن المتسبب.
بادرت فوراً باتخاذ ثلاثة قرارات حاسمة: أولاً، تجميد النشر التدريجي على متجر جوجل؛ ثانياً، إطلاق أمر سحابي عبر Firebase Remote Config لتفعيل نمط التصفح الاقتصادي وزيادة فترات إعادة المحاولة لدقيقة كاملة، مما هدأ حركة المرور وسمح للخوادم باستعادة عافيتها.
ثالثاً، توليت إدارة الاتصال المؤسسي بتحديث الإدارة وخدمة العملاء بتقارير دورية كل عشرين دقيقة لمنع تشتيت فريق المهندسين.
ثم قدت كتابة الحل المعماري الرصين؛ حيث أعدنا بناء معترض المصادقة في OkHttp باستخدام كوتلن Mutex لدمج طلبات التحديث المتزامنة في اتصال شبكي واحد، مع حقن تراجع أسي عشوائي Full Jitter لتوزيع الأحمال اللحظية.
وبعد إطلاق التحديث الطارئ واستعادة الاستقرار الكامل، أدرت جلسة مراجعة خالية من اللوم تمخضت عن بناء حصانة مؤسسية مستدامة: كتبنا قاعدة فحص مخصصة في Detekt تمنع دمج أي معترض شبكة يفتقر للتراجع العشوائي، وأضفنا اختبارات فوضى مؤتمتة تفصل رموز المصادقة عشوائياً تحت أقصى أحمال المحاكاة، ليخرج الفريق والمنظومة أكثر قوة ومناعة ضد أي مفاجآت مستقبلية."""
    }
}

# ==========================================
# LEAD-13: You discover a critical vulnerability days before launch. What is your release decision process?
# ==========================================
DATA["LEAD-13"] = {
    "concept_en": """Discovering a critical security vulnerability days before a major release requires disciplined risk classification, transparent stakeholder governance, and a multi-option decision matrix:
- The Senior Crisis Mindset:
  - Never succumb to launch fever by hiding or downplaying a genuine security defect to hit a marketing date.
  - Never panic and trigger an uncoordinated cancellation without exploring technical mitigation options.
- The 4-Stage Security Triage and Decision Process:
  1. Technical Triage & Exploitability Assessment (CVSS Framework):
     - Calculate Common Vulnerability Scoring System (CVSS) score: Attack Vector (Remote vs Physical access), Privileges Required, Data Exposure (PII, Auth tokens, Financial data vs cosmetic leaks).
     - Is the vulnerability actively exploitable in the wild, or does it require an already-rooted device with custom tooling?
  2. The 3-Option Engineering Decision Matrix:
     - Option A: Emergency Surgical Hotfix: If the fix is isolated (e.g., adding `android:exported="false"` to a leaked ContentProvider or updating an SDK), patch immediately, run targeted automated regression tests, and proceed with launch.
     - Option B: Dark Launch via Feature Flag: If the vulnerability resides in a new, non-essential feature, launch on schedule but keep the vulnerable feature permanently disabled remotely via Remote Config until properly remediated.
     - Option C: Hard Release Halt (The Red Line): If the vulnerability affects the core authentication, payment, or data encryption engine and cannot be patched without high regression risk, enforce an immediate release freeze.
  3. Executive & Cross-Functional Alignment:
     - Present findings objectively to the VP of Engineering, Product Lead, and Legal/Security Officer: explain the technical blast radius, estimated remediation duration, and business trade-offs.
  4. Controlled Verification & Release:
     - Re-audit the patch with dynamic security analysis tools and obtain formal sign-off from the Information Security team prior to binary promotion.""",
    "walkthrough_en": """Security Triage Matrix and Emergency Remote Feature-Flag mitigation in Kotlin:
```kotlin
// Emergency Remote Mitigation: Safely disabling a vulnerable feature flag
class PaymentFeatureCoordinator(
    private val remoteConfig: FirebaseRemoteConfig,
    private val securityAuditor: SecurityAuditor
) {
    // SECURITY GATE: Evaluates remote kill-switch before opening feature
    fun isBiometricPaymentAvailable(): Boolean {
        // If critical vulnerability CVE-2026-X is unpatched, remote flag turns feature OFF globally
        val isFeatureFlagEnabled = remoteConfig.getBoolean("enable_biometric_v2")
        val isDeviceCompromised = securityAuditor.isRootOrHookDetected()

        return isFeatureFlagEnabled && !isDeviceCompromised
    }
}

// Executive Decision Brief Template:
// "We identified a Critical Vulnerability (CVSS 8.8) in the new Biometric Fast-Checkout module:
// a crafted Intent can bypass biometric prompt verification on Android 12 devices.
// Recommendation: Proceed with the scheduled app release on Friday,
// but keep 'enable_biometric_v2' set to FALSE in Remote Config.
// This preserves the marketing launch date while reducing customer risk to zero.
// We will ship the surgical patch in an expedited v4.1 update next week."
```""",
    "short_en": """Evaluate critical pre-launch vulnerabilities using the CVSS framework, assessing exploitability and blast radius. Present a structured decision matrix to leadership: apply a surgical patch if low-risk, launch with the feature disabled via remote feature flags, or enforce a hard launch halt if core security is compromised, prioritizing customer protection over marketing deadlines.""",
    "structured_en": """Discovering a critical vulnerability days before a scheduled release demands calm triage, objective risk assessment, and decisive cross-functional governance.
A senior leader never conceals a vulnerability to meet a launch deadline, nor do they panic prematurely.
The process begins with technical triage using the CVSS framework, evaluating whether the flaw enables remote exploitation, requires physical device access, or risks customer data.
We then evaluate three potential remediation paths.
First is a surgical hotfix: if the fix is isolated and low-risk, we apply the patch, execute automated regression suites, and launch on schedule.
Second is a dark launch: if the vulnerability resides in a modular new feature, we launch on time with the feature remotely disabled via feature flags, eliminating risk while preserving marketing timelines.
Third is a hard release halt: if the flaw compromises core authentication or encryption and cannot be safely patched in time, we mandate postponing the release.
We present these options transparently to executive stakeholders, securing security sign-off before deployment.""",
    "deep_senior_en": """From an enterprise cybersecurity, legal compliance, and executive technology leadership standpoint, discovering a critical zero-day vulnerability on the eve of a major product launch tests an engineering leader\'s ethical integrity and risk governance.
The pressure from business, marketing, and commercial teams to ignore the defect and \"fix it in the next update\" can be overwhelming. Conceding to this pressure is an unacceptable failure of leadership that exposes users to financial fraud, violates regulatory frameworks like GDPR or PCI-DSS, and risks catastrophic brand destruction.
My response follows an uncompromising, data-driven security protocol.
The first step is rapid vulnerability scoring using CVSS v3.1. We establish the attack vector: Can the vulnerability be triggered remotely via a malicious deep link, or does it require an attacker to physically control an unlocked, rooted device? What data is exposed: session tokens, personal records, or peripheral metadata?
With forensic data established, I convene an emergency alignment briefing with the VP of Engineering, Head of Product, and Legal Counsel. I present a clear three-path decision matrix.
If the flaw is localized—such as an exported broadcast receiver missing an explicit permission—we apply a surgical patch, run continuous integration end-to-end tests, and maintain the launch schedule.
If the vulnerability is embedded in a new feature—such as an insecure biometric payment flow—we execute the smartest business compromise: we release the binary on schedule, but use our server-driven feature flags to keep the feature dark and inaccessible globally. Marketing proceeds with the overarching launch, while engineering patches the module safely for an update.
However, if the vulnerability lies in core infrastructure—such as flawed TLS certificate pinning or an SQL injection in our local encrypted database—I enforce an unyielding red line, recommending an immediate release halt. Protecting our users\' security and corporate reputation always supersedes artificial calendar deadlines.""",
    "meta_ar": {
        "id": "LEAD-13",
        "questionAr": "اكتشفت ثغرة أمنية حرجة قبل موعد الإطلاق بأيام قليلة. كيف تدير عملية اتخاذ قرار الإطلاق والتعامل مع الموقف؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "النزاهة المهنية وحوكمة المخاطر الأمنية، تصنيف الثغرات وفق معيار (CVSS)، مصفوفة اتخاذ القرار (الإصلاح السريع، الإطلاق مع التعطيل السحابي، أو الوقف التام)، والتواصل الشفاف مع الإدارة التنفيذية.",
        "concept_ar": "يتطلب اكتشاف ثغرة أمنية حرجة قبل موعد الإطلاق بأيام قليلة شجاعة مهنية وإدارة منضبطة للأزمات تستند إلى تقييم المخاطر وتجنب التستر لإرضاء المواعيد التجارية: فالقائد التقني لا يرضخ لضغط الحملات التسويقية لتجاهل الثغرة وتأجيلها، كما لا يتصرف بهلع عشوائي. وتعتمد المنهجية على 4 خطوات: أولاً، التقييم التقني الدقيق وحساب معامل خطورة الثغرة وفق معيار CVSS (هل تتطلب وصولاً فيزيائياً للهاتف أم يمكن استغلالها عن بُعد؟ وما هي البيانات المهددة؟)؛ ثانياً، استعراض مصفوفة الخيارات الثلاثة: الخيار الأول إصلاح جراحي سريع وآمن إذا كان الخطأ بسيطاً ومحصوراً، والخيار الثاني هو الإطلاق في الموعد مع تعطيل الميزة المصابة برمجياً عن بُعد عبر مفاتيح الميزات (Feature Flags) كحل توفيقي ذكي يحمي المستخدمين ويحفظ موعد التسويق، والخيار الثالث هو الوقف التام للإطلاق كخط أحمر إذا كانت الثغرة تمس صلب التشفير أو الدفع ولا يمكن حجبها؛ ثالثاً، رفع تقرير شفاف للإدارة التنفيذية والقطاع القانوني يوضح الخيارات وتكلفتها؛ رابعاً، التحقق الأمني الكامل قبل اعتماد أي حزمة للنشر.",
        "walkthrough_ar": """تطبيق قاطع الأعطال السحابي لتعطيل الميزة المصابة أمنياً قبل الإطلاق في كوتلن:
```kotlin
// تفعيل صمام الأمان السحابي لعزل الثغرة الأمنية دون تأجيل الإطلاق
class PaymentFeatureCoordinator(
    private val remoteConfig: FirebaseRemoteConfig,
    private val securityAuditor: SecurityAuditor
) {
    // فحص أمني حاسم: التحكم السحابي في فتح الميزة للمستخدمين
    fun isBiometricPaymentAvailable(): Boolean {
        // إذا كانت الميزة تحتوي على ثغرة حرجة، يُضبط المفتاح السحابي على false فوراً
        val isFeatureFlagEnabled = remoteConfig.getBoolean("enable_biometric_v2")
        val isDeviceCompromised = securityAuditor.isRootOrHookDetected()

        return isFeatureFlagEnabled && !isDeviceCompromised
    }
}

// صيغة التقرير الأمني الموجه للإدارة التنفيذية:
// "اكتشفنا ثغرة أمنية حرجة (بتقييم 8.8 CVSS) في ميزة الدفع بالبصمة الجديدة؛
// حيث يمكن لـ Intent خبيث تجاوز شاشة التحقق في أندرويد 12.
// التوصية الهندسية: المضي قدماً في إطلاق التطبيق في موعده التسويقي المحدد يوم الجمعة،
// ولكن مع إبقاء ميزة البصمة معطلة سحابياً بنسبة 100% عبر Remote Config.
// يحقق هذا القرار المعادلة الكاملة: حماية أموال وبيانات العملاء، وتفادي خسائر تأجيل الإطلاق،
// وسنطلق التحديث المصحح للميزة الأسبوع القادم بعد اكتمال المراجعة الأمنية."
```""",
        "why_it_matters_ar": "التستر على الثغرات الأمنية للتسليم في الموعد يعرض بيانات المستخدمين للاختراق ويكبد الشركة غرامات قانونية طائلة ويدمر سمعتها التجارية.",
        "worked_example_ar": "اكتشفنا ثغرة تسرب التوكن قبل الإطلاق بيومين؛ عطلنا الميزة المصابة سحابياً عبر Remote Config وأطلقنا التطبيق في موعده، ثم أصلحنا الثغرة بتحديث فرعي بعد 3 أيام دون أي ضرر للمستخدمين.",
        "trade_offs_ar": "إيقاف الإطلاق بالكامل يحمي الأمان لكنه يسبب خسائر تسويقية؛ والحل التوفيقي الأذكى هو تعطيل الميزة المصابة سحابياً والإطلاق بالميزات السليمة.",
        "failure_modes_ar": "أخطر الأخطاء هو الرضوخ لضغط مديري التسويق وإطلاق التطبيق المخترق مع الوعد بإصلاحه لاحقاً، أو تأجيل الإطلاق بالكامل لمشكلة كان يمكن تعطيلها سحابياً بلحظة.",
        "production_perspective_ar": "في الشركات الكبرى، تفرض لجان الأمن السيبراني (InfoSec) خطوطاً حمراء حتمية: أي ثغرة بتقييم CVSS يفوق 9.0 توقف الإطلاق فوراً دون نقاش.",
        "how_to_answer_ar": "ابدأ برفض التستر على الثغرة تماماً، واشرح تقييم الخطورة بـ CVSS، ثم اطرح مصفوفة الخيارات الثلاثة (إصلاح جراحي، تعطيل سحابي، أو إيقاف الإطلاق)، واختم بالحل التوفيقي الذكي بـ Feature Flags.",
        "talking_points_ar": "معيار خطورة الثغرات CVSS، النزاهة الهندسية، مصفوفة اتخاذ القرار الثلاثية، مفاتيح الميزات Feature Flags، الخطوط الحمراء الأمنية، والتواصل مع الإدارة التنفيذية.",
        "follow_ups_ar": "ماذا تفعل إذا أصر مدير المنتج التنفيذي على الإطلاق ورفض تعطيل الميزة المصابة أو تأجيل الموعد؟",
        "self_check_ar": "هل أكدت على استحالة التستر على الثغرة، واستخدمت معيار CVSS، وطرحت خيار التعطيل السحابي الذكي كبديل لتأجيل الإطلاق بالكامل؟",
        "references_ar": f"- [FIRST: Common Vulnerability Scoring System (CVSS) v3.1](https://www.first.org/cvss/) — المعيار القياسي الدولي المعتمد لتقييم وتصنيف خطورة الثغرات الأمنية البرمجية.\n- [OWASP: Mobile Security Testing Guide (MSTG)](https://mas.owasp.org/) — الدليل المرجعي العالمي لأمن واختبار تطبيقات الهواتف المحمولة وحمايتها من الاختراق.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """ندير القرار بتقييم خطورة الثغرة أولاً بمعيار CVSS لقياس إمكانية استغلالها والأثر على البيانات. ونعرض مصفوفة خيارات واضحة على الإدارة: إصلاح جراحي سريع إذا كان الخلل محصوراً، أو الإطلاق في الموعد مع تعطيل الميزة المصابة سحابياً عبر Feature Flags لحماية المستخدمين وحفظ موعد التسويق، أو الوقف التام للإطلاق إذا كانت الثغرة تمس صلب الأمان ولا يمكن حجبها.""",
        "best_answer_ar": """يتطلب التعامل مع اكتشاف ثغرة أمنية حرجة قبل موعد الإطلاق بأيام قليلة نضجاً هندسياً يوازن بين الأمان الصارم للأصول الرقمية والالتزامات التجارية للشركة.
يرفض القائد التقني مبدأين خاطئين: التستر على الثغرة للمضي خلف الموعد التسويقي، أو الهلع العشوائي بإلغاء الإطلاق دون دراسة البدائل التقنية.
تبدأ المنهجية بتقييم موضوعي للثغرة وفق مقياس CVSS العالمي لتحديد مسار الهجوم ونوعية البيانات المهددة وما إذا كانت تتطلب صلاحيات خاصة على الهاتف.
وبناءً على المعطيات، نطرح مصفوفة قرار ثلاثية على الإدارة التنفيذية:
الخيار الأول هو الإصلاح الجراحي السريع واختباره إذا كان الخلل موضعياً ومحدود الأثر.
الخيار الثاني، وهو الأذكى تجارياً، إطلاق التطبيق في موعده المحدد مع إبقاء الميزة المصابة معطلة ومحجوبة تماماً عن بُعد عبر مفاتيح الميزات السحابية، مما يحفظ الحدث التسويقي ويقضي على المخاطر بنسبة مئة بالمئة لحين إصلاح الكود.
الخيار الثالث هو الوقف التام للإطلاق كخط أحمر حتمي إذا كانت الثغرة تمس صلب تشفير الحسابات أو المدفوعات ولا يمكن عزلها سحابياً؛ فسلامة العملاء تسبق أي مواعيد وهمية.""",
        "deep_answer_ar": """من منظور حوكمة الأمن السيبراني المؤسسي والمسؤولية الأخلاقية للقيادة التقنية، يمثل اكتشاف ثغرة أمنية عشية الإطلاق الاختبار الحاسم لشجاعة المهندس والتزامه بالمعايير المهنية.
إن الضغوط التجارية للتغاضي عن الخلل وإطلاقه في الإنتاج تمثل فخاً مدمراً يهدد الشركة بغرامات تنظيمية باهظة تحت طائلة قوانين حماية البيانات كـ GDPR وPCI-DSS، فضلاً عن تدمير ثقة العملاء نهائياً في حال استغلال الثغرة.
وتعتمد المنهجية الاحترافية على نزع المشاعر وإدارة الأزمة بلغة البيانات الفنية القاطعة.
نبدأ بحساب معامل خطورة الثغرة وفق معيار CVSS v3.1؛ فنفحص ناقل الهجوم لتحديد ما إذا كان استغلال الثغرة متاحاً عن بُعد عبر روابط الـ Deep Links، أم يتطلب تدخلاً فيزيائياً من المستخدم، مع حصر طبيعة البيانات المعرضة للتسريب كرموز المصادقة أو السجلات المالية.
وبناءً على هذه الحقائق الجنائية، أعقد اجتماعاً عاجلاً مع مسؤولي الهندسة والمنتج والقطاع القانوني لطرح مصفوفة خيارات محكمة.
إذا كان الخطأ محصوراً، ننفذ إصلاحاً جراحياً مركزاً مدعوماً باختبارات انحدار آلية.
وإذا كانت الثغرة في ميزة فرعية كالدفع بالبصمة، نلجأ للخيار الاستراتيجي الأمثل: اعتماد إطلاق النسخة في موعدها مع إغلاق الميزة المصابة عالمياً عبر Firebase Remote Config؛ مما يسمح للحملة التسويقية بالانطلاق دون تعريض عميل واحد للخطر.
أما إذا ضربت الثغرة صلب منظومة التشفير أو الجلسات، أفرض خطاً أحمر لا يقبل المساومة بتعليق الإطلاق فوراً، فسمعة المؤسسة وسلامة بيانات مستخدميها تتقدم حتماً على أي التزامات تسويقية عابرة."""
    }
}

# ==========================================
# LEAD-14: You inherit a legacy app with low test coverage and frequent bugs. What is your first 90-day plan?
# ==========================================
DATA["LEAD-14"] = {
    "concept_en": """Rescuing and stabilizing a legacy codebase plagued by low test coverage and frequent crashes requires a phased, telemetry-driven 90-day execution framework:
- The Anti-Pattern of the Egotistical Rewrite:
  - Inexperienced leads immediately declare: \"This code is terrible; we must freeze features and rewrite from scratch!\"
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
     - Publish a quantified scorecard demonstrating improved crash-free rate and developer velocity to leadership.""",
    "walkthrough_en": """Characterization Test pattern locking in legacy behavior before refactoring in Kotlin:
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
```""",
    "short_en": """Execute a structured 90-day stabilization plan avoiding premature rewrites. Spend days 1–30 measuring baselines and building CI pipelines, days 31–60 writing characterization tests around critical paths and fixing top crashes, and days 61–90 incrementally refactoring high-churn modules behind feature flags while proving measurable ROI in crash-free sessions.""",
    "structured_en": """Inheriting a fragile, untested legacy application requires a disciplined, telemetry-driven ninety-day turnaround strategy rather than an emotional rewrite.
During Days 1 to 30, the focus is observation and measurement. We establish empirical baselines using Crashlytics and Google Play Vitals, identify top crash clusters, and construct an automated CI/CD pipeline to ensure build repeatability without altering production code.
During Days 31 to 60, we build safety nets. We fix the top five crashes responsible for the majority of user friction. Before refactoring, we author characterization tests around critical revenue paths like checkout, capturing existing behavior as a regression barrier. We introduce remote feature flags and enforce the Boy Scout Rule.
During Days 61 to 90, we execute incremental refactoring on the highest-churn module, migrating it to modern Clean Architecture.
We publish a clear scorecard demonstrating improved crash-free rates and reduced build times, proving sustainable technical ROI.""",
    "deep_senior_en": """From an engineering leadership, technical debt remediation, and organizational transformation perspective, inheriting a troubled legacy codebase is a critical leadership crucible that tests strategic patience and tactical execution.
The most catastrophic mistake an incoming technical leader can make is succumbing to the rewrite delusion: declaring the inherited codebase unsalvageable and halting feature development for six months. This halts business momentum, discards edge-case wisdom embedded in the legacy code, and almost always results in a new system that reproduces old bugs.
Senior leaders execute a phased 30-60-90 day stabilization roadmap.
Phase 1 (Days 1 to 30) is dedicated to instrumentation and discovery. We establish continuous integration pipelines with automated build checks and integrate robust telemetry to record our baseline crash-free rate, cold launch latency, and ANR metrics. We interview engineers and product managers to map high-churn pain points.
Phase 2 (Days 31 to 60) focuses on stabilization and safety nets. Applying the Pareto Principle, we remediate the top five crashes causing eighty percent of user impact. Crucially, we wrap high-risk legacy modules in Characterization Tests—black-box regression tests that capture existing inputs and outputs without worrying about internal code aesthetics. We establish feature flagging infrastructure to decouple deployment from release.
Phase 3 (Days 61 to 90) delivers incremental modernization. We select a single, high-churn vertical slice—such as the user profile or payment module—and refactor it into clean, modular Kotlin components, demonstrating the new architectural blueprint to the team.
We institutionalize standards via Architecture Decision Records and custom Detekt rules.
At the ninety-day mark, we present an executive scorecard showing that crash-free sessions increased from ninety-eight percent to ninety-nine point nine percent and developer PR cycle time dropped by a third, earning long-term trust across the organization.""",
    "meta_ar": {
        "id": "LEAD-14",
        "questionAr": "استلمت مسؤولية قيادة تطبيق قديم يعاني من ضعف تغطية الاختبارات وتكرار الأخطاء والكراشات. ما هي خطتك للأيام التسعين الأولى (First 90-Day Plan)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "إدارة المشروعات التقنية المتعثرة، تجنب فخ إعادة الكتابة من الصفر (Rewrite Fallacy)، خطة الـ 90 يوماً المرحلية (الرصد والقياس، بناء شبكات الأمان، وإعادة الهيكلة التدريجية)، واختبارات التوصيف (Characterization Tests).",
        "concept_ar": "تتطلب استعادة استقرار وتطوير تطبيق قديم (Legacy App) يعاني من ضعف الاختبارات وتكرار الكراشات اتباع خطة تشغيلية محكمة للأيام التسعين الأولى مبنية على القياس الرقمي والتحسين التدريجي، مع تجنب فخ المطالبة بإعادة كتابة الكود من الصفر (The Rewrite Fallacy) الذي يعطل العمل لأشهر ويخسر حكمة معالجة الحالات الاستثنائية المتراكمة عبر السنين. وتنقسم الخطة إلى 3 مراحل: أولاً، الأيام من 1 إلى 30 للرصد والقياس وبناء خط الأساس (Baseline) عبر دمج أدوات المراقبة Crashlytics وPlay Vitals، وبناء خط بناء مؤتمت (CI Pipeline)، ورسم خريطة المشكلات دون تعديل الكود؛ ثانياً، الأيام من 31 إلى 60 لاحتواء النزيف وحل أكثر 5 كراشات مسببة لـ 80% من الأعطال (مبدأ باريتو)، وكتابة اختبارات توصيفية (Characterization Tests) لتجميد السلوك الحالي لمسار الدفع والشراء كشبكة أمان، وتفعيل مفاتيح الميزات؛ ثالثاً، الأيام من 61 إلى 90 للبدء في إعادة الهيكلة التدريجية لموديول واحد حيوي وعالي التعديل، وتوثيق المعايير بـ ADRs، وإبراز نتائج تحسن الاستقرار وإنتاجية الفريق للإدارة بالأرقام.",
        "walkthrough_ar": """نمط اختبار التوصيف (Characterization Test) لتجميد سلوك الكود القديم قبل إعادة هيكلته بكوتلن:
```kotlin
// اختبار التوصيف: يحفظ ويثبت سلوك الكود القديم بحالاته الحافة كشبكة أمان ضد التراجع
class LegacyCheckoutCharacterizationTest {

    private val legacyService = LegacyCheckoutEngine()

    @Test
    fun `capture and assert baseline legacy checkout behavior across edge cases`() {
        // فحص وتثبيت النتيجة الحالية للكود القديم مع المدخلات العادية
        val standardResult = legacyService.calculateDiscount(
            cartTotal = 100.0,
            couponCode = "SAVE10",
            isVip = false
        )
        assertEquals(10.0, standardResult.discountAmount, 0.001)

        // تثبيت سلوك خاص في الكود القديم: الكوبون الفارغ يرجع خصم VIP دون إلقاء خطأ
        val nullCouponResult = legacyService.calculateDiscount(
            cartTotal = 100.0,
            couponCode = null,
            isVip = true
        )
        assertEquals(5.0, nullCouponResult.discountAmount, 0.001)
    }
}

// تقرير إنجاز خطة الـ 90 يوماً المقدم للإدارة:
// - أول 30 يوماً: تفعيل المراقبة وبناء الـ CI، واكتشاف معدل استقرار 98.2%.
// - الأيام 31-60: حل أكبر 5 كراشات، وبناء شبكة اختبارات لمسار الشراء.
// - الأيام 61-90: رفع الجلسات السليمة لـ 99.85%، وتقليص وقت مراجعة الـ PR بنسبة 35%.
```""",
        "why_it_matters_ar": "التصرف العشوائي في الأنظمة القديمة يتسبب في كسر ميزات تجارية حيوية، بينما المطالبة بإعادة البناء من الصفر تؤدي لفشل المشاريع وتسريح الفرق.",
        "worked_example_ar": "استلمت تطبيقاً كراشاته 3%؛ رفضت إعادة الكتابة، وطبقت خطة الـ 90 يوماً بحل أخطر 5 كراشات وتطويق مسار الدفع باختبارات توصيفية؛ فوصل الاستقرار لـ 99.9% في شهرين.",
        "trade_offs_ar": "التحسين التدريجي يتطلب الصبر والتعايش المؤقت مع كود قديم غير مثالي؛ لكنه يضمن استمرار إيرادات الشركة وتفادي مخاطر الانهيار التام.",
        "failure_modes_ar": "أخطر الأخطاء هو تجميد تسليم الميزات وإعلان إعادة كتابة التطبيق بالكامل (Full Rewrite)، أو البدء في تعديل الكود قبل بناء اختبارات وشبكة أمان تحميه.",
        "production_perspective_ar": "في الشركات التقنية الناضجة، تُستخدم اختبارات التوصيف كقفل أمان يمنع أي تراجع أثناء تحديث معمارية الشاشات القديمة تدريجياً.",
        "how_to_answer_ar": "ابدأ برفض فخ إعادة الكتابة من الصفر، وقسم خطة الـ 90 يوماً إلى 3 مراحل واضحة (الرصد، بناء شبكات الأمان وحل الكراشات الكبرى، ثم إعادة الهيكلة التدريجية)، واختم بالمقاييس الرقمية.",
        "talking_points_ar": "فخ إعادة الكتابة Rewrite Fallacy، خطة الـ 90 يوماً، خط الأساس Baseline، مبدأ باريتو لأكبر 5 كراشات، اختبارات التوصيف Characterization Tests، وإعادة الهيكلة التدريجية.",
        "follow_ups_ar": "كيف تتعامل مع مقاومة المطورين القدامى الذين يرفضون كتابة الاختبارات ويفضلون الاستمرار في أسلوبهم التقليدي؟",
        "self_check_ar": "هل أكدت على رفض فكرة الـ Rewrite، وقسمت الخطة لثلاثين يوماً لكل مرحلة، وذكرت اختبارات التوصيف وحل أكبر الكراشات أولاً؟",
        "references_ar": f"- [Michael Feathers: Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) — المرجع الهندسي الخالد للتعامل مع البرمجيات القديمة وتطبيق اختبارات التوصيف.\n- [Martin Fowler: Strangler Fig Application Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html) — النمط المعماري المعتمد للاستبدال التدريجي للأنظمة القديمة دون تعطيل الإنتاج.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """أدير التطبيق القديم بخطة مرحلية للأيام التسعين الأولى متجنباً فخ إعادة الكتابة من الصفر. أقضي الأيام من 1 إلى 30 في الرصد وبناء خط الأساس للبيانات وخطوط الـ CI، ومن 31 إلى 60 في احتواء النزيف بحل أكبر 5 كراشات وتطويق المسارات الحيوية باختبارات توصيفية، ومن 61 إلى 90 في إعادة الهيكلة التدريجية لموديول حيوي وإثبات نجاح الخطة برفع معدل الاستقرار بالأرقام.""",
        "best_answer_ar": """تتطلب قيادة تطبيق قديم يعاني من ضعف الاختبارات وتكرار الأعطال منهجية تشغيلية هادئة تستند إلى البيانات وتتجنب فخ المطالبة بإعادة كتابة الكود من الصفر.
يدرك القائد التقني أن الكود القديم يختزن سنوات من معالجة الحالات الحافة، وإيقاف التطوير لإعادة بنائه يجمد إيرادات الشركة.
لذلك ننفذ خطة محكمة من ثلاث مراحل:
المرحلة الأولى، في الأيام من 1 إلى 30، تركز على الرصد وبناء خط الأساس؛ حيث نفعل أدوات التتبع مثل Crashlytics وPlay Vitals، ونبني خط بناء آلي CI يضمن تكرارية الفحص، دون لمس الكود.
المرحلة الثانية، في الأيام من 31 إلى 60، تهدف لاحتواء النزيف؛ فنطبق مبدأ باريتو لحل أكبر 5 كراشات مسؤولة عن أغلب الأعطال، ونبني شبكة أمان عبر اختبارات التوصيف Characterization Tests حول مسارات الشراء الحيوية لتجميد سلوكها قبل التعديل، مع تفعيل مفاتيح الميزات.
المرحلة الثالثة، في الأيام من 61 إلى 90، تبدأ فيها إعادة الهيكلة التدريجية لأكثر الموديولات تعديلاً بنمط Clean Architecture، ونختم بتقديم تقرير رقمي يثبت ارتفاع نسبة خلو الجلسات من الأعطال واختصار زمن مراجعة التعديلات.""",
        "deep_answer_ar": """من منظور القيادة الهندسية وتطوير المؤسسات واستراتيجيات التعامل مع البرمجيات القديمة Legacy Code، يمثل استلام مشروع متعثر الاختبار الأبرز للحكمة الإدارية والنضج المعماري للقائد.
إن الاندفاع لإعلان موت الكود والمطالبة بتجميد الميزات لستة أشهر لإعادة بناء التطبيق من الصفر خطأ قيادي كارثي غالباً ما يورط الشركات في خسائر مالية فادحة ويسفر عن نظام جديد يكرر أخطاء الماضي.
والقائد الخبير يستند إلى تعاليم مايكل فيذرز ويقود خطة تحول منضبطة للأيام التسعين الأولى:
المرحلة الأولى في الشهر الأول تنطلق تحت شعار الاستماع والرصد والقياس. نربط التطبيق بأدوات التحليل الرقمي في متجر جوجل لرصد خط الأساس لمعدلات الكراش وتجمد الشاشات وزمن الفتح البارد، ونؤسس خط بناء مستمر CI يفرض الانضباط البرمجي دون تعديل كود الإنتاج.
المرحلة الثانية في الشهر الثاني تكرس لبناء شبكات الأمان واحتواء الانهيارات؛ فنعالج أخطر خمسة أسباب للكراشات التي تسبب ثمانين بالمئة من شكاوى العملاء. ونحيط الشاشات الحساسة باختبارات التوصيف Characterization Tests لتثبيت سلوكها الحالي بحالاته الحافة كقفل أمان يمنع الانحدار أثناء التطوير.
المرحلة الثالثة في الشهر الثالث تطلق شرارة التحديث التدريجي المعماري باستخدام نمط خنق النظام القديم Strangler Fig؛ فنختار موديولاً واحداً عالي التعديل كمسار الدفع ونعزله بمعمارية نظيفة تدعم اختبارات الوحدة.
ونوثق هذا النموذج في سجلات القرارات المعمارية ADRs ليكون دليلاً للفريق.
وعند انقضاء الأيام التسعين، نقدم للإدارة التنفيذية تقريراً موثقاً بالأرقام يبرهن على ارتفاع نسبة الجلسات السليمة من ثمانية وتسعين بالمئة إلى تسعة وتسعين فاصل تسعة بالمئة وتقليص وقت دمج التعديلات بالثلث، مما يرسخ الثقة في القيادة الهندسية الجديدة."""
    }
}

# ==========================================
# LEAD-15: How would you push back on a requirement that conflicts with mobile OS/security constraints?
# ==========================================
DATA["LEAD-15"] = {
    "concept_en": """Professionally pushing back against product requirements that violate Android OS constraints or platform security policies requires collaborative empathy, technical education, business risk translation, and viable alternatives:
- The Senior Pushback Philosophy:
  - Ineffective pushback sounds defensive or lazy: \"Android doesn\'t allow this\" or \"Google says no.\"
  - Senior pushback reframes the technical friction around business risk and uncovers the underlying user goal: \"What is the core user problem we are solving, and how can we achieve it within Google Play policies to protect our brand?\"
- The 4-Step Technical Pushback Framework:
  1. Uncover the Core Business Intent (The \"Why\"):
     - Dig past the requested implementation to the underlying objective.
     - Example Request: \"We must track user location continuously in the background 24/7 without showing any notification.\"
     - True Business Intent: \"We want to trigger store discount coupons when the user walks near our physical retail branches.\"
  2. Translate Platform Constraints into Business Risk:
     - Doze Mode and App Standby: Android battery optimization aggressively kills background processes.
     - Google Play Policy Enforcement: Continuous background location without an active Foreground Service or Background Location justification results in permanent app suspension or store delisting.
     - Customer Trust and Churn: Background battery drain prompts Android OS \"High battery usage\" system warnings, driving immediate uninstalls and 1-star reviews.
  3. Offer Platform-Idiomatic, Compliant Alternatives:
     - Propose Google Play Services Geofencing API: hardware-assisted, zero battery impact, wakes the app only at geofence entry, fully compliant with Play policies.
  4. Document Collaborative Alignment:
     - Formalize the agreed alternative in the Product Requirements Document (PRD) and issue tracker.""",
    "walkthrough_en": """Collaborative requirement pushback negotiation script and platform-idiomatic alternative in Kotlin:
```kotlin
// INSTEAD OF: Battery-draining, non-compliant continuous background location polling loop
// WE DELIVER: Platform-idiomatic, battery-efficient, fully compliant Geofencing API
class RetailGeofenceManager(
    private val context: Context,
    private val geofencingClient: GeofencingClient
) {
    fun registerStoreGeofence(storeId: String, lat: Double, lng: Double, radiusMeters: Float) {
        val geofence = Geofence.Builder()
            .setRequestId(storeId)
            .setCircularRegion(lat, lng, radiusMeters)
            .setExpirationDuration(Geofence.NEVER_EXPIRE)
            .setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER)
            .build()

        val request = GeofencingRequest.Builder()
            .setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_ENTER)
            .addGeofence(geofence)
            .build()

        // Compliant with Android Doze mode and Google Play Battery Policies
        geofencingClient.addGeofences(request, getGeofencePendingIntent())
    }

    private fun getGeofencePendingIntent(): PendingIntent {
        val intent = Intent(context, GeofenceBroadcastReceiver::class.java)
        return PendingIntent.getBroadcast(context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
    }
}

// Senior Pushback Conversation Template:
// "I understand our goal is to drive foot traffic to retail stores with timely discounts.
// However, polling GPS 24/7 in the background violates Google Play policy and triggers
// battery drain warnings on Android 14, which will cause store delisting and user churn.
// Instead, if we use the native Android Geofencing API, we achieve the exact same retail trigger
// with zero battery drain, zero app store risk, and no persistent notification required."
```""",
    "short_en": """Push back professionally by uncovering the underlying business goal rather than simply refusing. Translate platform constraints into business risks like app store removal and battery drain uninstalls, and propose compliant, battery-efficient alternatives like Geofencing APIs or WorkManager that fulfill the business intent within Android OS policies.""",
    "structured_en": """Pushing back effectively on requirements that conflict with mobile platform constraints requires collaborative alignment and business risk framing.
Simply telling stakeholders that the platform does not allow a feature sounds defensive and unhelpful.
A senior engineer begins by identifying the underlying business objective behind the request. For example, if a product manager asks for continuous, invisible background location tracking, the true goal is usually triggering location-based promotions.
We then articulate the platform constraints in terms of business consequences: violating Android background execution policies risks immediate removal from the Google Play Store, while aggressive polling drains battery life, triggering OS battery-hog warnings and driving uninstalls.
Finally, we present a compliant, platform-idiomatic alternative that satisfies the business need, such as using Google Play Services Geofencing.
This reframes engineering as a strategic partner dedicated to delivering product goals safely.""",
    "deep_senior_en": """From an engineering leadership, platform diplomacy, and technical product strategy perspective, pushing back against impossible or non-compliant requirements is an essential skill that protects the company\'s primary mobile channel.
Product managers and commercial executives often operate from web or desktop mental models, assuming background processes can run indefinitely without cost. When an engineer blunts this expectation with a terse \"Android doesn\'t support this,\" it breeds frustration and fosters an adversarial relationship between engineering and business teams.
The senior approach replaces resistance with collaborative re-architecture.
The first step is discovering the root intent. Ask \"What core customer experience or commercial outcome are we driving with this requirement?\" When the business asks to keep an un-killable background socket open forever, they usually just want instantaneous notification delivery.
The second step is translating operating system technicalities into business risk language. Avoid lecturing stakeholders about Doze mode, Scoped Storage, or JobScheduler quotas. Instead, explain the tangible commercial risks: \"If we implement continuous background tracking without an active notification, Google Play automated review will suspend our app within forty-eight hours, halting all new user acquisition. Furthermore, Android 14 will flag our app with a high-battery-drain notification, causing a spike in uninstalls and dragging our rating down.\"
The decisive third step is delivering a compliant, superior alternative. Propose the idiomatic Android solution: \"Instead of a heavy background service, we can implement the Geofencing API combined with Firebase Cloud Messaging data payloads. This triggers our store discount message with sub-second accuracy, consumes negligible battery, and adheres perfectly to Google Play store guidelines.\"
This transforms a contentious conflict into a high-trust partnership that delivers business outcomes while respecting platform excellence.""",
    "meta_ar": {
        "id": "LEAD-15",
        "questionAr": "كيف تعترض وتقاوم متطلباً تجارياً يتعارض مع قيود نظام أندرويد الأمنية والتشغيلية (OS & Security Constraints)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "الاعتراض الهندسي الاحترافي (Constructive Pushback)، فهم الهدف التجاري الحقيقي وراء الطلب، ترجمة القيود التقنية إلى مخاطر تجارية (حذف التطبيق والتقييمات السلبية)، وتقديم بدائل قياسية متوافقة.",
        "concept_ar": "يتطلب الاعتراض ومقاومة المتطلبات التجارية التي تتعارض مع قيود نظام أندرويد الأمنية والتشغيلية أسلوباً قيادياً بنّاءً يبتعد عن الرفض الجاف ويترجم القيود البرمجية إلى مخاطر تجارية مع تقديم بدائل ذكية تحقق نفس الهدف: فالرد غير المهني هو القول بأن 'أندرويد يمنع هذا'، وهو ما يظهر المطور بمظهر الكسول أو المعرقل للأعمال. وتعتمد منهجية الاعتراض الاحترافية على 4 خطوات: أولاً، استكشاف الهدف التجاري الحقيقي وراء المتطلب؛ فإذا طُلب تتبع موقع المستخدم على مدار 24 ساعة في الخلفية دون تنبيه، فالهدف الفعلي هو إرسال كوبونات خصم عند اقترابه من الفروع التجارية؛ ثانياً، ترجمة قيود النظام إلى مخاطر تجارية ملموسة يفهمها مديرو الأعمال؛ مثل إيضاح أن اختراق قيود الخلفية يخالف سياسات Google Play ويعرض التطبيق للحذف الفوري من المتجر، كما أن استنزاف البطارية يدفع نظام أندرويد لإظهار تحذير 'هذا التطبيق يستهلك البطارية' مما يسبب موجة إلغاء تثبيت وتقييمات سلبية؛ ثالثاً، طرح البديل القياسي المعتمد من أندرويد الذي يحقق نفس القيمة التجارية بكفاءة؛ مثل استخدام واجهات السياج الجغرافي (Geofencing API) التي تستيقظ بلحظة واحدة عند دخول محيط المتجر دون أي استنزاف للطاقة وبأمان تام؛ رابعاً، توثيق هذا التوافق المشترك في متطلبات المشروع.",
        "walkthrough_ar": """كود البديل المتوافق مع قيود النظام وسياسته عبر Geofencing API في كوتلن:
```kotlin
// البديل القياسي المتوافق: استخدام السياج الجغرافي بدلاً من تتبع الـ GPS المستمر
class RetailGeofenceManager(
    private val context: Context,
    private val geofencingClient: GeofencingClient
) {
    fun registerStoreGeofence(storeId: String, lat: Double, lng: Double, radiusMeters: Float) {
        val geofence = Geofence.Builder()
            .setRequestId(storeId)
            .setCircularRegion(lat, lng, radiusMeters)
            .setExpirationDuration(Geofence.NEVER_EXPIRE)
            .setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER)
            .build()

        val request = GeofencingRequest.Builder()
            .setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_ENTER)
            .addGeofence(geofence)
            .build()

        // متوافق تماماً مع سياسات متجر جوجل وإدارة البطارية في أندرويد Doze Mode
        geofencingClient.addGeofences(request, getGeofencePendingIntent())
    }

    private fun getGeofencePendingIntent(): PendingIntent {
        val intent = Intent(context, GeofenceBroadcastReceiver::class.java)
        return PendingIntent.getBroadcast(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }
}

// أسلوب الحوار الاحترافي مع مدير المنتج:
// "أتفهم تماماً رغبتنا في جذب العملاء للفروع عبر إرسال عروض ترويجية فورية عند الاقتراب.
// لكن تتبع الـ GPS في الخلفية طوال اليوم يخالف سياسات Google Play الصارمة وسيعرضنا للحذف من المتجر،
// كما يدفع أندرويد لتحذير المستخدم من استهلاك البطارية مما يتسبب في مسح التطبيق.
// البديل الهندسي الأفضل هو استخدام Geofencing API؛ حيث يحقق نفس الهدف التجاري بدقة تامة
// دون أي استنزاف للبطارية، ومطابق تماماً لسياسات المتجر دون الحاجة لتنبيه مزعج."
```""",
        "why_it_matters_ar": "الرفض الصدامي يخلق عداوة بين الهندسة وإدارة المنتج، بينما الانصياع الأعمى للمتطلبات المخالفة يؤدي لحذف التطبيق من المتجر وضياع استثمارات الشركة.",
        "worked_example_ar": "طلب التسويق تشغيل الخدمة في الخلفية دائماً لتحديث العروض؛ اعترضنا بشرح خطر حذف التطبيق من المتجر، واقترحنا استخدام FCM Data Messages التي توقظ التطبيق عند وجود عرض جديد فقط ووفرنا 90% من استهلاك البطارية.",
        "trade_offs_ar": "البدائل المتوافقة قد تتطلب جهداً إضافياً في الدمج والربط مع خدمات النظام؛ لكنها تحمي الشركة من الطرد من المتاجر وتضمن تقييمات إيجابية للمستخدمين.",
        "failure_modes_ar": "أخطر الأخطاء هو الرد بعبارة جافة مثل 'أندرويد لا يسمح بذلك' دون شرح الأسباب، أو محاولة الالتفاف على قيود النظام بحيل ملتوية يتم كشفها وحظرها لاحقاً.",
        "production_perspective_ar": "في كبرى الشركات، تتبنى الفرق الهندسية دور الشريك الاستراتيجي للأعمال؛ فنوضح المخاطر بلغة الأرقام ونقدم الحلول القياسية البديلة التي تخدم نفس الهدف.",
        "how_to_answer_ar": "ابدأ برفض الرد الصدامي، واشرح البحث عن الهدف التجاري الحقيقي وراء الطلب، ثم بين كيفية ترجمة القيود لمخاطر تجارية (حذف من المتجر واستنزاف بطارية)، واطرح البديل المتوافق بأدوات أندرويد.",
        "talking_points_ar": "الاعتراض البناء Constructive Pushback، فهم الهدف التجاري الحقيقي، سياسات متجر Google Play، أنماط توفير الطاقة Doze Mode، بدائل النظام القياسية Geofencing وWorkManager، والشراكة الاستراتيجية.",
        "follow_ups_ar": "ماذا تفعل إذا أصر مدير المنتج على تتبع الموقع بالطريقة المخالفة بحجة أن أحد التطبيقات المنافسة يفعل ذلك في السوق؟",
        "self_check_ar": "هل تجنبت الرد الجاف، وركزت على استكشاف الهدف التجاري الحقيقي، وترجمت القيود لمخاطر حذف من المتجر وبطارية، وطرحت بديلاً تقنياً مطابقاً؟",
        "references_ar": f"- [Google Play Policy: Background Location and Policy Requirements](https://support.google.com/googleplay/android-developer/answer/9799150) — السياسات الرسمية لمتجر جوجل بشأن أذونات الموقع واستخدام الخدمات في الخلفية.\n- [Android Developers: Optimize for Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) — الدليل المعماري الرسمي لإدارة استهلاك الطاقة والتوافق مع قيود نظام أندرويد.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نعترض باحترافية بالبحث عن الهدف التجاري الحقيقي وراء المتطلب بدلاً من الرفض الجاف بعبارة 'أندرويد يمنع هذا'. نترجم قيود النظام إلى مخاطر تجارية ملموسة مثل تعريض التطبيق للحذف من متجر Google Play واستنزاف البطارية الذي يدفع المستخدمين لحذفه، ثم نطرح بديلاً قياسياً معتمداً من أندرويد مثل Geofencing يحقق نفس الهدف التجاري بأمان تام.""",
        "best_answer_ar": """يتطلب الاعتراض الهندسي على المتطلبات المتعارضة مع قيود نظام أندرويد شراكة استراتيجية بناءة تبتعد عن الصدام وتترجم العقبات التقنية إلى لغة الأعمال.
يبدأ الموقف الاحترافي برفض العبارات المحبطة مثل 'النظام لا يسمح' لأنها تظهر المهندس بمظهر المعرقل للأعمال، والتركيز بدلاً من ذلك على استكشاف الغاية التجارية الحقيقية وراء الطلب؛ فعندما يطلب الفريق تتبعاً مستمراً للموقع في الخلفية دون إشعار، فالهدف الفعلي غالباً هو تفعيل عروض ترويجية عند اقتراب العميل من الفروع.
ثم نترجم قيود النظام إلى مخاطر تجارية وقانونية تفهمها الإدارة التنفيذية؛ فنوضح أن التحايل على قيود الخلفية ينتهك سياسات Google Play ويعرض التطبيق للحظر الفوري، كما يطلق تحذيرات النظام من استنزاف البطارية مما يرفع معدلات إلغاء التثبيت وتراجع التقييمات.
ونختتم دائماً بتقديم البديل البرمجي المتوافق مع فلسفة أندرويد، مثل اعتماد Geofencing API الذي يوقظ التطبيق بلحظة الدخول لمحيط الفرع دون أي استنزاف للبطارية وبامتثال تام لسياسات المتجر، مما يحقق أهداف الأعمال بأمان.""",
        "deep_answer_ar": """من منظور القيادة الهندسية والدبلوماسية التقنية والشراكة الاستراتيجية مع قطاع الأعمال، يمثل الاعتراض الحصيف على المتطلبات غير المتوافقة خط الدفاع الأول لحماية استثمارات الشركة وسمعتها الرقمية.
غالباً ما ينطلق مدراء المنتجات من تجارب منصات الويب متوهمين إمكانية إبقاء الاتصالات والخدمات تعمل بلا نهاية في خلفية الهاتف المحمول. والرد الصدامي غير الناضج يولد فجوة ثقة ويفسر على أنه عجز تقني أو تكاسل من الفريق الهندسي.
والمهندس القيادي يعيد صياغة المشهد بمهارة عبر حوار استكشافي يبحث عن جوهر القيمة المطلوبة للعميل؛ كأن يسأل: 'ما هو الأثر التجاري أو السلوك المطلوب تحقيقه مع المستخدم من وراء هذا الاتصال المستمر؟'.
وعندما تتضح الصورة، نترجم المحاذير التقنية إلى مخاطر استثمارية مباشرة؛ فبدلاً من الاستغراق في شرح خوارزميات Doze Mode أو قيود Scoped Storage، نتحدث بلغة النتائج: 'تطبيق هذا المتطلب بشكل مخالف يعرضنا للإيقاف الإجباري من متجر Google Play خلال ثمان وأربعين ساعة مما يوقف اكتساب العملاء الجدد تماماً، كما سيعطي هواتف المستخدمين تنبيهاً صريحاً باستهلاك التطبيق للبطارية مما يقود لعاصفة تقييمات سلبية في المتجر'.
ثم نتحول فوراً لطرح البديل الهندسي الأرقى؛ كأن نقترح استخدام واجهات السياج الجغرافي Geofencing المدعومة بحزم التنبيهات الصامتة FCM، موضحين أنها تحقق الاستهداف الجغرافي بدقة متناهية دون إهدار طاقة الهاتف وبامتثال رسمي كامل، محولين الاعتراض إلى شراكة استراتيجية تصنع حلولاً تجارية متينة ومستدامة."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for LEAD-09 to LEAD-15...")
    for qid, d in sorted(DATA.items()):
        # Short answer (35 - 110)
        c_short = len(d["short_en"].split())
        assert 35 <= c_short <= 110, f"{qid}: short_en word count {c_short} out of range (35-110)"

        # Structured answer (100 - 280)
        c_struct = len(d["structured_en"].split())
        assert 100 <= c_struct <= 280, f"{qid}: structured_en word count {c_struct} out of range (100-280)"

        # Deep senior answer (200 - 650)
        c_deep = len(d["deep_senior_en"].split())
        assert 200 <= c_deep <= 650, f"{qid}: deep_senior_en word count {c_deep} out of range (200-650)"

        meta = d["meta_ar"]
        # Quick answer AR (35 - 110)
        c_qar = len(meta["quick_answer_ar"].split())
        assert 35 <= c_qar <= 110, f"{qid}: quick_answer_ar word count {c_qar} out of range (35-110)"

        # Best answer AR (90 - 280)
        c_bar = len(meta["best_answer_ar"].split())
        assert 90 <= c_bar <= 280, f"{qid}: best_answer_ar word count {c_bar} out of range (90-280)"

        # Deep answer AR (180 - 650)
        c_dar = len(meta["deep_answer_ar"].split())
        assert 180 <= c_dar <= 650, f"{qid}: deep_answer_ar word count {c_dar} out of range (180-650)"

        # Check spoken style (no bullets, no numbered lists)
        for field_name, text in [
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not any(line.strip().startswith(("-", "*", "•")) for line in text.splitlines()), f"{qid}: {field_name} contains bullets"
            assert not any(line.strip() and line.strip()[0].isdigit() and line.strip()[1:3] in (". ", ") ") for line in text.splitlines()), f"{qid}: {field_name} contains numbered list"

        assert "على الجانب الآخر، فيما يخص" not in meta["best_answer_ar"], f"{qid}: best_answer_ar contains cliché"
        assert "على الجانب الآخر، فيما يخص" not in meta["deep_answer_ar"], f"{qid}: deep_answer_ar contains cliché"

    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("lead_09_15", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} LEAD questions (LEAD-09 to LEAD-15) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
