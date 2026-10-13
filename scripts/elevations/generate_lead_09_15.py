#!/usr/bin/env python3
"""Generator for LEAD-09 through LEAD-15 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "lead.json"

LEAD_09_15 = [
    {
        "id": "LEAD-09",
        "arabic_explanation": (
            "كيف تدير جلسة تحليل أسباب الحوادث الإنتاجية (Incident Postmortem) بدون لوم شخصي (Blameless Postmortem)؟\n\n"
            "1. فلسفة ثقافة عدم اللوم (Blameless Culture):\n"
            "   - مبدأ هندسة الموثوقية (Google SRE): **الأخطاء البشرية هي نتيجة حتمية للنظام غير المحصن، وليست السبب الجذري (Human error is a symptom, not the root cause)**.\n   - إذا ارتكب مهندس خطأً ورفع كوداً كسر الإنتاج، فإن النظام الهندسي هو الذي فشل: أين كانت اختبارات الـ CI؟ أين كانت فحوصات الـ Lint؟ أين كان الـ Staged Rollout؟\n   - توجيه اللوم للأفراد يجعل المهندسين يخفون أخطاءهم ويتجنبون المبادرة خوفاً من العقاب.\n\n"
            "2. الهيكل القياسي لوثيقة الـ Postmortem:\n   - **1. الملخص والأثر التجاري (Summary & Impact)**: مدة العطل، عدد المستخدمين المتأثرين، ونسبة العمليات الفاشلة.\n   - **2. الخط الزمني الدقيق (Timeline)**: تسلسل الأحداث بالدقائق (وقت نشر الكود -> وقت انطلاق أول تنبيه -> وقت الاستجابة -> وقت إيقاف الطرح -> وقت حل المشكلة بالكامل).\n   - **3. تحليل السبب الجذري (Root Cause Analysis - 5 Whys)**: السؤال المتكرر بـ \"لماذا؟\" للوصول إلى الخلل في الإجراءات أو الأدوات بدلاً من التوقف عند الخطأ السطحي.\n   - **4. ما الذي سار بشكل جيد وما الذي فشل**: تقييم سرعة اكتشاف الحادث وتنسيق الفريق.\n   - **5. بنود العمل الوقائية (Action Items / Preventative Measures)**: مهام محددة بمسؤولين وتواريخ إنجاز لمنع تكرار نفس الحادث نهائياً."
        ),
        "practical_walkthrough": (
            "نموذج تطبيق أسلوب الـ 5 Whys في تحليل حادث إنتاجي حقيقي على أندرويد:\n"
            "```markdown\n"
            "### تحليل السبب الجذري لحادث انهيار شاشة الدفع (Incident #108):\n"
            "\n"
            "1. لماذا انهار التطبيق لـ 15,000 مستخدم فور التحديث؟\n"
            "   -> حدث NullPointerException عند قراءة حقل `user_tier` من استجابة السيرفر.\n"
            "2. لماذا حدث NPE في كود Kotlin المفترض أنه Null-Safe؟\n"
            "   -> لأن كلاس البيانات استخدم `@SerializedName` بدون قيمة افتراضية، والـ Backend أرجع الحقل كـ null.\n"
            "3. لماذا لم ترصد اختبارات الوحدة هذه الحالة؟\n"
            "   -> لأن الـ Unit Tests استخدمت Fake Data يحتوي دائماً على قيم صالحة ولم تختبر الحقول الناقصة.\n"
            "4. لماذا لم ترصد بيئة الـ Staging المشكلة قبل الإطلاق؟\n"
            "   -> لأن قاعدة بيانات Staging احتوت على بيانات قديمة كاملة فقط ولم تحاكي المستخدمين الجدد.\n"
            "5. لماذا سمحت عملية الإطلاق بانتشار الخطأ لـ 15,000 مستخدم فوراً؟\n"
            "   -> لأن الإطلاق تم دفعة واحدة بنسبة 100% بدلاً من اتباع سياسة الـ Staged Rollout (1% -> 5%).\n"
            "\n"
            "✅ بنود العمل الوقائية المعتمدة (Action Items):\n"
            "- [P0] إضافة قاعدة Detekt تفحص أن كل كلاسات الـ DTO تمتلك قيم افتراضية لجميع الحقول (Owner: Ahmed - 3 days).\n"
            "- [P0] حظر الإطلاق بنسبة 100% وإجبار مسار الـ Staged Rollout عبر CI (Owner: Mohamed - 2 days).\n"
            "```"
        ),
        "quick_answer": "Run a blameless postmortem by focusing on systemic vulnerabilities, process gaps, and missing safeguards rather than individual human error. Construct an objective incident timeline, utilize the 5 Whys technique to uncover root systemic causes, document what went well and what failed, and track SMART preventative action items with assigned owners.",
        "best_answer": (
            "A blameless postmortem transforms production failures into architectural resilience without damaging team morale:\n\n"
            "1. **Core Philosophy of Blamelessness**:\n"
            "   - Assume good intent: every engineer made the best decision based on the information available at the time. A single developer's mistake reaching production is an indictment of the testing suite, staging fidelity, and deployment guardrails, not the individual.\n\n"
            "2. **Structured Postmortem Document**:\n"
            "   - **Executive Summary & Impact**: Downtime duration, crash-rate breach, and business loss (e.g. 8,000 unplaced orders).\n   - **Deterministic Chronological Timeline**: Objective UTC log from initial commit merge, alerting trigger, Slack triage kickoff, hotfix deployment, to resolution.\n   - **Root Cause Analysis (5 Whys)**: Drill down through systemic layers until reaching the tooling or verification gap that allowed the defect to bypass QA.\n   - **Lessons Learned**: Transparently evaluate alerting latency, monitoring blind spots, and runbook efficacy.\n\n"
            "3. **Actionable Remediation Backlog**:\n"
            "   - Define prioritized, assignable action items (P0/P1) with explicit completion dates focused on preventative automation: new static analysis lint rules, automated regression tests, and staged release gates."
        ),
        "deep_answer": (
            "From an engineering leadership and organizational psychological safety perspective, running postmortems requires emotional intelligence:\n\n"
            "1. **Facilitation Tone and Psychological Safety**: The meeting facilitator must immediately redirect any accusatory language ('Why did you merge that on Friday?') toward systemic inquiries ('What automated check should have flagged that dependency incompatibility before merge?'). Openly celebrate the engineers who triaged and resolved the outage under high pressure.\n\n"
            "2. **Preventing Action Item Bankruptcy**: A common failure mode is generating 25 low-priority action items that languish in Jira for months. Focus strictly on 2–3 high-leverage structural fixes (e.g., adding an integration test reproducing the exact failure mode and adding automated alert webhooks).\n\n"
            "3. **Democratizing Institutional Learning**: Publish the completed postmortem across the entire engineering organization. Sharing failure analyses prevents sibling squads from experiencing identical outages and reinforces a transparent, learning-oriented engineering culture."
        ),
        "follow_ups": [
            {
                "question": "What is the primary objective of the '5 Whys' root-cause methodology?",
                "answer": "To look past superficial human triggers and identify the deep systemic and procedural failures that permitted the bug to reach production."
            },
            {
                "question": "How do you handle an engineer who feels defensive or guilty during a postmortem?",
                "answer": "Reiterate that the system and pipeline failed to protect them, publicly refocusing the meeting on automated guardrails rather than individual actions."
            }
        ]
    },
    {
        "id": "LEAD-10",
        "arabic_explanation": (
            "كيف تتخذ قرار البناء الذاتي مقابل الشراء أو استخدام حل جاهز (Build versus Buy) للمكتبات وحزم الـ SDK في أندرويد؟\n\n"
            "1. إطار عمل التقييم الاستراتيجي (Core vs. Context Framework):\n"
            "   - **Core (جوهر الميزة التنافسية للشركة)**:\n     * الشيء الذي يميز تطبيقك عن جميع المنافسين (مثل: خوارزمية تسعير التوصيل في أوبر، أو محرك معالجة الصوت في Spotify).\n     * **القاعدة: ابنِ دائماً بنفسك (Build)** لامتلاك الملكية الفكرية والتحكم الكامل في الأداء والتطوير.\n   - **Context (البنية التحتية والوظائف المساعدة)**:\n     * وظائف ضرورية لتشغيل التطبيق لكنها ليست ميزتك التنافسية (مثل: عرض الخرائط، إرسال الإشعارات، معالجة الدفع ببطاقات الائتمان، أو قص وتعديل الصور).\n     * **القاعدة: اشترِ أو استخدم حلاً جاهزاً موثوقاً (Buy / Open Source)** لتوفير الوقت والتركيز على الـ Core.\n\n"
            "2. التكلفة الإجمالية للملكية (Total Cost of Ownership - TCO):\n   - يعتقد المطورون خطأً أن كتابة الحل داخلياً \"مجانية\"!\n   - تكلفة البناء الداخلي تشمل: رواتب المهندسين أثناء البناء، تكلفة الصيانة السنوية المستمرة، مواكبة تحديثات إصدارات أندرويد السنوية، وتصحيح الثغرات الأمنية.\n\n"
            "3. المخاطر التقنية لشراء واستخدام SDKs خارجية في أندرويد:\n   - **انتفاخ الحجم (APK Size Bloat)**: إضافة 15MB لحجم التطبيق.\n   - **أمان وخصوصية البيانات (GDPR/Compliance)**: هل الـ SDK تتتبع بيانات المستخدمين خلسة وتعرض التطبيق للحظر في Google Play؟\n   - **استهلاك البطارية واستقرار النظام**: هل تشغل Background Services تسبب OOM أو ANR؟\n   - **خطر الهجر (Abandonware)**: ماذا لو توقف المطور عن تحديث المكتبة مع إطلاق Android 15؟"
        ),
        "practical_walkthrough": (
            "مصفوفة تقييم عملية لقرار Build vs Buy (مثال: محرك المحادثة الفورية في تطبيق تجاري):\n"
            "```markdown\n"
            "| المعيار | الخيار 1: بناء نظام Chat داخلياً | الخيار 2: شراء SDK جاهز (Stream / Sendbird) |\n"
            "|---|---|---|\n"
            "| **الزمن اللازم للوصول للسوق (Time to Market)** | 6 إلى 9 أشهر | أسبوعان إلى شهر واحد |\n"
            "| **تكلفة التطوير المبدئية** | رواتب 4 مهندسين (~$200,000) | رسوم إعداد واشتراك شهري ($1,500/mo) |\n"
            "| **التوافق وميزات الموبايل** | مجهود ضخم: WebSockets, Local Room Caching, Reconnects | جاهزة: Offline Sync, Push Notifications, Media Uploads |\n"
            "| **التحكم والخصوصية** | تحكم كامل 100% في البيانات | البيانات مخزنة لدى طرف ثالث (تتطلب تدقيق أمني) |\n"
            "| **القرار النهائي والتبرير** | مرفوض (سيعطل إطلاق التطبيق ويشتت الفريق) | **تم اختياره** للوصول السريع للسوق مع عزله وراء Interface |\n"
            "```\n"
            "القاعدة الذهبية عند الشراء: **اعزل الـ SDK وراء Interface داخلي (Adapter Pattern)** حتى تتمكن من استبدالها لاحقاً إذا رفع المورد أسعاره دون إعادة كتابة التطبيق!"
        ),
        "quick_answer": "Decide build versus buy using the Core vs. Context framework: build custom solutions for core business differentiators that define your competitive edge; buy or use open-source SDKs for commodity infrastructure like analytics, maps, or chat. Evaluate the Total Cost of Ownership (ongoing maintenance, Android OS upgrades, APK size, security compliance) and encapsulate third-party SDKs behind internal interfaces.",
        "best_answer": (
            "Navigating the Build vs. Buy architectural dilemma requires balancing strategic differentiation against long-term maintenance overhead:\n\n"
            "1. **Strategic Core vs. Context Alignment**:\n"
            "   - **Core**: Capabilities that directly drive competitive differentiation and customer value (e.g. proprietary financial transaction routing). Build internally to maintain intellectual property, latency control, and roadmap flexibility.\n   - **Context**: Commodity capabilities required for application operation (e.g., payment gateway bridges, push notification delivery, video streaming pipelines). Buy SaaS or adopt tier-1 open-source solutions to maximize speed to market.\n\n"
            "2. **Total Cost of Ownership (TCO) Calculation**:\n"
            "   - Building internally carries massive hidden costs: opportunity cost of diverged engineering talent, continuous maintenance across annual Android OS breaking changes (e.g., photo picker migrations, background service restrictions), bug remediation, and documentation overhead.\n\n"
            "3. **Mobile-Specific Vendor Due Diligence**:\n"
            "   - Audit candidate SDKs against strict mobile criteria:\n     - **Binary Footprint**: Impact on download size (AAB/APK size) and method count limits.\n     - **Stability & Performance**: Background thread usage, memory consumption, and Crashlytics reputation.\n     - **Security & Privacy**: Adherence to Google Play User Data policies, runtime permissions, and transparent network telemetry.\n\n"
            "4. **Encapsulation via the Adapter Pattern**:\n"
            "   - Never allow vendor SDK classes to leak across domain code. Wrap external SDKs behind an internal abstraction interface, insulating the codebase from vendor deprecation or pricing hikes."
        ),
        "deep_answer": (
            "From an engineering governance and risk management angle, third-party mobile SDKs represent major supply-chain vulnerabilities:\n\n"
            "1. **Supply-Chain Security Audits**: Malicious SDK updates can silently introduce credential harvesting or violate user privacy policies, leading to immediate Google Play store de-platforming. Enforce dependency hash pinning, monitor CVE vulnerability databases, and review SDK ProGuard/R8 rules to ensure sensitive classes are not un-obfuscated.\n\n"
            "2. **Vendor Lock-In and Exit Strategy**: Always define an explicit exit gate before integrating proprietary SDKs. If a vendor doubles their license pricing in year 2, how long would it take the squad to migrate? If migration takes more than 2 sprints due to deep framework entanglement, the architecture lacks sufficient abstraction.\n\n"
            "3. **Open-Source Health Metrics**: When considering open-source libraries, audit commit frequency, issue triage velocity, corporate backing (e.g. Square, Google, JetBrains), and active Kotlin Multiplatform roadmaps to avoid adopting abandonware."
        ),
        "follow_ups": [
            {
                "question": "Why should third-party SDKs be encapsulated behind internal interface adapters?",
                "answer": "To prevent vendor-specific types from polluting business logic, making it easy to swap or remove the vendor without rewriting application code."
            },
            {
                "question": "What is the primary operational danger of integrating unvetted commercial SDKs into an Android app?",
                "answer": "Privacy violations or background tracking that can result in immediate Google Play policy enforcement and app removal."
            }
        ]
    },
    {
        "id": "LEAD-11",
        "arabic_explanation": (
            "اختلف الفريق الهندسي بشدة حول استخدام نمط MVVM مقابل MVI في التطبيق الجديد. كيف تقود الفريق لاتخاذ قرار موضوعي قائم على القيود؟\n\n"
            "1. طبيعة الخلافات المعمارية في الفرق:\n"
            "   - غالباً ما تتحول النقاشات حول الأنماط المعمارية إلى \"حروب دينية (Religious Tech Wars)\"؛ كل مهندس يدافع عن النمط الذي اعتاد عليه بحماس، مما يسبب تعطل اتخاذ القرار وتوتر بيئة العمل.\n   - دور القائد الهندسي هو **نزع الطابع الشخصي عن النقاش، وتحويله من \"ماذا أحب أنا؟\" إلى \"ما هي القيود والاحتياجات الحقيقية لمشروعنا وفريقنا؟\"**.\n\n"
            "2. المقارنة الهندسية الموضوعية بين MVVM و MVI:\n   - **MVVM (Model-View-ViewModel)**:\n     * المميزات: مألوف جداً لجميع المطورين، سهل التعلم، كمية كود مكرر (Boilerplate) قليلة، مناسب جداً للشاشات البسيطة والمتوسطة.\n     * العيوب: تعدد مصادر الحالة (`_stateA`, `_stateB`) قد يسبب حالات سباق وتضارب غير متوقع في الشاشات شديدة التعقيد.\n   - **MVI (Model-View-Intent)**:\n     * المميزات: تدفق أحادي صارم (Unidirectional Data Flow - UDF)، مصدر وحيد للحقيقة (`UiState` كائن واحد ثابت)، إمكانية تتبع الأخطاء وتسجيل جميع الأحداث وإعادة تشغيلها (Time-travel debugging) بسهولة.\n     * العيوب: كود مكرر كثير (Actions, Intents, Reducers, Effects)، منحنى تعلم أعلى، وتخصيص كائنات جديدة في الـ Heap مع كل حدث.\n\n"
            "3. خطوات قيادة القرار الهندسي:\n   - **1. عمل Prototype مصغر ومحدد بوقت (Timeboxed Spike)**: بناء نفس الشاشة المعقدة بكلا النمطين في يومي عمل.\n   - **2. وضع مصفوفة معايير موضوعية**: مقارنة سهولة الاختبار، ومنحنى التعلم لأعضاء الفريق الجدد، وسرعة التطوير.\n   - **3. اتخاذ القرار والالتزام به (Disagree and Commit)**: بعد الاتفاق، توثيق القرار في ADR، والتزام الجميع به لمنع تشتت الكود."
        ),
        "practical_walkthrough": (
            "مصفوفة تقييم مقارنة لاتخاذ قرار موضوعي في اجتماع الفريق:\n"
            "```markdown\n"
            "### مصفوفة تقييم المعمارية لاختيار نمط العرض (Presentation Layer):\n"
            "\n"
            "| المعيار المرجح (الوزن 1-5) | MVVM (Multiple StateFlows) | MVI (Single Immutable UiState) |\n"
            "|---|---|---|\n"
            "| **سهولة التنبؤ بالحالة ومنع التضارب (وزن 5)** | 3/5 (تعدد الـ Flows يسبب حالات وسيطة) | **5/5 (حالة ذرية واحدة مستحيلة التضارب)** |\n"
            "| **منحنى التعلم وإنتاجية الفريق الحالي (وزن 4)** | **5/5 (الجميع يتقنه بالفعل)** | 3/5 (يتطلب تدريب أسبوعين للـ Juniors) |\n"
            "| **كمية الكود الروتيني (Boilerplate) (وزن 3)** | **4/5 (كود مباشر وسريع)** | 2/5 (Sealed classes للـ Intents والـ Reducers) |\n"
            "| **توافق ممتاز مع Jetpack Compose (وزن 5)** | 4/5 | **5/5 (Compose يعشق الحالة الأحادية الثابتة)** |\n"
            "| **إجمالي النقاط المرجحة** | 67 نقطة | **72 نقطة (فوز MVI للشاشات المعقدة)** |\n"
            "```\n"
            "صياغة القرار التوافقي الذكي (Hybrid Pragmatism):\n"
            "\"سنعتمد نمط MVI المبسط (Single UiState مع StateFlow ودوال أحداث عادية في ViewModel بدلاً من Sealed Intents المعقدة) لنحصل على أمان الحالة الأحادية في Compose دون إغراق الفريق في كود مكرر غير ضروري.\""
        ),
        "quick_answer": "Lead the team to a constraint-based decision by depersonalizing the debate, building a shared rubric comparing MVVM and MVI against project variables (Compose compatibility, team seniority, state complexity), running a timeboxed prototype on a real screen, making a firm collaborative choice documented in an ADR, and enforcing 'Disagree and Commit'.",
        "best_answer": (
            "Resolving architectural deadlocks requires transforming subjective ideological debates into evidence-based systems engineering:\n\n"
            "1. **Depersonalize and Establish Objective Evaluation Criteria**:\n"
            "   - Remove dogma by defining evaluation dimensions weighted by project context: Jetpack Compose state compatibility, state predictability under concurrent flows, junior onboarding ramp-up time, and boilerplate verbosity.\n\n"
            "2. **Comparative Empirical Prototyping**:\n"
            "   - Commission a 2-day timeboxed spike where two engineers build the identical complex screen (e.g. checkout form with validation and payment polling) in lightweight MVVM and strict MVI. Compare pull requests side-by-side evaluating testability, readability, and state race condition susceptibility.\n\n"
            "3. **Synthesize Pragmatic Hybrid Solutions**:\n"
            "   - Often, the optimal engineering solution is a pragmatic synthesis. Adopt a 'Lightweight MVI' approach: a single immutable `StateFlow<UiState>` coupled with direct ViewModel action methods (`onSearchQueryChanged(q)`), capturing MVI's single source of truth without the cognitive friction of exhaustive Sealed Intent reducers.\n\n"
            "4. **Institutionalize via ADR & Disagree and Commit**:\n"
            "   - Author an ADR formalizing the standard. Establish team alignment around the principle of 'Disagree and Commit' to prevent rogue architectural fragmentation across feature modules."
        ),
        "deep_answer": (
            "From an engineering leadership and team dynamics perspective, architectural consistency supersedes local perfection:\n\n"
            "1. **Codebase Cohesion Value**: A medium-tier architecture applied with 100% consistency across 50 modules delivers significantly higher velocity than having 3 squads using pure MVI, 2 squads using MVVM, and 1 squad using Clean MVP. Consistent patterns allow engineers to switch squads seamlessly with zero cognitive friction.\n\n"
            "2. **Compose State Hoisting Reality**: In modern Jetpack Compose development, the line between MVVM and MVI has largely blurred. Google's official architecture guidelines prescribe a single unidirectional `StateFlow<UiState>` hoisted from ViewModel to Composable, standardizing the ecosystem on state-driven UDF patterns.\n\n"
            "3. **Navigating Technical Deadlocks**: When a squad remains in a 50/50 split, the technical lead must break the tie decisively based on the documented rubric. Explain the rationale transparently, listen to remaining concerns, and reinforce that team velocity requires moving forward as one cohesive unit."
        ),
        "follow_ups": [
            {
                "question": "What is the core advantage of a single immutable UiState (MVI) over multiple independent LiveData/StateFlows (MVVM)?",
                "answer": "It eliminates intermediate impossible states and race conditions, guaranteeing that the UI renders an atomic, synchronized snapshot of data."
            },
            {
                "question": "What does the leadership principle 'Disagree and Commit' mean in practice?",
                "answer": "Engineers debate vigorously and voice concerns, but once a decision is made, everyone fully commits to executing it without passive resistance."
            }
        ]
    },
    {
        "id": "LEAD-12",
        "arabic_explanation": (
            "حدثني عن حادث إنتاجي حرج (Production Incident) قمت بتحمل مسؤوليته وإدارته، وكيف منعت تكراره نهائياً؟\n\n"
            "1. إطار عمل الإجابة المقنعة في المقابلة (STAR Method):\n"
            "   - **S (Situation)**: سياق الموقف وحجم التطبيق وخطورة الحادث.\n   - **T (Task)**: مسؤوليتك المباشرة كمهندس قيادي لاحتواء الكارثة وحماية المستخدمين والشركة.\n   - **A (Action)**: الخطوات التقنية السريعة والمنظمة التي اتخذتها لحل المشكلة.\n   - **R (Result)**: النتائج بالأرقام، والدروس المستفادة، والإجراءات الوقائية الدائمة.\n\n"
            "2. مثال لسيناريو أندرويد واقعي واحترافي:\n   - **الموقف**: بعد إطلاق التحديث الرئيسي لتطبيق التجارة الإلكترونية، بدأ معدل الـ Crash-free يتدهور ووصل إلى 94% فوراً، وجميع الكراشات تحدث عند فتح التطبيق (Startup Crash) على هواتف Android 13 و 14.\n   - **الإجراءات الفورية المتخذة**:\n     1. **وقف الطرح فوراً (Halt Staged Rollout)** في Google Play Console عند نسبة 10% لمنع وصول الكارثة للملايين.\n     2. **فحص الـ Stacktrace في Crashlytics**: اكتشاف `IllegalStateException: Room cannot find Migration from 14 to 15`.\n     3. **تعطيل الميزة سحابياً (Feature Flag)** أو معرفة أن المشكلة في كود قاعدة البيانات المحلي التي تتطلب Hotfix فوري.\n     4. **إطلاق الـ Hotfix**: التفرع من الـ Release Tag، كتابة كود الـ Migration الصريح مع كتابة Automated Migration Test يثبت الترقية، وزيادة `versionCode` وطرح التحديث فوراً بنسبة 100% مع طلب مراجعة عاجلة (Expedited Review).\n   - **النتائج والوقاية المستدامة**:\n     * استعادة الاستقرار لـ 99.95% في خلال 4 ساعات.\n     * إضافة فحص آلي في الـ CI يقوم بمقارنة ومطابقة ملفات الـ Schema الخاصة بـ Room واختبار كل مسارات الترقية (`MigrationTestHelper`) قبل السماح بدمج أي PR يمس قاعدة البيانات."
        ),
        "practical_walkthrough": (
            "سرد الحادث بأسلوب مهندس Senior متزن وموثوق:\n"
            "```markdown\n"
            "\"في عملي السابق، كنا نطلق تحديثاً ربع سنوي لتطبيق حجز الرحلات (5 ملايين مستخدم نشط).\n"
            "خلال أول 6 ساعات من بدء الـ Staged Rollout بنسبة 5%، انطلق تنبيه P0 على Slack من Crashlytics:\n"
            "معدل الكراش قفز إلى 5.2% مع خطأ `Fatal SQLiteException`.\n"
            "\n"
            "قمت بقيادة الاستجابة الفورية:\n"
            "1. أمرت فوراً بإيقاف الـ Rollout على Play Console لحصر نطاق الضرر في الـ 5% فقط.\n"
            "2. حللت الـ De-obfuscated Stacktrace واكتشفت أن أحد الـ PRs أضاف عموداً جديداً `seat_preference`\n"
            "   في Room دون كتابة Migration Script، واعتمد المطور على fallbackToDestructiveMigration()\n"
            "   في الـ Debug فقط، بينما الـ Release انفجر لعدم وجود Migration!\n"
            "3. أنشأت فرع hotfix/3.2.1 من تاج الإصدار، وكتبت كود الـ Migration الصريح لاحتواء بيانات المستخدمين.\n"
            "4. كتبت Room Migration Test يحاكي قاعدة بيانات قديمة ويرقيها، وتأكدت من نجاحه.\n"
            "5. تم تجميع الـ AAB ورفعه ونشره، وعاد معدل الـ Crash-free إلى 99.96%.\n"
            "\n"
            "لمنع تكرار الحادث، قمت بعقد Blameless Postmortem وأضفنا أمرين في الـ CI:\n"
            "- تفعيل `room.schemaLocation` في Gradle لتوثيق كل تعديل schema كملف JSON.\n"
            "- إضافة اختبار آلي إلزامي في CI يشغل `MigrationTestHelper` على جميع الإصدارات السابقة.\n"
            "منذ ذلك اليوم، لم يتكرر أي حادث database migration في التطبيق نهائياً.\""
            "```"
        ),
        "quick_answer": "Structure your incident narrative using the STAR framework: quantify the blast radius, demonstrate rapid triage actions (halting staged rollouts, analyzing Crashlytics stack traces, cutting a surgical hotfix branch), report business recovery metrics, and emphasize systemic preventative guardrails implemented to prevent identical regressions.",
        "best_answer": (
            "A compelling production incident narrative showcases technical calmness, operational rigor, and systemic ownership under pressure:\n\n"
            "1. **Situation & Immediate Triage (STAR — Situation & Task)**:\n"
            "   - Frame a realistic, high-stakes scenario: e.g. a startup crash spiking during an active release cycle due to an unhandled Room database migration path affecting 5% of users. Quantify the business impact and user friction immediately.\n\n"
            "2. **Methodical Incident Containment (STAR — Action)**:\n"
            "   - Detail the systematic triage sequence:\n     - **Blast Radius Containment**: Immediately halt the Google Play staged rollout to prevent further user exposure.\n     - **Telemetry Forensics**: Inspect de-obfuscated Crashlytics breadcrumbs and device logs to isolate the exact commit introducing the defect.\n     - **Surgical Hotfix Isolation**: Branch directly from the production release tag (`hotfix/2.4.1`), write the missing database migration script, and accompany it with an automated test reproducing the upgrade failure.\n     - **Deployment & Verification**: Fast-track the signed build through the Internal Testing track, verify migration integrity, and submit an expedited production release to Google Play.\n\n"
            "3. **Business Impact & Permanent Safeguards (STAR — Result)**:\n"
            "   - Highlight metric restoration (crash-free rate returned to 99.95%).\n   - Detail institutional prevention: host a blameless postmortem and implement automated CI gates (e.g. running AndroidX `MigrationTestHelper` across all historical schema JSON exports on every PR touching Room entities)."
        ),
        "deep_answer": (
            "From an engineering leadership and executive communication angle, owning an incident demonstrates character:\n\n"
            "1. **Radical Ownership vs. Defensiveness**: Never deflect blame onto third-party libraries, QA testers, or junior developers. State clearly: 'As the technical lead, I owned the deployment gate, and our automated testing framework failed to catch the regression.' Taking radical ownership builds immense credibility with interviewers.\n\n"
            "2. **Communication Cadence During Sev-1 Outages**: Describe how you managed cross-functional stakeholders during the crisis. Establishing a dedicated incident Slack bridge, updating Product and Customer Support every 30 minutes with factual progress, and shielding the core engineering triage team from executive noise illustrates true leadership.\n\n"
            "3. **Long-Term Architectural Hardening**: Beyond immediate bug fixes, explain how the incident triggered deeper platform resilience: e.g., decoupling critical startup initialization tasks so a single module crash does not bring down the entire Android process."
        ),
        "follow_ups": [
            {
                "question": "What is the first operational action to take when a critical crash is detected during a staged rollout?",
                "answer": "Immediately halt the staged rollout in Google Play Console to contain the blast radius and prevent new users from downloading the flawed build."
            },
            {
                "question": "How can you prevent Room database migration crashes automatically in CI?",
                "answer": "Export schema JSON files using `room.schemaLocation` and enforce automated JUnit tests with `MigrationTestHelper` verifying all migration paths."
            }
        ]
    },
    {
        "id": "LEAD-13",
        "arabic_explanation": (
            "اكتشفت ثغرة أمنية حرجة (Critical Vulnerability) قبل موعد الإطلاق التجاري بيومين فقط. كيف تدير عملية اتخاذ قرار الإطلاق مع إدارة الشركة؟\n\n"
            "1. الموقف الحرج وحجم الضغوط:\n"
            "   - حملة تسويقية بملايين الدولارات جاهزة للإطلاق بعد 48 ساعة، ومواعيد نهائية صارمة مع شركاء العمل.\n   - فجأة، يكتشف فحص الأمان ثغرة خطيرة (مثل: تسريب رموز التحقق JWT في ملف الـ Logs، أو إمكانية تجاوز شاشة القفل عبر Deep Link غير محمي، أو ثغرة في مكتبة طرف ثالث تسمح بالتلاعب في الدفع).\n   - المهندس الضعيف يخفي الأمر أو يوافق على الإطلاق تحت الضغط! **المهندس القيادي (Lead) يحمي سمعة الشركة وأمان المستخدمين بحزم واحترافية**.\n\n"
            "2. إطار عمل تقييم المخاطر (Triage & Severity Assessment):\n   - تقييم الثغرة وفقاً لمعايير **CVSS (Common Vulnerability Scoring System)**:\n     * **القابلية للاستغلال (Exploitability)**: هل يمكن لأي شخص استغلالها عن بعد بسهولة؟ أم تتطلب جهازاً مكسور الحماية (Rooted) مع وصول مادي للهاتف؟\n     * **نطاق الضرر (Blast Radius)**: هل تسرب بيانات بنكية وكلمات مرور؟ أم مجرد بيانات غير حساسة؟\n\n"
            "3. مسارات الحلول المعروضة على الإدارة (Decision Pathways):\n   - **الخيار 1 (الإصلاح الجراحي العاجل - Fast-Track Patch)**: إذا كان الحل بسيطاً ومضموناً (سطر كود واحد مع اختبار أمان)، يتم تطبيقه وإعادة اختباره في 12 ساعة والإطلاق في الموعد.\n   - **الخيار 2 (الإطلاق المظلم مع تعطيل الميزة - Dark Launch / Feature Flag Kill-Switch)**: إطلاق التطبيق في موعده مع **تعطيل الميزة المصابة بالكامل سحابياً** حتى يتم إصلاحها لاحقاً دون إيقاف باقي التطبيق.\n   - **الخيار 3 (تأجيل الإطلاق الإلزامي - Hard Block Launch)**: إذا كانت الثغرة تمس البيانات المصرفية أو التشفير الأساسي ويستحيل إخفاؤها، يتم اتخاذ قرار حاسم بتأجيل الإطلاق وتوضيح المخاطر القانونية والمالية الكارثية للإدارة."
        ),
        "practical_walkthrough": (
            "مذكرة إحاطة تنفيذية (Executive Security Brief) تُعرض على الإدارة لحسم القرار:\n"
            "```markdown\n"
            "### مذكرة أمنية عاجلة: تقييم إطلاق الإصدار 2.0 (Security Launch Gate)\n"
            "\n"
            "#### ملخص الثغرة (Vulnerability Summary):\n"
            "تم اكتشاف ثغرة مصنفة [CVSS 8.5 - High] في معالج الـ Deep Links:\n"
            "يمكن لرابط خبيث من متصفح الويب تجاوز التحقق الثنائي (2FA) ونقل الـ Auth Token لجهة خارجية.\n"
            "\n"
            "#### تحليل المخاطر التجارية (Business Risk Analysis):\n"
            "- **المخاطرة في حال الإطلاق**: سرقة حسابات المستخدمين، غرامات امتثال GDPR، وأضرار جسيمة لسمعة الشركة.\n"
            "- **المخاطرة في حال التأجيل**: تأخير الحملة التسويقية لمدة 48 ساعة فقط.\n"
            "\n"
            "#### التوصية الهندسية والخيارات المتاحة:\n"
            "1. **[الخيار الموصى به - التعديل الجراحي]**: تعطيل استجابة الـ Deep Link لتسجيل الدخول مؤقتاً\n"
            "   وإجبار تسجيل الدخول اليدوي الآمن فقط عبر الشاشة. يستغرق التنفيذ والاختبار 8 ساعات،\n"
            "   ويحافظ على موعد الإطلاق بنسبة 100% وبأمان تام.\n"
            "2. **[الخيار البديل]**: تأجيل الإطلاق بالكامل إلى يوم الاثنين القادم للإصلاح الشامل.\n"
            "```\n"
            "بهذا الأسلوب، تقدم للإدارة بدائل تقنية ذكية لحماية الموعد بدلاً من مجرد إلقاء اللوم أو إيقاف المشروع."
        ),
        "quick_answer": "Manage pre-launch critical vulnerabilities through rigorous risk quantification (CVSS score, exploitability, blast radius). Present executive leadership with clear options rather than open-ended problems: an expedited surgical patch, dark-launching with the vulnerable feature kill-switched via remote config, or an unavoidable launch freeze if customer financial data or compliance is at risk.",
        "best_answer": (
            "Discovering a critical security vulnerability days before a major commercial launch requires decisive risk management and executive communication:\n\n"
            "1. **Triage Severity and Exploitability**:\n"
            "   - Immediately assess the vulnerability using standard frameworks (CVSS score):\n     - Can the flaw be exploited remotely, or does it require physical access to a rooted device?\n     - What is the blast radius: does it leak authentication tokens, payment details, or personal identifiable information (PII)?\n\n"
            "2. **Formulate Pragmatic Mitigation Pathways**:\n"
            "   - Never present executive stakeholders with a blunt roadblock without viable engineering alternatives:\n     - **Pathway A (Surgical Hotfix & Expedited Re-test)**: If the fix is isolated (e.g. adding `android:exported=\"false\"` or input sanitization), apply the patch, run automated security suites, and proceed with launch.\n     - **Pathway B (Dark Launch via Remote Kill-Switch)**: If the flaw resides in a specific non-core feature, disable that feature globally via Firebase Remote Config / Feature Flags, allowing the broader marketing launch to proceed on schedule with the vulnerable surface disabled.\n     - **Pathway C (Mandatory Launch Delay)**: If the flaw compromises core identity or financial encryption and cannot be gated, firmly advise delaying the launch, translating potential regulatory fines (GDPR/PCI-DSS) and brand destruction into concrete business numbers.\n\n"
            "3. **Transparent Stakeholder Alignment**:\n"
            "   - Document the decision matrix in an executive brief signed off by Engineering, Product, and Legal leads."
        ),
        "deep_answer": (
            "From an engineering ethics and professional integrity standpoint, security gating defines leadership:\n\n"
            "1. **Resisting Executive Pressure**: Under intense commercial pressure, business stakeholders may ask: 'Can we just ship and fix it in an update next week?' A senior lead must hold the line: mobile updates are not instantaneous; millions of users who download the build will retain the unpatched vulnerability for months. Knowingly shipping exploitable user-data vulnerabilities violates engineering ethics and exposes the company to legal liability.\n\n"
            "2. **Google Play Store Policy Repercussions**: Remind leadership that launching with critical vulnerabilities (e.g. embedded plain-text API secrets or insecure cryptographic algorithms) triggers automated Google Play Security Review rejections or sudden store delisting, turning a 2-day marketing delay into a catastrophic month-long suspension.\n\n"
            "3. **Post-Launch Red Teaming**: Ensure the incident feeds back into the DevSecOps pipeline by integrating static application security testing (SAST) tools like MobSF or Semgrep into the pull request CI gate, guaranteeing that similar vulnerabilities are caught weeks before release candidates are frozen."
        ),
        "follow_ups": [
            {
                "question": "How can feature flags salvage a scheduled commercial launch when a feature has a security flaw?",
                "answer": "By remotely kill-switching the affected feature server-side, allowing the rest of the application to launch safely on schedule."
            },
            {
                "question": "Why is 'we will fix it in a patch next week' an unacceptable response to a critical mobile vulnerability?",
                "answer": "Because mobile users do not update simultaneously; millions of devices will remain vulnerable in the wild indefinitely."
            }
        ]
    },
    {
        "id": "LEAD-14",
        "arabic_explanation": (
            "استلمت قيادة مشروع أندرويد قديم (Legacy App) يعاني من انعدام الاختبارات وتكرار الأخطاء وتذمر المطورين. ما هي خطتك الإستراتيجية لأول 90 يوماً (First 90-Day Plan)؟\n\n"
            "1. الفخ القاتل الذي يقع فيه المطورون الجدد:\n"
            "   - الحماس الزائد في الأسبوع الأول والمطالبة بإعادة كتابة التطبيق بالكامل من الصفر (The Total Rewrite Trap)!\n   - إعادة الكتابة توقف تطوير ميزات الشركة لشهور، وتعيد إنتاج نفس الأخطاء القديمة، وتفشل في 80% من الحالات.\n   - النهج الهندسي الناضج يعتمد على **الاستقرار أولاً، والتحسين المرحلي التدريجي (Strangler Fig Pattern)**.\n\n"
            "2. خطة الـ 90 يوماً الاستراتيجية:\n   - **الأيام 1 - 30 (الاستكشاف، القياس، وتأمين البيئة - Listen, Observe & Measure)**:\n     * الجلوس مع المطورين وفريق المنتج لفهم نقاط الألم وأولويات العمل.\n     * إنشاء **أدوات المراقبة (Observability Baseline)**: ضبط Crashlytics و Android Vitals لمعرفة أماكن تكرار الكراشات بدقة.\n     * تثبيت بيئة الـ CI: إصلاح الاختبارات المتقلبة وتسريع البناء البارد.\n     * إقرار **قاعدة الكشافة (Boy Scout Rule)**: إلزام المطورين بعدم لمس أي ملف دون كتابة اختبار بسيط له وترتيبه.\n   - **الأيام 31 - 60 (وضع المعايير وتأمين التغييرات الجديدة - Guard & Standardize)**:\n     * تطبيق مبدأ **\"Test-Driven Bug Fixing\"**: أي Bug جديد يُكتشف يُمنع إصلاحه إلا بعد كتابة Unit Test فاشل يثبت المشكلة أولاً ثم إصلاح الكود ليمر الاختبار.\n     * تفعيل أدوات الفحص الساكن (Spotless + Detekt) مع Baseline لمنع دخول أي ديون تقنية جديدة للفرع الرئيسي.\n     * كتابة أول ADR يحدد المعمارية الرسمية للميزات الجديدة (مثل Clean Architecture مع Compose و Coroutines).\n   - **الأيام 61 - 90 (التطوير المعماري ومضاعفة السرعة - Modernize & Accelerate)**:\n     * بدء تجزئة أول موديول معيب وعزله (Modularization via Strangler Fig).\n     * تفعيل الـ Remote Build Cache لتقليل وقت التجميع في الـ CI بنسبة 50%.\n     * استعراض الإنجازات بالأرقام أمام الإدارة: ارتفاع الـ Crash-free من 97% إلى 99.5%، وتسريع وقت تسليم الميزات الجديدة."
        ),
        "practical_walkthrough": (
            "خارطة طريق خطة الـ 90 يوماً التنفيذية (90-Day Execution Roadmap):\n"
            "```markdown\n"
            "### خارطة طريق الـ 90 يوماً لإنقاذ وترقية تطبيق Legacy Android:\n"
            "\n"
            "| المرحلة الزمنية | الأهداف والأنشطة الرئيسية | مؤشرات النجاح المستهدفة (OKRs) |\n"
            "|---|---|---|\n"
            "| **الشهر 1: الملاحظة والتأمين**<br>(الأيام 1-30) | - تدقيق الاعتماديات والمكتبات المهجورة.<br>- قياس زمن الـ CI ومعدل الكراش الحقيقي.<br>- جلسات 1:1 مع المهندسين وفريق المنتج.<br>- وقف نزيف الأخطاء عبر Boy Scout rule. | - تقرير شامل بحالة الديون التقنية.<br>- لوحة قياس Vitals حية ومفعلة.<br>- صفر اختبارات متقلبة في الـ CI. |\n"
            "| **الشهر 2: البوابات والمعايير**<br>(الأيام 31-60) | - فرض Unit Tests إجبارية لأي إصلاح Bug.<br>- تفعيل Detekt & Android Lint baselines.<br>- إقرار ADR للميزات الجديدة.<br>- تدريب الفريق على Compose و Coroutines. | - تغطية 100% لجميع الأخطاء الجديدة بتستات.<br>- انخفاض الـ Escaped Bugs بنسبة 40%.<br>- تسليم أول ميزة بالمعمارية الجديدة. |\n"
            "| **الشهر 3: التحديث والتسريع**<br>(الأيام 61-90) | - تجزئة أكثر موديول مسبب للكراشات.<br>- تفعيل Gradle Remote Build Cache.<br>- توثيق الإنجازات في مراجعة ربع سنوية. | - ارتفاع Crash-free من 97.2% إلى 99.5%.<br>- خفض زمن بناء CI من 35 إلى 10 دقائق.<br>- ارتفاع مؤشر رضا المهندسين. |\n"
            "```"
        ),
        "quick_answer": "Structure your first 90 days into three distinct 30-day horizons: Days 1–30 focuses on listening, establishing observability baselines, and stabilizing the CI pipeline; Days 31–60 institutes quality gates, mandatory test-driven bug fixes, and ADR architectural standards; Days 61–90 executes targeted modular refactoring via the Strangler Fig pattern and celebrates quantifiable stability gains.",
        "best_answer": (
            "Rescuing an inherited legacy codebase requires a disciplined, structured 30-60-90 day framework that builds team trust before touching core architecture:\n\n"
            "1. **Days 1–30: Listen, Observe, and Establish Baselines**:\n"
            "   - **Avoid the Rewrite Trap**: Reject calls for an immediate ground-up rewrite. Understand business domain history and developer friction through 1-on-1 discovery interviews.\n   - **Telemetry & Baseline Observability**: Audit Google Play Vitals and Crashlytics. Measure key operational baselines: crash-free user rate, cold startup latency, and CI execution times.\n   - **Pipeline Hygiene**: Fix broken CI scripts and stabilize flaky tests so developers regain confidence in automated gates.\n\n"
            "2. **Days 31–60: Standardize Quality Gates & Prevent New Debt**:\n"
            "   - **Test-Driven Defect Resolution**: Enforce an uncompromising team policy: no production bug is fixed without an accompanying automated test that reproduces the failure before applying the fix.\n   - **Automated Linters with Baselines**: Introduce Spotless and Detekt with baseline files to freeze legacy technical debt and reject any new violations.\n   - **Architectural Standards (ADR)**: Author an ADR codifying the architectural standard (e.g. MVI + Compose) mandated for all net-new screens.\n\n"
            "3. **Days 61–90: Modernize, Accelerate, and Demonstrate ROI**:\n"
            "   - **Strangler Fig Refactoring**: Extract the most volatile legacy god-class into an isolated, tested module behind a clean interface.\n   - **Build Performance**: Implement Gradle build caching and parallel execution to halve CI feedback loops.\n   - **Quantifiable Executive Reporting**: Present leadership with measurable wins: crash-free rate improved to 99.5%, defect turnaround times reduced, and developer velocity restored."
        ),
        "deep_answer": (
            "From an organizational change management and cultural perspective, leadership determines adoption:\n\n"
            "1. **Winning Hearts and Minds Before Refactoring Code**: When a new lead arrives and immediately criticizes existing code, legacy team members become defensive. Acknowledge that the legacy code generated the company's revenue and kept the business alive. Position refactoring as empowering the team with modern tooling rather than correcting past mistakes.\n\n"
            "2. **Tackling the Worst Pain Point First**: Identify the single recurring issue that causes developers the most daily frustration (e.g., an unpredictable 45-minute CI build or a flaky database migration). Fixing that single issue in your first 3 weeks earns immediate technical credibility and unlocks team buy-in for future architectural standards.\n\n"
            "3. **Incremental strangler fig vs Big Bang**: Emphasize continuous value delivery. By isolating legacy screens behind feature flags and swapping them incrementally, the product continues shipping user features every sprint while health metrics climb steadily."
        ),
        "follow_ups": [
            {
                "question": "Why is demanding a complete app rewrite in your first month a major red flag for leadership?",
                "answer": "Because it halts product delivery for months, carries massive business risk, and disregards years of hard-won edge case solutions embedded in the legacy code."
            },
            {
                "question": "What is 'Test-Driven Bug Fixing' and why is it vital for legacy projects?",
                "answer": "Writing a failing test that reproduces the bug before touching the code, ensuring the bug is truly understood and preventing it from ever regressing."
            }
        ]
    },
    {
        "id": "LEAD-15",
        "arabic_explanation": (
            "كيف ترفض وتعدل بأدب واحترافية متطلباً من فريق المنتج أو الأعمال يتعارض مع قيود نظام أندرويد الصارمة أو الأمان والخصوصية؟\n\n"
            "1. الخطأ الشائع: الرفض الجاف المباشر:\n"
            "   - إذا قال مدير المنتج: \"نريد تتبع موقع المستخدم بالـ GPS كل 10 ثوانٍ في الخلفية 24 ساعة يومياً\"، وجاء ردك: \"أندرويد يمنع ذلك ومستحيل!\"، فسيراك فريق الأعمال كعائق ومهندس سلبي.\n   - المهندس المحترف لا يكتفي بقول \"لا\"، بل **يفهم الهدف التجاري الحقيقي وراء الطلب، ويشرح القيود بلغة مصلحة المنتج، ويقدم البدائل المتوافقة مع أندرويد (Proposing Idiomatic Alternatives)**.\n\n"
            "2. إطار عمل الحوار الهندسي المقنع (The Pushback Framework):\n   - **1. فهم النية والهدف التجاري (Understand the Underlying 'Why')**:\n     * اسأل: \"ما هي القيمة الحقيقية التي نريد تقديمها للمستخدم من خلال معرفة موقعه طوال اليوم؟\"\n   - **2. شرح عواقب المتطلب بلغة مصلحة الأعمال والمنتج (Business & User Consequences)**:\n     * بدلاً من \"قيود البطارية في أندرويد\": \"تتبع الـ GPS المستمر سيستنزف بطارية الهاتف بنسبة 40% في 3 ساعات، وسيؤدي لتصنيف تطبيقنا في Google Play Vitals كـ 'تطبيق مسيء للبطارية' وخسارة الترتيب في المتجر وتقييمات نجمة واحدة\".\n     * بدلاً من \"سياسات جوجل تمنع ذلك\": \"جوجل بلاي تفرض مراجعة أمنية خاصة لصلاحية `ACCESS_BACKGROUND_LOCATION` وإذا لم يكن هناك سبب جوهري ستسحب التطبيق من المتجر، وأكثر من 85% من المستخدمين يرفضون منح هذه الصلاحية أصلاً\".\n   - **3. تقديم الحلول البديلة المتوافقة مع أندرويد (Idiomatic Android Alternatives)**:\n     * تقديم حل **Geofencing API**: تحديد مناطق جغرافية دائرية يستيقظ التطبيق فقط عند دخولها أو الخروج منها باستهلاك بطارية شبه معدوم.\n     * أو استخدام **Foreground Service** مع إشعار دائم واضح ومفيد للمستخدم أثناء تتبع الرحلة فقط."
        ),
        "practical_walkthrough": (
            "سيناريو حوار واقعي يوضح كيفية إدارة الموقف باحترافية:\n"
            "```markdown\n"
            "### سيناريو واقعي في اجتماع التخطيط:\n"
            "مدير المنتج: \"نريد جمع كل الصور ومقاطع الفيديو من هاتف المستخدم تلقائياً لتحليلها وعمل ألبوم ذكي.\"\n"
            "\n"
            "❌ الرفض الضعيف الصدامي:\n"
            "\"مش هينفع، نظام أندرويد حاطط Scoped Storage وجوجل مش هتوافق.\"\n"
            "\n"
            "✅ الرد الاحترافي البناء والبديل:\n"
            "المهندس: \"أنا فاهم جداً القيمة الممتازة لعمل ألبوم ذكي للمستخدمين، لكن محتاجين نراعي أمرين حاسمين:\n"
            "1. من بداية Android 11 و 13، يفرض النظام سياسة Scoped Storage ويحظر الوصول لكامل مساحة التخزين،\n"
            "   وطلب صلاحية `READ_MEDIA_IMAGES` بالكامل يتطلب موافقة خاصة من جوجل، ويرفضها 70% من المستخدمين خوفاً على خصوصيتهم.\n"
            "2. البديل الأمثل والمدعوم رسمياً من جوجل:\n"
            "   نستخدم **Photo Picker API** الرسمي من أندرويد.\n"
            "   الميزة: يفتح واجهة آمنة تتيح للمستخدم اختيار الصور المحددة التي يريدها فقط،\n"
            "   **بدون الحاجة لطلب أي صلاحيات Runtime نهائياً (Zero Permissions)**!\n"
            "   ده هيرفع ثقة المستخدم في التطبيق بنسبة 100%، ويضمن قبول التحديث في المتجر فوراً بدون أي تأخير.\"\n"
            "```\n"
            "بهذا الأسلوب، حولت \"المستحيل\" إلى ميزة تنافسية تعزز ثقة المستخدم وتحقق هدف المنتج بأمان."
        ),
        "quick_answer": "Push back professionally by uncovering the underlying user goal, articulating constraints in terms of business consequences (battery drain, 1-star reviews, Google Play rejection, high user permission denials), and proactively offering platform-idiomatic alternative APIs (such as Geofencing instead of continuous GPS polling, or the Android Photo Picker instead of broad storage access).",
        "best_answer": (
            "Pushing back constructively on unrealistic product requirements separates engineering partners from order takers:\n\n"
            "1. **Uncover the Underlying Business Motivation ('The Why')**:\n"
            "   - Begin by seeking clarity on the desired business outcome. Product requirements often conflate a high-level user goal with a rigid implementation detail. For instance: 'We need 24/7 background location' usually means 'We want to notify users when they enter a retail store.'\n\n"
            "2. **Frame Constraints in Commercial and User Terms**:\n"
            "   - Avoid citing technical jargon ('Android OS restrictions'). Translate technical realities into business risk:\n     - **Store Rejection Risk**: Google Play enforces draconian reviews for sensitive permissions (`ACCESS_BACKGROUND_LOCATION`, broad storage); violations trigger immediate removal.\n     - **User Churn & Retention**: Aggressive background polling drains battery, surfacing your app on Android's high-battery-usage system warnings and driving uninstalls.\n     - **Permission Opt-In Dropoff**: Prompting for intrusive runtime permissions causes high drop-off rates during user onboarding.\n\n"
            "3. **Propose Idiomatic Platform Solutions**:\n"
            "   - Never say 'No' without presenting 'Here is how we accomplish the exact business goal sustainably':\n     - Replace continuous GPS polling with Google Play services Geofencing API.\n     - Replace broad storage permissions with the modern Android Photo Picker (zero runtime permissions).\n     - Replace persistent background polling with WorkManager periodic sync or Firebase Cloud Messaging (FCM) push notifications."
        ),
        "deep_answer": (
            "From an engineering leadership and strategic alignment perspective, setting platform boundaries builds trust:\n\n"
            "1. **The 'Yes, If' Technique**: Master the collaborative communication pattern: 'Yes, we can achieve that retail proximity alert, if we use the Geofencing API rather than continuous GPS tracking.' This positions engineering as a creative problem-solving partner rather than a bureaucratic blocker.\n\n"
            "2. **Leveraging Official Platform Guidelines as Neutral Arbiters**: When product stakeholders remain skeptical, do not argue personal opinions. Share Google's official Android Developer Quality Guidelines, Android Vitals thresholds, and Play Console Policy documentation. Pointing to Google's public policy shifts the conversation from personal friction to navigating external industry rules.\n\n"
            "3. **Empirical A/B Prototype Demonstrations**: If stakeholders remain convinced that a background feature will not hurt battery life, instrument a rapid prototype measuring battery discharge via Batterystats/Historian on a test device over 12 hours. Showing hard empirical data (e.g. 45% battery drain) resolves the debate definitively with data."
        ),
        "follow_ups": [
            {
                "question": "Why is the Android Photo Picker superior to requesting broad media storage permissions?",
                "answer": "Because it runs in a separate system process requiring zero runtime permissions from the user, preserving privacy and eliminating store review friction."
            },
            {
                "question": "What API replaces continuous background GPS polling for detecting when a user arrives at a store?",
                "answer": "Google Play services Geofencing API, which monitors geographic coordinates hardware-efficiently using cell towers and Wi-Fi with negligible battery drain."
            }
        ]
    }
]


def main() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing_data: list[dict] = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    existing_dict = {item["id"]: item for item in existing_data}
    for item in LEAD_09_15:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions LEAD-09 to LEAD-15. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
