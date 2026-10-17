#!/usr/bin/env python3
"""
Elevation script for CIC questions: CIC-08 to CIC-14.
Topic: CI/CD, Git & Team Delivery (CIC)
Phase 4, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "الـ CI/CD والـ Git وتسليم المشاريع في الفرق الهندسية"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# CIC-08: How do you configure PR checks for lint, static analysis, and tests?
# ==========================================
DATA["CIC-08"] = {
    "concept_en": """Pull Request verification gates enforce automated quality standards before code enters the shared mainline, operating on the fail-fast principle to maximize developer velocity:
- Tiered Quality Gate Strategy:
  - Formatting & Style Verification:
    - Executes deterministic linters like Spotless or ktlint. Confirms spacing, imports, and naming standards without semantic analysis overhead within seconds.
  - Static Code Analysis:
    - Runs Detekt to detect cyclomatic complexity, code smells, duplicate code, and custom architectural boundary rules (e.g., forbidding Android framework imports in domain modules).
  - Android Framework Linting:
    - Runs `./gradlew lintDebug`. Evaluates Android resource hygiene, security vulnerabilities, accessibility omissions, and API compatibility across minSdk and targetSdk versions.
  - Historical Debt Management via Baselines:
    - In mature codebases with legacy warnings, running Lint without baselines can produce hundreds of historical errors. Teams generate `lint-baseline.xml` and Detekt baseline files; the gate ignores preexisting issues but strictly breaks the build if a developer introduces even one net-new defect.
  - Host JVM Unit Testing:
    - Executes `./gradlew testDebugUnitTest` across affected modules, validating domain business logic, state machines, and repository contracts without emulator latency.
  - Unified Failure Reporting:
    - Pipelines execute checks with the `--continue` flag so all errors across modules are aggregated in a single run. Reports are ingested and published directly as SARIF annotations and inline PR comments.""",
    "walkthrough_en": """GitHub Actions workflow configuring fail-fast PR static analysis and unit testing:
```yaml
# .github/workflows/pr_checks.yml
name: PR Quality Verification

on:
  pull_request:
    branches: [ main, develop ]

concurrency:
  group: pr-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  static_analysis:
    name: Lint & Detekt
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Formatting & Static Analysis
        run: ./gradlew spotlessCheck detekt lintDebug --continue
      - name: Publish SARIF Lint Report
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: build/reports/detekt/detekt.sarif

  unit_tests:
    name: JVM Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Host Unit Tests
        run: ./gradlew testDebugUnitTest --continue
      - name: Archive Test Results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: '**/build/reports/tests/testDebugUnitTest/'
```""",
    "short_en": """PR checks are configured as fail-fast parallel pipelines combining Spotless for formatting, Detekt for static complexity rules, Android Lint with baselines for SDK and resource hygiene, and testDebugUnitTest for business logic. Running with the continue flag aggregates all defects in a single pass, publishing inline PR annotations so developers receive comprehensive feedback within minutes.""",
    "structured_en": """Configuring Pull Request checks requires balancing thorough regression prevention against developer iteration velocity.
In high-performing engineering teams, we structure PR validation into parallel, fail-fast jobs. The first tier runs Spotless or ktlint to enforce code formatting instantly. Alongside it, Detekt executes static analysis rules enforcing cyclomatic complexity thresholds and preventing architectural layer violations.
For platform correctness, we run Android Lint on debug variants. To prevent historical warnings from blocking new feature work in mature codebases, we enforce baseline files like lint-baseline.xml; this ensures the pipeline only breaks when net-new violations are introduced. Concurrently, host JVM unit tests run across all modified modules using testDebugUnitTest.
By executing Gradle tasks with the continue flag and leveraging GitHub Actions concurrency cancellation, existing runs on outdated commits are terminated immediately when a developer pushes a new commit. Build summaries and SARIF annotations post failure reports directly into the pull request review interface, providing complete actionable feedback in under five minutes.""",
    "deep_senior_en": """From a release engineering and developer productivity perspective, pull request checks are the foundational filter protecting mainline stability and reducing code review cycle time.
When designing an enterprise-scale PR verification pipeline, the primary architectural trap is attempting to run exhaustive test suites or full instrumentation emulators on every commit. This bloats queue times to half an hour and degrades team velocity. Instead, we divide verification into fast presubmit gates on PRs and exhaustive post-merge nightly runs. Presubmit checks focus exclusively on deterministic, low-overhead tasks: bytecode and source formatting with Spotless, static architecture governance with Detekt, platform resource verification with Android Lint, and JVM unit tests.
Managing technical debt in large legacy codebases requires disciplined baseline governance. Simply turning on Lint with fail-on-warning will paralyze development by surfacing thousands of legacy warnings. We establish baseline files that capture historical debt at a specific point in time, configuring CI to fail only on regression deltas. We then schedule automated recurring maintenance tasks to ratcheting down baselines incrementally over time.
To optimize CI infrastructure costs and runtimes, we combine Gradle configuration caching with affected-module detection tools. If a pull request touches only the profile feature module, our pipeline skips compiling unaffected payments and authentication modules entirely. Furthermore, we mandate pull request concurrency controls; pushing a new commit immediately cancels obsolete runner jobs, freeing up CI runners and ensuring that engineering feedback loops remain snappy, reliable, and friction-free.""",
    "meta_ar": {
        "id": "CIC-08",
        "questionAr": "كيف تقوم بإعداد وتأمين بوابات فحص الـ PRs (Pull Request Checks) للـ Lint والتحليل الساكن واختبارات الوحدة؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استراتيجية بوابات جودة الكود (PR Quality Gates)، مبدأ Fail-Fast، إدارة ملفات الـ Baseline لمنع تراكم الديون التقنية، وأتمتة تقارير الفحص عبر الـ CI.",
        "concept_ar": "تعتمد بوابات فحص طلبات الدمج على مبدأ الإخفاق السريع لفحص التعديلات في غضون دقائق معدودة قبل استهلاك موارد الحوسبة في مهام بناء ثقيلة. يتم تنظيم البوابة في مسارات متوازية تبدأ بفحص التنسيق السريع عبر Spotless أو ktlint للتأكد من التزام الكود بأنماط كوتلن القياسية، يليه التحليل الساكن المتقدم عبر Detekt لكشف مشاكل التعقيد المعماري ومخالفات الطبقات. بعد ذلك، يُشغل فحص أندرويد لنت لاكتشاف مشاكل موارد النظام وملاءمة الـ APIs وإدارة الذاكرة؛ ولتجنب تعطيل الفرق في المشاريع القديمة التي تحتوي على مئات التحذيرات السابقة، يتم استخدام ملفات الـ Baseline مثل lint-baseline.xml بحيث تتجاهل البوابة المشاكل التاريخية وترفض الـ PR فوراً إذا أضاف أي مشكلة جديدة. وتختتم البوابة بتشغيل اختبارات الوحدة السريعة على الـ JVM مع تفعيل علم continue لتجميع كافة التقارير ورفعها كـ SARIF annotations تظهر مباشرة على أسطر الكود داخل الـ PR.",
        "walkthrough_ar": """إعداد GitHub Actions لتشغيل الفحوصات بالتوازي مع إلغاء المهام القديمة:
```yaml
# .github/workflows/pr_checks.yml
name: PR Static & Unit Checks
on:
  pull_request:
    branches: [ main, develop ]

concurrency:
  group: pr-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  static_analysis:
    name: Lint & Detekt
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Linters & Detekt
        run: ./gradlew spotlessCheck detekt lintDebug --continue

  unit_tests:
    name: JVM Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Unit Tests
        run: ./gradlew testDebugUnitTest --continue
```""",
        "why_it_matters_ar": "حماية الفرع الرئيسي من الأخطاء النحوية والتراجع في منطق الأعمال يوفر مئات الساعات المهدرة في مراجعات الكود اليدوية ويمنع تعطل بيئات التطوير المشتركة.",
        "worked_example_ar": "في مشروع متعدد الوحدات، نقوم بإعداد Spotless لفحص المسافات والواردات غير المستخدمة، وDetekt لفرض قواعد المعمارية، وLint مع baseline.xml لرفض التحذيرات الجديدة فقط، مع تشغيل testDebugUnitTest لكافة الموديولات المتأثرة.",
        "trade_offs_ar": "إضافة اختبارات المحاكي الثقيلة في كل PR يوفر ثقة أعلى ولكنه يبطئ دورة عمل المطورين لعشرات الدقائق؛ بينما الاكتفاء بالتحليل الساكن واختبارات الـ JVM يوفر سرعة رد فائقة خلال دقائق مع تأجيل الاختبارات الثقيلة للمسار الليلي.",
        "failure_modes_ar": "أخطر الأخطاء هو تشغيل Lint بإعداد يوقف البناء على تحذيرات قديمة مما يولد إحباطاً لدى المطورين، أو عدم استخدام cancel-in-progress مما يهدر موارد الـ CI في فحص تعديلات تم استبدالها بالفعل.",
        "production_perspective_ar": "في الشركات الكبرى، تُربط تقارير SARIF الصادرة من Detekt وLint مع واجهة الـ PR ليظهر التنبيه للمطور مباشرة على السطر المخطئ، مما يجعل عملية الإصلاح فورية وبديهية.",
        "how_to_answer_ar": "ابدأ ببيان مبدأ Fail-Fast، ثم اشرح التدرج من التنسيق السطحي للتحليل الساكن ثم فحص النظام والوحدات، وركز على حل مشكلة الكود القديم عبر ملفات الـ Baseline وكيفية تسريع الـ CI بالتوازي.",
        "talking_points_ar": "مبدأ Fail-Fast، دور Spotless وktlint، قواعد Detekt المعمارية، ملفات lint-baseline.xml، علم continue، وإلغاء المهام المتكررة عبر cancel-in-progress.",
        "follow_ups_ar": "كيف تتعامل مع فحص الموديولات المعدلة فقط عبر Affected Module Detector؟ وكيف تمنع تسرب التحذيرات الجديدة للـ Baseline؟",
        "self_check_ar": "هل شرحت مبدأ Fail-Fast، دور Spotless وDetekt وAndroid Lint، وكيف تمنع ملفات الـ Baseline الديون التقنية؟",
        "references_ar": f"- [Android Developers: Improve your code with lint checks](https://developer.android.com/studio/write/lint) — التوثيق الرسمي لأداة أندرويد لنت وإدارة ملفات الـ Baseline.\n- [Detekt: Static code analysis for Kotlin](https://detekt.dev/) — التوثيق الرسمي لأداة التحليل الساكن لكوتلن.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نقوم بإعداد بوابات الـ PR وفق مبدأ الإخفاق السريع بتشغيل مهام متوازية تشمل Spotless للتنسيق، وDetekt للتحليل الساكن، وAndroid Lint مع ملفات الـ Baseline لحظر الأخطاء الجديدة دون التعطل في المشاكل القديمة، واختبارات testDebugUnitTest. ونستخدم علم continue لتجميع الأخطاء وإظهارها مباشرة على الـ PR في دقائق معدودة.""",
        "best_answer_ar": """تصميم بوابة فحص طلبات الدمج يهدف إلى حماية جودة الكود دون إبطاء حركة المطورين.
نبدأ بتقسيم الفحوصات إلى مراحل سريعة ومتوازية؛ حيث يفحص Spotless أو ktlint التنسيق السطحي في ثوانٍ، بينما يتولى Detekt التأكد من عدم تجاوز تعقيد الدوال للحدود المسموحة ومنع خرق حدود المعمارية كاستيراد كلاسات أندرويد داخل طبقة الـ Domain.
أما بالنسبة لأندرويد لنت، فنقوم بتشغيل lintDebug بالاعتماد على ملفات الـ Baseline مثل lint-baseline.xml؛ وهذا يتيح للبوابة تجاهل المشاكل التاريخية المتراكمة في المشاريع القديمة مع إيقاف البناء فوراً إذا تسبب المطور في إضافة أي خطأ أو تحذير جديد. بالتوازي مع ذلك، نشغل اختبارات الوحدة على الـ JVM للتحقق من منطق العمل.
ونحرص على تشغيل المهام باستخدام علم continue لتسجيل كافة الملاحظات في تقرير موحد، مع ضبط سياسة إلغاء المهام السابقة بمجرد رفع تعديل جديد على الـ PR؛ مما يضمن وصول التعليقات للمطور على أسطر الكود مباشرة في أقل من خمس دقائق.""",
        "deep_answer_ar": """من منظور إنتاجية المطورين وهندسة الإصدارات، تعد بوابات فحص طلبات الدمج خط الدفاع الأول لضمان سلامة الفرع الرئيسي وتقليص وقت المراجعة اليدوية بين أعضاء الفريق الهندسي.
الخطأ المعماري الشائع في تصميم بوابات الـ PR هو محاولة تشغيل اختبارات المحاكي الثقيلة أو بناء الحزم الإنتاجية مع كل تعديل؛ مما يرفع وقت الانتظار لنصف ساعة ويثبط عزيمة المطورين ويقلل من وتيرة الشحن البرمجي. النهج الهندسي الصحيح هو قصر فحوصات الـ PR على التحقق الحتمي السريع الذي لا يتجاوز خمس دقائق، بينما تُرحل الاختبارات الموسعة والتكاملية للمسارات الليلية المجدولة.
ولإدارة الديون التقنية في المشاريع الكبرى دون شل حركة العمليات، نلجأ إلى حوكمة الـ Baselines؛ حيث يتم تثبيت التحذيرات القديمة في ملف مرجعي محمي، ويقتصر فشل الـ CI على الأخطاء المستحدثة فقط، مع تخصيص مهام ربع سنوية لتخفيض هذه الديون تدريجياً دون المساس بإنتاجية الفريق.
كما نعمل على تقليص استهلاك السيرفرات السحابية باستخدام كاش Gradle وتفعيل خاصية اكتشاف الموديولات المعدلة؛ فإذا شمل التعديل شاشة الملف الشخصي فقط، يتم استبعاد موديولات الدفع والمصادقة من الفحص كلياً. وبدمج ذلك مع إلغاء المهام غير المكتملة فور رفع كوميت جديد ورفع تقارير SARIF مباشرة في واجهة المراجعة، نضمن بيئة عمل رشيقة، منضبطة، واقتصادية في استهلاك موارد الحوسبة."""
    }
}

