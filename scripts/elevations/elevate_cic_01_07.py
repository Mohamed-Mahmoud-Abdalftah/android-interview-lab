#!/usr/bin/env python3
"""
Elevation script for CIC questions: CIC-01 to CIC-07.
Topic: CI/CD, Git & Team Delivery (CIC)
Phase 4, Batch 1
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "الـ CI/CD والـ Git وتسليم المشاريع في الفرق الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# CIC-01: What are CI, Continuous Delivery, and Continuous Deployment?
# ==========================================
DATA["CIC-01"] = {
    "concept_en": """The differentiation between Continuous Integration, Continuous Delivery, and Continuous Deployment centers on automation boundaries, release gating, and mobile operating system invariants:
- Continuous Integration (CI):
  - Developers integrate code into the mainline trunk multiple times per day.
  - Every pull request triggers an automated verification pipeline executing fast compilation, static code analysis (Spotless, ktlint, Detekt, Android Lint), and host JVM unit tests (testDebugUnitTest).
  - Primary Goal: Fail fast, surface integration anomalies early, and protect main branch stability.
- Continuous Delivery (CD):
  - Every passing commit on the main branch automatically builds, obfuscates via R8, signs, and packages release artifacts (AAB).
  - Deploys the artifact to internal staging environments or Google Play Internal Testing tracks.
  - Release-Ready Guarantee: The software is perpetually in a releasable state, but actual promotion to public production users requires an intentional human business decision (Manual Approval Gate).
- Continuous Deployment (CD):
  - Fully automated end-to-end flow where every commit passing automated verification deploys directly to public end users without manual gates.
  - Mobile Engineering Realities: Pure continuous deployment to 100% of production users is an anti-pattern in high-scale mobile apps. Client binary rollbacks are impossible without user updates, app store reviews introduce latency, and defective builds directly damage device storage and user trust. Mobile teams combine Continuous Delivery with Staged Rollouts and Server-Driven Feature Flags.""",
    "walkthrough_en": """GitHub Actions workflow illustrating CI verification and Continuous Delivery staging:
```yaml
# .github/workflows/android_release_pipeline.yml
name: Android Release Pipeline

on:
  pull_request:
    branches: [ main ] # Phase 1: Continuous Integration (CI)
  push:
    branches: [ main ] # Phase 2: Continuous Delivery (CD)

jobs:
  # Fast CI Verification Gate
  ci_validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Run Linters & JVM Unit Tests
        run: ./gradlew lintDebug testDebugUnitTest

  # Continuous Delivery: Builds signed AAB and uploads to Internal Testing
  cd_staging:
    needs: ci_validation
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Build Release Bundle
        run: ./gradlew bundleRelease
      - name: Deploy to Google Play Internal Track (Awaiting manual release approval)
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_JSON_KEY }}
          packageName: com.company.app
          releaseFiles: app/build/outputs/bundle/release/*.aab
          track: internal # Deliberate human gate required for production promotion
```""",
    "short_en": """Continuous Integration automates compilation, linting, and unit testing on every pull request to catch defects early. Continuous Delivery ensures every main commit automatically generates a signed release bundle published to internal testing rings ready for manual release approval. Continuous Deployment removes that human gate, automatically pushing code directly to production end users.""",
    "structured_en": """The distinction between Continuous Integration and the two forms of Continuous Delivery hinges on automation boundaries and operational risk tolerance.
In mobile engineering, Continuous Integration focuses on rapid verification. Every developer pull request triggers an automated pipeline executing static analysis, Detekt, ktlint, Android Lint, and host JVM unit tests to ensure no regressions break the shared mainline.
Continuous Delivery extends this automation into release preparation. Every commit merged to the main branch automatically compiles, shrinks via R8, signs, and publishes a release bundle to internal or closed Google Play testing tracks. The application remains permanently releasable, but public promotion requires a conscious human approval gate.
Continuous Deployment eliminates human intervention entirely, pushing every green build straight to production users. In Android development, teams practice Continuous Delivery rather than pure Continuous Deployment. Because client-side application rollbacks are impossible without store reviews and user updates, gating public rollouts with phased percentages and remote feature flags is essential to protect user trust and device stability.""",
    "deep_senior_en": """From a platform architecture and release operations perspective, mobile continuous delivery requires different architectural foundations than web microservices.
In backend architectures, Continuous Deployment is widespread because a defective container deployed to production can be rolled back in seconds using blue-green traffic routing or canary switches. In mobile systems, software is distributed asynchronously as compiled binaries onto millions of heterogeneous physical devices. The Android operating system strictly prevents package version downgrades to avoid data corruption, meaning a defective release cannot simply be revoked on user hardware. Resolving a critical crash requires compiling a hotfix, submitting it through app store review, and waiting for end users to download the update over wireless networks.
Consequently, high-performing mobile organizations adopt Continuous Delivery coupled with automated staged rollouts. The continuous integration pipeline validates pull requests within minutes using cached Gradle build actions and parallelized JVM tests. Merging into trunk automatically triggers delivery pipelines that compile signed Android App Bundles, archive R8 mapping files for Crashlytics de-obfuscation, and distribute artifacts to internal employee dogfood rings.
To achieve rapid iteration without compromising safety, we decouple binary deployment from feature exposure. By shipping dark-launched code behind server-driven feature flags using tools like LaunchDarkly or Firebase Remote Config, engineering teams release features to targeted user cohorts dynamically. If telemetry signals anomalous crash rates in production, the feature is disabled remotely within seconds without requiring an emergency binary hotfix, providing the speed of Continuous Deployment with the safety of disciplined Continuous Delivery.""",
    "meta_ar": {
        "id": "CIC-01",
        "questionAr": "ما هو الفرق بين التكامل المستمر (CI)، والتسليم المستمر (Continuous Delivery)، والنشر المستمر (Continuous Deployment) في أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مستويات أتمتة دورة حياة البرمجيات، والفرق بين البوابة البشرية في Delivery والأتمتة الكاملة في Deployment، وخصوصية تطبيقات الموبايل في حظر الـ Downgrade والحاجة لـ Staged Rollouts.",
        "concept_ar": "يتمحور التمييز بين التكامل المستمر والتسليم المستمر والنشر المستمر حول حدود الأتمتة وحوكمة المخاطر في بيئة الموبايل: التكامل المستمر (CI) يركز على دمج كود المطورين دورياً في الفرع الرئيسي مع تشغيل فحص آلي فوري يشمل التحليل الساكن واختبارات الوحدة لضمان سلامة الكود مبكراً. التسليم المستمر (Continuous Delivery) يأخذ الكود المدمج في Main ويبني حزمة الإنتاج الموقعة ويرفعها لمسار الاختبار الداخلي في Google Play؛ فيكون التطبيق جاهزاً للإطلاق فورياً لكن عملية الطرح للمستخدمين تتطلب موافقة بشرية بنقرة زر. أما النشر المستمر (Continuous Deployment) فينشر الكود للمستخدمين تلقائياً دون أي تدخل بشري. وفي أندرويد، يُفضل التسليم المستمر مع الطرح التدريجي ومفاتيح الميزات لأن أجهزة المستخدمين تمنع التراجع التلقائي وتتطلب تحديثاً ثنائياً كاملاً.",
        "walkthrough_ar": """مخطط GitHub Actions يوضح مسار الـ CI وفصل الـ Delivery ببوابة مخصصة:
```yaml
# .github/workflows/android_ci_cd.yml
name: Android CI/CD Pipeline

on:
  pull_request:
    branches: [ main ] # مرحلة التكامل المستمر (CI)
  push:
    branches: [ main ] # مرحلة التسليم المستمر (CD)

jobs:
  ci_verification:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - run: ./gradlew lintDebug testDebugUnitTest

  cd_delivery:
    needs: ci_verification
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew bundleRelease
      - name: Deploy to Google Play Internal Track
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_JSON_KEY }}
          packageName: com.company.app
          releaseFiles: app/build/outputs/bundle/release/*.aab
          track: internal # بوابات الموافقة اليدوية للطرح العام
```""",
        "why_it_matters_ar": "يحدد سرعة وصول الميزات للمستخدمين مع حماية استقرار التطبيق وتفادي الكوارث الإنتاجية التي يستحيل التراجع عنها لحظياً في الهواتف.",
        "worked_example_ar": "شركة نقل ذكي تعتمد CI لفحص كل Pull Request في 4 دقائق، مع تسليم مستمر يرفع الحزمة لمختبري الشركة تلقائياً، وتطرح التحديث للمستخدمين تدريجياً بنسبة 5% بعد موافقة الـ QA.",
        "trade_offs_ar": "النشر المستمر التلقائي الكامل يلغي التأخير البشري لكنه شديد الخطورة في الموبايل؛ بينما التسليم المستمر يضيف مراجعة بشرية تضمن سلامة النسخة قبل وصولها لملايين الأجهزة.",
        "failure_modes_ar": "إطلاق نسخة إنتاجية لـ 100% من المستخدمين دون اختبار في مسار داخلي، أو الخلط بين مصطلح التسليم المستمر والنشر الكامل دون وجود بوابات أمان.",
        "production_perspective_ar": "في بيئات الإنتاج الكبرى، نعتمد التسليم المستمر حتى مسار Closed Testing في Google Play، ونربط الطرح التدريجي بمؤشرات Crashlytics و Feature Flags للتحكم السحابي الفوري.",
        "how_to_answer_ar": "حدد الفارق بدقة: CI للتحقق التلقائي من الكود، Continuous Delivery لجعل النسخة جاهزة دائماً مع بوابة موافقة يدوية، و Continuous Deployment للنشر الآلي الكامل، مع تبرير تفضيل Delivery في الموبايل.",
        "talking_points_ar": "فحص Pull Requests الآلي، جاهزية الحزمة الدائمة، بوابة الموافقة البشرية، حظر الـ Rollback في أندرويد، وفصل النشر الثنائي عن تفعيل الميزات بـ Feature Flags.",
        "follow_ups_ar": "- **المحاور:** 'لماذا تتجنب معظم فرق الموبايل النشر المستمر التلقائي بنسبة 100% في الإنتاج؟'\n  **المرشح:** 'لأن تطبيقات الموبايل تُثبت كثنائيات على أجهزة المستخدمين ويستحيل التراجع عنها فورياً إذا حدث عطل كارثي؛ كما أن مراجعات المتاجر تستغرق وقتاً، لذا يفضل الطرح التدريجي مع مفاتيح الميزات.'\n\n- **المحاور:** 'كيف يساعد استخدام Feature Flags في سد الفجوة بين Delivery و Deployment؟'\n  **المرشح:** 'يتيح شحن الكود باستمرار إلى الأجهزة في وضع خامل، ثم تفعيله تدريجياً من السيرفر لمجموعات محددة دون الحاجة لانتظار دورة تحديث جديدة في المتجر.'",
        "self_check_ar": "هل وضحت الفارق بين المستويات الثلاثة وبوابة الموافقة البشرية وخصوصية نظام أندرويد في الـ Rollback؟",
        "references_ar": f"- [Martin Fowler: Continuous Delivery vs Deployment](https://martinfowler.com/bliki/ContinuousDelivery.html) — المرجع الكلاسيكي للفروق المعمارية بين أنماط التسليم.\n- [Google Play: Release tracks and staged rollouts](https://support.google.com/googleplay/android-developer/answer/6346149) — دليل مسارات الإطلاق والطرح التدريجي الرسمي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """التكامل المستمر يؤتمت فحص الكود واختبارات الوحدة مع كل دمج لاكتشاف المشاكل مبكراً. التسليم المستمر يضمن أن الكود المدمج يولد تلقائياً حزمة جاهزة للنشر ومرفوعة للمسار الداخلي وتنتظر موافقة يدوية. أما النشر المستمر فيلغي البوابة البشرية وينشر التحديث تلقائياً وبشكل كامل للمستخدمين في الإنتاج.""",
        "best_answer_ar": """يكمن الفرق بين التكامل المستمر والتسليم المستمر والنشر المستمر في حدود الأتمتة ودرجة التحكم في مخاطر الإصدار.
في التكامل المستمر، يقوم المطورون بدمج الكود في الفرع الرئيسي بانتظام، ويطلق كل طلب دمج خطاً آلياً يفحص التنسيق ويشغل التحليل الساكن واختبارات الوحدة السريعة على الـ JVM لضمان سلامة الكود وعدم كسر المشروع المشترك.
أما التسليم المستمر، فيوسع الأتمتة لتشمل بناء الحزم الموقعة بـ R8 ورفعها لمسارات الاختبار الداخلية في Google Play؛ وبذلك يكون التطبيق في حالة جاهزية دائمة للنشر، ولكن عملية إطلاقه للمستخدمين في المتجر تتطلب قراراً بشرياً واعياً.
وفي النشر المستمر، تُنشر أي تعديلات تجتاز الاختبارات تلقائياً ومباشرة إلى المستخدمين دون أي مراجعة بشرية. وفي هندسة أندرويد، تفضل الفرق التسليم المستمر نظراً لاستحالة التراجع الفوري عن النسخ المثبتة على هواتف المستخدمين، مما يجعل الطرح التدريجي ومفاتيح الميزات صمام أمان لا غنى عنه.""",
        "deep_answer_ar": """من منظور حوكمة المنصات وعمليات الإصدار، تتطلب تطبيقات الهواتف الذكية معمارية تسليم تختلف جذرياً عن الأنظمة الخلفية السحابية.
