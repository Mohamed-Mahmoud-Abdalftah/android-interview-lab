#!/usr/bin/env python3
"""Generator for LEAD-01 through LEAD-08 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "lead.json"

LEAD_01_08 = [
    {
        "id": "LEAD-01",
        "arabic_explanation": (
            "كيف تشرح المفاضلات المعمارية (Architectural Trade-offs) بوضوح واحترافية في المقابلة التقنية لمنصب Senior/Lead؟\n\n"
            "1. جوهر النضج الهندسي (Senior Mindset):\n"
            "   - المهندس المبتدئ يبحث عن \"الحل المثالي الوحيد\" أو يدافع بتعصب عن نمط معين (Dogmatism).\n   - المهندس الخبير (Senior/Lead) يدرك أنه **لا يوجد حل معماري مثالي بالمطلق؛ كل قرار هندسي هو صفقة مقايضة (There are no solutions, only trade-offs)**.\n\n"
            "2. إطار عمل الشرح المقنع (Trade-off Framework):\n"
            "   - **1. توصيف سياق المشكلة والقيود (Context & Constraints)**: تحديد حجم الفريق، والوقت المتاح للوصول للسوق (Time to Market)، وقيود الأجهزة المستهدفة (Low-end vs High-end)، وحجم قاعدة الكود.\n   - **2. طرح البدائل ومزايا وعيوب كل خيار (Pros & Cons)**: مثلاً مقارنة MVI مقابل MVVM: MVI يعطي قابلية تنبؤ تامة بحالة الواجهة وتتبع الأخطاء في تدفق أحادي، لكنه يفرض Boilerplate عالي وتكلفة إنشاء كائنات جديدة في كل حدث.\n   - **3. التبرير بناءً على القيود المحددة (Decision Rationale)**: شرح لماذا اخترت هذا الحل بالتحديد في هذا المشروع، وما هي العيوب التي قبلت التعايش معها وكيف قمت بتحجيم مخاطرها.\n   - **4. استراتيجية الخروج والتطور (Evolution Strategy)**: كيف يمكن تعديل هذا القرار مستقبلاً إذا تضاعف حجم الفريق أو البيانات."
        ),
        "practical_walkthrough": (
            "مصفوفة مفاضلة معمارية واقعية يمكن تقديمها في مقابلة تقنية (مثال: اختيار مكتبة حقن التبعيات):\n"
            "```markdown\n"
            "| المعيار / الأداة | Dagger / Hilt | Koin | Pure Manual DI |\n"
            "|---|---|---|---|\n"
            "| زمن التجميع (Build Time) | أبطأ بسبب KSP/APT وتوليد الكود | سريع جداً (بدون توليد كود) | الأسرع على الإطلاق |\n"
            "| الأمان وقت التجميع (Compile-time Safety) | تحقق كامل 100% من الرسم البياني | Runtime Crash إذا نسيت تعريف Module | تحقق 100% عبر مترجم Kotlin |\n"
            "| منحنى التعلم (Learning Curve) | حاد ومعقد للمبتدئين | سهل وبسيط جداً | بديهي ومباشر |\n"
            "| ملائمة المشاريع الكبيرة (Scale: 50+ devs) | الخيار القياسي المعياري | خطر كراشات خفية في الإنتاج | مجهود يدوي متكرر |\n"
            "```\n"
            "النموذج اللفظي في الإجابة:\n"
            "\"اخترنا Hilt رغم بطء وقت التجميع المبدئي لأن فريقنا يضم 30 مهندساً؛ والأولوية القصوى كانت منع كراشات الـ Missing Dependency أثناء إطلاق الـ Production، وقبلنا زيادة دقيقة واحدة في CI مقابل أمان تام.\""
        ),
        "quick_answer": "Explain architectural trade-offs by anchoring discussions in specific business and team constraints rather than dogmatic preferences. Outline candidate approaches, contrast what each choice buys you against what it costs (complexity, build time, memory), state your clear recommendation, and explain how you mitigate the chosen approach's weaknesses.",
        "best_answer": (
            "Senior engineers distinguish themselves by articulating engineering decisions as conscious trade-offs rather than absolute truths:\n\n"
            "1. **Anchor in Context and Business Constraints**:\n"
            "   - Frame the decision around concrete variables: team size and experience, delivery timelines, codebase modularity, app performance budgets, and long-term maintainability.\n\n"
            "2. **Comparative Multi-Option Evaluation**:\n"
            "   - Present at least two viable architectural paths. Explicitly state what each option optimizes for and what penalty it exacts. For instance: 'Modularizing into 40 dynamic-feature modules decouples feature squads and isolates build boundaries, but increases Gradle configuration overhead and dependency graph complexity.'\n\n"
            "3. **Justify the Decisive Choice**:\n"
            "   - Explain why the chosen trade-off aligns with organizational priorities. Demonstrate maturity by acknowledging the drawbacks of your choice and outlining mitigation tactics (e.g., configuring remote build caching to counteract multi-module build times).\n\n"
            "4. **Reversibility and Exit Gates**:\n"
            "   - Categorize whether the choice is a one-way door (irreversible database migration) or a two-way door (state management pattern behind an interface), demonstrating risk management."
        ),
        "deep_answer": (
            "From an engineering leadership and systems architecture perspective, evaluating trade-offs involves balancing immediate delivery against long-term operational costs:\n\n"
            "1. **The Cost of Abstraction (Indirection Debt)**: Juniors often over-engineer solutions with 5 layers of interfaces and Clean Architecture interactors for a simple static FAQ screen. A senior explains: 'Every layer of indirection introduces cognitive overhead, file count bloat, and navigation friction. We strictly enforce Clean Architecture boundaries on core transactional domains (payments, checkout), but permit lightweight pragmatic patterns on static presentation modules.'\n\n"
            "2. **Team Topology and Conway's Law**: Software architectures inevitably mirror team communication structures. Modularizing by feature (`:feature:checkout`, `:feature:catalog`) mirrors cross-functional squad ownership, reducing PR merge collisions, whereas modularizing by technical layer (`:data`, `:domain`, `:presentation`) forces 4 squads to touch the identical data module concurrently.\n\n"
            "3. **Pragmatic Compromise Over Dogmatism**: Articulate instances where you deliberately chose an imperfect architecture to hit a critical company milestone, accompanied by an explicit tech-debt repayment plan recorded in an Architecture Decision Record (ADR)."
        ),
        "follow_ups": [
            {
                "question": "What is the difference between a one-way door and a two-way door architectural decision?",
                "answer": "A one-way door decision is costly and almost irreversible (e.g. database engine choice), requiring deep analysis; a two-way door can be easily reverted or refactored (e.g. UI layout choice)."
            },
            {
                "question": "Why is modularizing by feature generally superior to modularizing by layer in large teams?",
                "answer": "Because it aligns with autonomous squad ownership, isolating PRs and minimizing cross-team merge conflicts and compilation bottlenecks."
            }
        ]
    },
    {
        "id": "LEAD-02",
        "arabic_explanation": (
            "كيف تدير عملية مراجعة الكود (Code Review) بشكل منهجي يغطي الصحة البرمجية (Correctness)، والأمان (Security)، وسهولة القراءة، وقابلية الاختبار؟\n\n"
            "1. فلسفة مراجعة الكود للـ Senior Engineer:\n"
            "   - مراجعة الكود ليست تصيداً للأخطاء الشخصية، بل هي **بوابة جودة هندسية (Quality Gate) وأداة لنشر المعرفة داخل الفريق**.\n   - **أتمتة ما يمكن أتمتته**: لا تضيع وقتك البشري في مراجعة المسافات والتنسيق؛ دع Spotless و ktlint و Detekt يرفضون الـ PR آلياً.\n\n"
            "2. المحاور الأربعة للمراجعة العميقة:\n"
            "   - **1. الصحة البرمجية ومنطق العمل (Correctness)**: هل الكود يلبي متطلبات الـ User Story؟ هل تم التعامل مع الحالات الحدية (Empty states, Network timeout, Screen rotation, Process Death)؟ هل هناك تسريبات ذاكرة أو Coroutine leaks؟\n   - **2. الأمان والخصوصية (Security)**: هل تم تشفير البيانات الحساسة؟ هل تم منع كشف الـ Tokens في الـ Logs؟ هل يوجد فحص لمدخلات الـ Deep Links؟ هل تم تعيين `android:exported=\"false\"` للمكونات غير العامة؟\n   - **3. سهولة القراءة والمعمارية (Readability & Architecture)**: هل الكود يتبع النمط المعتمد (MVI/MVVM)؟ هل التسميات تعبر عن نية الكود (Intent-revealing names)؟ هل تم احترام Single Responsibility Principle؟\n   - **4. قابلية الاختبار وجودة الفحص (Testability)**: هل الكود الجديد مغطى بـ Unit Tests حقيقية تفحص منطق العمل وليس مجرد رفع نسبة التغطية (Code Coverage) بسطور وهمية؟"
        ),
        "practical_walkthrough": (
            "قائمة مراجعة عملية (Code Review Checklist) ونموذج للتعليقات البناءة:\n"
            "```markdown\n"
            "### ❌ نموذج تعليق سيئ وغير بناء:\n"
            "\"This is wrong. Change it to Coroutines and fix your architecture.\"\n"
            "\n"
            "### ✅ نموذج تعليق Senior بناء وتعليمي:\n"
            "\"[Blocking - Correctness]: I noticed we're collecting this Flow directly inside `onCreate`:\n"
            "`viewModel.state.collect { ... }`\n"
            "On Android, if the app goes to the background, this coroutine continues emitting,\n"
            "which can trigger UI updates and waste battery or crash if accessing views.\n"
            "Could we wrap this in `repeatOnLifecycle(Lifecycle.State.STARTED)`?\n"
            "Here's the official Android guide for reference: [link]\"\n"
            "\n"
            "### مستويات تصنيف الملاحظات (Conventional Comments):\n"
            "- **[Blocking]**: خطأ منطقي، تسريب ذاكرة، ثغرة أمنية (يمنع الدمج).\n"
            "- **[Non-blocking / Suggestion]**: تحسين أداء طفيف أو إعادة صياغة بديلة.\n"
            "- **[Question]**: طلب توضيح حول قرار معين.\n"
            "- **[Nitpick]**: تفصيلة جمالية غير مؤثرة (لا تمنع الدمج إطلاقاً).\n"
            "- **[Praise]**: إشادة بحل هندسي ذكي ومكتوب باحترافية.\n"
            "```"
        ),
        "quick_answer": "Review code systematically by automating style and formatting via linters, focusing human review on business correctness, edge cases, memory leaks, security vulnerabilities, architectural alignment, and meaningful unit test coverage. Use conventional comment prefixes (Blocking, Non-blocking, Nitpick) to communicate intent constructively.",
        "best_answer": (
            "A structured code review process balances technical rigor with psychological safety and team velocity:\n\n"
            "1. **Automate Mechanical Checks**:\n"
            "   - Enforce formatting (Spotless/ktlint), static analysis (Detekt), and framework issues (Android Lint) in automated CI gates. Human reviewers should never spend time debating tab widths or unused imports.\n\n"
            "2. **Four-Pillar Review Rubric**:\n"
            "   - **Correctness**: Validate business logic fidelity, edge cases (empty states, process death, offline states), coroutine lifecycle safety (`repeatOnLifecycle`), and thread-safety.\n   - **Security**: Inspect sensitive data storage (EncryptedSharedPreferences), log sanitization (no PII in Logcat), secure component exports (`android:exported`), and deep-link payload validation.\n   - **Architecture & Maintainability**: Ensure separation of concerns, adherence to team architectural boundaries (Clean Architecture / MVI), and clear domain naming.\n   - **Testability**: Verify that new code introduces robust unit tests verifying behavior and edge cases rather than tautological mock assertions.\n\n"
            "3. **Empathetic and Actionable Feedback**:\n"
            "   - Use structured conventional prefixes: `[Blocking]`, `[Suggestion]`, `[Question]`, `[Nitpick]`. Provide clear technical rationale and links to official documentation rather than subjective directives."
        ),
        "deep_answer": (
            "From an engineering leadership and team velocity standpoint, code reviews require operational governance:\n\n"
            "1. **PR Size Caps and Review Latency SLA**: Research proves review thoroughness drops precipitously on PRs exceeding 400 lines of code. Enforce a team cultural limit: PRs should be small and atomic ($< 300$ lines). Establish an internal SLA where PRs are reviewed within 4 business hours to avoid blocking teammates.\n\n"
            "2. **Pairing on Complex Architecture**: When reviewing foundational changes (e.g. migrating authentication engines or introducing a new database schema), asynchronous GitHub comments are inefficient and lead to misunderstandings. Senior leads jump on a 15-minute synchronous pairing session to align on the mental model before final sign-off.\n\n"
            "3. **Fostering Codebase Collective Ownership**: Use reviews to mentor engineers and highlight great work with explicit `[Praise]` comments. Encourage junior engineers to review senior PRs; asking questions on unfamiliar patterns democratizes architectural knowledge across the squad."
        ),
        "follow_ups": [
            {
                "question": "Why should formatting and linting checks be completely removed from human code reviews?",
                "answer": "Because automated CI linters execute them instantaneously and objectively, freeing human reviewers to focus on architectural correctness and security."
            },
            {
                "question": "What is the benefit of using prefixes like `[Blocking]` and `[Nitpick]` in review comments?",
                "answer": "It provides unambiguous clarity to the PR author on which comments require resolution before merge versus which are purely optional suggestions."
            }
        ]
    },
    {
        "id": "LEAD-03",
        "arabic_explanation": (
            "ما هو الدين التقني (Technical Debt)، وكيف تقنع مدراء المنتج (Product Managers) بتخصيص وقت لسداده وترتيب أولوياته؟\n\n"
            "1. ما هو الدين التقني؟\n"
            "   - هو تكلفة الترقيعات والاختصارات الهندسية السريعة التي تم اتخاذها في الماضي لتسليم ميزة بسرعة للعملاء.\n   - مثل القرض المالي: إذا لم تسدد أصل القرض، ستتراكم عليك **الفوائد (Interest)** في صورة: بطء إضافة ميزات جديدة، وتكرار الأعطال في الإنتاج، وبطء وقت البناء، وإحباط المهندسين واستقالتهم.\n\n"
            "2. ترجمة الدين التقني للغة الأعمال (Translating Tech Debt to Business Impact):\n"
            "   - مدير المنتج لا يهتم إذا قلت: \"الكود ليس Clean ونريد إعادة كتابته بـ MVI!\".\n   - **تحدث بلغة الأرقام ومؤشرات الأعمال (Business Metrics)**:\n     * بدلاً من \"الكود فوضوي\": \"كل ميزة جديدة في شاشة الدفع تستغرق 3 أسابيع بدلاً من 4 أيام بسبب تشابك الكود القديم (خسارة سرعة بنسبة 70%)\".\n     * بدلاً من \"نريد ترقية Gradle\": \"بناء التطبيق في الـ CI يستغرق 40 دقيقة، مما يهدر 150 ساعة شهرياً من وقت الفريق (تكلفة رواتب مهدرة)\".\n     * بدلاً من \"نريد إصلاح الـ Memory Leaks\": \"معدل الـ Crash-free انخفض إلى 98.8% مما يعرض التطبيق لعقوبات Google Play Vitals وفقدان عملاء جدد\".\n\n"
            "3. استراتيجيات إدارة وسداد الدين التقني:\n   - **قاعدة الكشافة (The Boy Scout Rule)**: \"اترك الكود أنظف قليلاً مما وجدته\" في كل PR.\n   - **مخصص الـ 20% (The 20% Tech Debt Budget)**: الاتفاق مع إدارة المنتج على تخصيص 20% من سعة كل Sprint لسداد الديون التقنية والبنية التحتية، مقابل 80% للميزات الجديدة."
        ),
        "practical_walkthrough": (
            "مصفوفة ترتيب أولويات الدين التقني (Tech Debt Prioritization Matrix):\n"
            "```markdown\n"
            "| نوع الدين التقني | التأثير التجاري / الأمني | تكرار الحدوث | التكلفة والجهد | الأولوية (Priority) |\n"
            "|---|---|---|---|---|\n"
            "| تسريب ذاكرة يسبب كراش OOM في شاشة الشراء | مباشر: خسارة مبيعات فورية | عالي (3% من المستخدمين) | يومان عمل | **P0 (فوري)** |\n"
            "| مكتبة أمان قديمة معلنة كثغرة CVE | خطر اختراق وسحب من المتجر | محتمل | 3 أيام عمل | **P1 (عاجل)** |\n"
            "| شاشة قديمة مكتوبة بـ XML معقد | بطء تطوير الميزات الجديدة | متوسط | أسبوع عمل | **P2 (مجدول في سبرنت)** |\n"
            "| عدم توحيد أسماء الألوان في styles.xml | جمالي وتنظيمي فقط | منخفض | يوم عمل | **P3 (عند التفرغ)** |\n"
            "```\n"
            "صياغة اتفاقية Sprint مع الـ Product Manager:\n"
            "\"إذا استثمرنا 3 أيام في هذا الـ Sprint لفصل CheckoutViewModel القديم، سنخفض زمن تسليم ميزة Apple Pay و Google Pay القادمة من شهر إلى أسبوع واحد فقط.\""
        ),
        "quick_answer": "Technical debt is the accrued engineering cost of past shortcuts that compounds interest in slower velocity and higher defect rates. Prioritize it by quantifying its business impact (lost revenue from crashes, developer hours wasted on slow CI, sprint velocity drops) and negotiate a standing 20% sprint capacity allocation dedicated to ongoing remediation.",
        "best_answer": (
            "Managing technical debt requires framing engineering hygiene in terms of business velocity and risk mitigation:\n\n"
            "1. **Translate Technical Problems to Business Metrics**:\n"
            "   - Product Managers do not prioritize abstract purity. Translate debt into business impact:\n     - 'Refactoring the payment module' becomes: 'Our checkout failure rate is 2.4% due to legacy state race conditions, directly losing \\$40,000 monthly in gross merchandise value.'\n     - 'Updating Gradle build scripts' becomes: 'CI takes 45 minutes per PR, delaying release cycles and wasting 20 engineering hours weekly.'\n\n"
            "2. **Categorize and Prioritize Debt**:\n"
            "   - Evaluate debt using an Impact vs. Effort matrix:\n     - **High Impact, Low Effort (Quick Wins)**: Immediate priority.\n     - **High Impact, High Effort (Strategic Refactors)**: Requires dedicated architectural epics.\n     - **Low Impact, Low Effort**: Resolved organically via Boy Scout rule.\n     - **Low Impact, High Effort**: Explicitly ignored or deprioritized.\n\n"
            "3. **Establish a Standing Capacity Agreement**:\n"
            "   - Negotiate a fixed 80/20 capacity split with product leadership: 80% dedicated to product feature delivery, 20% strictly allocated to architectural health, tooling, dependency upgrades, and test coverage."
        ),
        "deep_answer": (
            "From an engineering leadership and organizational health standpoint, distinguishing debt types prevents toxic cycles:\n\n"
            "1. **Prudent vs. Reckless Debt (Martin Fowler's Debt Quadrant)**:\n"
            "   - Not all tech debt is bad. **Prudent deliberate debt** (taking a known shortcut to hit a regulatory launch date with an immediate plan to refactor) is a valid business tool. **Reckless inadvertent debt** (sloppy code produced by lack of design standards or testing) poisons the codebase. Leaders celebrate prudent trade-offs while ruthlessly eliminating reckless practices.\n\n"
            "2. **The Refactor-Rewrite Fallacy**: A classic junior mistake is requesting a complete ground-up app rewrite ('Let's throw away the legacy app and rewrite it in Compose!'). Rewrites take 3x longer than estimated, halt product delivery, and re-introduce obscure bugs that the legacy app solved over 5 years. Senior leaders advocate for incremental in-place strangler-fig pattern refactorings.\n\n"
            "3. **Visualizing Debt in Sprint Boards**: Tag debt items explicitly with a `tech-debt` label in Jira/Linear and track cycle times. If the ratio of bugs to features climbs above 30%, freeze feature development for a stabilization sprint."
        ),
        "follow_ups": [
            {
                "question": "Why is the Strangler Fig pattern preferred over a full ground-up app rewrite?",
                "answer": "Because it incrementally replaces legacy components one by one behind interfaces, allowing continuous product delivery without the extreme risk of a monolithic rewrite."
            },
            {
                "question": "What is the 'Boy Scout Rule' in software engineering?",
                "answer": "Always leave the code you touch a little cleaner than you found it, gradually paying down technical debt during routine feature work."
            }
        ]
    },
    {
        "id": "LEAD-04",
        "arabic_explanation": (
            "كيف تقوم بتقدير وقت ميزة غير مألوفة (Unfamiliar Feature) وتوصيل المخاطر بوضوح لإدارة المشروع؟\n\n"
            "1. التحدي في الميزات غير المألوفة:\n"
            "   - عندما يُطلب منك تقدير ميزة تعتمد على تكنولوجيا جديدة لم تستخدمها من قبل (مثل: Bluetooth Low Energy، أو إضافة Biometric Crypto جديدة، أو مكتبة C++ NDK خارجية).\n   - التقدير السريع المتسرع (\"أسبوعان!\") هو فخ هندسي يدمر مصداقيتك عندما تظهر مشاكل غير متوقعة في الـ Hardware.\n\n"
            "2. استراتيجية التقدير الاحترافية (Estimation Methodology):\n   - **1. الفصل بين البحث والتنفيذ (Spike / Timeboxed Exploration)**:\n     * اطلب تخصيص **Spike** لمدة يومين أو 3 أيام بهدف واحد: عمل Prototype سريع يختبر إمكانية الاتصال والـ APIs وإثبات المفهوم (Proof of Concept).\n     * بعد انتهاء الـ Spike فقط، يمكنك تقديم تقدير زمني دقيق للميزة الحقيقية.\n   - **2. التفكيك لعناصر ذرية (WBS - Work Breakdown Structure)**:\n     * تقسيم الميزة إلى مهام صغيرة: واجهة المستخدم (UI)، طبقة البيانات والـ Network، معالجة الـ Edge cases، كتابة الاختبارات، واختبارات الـ QA.\n   - **3. التقدير ثلاثي النقاط (Three-Point Estimation)**:\n     * حساب: التقدير المتفائل (Optimistic $O$)، التقدير الأكثر احتمالاً (Most Likely $M$)، والتقدير المتشائم عند حدوث مشاكل (Pessimistic $P$).\n     * المتوسط المتوقع: $E = \\frac{O + 4M + P}{6}$.\n\n"
            "3. توصيل المخاطر للإدارة:\n   - توضيح الاعتماديات الخارجية (External Blockers): مثل اعتماد الميزة على جاهزية سيرفرات الـ Backend، أو سلوك الـ Bluetooth المختلف بين هواتف Samsung و Xiaomi."
        ),
        "practical_walkthrough": (
            "نموذج خطة Spike وتقدير شفاف لميزة BLE غير مألوفة:\n"
            "```markdown\n"
            "### مقترح إدارة المخاطر لميزة Bluetooth IoT Sync:\n"
            "\n"
            "#### المرحلة 1: Timeboxed Technical Spike (3 أيام عمل)\n"
            "- **الهدف**: اختبار الاتصال بالعتاد (BLE GATT Services) على أجهزة Android 12-14.\n"
            "- **المخرجات**: تقرير جدوى فني + اكتشاف القيود النظامية + إزالة الغموض بنسبة 80%.\n"
            "\n"
            "#### المرحلة 2: تفكيك التقدير (بناءً على نتائج الـ Spike):\n"
            "- تصميم واجهات الـ Compose وحالات الأخطاء: 3 أيام.\n"
            "- خدمة الاتصال الخلفية وربط Coroutines بالـ BLE callbacks: 5 أيام.\n"
            "- التعامل مع القيود الخاصة بالمصنعين (OEM background kills & permissions): 4 أيام.\n"
            "- اختبارات الوحدة والـ Integration Tests: 3 أيام.\n"
            "\n"
            "#### مصفوفة المخاطر المعلنة (Identified Risks):\n"
            "1. **[مخاطرة عالية]**: تأخر توفير جهاز الهاردوير التجريبي (Hardware Sample) سيعطل الـ QA.\n"
            "2. **[مخاطرة متوسطة]**: قيود توفير الطاقة في هواتف Xiaomi قد توقف الفحص بالخلفية.\n"
            "```"
        ),
        "quick_answer": "Estimate unfamiliar features by separating discovery from delivery using a timeboxed technical spike (2–3 days) to build a prototype and de-risk core unknowns. Break the remaining work into small tasks, provide three-point ranges (best, likely, worst case), and transparently communicate external hardware, backend, and OEM dependencies.",
        "best_answer": (
            "Estimating novel or high-uncertainty mobile features requires disciplined risk engineering rather than speculative guessing:\n\n"
            "1. **The Timeboxed Technical Spike Protocol**:\n"
            "   - When facing unfamiliar domain territory (e.g. BLE, custom NDK audio, complex biometrics), refuse to provide a full release estimate immediately. Instead, scope a 2-to-3-day timeboxed 'Spike'. The sole objective of the spike is building a disposable proof-of-concept to validate framework APIs, verify hardware compatibility, and uncover hidden constraints.\n\n"
            "2. **Granular Work Breakdown (WBS)**:\n"
            "   - Following the spike, decompose the epic into discrete sub-tasks: domain models, background services, UI presentation states, offline error recovery, automated tests, and regression testing.\n\n"
            "3. **Three-Point Probabilistic Estimation (PERT)**:\n"
            "   - Present estimates as ranges rather than single integers:\n     - Optimistic ($O$): Everything works smoothly without device anomalies.\n     - Nominal ($M$): Expected delivery with standard iteration.\n     - Pessimistic ($P$): Vendor bugs, OEM permission hurdles, and store review delays.\n     - Expected duration: $E = \\frac{O + 4M + P}{6}$.\n\n"
            "4. **Explicit Risk & Dependency Transparency**:\n"
            "   - Clearly enumerate external blockers: backend API delivery dates, physical test hardware availability, and third-party vendor SDK support."
        ),
        "deep_answer": (
            "From an engineering leadership and stakeholder communication perspective, managing expectations prevents project crises:\n\n"
            "1. **The Cone of Uncertainty**: Communicate the 'Cone of Uncertainty' to product and executive stakeholders. Early in the discovery phase, estimates carry a $4\\times$ variance. As the spike concludes and architecture solidifies, variance drops to $1.2\\times$. Explaining this mathematically protects team credibility.\n\n"
            "2. **Mobile-Specific Hardware Fragmentation Variance**: Mobile estimates carry unique risks that backend projects do not: vendor-specific battery managers (e.g. Samsung vs. Xiaomi killing background workers), camera driver discrepancies, and Play Store policy scrutiny. Factor an explicit 'Device Matrix Testing' buffer into unfamiliar hardware features.\n\n"
            "3. **Descoping Strategy (MVP vs. Full Scope)**:\n"
            "   - Always present a staged delivery path: 'If the deadline is non-negotiable for an upcoming trade show, we can deliver the MVP (foreground sync only) in 2 weeks with minimal risk, and schedule automated background syncing for the subsequent release.'"
        ),
        "follow_ups": [
            {
                "question": "What is the primary deliverable of an engineering spike?",
                "answer": "A throwaway proof-of-concept that answers specific architectural unknowns and allows accurate delivery estimation, not production code."
            },
            {
                "question": "Why should mobile estimates factor in device fragmentation buffers?",
                "answer": "Because proprietary OEM battery optimizations, hardware differences, and OS versions introduce device-specific edge cases not visible on emulators."
            }
        ]
    },
    {
        "id": "LEAD-05",
        "arabic_explanation": (
            "كيف تقوم بتوجيه المطورين المبتدئين (Mentoring Juniors) ورفع المستوى الهندسي العام للفريق (Engineering Excellence)؟\n\n"
            "1. دور الـ Senior الحقيقي:\n"
            "   - الـ Senior لا يُقاس بعدد أسطر الكود التي يكتبها بمفرده، بل بـ **مضاعفة إنتاجية وقدرات زملائه في الفريق (Force Multiplier)**.\n   - إعطاء الحل المباشر للمبتدئ يجعله معتمداً عليك دائماً؛ التوجيه الحقيقي يعلمه **كيف يفكر كمهندس، وكيف يقرأ الـ Stacktrace، وكيف يختبر افتراضاته بنفسه**.\n\n"
            "2. استراتيجيات التوجيه الفردي (Mentorship Tactics):\n   - **1. البرمجة الثنائية الموجهة (Pair Programming with Driver/Navigator)**: المبتدئ هو من يكتب الكود على لوحة المفاتيح (Driver)، بينما الـ Senior يوجه ويسأل أسئلة تحفيزية (Navigator).\n   - **2. جلسات 1:1 منتظمة مع خطة نمو واضحة**: مراجعة التحديات التي تواجهه، واقتراح كتب أو مقالات أو أجزاء من الكود لدراستها وتطبيقها.\n   - **3. تشجيع الاستكشاف في بيئة آمنة**: السماح له بارتكاب أخطاء في الـ PR وتوجيهه لاكتشافها عبر الاختبارات دون إحراج.\n\n"
            "3. رفع المستوى الهندسي للفريق ككل (Team Excellence):\n   - **ورش عمل داخلية (Tech Talks / Lunch & Learns)**: مشاركة أحدث الأدوات (مثل Compose Performance, Baseline Profiles).\n   - **توثيق المعمارية وقرارات التصميم (ADRs & Guidelines)**: كتابة وثائق واضحة في الـ Wiki حتى لا تظل المعرفة حكراً على شخص واحد (Eliminating the Bus Factor).\n   - **توحيد معايير الـ PRs**: إعداد قوالب للـ PR تفرض كتابة خطوات الاختبار وإرفاق صور للـ UI."
        ),
        "practical_walkthrough": (
            "إطار عمل لجلسة توجيه عملية (Mentoring Framework) ونموذج الـ Socratic Method:\n"
            "```markdown\n"
            "### سيناريو توجيه واقعي:\n"
            "المبتدئ: \"الـ App بيكراش في الشاشة دي ومش عارف ليه، ممكن تساعدني أصلحه؟\"\n"
            "\n"
            "❌ رد خاطئ من Senior متعالٍ:\n"
            "\"أنت ناسي تحط nullable check في السطر ده، حط ?.let وهيشتغل.\"\n"
            "\n"
            "✅ الرد الاحترافي التوجيهي (Socratic Method):\n"
            "الـ Senior: \"تعال نبص سوا على الـ Logcat. افتح الـ Stacktrace... إيه أول سطر مكتوب فيه كود يخص مشروعنا؟\"\n"
            "المبتدئ: \"السطر 42 في ProfileViewModel.\"\n"
            "الـ Senior: \"ممتاز! نوع الـ Exception إيه؟\"\n"
            "المبتدئ: \"NullPointerException على user.email.\"\n"
            "الـ Senior: \"عظيم، تفتكر ليه user.email ممكن يرجع null من السيرفر في الحالة دي؟ وإزاي نخلي الـ ViewModel يعالج الحالة دي بأمان في الـ Unit Test قبل ما نعدل الكود؟\"\n"
            "```\n"
            "النتيجة: تعلم المبتدئ كيفية قراءة الـ Logcat، واستنتاج السبب الجذري، وكتابة اختبار لمنع تكرار الخطأ."
        ),
        "quick_answer": "Mentor junior engineers by acting as a force multiplier: use the Socratic method to guide problem-solving rather than handing out answers, pair-program with juniors at the keyboard, and provide safe psychological environments for learning. Elevate team practice through internal tech talks, architectural documentation (ADRs), and clear engineering standards.",
        "best_answer": (
            "Technical mentorship is the primary metric distinguishing senior engineers from individual contributors:\n\n"
            "1. **Socratic Guidance Over Handing Out Solutions**:\n"
            "   - When a junior encounters a blocker, resist writing the code for them. Use Socratic questioning to walk them through debugging: inspecting Logcat, setting conditional breakpoints, analyzing coroutine stack traces, and forming hypotheses. This builds independent problem-solving capability.\n\n"
            "2. **Pair Programming Dynamics**:\n"
            "   - Practice Driver-Navigator pairing where the junior developer holds the keyboard ('Driver') while the senior navigates high-level design and tests ('Navigator'). This forces active cognitive participation.\n\n"
            "3. **Structured Growth and Psychological Safety**:\n"
            "   - Establish regular 1-on-1 engineering check-ins. Assign stretch tasks calibrated slightly above their current capability, paired with an explicit safety net of prompt, empathetic PR reviews.\n\n"
            "4. **Systemic Team-Level Elevation**:\n"
            "   - Codify tribal knowledge into written Architecture Decision Records (ADRs) and onboarding wikis to lower the Bus Factor. Host monthly internal lightning talks covering emerging Android practices (Baseline Profiles, Compose stability, KMP)."
        ),
        "deep_answer": (
            "From an organizational health and team culture perspective, leadership creates high-trust environments:\n\n"
            "1. **Normalizing Vulnerability and Mistakes**: Senior leaders build psychological safety by openly discussing their own past production mistakes and refactoring missteps. When a junior sees a staff engineer say 'I was wrong about that architecture approach, let's pivot', it eliminates imposter syndrome and encourages transparency.\n\n"
            "2. **Delegating Architectural Ownership**: The ultimate test of mentorship is delegation. Identify promising mid-level engineers and assign them ownership of an entire technical epic (e.g. migrating SharedPreferences to Jetpack DataStore), coaching them from behind the scenes on writing the RFC and coordinating with stakeholders.\n\n"
            "3. **Establishing Objective Career Ladders**: Partner with engineering management to map clear competencies (Junior -> Mid -> Senior). Ensure mentees understand what behaviors (code quality, communication, system design, initiative) are required for their next career milestone."
        ),
        "follow_ups": [
            {
                "question": "Why is the junior holding the keyboard during pair programming more effective?",
                "answer": "Because it forces active muscle memory and cognitive engagement, preventing passive watching and accelerating learning."
            },
            {
                "question": "What is the 'Bus Factor' and how does technical documentation mitigate it?",
                "answer": "The minimum number of engineers that can abruptly leave the team before a project stalls; documentation distributes knowledge so projects survive departures."
            }
        ]
    },
    {
        "id": "LEAD-06",
        "arabic_explanation": (
            "كيف تكتب وثيقة مقترح معماري (RFC - Request for Comments) أو سجل قرار معماري (ADR - Architecture Decision Record) لتغيير جذري في النظام؟\n\n"
            "1. ما هو الفرق بين RFC و ADR؟\n"
            "   - **RFC (Request for Comments)**: وثيقة **استكشافية ونقاشية مفتوحة** تُطرح قبل اتخاذ القرار لجمع آراء واعتراضات واقتراحات الفريق حول مشكلة كبيرة (مثل: \"مقترح الانتقال من Groovy إلى Kotlin DSL و Version Catalogs\").\n   - **ADR (Architecture Decision Record)**: وثيقة **قصيرة وتوثيقية نهائية** تلخص القرار الذي تم الاستقرار عليه وتاريخه وسياقه والبدائل المرفوضة والآثار المترتبة عليه، وتُحفظ داخل مستودع الكود (`docs/adr/`).\n\n"
            "2. الهيكل القياسي لوثيقة الـ RFC/ADR:\n   - **1. العنوان والحالة (Title & Status)**: مثل `ADR-004: Migrate Image Loading to Coil` (الحالة: Proposed, Accepted, Superceded).\n   - **2. السياق والمشكلة (Context & Problem Statement)**: لماذا نحتاج لهذا التغيير الآن؟ ما هي نقاط الألم في الوضع الحالي؟\n   - **3. القرار المقترح (Decision / Proposal)**: الحل الهندسي المختار بالتفصيل.\n   - **4. البدائل المدروسة ولماذا تم رفضها (Considered Alternatives)**: مقارنة الخيارات الأخرى (مثلاً مقارنة Coil بـ Glide و Fresco).\n   - **5. العواقب والمخاطر والآثار الجانبية (Consequences)**: التأثير على حجم الـ APK، وسرعة البناء، وتكلفة تدريب الفريق.\n   - **6. خطة الترحيل المرحلية (Rollout & Migration Plan)**: كيفية الانتقال خطوة بخطوة دون تعطيل الإنتاج."
        ),
        "practical_walkthrough": (
            "قالب حقيقي لوثيقة ADR مصممة لمشروع أندرويد:\n"
            "```markdown\n"
            "# ADR-012: Adoption of Jetpack DataStore over SharedPreferences\n"
            "\n"
            "## Status: Accepted\n"
            "Date: 2026-03-15 | Author: Mohamed Mahmoud | Approvers: Mobile Core Squad\n"
            "\n"
            "## Context\n"
            "`SharedPreferences` causes ANRs on the Main Thread during synchronous `apply()`\n"
            "and `commit()` disk flushes, and lacks transactional type-safety and reactive\n"
            "Flow support for real-time preference updates.\n"
            "\n"
            "## Decision\n"
            "We will adopt `Proto DataStore` backed by Kotlin Serialization and Coroutines Flow\n"
            "as the standard key-value and typed configuration storage for the application.\n"
            "\n"
            "## Consequences\n"
            "### Positive:\n"
            "- Asynchronous, non-blocking disk I/O on `Dispatchers.IO` eliminates main-thread ANRs.\n"
            "- Native Kotlin `Flow` integration simplifies reactive state in ViewModels.\n"
            "- Proto schemas provide compile-time type safety.\n"
            "\n"
            "### Negative / Trade-offs:\n"
            "- Requires writing Protobuf schema files (`.proto`).\n"
            "- Adds ~40KB to compiled APK size.\n"
            "\n"
            "## Migration Plan\n"
            "1. Implement `SharedPreferencesMigration` utility to transfer user data automatically on first launch.\n"
            "2. Deprecate `LegacyPrefsManager` with a Lint warning.\n"
            "3. Migrate feature modules incrementally over the next 2 sprints.\n"
            "```"
        ),
        "quick_answer": "An RFC gathers collaborative team feedback on major architectural proposals before commitment, while an ADR records the accepted decision, rationale, context, rejected alternatives, and consequences within the repository. A strong document clearly defines the problem, contrasts alternatives, states trade-offs, and details an incremental migration plan.",
        "best_answer": (
            "RFCs and ADRs establish institutional memory and collaborative alignment for significant engineering changes:\n\n"
            "1. **RFC vs. ADR Distinction**:\n"
            "   - **RFC (Request for Comments)**: A collaborative exploration document published early in the ideation cycle to solicit feedback, unearth blind spots, and align cross-functional stakeholders on complex architectural shifts.\n   - **ADR (Architecture Decision Record)**: An immutable, version-controlled historical record stored directly in the repository (`/docs/adr/ADR-005.md`) capturing what was decided, why, and what trade-offs were accepted.\n\n"
            "2. **Essential Architectural Document Sections**:\n"
            "   - **Status & Metadata**: (Proposed, Accepted, Deprecated, Superceded) with author and approver timestamps.\n   - **Context & Problem Statement**: Explicit business and technical motivations driving the change.\n   - **The Decision**: Crisp specification of the chosen architectural pattern, library, or protocol.\n   - **Considered Alternatives**: Rigorous comparison table explaining why alternative options were rejected.\n   - **Consequences (Positive and Negative)**: Honest accounting of benefits alongside accepted trade-offs (e.g. build time penalties, learning curves).\n   - **Staged Migration Plan**: Incremental rollout strategy avoiding big-bang migrations."
        ),
        "deep_answer": (
            "From an engineering governance and consensus building angle, leading an RFC requires stakeholder empathy:\n\n"
            "1. **The Pre-RFC Socialization Phase**: Never publish a massive 15-page RFC as a surprise to the team. Socialize the core thesis with key senior influencers, platform leads, and QA directors through casual 1-on-1 discussions first. Addressing core anxieties in advance guarantees a constructive, calm public RFC review.\n\n"
            "2. **Timeboxing the RFC Lifecycle**: Open-ended architectural debates cause analysis paralysis. Set an explicit deadline (e.g. 10 business days for comments). At the deadline, the technical lead synthesizes feedback, resolves remaining dissenting opinions with a documented rationale, and transitions the RFC into an accepted ADR.\n\n"
            "3. **Living ADR Hygiene**: When architectural paradigms evolve (e.g. replacing RxJava with Kotlin Coroutines), do not edit the historical ADR to rewrite the past. Author a new ADR (`ADR-024`) that formally references and **supercedes** the old record (`ADR-003: Supercedes ADR-001`), maintaining an authentic genealogical record of codebase evolution."
        ),
        "follow_ups": [
            {
                "question": "Why should you never edit an existing accepted ADR when technology changes years later?",
                "answer": "Because an ADR is an immutable historical record of why a choice was made under past constraints; new choices must be recorded in a new ADR that explicitly supercedes the old one."
            },
            {
                "question": "What is the danger of not timeboxing an RFC discussion?",
                "answer": "The team enters analysis paralysis, endlessly debating theoretical trade-offs without committing to execution."
            }
        ]
    },
    {
        "id": "LEAD-07",
        "arabic_explanation": (
            "كيف تقوم بمواءمة وتنسيق العمل بين فرق الموبايل، والـ Backend، والـ QA، والأمان على عقد الـ API (API Contract) قبل كتابة الكود؟\n\n"
            "1. معضلة التطوير التقليدي المنعزل (Siloed Development):\n"
            "   - يكتب فريق الـ Backend الـ API على هواه بناءً على هيكل قاعدة البيانات (Data-centric).\n   - بعد أسبوعين يتسلمه مهندس الموبايل ليكتشف أن الـ API يتطلب 5 استدعاءات متتالية لعرض شاشة واحدة، وأن حقول الـ Nullability غير واضحة، وأن استجابة الـ JSON ضخمة وتستهلك باقات المستخدمين!\n   - النتيجة: إعادة كتابة الكود، وتأخر الإطلاق، وتبادل اللوم.\n\n"
            "2. منهجية الـ API-First / Contract-Driven Development:\n   - **1. الاجتماع المبكر لصياغة العقد (Contract Workshop)**: اجتماع مصغر يجمع مهندس الموبايل، ومهندس الـ Backend، وممثل الـ QA، ومهندس الأمان قبل كتابة سطر كود واحد.\n   - **2. توثيق العقد بصيغة قياسية موحدة (OpenAPI / Swagger / Protocol Buffers)**:\n     * تحديد أسماء الحقول بدقة، وأنواع البيانات، والـ Nullability الصريحة (هل الحقل قد يرجع `null`؟).\n     * تحديد رموز الأخطاء (HTTP Status Codes) وهيكل كائن الخطأ الموحد (`ErrorCode`, `UserMessage`, `Retryable`).\n   - **3. تصميم الـ API لتلبية تجربة المستخدم (UI-Driven API Design)**:\n     * تطبيق نمط **Backend For Frontend (BFF)** أو نقاط نهاية مخصصة تجمع البيانات لشاشة الموبايل في طلب واحد لتقليل استهلاك البطارية والشبكة.\n   - **4. فك ارتباط التطوير عبر الـ Mock Servers**:\n     * بمجرد اعتماد ملف الـ OpenAPI، يقوم فريق الموبايل والـ QA بتوليد **Mock Server** (عبر Prism أو Postman أو MockWebServer).\n     * يبدأ مهندس الموبايل في كتابة الواجهة واختبارها فوراً بالتوازي مع قيام الـ Backend ببناء الـ Services الحقيقية."
        ),
        "practical_walkthrough": (
            "نموذج عقد API قياسي متفق عليه بصيغة OpenAPI ومخطط استجابة أخطاء موحد:\n"
            "```yaml\n"
            "# openapi-contract.yaml\n"
            "paths:\n"
            "  /v1/checkout/summary:\n"
            "    get:\n"
            "      summary: Retrieve checkout summary for mobile\n"
            "      responses:\n"
            "        '200':\n"
            "          content:\n"
            "            application/json:\n"
            "              schema:\n"
            "                type: object\n"
            "                required: [order_id, total_amount, currency, items]\n"
            "                properties:\n"
            "                  order_id: { type: string, example: \"ord_9876\" }\n"
            "                  total_amount: { type: string, example: \"149.99\" } # String لتفادي مشاكل تقريب Float\n"
            "                  discount_applied: { type: boolean }\n"
            "                  promo_code: { type: string, nullable: true } # Nullable صريح لمنع NPE\n"
            "        '422':\n"
            "          description: Business validation error\n"
            "          content:\n"
            "            application/json:\n"
            "              schema:\n"
            "                type: object\n"
            "                required: [error_code, message, is_retryable]\n"
            "                properties:\n"
            "                  error_code: { type: string, example: \"ERR_INSUFFICIENT_STOCK\" }\n"
            "                  message: { type: string, example: \"Item out of stock\" }\n"
            "                  is_retryable: { type: boolean, example: false }\n"
            "```"
        ),
        "quick_answer": "Align cross-functional teams using Contract-First API Design: co-author the specification (OpenAPI/Protobuf) collaboratively before implementation, explicitly defining nullability, error payload schemas, and pagination. Spin up mock servers from the contract so mobile, QA, and backend build and test concurrently without blocking.",
        "best_answer": (
            "Cross-functional API contract alignment requires adopting a Contract-First / API-First methodology:\n\n"
            "1. **Collaborative Contract Co-Design**:\n"
            "   - Convene a short alignment workshop with Mobile, Backend, QA, and Security leads. Design endpoints around mobile UI consumption patterns (minimizing roundtrips) rather than raw database relational schemas.\n\n"
            "2. **Rigorous OpenAPI / Protobuf Specification**:\n"
            "   - Formulate the contract using OpenAPI (Swagger) or Protocol Buffers. Explicitly codify:\n     - **Nullability and Optionality**: Prevent Kotlin `NullPointerException` crashes by strictly documenting whether fields can be null.\n     - **Numeric Precision**: Transmit monetary values as Strings or integer cents to avoid floating-point inaccuracies.\n     - **Standardized Error Schemas**: Define a unified error envelope containing `error_code`, localized user message, and a boolean `is_retryable` flag.\n\n"
            "3. **Parallel Execution via Contract Mocking**:\n"
            "   - Export the verified spec into mock servers (MockWebServer, WireMock, or Prism). Mobile engineers develop and test against realistic mock payloads, and QA authors test matrices in parallel while backend engineers build database pipelines."
        ),
        "deep_answer": (
            "From an API governance and backward compatibility angle, contracts must enforce long-term survivability:\n\n"
            "1. **The Asymmetry of Mobile Version Lifecycles**: A backend API can be updated in a single deployment, but legacy mobile app versions linger in production for years because users disable auto-updates. The contract must mandate **strict backward compatibility**: fields can be added, but existing fields must never be renamed, deleted, or have their types altered without incrementing the API path version (`/v2/`).\n\n"
            "2. **Security & Data Minimization Auditing**: Security and compliance teams must audit the API contract against GDPR/CCPA regulations. Mobile payloads must never leak excessive PII or backend server details (e.g. leaking raw SQL stack traces in 500 error responses).\n\n"
            "3. **Automated Contract Testing (Pact / Consumer-Driven Contracts)**: Modern engineering teams integrate Consumer-Driven Contract testing (such as Pact). Mobile test suites define contract expectations; if a backend engineer modifies a response field on a PR, the backend CI build breaks automatically before the breaking change reaches staging."
        ),
        "follow_ups": [
            {
                "question": "Why is backward compatibility far more critical for mobile APIs than web frontend APIs?",
                "answer": "Because users run old app versions indefinitely without updating, whereas web users receive the newest JavaScript bundle upon page refresh."
            },
            {
                "question": "Why should monetary amounts never be transmitted as standard Float or Double in API JSON responses?",
                "answer": "Because binary floating-point representation causes precision loss and rounding errors; amounts should be passed as fixed strings or integer cents."
            }
        ]
    },
    {
        "id": "LEAD-08",
        "arabic_explanation": (
            "ما هي المقاييس الدقيقة (Metrics) التي تثبت نجاح عملية إعادة الهيكلة الكبيرة (Refactoring) وتبرر الاستثمار فيها للإدارة؟\n\n"
            "1. خطأ قياس النجاح بالانطباعات الشخصية:\n"
            "   - لا يمكنك الذهاب لمدير الهندسة وقول: \"الكود أصبح أجمل وأشعر بالراحة!\".\n   - النجاح الهندسي الحقيقي يجب أن يكون **قابلاً للقياس الكمي (Quantifiable)** بأرقام ومؤشرات واضحة وملموسة قبل وبعد عملية الـ Refactoring.\n\n"
            "2. المقاييس الأربعة الأساسية لتقييم الـ Refactor:\n   - **1. مقاييس الجودة والاستقرار (Quality & Stability)**:\n     * **معدل المستخدمين الخالين من الكراش (Crash-Free User Rate)**: الارتفاع من 99.1% إلى 99.95%.\n     * **معدل الانحدار والأخطاء (Regression Bug Rate)**: انخفاض تذاكر الأخطاء المرتبطة بالموديول المعاد هيكلته بنسبة 70% في أول شهرين.\n   - **2. مقاييس سرعة وتدفق الفريق (Engineering Velocity)**:\n     * **زمن تسليم الميزات (Lead Time for Changes)**: انخفاض وقت بناء ميزة جديدة في هذا الموديول من 3 أسابيع إلى 4 أيام.\n     * **معدل تعارض الفروع (Merge Conflict Frequency)**: انخفاض التعارضات بفضل تجزئة الكلاسات العملاقة إلى مكونات صغيرة وموديولات مستقلة.\n   - **3. مقاييس أداء النظام والتجميع (Performance & Build Time)**:\n     * **زمن بناء الـ CI والتجميع المحلي**: انخفاض زمن تجميع Gradle بنسبة 35% بفضل الـ Modularity واستغلال الـ Build Cache.\n     * **زمن بدء تشغيل التطبيق (App Startup Time) ومعدل الإطارات (FPS)**: انخفاض زمن التشغيل البارد بمقدار 400ms بفضل إزالة التهيئة المتزامنة على الـ Main Thread.\n   - **4. مقاييس جودة الكود والفحص (Testability)**:\n     * ارتفاع نسبة التغطية لاختبارات الوحدة الحقيقية (Unit Test Coverage) للمنطق الحرج من 10% إلى 85%."
        ),
        "practical_walkthrough": (
            "لوحة تقرير إثبات نجاح الـ Refactoring (Executive Refactor Scorecard):\n"
            "```markdown\n"
            "## تقرير نتائج إعادة هيكلة موديول الدفع (Payments Modularization Refactor)\n"
            "الفترة: مقارنة الربع الأول (قبل) بالربع الثاني (بعد)\n"
            "\n"
            "| المؤشر الهندسي / التجاري | قبل الـ Refactor | بعد الـ Refactor | نسبة التحسن |\n"
            "|---|---|---|---|\n"
            "| **Crash-Free Sessions** | 99.15% | 99.94% | **+0.79% (استقرار ممتاز)** |\n"
            "| **وقت تسليم الميزة الجديدة** | 16 يوم عمل | 4 أيام عمل | **75% تسريع في السرعة** |\n"
            "| **أخطاء الإنتاج (Production Incidents)** | 8 حوادث/شهر | 0 حوادث | **انخفاض 100%** |\n"
            "| **وقت تجميع الـ Module في CI** | 9 دقائق | 1.8 دقيقة | **80% توفير وقت كاش** |\n"
            "| **تغطية اختبارات الوحدة للمنطق** | 12% | 88% | **+76% موثوقية** |\n"
            "| **حجم الكلاس الأكبر (God Class)** | 4,200 سطر | 280 سطر كحد أقصى | **كود نظيف ومستقل** |\n"
            "```\n"
            "هذا التقرير يثبت للمدير التنفيذي أن الـ 3 أسابيع التي قضاها الفريق في الـ Refactor ستوفر مئات الساعات وآلاف الدولارات في المستقبل."
        ),
        "quick_answer": "Prove refactoring success using quantitative metrics across four domains: Stability (crash-free rates, regression bug count), Velocity (lead time for changes, PR merge conflict rates), Performance (Gradle build times, app startup latency, frame drops), and Testability (meaningful unit test coverage and modular dependency isolation).",
        "best_answer": (
            "A successful refactoring initiative is judged strictly by empirical metrics collected before and after the transition:\n\n"
            "1. **Operational Stability & Quality Metrics**:\n"
            "   - **Crash-Free Rates**: Increase in Crash-Free User/Session percentages in Crashlytics and Android Vitals.\n   - **Defect Escape Rate**: Significant reduction in post-release bugs filed by QA and end-users against the affected domain.\n\n"
            "2. **Engineering Velocity & Agility**:\n"
            "   - **Lead Time for Changes**: Measures the duration from PR creation to production deployment for subsequent features built on top of the refactored system.\n   - **PR Review & Merge Cycle Time**: Smaller, decoupled classes reduce cognitive overhead and eliminate painful Git merge conflicts across squad boundaries.\n\n"
            "3. **Runtime & Build Performance**:\n"
            "   - **Build Duration**: Reduction in local and CI Gradle build times achieved through effective module boundary caching.\n   - **Client Runtime Metrics**: Cold startup duration, frame drop rates (JankStats), and memory allocation headroom.\n\n"
            "4. **Testability & Coupling**:\n"
            "   - Progression from brittle, end-to-end UI tests to fast, deterministic local JVM unit tests covering 80%+ of core business state machines."
        ),
        "deep_answer": (
            "From an engineering leadership and platform maturity standpoint, measuring refactoring requires counteracting vanity metrics:\n\n"
            "1. **The Code Coverage Vanity Trap**: Beware of measuring refactor success purely by raw line coverage percentage. An engineer can achieve 90% coverage by writing tautological tests that assert getters without verifying edge cases or state race conditions. Focus on mutation testing scores or behavioral scenario coverage on core UseCases.\n\n"
            "2. **Developer Sentiment and Friction Index**: Complement quantitative numbers with qualitative developer surveys. Survey squad members on cognitive friction before and after refactoring ('How confident are you modifying the Checkout flow without breaking unrelated code?'). A leap from 2/10 to 9/10 in team confidence confirms sustainable velocity.\n\n"
            "3. **Zero-Regression Canary Releases**: For major structural refactorings, release the new architecture behind a server-side Feature Flag to a 5% canary cohort. Compare business conversion metrics and crash telemetry directly against the legacy 95% cohort to prove algorithmic parity before complete cutover."
        ),
        "follow_ups": [
            {
                "question": "Why is feature lead time a more meaningful metric for refactoring success than lines of code removed?",
                "answer": "Because lines of code is a vanity metric, whereas lead time measures actual business acceleration and how easily the team ships value."
            },
            {
                "question": "How do feature flags protect major architectural refactorings during rollout?",
                "answer": "They allow A/B telemetry comparison against the legacy code in production and provide an instantaneous zero-downtime rollback switch if bugs appear."
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
    for item in LEAD_01_08:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions LEAD-01 to LEAD-08. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