# ==========================================
# CIC-09: How do you protect signing material and CI secrets?
# ==========================================
DATA["CIC-09"] = {
    "concept_en": """Securing cryptographic signing keys and deployment credentials in CI pipelines is critical to prevent malicious binary injection, repository takeovers, and unauthorized app publication:
- Play App Signing Decoupling:
  - Google Play App Signing separates the developer's Upload Key from the actual App Signing Key held securely within Google Cloud Key Management Service (Cloud KMS) Hardware Security Modules.
  - If an Upload Key is compromised or lost, it can be revoked and reset via Play Console support without orphaning existing installed users. The core App Signing Key is never exposed to developers or CI runners.
- Keystore Ingestion Architecture:
  - Production Keystore files (`.jks` or `.keystore`) must never be checked into Git repositories.
  - Keystores are stored as base64-encoded strings inside encrypted CI secret vaults (GitHub Actions Secrets, HashiCorp Vault, AWS Secrets Manager).
  - The CI workflow decodes the secret into an ephemeral, temporary file on the runner filesystem, signs the binary, and guarantees deletion in a post-execution cleanup step.
- Secret Ingestion via Environment Variables:
  - Keystore passwords, key aliases, and service account keys are injected at runtime via environment variables rather than hardcoded in `gradle.properties` or `build.gradle.kts`.
  - Gradle build scripts read properties via `System.getenv("KEYSTORE_PASSWORD")` or `providers.environmentVariable()`.
- Pull Request Sandbox Governance:
  - Workflows triggered by `pull_request` from untrusted fork repositories must not have access to production secrets.
  - Using dangerous triggers like `pull_request_target` without explicit commit verification allows malicious external actors to submit pull requests that extract secrets via Gradle execution.
  - Release signing jobs are restricted exclusively to protected mainline branches with manual deployment approvals and environment protection rules.""",
    "walkthrough_en": """Secure signing setup in Gradle Kotlin DSL and GitHub Actions:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE_PATH") ?: "keystore/dummy.jks")
            storePassword = System.getenv("KEYSTORE_STORE_PASSWORD")
            keyAlias = System.getenv("KEYSTORE_KEY_ALIAS")
            keyPassword = System.getenv("KEYSTORE_KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

```yaml
# .github/workflows/release_signing.yml
name: Production Release Build
on:
  push:
    branches: [ main ] # Only run on protected mainline

jobs:
  sign_and_package:
    runs-on: ubuntu-latest
    environment: production # Requires designated environment approval
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }

      # Decode Keystore into ephemeral file
      - name: Provision Ephemeral Keystore
        run: |
          mkdir -p $HOME/signing
          echo "${{ secrets.RELEASE_KEYSTORE_BASE64 }}" | base64 -d > $HOME/signing/release.keystore
          chmod 600 $HOME/signing/release.keystore

      - name: Build Signed Release Bundle
        env:
          KEYSTORE_FILE_PATH: ${{ env.HOME }}/signing/release.keystore
          KEYSTORE_STORE_PASSWORD: ${{ secrets.KEYSTORE_STORE_PASSWORD }}
          KEYSTORE_KEY_ALIAS: ${{ secrets.KEYSTORE_KEY_ALIAS }}
          KEYSTORE_KEY_PASSWORD: ${{ secrets.KEYSTORE_KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      # Always wipe ephemeral credentials, even if build fails
      - name: Purge Ephemeral Keystore
        if: always()
        run: rm -rf $HOME/signing/
```""",
    "short_en": """Protect signing materials by using Google Play App Signing, keeping upload keystores out of Git, and storing them as base64 strings in encrypted CI secrets. Decode them into ephemeral runner files during release builds, pass passwords through environment variables, wipe keys in guaranteed post-cleanup steps, and sandbox pull request workflows to prevent credential exfiltration.""",
    "structured_en": """Securing signing keys and deployment credentials requires strict isolation between CI runners, repository code, and production secrets.
At the architectural level, teams leverage Google Play App Signing. This decouples the Upload Key used by CI from the master App Signing Key stored securely in Google Cloud Hardware Security Modules, ensuring a compromised upload key can be revoked without breaking user updates.
In the CI environment, keystore files are never stored in version control. Instead, they are encoded in base64 and stored within encrypted secrets vaults like GitHub Secrets or HashiCorp Vault. During release jobs on protected branches, the pipeline decodes the keystore into an ephemeral file on the runner, injecting passwords via environment variables through Gradle providers.
Critically, cleanup steps running with if-always flags purge the decoded keystore from the runner disk immediately after compilation. Furthermore, PR workflows triggered from public forks are strictly sandboxed without access to production credentials, mitigating unauthorized secret exfiltration attacks.""",
    "deep_senior_en": """From a security architecture and platform integrity standpoint, mobile signing credentials represent existential organizational risk. A leaked production keystore allows malicious actors to publish compromised binaries or impersonate the enterprise.
We mitigate this through defense in depth. First, Google Play App Signing is non-negotiable. It isolates the developer signing certificate from the definitive distribution key managed within Google Cloud KMS. If a runner vulnerability compromises our upload certificate, we can submit a revocation request and regenerate the upload key without stranding millions of installed production users.
Second, secrets management mandates zero-trust persistence. Keystores and Google Play service account JSON tokens are stored in encrypted vaults and injected strictly at execution time. In GitHub Actions, we decode the base64 keystore into an ephemeral directory with strict 600 file permissions. Passwords and aliases are passed exclusively via transient process environment variables, preventing Gradle from writing them to build cache metadata or daemon logs. An explicit cleanup hook with an if-always condition wipes the ephemeral keystore even if Gradle crashes or times out.
Finally, repository privilege segregation is critical. We isolate signing pipelines inside restricted GitHub Environments requiring manual approvals from designated release engineers. We strictly prohibit pull request workflows from accessing deployment credentials, avoiding vulnerable triggers like pull-request-target that allow untrusted contributors to exfiltrate secrets via modified Gradle tasks. This multi-layered posture ensures robust automation without exposing critical cryptographic assets.""",
    "meta_ar": {
        "id": "CIC-09",
        "questionAr": "كيف تحمي مفاتيح توقيع التطبيق (Signing Material) والأسرار في بيئات الـ CI؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استراتيجيات تأمين مفاتيح التوقيع، معمارية Play App Signing، إدارة الأسرار عبر الـ Base64 ومتغيرات البيئة، منع تسريب البيانات من الـ PRs المشبوهة، وحذف المفاتيح المؤقتة.",
        "concept_ar": "تعتمد حماية مفاتيح التوقيع والأسرار في الـ CI على معمارية دفاعية متعددة الطبقات لمنع تسريب المفاتيح أو نشر نسخ خبيثة: تبدأ الاستراتيجية بتفعيل Google Play App Signing الذي يفصل مفتاح الرفع (Upload Key) الموجود في الـ CI عن مفتاح التوقيع الفعلي (App Signing Key) المحفوظ داخل وحدات أمان سحابية (HSM) لدى جوجل؛ مما يتيح استبدال مفتاح الرفع بسهولة في حال اختراقه دون فقدان المستخدمين. ثانياً، يُحظر تماماً حفظ ملفات الـ Keystore داخل Git، بل تُشفر بصيغة base64 وتُحفظ داخل خزائن الأسرار المشفرة للـ CI. أثناء بناء النسخة الإنتاجية، يفك الـ CI تشفير المفتاح في مسار مؤقت على السيرفر ويحقن كلمات المرور كمتغيرات بيئة دون كتابتها في ملفات Gradle، مع تنفيذ خطوة تنظيف حتمية تحذف المفتاح المؤقت حتى لو فشل البناء. ثالثاً، تُعزل بيئات النشر بصلاحيات محمية وموافقة يدوية مع حظر وصول أي طلب دمج قادم من Fork للأسرار.",
        "walkthrough_ar": """تكوين Gradle واستخدام مسار مؤقت للمفتاح في GitHub Actions:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE_PATH") ?: "dummy.jks")
            storePassword = System.getenv("KEYSTORE_STORE_PASSWORD")
            keyAlias = System.getenv("KEYSTORE_KEY_ALIAS")
            keyPassword = System.getenv("KEYSTORE_KEY_PASSWORD")
        }
    }
}
```

```yaml
# .github/workflows/release.yml
jobs:
  sign:
    runs-on: ubuntu-latest
    environment: production # حماية البيئة بموافقة يدوية
    steps:
      - uses: actions/checkout@v4
      - name: Decode Keystore
        run: |
          mkdir -p $HOME/signing
          echo "${{ secrets.RELEASE_KEYSTORE_BASE64 }}" | base64 -d > $HOME/signing/release.keystore
          chmod 600 $HOME/signing/release.keystore
      - name: Build Bundle
        env:
          KEYSTORE_FILE_PATH: ${{ env.HOME }}/signing/release.keystore
          KEYSTORE_STORE_PASSWORD: ${{ secrets.KEYSTORE_STORE_PASSWORD }}
          KEYSTORE_KEY_ALIAS: ${{ secrets.KEYSTORE_KEY_ALIAS }}
          KEYSTORE_KEY_PASSWORD: ${{ secrets.KEYSTORE_KEY_PASSWORD }}
        run: ./gradlew bundleRelease
      - name: Clean Keystore
        if: always()
        run: rm -rf $HOME/signing/
```""",
        "why_it_matters_ar": "تسريب مفاتيح التوقيع يهدد وجود الشركة بالكامل؛ حيث يمكن للمهاجمين نشر برمجيات خبيثة باسم التطبيق أو السيطرة على حسابات المستخدمين وبياناتهم.",
        "worked_example_ar": "نقوم بترميز keystore.jks بصيغة base64 وحفظه في GitHub Secrets، ثم في خط البناء نفك ترميزه إلى ملف مؤقت ونحقن كلمات المرور كمتغيرات بيئة، وننفذ أمر rm -rf للملف في خطوة إجبارية.",
        "trade_offs_ar": "الاحتفاظ بالمفاتيح يدوياً لدى مطور واحد يقلل خطر الـ CI ولكنه يعطل الأتمتة بالكامل؛ بينما أتمتة التوقيع عبر خزائن الأسرار السحابية مع صلاحيات البيئة المشروطة يوفر أماناً عالياً مع استمرارية التسليم.",
        "failure_modes_ar": "أخطر الأخطاء هو ارتكاب ملف المفتاح أو كلمات المرور داخل ملف gradle.properties في Git، أو استخدام مشغل pull_request_target بدون حذر مما يتيح لأي PR خارجي طباعة الأسرار في السجلات.",
        "production_perspective_ar": "في بيئات الإنتاج، تُربط أسرار البناء بـ Environment Protection Rules تتطلب موافقة مهندس إصدارات معتمد قبل فك تشفير المفاتيح، مع تفعيل إخفاء السجلات (Secret Masking).",
        "how_to_answer_ar": "اشرح أولاً دور Play App Signing في حماية التطبيق من الكوارث، ثم وضح آلية تحويل المفتاح لـ base64 وفكه في مسار مؤقت، وأكد على أهمية متغيرات البيئة وخطوة التنظيف الإجبارية وعزل الـ PRs.",
        "talking_points_ar": "ميزة Play App Signing، تشفير المفتاح كـ base64، حقن كلمات المرور عبر متغيرات البيئة، خطوة التنظيف الحتمية if-always، وحظر الأسرار عن طلبات الدمج من الفروع الخارجية.",
        "follow_ups_ar": "كيف تتصرف إذا تم تسريب مفتاح الرفع Upload Key؟ وما هي مخاطر استخدام حدث pull_request_target في GitHub Actions؟",
        "self_check_ar": "هل وضحت الفارق بين Upload Key وApp Signing Key، وكيفية فك المفتاح وحذفه بشكل آمن في الـ CI؟",
        "references_ar": f"- [Google Play Console: Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) — الدليل الرسمي لحماية وإدارة مفاتيح التوقيع السحابية.\n- [GitHub Docs: Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) — التوثيق الرسمي لحماية الأسرار وعزل البيئات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نحمي مفاتيح التوقيع بالاعتماد على Google Play App Signing لفصل مفتاح الرفع عن مفتاح التطبيق الأساسي، ونخزن ملف الـ Keystore مشفراً كـ base64 داخل خزنة الـ CI. وأثناء بناء الإنتاج نفك تشفيره في مسار مؤقت ونحقن كلمات المرور كمتغيرات بيئة، ثم نحذف الملف فوراً في خطوة تنظيف إجبارية مع حظر وصول طلبات الدمج للأسرار.""",
        "best_answer_ar": """حماية مفاتيح التوقيع وأسرار النشر تتطلب عزلاً صارماً بين سيرفرات الـ CI وشفرة المشروع وخزائن الأسرار.
نبدأ بتفعيل Google Play App Signing؛ وهي خطوة معمارية حاسمة تفصل مفتاح الرفع المستخدم في الـ CI عن مفتاح التوقيع الرئيسي المحفوظ بأمان في خوادم جوجل السحابية، مما يسمح بإلغاء واستبدال مفتاح الرفع بسهولة في حال اختراقه دون أن يتأثر مستخدمو التطبيق.
داخل خطوط الـ CI، يُحظر رفع ملف الـ Keystore إلى Git، بل يتم تحويله إلى نص مشفر بـ base64 وحفظه في GitHub Secrets. وأثناء تنفيذ خط البناء على الفروع المحمية فقط، يفك السيرفر تشفير المفتاح إلى ملف مؤقت، وتُحقن كلمات المرور كمتغيرات بيئة تُمرر مباشرة لـ Gradle دون تسجيلها في السجلات.
وفور انتهاء عملية البناء، تُشغل خطوة تنظيف حتمية تعمل حتى في حال فشل البناء لحذف المفتاح المؤقت تماماً من القرص. كما نمنع طلبات الدمج القادمة من الـ Forks الخارجية من الوصول لبيئة الإنتاج لحماية الأسرار من التسريب.""",
        "deep_answer_ar": """من منظور الأمان المؤسسي وسلامة المنصات، يمثل تسريب مفتاح توقيع التطبيق خطراً وجودياً يتيح للمخترقين إصدار نسخ ضارة للمستخدمين وانتحال هوية التطبيق في متجر جوجل.
ولذلك نعتمد استراتيجية الدفاع في العمق؛ أولها الاعتماد الإلزامي على Play App Signing لعزل شهادة الرفع عن المفتاح الجذري المشفر في وحدات الأمان السحابية لدى جوجل؛ فإذا تعرض سيرفر الـ CI لأي اختراق أو تم تسريب مفتاح الرفع بالخطأ، يمكننا إعادة توليد مفتاح الرفع عبر طلب دعم رسمي دون فقدان قاعدة المستخدمين الحالية أو تعريض تحديثاتهم للخطر.
ثانياً، نطبق مبدأ انعدام الثقة في إدارة الأسرار؛ حيث يُشفر ملف المفتاح بصيغة base64 ويُفك تشفيره أثناء بناء الإنتاج فقط داخل مجلد مؤقت بصلاحيات قراءة مقتصرة على السيرفر. وتُمرر كلمات المرور واسم الـ Alias عبر متغيرات بيئة مؤقتة تمنع كاش Gradle من حفظها أو كتابتها في السجلات، مع استخدام خطوة تنظيف تعمل شرطياً في كافة الحالات لحذف المفتاح المؤقت فور اكتمال التجميع حتى لو فشل البناء.
وأخيراً، نضع حواجز صارمة على مستوى الصلاحيات وإدارة الوصول؛ حيث تقتصر مهام التوقيع على الفرع الرئيسي بعد نيل موافقة يدوية من مهندس الإصدارات المسؤول، مع حظر تشغيل هذه الأسرار في مهام طلبات الدمج العامة ومنع الأحداث الخطرة مثل pull-request-target من قراءة الخزائن المشفرة؛ مما يسد ثغرات استخراج البيانات عبر السجلات ويوفر خط تسليم مؤتمت وفائق التحصين يمنع أي اختراق."""
    }
}