في الخدمات السحابية، يمكن تطبيق النشر المستمر التلقائي الكامل بسهولة؛ لأن أي عطل غير متوقع يمكن معالجته في ثوانٍ عبر توجيه حركة المرور لإصدار سابق. أما في أندرويد، فيتم توزيع البرنامج كملف ثنائي مستقل على ملايين الأجهزة؛ ونظام التشغيل يمنع خفض رقم الإصدار حماية لقواعد البيانات المحلية، مما يعني أن سحب نسخة معطوبة يتطلب بناء تحديث جديد وانتظار مراجعة المتجر وتنزيل المستخدمين له.
ولذلك، تعتمد الفرق المتطورة استراتيجية التسليم المستمر بالتكامل مع الطرح التدريجي؛ حيث يتم فحص التعديلات في خط الـ CI خلال دقائق باستخدام الكاش السحابي، ثم تُبنى حزمة AAB موحدة تُرفع إلى مسارات الاختبار المغلقة للتحقق منها مع حفظ ملفات mapping.txt لتشخيص الانهيارات.
ولتحقيق سرعة الإطلاق دون التضحية بالأمان، نفصل نشر الملف الثنائي عن إطلاق الميزات للمستخدمين؛ حيث نشحن الأكواد الجديدة في وضع خامل ونتحكم في ظهورها عبر مفاتيح الميزات المدارة سحابياً مثل Firebase Remote Config أو LaunchDarkly. فإذا أظهرت المراقبة الحية أي زيادة في معدل الانهيارات، يتم تعطيل الميزة لحظياً من السيرفر دون الحاجة لإطلاق تحديث طارئ، مما يوفر سرعة النشر المستمر مع أمان التسليم المنضبط."""
    }
}

# ==========================================
# CIC-02: What are typical stages in an Android CI pipeline?
# ==========================================
DATA["CIC-02"] = {
    "concept_en": """A production-grade Android Continuous Integration pipeline is organized into tiered, parallel stages optimized to fail fast and conserve runner compute:
- Core CI Pipeline Stages:
  1. Environment Setup & Cache Restoration:
     - Check out source repository, provision JDK via Gradle toolchains, and hydrate Gradle user home and remote build cache.
  2. Static Code Analysis & Linting:
     - Execute formatting linters (Spotless, ktlint), static analysis for code smells and architecture boundaries (Detekt), and Android framework linting (lintDebug with baselines).
  3. Host JVM Unit Testing:
     - Run testDebugUnitTest in parallel across modules. Validates business logic, domain use cases, ViewModels, and state machines within minutes without emulator overhead.
  4. Compilation & Assembly Verification:
     - Compile debug and release variants (assembleDebug, bundleRelease) to verify DEX packaging and R8 configuration validity.
  5. Automated UI & Instrumentation Testing:
     - Execute automated UI smoke tests on managed emulators or cloud test labs (Firebase Test Lab) for critical checkout and login flows.
  6. Binary Governance & Size Budgeting:
     - Diff APK/AAB size budgets against base commits using tools like Diffuse to prevent accidental asset bloat; audit dependency CVE vulnerabilities.
  7. Artifact Archival & Observability:
     - Archive test execution reports, coverage outputs, and upload R8 mapping.txt to Crashlytics.""",
    "walkthrough_en": """Parallel, fail-fast Android CI workflow configuration:
```yaml
# .github/workflows/pr_verification.yml
name: PR Quality Verification
on: [pull_request]

jobs:
  # Fast Tier: Formatting, Linters, and Architecture rules
  static_analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Linters & Detekt
        run: ./gradlew spotlessCheck detekt

  # Fast Tier: Host JVM Unit Tests in parallel
  unit_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run JVM Unit Tests
        run: ./gradlew testDebugUnitTest

  # Gated Tier: Assembly and Binary Sizing (Runs only after fast checks pass)
  build_assembly:
    needs: [static_analysis, unit_tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Compile Debug APK & Assert Size Budget
        run: ./gradlew assembleDebug
```""",
    "short_en": """A production Android CI pipeline consists of environment checkout and cache restoration, parallel static analysis with Detekt and Spotless, host JVM unit testing via testDebugUnitTest, compilation and assembly verification, automated UI testing on device farms, binary size regression auditing, and test report and mapping artifact archiving.""",
    "structured_en": """A mature Android CI pipeline is structured into tiered, parallel stages designed to fail fast and minimize developer waiting times.
The pipeline begins with environment hydration, setting up the target JDK toolchain and restoring remote Gradle build caches.
Next, fast verification runs in parallel. We execute static analysis including Spotless, ktlint, Detekt, and Android Lint to enforce coding standards, alongside host JVM unit tests via testDebugUnitTest across all modules. By running these lightweight jobs concurrently, defects in formatting, architecture rules, or domain logic fail the pipeline within two minutes.
Once fast checks pass, gated stages execute assembly verification. Tasks like assembleDebug and bundleRelease compile the binary and validate R8 shrinking rules.
Finally, high-confidence release pipelines execute automated instrumentation tests on cloud device farms such as Firebase Test Lab, run binary size diffing to prevent bloat, and archive R8 mapping files and test summaries for observability.""",
    "deep_senior_en": """From a platform engineering leadership perspective, structuring an Android CI pipeline requires balancing thorough quality gates against developer feedback velocity and infrastructure costs.
A common failure mode in mobile teams is running CI stages sequentially: checkout, assemble, lint, and test. When a compilation or assembly task runs before linting, a developer who forgot a trailing comma or broke a single unit test must wait eight minutes for a failure that should have surfaced in sixty seconds.
Senior architectures decouple and parallelize stages based on execution duration and failure frequency. Static code analysis and host JVM unit tests run concurrently as the first tier. These tasks require no emulator virtualization and complete in under two minutes, terminating the pipeline immediately on failure to conserve runner resources.
Furthermore, we separate pull request verification from merge queue and nightly pipelines. Heavy end-to-end instrumentation tests, screenshot regression suites, and full release AAB compilation are impractical to run on every single pull request push. We execute a targeted smoke suite on pull requests, while delegating exhaustive multi-device matrix testing and baseline profile generation to post-merge pipelines or scheduled nightly runs.
Finally, artifact management is a critical pipeline responsibility. The pipeline must generate and retain test result XMLs for flaky test tracking, export code coverage metrics to SonarQube, and automatically upload R8 mapping.txt artifacts to monitoring platforms like Firebase Crashlytics. Without automated symbol file archiving paired with each build commit, field crashes in release builds become impossible to diagnose.""",
    "meta_ar": {
        "id": "CIC-02",
        "questionAr": "ما هي المراحل النموذجية (Stages) في خط أنابيب أندرويد (Android CI Pipeline) المتكامل؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "هيكلة مراحل الـ CI المتوازية لتطبيق مبدأ Fail-Fast، والفصل بين الفحوصات السريعة وتجميع الـ APK الثقيل، وإدارة كاش Gradle، وفصل فحوصات PR عن اختبارات الأجهزة السحابية.",
        "concept_ar": "تُنظم خطوط أنابيب الـ CI الاحترافية في أندرويد على هيئة مراحل متوازية ومتدرجة تهدف إلى اكتشاف الأخطاء بأسرع وقت وتقليل استهلاك موارد السيرفرات: المرحلة الأولى هي تجهيز البيئة واستعادة كاش Gradle السحابي لتجنب إعادة تنزيل التبعيات. المرحلة الثانية والثالثة تعملان بالتوازي وتشملان التحليل الساكن (Spotless و Detekt و Lint) واختبارات الوحدة على الـ JVM (testDebugUnitTest)؛ حيث تنتهي هذه الفحوصات في أقل من دقيقتين. والمرحلة الرابعة هي التجميع (Assemble) وبناء الـ AAB للتأكد من سلامة ملفات الـ DEX وقواعد R8. والمرحلة الخامسة هي اختبارات الواجهة والأجهزة الحقيقية (Instrumentation Tests) على مزارع سحابية كـ Firebase Test Lab. وأخيراً مرحلة قياس حجم الحزمة وأرشفة ملفات mapping.txt وتقارير الاختبارات.",
        "walkthrough_ar": """مخطط تفصيلي لمراحل الـ CI Pipeline في ملف عمل GitHub Actions متوازي:
```yaml
# .github/workflows/pr_validation.yml
name: PR Quality Gate
on: [pull_request]

jobs:
  static_analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Run Linters & Detekt
        run: ./gradlew spotlessCheck detekt

  unit_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Run JVM Unit Tests
        run: ./gradlew testDebugUnitTest

  bundle_and_size:
    needs: [static_analysis, unit_tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
      - name: Build Debug APK & Analyze Size
        run: ./gradlew assembleDebug
```""",
        "why_it_matters_ar": "يمنع تعطل الفروع المشتركة، ويوفر تغذية راجعة للمطورين في دقائق معدودة بدلاً من الانتظار الطويل، ويقلل تكاليف سيرفرات الـ CI.",
        "worked_example_ar": "تحويل خط CI تتابعي يستغرق 15 دقيقة إلى خط متوازي يفحص التنسيق والـ Unit Tests معاً، فاكتشف المطور خطأ كسر الاختبارات في دقيقة واحدة ووفر 70% من وقت البناء.",
        "trade_offs_ar": "تشغيل كافة الاختبارات الثقيلة على كل PR يوفر أماناً مطلقاً ولكنه يعطل حركة الفريق؛ والحل هو فحص سريع في الـ PR وتأجيل الاختبارات الثقيلة لما بعد الدمج.",
        "failure_modes_ar": "تشغيل مهمة assembleDebug الثقيلة قبل فحوصات التنسيق البسيطة، أو إهمال كاش Gradle مما يضاعف زمن البناء في كل تشغيل.",
        "production_perspective_ar": "في المشروعات الكبرى، نعتمد Remote Build Cache لـ Gradle، ونفصل اختبارات الـ UI لتشغيلها ليلياً أو عند دمج الكود في فروع الإصدار الرسمية.",
        "how_to_answer_ar": "قسم الإجابة إلى مستويات: تجهيز الكاش، الفحوصات السريعة المتوازية (Lint و Unit Tests)، التجميع والتحقق من R8، اختبارات الأجهزة، وأرشفة التقارير والرموز.",
        "talking_points_ar": "مبدأ Fail-Fast، الفحوصات المتوازية، اختبارات JVM السريعة، تجنب المحاكيات في كل PR، مراقبة حجم الحزمة، وأرشفة ملف mapping.txt.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يجب تشغيل التحليل الساكن واختبارات الـ Unit Tests قبل مهمة assemble؟'\n  **المرشح:** 'لتطبيق مبدأ الفشل السريع Fail-Fast؛ فإذا كان هناك خطأ تنسيق أو كسر لاختبار وحدة، يفشل البناء في أقل من دقيقتين دون إضاعة خمس دقائق في تجميع الـ APK كاملاً.'\n\n- **المحاور:** 'كيف تتعامل مع اختبارات الواجهة Instrumentation Tests التي تستغرق وقتاً طويلاً؟'\n  **المرشح:** 'نشغل عينة سريعة من اختبارات المسارات الحرجة Smoke Tests على طلبات الدمج، بينما نرحل حزمة الاختبارات الشاملة لتعمل ليلياً على أجهزة سحابية.'",
        "self_check_ar": "هل غطيت مراحل الكاش والتحليل الساكن واختبارات JVM والتجميع واختبارات الأجهزة وأرشفة المخرجات؟",
        "references_ar": f"- [Gradle: Build Cache and CI](https://docs.gradle.org/current/userguide/build_cache.html) — الدليل الرسمي لإعداد كاش Gradle في بيئات الـ CI.\n- [Android Developers: Test in CI](https://developer.android.com/training/testing/instrumented-tests) — توثيق تشغيل الاختبارات الآلية في خطوط الأنابيب.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """يتكون خط أنابيب أندرويد النموذجي من مراحل متدرجة: استعادة الكاش وتجهيز البيئة، الفحص الساكن المتوازي بـ Detekt و Spotless، اختبارات الوحدة على JVM بـ testDebugUnitTest، تجميع الحزم والتحقق من قواعد R8، اختبارات الأجهزة السحابية، تدقيق حجم الـ APK، وأرشفة ملفات mapping.txt والتقارير.""",
        "best_answer_ar": """يُهيكل خط أنابيب أندرويد الاحترافي في مراحل متوازية ومتدرجة صُممت لتطبيق مبدأ الفشل السريع وتوفير وقت المطورين.