# ==========================================
# CIC-10: How do you publish builds to internal testing and Play Console?
# ==========================================
DATA["CIC-10"] = {
    "concept_en": """Automating binary deployment to Google Play Console eliminates manual web UI uploads, guarantees reproducible releases, and accelerates internal feedback loops:
- Google Play Developer API Architecture:
  - Google Play provides RESTful publishing APIs (Play Developer API v3) enabling automated package uploads, track assignments, staged rollout updates, and listing metadata synchronization.
  - Automation tools integrate via a Google Cloud Platform Service Account granted Release Manager privileges within the Google Play Console API access settings.
- Industry-Standard Deployment Tooling:
  - Gradle Play Publisher (GPP): A Gradle plugin (`com.github.triplet.play`) allowing native build task execution (e.g., `./gradlew publishReleaseBundle --track internal`). It handles AAB compilation, R8 mapping file ingestion, and API communication in a single Gradle invocation.
  - Fastlane Supply: Part of the Ruby-based Fastlane suite. Separates compilation from publication, widely used in organizations managing multi-platform (iOS and Android) release tooling.
- Mandatory Artifact Requirements:
  - Android App Bundle (AAB): Google Play strictly mandates AABs for new releases, allowing Google Play Dynamic Delivery to split APKs per device density, ABI, and language.
  - De-obfuscation Mapping File (`mapping.txt`): Must be uploaded alongside the AAB so Play Console and Firebase Crashlytics can de-obfuscate stack traces from production crashes.
  - Native Debug Symbols: If the app includes C/C++ libraries via the NDK, unstripped `.so` symbols must be archived and uploaded.
- Tiered Track Strategy:
  - Builds are never published directly to production. The CI pipeline targets the Internal Testing Track, providing near-instant distribution (under 5 minutes without manual app review) to QA and internal dogfooders.
  - Subsequent promotions from Internal to Closed Alpha/Beta and Staged Production are orchestrated via gated API calls or explicit human sign-offs.""",
    "walkthrough_en": """Gradle Play Publisher configuration and deployment pipeline:
```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
    id("com.github.triplet.play") version "3.9.0"
}

play {
    serviceAccountCredentials.set(file(System.getenv("PLAY_SERVICE_ACCOUNT_KEY") ?: "play-key.json"))
    track.set(com.github.triplet.gradle.play.tasks.TrackType.INTERNAL)
    defaultToAppBundles.set(true)
    releaseStatus.set(com.github.triplet.gradle.play.tasks.ReleaseStatus.COMPLETED)
    resolutionStrategy.set(com.github.triplet.gradle.play.tasks.ResolutionStrategy.AUTO)
}
```

```yaml
# .github/workflows/deploy_internal.yml
name: Deploy Internal Testing
on:
  push:
    branches: [ main ]

jobs:
  publish_internal:
    runs-on: ubuntu-latest
    environment: internal-staging
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3

      - name: Provision Service Account Key
        run: echo "${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}" > $HOME/play-key.json

      - name: Build and Publish to Google Play Internal
        env:
          PLAY_SERVICE_ACCOUNT_KEY: ${{ env.HOME }}/play-key.json
          KEYSTORE_FILE_PATH: ${{ secrets.KEYSTORE_PATH }}
          KEYSTORE_STORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEYSTORE_KEY_ALIAS: ${{ secrets.KEYSTORE_ALIAS }}
          KEYSTORE_KEY_PASSWORD: ${{ secrets.KEYSTORE_ALIAS_PASSWORD }}
        run: ./gradlew publishReleaseBundle --track internal

      - name: Purge Credentials
        if: always()
        run: rm -f $HOME/play-key.json
```""",
    "short_en": """Automate Google Play deployment by configuring a Google Cloud Service Account with Release Manager permissions, using Gradle Play Publisher or Fastlane Supply. On merge to main, CI compiles the release Android App Bundle, automatically bundles R8 mapping.txt and native symbols, and uploads directly to the Internal Testing track for rapid distribution without manual console intervention.""",
    "structured_en": """Publishing builds to Google Play requires a secure, automated pipeline that handles binary distribution and observability artifacts simultaneously.
In modern Android delivery, we connect our CI pipeline to the Google Play Developer API using a dedicated Google Cloud Service Account. In Google Play Console, this service account is restricted with release management permissions on specific app packages.
We typically employ Gradle Play Publisher or Fastlane Supply to orchestrate the deployment. The pipeline triggers automatically upon merging release branches, building an obfuscated Android App Bundle using bundleRelease.
Crucially, the publishing task automatically pairs the AAB with the corresponding R8 mapping.txt and native debug symbols, ensuring that Crashlytics and Google Play Vitals can de-obfuscate production crashes immediately.
By routing automated deployments exclusively to the Internal Testing track, builds become available to internal dogfooders and QA teams within minutes, entirely bypassing the multi-hour review delays associated with public production tracks.""",
    "deep_senior_en": """From a release operations and platform reliability standpoint, automating Google Play publishing eliminates error-prone manual web dashboard uploads and ensures cryptographic and diagnostic integrity.
A production deployment pipeline relies on the Google Play Developer API v3, accessed via an automated Service Account key stored securely in CI secrets. We configure tools like Gradle Play Publisher or Fastlane Supply to upload the Android App Bundle directly to the Internal Testing track. Operating on the internal track is an architectural best practice because Google distributes internal builds almost instantaneously without subjecting them to standard app review pipelines, allowing our QA teams to validate release candidates immediately.
Equally vital is the automated archival of diagnostic metadata. A common production failure mode occurs when an engineering team uploads an AAB manually but forgets to upload the R8 mapping.txt or native symbol files. When production crashes occur, stack traces remain obfuscated, turning critical incident triaging into a guessing game. Gradle Play Publisher automatically attaches mapping.txt to the release edit, guaranteeing full Crashlytics readability.
Finally, we implement release governance through track promotion rather than rebuilding binaries. Once an internal release candidate passes dogfooding and automated smoke tests, a downstream workflow promotes that exact, byte-for-byte identical AAB from internal to closed alpha, and eventually to staged production rollout. Recompiling binaries between tracks is strictly prohibited, as rebuilding can introduce subtle toolchain or dependency variations that invalidate prior QA verification.""",
    "meta_ar": {
        "id": "CIC-10",
        "questionAr": "كيف تؤتمت نشر النسخ إلى مسارات الاختبار الداخلي (Internal Testing) ومتجر Google Play؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "أتمتة النشر عبر Google Play Developer API، إعداد حسابات الخدمة السحابية (Service Accounts)، استخدام Gradle Play Publisher وFastlane، رفع ملفات mapping.txt ورموز NDK، وحوكمة ترقية المسارات.",
        "concept_ar": "تعتمد أتمتة نشر التطبيقات إلى Google Play على ربط خطوط الـ CI بواجهة برمجة تطبيقات Google Play Developer API v3 باستخدام حساب خدمة سحابي (Google Cloud Service Account) مخصص يمتلك صلاحيات إدارة الإصدارات. تُستخدم أدوات قياسية مثل إضافة Gradle Play Publisher (GPP) أو Fastlane Supply لأتمتة العملية؛ حيث يقوم خط الـ CI بتجميع حزمة Android App Bundle (AAB) الموقعة ورفعها تلقائياً. وتشترط المعمارية السليمة رفع ملف فك التشويش mapping.txt وملفات رموز الـ C++ غير المجردة (Native Debug Symbols) بالتزامن مع الحزمة لضمان قراءة تقارير الانهيار في Crashlytics. ويتم توجيه النسخ دائماً إلى مسار الاختبار الداخلي (Internal Testing Track) الذي يوفر توزيعاً فورياً للمختبرين خلال دقائق دون انتظار مراجعة المتجر، ثم تُرقّى نفس الحزمة الثنائية إلى المسارات المغلقة والإنتاجية دون إعادة بناء الكود.",
        "walkthrough_ar": """تكوين إضافة Gradle Play Publisher وملف عمل النشر التلقائي:
```kotlin
// app/build.gradle.kts
play {
    serviceAccountCredentials.set(file(System.getenv("PLAY_KEY_PATH") ?: "play-key.json"))
    track.set(com.github.triplet.gradle.play.tasks.TrackType.INTERNAL)
    defaultToAppBundles.set(true)
}
```

```yaml
# .github/workflows/deploy_internal.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Key
        run: echo "${{ secrets.PLAY_JSON_KEY }}" > $HOME/play-key.json
      - name: Publish to Internal Track
        env:
          PLAY_KEY_PATH: ${{ env.HOME }}/play-key.json
        run: ./gradlew publishReleaseBundle --track internal
      - name: Clean
        if: always()
        run: rm -f $HOME/play-key.json
```""",
        "why_it_matters_ar": "رفع النسخ يدوياً عبر لوحة التحكم عرضة للخطأ البشري الشديد ونسيان ملفات mapping.txt؛ والأتمتة تضمن تسليماً سريعاً وموثوقاً لمختبري الجودة مع حماية تشخيص الأعطال.",
        "worked_example_ar": "في خط الـ CI، نستخدم حساب خدمة سحابي مع مفتاح JSON لرفع حزمة AAB المنتجة مع ملف mapping.txt تلقائياً إلى المسار الداخلي، لتصل للمختبرين خلال 3 دقائق.",
        "trade_offs_ar": "استخدام Fastlane يوفر أدوات موحدة لإدارتي أندرويد وiOS معاً ولكنه يتطلب بيئة Ruby إضافية؛ بينما يوفر Gradle Play Publisher تكاملاً أصلياً فائق السرعة داخل مهام Gradle دون أي اعتماديات خارجية.",
        "failure_modes_ar": "رفع حزمة AAB دون ملف mapping.txt المصاحب يجعل كافة سجلات الانهيار في Crashlytics غير قابلة للقراءة ومشفرة بحروف مبهمة، أو بناء حزمة جديدة أثناء الترقية للإنتاج بدلاً من ترقية نفس الملف المختبر.",
        "production_perspective_ar": "في الفرق الناضجة، تُحظر إعادة بناء الـ AAB عند الانتقال من الاختبار الداخلي إلى الإنتاج؛ بل يتم ترقية الحزمة الثنائية ذاتها عبر استدعاء Track Promotion API لضمان مطابقة النسخة المختبرة تماماً.",
        "how_to_answer_ar": "ابدأ بتوضيح الربط عبر Service Account والـ Play Developer API، ثم اذكر الأدوات المستخدمة، وركز على رفع ملفات mapping.txt والرموز الأصلية، واشرح فلسفة النشر للمسار الداخلي وترقية النسخة ذاتها.",
        "talking_points_ar": "حساب الخدمة السحابي Service Account، أداة Gradle Play Publisher وFastlane Supply، رفع ملف mapping.txt، سرعة المسار الداخلي Internal Track، ومبدأ ترقية الحزمة الثنائية دون إعادة بناء.",
        "follow_ups_ar": "كيف تضمن مطابقة النسخة المرفوعة للمسار الداخلي مع النسخة المنشورة للإنتاج؟ وما الحل إذا انتهت صلاحية حساب الخدمة؟",
        "self_check_ar": "هل شرحت آلية الربط عبر Service Account، ورفع ملف mapping.txt، وأهمية المسار الداخلي وترقية الحزمة؟",
        "references_ar": f"- [Google Play Developer API](https://developers.google.com/android-publisher) — التوثيق الرسمي لواجهة برمجة تطبيقات نشر وإدارة تطبيقات أندرويد.\n- [Gradle Play Publisher Plugin](https://github.com/Triple-T/gradle-play-publisher) — الإضافة القياسية لأتمتة نشر حزم أندرويد مباشرة عبر Gradle.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نؤتمت النشر إلى Google Play بربط الـ CI مع Play Developer API عبر حساب خدمة سحابي معتمد، وباستخدام أدوات مثل Gradle Play Publisher أو Fastlane Supply. يقوم خط العمل ببناء حزمة AAB الموقعة ورفعها مع ملفات mapping.txt والرموز الأصلية إلى مسار الاختبار الداخلي، مما يوفر توزيعاً فورياً للمختبرين دون انتظار مراجعة المتجر.""",
        "best_answer_ar": """أتمتة النشر إلى متجر Google Play تضمن تسليماً سريعاً وتلغي الأخطاء البشرية الناتجة عن الرفع اليدوي.
نبدأ بإنشاء حساب خدمة سحابي على Google Cloud Platform ومنحه صلاحيات إدارة الإصدارات داخل لوحة تحكم Google Play، ثم نحفظ مفتاح الـ JSON الخاص به كسر مشفر في الـ CI.
نعتمد على أدوات مثل إضافة Gradle Play Publisher لتنفيذ عملية النشر تلقائياً بمجرد دمج التعديلات في الفرع الرئيسي؛ حيث يتولى الـ CI بناء حزمة Android App Bundle الموقعة ورفعها مباشرة إلى مسار الاختبار الداخلي.
ومن الركائز الأساسية في هذه العملية التأكد من رفع ملف mapping.txt الناتج عن تشويش R8 وملفات رموز لغة سي بلس بلس مع الحزمة في نفس العملية؛ لضمان فك تشفير وتوضيح مسببات الانهيارات في Crashlytics وAndroid Vitals.
كما نعتمد سياسة ترقية المسارات برفع النسخة المختبرة ذاتها من المسار الداخلي إلى المسارات التجريبية ثم إلى الإنتاج تدريجياً، ونمنع تماماً إعادة تجميع الكود بين المسارات لضمان سلامة النسخة المعتمدة.""",
        "deep_answer_ar": """من منظور هندسة الإصدارات وضمان موثوقية المنصة، تعد أتمتة النشر إلى Google Play حجر الزاوية لتسريع دورات التحقق البرمجي وحماية أدوات التشخيص والمراقبة الحية في بيئة الإنتاج.
يعتمد الخط المؤتمت على واجهة Play Developer API v3 عبر حساب خدمة سحابي بصلاحيات محددة لإدارة الإصدارات دون المساس بباقي إعدادات الحساب. ونوجه الحزم الموقعة دائماً إلى مسار الاختبار الداخلي؛ وميزة هذا المسار تكمن في توفير الحزمة للمختبرين وفريق العمل خلال دقائق معدودة متجاوزاً فترات انتظار المراجعة اليدوية للمتجر، مما يسرع التحقق من النسخ التجريبية وجمع الملاحظات السريعة.
أحد أخطر الفخاخ التي تقع فيها الفرق هو الرفع اليدوي الذي غالباً ما يغفل رفع ملف mapping.txt وملفات الرموز الأصلية؛ مما يحول تشخيص حوادث الإنتاج إلى كابوس بسبب تشفير أسماء الدوال والكلاسات في سجلات Crashlytics وظهور تقارير الأعطال برموز غير مفهومة. أتمتة الرفع عبر Gradle Play Publisher تضمن ربط ملف الـ mapping والرموز البرمجية بكل إصدار بصورة حتمية متزامنة في نفس استدعاء النشر.
وفضلاً عن ذلك، نطبق مبدأ حوكمة الحزمة الثنائية الصارمة؛ فعندما تجتاز النسخة الاختبارات الداخلية، نقوم بترقية نفس ملف الـ AAB إلى مسارات الإنتاج عبر واجهة برمجة التطبيقات دون إعادة بنائه من الكود المصدري؛ لأن إعادة البناء قد تتسبب في تغير غير مقصود في المكتبات أو الأدوات المستعملة، مما يبطل كافة الاختبارات السابقة ويهدد استقرار المنظومة الإنتاجية للمستخدمين."""
    }
}

# ==========================================
# CIC-11: How do you automate versioning, changelog, and tagging?
# ==========================================
DATA["CIC-11"] = {
    "concept_en": """Automating release versioning, release notes, and Git metadata tagging establishes traceability between user-facing releases, issue trackers, and exact source commits:
- Semantic Versioning (SemVer) for `versionName`:
  - Public mobile versions follow `MAJOR.MINOR.PATCH` semantics (e.g., `2.14.1`).
  - Major increments represent breaking changes or massive redesigns; Minor increments signify backward-compatible new feature additions; Patch increments represent critical bug fixes.
- Android `versionCode` Mechanics:
  - Google Play mandates that every newly uploaded binary has a strictly positive, monotonically increasing 32-bit integer `versionCode` (cannot exceed 2,100,000,000).
  - Best-practice calculation strategies:
    - Git Commit Count: Derived via `git rev-list --count HEAD`. Naturally monotonic along a linear Git history.
    - CI Monotonic Counter: Managed by CI platforms (e.g., GitHub Actions `github.run_number` combined with a base offset).
    - Timestamp Formula: Encodes year, month, day, and build sequence (e.g., `YYMMDDHH`), though teams must guard against integer overflow.
- Conventional Commits Architecture:
  - Commit messages enforce strict prefixes: `feat:` for new features, `fix:` for bug fixes, `perf:` for performance optimizations, `refactor:`, `chore:`, and `BREAKING CHANGE:`.
  - Enforced locally via Git hooks (using Husky or Lefthook) and verified on CI pull request gates.
- Automated Changelog & Tagging Tooling:
  - Tools such as Standard-Version, Semantic-Release, or Release-It parse commit history since the previous tag.
  - Automatically calculates the next SemVer version, updates `version.properties` and `CHANGELOG.md`, creates an immutable annotated Git tag (e.g., `v2.14.0`), and pushes the commit and tag back to the repository using a verified bot token.""",
    "walkthrough_en": """Gradle versioning logic and GitHub Actions release tagging workflow:
```kotlin
// app/build.gradle.kts
import java.io.FileInputStream
import java.util.Properties

val versionPropsFile = file("version.properties")
val versionProps = Properties().apply {
    if (versionPropsFile.exists()) load(FileInputStream(versionPropsFile))
}

val major = versionProps.getProperty("major", "1").toInt()
val minor = versionProps.getProperty("minor", "0").toInt()
val patch = versionProps.getProperty("patch", "0").toInt()

// Calculate monotonic versionCode using Git commit count
val gitCommitCount = providers.exec {
    commandLine("git", "rev-list", "--count", "HEAD")
}.standardOutput.asText.get().trim().toIntOrNull() ?: 1

android {
    defaultConfig {
        versionCode = gitCommitCount
        versionName = "$major.$minor.$patch"
    }
}
```

```yaml
# .github/workflows/tag_and_release.yml
name: Release Tagging & Changelog
on:
  push:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.RELEASE_BOT_PAT }} # Bot token with write permissions

      - name: Setup Node.js for Release Tooling
        uses: actions/setup-node@v4
        with: { node-version: '20' }

      - name: Calculate SemVer and Generate Changelog
        run: |
          npx standard-version --sign
          git push --follow-tags origin main
```""",
    "short_en": """Automate release management using Conventional Commits to derive Semantic Versioning for versionName and generating CHANGELOG.md. Derive Android versionCode monotonically from git rev-list commit count or CI build numbers to ensure continuous ascension. Tools like standard-version bump versions, create annotated Git tags, and push metadata automatically on merge.""",
    "structured_en": """Automating versioning, changelog generation, and Git tagging guarantees consistency between deployed binaries and source control.
For user-facing releases, we adopt Semantic Versioning (MAJOR.MINOR.PATCH) for versionName. For the Android platform requirement, versionCode must be a strictly increasing integer. We compute versionCode automatically using Git commit counts via git rev-list or CI run counters, avoiding manual increments that cause merge conflicts.
To automate changelogs, the team adopts Conventional Commits, using standard prefixes like feat, fix, and perf. In the CI pipeline upon merging to main, tools like standard-version or semantic-release parse commit messages since the last release tag.
The tool automatically determines the next version bump, generates or appends formatted release notes to CHANGELOG.md, creates an annotated Git tag such as v2.5.0, and pushes the changes back to origin using a service bot token. This ensures end-to-end traceability for every production build.""",
    "deep_senior_en": """From a software configuration management and release governance standpoint, manual version bumps and hand-written changelogs are severe anti-patterns that create release bottlenecks and untraceable regressions.
A production-grade mobile versioning architecture decouples marketing versioning from platform execution constraints. Google Play enforces a 32-bit positive integer constraint on versionCode that can never decrease. Manually editing this value in gradle files frequently results in parallel branches claiming the same number, blocking deployment. We automate versionCode derivation using git commit counts along the mainline or monotonic CI build run counters, ensuring linear ascension across all releases.
For human-facing versioning, we standardize team commits on the Conventional Commits specification. By validating commit headers during pull request checks, we ensure that every commit carries machine-readable intent. When a release batch merges into mainline, automated tools analyze the git graph, accurately determine whether to bump a major, minor, or patch version, and synthesize a structured CHANGELOG.md grouping user features and bug fixes.
Finally, release tagging must be cryptographically immutable. The automated pipeline creates an annotated, signed Git tag and commits the updated version metadata back to trunk using an authenticated machine bot account. This tag triggers downstream deployment jobs and links directly into Sentry or Crashlytics release dashboards. When an alert fires in production, engineers can trace the exact commit SHA and changelog entries, drastically accelerating mean time to resolution.""",
    "meta_ar": {
        "id": "CIC-11",
        "questionAr": "كيف تؤتمت إدارة أرقام الإصدارات (Versioning)، وسجل التغييرات (Changelog)، والوسوم (Git Tags)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تطبيق Semantic Versioning، حساب الـ versionCode بشكل تصاعدي حتمي، معايير Conventional Commits، أتمتة توليد CHANGELOG.md، وإنشاء وإدارة وسوم Git Tags آلياً.",
        "concept_ar": "تعتمد أتمتة إدارة الإصدارات على ربط رسائل الالتزام (Commit Messages) بأرقام الإصدارات وسجلات التغيير لضمان التتبع البرمجي الكامل: يُستخدم نظام الترقيم الدلالي (Semantic Versioning: MAJOR.MINOR.PATCH) لتحديد رقم النسخة الظاهر للمستخدمين (versionName)؛ حيث يشير Major للتغييرات الجذرية، وMinor للميزات الجديدة، وPatch لإصلاح الأعطال. أما رقم الإصدار الفني للنظام (versionCode) فيشترط متجر Google Play أن يكون رقماً صحيحاً يتزايد تصاعدياً بصورة حتمية، ويتم حسابه برمجياً من إجمالي عدد كوميتات Git أو رقم تشغيل الـ CI لتفادي التضارب اليدوي. وتفرض الفرق معايير الالتزام القياسية (Conventional Commits) مثل feat وfix، مما يتيح لأدوات مثل standard-version أو semantic-release قراءة سجل الكوميتات تلقائياً، وتحديد نوع الترقية المناسب، وتوليد ملف CHANGELOG.md، وإنشاء وسم Git معتمد وموقع مثل v2.1.0 ورفعه إلى المستودع عبر حساب آلي معتمد.",
        "walkthrough_ar": """توليد versionCode من عدد كوميتات Git وأتمتة الوسوم في GitHub Actions:
```kotlin
// app/build.gradle.kts
val gitCommitCount = providers.exec {
    commandLine("git", "rev-list", "--count", "HEAD")
}.standardOutput.asText.get().trim().toIntOrNull() ?: 1

android {
    defaultConfig {
        versionCode = gitCommitCount
        versionName = "2.4.0"
    }
}
```

```yaml
# .github/workflows/release_tag.yml
jobs:
  tag_release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0, token: ${{ secrets.BOT_TOKEN }} }
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Bump Version and Push Tag
        run: |
          npx standard-version
          git push --follow-tags origin main
```""",
        "why_it_matters_ar": "الترقيم اليدوي يسبب نزاعات دمج مستمرة وتضارب أرقام النسخ في المتجر؛ والأتمتة تربط كل نسخة في الإنتاج بنقطة محددة ودقيقة في تاريخ Git.",
        "worked_example_ar": "نلزم المطورين بكتابة feat: add login وfix: resolve crash، ثم تشغل أداة standard-version في الـ CI لزيادة Minor أو Patch آلياً، وتحديث CHANGELOG.md، وتوليد وسم Git ورفعه.",
        "trade_offs_ar": "حساب versionCode من وقت النظام بالثواني قد يسبب تجاوز حد الأرقام الصحيحة في أندرويد؛ بينما الاعتماد على عدد كوميتات Git يوفر أرقاماً متسلسلة بدقة طالما أن تاريخ الفرع خطي.",
        "failure_modes_ar": "أخطر الأخطاء هو حدوث سباق بين فرعين مختلفين يحملان نفس رقم versionCode مما يرفضه المتجر، أو السماح بتعديل أرقام الإصدارات يدوياً مما يكسر تسلسل النشر.",
        "production_perspective_ar": "في بيئات الإنتاج، تُربط وسوم Git مباشرة بأنظمة المراقبة مثل Crashlytics؛ بحيث يظهر اسم الإصدار والوسم تلقائياً أمام مهندسي الدعم لتحديد الكوميت المسؤول عن أي عطل بدقة.",
        "how_to_answer_ar": "ميز أولاً بين SemVer للـ versionName والتزايد الحتمي للـ versionCode، ثم اشرح دور Conventional Commits وأدوات التوليد الآلي لسجل التغييرات، واختم بإنشاء وسوم Git وتتبعها في الإنتاج.",
        "talking_points_ar": "نظام SemVer، قيود versionCode في أندرويد، استخراج الرقم عبر git rev-list، معايير Conventional Commits، أداة standard-version، وربط وسوم Git بالـ Crashlytics.",
        "follow_ups_ar": "ماذا تفعل إذا وصل رقم versionCode للحد الأقصى في أندرويد؟ وكيف تمنع سباق التوليد المتزامن للوسوم في الـ CI؟",
        "self_check_ar": "هل فرقت بين versionName وversionCode، وشرحت معايير Conventional Commits وأتمتة الـ Tags؟",
        "references_ar": f"- [Semantic Versioning 2.0.0](https://semver.org/) — المواصفة القياسية لإدارة أرقام الإصدارات البرمجية.\n- [Conventional Commits](https://www.conventionalcommits.org/) — المعيار الهندسي لتوثيق رسائل الالتزام التلقائية.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نؤتمت الإصدارات باعتماد الترقيم الدلالي SemVer لرقم versionName، وحساب versionCode تصاعدياً من عدد كوميتات Git أو عداد الـ CI لمنع التضارب. ونلزم الفريق بمعايير Conventional Commits لتشغيل أدوات مثل standard-version التي تقرأ التعديلات وتحدث سجل CHANGELOG.md وتولد وسوم Git آلياً عند الدمج.""",
        "best_answer_ar": """أتمتة أرقام الإصدارات وسجلات التغيير والوسوم تحقق اتساقاً كاملاً بين الحزم المنشورة وتاريخ الكود.
بالنسبة للأرقام، نستخدم نظام الترقيم الدلالي SemVer لتحديد رقم النسخة الظاهر للمستخدمين، بينما نشتق رقم versionCode الداخلي بصورة حتمية متزايدة باستخدام إجمالي عدد كوميتات Git عبر أمر git rev-list أو من خلال عداد الـ CI؛ مما يلغي التعديل اليدوي ونزاعات الدمج نهائياً.
ولأتمتة سجل التغييرات، نلزم المطورين باتباع معايير Conventional Commits لكتابة رسائل واضحة مثل feat للميزات وfix للإصلاحات. وفور دمج التعديلات في الفرع الرئيسي، تشغل أدوات أتمتة مثل standard-version أو semantic-release.
تقوم هذه الأدوات بقراءة رسائل الكوميت منذ آخر إصدار، وتحديد قيمة الزيادة المطلوبة تلقائياً، وتحديث ملف CHANGELOG.md، ثم إنشاء وسم Git معتمد مثل v2.4.0 ودفعه إلى المستودع باستخدام حساب آلي مخصص؛ مما يتيح تتبع كل نسخة إنتاجية بدقة متناهية.""",
        "deep_answer_ar": """من منظور حوكمة التكوين البرمجي وهندسة الإصدارات، يعد التعديل اليدوي لأرقام الإصدارات وكتابة سجلات التغيير يدوياً من الممارسات العتيقة التي تزيد من احتمالية الخطأ البشري وتعطل دورات الإصدار المنتظمة.
في تطبيقات أندرويد، يفرض متجر Google Play قيداً صارماً على رقم versionCode بألا يتجاوز حداً معيناً وأن يتزايد دائماً في كل ملف جديد؛ ولذلك فإن حسابه آلياً من عدد الكوميتات على الفرع الرئيسي عبر أمر git rev-list أو عبر عداد الـ CI المشترك يمنع تماماً تعارض النسخ بين المطورين ويضمن تسلسلاً تصاعدياً حتمياً لا يمكن أن ينكسر مهما تفرعت العمليات الهندسية.
وعلى صعيد التواصل وتوثيق التغييرات، يعد الالتزام بمعيار Conventional Commits قاعدة أساسية لا غنى عنها؛ حيث يتم التحقق من بادئات الرسائل في بوابات الـ PR، مما يوفر بيئة غنية للبيانات الآلية. وعند إطلاق الإصدار، تفحص الأدوات المتخصصة شجرة Git لإنشاء ملف CHANGELOG.md منظم يقسم التعديلات بوضوح بين ميزات جديدة وإصلاحات فنية وتحسينات للأداء العام.
وأخيراً، يتم تأمين وسوم Git برمجياً وربطها بأنظمة مراقبة الأعطال مثل Crashlytics؛ فبمجرد رصد انهيار غير متوقع في الإنتاج، يستطيع مهندس البرمجيات استدعاء الوسم المرجعي والوصول الفوري لكافة الالتزامات البرمجية التي تضمنها ذلك الإصدار بدقة، مع إمكانية إعادة إنتاج نفس النسخة وتحديد السبب الجذري للخلل وإصلاحه بأسرع وقت ممكن."""
    }
}