تبدأ المرحلة الأولى بتجهيز بيئة الـ JDK واستعادة كاش Gradle السحابي لتفادي إعادة تنزيل المكتبات وتجميع الأكواد غير المعدلة.
بعد ذلك، تنطلق مرحلة الفحوصات السريعة بالتوازي؛ حيث يُشغل السيرفر أدوات التحليل الساكن والتنسيق مثل Spotless و Detekt و Android Lint جنباً إلى جنب مع اختبارات الوحدة على الـ JVM عبر مهمة testDebugUnitTest لكافة الموديولات. وتتميز هذه المرحلة بالسرعة الفائقة حيث تكتشف أخطاء التنسيق وكسر المنطق البرمجي خلال دقيقتين فقط.
وبعد اجتياز الفحوصات السريعة، تبدأ مرحلة تجميع الحزمة عبر مهام assembleDebug أو bundleRelease للتأكد من خلو ملفات DEX من الأخطاء وسلامة قواعد تقليص R8.
وأخيراً، تنفذ خطوط الإصدار اختبارات الواجهة المؤتمتة على أجهزة سحابية، وتدقق حجم الحزمة لمنع التضخم، وترفع ملفات mapping.txt لمنصات المراقبة مثل Crashlytics.""",
        "deep_answer_ar": """من منظور قيادة هندسة المنصات، تتطلب هيكلة خطوط الـ CI موازنة دقيقة بين فرض معايير الجودة الصارمة وسرعة التغذية الراجعة للمطورين وتكاليف الخوادم.
إن الخطأ الأكثر شيوعاً في فرق الموبايل هو بناء خط تتابعي ينفذ المهام خطوة تلو الأخرى: تنزيل الكود، تجميع الـ APK، فحص الكود الساكن، ثم تشغيل الاختبارات. فعند تشغيل مهمة تجميع ثقيلة في البداية، يضطر المطور لانتظار ثماني دقائق ليكتشف في النهاية أن البناء فشل بسبب فاصلة منقوطة مفقودة أو اختبار وحدة بسيط كان يمكن كشفه في ثلاثين ثانية.
ولذلك، نبني المعمارية على نظام المستويات المتوازية؛ حيث ينفذ المستوى الأول فحص التنسيق والتحليل الساكن واختبارات الوحدة على الـ JVM بالتوازي وبمعزل عن محاكيات أندرويد الثقيلة، مما يوفر نتيجة فورية ويوقف خط البناء عند وجود أي خلل قبل استهلاك خوادم البناء.
علاوة على ذلك، نفصل متطلبات فحص طلبات الدمج اليومية عن خطوط ما بعد الدمج والإصدار الرسمي؛ فلا يمكن تشغيل اختبارات الواجهة الشاملة واختبارات الانحدار البصري عند كل تعديل بسيط، بل نكتفي باختبارات المسار الحرج في الـ PR، ونرحل الاختبارات المعقدة وتوليد Baseline Profiles إلى خطوط البناء الليلية.
وأخيراً، نولي أرشفة المخرجات أهمية قصوى؛ حيث يرفع الـ Pipeline تقارير الاختبارات لتتبع الاختبارات المتذبذبة، ويرفع ملفات mapping.txt الخاصة بـ R8 تلقائياً إلى Firebase Crashlytics لضمان القدرة على فك تشفير أي انهيار يحدث في الإنتاج فورياً."""
    }
}

# ==========================================
# CIC-03: What are build artifacts and release tracks?
# ==========================================
DATA["CIC-03"] = {
    "concept_en": """Android build artifacts represent the compiled deliverables of a build variant, while release tracks define progressive distribution rings connecting compilation to end users:
- Core Android Build Artifacts:
  1. Android App Bundle (.aab): The official distribution format for Google Play. Contains compiled DEX, resources, and native binaries. Enables Google Play Dynamic Delivery to generate optimized Split APKs tailored to device screen density, CPU architecture (ABI), and language, saving 20-30% download size.
  2. APK (.apk): Standalone installable package used for local development debugging, internal QA sideloading, and enterprise distribution via Firebase App Distribution.
  3. R8 / ProGuard Mapping File (mapping.txt): Generated during release shrinking. Translates obfuscated class and method tokens back to original source lines. Required by Crashlytics and Google Play for de-obfuscation.
  4. Baseline Profiles (baseline.prof): Pre-compiled rules guiding ART ahead-of-time (AOT) compilation to boost cold startup speed and scroll frame rates.
- Google Play Release Tracks:
  - Internal Testing Track: Instant distribution to up to 100 designated internal testers with virtually zero review latency.
  - Closed (Alpha/Beta) Track: Controlled cohorts of specific user groups or organizations.
  - Open Track: Broad public beta accessible directly on the store.
  - Production Track: General public consumer release with staged rollout percentages (1% to 100%).
- Principle of Artifact Immutability: Build and sign once; promote the identical binary across tracks without recompiling.""",
    "walkthrough_en": """Automated mapping file archival and release artifact configuration:
```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

// Gradle task to archive release mapping files paired with version code:
tasks.register<Copy>("archiveReleaseMetadata") {
    dependsOn("minifyReleaseWithR8")
    from(layout.buildDirectory.dir("outputs/mapping/release"))
    into(layout.projectDirectory.dir("release-metadata"))
    include("mapping.txt")
    rename { "mapping-v${android.defaultConfig.versionCode}.txt" }
}
```""",
    "short_en": """Build artifacts are compiled deliverables including AAB bundles for Google Play Dynamic Delivery, installable APKs for internal QA, mapping.txt for R8 crash de-obfuscation, and baseline profiles for startup acceleration. Release tracks are tiered distribution rings spanning Internal testing, Closed alpha cohorts, Open beta testing, and Staged Production rollouts.""",
    "structured_en": """Build artifacts and release tracks represent the compiled deliverables and progressive distribution channels connecting code compilation to end users.
On the artifact side, the Android App Bundle is the required publishing format for Google Play. It enables Dynamic Delivery, generating optimized Split APKs per device to reduce download sizes. In contrast, universal APKs serve as standalone binaries for local debugging and QA distribution via Firebase App Distribution. Critical accompanying artifacts include the R8 mapping.txt file, which is required by Crashlytics to de-obfuscate release stack traces, and Baseline Profiles that guide ahead-of-time compilation for instant application startup.
On the distribution side, Google Play Console provides tiered release tracks. The Internal track enables immediate distribution to team members without store review delays. Closed and Open tracks allow testing with controlled user cohorts and public beta testers. Finally, the Production track serves the general public using staged rollouts to monitor performance and contain regressions. Across all tracks, we enforce artifact immutability, ensuring the identical binary tested in staging is promoted to production without recompilation.""",
    "deep_senior_en": """From an enterprise release governance and build architecture standpoint, managing build deliverables requires strict adherence to artifact immutability and observability pairing.
A critical anti-pattern observed in immature release pipelines is compiling one binary for QA testing and compiling a second binary for store deployment. Recompiling across environments introduces non-deterministic timestamp discrepancies, subtle dependency drift, and untested bytecode variations. High-performing mobile organizations build and sign a single immutable release Android App Bundle once, promote it through Internal, Closed, and Open tracks, and finally push that exact artifact to production.
Utilizing the Android App Bundle unlocks Google Play Dynamic Delivery and App Slicing. Rather than forcing users to download a bloated universal package containing every screen density from mdpi to xxxhdpi and native libraries across multiple architectures, the Play Store generates a minimal base APK with architecture and language splits tailored to the user device, reducing download friction and uninstalls.
Equally vital is the automated pairing of build metadata. When R8 obfuscates code, classes and line numbers are rewritten into short tokens. If the release pipeline fails to archive mapping.txt and upload it to Firebase Crashlytics via the uploadCrashlyticsSymbolFileRelease task, field crashes appear as unreadable minified traces, paralyzing incident response.
By coupling immutable AAB artifacts, automated Crashlytics symbol ingestion, and staged production rollout cadences, platform teams achieve safe, observable, and reproducible app delivery.""",
    "meta_ar": {
        "id": "CIC-03",
        "questionAr": "ما هي مخرجات البناء (Build Artifacts) ومسارات الإطلاق (Release Tracks) في تطوير تطبيقات أندرويد؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مخرجات البناء (AAB و APK و mapping.txt و Baseline Profiles)، ومسارات الإطلاق في Google Play (داخلي ومغلق ومفتوح وإنتاج)، ومبدأ ثبات الحزمة (Artifact Immutability).",
        "concept_ar": "تمثل مخرجات البناء (Build Artifacts) الملفات الثنائية الناتجة عن عملية الترجمة، بينما تمثل مسارات الإطلاق (Release Tracks) حلقات التوزيع المتدرجة: مخرجات البناء تشمل حزمة Android App Bundle (AAB) المخصصة لـ Google Play لتقسيم الحزم عبر Dynamic Delivery وتوفير 20-30% من الحجم، وملفات APK للتثبيت المباشر في الاختبارات، وملف الخرائط mapping.txt الضروري لفك تشفير تقارير الأخطاء في Crashlytics، وملفات Baseline Profiles لتسريع الإقلاع. ومسارات الإطلاق تشمل المسار الداخلي (Internal) لفرق العمل الفورية، والمسار المغلق (Closed) لمجموعات محددة، والمسار المفتوح (Open) للبيتا العامة، ومسار الإنتاج (Production) مع الطرح التدريجي. وتعتمد الحوكمة الاحترافية على مبدأ ثبات الحزمة (Artifact Immutability) حيث يتم بناء الحزمة وتوقيعها مرة واحدة وترقيتها بين المسارات دون إعادة تجميع.",
        "walkthrough_ar": """إعداد أرشفة ملف الـ mapping وضبط مخرجات الـ Release في build.gradle.kts:
```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

// مهمة Gradle لأرشفة ملف الخرائط mapping.txt مع رقم الإصدار:
tasks.register<Copy>("archiveReleaseMetadata") {
    dependsOn("minifyReleaseWithR8")
    from(layout.buildDirectory.dir("outputs/mapping/release"))
    into(layout.projectDirectory.dir("release-metadata"))
    include("mapping.txt")
    rename { "mapping-v${android.defaultConfig.versionCode}.txt" }
}
```""",
        "why_it_matters_ar": "يضمن تقليل حجم التنزيل للمستخدمين، وتوفير الشفافية الكاملة لتشخيص كراشات الإنتاج، وترقية النسخ بأمان وموثوقية عالية.",
        "worked_example_ar": "فريق أطلق نسخة دون رفع mapping.txt فظهرت الانهيارات مشوشة؛ أضاف الفريق مهمة رفع الخرائط آلياً في الـ CI واعتمد حزم AAB فقلص حجم التطبيق بنسبة 25%.",
        "trade_offs_ar": "حزمة AAB تتطلب استخدام Google Play لتوليد الحزم المجزأة، بينما ملف الـ APK المباشر أسهل للتوزيع الداخلي لكنه أكبر حجماً بكثير.",
        "failure_modes_ar": "إعادة بناء التطبيق من الصفر عند الانتقال من مرحلة الاختبار إلى الإنتاج بدلاً من ترقية نفس الملف، مما يكسر مبدأ ثبات الحزمة ويسبب فروقاً غير مختبرة.",
        "production_perspective_ar": "نلزم خط الـ CI برفع ملف mapping.txt إلى Crashlytics آلياً، ونعتمد مسار Internal Testing للتوزيع الداخلي اليومي قبل فتح أي اختبار عام.",
        "how_to_answer_ar": "اشرح أولاً مخرجات البناء (AAB للتوزيع و APK للاختبار و mapping للتشخيص و Baseline Profiles)، ثم مسارات المتجر (Internal و Closed و Open و Production)، وأكد على مبدأ ثبات الحزمة.",
        "talking_points_ar": "حزمة AAB وتقنية Dynamic Delivery، دور mapping.txt في Crashlytics، مسارات الاختبار الداخلي والمغلق، والطرح التدريجي، ومبدأ Artifact Immutability.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا تم نشر تطبيق في الإنتاج دون رفع ملف mapping.txt إلى Crashlytics؟'\n  **المرشح:** 'ستظهر كافة سجلات الانهيار في لوحة التحكم بأسماء مشوشة ومبهمة مثل a.b.c، مما يجعل تحديد السطر أو الدالة المتسببة في الانهيار أمراً شبه مستحيل.'\n\n- **المحاور:** 'لماذا يُحظر إعادة بناء الكود عند ترقية النسخة من مسار الاختبار الداخلي إلى الإنتاج؟'\n  **المرشح:** 'لأن إعادة البناء تكسر مبدأ ثبات الحزمة؛ فقد تؤدي لاختلاف الطوابع الزمنية أو جلب تحديثات غير مختبرة في التبعيات، ويجب ترقية نفس الحزمة الثنائية التي تم اختبارها بدقة.'",
        "self_check_ar": "هل شرحت حزم AAB و APK وملف mapping ومسارات الاختبار والمتجر ومبدأ ثبات الحزمة؟",
        "references_ar": f"- [Android Developers: Android App Bundle](https://developer.android.com/guide/app-bundle) — التوثيق الرسمي لحزم AAB وتقنية Dynamic Delivery.\n- [Google Play: Manage release tracks](https://support.google.com/googleplay/android-developer/answer/9845334) — دليل إدارة مسارات الإطلاق في Google Play.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """مخرجات البناء هي الثنائيات الناتجة وتشمل حزم AAB للنشر في Google Play مع تقليل الحجم، وملفات APK للاختبارات المباشرة، وملف mapping.txt لفك تشفير تقارير الأخطاء بـ R8، وملفات Baseline Profiles لتسريع الإقلاع. ومسارات الإطلاق هي قنوات توزيع متدرجة تشمل المسار الداخلي، والمسار المغلق، والمسار المفتوح، ومسار الإنتاج التدريجي.""",
        "best_answer_ar": """تمثل مخرجات البناء وحلقات الإطلاق المنظومة المتكاملة التي تربط تجميع الكود المصدري بتسليمه الفعلي للمستخدمين.