# ==========================================
# CIC-12: How do you reduce Gradle cold-build and CI execution times?
# ==========================================
DATA["CIC-12"] = {
    "concept_en": """Optimizing Android CI build durations and mitigating cold-start penalties requires architectural intervention across caching, configuration, JVM ergonomics, and modular execution:
- Bottleneck Identification via Gradle Build Scans:
  - Profiling build execution with `--scan` or Gradle Profiler identifies task execution breakdown, garbage collection pressure, non-cacheable task executions, and long configuration phases.
- Remote Build Cache Architecture:
  - In CI environments, runner instances are ephemeral and destroy their local caches upon termination.
  - Enabling Gradle Remote Build Cache (via Gradle Develocity or self-hosted HTTP/S3 cache nodes) enables runners to download precompiled task outputs generated by previous CI runs or developer workstations, turning long compilation steps into instantaneous cache hits (`FROM-CACHE`).
- Gradle Configuration Cache:
  - Enabling `org.gradle.configuration-cache=true` records task dependency graphs on the first run.
  - In subsequent runs, Gradle skips the costly build script evaluation phase entirely, launching tasks immediately.
- Dependency & Toolchain Persistence:
  - Utilizing `gradle/actions/setup-gradle` preserves `~/.gradle/caches` and wrapper binaries across workflow invocations.
  - Pre-baking Android SDK platforms and build-tools into custom CI Docker images avoids downloading SDK components during pipeline startup.
- Selective Execution via Affected Module Detection:
  - Utilizing tools like `affected-module-detector` analyzes Git diffs against the target branch.
  - Runs unit tests and lint only on modified modules and their downstream dependents, bypassing dozens of untouched modules in large multi-module repositories.
- Daemon Management & JVM Tuning:
  - Ephemeral CI runners benefit from allocating adequate JVM heap space (`-Xmx4g -XX:+UseG1GC`) while disabling in-memory file system watching (`org.gradle.vfs.watch=false`) which is redundant on transient virtual machines.""",
    "walkthrough_en": """Gradle enterprise caching and CI runner tuning configuration:
```properties
# gradle.properties
# Enable parallel execution across decoupled modules
org.gradle.parallel=true

# Enable build caching and configuration caching
org.gradle.caching=true
org.gradle.configuration-cache=true

# Optimize JVM memory allocation and garbage collection for CI
org.gradle.jvmargs=-Xmx4096m -XX:+UseG1GC -XX:+ParallelRefProcEnabled

# Disable file system watching on ephemeral CI containers
org.gradle.vfs.watch=false
```

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
    }
    remote<HttpBuildCache> {
        url = uri("https://gradle-cache.company.internal/cache/")
        isPush = System.getenv("CI") == "true" && System.getenv("GITHUB_REF") == "refs/heads/main"
        credentials {
            username = System.getenv("GRADLE_CACHE_USER")
            password = System.getenv("GRADLE_CACHE_PASSWORD")
        }
    }
}
```

```yaml
# .github/workflows/fast_ci.yml
name: Optimized PR Build
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with:
          cache-read-only: true

      # Run tests only on modules affected by this PR
      - name: Run Affected Unit Tests
        run: ./gradlew runAffectedUnitTests -Paffected_module_detector.baseRef=origin/main
```""",
    "short_en": """Reduce Gradle CI cold-build times by combining a Remote Build Cache to share compiled outputs across runners, enabling Configuration Cache to skip configuration phases, and using affected-module-detector to test only changed code. Tune JVM memory with G1GC and persist wrapper caches to avoid redundant downloads on ephemeral runners.""",
    "structured_en": """Accelerating Gradle cold builds on CI requires eliminating redundant work across the build lifecycle.
We begin by diagnosing execution bottlenecks using Gradle Build Scans to identify slow plugins and non-cacheable tasks. Because CI runners are ephemeral and start with empty local caches, the most impactful optimization is introducing a Gradle Remote Build Cache. This allows CI runners to fetch precompiled outputs from prior runs, transforming expensive Kotlin compilation and R8 tasks into near-instant cache hits.
Next, we enable the Configuration Cache to bypass the build script evaluation phase on recurring runs. In multi-module codebases, we apply affected-module-detector so pull request pipelines compile and test only the modules modified by the diff alongside their direct dependents, completely skipping dozens of unaffected modules.
Finally, we configure runner infrastructure by persisting dependency directories with GitHub Actions Gradle setup, pre-installing the Android SDK in custom runner images, and allocating four gigabytes of heap with G1GC. This comprehensive setup cuts CI execution times from twenty minutes to under five.""",
    "deep_senior_en": """From a developer productivity engineering and infrastructure cost perspective, cold Gradle builds on CI runners represent a massive tax on team iteration velocity.
The fundamental problem with ephemeral CI runners is that they lack warm build daemons and local build caches. Every job starts cold, downloading dependencies and recompiling code from scratch. To overcome this, our primary architecture investment is a Remote Build Cache hosted on an internal S3 or HTTP node. When master builds run, they push compiled artifacts to the remote cache; subsequent pull request builds query the cache and reuse bytecode outputs, slashing compilation and Dexing times by up to seventy percent.
In parallel, we eliminate configuration phase overhead by turning on the Gradle Configuration Cache. Gradle evaluates project dependencies once, serializes the execution graph, and skips configuration entirely on subsequent runs. To prevent unnecessary work across expansive codebases, we integrate affected module detection tools. Instead of running testDebugUnitTest across fifty modules, our pipeline analyzes Git merge bases and executes tests strictly against the delta graph of changed modules and their consumers.
On the virtual machine level, we tune Gradle JVM arguments specifically for ephemeral instances. We allocate four gigabytes of heap with modern G1 garbage collection, enable parallel execution across subprojects, and disable file system watching, which wastes memory on transient runners. By persisting Gradle wrapper and dependency caches between workflow runs, we transform slow cold builds into snappy, high-throughput delivery pipelines.""",
    "meta_ar": {
        "id": "CIC-12",
        "questionAr": "كيف تقلل أوقات البناء البارد (Cold-Build) وتنفيذ خطوط الـ CI في Gradle؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "تشخيص اختناقات Gradle عبر Build Scans، إعداد كاش البناء البعيد (Remote Build Cache)، تفعيل كاش التكوين (Configuration Cache)، فحص الموديولات المتأثرة فقط (Affected Module Detection)، وضبط ذاكرة الـ JVM.",
        "concept_ar": "يتطلب تقليص وقت البناء البارد وتسريع خطوط الـ CI تدخلاً معمارياً يعالج مراحل البناء المختلفة: يبدأ التحليل بتشخيص الاختناقات عبر مسح البناء (Gradle Build Scan) لتحديد المهام غير القابلة للكاش واستهلاك الذاكرة. ولأن خوادم الـ CI مؤقتة وتبدأ دائماً بقرص فارغ، تعد معمارية كاش البناء البعيد (Remote Build Cache) الحل الأقوى؛ حيث يرفع الفرع الرئيسي مخرجات التجميع إلى سيرفر كاش سحابي، وتسترجع خوادم الـ PR هذه المخرجات دون إعادة تجميعها. ثانياً، يُفعل كاش التكوين (Configuration Cache) لتخطي مرحلة قراءة ملفات الإعدادات وبناء شجرة المهام بعد أول تشغيل. ثالثاً، تُستخدم أدوات فحص الموديولات المتأثرة (Affected Module Detector) لقصر الاختبارات والتحليل على الموديولات المعدلة في الـ PR وفروعها المعتمدة فقط، مع ضبط ذاكرة الـ JVM عبر محرك G1GC وإلغاء مراقبة الملفات VFS غير الضرورية على الخوادم المؤقتة.",
        "walkthrough_ar": """إعداد خصائص Gradle والكاش البعيد وفحص الموديولات المعدلة:
```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx4g -XX:+UseG1GC
org.gradle.vfs.watch=false
```

```yaml
# .github/workflows/pr_build.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3
        with: { cache-read-only: true }
      - name: Run Only Affected Tests
        run: ./gradlew runAffectedUnitTests -Paffected_module_detector.baseRef=origin/main
```""",
        "why_it_matters_ar": "بطء خطوط الـ CI يهدر ساعات العمل ويزيد تكاليف السيرفرات السحابية ويعطل دمج التعديلات العاجلة، مما يصيب الفريق بالإحباط ويبطئ وتيرة التطوير.",
        "worked_example_ar": "في مشروع يحتوي على 60 موديول، قمنا بتفعيل الكاش البعيد وفحص الموديولات المعدلة فقط؛ فانخفض زمن فحص الـ PR من 25 دقيقة إلى 4 دقائق فقط بتخطي الموديولات السليمة.",
        "trade_offs_ar": "تشغيل كافة الاختبارات في كل PR يضمن ثقة كاملة بنسبة مئة بالمئة ولكنه يستهلك وقتاً طويلاً ومكلفاً؛ بينما فحص الموديولات المتأثرة فقط يقلص الوقت بنسبة 80% مع الاعتماد على المسار الليلي الشامل.",
        "failure_modes_ar": "أخطر الأخطاء هو كتابة مهام Gradle بطريقة تكسر شروط الكاش (مثل استخدام الوقت الحالي أو مسارات مطلقة كمدخلات للمهمة)، مما يمنع استرجاع المخرجات من الكاش البعيد.",
        "production_perspective_ar": "في الفرق الكبرى، تُجهز صور Docker مخصصة لخوادم الـ CI تحتوي مسبقاً على الـ Android SDK وأحدث إصدارات الأدوات لتفادي تنزيلها مع كل عملية بناء جديدة.",
        "how_to_answer_ar": "ابدأ بتوضيح أدوات التشخيص عبر Build Scan، ثم ركز على تفعيل الكاش البعيد وكاش التكوين، واشرح تقنية فحص الموديولات المتأثرة وضبط إعدادات الـ JVM للسيرفرات المؤقتة.",
        "talking_points_ar": "أداة Gradle Build Scan، الكاش البعيد Remote Build Cache، كاش التكوين Configuration Cache، أداة Affected Module Detector، وضبط ذاكرة JVM بـ G1GC.",
        "follow_ups_ar": "كيف تتأكد من أن مهام Gradle قابلة للكاش التام وتتجنب Cache Misses؟ ومتى يجب تعطيل فحص الموديولات المتأثرة وتشغيل البناء الكامل؟",
        "self_check_ar": "هل شرحت كاش البناء البعيد، كاش التكوين، وفحص الموديولات المتأثرة وضبط الـ JVM؟",
        "references_ar": f"- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html) — الدليل الرسمي لإعداد واستخدام كاش البناء المحلي والبعيد.\n- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html) — التوثيق الرسمي لتفعيل كاش مرحلة التكوين وتسريع البناء.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نقلل وقت بناء الـ CI بتفعيل كاش البناء البعيد لمشاركة مخرجات التجميع بين السيرفرات، وتفعيل كاش التكوين لتخطي قراءة الإعدادات، واستخدام أداة Affected Module Detector لاختبار الموديولات المعدلة فقط. كما نضبط ذاكرة الـ JVM مع محرك G1GC ونحتفظ بكاش الاعتماديات بين مرات التشغيل.""",
        "best_answer_ar": """تقليص أوقات البناء في بيئات الـ CI يعتمد على القضاء على العمل المتكرر في كافة مراحل دورة حياة Gradle.
نبدأ بتشخيص أسباب البطء عبر مسح البناء لمعرفة المهام التي تستغرق وقتاً طويلاً. ولأن سيرفرات الـ CI تبدأ دائماً بقرص فارغ، فإن أهم استثمار هو إعداد كاش البناء البعيد؛ حيث يرفع الفرع الرئيسي مخرجات المهام إلى خادم كاش داخلي، فتسترجع سيرفرات الـ PR هذه المخرجات الجاهزة وتتحول عمليات التجميع المعقدة إلى استرجاع فوري.
إلى جانب ذلك، نفعل كاش التكوين لتجاوز مرحلة قراءة ملفات البناء في كل مرة لا تتغير فيها الإعدادات. وفي المشاريع الكبيرة متعددة الموديولات، نستخدم أداة Affected Module Detector لقصر الفحص على الموديولات التي شملها التعديل فقط مع الموديولات المعتمدة عليها، متجاوزين عشرات الموديولات غير المتأثرة.
وأخيراً، نضبط إعدادات السيرفر عبر حفظ مجلد كاش الاعتماديات، وتخصيص ذاكرة كافية للـ JVM باستخدام محرك تجميع المهملات الحديث، مع إيقاف مراقبة الملفات التلقائية غير المفيدة في السيرفرات المؤقتة؛ مما يقلص زمن الفحص لأقل من خمس دقائق.""",
        "deep_answer_ar": """من منظور إنتاجية المطورين وتكلفة البنية التحتية، تمثل عمليات البناء الباردة على سيرفرات الـ CI المؤقتة ضريبة باهظة تبطئ حركة الفرق الهندسية.
المعضلة الأساسية في السيرفرات المؤقتة هي انعدام الذاكرة المشتركة؛ فكل سيرفر يبدأ من الصفر ويعيد تجميع كود لم يطرأ عليه أي تغيير. ولحل هذه المشكلة جذرياً، نستثمر في كاش البناء البعيد؛ فعند اكتمال البناء على الفرع الرئيسي، تُرفع المخرجات للسيرفر السحابي، لتقوم سيرفرات طلبات الدمج بتنزيل المخرجات الجاهزة بدلاً من إعادة ترجمة كود كوتلن وDEXing، مما يختصر أكثر من ستين بالمئة من الوقت.
وبالتوازي مع ذلك، نتغلب على بطء مرحلة الإعداد بتفعيل Configuration Cache؛ حيث يحفظ Gradle شجرة المهام بعد أول تقييم ويتخطى مرحلة المعالجة في المرات اللاحقة. كما نطبق مبدأ التنفيذ الانتقائي في المشاريع الضخمة؛ فبدلاً من تشغيل اختبارات الوحدة على ستين موديولاً، تحلل الأداة فارق الكود في Git وتوجه الاختبارات حصراً نحو الموديولات المتأثرة.
وعلى مستوى نظام التشغيل الافتراضي، نضبط معاملات الـ JVM لتخصيص أربعة غيغابايت مع محرك G1GC ونلغي ميزة مراقبة الملفات التي تستهلك الذاكرة دون جدوى في بيئة تنتهي صلاحيتها بانتهاء المهمة. وبدمج ذلك مع الاحتفاظ بالاعتماديات في كاش GitHub Actions، نتحول من خطوط بطيئة تستغرق نصف ساعة إلى بيئة عمل فائقة السرعة والاستجابة."""
    }
}

# ==========================================
# CIC-13: How do you deal with flaky tests, retries, and quarantine policies?
# ==========================================
DATA["CIC-13"] = {
    "concept_en": """Flaky tests—tests that exhibit non-deterministic pass/fail outcomes on identical commit SHAs—erode developer trust, block merge queues, and waste CI compute:
- Root Causes of Test Flakiness:
  - Timing and Asynchrony: Using arbitrary delays like `Thread.sleep()` instead of coroutine virtual time (`StandardTestDispatcher`, `runTest`, Turbine) or Espresso Idling Resources.
  - Shared State and Side Effects: Static singletons, in-memory databases, or preferences leaking state between independent test cases.
  - Main Thread Starvation: Resource contention on constrained CI runners causing animation or layout timeouts.
- Bounded Retries Architecture:
  - Using tools like the Gradle Test Retry Plugin (`org.gradle.test-retry`).
  - Strict Operational Rule: Retries must be bounded and monitored (e.g., `maxRetries = 1`, `maxFailures = 5`).
  - Retries prevent a single intermittent network blip or race condition from failing an entire build, but must NEVER be allowed to silently mask defects. CI logs must flag tests that passed only on retry.
- Test Quarantine Policy:
  - When a test is identified as flaky, it is immediately decorated with a `@FlakyTest` or `@Quarantined` annotation.
  - The primary pull request pipeline filters out quarantined tests, preventing them from blocking developer merges.
  - Quarantined tests are executed in scheduled non-blocking nightly observability pipelines to collect statistical flake rates.
- Flaky Test SLA & Engineering Budget:
  - A quarantined test is treated as a P1 bug assigned to the owning feature team.
  - Strict SLA: The test must be diagnosed and resolved with deterministic synchronization within one sprint, or permanently deleted if it provides insufficient signal. Indefinite quarantine is strictly forbidden.""",
    "walkthrough_en": """Gradle test retry plugin configuration and quarantine test filtering:
```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
    id("org.gradle.test-retry") version "1.5.8"
}

tasks.withType<Test>().configureEach {
    retry {
        // Only retry on CI runners
        val isCi = System.getenv("CI") == "true"
        maxRetries.set(if (isCi) 1 else 0)
        maxFailures.set(5) // Stop build if 5 tests fail to prevent retry runaway
        failOnPassedAfterRetry.set(false) // Allow build to pass, but record flake
    }

    // Filter out quarantined tests on PR builds
    useJUnitPlatform {
        if (project.hasProperty("excludeQuarantine")) {
            excludeTags("Quarantine")
        }
    }
}
```

```kotlin
// Example quarantined test file
@Tag("Quarantine")
@Test
fun testFlakyCheckoutAnimationFlow() = runTest {
    // Flagged for investigation due to CI race condition on runner VMs
}
```

```yaml
# .github/workflows/pr_checks.yml
- name: Run Unit Tests (Excluding Quarantined)
  run: ./gradlew testDebugUnitTest -PexcludeQuarantine
```""",
    "short_en": """Address flaky tests by combining bounded retries via the Gradle Test Retry plugin, an immediate quarantine policy using custom test tags to unblock PR merges, and routing quarantined tests to nightly observability suites. Enforce a strict one-sprint SLA to fix async timing issues or delete non-viable tests to prevent eroding suite credibility.""",
    "structured_en": """Managing flaky tests requires balancing immediate developer productivity against long-term test suite reliability.
The primary causes of flakiness in Android are race conditions in asynchronous coroutines, animation timing mismatches, and shared static state. To protect developer momentum on pull requests, we configure the Gradle Test Retry plugin with bounded retries, allowing a maximum of one retry per failing test while capping total failures at five to prevent runaway build loops.
However, retries merely buy time; they do not solve flakiness. When a test flakes repeatedly, we apply a Quarantine annotation to immediately exclude it from the PR blocking gate. This unblocks the team while routing the test into a scheduled, non-blocking nightly pipeline that tracks pass-fail statistics.
Critically, we enforce a strict team SLA: quarantined tests are treated as high-priority bugs. The owning team has one sprint to refactor the test using deterministic tools like Turbine and virtual test dispatchers, or delete the test entirely if its value does not justify the maintenance burden.""",
    "deep_senior_en": """From a quality engineering and team operations perspective, flaky tests are cancer to software delivery. When tests fail unpredictably on identical code, developers lose faith in the entire test suite, ignoring legitimate regression failures and resorting to blind retries.
To maintain high velocity without surrendering quality, we implement a three-tiered defense: bounded mitigation, quarantine isolation, and root-cause remediation. First, at the build level, we configure the Gradle Test Retry plugin. Crucially, retries must be strictly bounded to a single attempt. Unbounded retries turn CI pipelines into a game of roulette and dramatically inflate runner costs. Furthermore, every test that passes only after a retry is logged and reported to an observability dashboard as a flake event.
Second, tests exhibiting chronic flakiness are immediately quarantined using JUnit tags. Pull request pipelines pass a property excluding the Quarantine tag, instantly removing the blocker from developer queues. Quarantined tests do not disappear; they run in continuous nightly runs where they are subjected to stress loops of fifty consecutive executions to isolate race conditions.
Finally, quarantine governance requires an ironclad SLA. A quarantined test is an open technical debt ticket. We give feature teams a one-sprint deadline to either repair the test using deterministic virtual clocks, proper TestScope synchronization, and isolated state, or permanently remove it. Allowing tests to languish in quarantine indefinitely normalizes bad testing hygiene and undermines organizational discipline.""",
    "meta_ar": {
        "id": "CIC-13",
        "questionAr": "كيف تتعامل مع الاختبارات غير المستقرة (Flaky Tests)، وسياسات إعادة المحاولة (Retries)، والعزل (Quarantine)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم أسباب عدم استقرار الاختبارات (Flakiness)، ضبط سياسة إعادة المحاولة المقيدة (Bounded Retries)، معمارية عزل الاختبارات (Quarantine Policy)، وفرض اتفاقيات مستوى الخدمة (SLAs) لإصلاحها.",
        "concept_ar": "تعد الاختبارات غير المستقرة (Flaky Tests)—التي تنجح وتفشل عشوائياً على نفس الكود دون تعديل—من أكبر معوقات الإنتاجية لأنها تفقد الفريق الثقة في خط الـ CI. تعود أسباب عدم الاستقرار غالباً إلى التوقيت غير الحتمي في العمليات غير المتزامنة، أو استخدام Thread.sleep بدلاً من الساعات الافتراضية في Coroutines، أو تسرب البيانات في الكائنات الثابتة (Singletons). وتعتمد المعالجة على استراتيجية ثلاثية: أولاً، تفعيل إعادة المحاولة المقيدة عبر إضافة Gradle Test Retry بحيث يُسمح بمحاولة واحدة إضافية فقط لمنع تعطل البناء بسبب ومضة مؤقتة في السيرفر دون إخفاء العيوب. ثانياً، تطبيق سياسة العزل الفوري بوسم الاختبار بـ Quarantine واستبعاده من بوابات الـ PR الإلزامية حتى لا يعطل المطورين. ثالثاً، تشغيل الاختبارات المعزولة في مسار ليلي مراقب مع فرض اتفاقية خدمة تلزم الفريق بإصلاح الاختبار باستخدام أدوات حتمية مثل Turbine وTestScope خلال أسبوعين أو حذفه تماماً.",
        "walkthrough_ar": """تكوين إضافة إعادة المحاولة وعزل الاختبارات بوسم JUnit:
```kotlin
// app/build.gradle.kts
tasks.withType<Test>().configureEach {
    retry {
        val isCi = System.getenv("CI") == "true"
        maxRetries.set(if (isCi) 1 else 0) // محاولة واحدة فقط على السيرفر
        maxFailures.set(5) // إيقاف البناء إذا فشلت 5 اختبارات
    }

    useJUnitPlatform {
        if (project.hasProperty("excludeQuarantine")) {
            excludeTags("Quarantine")
        }
    }
}
```

```yaml
# .github/workflows/pr.yml
- name: Run Tests without Quarantined
  run: ./gradlew testDebugUnitTest -PexcludeQuarantine
```""",
        "why_it_matters_ar": "الاختبارات المتذبذبة تفقد المطورين الثقة في الـ CI وتدفعهم لإعادة تشغيل المهام عشوائياً، مما يهدر الوقت ويسمح بتسرب الأخطاء الحقيقية إلى الإنتاج.",
        "worked_example_ar": "عندما لاحظنا تذبذب اختبار شاشة الدفع بسبب تأخير في تدفق الـ Flow، قمنا بوسمه بـ Quarantine لاستبعاده من الـ PR، وأصلحناه باستخدام Turbine وrunTest ليعمل بحتمية تامة.",
        "trade_offs_ar": "إعادة المحاولة غير المحدودة تخفي المشاكل وتزيد تكلفة السيرفرات؛ بينما حصر المحاولات في واحدة مع العزل المؤقت يوازن بين سرعة الدمج وعدم التستر على الكود المعطوب.",
        "failure_modes_ar": "أخطر الأخطاء هو ترك الاختبارات في مسار العزل Quarantine لشهور طويلة دون محاسبة، أو الاعتماد على تكرار المحاولات 5 مرات لتمرير الـ PR مما يحول الـ CI إلى لعبة حظ.",
        "production_perspective_ar": "في الشركات الكبرى، يُسجل كل اختبار ينجح بعد إعادة المحاولة في لوحة بيانات مخصصة (Flake Dashboard)، ويُفتح له تذكرة عطل فورية للفريق المالك كخلل عالي الأولوية.",
        "how_to_answer_ar": "اشرح أسباب الـ Flakiness أولاً، ثم بين ضوابط استخدام إعادة المحاولة المحدودة، واشرح آلية العزل لاستمرار العمل، واختم باتفاقية الخدمة SLA الإلزامية لإصلاح الاختبار أو حذفه.",
        "talking_points_ar": "أسباب الـ Flakiness، التوقيت غير الحتمي، إضافة Gradle Test Retry، وسم Quarantine، استبعاد الفحص في الـ PR، وميثاق SLA لحل المشكلة خلال سبرنت واحد.",
        "follow_ups_ar": "كيف تستخدم أدوات مثل Turbine لمنع تذبذب اختبارات StateFlow؟ وما المعيار الحاسم لحذف اختبار معزول بدلاً من إصلاحه؟",
        "self_check_ar": "هل وضحت الفارق بين إعادة المحاولة المقيدة والعزل، وأكدت على عدم ترك الاختبارات في العزل إلى الأبد؟",
        "references_ar": f"- [Gradle Test Retry Plugin](https://github.com/gradle/test-retry-gradle-plugin) — الإضافة الرسمية لإدارة وإعادة تشغيل الاختبارات غير المستقرة على Gradle.\n- [Google Testing Blog: Flaky Tests at Google](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html) — مقال كلاسيكي يوضح سياسات جوجل في التعامل مع الاختبارات المتذبذبة.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """نتعامل مع الاختبارات غير المستقرة باستراتيجية ثلاثية توازن بين حماية الـ CI واستقرار الكود: نطبق إعادة محاولة مقيدة بحد أقصى مرة واحدة عبر إضافة Test Retry لمنع فشل البناء بسبب تقلبات عارضة، ثم نعزل الاختبار فور تكراره بوسم Quarantine لاستبعاده من بوابات الـ PR، ونلزم الفريق بميثاق زمني لإصلاحه خلال سبرنت واحد أو حذفه.""",
        "best_answer_ar": """إدارة الاختبارات المتذبذبة تتطلب موازنة دقيقة بين الحفاظ على سرعة حركة المطورين وضمان مصداقية منظومة الاختبارات.
تنشأ المشكلة عادة من السباق غير المتزامن في الكوروتينز أو تسرب البيانات في الكائنات المشتركة. ولحماية وقت الفريق على طلبات الدمج، نستخدم إضافة Gradle Test Retry مع وضع سقف صارم لا يتجاوز إعادة محاولة واحدة للاختبار الفاشل، مع إيقاف البناء فوراً إذا تعطلت خمسة اختبارات لمنع تضييع موارد السيرفر.
ومع ذلك، فإن إعادة المحاولة حل مؤقت لا يعالج أصل المشكلة؛ ولذلك فإن أي اختبار يتكرر تذبذبه يوضع عليه وسم العزل Quarantine فوراً، ويتم استبعاده من بوابات الـ PR الإلزامية حتى لا يعطل دمج الأكواد، مع توجيهه لمسار ليلي مستقل يجمع إحصائيات دقيقة عن معدل استقراره.
والأهم من ذلك هو فرض اتفاقية عمل صارمة مع الفريق الهندسي المسؤول؛ بحيث تمنح التذكرة أولوية قصوى لإصلاح الاختبار باستخدام أدوات حتمية مثل Turbine وتوحيد الساعات الافتراضية خلال سبرنت واحد، أو حذفه تماماً إذا لم يكن ذا جدوى معمارية حقيقية.""",
        "deep_answer_ar": """من منظور هندسة الجودة والعمليات البرمجية، تمثل الاختبارات غير المستقرة أكبر خطر يهدد ثقة المطورين في خطوط التسليم؛ فعندما يفشل الفحص عشوائياً، يعتاد الفريق على تجاهل الإشارات التحذيرية وتمرير التعديلات دون مراجعة.
ولذلك نصمم منظومة دفاع متكاملة تقوم على ثلاثة مبادئ أساسية: التخفيف المنضبط، العزل المؤقت، والمعالجة الجذرية الملزمة. في مرحلة البناء، نسمح بإعادة تشغيل الاختبار لمرة واحدة فقط كصمام أمان ضد عوارض السيرفرات السحابية المؤقتة، مع تسجيل كل حالة نجاح بعد إعادة المحاولة في لوحة متابعة خاصة لتوثيق حدوث التذبذب وعدم إخفائه.
وفي مرحلة العزل، نستخدم وسوماً مرنة في كود الاختبار تتيح لخط فحص الـ PR استبعاد هذه الفئة تماماً، مما يحرر قائمة الانتظار للمطورين دون المساس بجدية الفحص. وتُنقل هذه الاختبارات إلى بيئة مراقبة ليلية تُكرر فيها الحالات خمسين مرة متتالية تحت ضغط عالٍ لعزل شروط التسابق وكشف الخلل بدقة.
وأخيراً، نلزم الفرق بجدول زمني لا يتجاوز دورة عمل واحدة لحل مشكلة الاختبار المعزول؛ حيث يُعاد بناؤه باستخدام أدوات التحكم في الزمن الافتراضي وفصل البيانات المشتركة، أو يُحذف نهائياً إن تبين أنه يكرر تغطية موجودة في مكان آخر؛ لأن السماح ببقاء الاختبارات المعزولة بلا نهاية يكرس ثقافة التهاون ويدمر انضباط بيئة العمل البرمجية."""
    }
}

# ==========================================
# CIC-14: How do you use staged rollout, crash-rate gates, and rollback plans?
# ==========================================
DATA["CIC-14"] = {
    "concept_en": """Mitigating blast radius during Android production releases requires orchestrating staged rollout increments, real-time telemetry gating, and rapid mitigation strategies:
- Staged Rollout Mechanics:
  - Google Play Console allows releasing updates incrementally to a percentage of users: typically 1%, 5%, 10%, 20%, 50%, and finally 100%.
  - Google Play assigns user cohorts pseudorandomly; users who receive the update keep it, while users who have not updated continue receiving the prior stable build.
  - Manual or API-driven progression pauses at each tier for a soak period (e.g., 24 to 48 hours) to accumulate statistical telemetry.
- Telemetry & Crash-Rate Quality Gates:
  - Android Vitals: Google tracks device stability metrics across the fleet. Apps exceeding the bad behavior threshold (overall crash rate > 1.09% or ANR rate > 0.47%) suffer catastrophic store discovery penalties and search demotions.
  - Real-time Observability: Crashlytics and Datadog capture real-time crash-free user and session percentages. Teams enforce strict gates: if crash-free user rates drop below 99.9% or an unhandled exception spikes in a critical flow, the rollout is halted immediately.
- The Mobile Rollback Paradigm:
  - In Android OS architecture, traditional binary rollbacks are strictly impossible. The Android Package Manager prevents installing an APK or AAB with a lower `versionCode` over an existing installation to prevent Room database corruption.
  - True mitigation paths:
    - Immediate Halt: Halting the rollout in Play Console prevents any additional devices from receiving the defective build.
    - Fast Roll-Forward: An emergency hotfix branch is cut, the fix is applied, `versionCode` is incremented, and an expedited build is submitted to Google Play.
    - Server-Driven Feature Flags (Kill Switches): By wrapping new features in remote configuration flags (Firebase Remote Config, LaunchDarkly), engineering teams can instantly flip a feature off remotely within seconds, mitigating crashes without waiting for app store reviews.""",
    "walkthrough_en": """Feature flag kill-switch architecture and automated Play Store rollout halting script:
```kotlin
// Remote kill-switch protection in ViewModel
class CheckoutViewModel(
    private val remoteConfig: FirebaseRemoteConfig,
    private val analytics: AnalyticsTracker
) : ViewModel() {

    fun initiatePayment() {
        val isNewPaymentFlowEnabled = remoteConfig.getBoolean("is_new_payment_flow_enabled")
        if (isNewPaymentFlowEnabled) {
            executeModernPaymentFlow()
        } else {
            // Instant fallback if new flow causes unexpected production crashes
            executeLegacyPaymentFlow()
        }
    }
}
```

```python
# scripts/monitor_and_halt_rollout.py
import os
import requests

CRASH_RATE_THRESHOLD = 0.001 # 0.1% max acceptable crash rate
PACKAGE_NAME = "com.company.app"

def check_crashlytics_metrics():
    # Fetch real-time crash-free rate from telemetry API
    response = requests.get(
        "https://telemetry.internal.company/v1/metrics",
        headers={"Authorization": f"Bearer {os.environ['METRICS_TOKEN']}"}
    )
    data = response.json()
    crash_rate = data["current_release_crash_rate"]

    if crash_rate > CRASH_RATE_THRESHOLD:
        print(f"CRITICAL: Crash rate {crash_rate:.4f} exceeded threshold! Halting staged rollout...")
        halt_google_play_rollout()

def halt_google_play_rollout():
    # Call Google Play Developer API to halt the active rollout track
    pass
```""",
    "short_en": """Mitigate release risk through Google Play staged rollouts progressing from 1% to 100% with soak periods. Enforce strict telemetry gates monitoring Android Vitals and Crashlytics for 99.9% crash-free rates. Because Android strictly prevents binary downgrades, rollback plans combine immediate rollout halting, fast roll-forward hotfixes, and remote feature flag kill switches to disable defective code instantly.""",
    "structured_en": """Deploying mobile updates safely requires orchestrating staged rollout percentages alongside automated observability gates and operational mitigation procedures.
In Google Play Console, we deploy production releases incrementally, typically progressing from one percent to five, twenty, fifty, and finally one hundred percent. At each percentage tier, we enforce a mandatory soak period to accumulate real-world telemetry across diverse hardware and OS versions.
During this window, we monitor telemetry against strict quality gates. We track Android Vitals to ensure crash rates remain comfortably below Google's bad behavior thresholds, while simultaneously enforcing a ninety-nine point nine percent crash-free user standard in Firebase Crashlytics. If an anomaly or spike in ANRs occurs, the rollout is halted immediately via the Play Developer API.
Because the Android operating system strictly prevents package version downgrades to avoid local database corruption, true binary rollbacks are impossible. Therefore, our rollback strategy centers on server-driven feature flags. By wrapping new features in remote kill switches, we can disable failing code globally within seconds, avoiding the delays of emergency store hotfixes.""",
    "deep_senior_en": """From a platform operations and site reliability engineering perspective, releasing software to mobile devices represents an asynchronous, one-way door with irreversible hardware side effects.
When an update ships, we strictly govern blast radius using staged rollouts in Google Play. Progression follows a calculated schedule: launching at one percent to catch catastrophic startup crashes, expanding to five and twenty percent to evaluate diverse device manufacturers, and pausing for twenty-four-hour soak periods before full rollout.
During every stage, our monitoring infrastructure validates stability against hard automated gates. Android Vitals is watched continuously because crossing the one point zero nine percent crash threshold triggers automated algorithmic demotion across Google Play search rankings, permanently damaging organic user acquisition. In parallel, our real-time Crashlytics telemetry monitors crash-free rates against a strict ninety-nine point nine percent Service Level Objective. If any gate fails, an automated webhook immediately pauses the rollout.
However, halting a rollout merely prevents further infection; users who already installed the defective binary remain trapped on it. Because Android Package Manager explicitly rejects binary downgrades to safeguard Room database migrations, engineering teams cannot simply roll back an APK. Consequently, our primary operational mitigation is runtime decoupling using remote feature flags. Every significant user-facing change is shielded behind a server-managed kill switch. If a fatal crash slips past staging, we flip the feature flag in our configuration console, instantly neutralizing the defective code path globally without waiting for a recompiled hotfix to clear app store review.""",
    "meta_ar": {
        "id": "CIC-14",
        "questionAr": "كيف تدير الإطلاق التدريجي (Staged Rollout)، وبوابات معدل الانهيار، وخطط التراجع (Rollback)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "استراتيجية الطرح التدريجي عبر Google Play، معايير Android Vitals وCrashlytics لمنع الانهيارات، حقيقة استحالة التراجع الثنائي (No Binary Downgrades) في أندرويد، وتفعيل مفاتيح الميزات كـ Kill Switches فورية.",
        "concept_ar": "تعتمد حماية التطبيق أثناء الإطلاق على تقليص نطاق التأثير عبر الطرح التدريجي (Staged Rollout) والمراقبة الحية: يُطرح التحديث في Google Play بنسب متصاعدة تبدأ من 1% ثم 5% و10% و20% و50% وتصل إلى 100% مع فترات انتظار تمتد من 24 إلى 48 ساعة لتجميع البيانات. وخلال كل مرحلة، تخضع النسخة لبوابات جودة رقمية صارمة تراقب مؤشرات Android Vitals بحيث لا يتجاوز معدل الانهيار 1.09% ولا تتجاوز حالات عدم الاستجابة (ANR) نسبة 0.47% تجنباً لعقوبات المتجر الخوارزمية، بالتزامن مع اشتراط نسبة 99.9% من المستخدمين الخالين من الأعطال في Crashlytics. وإذا تخطت النسخة هذه الحدود، يُوقف الطرح فوراً. ولأن نظام أندرويد يمنع تثبيت نسخة برقم versionCode أقل حماية لقواعد البيانات المحلية، فإن التراجع الثنائي مستحيل تماماً؛ ولذلك تعتمد خطة التراجع على إيقاف الطرح أولاً، وتجهيز تحديث تصاعدي سريع (Roll-Forward Hotfix)، مع تفعيل مفاتيح الميزات السحابية (Kill Switches) لتعطيل الميزة المعطوبة برمجياً في ثوانٍ دون انتظار مراجعة المتجر.",
        "walkthrough_ar": """استخدام مفتاح ميزة سحابي كصمام أمان برمجي وسيناريو إيقاف الطرح:
```kotlin
// CheckoutViewModel.kt
class CheckoutViewModel(
    private val remoteConfig: FirebaseRemoteConfig
) : ViewModel() {

    fun startCheckout() {
        // مفتاح أمان لتعطيل الميزة الجديدة لحظياً في حال حدوث أعطال في الإنتاج
        val isNewCheckoutActive = remoteConfig.getBoolean("new_checkout_flow_v2")
        if (isNewCheckoutActive) {
            launchNewCheckout()
        } else {
            launchLegacyCheckout()
        }
    }
}
```

```yaml
# سيناريو مراقبة الـ Rollout
# 1. إطلاق بنسبة 1% ومراقبة Crashlytics لمدة 24 ساعة
# 2. إذا كان Crash-Free Users < 99.9%:
#    أ- إيقاف الطرح فوراً عبر Play Console API (Halt Rollout)
#    ب- إغلاق مفتاح الميزة new_checkout_flow_v2 من لوحة التحكم
#    ج- بناء كوميت تصحيحي Roll-Forward برقم versionCode أعلى
```""",
        "why_it_matters_ar": "إطلاق تطبيق معطوب لـ 100% من المستخدمين فجأة يدمر تقييم التطبيق ويخسره آلاف المستخدمين نهائياً نظراً لاستحالة التراجع الفوري عن النسخ المثبتة على الأجهزة.",
        "worked_example_ar": "عند إطلاق ميزة تحويل الأموال بنسبة 5%، سجلت لوحة Crashlytics انهياراً في أجهزة سامسونغ القديمة؛ فأوقفنا الطرح تلقائياً وعطلنا مفتاح الميزة من Firebase لإنقاذ المستخدمين خلال دقيقتين.",
        "trade_offs_ar": "الطرح البطيء جداً يؤخر وصول الميزات للمستخدمين ويطيل فترة اختبار الإصدار؛ بينما الطرح المتسرع يهدد سلامة التطبيق بالكامل. والتدرج بنسب 1% و5% و20% يمثل التوازن الأمثل للأمان والسرعة.",
        "failure_modes_ar": "أخطر الأخطاء هو الاعتقاد بإمكانية عمل Rollback لتثبيت النسخة السابقة في هواتف المستخدمين؛ مما يجعل الفريق عاجزاً عند حدوث كارثة إذا لم تكن هناك مفاتيح ميزات سحابية.",
        "production_perspective_ar": "في كبرى الشركات، تُربط تنبيهات Crashlytics تلقائياً بـ Webhooks توقف الطرح التدريجي في Google Play برمجياً دون انتظار تدخل بشري فور تجاوز معدل الخطأ للحد المسموح.",
        "how_to_answer_ar": "ابدأ بجدول نسب الطرح التدريجي، ثم اشرح بوابات Android Vitals ومعدل 99.9% في Crashlytics، وأكد بحزم على استحالة الـ Downgrade في أندرويد ودور Remote Config كطوق نجاة.",
        "talking_points_ar": "نسب Staged Rollout، مؤشرات Android Vitals، حدود الـ ANR والانهيار، حقيقة حظر الـ Downgrade في أندرويد، استراتيجية Roll-Forward، ومفاتيح الميزات السحابية كـ Kill Switches.",
        "follow_ups_ar": "كيف تتصرف مع المستخدمين الذين استلموا النسخة المعطوبة بالفعل بعد إيقاف الطرح؟ وكيف تصمم شاشات الإجبار على التحديث Force Update؟",
        "self_check_ar": "هل أكدت على استحالة التراجع الثنائي في أندرويد، وشرحت نسب الطرح وبوابات الجودة ومفاتيح التحكم السحابية؟",
        "references_ar": f"- [Google Play: Release app updates with staged rollouts](https://support.google.com/googleplay/android-developer/answer/6346149) — التوثيق الرسمي لسياسات ونسب الطرح التدريجي في متجر جوجل بلاي.\n- [Android Vitals: Core metrics and bad behavior thresholds](https://developer.android.com/distribute/play-console/vitals/core-metrics) — الحدود الرسمية لمعدلات الانهيار وتجمد التطبيق في جوجل بلاي.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": """ندير الإطلاق بنسب طرح تدريجي في Google Play تبدأ من 1% حتى 100% مع فترات مراقبة حية. ونضع بوابات جودة صارمة تراقب Android Vitals وCrashlytics لضمان خلو 99.9% من المستخدمين من الأعطال. ولأن نظام أندرويد يمنع التراجع للنسخ السابقة نهائياً، تعتمد خطة التراجع على إيقاف الطرح فوراً واستخدام مفاتيح الميزات السحابية لتعطيل الميزة المعطوبة لحظياً.""",
        "best_answer_ar": """إطلاق التحديثات بأمان يتطلب تنسيقاً دقيقاً بين نسب الطرح التدريجي وبوابات المراقبة اللحظية وخطط الاستجابة السريعة.
نبدأ بطرح التحديث تدريجياً عبر لوحة Google Play بنسب تبدأ من واحد بالمئة ثم خمسة وعشرين وخمسين وصولاً إلى الإطلاق الكامل، مع ترك فترة مراقبة لا تقل عن يوم كامل بين المراحل لتجميع البيانات عبر مختلف الأجهزة والشرائح.
وخلال هذه الفترة، نراقب بوابات الجودة بصرامة تامة؛ حيث نتتبع مؤشرات Android Vitals لضمان بقاء الانهيارات وتجمد التطبيق دون الحدود التي تفرض عندها جوجل عقوبات في خوارزميات البحث، مع اشتراط استقرار بنسبة تسعة وتسعين فاصل تسعة بالمئة من المستخدمين في Crashlytics، وإيقاف الطرح فوراً إذا حدث أي خلل غير متوقع.
ولأن نظام أندرويد يمنع برمجياً تثبيت نسخة سابقة برقم إصدار أقل حماية لقواعد البيانات المحلية، فإن التراجع الثنائي مستحيل تماماً على أجهزة المستخدمين؛ ولذلك نعتمد في خطة التراجع على مفاتيح الميزات المدارة سحابياً، والتي تمكننا من إغلاق الميزة المعطوبة عن بعد في ثوانٍ معدودة دون الحاجة لانتظار بناء ومراجعة تحديث طارئ.""",
        "deep_answer_ar": """من منظور استقرار المنصات وهندسة موثوقية النظم، يعد إطلاق البرمجيات لأجهزة الهواتف الذكية مساراً ذا اتجاه واحد لا يحتمل المجازفة، نظراً لتأثيره المباشر على أجهزة المستخدمين.
وللحد من نطاق أي خلل برمجى محتمل، نلزم كافة الإصدارات بالطرح التدريجي؛ فنبدأ بنسبة واحد بالمئة لرصد أي انهيار فوري عند الإقلاع، ثم نرفع النسبة تدريجياً لاختبار سلوك التطبيق على عتاد مختلف الشركات المصنعة، مع الالتزام بفترات تهدئة كافية لملاحظة ردود الفعل واستقرار النظام.
وأثناء كل مرحلة، تعمل بوابات الجودة المؤتمتة بالتكامل مع منصات المراقبة؛ حيث نراقب مؤشرات Android Vitals بدقة لأن تجاوز حد الانهيار الرسمي البالغ واحد فاصل تسعة من مئة بالمئة يتسبب في خفض ترتيب التطبيق في متجر جوجل وحرمانه من الظهور في نتائج البحث. كما ترتبط منصة Crashlytics بأنظمة إنذار مبكر توقف الطرح برمجياً بمجرد انخفاض نسبة المستخدمين الخالين من الأعطال.
وعند وقوع أي خلل، يواجه مهندس أندرويد حقيقة أن نظام التشغيل يرفض التراجع إلى رقم إصدار أقل لحماية تكامل بيانات الغرفة وقواعد البيانات؛ مما يعني أن إيقاف الطرح يمنع انتشار المشكلة فقط لكنه لا يعالج الأجهزة المتضررة. وهنا يبرز دور الفصل المعماري بين نشر الكود وتفعيل الميزات؛ حيث نغلف كل مسار برمجي جديد بمفتاح تحكم سحابي عن بعد، يتيح لمهندسي النظام إطفاء الميزة المتسببة في العطل فورياً لكافة المستخدمين دون الحاجة لانتظار ساعات طويلة لبناء واعتماد تحديث جديد من المتجر."""
    }
}

# ==========================================
# Validation & Runner logic
# ==========================================
def validate_words():
    print("Checking word counts and spoken style for CIC-08 to CIC-14...")
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

    ee.save_topic_metadata("cic_08_14", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\nAll {len(DATA)} CIC questions (CIC-08 to CIC-14) successfully elevated and passed validation!\n")

if __name__ == "__main__":
    apply_elevations()