على صعيد مخرجات البناء، تعد حزمة Android App Bundle الصيغة الإلزامية للنشر في متجر Google Play؛ حيث تستخدم تقنية Dynamic Delivery لتقسيم التطبيق وتوليد حزم مخصصة لكل هاتف بحسب المعالج والشاشة واللغة مما يقلل الحجم بنسبة كبيرة. في المقابل، نستخدم ملفات APK كحزم شاملة للاختبارات الداخلية عبر Firebase App Distribution. وتتضمن المخرجات الحيوية ملف الخرائط mapping.txt لفك تشفير الأخطاء في Crashlytics، وملفات Baseline Profiles لتحسين سرعة بدء التشغيل.
أما مسارات الإطلاق في Google Play، فتوفر قنوات تدريجية تبدأ بالمسار الداخلي لفرق العمل دون انتظار مراجعة المتجر، ثم المسار المغلق لاختبار الميزات مع شرائح مستخدمين محددة، ثم المسار المفتوح للنسخ التجريبية العامة، وصولاً لمسار الإنتاج الذي يعتمد الطرح التدريجي لتقليل المخاطر. ونلتزم في كافة المسارات بمبدأ ثبات الحزمة؛ حيث يتم بناء وتوقيع النسخة مرة واحدة وترقيتها بين المسارات دون إعادة تجميع الكود.""",
        "deep_answer_ar": """من منظور حوكمة الإصدارات وهندسة البناء في المؤسسات الكبرى، يتطلب التعامل مع مخرجات البناء ومسارات النشر التزاماً صارماً بمبدأ ثبات الحزمة وتكامل أدوات المراقبة.
إن أخطر الممارسات الخاطئة في خطوط الأنابيب غير الناضجة هي تجميع نسخة لفرق اختبار الجودة ثم إعادة تجميع نسخة جديدة للمتجر؛ فهذا يعرض المشروع لاختلافات غير مقصودة في التبعيات وتغيرات غير مختبرة في الـ Bytecode. والنهج الهندسي الصحيح هو بناء حزمة AAB موحدة وموقعة وتمرير نفس الملف الثنائي عبر مسارات الاختبار الداخلي ثم التجريبي ثم الإنتاج دون مساس.
ويحقق استخدام حزم AAB وفورات ضخمة في حجم التنزيل للمستخدمين؛ حيث يقوم متجر Google Play بفصل الموارد واللغات ومكتبات المعالجات وتقديم حزمة مجزأة مخصصة لكل جهاز بدلاً من تنزيل حزمة شاملة ضخمة، مما يحسن معدلات التحويل ويقلل حذف التطبيق.
وعلاوة على ذلك، تلعب أرشفة مخرجات الميتاداتا دوراً محورياً في استقرار التشغيل؛ فعند تفعيل تقليص وتشويش الكود عبر R8، تتغير أسماء الكلاسات والدوال. وإذا لم يرفع خط الـ CI ملف الخرائط mapping.txt إلى Firebase Crashlytics عبر المهمة المخصصة، ستظهر الانهيارات الإنتاجية على هيئة رموز مبهمة يستحيل قراءتها، مما يشل قدرة الفريق على الاستجابة للأعطال الطارئة.
ومن خلال الدمج بين حزم AAB الثابتة، وأرشفة ملفات الخرائط التلقائية، وجدولة الطرح التدريجي عبر مسارات المتجر، نضمن إطلاقاً سلساً وموثوقاً وخالياً من المفاجآت لكافة مستخدمي التطبيق."""
    }
}

# ==========================================
# CIC-04: Compare Git merge, rebase, squash, revert, and reset.
# ==========================================
DATA["CIC-04"] = {
    "concept_en": """Git operations govern how commit histories are joined, reshaped, or reversed across collaboration workflows:
- Comparative Behavioral Analysis:
  1. git merge:
     - Joins diverged branch histories by creating a 3-way merge commit with two parents.
     - Preserves full chronological accuracy and branch topology, but creates non-linear graph complexity with merge commit noise.
  2. git rebase:
     - Replays commits from the current branch onto the tip of the target base branch one by one.
     - Produces a pristine linear history. Rewrites commit SHA hashes; strictly prohibited on public shared branches.
  3. git squash:
     - Condenses multiple incremental commits into a single atomic commit.
     - Standard in pull request workflows (Squash and Merge) to hide intermediate exploratory commits and keep mainline history bisect-friendly.
  4. git revert:
     - Undoes a previous commit by generating a new forward commit containing the inverse diff.
     - 100% safe on shared branches because it preserves history immutability without requiring force-pushing.
  5. git reset:
     - Moves the current branch HEAD ref backward in time to a previous commit.
     - Modifies history and discards or unstages commits; destructive if pushed to remotes requiring forced updates.""",
    "walkthrough_en": """Practical Git CLI workflows comparing rebase, squash, revert, and reset:
```bash
# 1. Linear history: Rebase feature branch on updated main before PR creation:
git checkout feature/checkout-flow
git fetch origin
git rebase origin/main

# 2. Squash multiple commits interactively:
git rebase -i HEAD~3
# Mark commits as 'squash' (or 's') to collapse them into an atomic commit

# 3. Safe undo on shared main branch using revert (creates a new inverse commit):
git checkout main
git pull origin main
git revert 4f8a91b -m 1 # Use -m 1 if reverting a merge commit
git push origin main    # Safe standard push without --force

# 4. Local cleanup using reset:
git reset --soft HEAD~1 # Undoes last commit, keeping all changes staged
```""",
    "short_en": """Merge joins branches preserving full history with a merge commit. Rebase replays commits linearly on top of upstream, rewriting hashes. Squash collapses multiple commits into a single atomic commit. Revert creates a new inverse commit to safely undo changes on shared branches without rewriting history, and Reset moves the branch pointer backward, altering history.""",
    "structured_en": """These five Git operations govern how branch histories are combined, rewritten, or reversed across engineering workflows.
Git merge integrates diverged branches by creating a 3-way merge commit with two parents. It guarantees complete historical accuracy and context, but creates a non-linear graph with merge commit clutter.
Git rebase replays local commits one by one on top of the target base branch, yielding a clean, linear commit history. Because it assigns new commit SHA hashes, it must never be run on public shared branches.
Git squash compresses a series of incremental commits into a single commit. It is standard in pull request merges to condense exploratory development into a single logical, bisect-friendly commit on main.
Git revert safely rolls back changes by creating a new forward commit containing the inverse diff. It preserves history immutability and causes no merge conflicts for teammates on shared branches.
Git reset adjusts the current branch HEAD backward in time. It rewrites branch history and requires forced pushes if already pushed to remotes, making it suitable strictly for local unshared work.""",
    "deep_senior_en": """In team Git architecture and continuous integration governance, choosing between merge, rebase, and squash impacts debugging, git bisect operations, and release auditability.
A linear commit history generated by git rebase or squash-and-merge makes automated regression hunting with git bisect remarkably fast and reliable. When messy merge commit graphs exist, automated bisect scripts frequently stumble into broken intermediary states where commits were merged half-baked. Squash-and-merge is preferred in many mobile teams because it reduces pull request clutter to a single cohesive feature commit linked to an issue tracker identifier. However, if a large pull request contains distinct architectural refactors, squashing them destroys the context of each separate change; an interactive rebase preserving several clean, atomic commits is superior in complex architectural migrations.
The golden rule of Git rebase is never rebasing a branch that has been published and shared with other engineers. Rebase rewrites commit SHA hashes. When collaborators pull a rebased branch, Git interprets their identical local commits as divergent, creating duplicate commits and painful merge conflicts.
Finally, when production incidents require rolling back defective merges, git revert is the mandatory tool. Reverting a merge commit with git revert -m 1 creates an inverse commit advancing history forward, allowing standard pushing without dangerous force-pushing. Teams configure branch protection rules in GitHub or GitLab that strictly disallow force pushes on trunk, enforcing non-destructive reverts by operational policy.""",
    "meta_ar": {
        "id": "CIC-04",
        "questionAr": "قارن بين أوامر Git الأساسية: merge و rebase و squash و revert و reset من حيث السلوك وتعديل التاريخ؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "المقارنة الهندسية بين دمج الفروع وإعادة البناء وتعديل التاريخ، وفهم خطورة rebase و reset على الفروع المشتركة، ودور squash و revert في نظافة التاريخ وتتبع الأخطاء بـ git bisect.",
        "concept_ar": "تحدد هذه العمليات الخمس كيفية دمج التعديلات وإعادة تشكيل التاريخ والتراجع عن الأخطاء في Git: أمر git merge يدمج فرعين بإنشاء Merge Commit يحمل أصلين، ويحافظ على التاريخ كاملاً ولكنه ينتج مخططاً غير خطي. أمر git rebase يعيد تشغيل كوميتات الفرع فوق قمة الفرع المستهدف لينتج تاريخاً خطياً نظيفاً، ولكنه يعيد كتابة الـ Hashes ويُحظر على الفروع المشتركة. أمر git squash يدمج عدة كوميتات صغيرة في كوميت واحد ذري ونظيف، وهو ممتاز لطلبات الدمج لتسهيل البحث بـ git bisect. أمر git revert يلغي تأثيراً سابقاً بإنشاء كوميت جديد للأمام يحمل التعديل العكسي، وهو آمن تماماً على الفروع المشتركة دون Force Push. وأمر git reset يحرك مؤشر HEAD للوراء ويمسح الكوميتات مما يجعله خطيراً ومقتصراً على العمل المحلي.",
        "walkthrough_ar": """أمثلة عملية توضح الفوارق بين أوامر Git في بيئة العمل اليومية:
```bash
# 1. إعادة بناء الفرع فوق main لتاريخ خطي نظيف قبل فتح الـ PR:
git checkout feature/checkout-flow
git fetch origin
git rebase origin/main

# 2. دمج الكوميتات تفاعلياً بـ Squash:
git rebase -i HEAD~3
# استبدل 'pick' بـ 'squash' للكوميتات الفرعية

# 3. التراجع الآمن عن كوميت معطوب على فرع main المشترك بـ Revert:
git checkout main
git pull origin main
git revert 4f8a91b -m 1
git push origin main # دفع اعتيادي آمن دون --force

# 4. إلغاء الكوميت محلياً مع إبقاء التعديلات مجهزة بـ Reset:
git reset --soft HEAD~1
```""",
        "why_it_matters_ar": "يحافظ على سلامة تاريخ المشروع المشترك، ويسهل اكتشاف وتحديد مصدر الانهيارات بـ git bisect، ويمنع كوارث تضارب الكود بين المطورين.",
        "worked_example_ar": "كوميت تسبب في كراش إنتاجي على فرع main؛ قام الفريق بعمل git revert للكوميت فتم التراجع عنه في دقيقة واحدة دون force push ودون التأثير على فروع الزملاء.",
        "trade_offs_ar": "استخدام rebase يمنح تاريخاً خطياً رائعاً ولكنه يتطلب حذراً كبيراً لعدم استخدامه على الفروع العامة؛ بينما merge يحافظ على السياق الكامل لكنه يزيد تشابك التاريخ.",
        "failure_modes_ar": "استخدام git rebase أو git reset --hard على فرع رئيسي مشترك ورفعه بـ force push، مما يعطل فروع زملائك ويولد كوميتات مكررة متضاربة.",
        "production_perspective_ar": "نلزم المطورين في سياسات GitHub بتفعيل Branch Protection لحظر force push على main، ونعتمد Squash and Merge لدمج الـ PRs في كوميت ذري واحد.",
        "how_to_answer_ar": "قارن كل أمر من حيث: إنشاء كوميت جديد، إعادة كتابة التاريخ، والحالة المثلى للاستخدام، مع التشديد على سلامة الفروع المشتركة وتفادي force push.",
        "talking_points_ar": "التاريخ الخطي مقابل المتشابك، مخاطر إعادة كتابة الـ Hashes، أمر git bisect، أمان git revert للأمام، واستخدام squash لطلبات الدمج.",
        "follow_ups_ar": "- **المحاور:** 'ما الخطر الأساسي من استخدام git rebase على فرع عام مشترك؟'\n  **المرشح:** 'يعيد rebase كتابة أرقام الـ Hashes للكوميتات؛ فعندما يقوم الزملاء بسحب الفرع، يعتبر Git كوميتاتهم المحلية السابقة مختلفة، مما ينتج كوميتات مكررة وتضاربات معقدة.'\n\n- **المحاور:** 'كيف يساعد Squash and Merge في تسريع عملية git bisect؟'\n  **المرشح:** 'يضمن أن كل كوميت على فرع main يمثل حالة متكاملة وقابلة للتجميع وتجتاز الاختبارات، بدلاً من التوقف عند كوميتات تجريبية مكسورة أثناء التتبع التلقائي.'",
        "self_check_ar": "هل قارنت بين الأوامر الخمسة بدقة وشرحت أثرها على التاريخ وحالات الاستخدام الآمنة؟",
        "references_ar": f"- [Pro Git Book: Branching and Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) — الفصل الرسمي لإعادة البناء والدمج في Git.\n- [Pro Git Book: Reset Demystified](https://git-scm.com/blog/2011/07/11/reset.html) — الشرح المرجعي العميق لفروق أوامر Reset و Revert.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """أمر merge يدمج الفروع مع الحفاظ على التاريخ الكامل بـ Merge Commit. أمر rebase يعيد تطبيق التعديلات خطياً فوق الفرع المستهدف ويعيد كتابة الـ Hashes. أمر squash يدمج عدة كوميتات في كوميت ذري واحد. أمر revert ينشئ كوميت جديد يعكس التعديل للتراجع الآمن على الفروع المشتركة، وأمر reset يحرك المؤشر للوراء ويمسح الكوميتات.""",
        "best_answer_ar": """تتحكم هذه العمليات الخمس في كيفية دمج تواريخ الفروع وإعادة تشكيلها أو التراجع عن التعديلات في بيئة العمل الجماعي.
يقوم أمر git merge بدمج الفروع المتشعبة عبر إنشاء كوميت دمج يربط بين أصلين؛ وهو ما يضمن توثيق التاريخ بدقة زمنية ولكنه ينتج رسماً بیانياً معقداً ومليئاً بكوميتات الدمج.
في المقابل، يعيد أمر git rebase تطبيق تعديلات الفرع المحلي سطراً بسطر فوق قمة الفرع المستهدف، مما يمنح المشروع تاريخاً خطياً فائق النظافة؛ ولكنه يعيد كتابة البصمات التشفيرية للكوميتات، ولذلك يُحظر استخدامه تماماً على الفروع العامة المشتركة.
ويقوم أمر git squash بدمج سلسلة من الكوميتات التجريبية الصغيرة في كوميت واحد ذري ومترابط؛ وهو الخيار المفضل في طلبات الدمج للحفاظ على استقرار الفرع الرئيسي وسهولة تتبعه بـ git bisect.
أما أمر git revert فهو الوسيلة الآمنة للتراجع عن الأخطاء على الفروع المشتركة؛ حيث ينشئ كوميت جديد للأمام يعكس التغييرات دون تعديل التاريخ أو طلب دفع بالقوة. وأخيراً يرجع أمر git reset مؤشر الفرع إلى الوراء لمسح الكوميتات، وهو مخصص حصرياً للتعديلات المحلية غير المنشورة.""",
        "deep_answer_ar": """من منظور حوكمة إدارة الأكواد وهندسة التسليم المستمر، يؤثر الاختيار بين هذه الأوامر تأثيراً مباشراً على عمليات التدقيق البرمجي والقدرة على عزل الأخطاء الإنتاجية بسرعة.
إن التاريخ الخطي الذي تنتجه أدوات rebase و squash and merge يجعل استخدام أداة git bisect دقيقاً وفعالاً للغاية عند البحث عن الكوميت المتسبب في تراجع الأداء؛ فعند وجود تاريخ متشابك مليء بكوميتات الدمج العشوائية، تتوقف خوارزمية البحث الثنائي عند كوميتات وسيطة غير مستقرة تعطل عملية الاختبار التلقائي. ومع ذلك، نراعي في طلبات الدمج المعقدة ألا يؤدي الدمج بـ squash إلى تدمير سياق التعديلات المعمارية الكبيرة؛ فإذا كان التعديل يشمل عدة مراحل منطقية منفصلة، يفضل استخدام rebase تفاعلي محلي يختصرها في كوميتين أو ثلاثة ذات معنى واضح.
وتظل القاعدة الذهبية في Git هي حظر إعادة كتابة تاريخ الفروع المشتركة نهائياً؛ فاستخدام rebase أو reset ثم الدفع بالقوة force push على فرع رئيسي يربك بيئات عمل المطورين الآخرين ويتسبب في ظهور كوميتات مكررة وتضاربات تلتهم ساعات طويلة من وقت الفريق.
ولذلك، تفرض الفرق الاحترافية قيود Branch Protection على الفروع الحساسة لمنع الدفع بالقوة، وتلزم المهندسين باستخدام git revert عند ظهور أي خلل إنتاجي؛ حيث يولد أمراً عكسياً يتقدم بالتاريخ للأمام ويوثق سبب التراجع بكل شفافية لأغراض الامتثال والأمان."""
    }
}

# ==========================================
# CIC-05: Compare git reset --soft versus --hard.
# ==========================================
DATA["CIC-05"] = {
    "concept_en": """Understanding Git reset variants requires analyzing how they manipulate Git's three fundamental architecture trees:
- Git's Three Trees:
  1. HEAD: Pointer tracking the latest commit snapshot of the current branch.
  2. Index (Staging Area): The proposed next commit snapshot prepared via git add.
  3. Working Tree: The active filesystem directory containing files on disk.
- Reset Modes Comparison:
  - git reset --soft <commit>:
    * Updates the HEAD reference to point to the designated commit.
    * Leaves both the Index and the Working Tree completely untouched.
    * Result: All changes introduced after that commit remain staged in the Index, ready to be immediately re-committed. Ideal for amending messages, combining local commits, or restructuring history before pushing.
  - git reset --mixed <commit> (Default behavior):
    * Updates HEAD and resets the Index to match the target commit snapshot.
    * Leaves the Working Tree files on disk untouched.
    * Result: Undone changes remain intact in your files but become unstaged modifications. Ideal for splitting commits or re-staging files selectively.
  - git reset --hard <commit>:
    * Updates HEAD, resets the Index, and forces the Working Tree to match the target commit snapshot.
    * Destructive Operation: Obliterates all tracked changes in files on disk. Uncommitted changes cannot be recovered.
- Disaster Recovery via Reflog:
  - If a commit was previously committed, git reflog retains its SHA identifier. Running git reset --hard <previous-sha> safely recovers lost commits.""",
    "walkthrough_en": """Hands-on CLI scenarios comparing soft, mixed, and hard resets:
```bash
# Scenario 1: Undo accidental commit, preserve changes as staged to edit commit message:
git commit -m "wip payment featur"
git reset --soft HEAD~1
git status # Shows: Changes to be committed (Staged)
git commit -m "feat(payment): integrate biometric confirmation"

# Scenario 2: Split last commit into two atomic commits (Default Mixed Reset):
git reset --mixed HEAD~1
git status # Shows: Changes not staged for commit
git add PaymentService.kt && git commit -m "feat: add payment service"
git add PaymentTest.kt && git commit -m "test: add payment unit tests"

# Scenario 3: Discard bad experiment completely and restore clean main branch state:
git reset --hard origin/main

# Scenario 4: Disaster recovery after accidental hard reset using git reflog:
git reflog # Locate commit SHA before the reset, e.g. 7c8d9e0
git reset --hard 7c8d9e0 # Restores lost commits completely!
```""",
    "short_en": """Git reset --soft moves the HEAD pointer to a target commit while keeping both the Index and Working Tree intact, leaving changes staged for a new commit. Git reset --mixed moves HEAD and resets the Index, leaving changes unstaged on disk. Git reset --hard resets HEAD, Index, and Working Tree, permanently discarding all tracked changes.""",
    "structured_en": """The difference between Git reset modes lies in how they interact with Git's three fundamental architecture trees: the HEAD pointer, the Index staging area, and the Working Tree.
When executing git reset --soft, Git moves the HEAD pointer backward to the specified commit, but leaves both the Index and the Working Tree unmodified. As a result, all modifications from the undone commits remain staged, making it the ideal command for amending commit messages, adding missing files, or squashing recent commits locally before opening a pull request.
In contrast, git reset --mixed, which is the default reset mode, moves HEAD and clears the Index to match the target commit, but leaves your Working Tree files untouched on disk. The modifications become unstaged, allowing developers to review differences and re-stage them into smaller, atomic commits.
Finally, git reset --hard is a destructive operation that updates HEAD, resets the Index, and forces the Working Tree files to match the target commit, completely obliterating uncommitted changes. However, if committed work was accidentally wiped, it can be recovered using git reflog.""",
    "deep_senior_en": """From a version control architecture and developer safety perspective, mastering reset mechanics prevents catastrophic data loss and clarifies workspace synchronization.
Git manages data across three decoupled layers: HEAD records the committed object graph, the Index stages tree objects for the next snapshot, and the Working Tree holds the local OS filesystem state. Understanding how reset flags boundary these layers enables surgical local modifications without fear.
Using git reset --soft HEAD~1 is the cleanest method to rewrite local commit history. It rolls back the branch pointer while preserving all edited files in the staging area. This allows engineers to split, combine, or re-label commits before publishing.
When employing git reset --hard, engineers must understand what is recoverable and what is lost forever. If modifications were previously committed, Git's content-addressable object store retains the commit objects even after the branch pointer moves away. Running git reflog exposes the history of HEAD movements, allowing developers to locate the orphaned commit SHA and restore it via git reset --hard <sha>. However, if a developer had uncommitted, untracked, or dirty working tree changes when executing git reset --hard, those uncommitted diffs never existed in Git's object database and are destroyed permanently.
Furthermore, git reset --hard only alters tracked files; newly created untracked files are ignored. In continuous integration runners where clean state is mandatory between builds, teams run git reset --hard HEAD followed by git clean -ffdx to purge untracked files, ignored compiler caches, and build outputs.""",
    "meta_ar": {
        "id": "CIC-05",
        "questionAr": "قارن بين git reset --soft و git reset --hard (بالإضافة إلى --mixed) وتأثيرها على HEAD والـ Index وبيئة العمل؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الأشجار الثلاثة في Git (HEAD و Index و Working Tree)، والفرق الدقيق بين خيارات reset (soft و mixed و hard)، وآلية استرجاع الكود المحذوف عبر git reflog.",
        "concept_ar": "يرتكز الاختلاف بين أوضاع git reset على كيفية تعاملها مع أشجار Git الثلاث: مؤشر HEAD الذي يشير إلى آخر كوميت، ومنطقة التجهيز Index التي تحتوي على الملفات المجهزة للكوميت (Staged)، وبيئة العمل Working Tree التي تمثل الملفات الفعلية على القرص الصلب. أمر git reset --soft يحرك مؤشر HEAD للوراء فقط ويترك الـ Index والـ Working Tree دون مساس، فتظل التعديلات مجهزة للكوميت (Staged) وهو مثالي لتعديل رسائل الكوميت. أمر git reset --mixed (الوضع الافتراضي) يحرك HEAD ويعيد ضبط الـ Index ليطابق الكوميت لكنه يترك الملفات على القرص، فتتحول التعديلات إلى غير مجهزة (Unstaged). أما أمر git reset --hard فيعيد ضبط HEAD والـ Index والـ Working Tree معاً، مما يمسح كافة التعديلات من القرص نهائياً. وإذا تم مسح كوميتات مسجلة بالخطأ، يمكن استعادتها عبر git reflog.",
        "walkthrough_ar": """سيناريوهات عملية توضح متى تستخدم كل نوع من أنواع الـ Reset:
```bash
# سيناريو 1: التراجع عن كوميت مع إبقاء التعديلات مجهزة لتعديل الرسالة:
git commit -m "wip payment featur"
git reset --soft HEAD~1
git commit -m "feat(payment): integrate biometric confirmation"

# سيناريو 2: فصل التعديلات لكوميتين منفصلين (Mixed Reset الافتراضي):
git reset --mixed HEAD~1
git add PaymentService.kt && git commit -m "feat: add payment service"
git add PaymentTest.kt && git commit -m "test: add payment tests"

# سيناريو 3: التخلص التام من تجربة فاشلة والعودة لكود main النظيف:
git reset --hard origin/main

# استرجاع كوميت محذوف بالخطأ بـ reflog:
git reflog # تحديد الـ Hash القديم e.g. 7c8d9e0
git reset --hard 7c8d9e0 # استعادة الكود بالكامل
```""",
        "why_it_matters_ar": "يمنع فقدان الأكواد البرمجية أثناء تعديل التاريخ محلياً، ويوفر أداة دقيقة لإعادة تنظيم الكوميتات قبل تقديم طلبات الدمج.",
        "worked_example_ar": "مطور نفذ git reset --hard HEAD~3 بالخطأ ومسح عمل يوم كامل؛ باستخدام git reflog تم العثور على البصمة التشفيرية السابقة واستعادة الكود في ثوانٍ معدودة.",
        "trade_offs_ar": "أمر --soft يحافظ على حالة التجهيز لسهولة إعادة الرفع، بينما --mixed يتيح مراجعة الملفات وتجهيزها تدريجياً، وأمر --hard خطير وتدميري ولا رجعة فيه إلا للكوميتات المسجلة.",
        "failure_modes_ar": "تنفيذ git reset --hard في وجود تعديلات محلية غير مسجلة بكوميت، مما يؤدي لحذفها من القرص تماماً واستحالة استعادتها حتى بـ reflog.",
        "production_perspective_ar": "في سيرفرات الـ CI ذاتية الاستضافة، نشغل git reset --hard HEAD مع git clean -ffdx لضمان تنظيف بيئة العمل بالكامل من مخرجات البناء السابقة قبل بدء أي مهمة.",
        "how_to_answer_ar": "ابدأ بشرح الأشجار الثلاثة (HEAD و Index و Working Tree)، ثم قارن بين soft و mixed و hard بدقة، واختم بذكر ميزة الأمان العظيمة git reflog.",
        "talking_points_ar": "شجرة Git الثلاثية، حالة التجهيز Staged مقابل Unstaged، خطورة --hard، استعادة الكود بـ git reflog، وتطهير بيئات الـ CI بـ git clean.",
        "follow_ups_ar": "- **المحاور:** 'هل يمكن استعادة الكود بعد تنفيذ أمر git reset --hard بالخطأ؟'\n  **المرشح:** 'نعم، بشرط أن يكون الكود قد تم تسجيله في كوميت سابق؛ حيث نحصل على رقم البصمة من سجل الحركات المحلي git reflog ونعيد المؤشر إليه؛ أما التعديلات غير المسجلة بكوميت فتفقد نهائياً.'\n\n- **المحاور:** 'ما هي الحالة المثالية لاستخدام أمر git reset --soft HEAD~1؟'\n  **المرشح:** 'عندما تقوم بعمل كوميت محلي وتكتشف خطأ إملائياً في الرسالة أو تنسى إضافة ملف، فتتراجع عن الكوميت مع بقاء كافة الملفات مجهزة فورياً لإعادة تسجيلها بشكل صحيح.'",
        "self_check_ar": "هل شرحت أثر كل نوع على الأشجار الثلاثة وحالات الاستخدام واسترجاع الكود بـ reflog؟",
        "references_ar": f"- [Pro Git Book: Git Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified) — الدليل الشامل لفهم آلية عمل Reset وأشجار Git الثلاث.\n- [Git Documentation: git-reflog](https://git-scm.com/docs/git-reflog) — توثيق أداة استعادة الكوميتات المفقودة عبر سجل المراجع.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """أمر git reset --soft يحرك مؤشر HEAD إلى الكوميت المحدد مع بقاء التعديلات مجهزة في الـ Index والملفات سليمة على القرص. أمر git reset --mixed يعيد ضبط الـ Index فتصبح التعديلات غير مجهزة لكنها محفوظة على القرص. أما أمر git reset --hard فيعيد ضبط HEAD والـ Index وملفات القرص مما يحذف كافة التعديلات المسجلة وغير المسجلة نهائياً.""",
        "best_answer_ar": """يرتكز الفارق بين أوضاع أمر git reset على كيفية تفاعلها مع طبقات Git المعمارية الثلاث: مؤشر HEAD، ومنطقة التجهيز Index، وبيئة العمل الفعلية على القرص Working Tree.
عند تنفيذ أمر git reset --soft، يقوم Git بتحريك مؤشر HEAD للوراء إلى الكوميت المطلوب، ولكنه يترك كلاً من الـ Index والملفات على القرص دون أي تغيير. ونتيجة لذلك، تظل كافة التعديلات في حالة مجهزة Staged، مما يجعله الخيار المثالي لتعديل رسالة الكوميت أو إضافة ملفات منسية أو دمج عدة كوميتات محلية قبل مشاركتها.
في المقابل، فإن الوضع الافتراضي git reset --mixed يحرك مؤشر HEAD ويعيد تعيين الـ Index ليطابق الكوميت المستهدف، ولكنه يحافظ على ملفاتك على القرص الصلب؛ فتتحول التعديلات إلى حالة غير مجهزة Unstaged، مما يتيح لك مراجعة الفروق وتجهيز الملفات بشكل تدريجي في كوميتات ذرية منفصلة.
أما أمر git reset --hard فهو عملية تدميرية تقوم بتحديث HEAD وتفريغ الـ Index وإجبار ملفات القرص الصلب على مطابقة الكوميت القديم، مما يمسح كافة التعديلات غير المدمجة تماماً؛ ومع ذلك، إذا كانت التعديلات قد سُجلت بكوميت سابق، يمكن استرجاعها عبر أداة git reflog.""",
        "deep_answer_ar": """من منظور البنية التحتية لإدارة النسخ وأمان المطورين، يمثل فهم حدود أوضاع الـ Reset الفارق بين التعديل الهندسي الآمن وفقدان العمل البرمجي نهائياً.
يعتمد Git على نموذج بيانات يفصل بذكاء بين سجل الكائنات المؤرشفة HEAD، والشجرة المؤقتة المجهزة للقطة التالية Index، والملفات المحررة على نظام التشغيل Working Tree.
وعند استخدام خيار soft، نتمكن من إعادة كتابة التاريخ المحلي بسلاسة فائقة؛ حيث نتراجع عن الكوميت مع بقاء التعديلات في الذاكرة التجهيزية، مما يتيح إعادة صياغة رسائل الكوميت وفق معايير Conventional Commits قبل رفعها لمراجعة الكود.
أما عند استخدام أمر git reset --hard، فيجب التمييز بدقة بين ما يمكن استعادته وما يضيع إلى الأبد. فإذا كانت التعديلات قد خضعت لكوميت واحد على الأقل، فإن قاعدة بيانات Git تحفظ الكائن في سجلاتها حتى لو فُقد المؤشر؛ وباستخدام أمر git reflog، نستعرض تاريخ تحركات مؤشر HEAD ونسترجع الـ Hash القديم ونلغي الحذف تماماً. ولكن إذا كانت هناك تعديلات محلية قيد الكتابة لم يسبق تسجيلها في أي كوميت، فإن تنفيذ hard reset يمسحها من القرص الصلب نهائياً ولا تستطيع أي أداة استعادتها.
وبالإضافة إلى ذلك، يقتصر تأثير hard reset على الملفات المتابعة فقط دون الملفات الجديدة غير المتابعة؛ ولذلك نلزم خطوط الـ CI ذاتية الاستضافة بتشغيل git reset --hard متبوعاً بأمر git clean -ffdx لمسح الملفات غير المتابعة ومخلفات التجميع السابقة لضمان بيئة بناء نظيفة مئة بالمائة."""
    }
}

# ==========================================
# CIC-06: When is revert safer than reset on shared branches?
# ==========================================
DATA["CIC-06"] = {
    "concept_en": """On shared collaborative branches such as main, develop, or release tracks, git revert is the only non-destructive rollback strategy:
- Why git reset Fails on Shared Branches:
  1. Rewriting Distributed History: Resetting rewinds the branch pointer backward. Because remote repositories reject non-fast-forward updates, the developer must execute git push --force.
  2. The Ghost Merge Dilemma: Every collaborator whose local machine has pulled the branch still retains the erased commits. The next time any teammate pulls or merges, Git identifies those local commits as new incoming work and re-introduces the buggy code back into the mainline.
  3. Destruction of the Audit Log: Force-pushing overwrites previous commits, erasing author attribution, timestamps, and the historical justification required by enterprise compliance (SOC2, ISO 27001).
- Why git revert is Architecturally Safe:
  - Forward-Only Evolution: Creates a brand-new commit containing the exact inverse diff of the target commit.
  - Standard Non-Destructive Push: Advances the branch forward; collaborators pull smoothly without diverged histories or conflicts.
  - Complete Provenance: Transparently records that an issue occurred and was intentionally rolled back.
- Handling Merge Commit Reverts:
  - Reverting a merge commit requires the -m 1 flag to designate which parent branch represents the mainline baseline.
  - Re-introducing the reverted feature later requires reverting the revert commit (git revert <revert-sha>) before merging new fixes.""",
    "walkthrough_en": """Demonstrating safe emergency rollback on a shared release branch using revert:
```bash
# ❌ DANGEROUS ANTI-PATTERN: Never reset and force-push on shared branches!
# git checkout main && git reset --hard HEAD~1 && git push origin main --force

# ✅ SAFE ENGINEERING PRACTICE: Revert forward on shared branches:
git checkout main
git pull origin main

# 1. Inspect recent commit logs to identify the culprit commit SHA:
git log --oneline -n 5
# Example: 9a8b7c6 "feat: integrate experimental payment SDK"

# 2. Generate an inverse commit rolling back the defective changes:
git revert 9a8b7c6 -m 1 # Use -m 1 if the target was a merge commit

# 3. Push the new forward commit safely to the remote repository:
git push origin main # Clean standard push, zero force required!

# 4. Re-introducing the feature later after fixing the underlying bug:
git checkout feature/payment-sdk-fix
git revert <revert-commit-sha> # Reverts the revert, restoring the original diff!
```""",
    "short_en": """Git revert is safer on shared branches because it creates a new forward-moving commit that inverts the target changes without rewriting history. Git reset rewrites branch history and requires force-pushing, which corrupts teammates' local branches, causes ghost commit re-merges, and destroys enterprise compliance audit trails.""",
    "structured_en": """On shared collaborative branches like main or release stabilization branches, git revert is the only safe undo mechanism for three core architectural reasons.
First, git revert creates a forward-moving commit that records the exact inverse diff of the flawed commit. Because the branch tip advances forward naturally, it can be pushed with a standard git push without requiring destructive force pushes.
Second, git reset corrupts teammate synchronization. If a developer resets a shared branch and force-pushes, any collaborator whose local clone still holds the erased commit will unknowingly re-introduce it the next time they pull or merge, causing ghost bug resuscitations and severe merge conflicts.
Third, enterprise compliance frameworks mandate an immutable audit trail. Git revert transparently documents that a feature was committed, caused an issue, and was subsequently rolled back, preserving full engineering attribution.
When reverting merge commits, developers pass the -m 1 flag to explicitly designate the mainline parent against which to calculate the inverse diff.""",
    "deep_senior_en": """From an engineering governance and continuous delivery perspective, managing rollbacks on shared branches demands strict adherence to non-destructive version control principles.
When a production regression escapes into a shared trunk, developers under stress often reach for git reset to erase the bad commit. On a local branch, resetting is harmless. On a shared branch cloned by dozens of developers and continuous integration workers, force-pushing a rewritten history wreaks havoc. When teammates execute git pull, Git identifies their local commits as divergent from the remote branch, prompting merge conflicts or triggering silent re-merges that resurrect the defective code into production.
Employing git revert sidesteps these synchronization hazards completely. By calculating an inverse patch and appending a new commit to the branch tip, the operation is completely transparent to continuous integration runners and teammates. Collaborators pull the fix smoothly without re-basing local work.
However, senior engineers must navigate a subtle trap when reverting merge commits. A merge commit possesses multiple parent commits. When running git revert, Git throws an error unless provided with the -m flag. Passing -m 1 instructs Git that the first parent, typically the mainline trunk, is the baseline to retain.
Furthermore, if the developer later resolves the root cause on the original feature branch and attempts to re-merge it into main, Git inspects the commit graph, determines that those commits already exist in history, and silently refuses to re-apply the feature diff. To safely re-introduce the feature, the team must execute git revert on the revert commit itself, restoring the original diff into the branch before merging subsequent bugfixes.""",
    "meta_ar": {
        "id": "CIC-06",
        "questionAr": "لماذا يعتبر أمر git revert أكثر أماناً من git reset على الفروع المشتركة (Shared Branches)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم خطورة إعادة كتابة التاريخ على الفروع المشتركة، وظاهرة عودة الكود المحذوف (Ghost Merges)، والحفاظ على سجل التدقيق التشفيري، ومعالجة التراجع عن الـ Merge Commits بخيار -m 1.",
        "concept_ar": "يعتبر git revert الخيار الآمن والوحيد للتراجع على الفروع المشتركة (مثل main و develop وفروع الإصدار) لثلاثة أسباب جوهرية: أولاً، أمر revert يتقدم بالتاريخ للأمام؛ حيث ينشئ كوميت جديد تماماً يحتوي على التعديل العكسي، مما يتيح رفعه للـ Remote بأمر push عادي دون الحاجة لـ force push. ثانياً، استخدام reset يتطلب force push مما يكسر تزامن فروع الزملاء؛ فعندما يقوم زميل بعمل pull يعيد Git دمج الكوميت المحذوف تلقائياً (Ghost Merge) ويعود الكراش للإنتاج مجدداً. ثالثاً، يحافظ revert على سجل التدقيق وسلسلة الامتثال الأمني بمعرفة من أضاف الكود وسبب التراجع عنه. وعند التراجع عن Merge Commit، نستخدم خيار -m 1 لتحديد الفرع الأصلي لحساب الفرق العكسي.",
        "walkthrough_ar": """سيناريو عملي يوضح التراجع الآمن عن عطل إنتاجي على الفرع المشترك:
```bash
# ❌ السيناريو الخاطئ والمدمر (حظر الـ Reset على الفروع المشتركة):
# git reset --hard HEAD~1 && git push origin main --force

# ✅ السيناريو الهندسي الآمن بـ Revert:
git checkout main
git pull origin main

# 1. تحديد الكوميت المعطوب من السجل:
git log --oneline -n 3 # e.g. 9a8b7c6 "feat: add payment gateway"

# 2. إنشاء كوميت عكسي يلغي التغيير مع تحديد الأصل إذا كان Merge Commit:
git revert 9a8b7c6 -m 1

# 3. دفع التعديل للأمام بسلاسة وبدون أي force push:
git push origin main

# 4. إعادة الميزة لاحقاً بعد إصلاحها عبر عكس الـ Revert:
git checkout feature/fix-payment
git revert <revert-commit-sha> # إعادة الكود السابق للعمل
```""",
        "why_it_matters_ar": "يحمي بيئة العمل الجماعي من تضارب الفروع والكوميتات المكررة، ويضمن الشفافية والامتثال في تتبع التعديلات والقرارات الهندسية.",
        "worked_example_ar": "ميزة دمجت في main وتسببت في عطل؛ تم استخدام git revert فتم حل المشكلة وتحديث سيرفرات الـ CI وأجهزة الفريق فورياً دون أي تعارض أو force push.",
        "trade_offs_ar": "أمر revert يضيف كوميت إضافياً في التاريخ ولكنه يحافظ على الأمان والشفافية؛ بينما reset يخفي الخطأ تماماً لكنه يدمر تزامن الفريق.",
        "failure_modes_ar": "استخدام git reset --hard على main والدفع بالقوة، مما يمسح أعمال الزملاء، أو محاولة إعادة دمج فرع تم عمل revert له دون عكس كوميت الـ revert أولاً.",
        "production_perspective_ar": "نفرض في سياسات حماية الفروع حظر الدفع بالقوة (Disallow Force Push) على فروع الإنتاج، ونلزم الفرق بفتح Pull Request يحتوي على git revert للأعطال.",
        "how_to_answer_ar": "اشرح ثلاث نقاط رئيسية: حركة التاريخ للأمام وتجنب force push، ظاهرة Ghost Merges عند الزملاء، والحفاظ على سجل التدقيق والامتثال، واذكر كيفية التعامل مع Merge Commits.",
        "talking_points_ar": "التاريخ التطلعي للأمام، مخاطر force push، ظاهرة Ghost Merges، سجل التدقيق والامتثال، وخيار -m 1 عند التراجع عن دمج الفروع.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث إذا قمت بعمل git reset ودفع بالقوة على فرع main المشترك؟'\n  **المرشح:** 'ستنكسر بيئة عمل كل المطورين الذين سحبوا النسخة السابقة؛ وعندما يقوم أحدهم بالدمج أو الرفع مجدداً، سيرى Git أن الكوميت المحذوف موجود محلياً فيعيده للفرع الرئيسي وتعود المشكلة للحياة.'\n\n- **المحاور:** 'لماذا نحتاج لتمرير خيار -m 1 عند التراجع عن Merge Commit؟'\n  **المرشح:** 'لأن كوميت الدمج يمتلك أصلين مختلفين، فيعجز Git عن معرفة أي مسار يريد المطور اعتماده كخط أساس؛ وخيار -m 1 يحدد الأصل الأول وهو فرع main لحساب التعديل العكسي ضده.'",
        "self_check_ar": "هل بينت مخاطر الـ reset وظاهرة الـ Ghost Merges وأمان الـ revert للأمام والتعامل مع خيار -m 1؟",
        "references_ar": f"- [Pro Git Book: Undoing Things - git revert](https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things) — الدليل الرسمي لآليات التراجع الآمن في Git.\n- [GitHub Docs: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches) — توثيق حماية الفروع المشتركة وحظر Force Push.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """أمر git revert أكثر أماناً على الفروع المشتركة لأنه ينشئ كوميت جديد للأمام يعكس التغييرات دون العبث بالتاريخ أو الحاجة لـ force push. بينما أمر git reset يعيد كتابة التاريخ ويتطلب دفعاً بالقوة مما يكسر فروع الزملاء ويؤدي لعودة الكود المعطوب تلقائياً عبر ظاهرة Ghost Merges ويدمر سجل التدقيق الأمني.""",
        "best_answer_ar": """على الفروع المشتركة مثل main وفروع إطلاق الإصدارات، يعد أمر git revert الآلية الهندسية الوحيدة الآمنة للتراجع عن الأخطاء لثلاثة أسباب جوهرية.
أولاً، يعمل أمر git revert بطريقة تطلعية للأمام؛ حيث ينشئ كوميت جديد يحتوي على الفروق العكسية للكوميت المعطوب، وبما أن مؤشر الفرع يتقدم للأمام، يمكن دفعه للسيرفر عبر أمر git push اعتيادي دون الحاجة للدفع بالقوة force push.
ثانياً، يحمي تزامن الفريق ويمنع ظاهرة عودة الأخطاء؛ فعند استخدام reset مع الدفع بالقوة، يظل الكوميت الممسوح موجوداً على أجهزة الزملاء، وعندما يقوم أحدهم بالدمج أو الرفع يعيد Git إدماج الكوميت المحذوف وتعود المشكلة مجدداً للفرع الرئيسي.
ثالثاً، يحافظ أمر revert على سجل التدقيق الأمني المطلوب في المؤسسات الكبرى، موثقاً من قام بالتعديل ومتى حدث التراجع وسببه. وعند التراجع عن كوميت دمج يربط بين فرعين، نمرر خيار -m 1 لتوجيه Git لاعتماد الفرع الأصلي الرئيسي كخط أساس لحساب التعديل العكسي.""",
        "deep_answer_ar": """من منظور حوكمة هندسة البرمجيات والتسليم المستمر، يمثل التعامل مع الأعطال على الفروع المشتركة اختباراً حقيقياً لنضج ثقافة الفريق الهندسية.
عندما يتسبب كود مدمج في انحدار إنتاجي خطير، يميل بعض المطورين تحت الضغط لاستخدام git reset لمسح الكوميت من التاريخ ظناً منهم أن ذلك ينهي المشكلة. وفي الفروع المحلية الخاصة، لا بأس بذلك؛ أما على الفروع المشتركة، فإن مسح الكوميت يتطلب دفعاً مدمراً بالقوة force push ينسف تسلسل التاريخ لجميع المهندسين وسيرفرات الـ CI.
وعندما يسحب المطورون التحديثات، يعتبر Git أن فروعهم المحلية تمتلك كوداً أحدث من الفرع البعيد، فيقوم بدمج الكوميت الممسوح تلقائياً فيما يعرف بـ Ghost Merges، مما يعيد الخطأ للإنتاج بصمت بعد ساعات من مسحه.
ويحل أمر git revert هذه المعضلة الهندسية بالكامل؛ فهو لا يحذف أي كائن من قاعدة بيانات Git، بل يحسب الفارق العكسي ويضيفه ككوميت جديد في قمة الفرع، مما يجعل التحديث ينساب بسلاسة إلى أجهزة الفريق وسيرفرات البناء دون أي تعارضات أو حاجة لـ rebase محلي.
ومع ذلك، يواجه كبار المهندسين فخاً شهيراً عند التراجع عن كوميتات الدمج؛ فإذا حاول المطور لاحقاً إعادة دمج نفس فرع الميزة بعد إصلاح الخلل، سيرفض Git تطبيق الكود لأن كوميتات الميزة مسجلة في التاريخ كأكواد تم دمجها مسبقاً. ولحل هذه الإشكالية، يجب تنفيذ git revert على كوميت التراجع نفسه أولاً لإعادة إحياء الكود الأصلي، ثم دمج الإصلاحات الجديدة فوقه بسلاسة."""
    }
}

# ==========================================
# CIC-07: What are git stash, cherry-pick, and fork?
# ==========================================
DATA["CIC-07"] = {
    "concept_en": """Advanced Git mechanisms solve context switching, isolated patch backporting, and decentralized contribution boundaries:
- Detailed Breakdown of Operations:
  1. git stash:
     - Shelves uncommitted modifications (both staged and unstaged files) into an internal LIFO stack (stash@{0}), resetting the Working Tree to match the clean HEAD commit.
     - Primary Use Case: Urgent context switching (e.g. investigating an immediate production crash on another branch while midway through feature development).
     - Essential Flag: git stash -u (or --include-untracked) to ensure newly added, untracked files are captured alongside tracked edits.
     - Volatility Risk: Stashes are strictly local and unbacked; leaving large refactors in stash risks unrecoverable data loss during machine failure.
  2. git cherry-pick <commit-sha>:
     - Extracts the precise diff introduced by a designated commit on any branch and applies it as a brand-new commit on the currently active branch.
     - Primary Use Case: Hotfix backporting (e.g. applying an emergency security patch committed to main onto an active release/2.4 maintenance branch without merging unready features).
     - Best Practice: Use git cherry-pick -x to append origin commit metadata and preserve auditability.
  3. Fork:
     - A server-side clone of a remote repository hosted under an independent user or organization account on GitHub/GitLab.
     - Primary Use Case: Open-source collaboration and enterprise contractor boundaries where external contributors lack direct write permissions and submit contributions via pull requests across forks.""",
    "walkthrough_en": """Hands-on CLI usage for stash, cherry-pick, and fork synchronization:
```bash
# 1. Stash dirty workspace including untracked files with a descriptive message:
git stash push -u -m "WIP: biometric card tokenization"
git checkout hotfix/crash-fix
# ... resolve hotfix, commit, and push ...
git checkout feature/biometric
git stash pop # Restores files and removes them from the stash stack

# 2. Backport a hotfix commit from main to release-v1.4 using cherry-pick:
git checkout release/v1.4
git log origin/main --oneline -n 3 # Locate target commit SHA, e.g. c8d9e0f
git cherry-pick -x c8d9e0f # -x records original commit hash in commit message
git push origin release/v1.4

# 3. Synchronize a local fork with upstream canonical repository:
git remote add upstream https://github.com/organization/android-core.git
git fetch upstream
git checkout main
git merge upstream/main
```""",
    "short_en": """Git stash shelves uncommitted changes to allow clean branch switching for urgent tasks. Git cherry-pick extracts and applies a specific commit by hash from another branch onto the current branch without merging the full branch. A Fork is a server-side repository copy enabling external contributors to propose changes via pull requests without direct push access.""",
    "structured_en": """These three Git tools solve distinct workflow isolation and collaboration challenges across engineering teams.
Git stash temporarily shelves uncommitted local modifications, both staged and unstaged, onto an internal stack and resets the working directory to clean HEAD. It is essential for rapid context switching, such as interrupting feature development to investigate an emergency hotfix. Using the include-untracked flag guarantees newly created files are also preserved.
Git cherry-pick extracts the exact diff from a designated commit on another branch and applies it as a brand-new commit on the current branch. It is primarily used for backporting bug fixes from the main trunk onto active release or maintenance branches without pulling in unreleased features.
A Fork is a server-side clone of a repository created under an independent user or organization account on platforms like GitHub. It provides a clean security boundary for open-source projects and external contractors who lack direct repository write permissions, allowing them to push changes to their fork and submit cross-repository pull requests to the upstream repository.""",
    "deep_senior_en": """From a version control governance and release engineering perspective, stash, cherry-pick, and forks introduce operational nuances that require disciplined usage.
While git stash is convenient for short context switches, treating it as a long-term storage mechanism is dangerous. Stashes reside exclusively on the developer's local hard drive and are not backed up to remote servers. If a machine crashes or a developer runs hard clean commands, uncommitted stashed work can be lost forever. Mature teams establish a convention where multi-day exploratory work is committed and pushed to a remote draft branch rather than parked in a local stash.
When executing git cherry-pick, senior engineers guard against duplicate commit hazards. Applying a commit from main onto a release branch creates an identical diff with a distinct SHA hash. If that release branch is eventually merged back into main, Git must reconcile two commits sharing identical code changes, which can trigger confusing conflict resolutions. We always execute git cherry-pick with the -x flag, which automatically appends a reference to the source commit SHA in the commit message, preserving provenance and simplifying future release auditing.
Finally, managing forked workflows at scale requires automated upstream synchronization. In large organizations utilizing vendor forks, drift between the internal fork and upstream repositories quickly compounds into painful merge conflicts. Teams configure automated scheduled workflows that fetch upstream changes and rebase internal tracks continuously, ensuring external dependencies and forks remain closely aligned with the canonical codebase.""",
    "meta_ar": {
        "id": "CIC-07",
        "questionAr": "ما هي أدوات Git المتقدمة: git stash و git cherry-pick ومفهوم الـ Fork ومتى يُستخدم كل منها؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم حفظ العمل المؤقت بـ stash وإدارة الملفات غير المتابعة (-u)، واستخدام cherry-pick لنقل الإصلاحات بين الفروع وخيار -x، ومفهوم الـ Fork في المساهمات الخارجية ومزامنة الـ Upstream.",
        "concept_ar": "تحل هذه الأدوات الثلاث مشكلات التبديل السريع ونقل الإصلاحات وحدود الصلاحيات: أمر git stash يحفظ التعديلات غير المسجلة مؤقتاً في مكدس محلي ويعيد بيئة العمل نظيفة للتبديل السريع بين المهام؛ ويجب استخدام خيار -u لحفظ الملفات الجديدة غير المتابعة. أمر git cherry-pick يتيح نسخ كوميت محدد ببصمته التشفيرية من أي فرع وتطبيقه ككوميت جديد على الفرع الحالي؛ ويستخدم أساساً في نقل الإصلاحات العاجلة (Backporting) من main إلى فروع الإصدار القديمة دون دمج الميزات غير المكتملة. والـ Fork هو استنساخ كامل للمستودع على خادم GitHub/GitLab تحت حساب منفصل؛ ويُستخدم في المشاريع مفتوحة المصدر أو مع المطورين الخارجيين الذين لا يملكون صلاحيات دفع مباشرة، حيث يقومون بالتعديل في الـ Fork وفتح Pull Request للمستودع الأصلي Upstream.",
        "walkthrough_ar": """أمثلة لأوامر stash و cherry-pick ومزامنة الـ Fork في بيئة العمل:
```bash
# 1. تخزين التعديلات المحلية مؤقتاً مع الملفات غير المتابعة:
git stash push -u -m "WIP: biometric card validation"
git checkout hotfix/crash-fix
# ... إصلاح العطل ودفعه ...
git checkout feature/biometric
git stash pop # استرجاع التعديلات ومسحها من المكدس

# 2. نقل كوميت إصلاح عطل من main إلى فرع الإصدار release-v1.4:
git checkout release/v1.4
git cherry-pick -x c8d9e0f # -x تسجل بصمة الكوميت الأصلي للتوثيق
git push origin release/v1.4

# 3. مزامنة الـ Fork المحلي مع المستودع الأصلي (Upstream):
git remote add upstream https://github.com/organization/android-core.git
git fetch upstream
git checkout main
git merge upstream/main
```""",
        "why_it_matters_ar": "يمكن المطور من الانتقال اللحظي للمهام الطارئة دون فقدان الكود، ويتيح إصلاح الأعطال في فروع الإنتاج المستقرة دون جلب أكواد غير ناضجة.",
        "worked_example_ar": "اكتشاف ثغرة في تطبيق منشور بإصدار قديم؛ تم إصلاحها في main ونقل الكوميت عبر cherry-pick -x لفرع الإصدار القديم ونشره خلال نصف ساعة دون أي تعقيد.",
        "trade_offs_ar": "أمر cherry-pick رائع لنقل الإصلاحات لكنه يولد كوميتات مكررة بهاش جديد؛ والـ stash مفيد للتبديل السريع لكن حفظ العمل فيه لأيام طويلة يعرضه للفقدان لعدم نسخه احتياطياً.",
        "failure_modes_ar": "نسيان استخدام خيار -u مع stash مما يترك الملفات الجديدة في مسار العمل فتتعارض مع الفرع الآخر، أو استخدام stash كبديل للكوميتات لفترات طويلة.",
        "production_perspective_ar": "نلزم المطورين باستخدام خيار -x عند عمل cherry-pick لتوثيق المصدر، ونشغل أتمتة دورية لمزامنة مستودعات الـ Fork مع الـ Upstream لتجنب الانحراف التراكمي.",
        "how_to_answer_ar": "عرف كل أداة بوضوح: stash لحفظ العمل المؤقت، cherry-pick لانتقاء كوميت محدد لنقل الإصلاحات، والـ Fork للفصل الأمني والمساهمات الخارجية.",
        "talking_points_ar": "مكدس stash وخيار -u، نقل الإصلاحات العاجلة بـ cherry-pick، توثيق الكوميت الأصلي بـ -x، مستودعات الـ Fork، ومزامنة فرع Upstream.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يفضل تمرير خيار -x عند تنفيذ أمر git cherry-pick؟'\n  **المرشح:** 'لأنه يضيف تلقائياً نصاً في رسالة الكوميت يوضح الـ Hash الأصلي الذي نُقل منه التعديل، مما يسهل التدقيق الأمني ويمنع الالتباس عند مراجعة تاريخ الفروع.'\n\n- **المحاور:** 'ما الفرق بين git stash pop و git stash apply؟'\n  **المرشح:** 'أمر pop يسترجع التعديلات ويحذفها فوراً من مكدس الـ stash؛ بينما apply يسترجع التعديلات ويحتفظ بنسخة منها داخل المكدس لاستخدامها لاحقاً إذا رغب المطور.'",
        "self_check_ar": "هل شرحت stash وخيار -u، وآلية cherry-pick واستخداماته وخيار -x، ومفهوم الـ Fork ومزامنة Upstream؟",
        "references_ar": f"- [Pro Git Book: Git Stashing and Cleaning](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning) — الدليل الرسمي لحفظ وتفريغ مساحات العمل في Git.\n- [Pro Git Book: Git Cherry-pick and Workflows](https://git-scm.com/docs/git-cherry-pick) — التوثيق الرسمي لانتقاء ونقل الكوميتات المنفردة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """أمر git stash يحفظ التعديلات غير المسجلة مؤقتاً لتفريغ بيئة العمل للتبديل السريع للمهام الطارئة. أمر git cherry-pick ينقل كوميت محدد برقم الهاش من فرع لآخر دون دمج الفرع كاملاً وهو مثالي لنقل الإصلاحات العاجلة لفروع الإصدارات. أما الـ Fork فهو استنساخ كامل للمستودع على السيرفر للمساهمة في المشاريع دون صلاحيات تعديل مباشرة.""",
        "best_answer_ar": """تحل هذه الأدوات الثلاث تحديات مميزة في إدارة التعديلات المحلية ونقل الإصلاحات وتنظيم مساهمات الفرق البرمجية.
يقوم أمر git stash بتخزين التعديلات غير المسجلة محلياً في مكدس داخلي، مما يعيد بيئة العمل لحالة نظيفة تتيح الانتقال الفوري لمعالجة عطل طارئ على فرع آخر؛ وباستخدام خيار -u نضمن شمول الملفات الجديدة غير المتابعة في التخزين.
في حين يتيح أمر git cherry-pick استخراج التعديل الناتج عن كوميت محدد في أي فرع وتطبيقه ككوميت جديد ومستقل على الفرع الحالي؛ وهو ما يجعله الأداة المثالية لنقل إصلاحات الأخطاء العاجلة من الفرع الرئيسي إلى فروع الإصدارات الإنتاجية القديمة دون جلب ميزات غير مكتملة.
أما مفهوم الـ Fork، فيمثل استنساخاً كاملاً للمستودع على مستوى خادم GitHub أو GitLab تحت حساب منفصل؛ وهو النمط القياسي في المشاريع مفتوحة المصدر وللمتعاقدين الخارجيين الذين لا يملكون صلاحيات دفع مباشرة، حيث يتيح لهم تطوير الميزات في مستودعهم الخاص ثم فتح طلب دمج موجه نحو المستودع الأصلي.""",
        "deep_answer_ar": """من منظور حوكمة الأكواد وهندسة الإصدارات، يتطلب الاستخدام الاحترافي لهذه الأدوات إدراكاً عميقاً لمصائدها التشغيلية في بيئات العمل المشتركة.
إن اللجوء إلى git stash مفيد جداً للمقاطعات السريعة، لكن الاعتماد عليه كأداة لأرشفة الأعمال لعدة أيام يمثل مجازفة كبرى؛ لأن مكدس الـ stash محلي تماماً ولا يتم رفعه للـ Remote، وأي عطل في قرص المطور أو تشغيل لأوامر التنظيف التدميرية يؤدي لفقدان العمل دون رجعة؛ والحل الأفضل للمهام المعلقة هو رفعها لفرع مسودة سحابي خاص.
وعند استخدام git cherry-pick، يجب الانتباه لمشكلة تكرار الكوميتات؛ فنقل كوميت من فرع لآخر يعيد كتابة الـ Hash، وإذا أُعيد دمج الفرعين لاحقاً، يتعامل Git مع الكوميتين كتعديلات متشابهة قد تولد تعارضات غير ضرورية. ولذلك نلزم الفرق بتمرير خيار -x دائماً لتوثيق البصمة الأصلية في الرسالة لسهولة التدقيق والدمج اللاحق.
أما في إدارة المستودعات المتفرعة Forked Repositories في المؤسسات الكبرى، فإن التحدي الأكبر هو تجنب انحراف الكود عن المستودع الرئيسي Upstream. ولمنع تراكم التضاربات، نربط الـ Fork بخطوط أتمتة مجدولة تقوم بجلب التحديثات من الفرع الأصلي بانتظام، مما يحافظ على التوافق الدائم ويسهل قبول طلبات الدمج دون مجهود مضاعف، مع وضع سياسات حوكمة صارمة لحماية الأصول البرمجية للشركة وسلسلة التوريد."""
    }
}

# ==========================================
# Runner & Word Count Validation
# ==========================================
import re

def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())

        meta = d["meta_ar"]
        quick_ar_w = len(meta["quick_answer_ar"].split())
        best_ar_w = len(meta["best_answer_ar"].split())
        deep_ar_w = len(meta["deep_answer_ar"].split())

        print(f"[{qid}] Words -> EN: short={short_w}, struct={struct_w}, deep={deep_w} | AR: quick={quick_ar_w}, best={best_ar_w}, deep={deep_ar_w}")

        assert 35 <= short_w <= 110, f"{qid}: short_en word count {short_w} out of range [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid}: structured_en word count {struct_w} out of range [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid}: deep_senior_en word count {deep_w} out of range [200, 650]"

        assert 35 <= quick_ar_w <= 110, f"{qid}: quick_answer_ar word count {quick_ar_w} out of range [35, 110]"
        assert 90 <= best_ar_w <= 280, f"{qid}: best_answer_ar word count {best_ar_w} out of range [90, 280]"
        assert 180 <= deep_ar_w <= 650, f"{qid}: deep_answer_ar word count {deep_ar_w} out of range [180, 650]"

        for name, text in [
            ("short_en", d["short_en"]),
            ("structured_en", d["structured_en"]),
            ("deep_senior_en", d["deep_senior_en"]),
            ("quick_answer_ar", meta["quick_answer_ar"]),
            ("best_answer_ar", meta["best_answer_ar"]),
            ("deep_answer_ar", meta["deep_answer_ar"]),
        ]:
            assert not re.search(r"^\s*[-*•]\s*", text, re.M), f"{qid}: {name} contains bullets"
            assert not re.search(r"^\s*\d+[\.\)]\s*", text, re.M), f"{qid}: {name} contains numbered list"

        assert "First," not in d["structured_en"] or "Next," not in d["structured_en"], f"{qid}: structured_en has formulaic enumeration"
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

    ee.save_topic_metadata("cic_01_07", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} CIC questions (CIC-01 to CIC-07) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
