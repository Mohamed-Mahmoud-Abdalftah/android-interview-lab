#!/usr/bin/env python3
"""Generator for CIC-08 through CIC-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cic.json"

CIC_08_14 = [
    {
        "id": "CIC-08",
        "arabic_explanation": (
            "كيف تقوم بإعداد وتأمين بوابات فحص الـ PRs (Pull Request Checks) للـ Lint والتحليل الساكن واختبارات الوحدة؟\n\n"
            "1. استراتيجية بوابة الجودة للـ PR (PR Quality Gate):\n"
            "   - الهدف الأساسي هو مبدأ **Fail-Fast**: إيقاف الكود المعيب في أسرع وقت ممكن (خلال دقيقة إلى 3 دقائق) قبل إهدار موارد السيرفر في بناء كامل أو اختبارات بطيئة.\n\n"
            "2. المكونات الأساسية للبوابة:\n"
            "   - **1. تنسيق الكود (Code Formatting)**: استخدام Spotless أو ktlint للتحقق من التزام الكود بمعايير Kotlin الرسمية (المسافات، الترتيب، الـ imports غير المستخدمة).\n"
            "   - **2. التحليل الساكن (Static Analysis)**: تشغيل Detekt لكشف مشاكل تعقيد الكود (Cyclomatic Complexity)، والـ Code Smells، والـ Magic Numbers.\n"
            "   - **3. أندرويد لنت (Android Lint)**: تشغيل `./gradlew lintDebug` للتحقق من مشاكل الـ Android SDK وموارد التطبيق والذاكرة واستخدام الـ APIs غير المتوافقة.\n"
            "   - **4. اختبارات الوحدة السريعة**: تشغيل `./gradlew testDebugUnitTest` للتأكد من خلو منطق العمل من أي انحدار (Regressions).\n\n"
            "3. إدارة الديون التقنية عبر الـ Baselines:\n"
            "   - في المشاريع الكبيرة ذات الكود القديم، تشغيل Lint قد يُظهر 500 خطأ قديم! الحل ليس تجاهل Lint، بل توليد **Lint Baseline (`lint-baseline.xml`)** و **Detekt Baseline**؛ بحيث تتجاهل البوابة الأخطاء القديمة مؤقتاً، ولكن **ترفض الـ PR فوراً إذا أضاف المطور خطأً جديداً واحداً**."
        ),
        "practical_walkthrough": (
            "إعداد Gradle وملف عمل GitHub Actions لتشغيل الفحوصات وإظهار التقارير مباشرة في الـ PR:\n"
            "```yaml\n"
            "# .github/workflows/pr_checks.yml\n"
            "name: PR Static & Unit Checks\n"
            "on:\n"
            "  pull_request:\n"
            "    branches: [ main, develop ]\n"
            "\n"
            "jobs:\n"
            "  quality_gate:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "\n"
            "      # تشغيل الفحوصات مع استمرار التنفيذ لتجميع كل الأخطاء وتقديم تقرير موحد (--continue)\n"
            "      - name: Run Linters and Tests\n"
            "        run: ./gradlew spotlessCheck detekt lintDebug testDebugUnitTest --continue\n"
            "\n"
            "      # رفع تقارير الفحص كـ Artifacts في حال فشل أي فحص لتسهيل الفحص\n"
            "      - name: Upload Test and Lint Reports\n"
            "        if: failure()\n"
            "        uses: actions/upload-artifact@v4\n"
            "        with:\n"
            "          name: pr-check-reports\n"
            "          path: |\n"
            "            **/build/reports/lint-results-debug.html\n"
            "            **/build/reports/tests/testDebugUnitTest/\n"
            "```"
        ),
        "quick_answer": "Configure PR checks by chaining Spotless/ktlint for formatting, Detekt for static analysis, Android Lint with baseline files for framework checks, and testDebugUnitTest for local JVM unit tests. Run with the --continue flag in parallel jobs to fail fast while aggregating all errors into PR comments or build summaries.",
        "best_answer": (
            "A production PR quality gate is designed to enforce strict code standards without crippling developer velocity:\n\n"
            "1. **Fail-Fast Pipeline Structure**:\n"
            "   - Separate lightweight checks into parallel jobs: (a) formatting and static analysis (Spotless/ktlint, Detekt), and (b) local JVM unit tests (`testDebugUnitTest`). This provides feedback within 2–3 minutes.\n\n"
            "2. **Baseline Management for Legacy Projects**:\n"
            "   - Enforce zero-tolerance for new issues in legacy codebases by generating Lint and Detekt baselines (`lintOptions { baseline = file(\"lint-baseline.xml\") }`). Existing issues are recorded and grandfathered in, while newly introduced violations fail the PR build immediately.\n\n"
            "3. **Inline PR Feedback & Actionable Reporting**:\n"
            "   - Integrate tools like Danger or reviewdog to parse Lint XML reports and publish inline GitHub PR comments directly on offending lines, eliminating the need for engineers to download raw CI log files.\n\n"
            "4. **Execution Resilience**:\n"
            "   - Use the `--continue` Gradle flag so the runner executes all static checks in a single pass, reporting formatting, lint, and unit test failures simultaneously rather than forcing repeated CI runs for sequential errors."
        ),
        "deep_answer": (
            "From an engineering governance and CI infrastructure standpoint, PR checks require careful caching and branch protection rules:\n\n"
            "1. **Branch Protection Enforcement**: In GitHub or GitLab settings, mandate 'Require status checks to pass before merging' and 'Require branches to be up to date before merging'. This prevents race conditions where two PRs pass CI independently but break when merged together.\n\n"
            "2. **Targeted Subproject Execution**: In a multi-module architecture of 80+ modules, running `./gradlew check` across the entire project on every 3-line PR wastes massive compute. Teams configure path filters or tools like Gradle's configuration-cache and affected-module-detector to run tests only on modules impacted by the PR's git diff.\n\n"
            "3. **Remote Build Cache**: Enable Gradle's remote build cache (`org.gradle.caching=true`) backed by an S3/GCS or Develocity instance. If an engineer refactors a leaf module, upstream modules are retrieved from cache with `FROM-CACHE` status in seconds."
        ),
        "follow_ups": [
            {
                "question": "What is the purpose of the `--continue` flag in Gradle CI commands?",
                "answer": "It instructs Gradle to execute every scheduled task even if an earlier task fails, aggregating all errors in a single CI run."
            },
            {
                "question": "How do baseline files help manage tech debt in Android Lint?",
                "answer": "They record existing violations so CI only fails if a developer introduces new violations or modifies lines containing old ones."
            }
        ]
    },
    {
        "id": "CIC-09",
        "arabic_explanation": (
            "كيف تقوم بحماية مفاتيح التوقيع (Signing Keystore) وأسرار الـ CI/CD من التسريب أو الاختراق؟\n\n"
            "1. المخاطر الأمنية الرئيسية:\n"
            "   - **تسريب الـ Keystore**: إذا تسرب مفتاح توقيع التطبيق وكلمة السر، يمكن لأي مخترق نشر تحديثات خبيثة للمستخدمين.\n   - **اختراق عبر Pull Requests**: تشغيل سيرفرات الـ CI تلقائياً على فروع الـ Forks المفتوحة قد يسمح لمهاجم بطباعة الـ Secrets في الـ Logs (`echo $KEYSTORE`).\n   - **كشف الأسرار في الـ Version Control**: رفع ملفات `.jks` أو كلمات المرور صراحة في `build.gradle.kts`.\n\n"
            "2. أفضل الممارسات الهندسية لحماية الأسرار:\n"
            "   - **Google Play App Signing**: الاعتماد على جوجل لحفظ مفتاح التوقيع الرئيسي (App Signing Key). السيرفر يحتاج فقط لمفتاح الرفع (Upload Key)؛ وإذا ضاع أو تسرب مفتاح الرفع، يمكن إعادة ضبطه بسهولة عبر Google Support دون فقدان التطبيق.\n   - **تخزين الـ Keystore كـ Secret سحابي**: تحويل ملف الـ JKS إلى نص مشفر (Base64) وتخزينه داخل GitHub Secrets أو HashiCorp Vault أو GCP Secret Manager.\n   - **استدعاء الأسرار بشكل عابر (Ephemeral Extraction)**: فك تشفير الـ Keystore في ملف مؤقت داخل مجلد الـ Runner أثناء البناء فقط، ثم حذفه فور انتهاء المهمة.\n   - **عزل أسرار الـ PRs**: منع فروع الـ PRs القادمة من الـ Forks من الوصول لأسرار التوقيع والـ Play Store نهائياً."
        ),
        "practical_walkthrough": (
            "إعداد توقيع الـ Release في Gradle بشكل آمن باستخدام متغيرات البيئة المشفرة:\n"
            "```kotlin\n"
            "// app/build.gradle.kts\n"
            "android {\n"
            "    signingConfigs {\n"
            "        create(\"release\") {\n"
            "            // قراءة المسار والأسرار من متغيرات البيئة فقط، وتجنب وضعها في الكود نهائياً:\n"
            "            storeFile = System.getenv(\"KEYSTORE_FILE_PATH\")?.let { file(it) }\n"
            "            storePassword = System.getenv(\"KEYSTORE_STORE_PASSWORD\")\n"
            "            keyAlias = System.getenv(\"KEYSTORE_KEY_ALIAS\")\n"
            "            keyPassword = System.getenv(\"KEYSTORE_KEY_PASSWORD\")\n"
            "        }\n"
            "    }\n"
            "    buildTypes {\n"
            "        release {\n"
            "            signingConfig = signingConfigs.getByName(\"release\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```\n"
            "وفي ملف GitHub Actions:\n"
            "```yaml\n"
            "- name: Decode and Setup Keystore\n"
            "  env:\n"
            "    KEYSTORE_BASE64: ${{ secrets.ANDROID_UPLOAD_KEYSTORE_BASE64 }}\n"
            "  run: |\n"
            "    echo \"$KEYSTORE_BASE64\" | base64 --decode > /tmp/release_upload.jks\n"
            "- name: Build Release Bundle\n"
            "  env:\n"
            "    KEYSTORE_FILE_PATH: /tmp/release_upload.jks\n"
            "    KEYSTORE_STORE_PASSWORD: ${{ secrets.KEYSTORE_STORE_PASSWORD }}\n"
            "    KEYSTORE_KEY_ALIAS: ${{ secrets.KEYSTORE_KEY_ALIAS }}\n"
            "    KEYSTORE_KEY_PASSWORD: ${{ secrets.KEYSTORE_KEY_PASSWORD }}\n"
            "  run: ./gradlew bundleRelease\n"
            "- name: Clean Up Keystore\n"
            "  if: always()\n"
            "  run: rm -f /tmp/release_upload.jks\n"
            "```"
        ),
        "quick_answer": "Protect signing material by using Google Play App Signing (so CI only holds an Upload Key), storing the keystore as a base64-encoded secret in CI secret vaults, injecting credentials dynamically via environment variables, decoding the file ephemerally into a temporary path deleted on cleanup, and strictly isolating release secrets from untrusted PR builds.",
        "best_answer": (
            "A hardened mobile secret management architecture relies on four defensive layers:\n\n"
            "1. **Google Play App Signing Architecture**:\n"
            "   - Delegate root app signing authority to Google Cloud Key Management. The CI pipeline only holds an **Upload Key**. If an upload key is compromised, administrators can revoke and rotate it via Play Console without stranding existing installed users.\n\n"
            "2. **Encrypted Secret Storage & Ephemeral Lifecycle**:\n"
            "   - The upload keystore binary is encoded as base64 and stored in enterprise secret vaults (GitHub Secrets, AWS Secrets Manager, or HashiCorp Vault). The CI runner decodes the file into an ephemeral temporary path (`/tmp/upload.jks`) immediately before compilation and securely wipes it in a `finally` or `if: always()` post-build step.\n\n"
            "3. **Zero Secrets in Source Control**:\n"
            "   - Keystore passwords, aliases, and Play Console JSON API keys are strictly injected via environment variables at runtime, never committed to `build.gradle.kts` or `keystore.properties`.\n\n"
            "4. **PR Execution Security Boundary**:\n"
            "   - Pull requests originating from public forks or unverified contributors are executed in unprivileged sandbox runners where production release secrets are strictly masked and unavailable."
        ),
        "deep_answer": (
            "From a DevSecOps and supply-chain defense perspective, advanced secret protection involves preventing indirect exfiltration:\n\n"
            "1. **Malicious Dependency and PR Injection**: Attackers can submit PRs modifying third-party dependencies or Gradle build scripts to print `System.getenv()` into build logs or send secrets via curl. GitHub Actions enforces that `pull_request` triggers do not have access to repository secrets by default. Never use `pull_request_target` with an automatic checkout of PR head code, as this exposes secrets to attacker-controlled scripts.\n\n"
            "2. **Log Masking and Redaction**: Ensure CI secret values are registered with secret masking utilities (e.g., `::add-mask::` in GitHub Actions). Gradle log levels must never be set to `--debug` or `--info` on production signing tasks, as Gradle may log command-line arguments and environment parameters.\n\n"
            "3. **OIDC (OpenID Connect) for Cloud Access**: Replace long-lived API service account JSON keys for Google Cloud and Google Play with short-lived OIDC federated tokens. The GitHub Actions runner authenticates directly with GCP Workload Identity Federation using temporary cryptographic credentials, eliminating static stored credentials."
        ),
        "follow_ups": [
            {
                "question": "What is the critical security benefit of Google Play App Signing over managing the app signing key manually?",
                "answer": "If your upload key is compromised or lost, Google Play can rotate it upon request without abandoning the app or stranding existing users."
            },
            {
                "question": "Why is using `pull_request_target` dangerous when handling secrets in GitHub Actions?",
                "answer": "Because it runs in the context of the base branch with secret access, allowing untrusted PR code to exfiltrate secrets if checked out directly."
            }
        ]
    },
    {
        "id": "CIC-10",
        "arabic_explanation": (
            "كيف تقوم بأتمتة نشر وتوزيع نسخ التطبيق على مسار الاختبارات الداخلية (Internal Testing) ومتجر Google Play؟\n\n"
            "1. مسار الأتمتة الحديث:\n"
            "   - النشر اليدوي عبر سحب وإفلات الـ AAB في المتصفح بطيء وعرضة للأخطاء البشرية (مثل نسيان رفع ملف الـ mapping.txt أو اختيار حزمة خاطئة).\n   - الحل الهندسي: استخدام **Google Play Developer API** عبر أدوات أتمتة مثل: Fastlane (`supply`), أو إضافة Gradle Play Publisher (GPP), أو GitHub Actions الرسمية.\n\n"
            "2. خطوات الإعداد المتكاملة:\n"
            "   - **1. حساب الخدمة (Service Account)**: إنشاء Service Account في Google Cloud Console ومنحه الصلاحيات المطلوبة في Google Play Console (صلاحيات الإصدار وإدارة مسارات الاختبار).\n   - **2. مفتاح الـ API**: تحميل مفتاح JSON الخاص بالـ Service Account وتخزينه كـ Secret مشفر في الـ CI.\n   - **3. بناء حزمة الإنتاج (AAB)**: تشغيل `./gradlew bundleRelease` لتوليد الـ Android App Bundle.\n   - **4. رفع الـ AAB وملفات الـ De-obfuscation**: إرسال الـ AAB مصحوباً بملف `mapping.txt` و `native-debug-symbols.zip` إن وجدت.\n   - **5. كتابة الـ Release Notes**: تضمين ملفات الـ Changelog لكل لغة مدعومة تلقائياً (مثلاً `whatsnew-en-US`).\n   - **6. تعيين المسار (Track)**: النشر التلقائي المباشر لمسار الـ `internal` للاختبار السريع من قبل الفريق."
        ),
        "practical_walkthrough": (
            "طريقتان شائعتان لنشر الـ AAB تلقائياً لمسار Internal Testing:\n"
            "```yaml\n"
            "# الطريقة 1: استخدام GitHub Action موثوقة ومباشرة\n"
            "- name: Deploy to Google Play Internal\n"
            "  uses: r0adkll/upload-google-play@v1\n"
            "  with:\n"
            "    serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_SERVICE_ACCOUNT_JSON }}\n"
            "    packageName: com.example.proapp\n"
            "    releaseFiles: app/build/outputs/bundle/release/app-release.aab\n"
            "    track: internal\n"
            "    status: completed\n"
            "    mappingFile: app/build/outputs/mapping/release/mapping.txt\n"
            "    whatsNewDirectory: distribution/whatsnew\n"
            "```\n"
            "```ruby\n"
            "# الطريقة 2: استخدام Fastlane (Lane مخصصة في Fastfile)\n"
            "lane :deploy_internal do\n"
            "  gradle(task: 'bundleRelease')\n"
            "  upload_to_play_store(\n"
            "    track: 'internal',\n"
            "    package_name: 'com.example.proapp',\n"
            "    json_key_data: ENV['PLAY_STORE_JSON_KEY'],\n"
            "    aab: 'app/build/outputs/bundle/release/app-release.aab',\n"
            "    mapping_paths: ['app/build/outputs/mapping/release/mapping.txt'],\n"
            "    skip_upload_images: true,\n"
            "    skip_upload_screenshots: true\n"
            "  )\n"
            "end\n"
            "```"
        ),
        "quick_answer": "Automate publishing by generating a signed AAB, configuring a Google Cloud Service Account with Google Play Console release permissions, and using Fastlane (supply), Gradle Play Publisher, or a GitHub Action to upload the AAB along with R8 mapping.txt and release notes to the Internal Testing track via the Play Developer API.",
        "best_answer": (
            "Publishing Android builds to internal testing and Google Play tracks is automated through a systematic workflow:\n\n"
            "1. **Identity & Access Management (IAM)**:\n"
            "   - Create a dedicated Google Cloud Service Account linked to Google Play Console with least-privilege permissions (e.g. 'Manage testing tracks and releases'). Store its JSON private key in CI secrets.\n\n"
            "2. **Release Compilation & Metadata Packaging**:\n"
            "   - The CI pipeline executes `./gradlew bundleRelease` producing the `.aab`, while R8 produces the corresponding `mapping.txt` and native debug symbols (`native-debug-symbols.zip`).\n\n"
            "3. **Automated Upload via Play Developer API**:\n"
            "   - Using tooling like Fastlane (`upload_to_play_store`), Gradle Play Publisher (GPP), or GitHub Actions (`r0adkll/upload-google-play`), the pipeline initiates an edit session on the Google Play Developer API, uploads the AAB and de-obfuscation files, attaches localized changelogs (`whatsnew/whatsnew-en-US`), and commits the edit to the `internal` testing track.\n\n"
            "4. **Instant Verification Ring**:\n"
            "   - Builds deployed to the Internal Testing track bypass lengthy Google Play manual reviews, becoming accessible to internal QA and developers via Play Store links within minutes."
        ),
        "deep_answer": (
            "In enterprise release management, managing API limits and track progression requires strategic design:\n\n"
            "1. **Track Promotion Without Rebuilding**: An essential practice is promoting existing builds rather than rebuilding. Once an internal track AAB is validated, use the Play Developer API to promote that exact release artifact from `internal` to `closed` (alpha/beta) and eventually to `production`, maintaining 100% binary parity.\n\n"
            "2. **Google Play API Quotas & Race Conditions**: Google Play API allows only one active edit session per package at any given time. Concurrent CI pipelines trying to upload distinct flavors simultaneously will fail with HTTP 409 Conflict. CI runners must serialize Play Store publishing jobs or use mutex locks.\n\n"
            "3. **Automated Notification Integration**: After successful upload, the pipeline queries the Play API for the newly minted release status and posts an actionable Slack/Teams alert containing the direct Play Store testing link, the git commit SHA, and author details."
        ),
        "follow_ups": [
            {
                "question": "Why is the Google Play Internal Testing track preferred for automated CI over Closed Alpha?",
                "answer": "Internal testing updates are available almost instantaneously (under 5–10 minutes) without undergoing standard Google Play store review latency."
            },
            {
                "question": "What error occurs if two CI jobs attempt to upload releases to the Play Store API simultaneously?",
                "answer": "An HTTP 409 conflict, because the Play Developer API enforces a single active edit session per application at a time."
            }
        ]
    },
    {
        "id": "CIC-11",
        "arabic_explanation": (
            "كيف تقوم بأتمتة ترقيم الإصدارات (Versioning)، وسجل التغييرات (Changelog)، والـ Git Tags في أندرويد؟\n\n"
            "1. هيكل ترقيم أندرويد الإلزامي:\n"
            "   - **`versionName` (String)**: الرقم الظاهر للمستخدم (مثل `\"2.4.1\"`). يتبع عادة نظام **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`.\n   - **`versionCode` (Integer)**: رقم صحيح تزايدي إلزامي لمتجر Google Play (يجب أن يكون كل تحديث يحمل رقماً أعلى من سابقه، وبحد أقصى $2.1 \\times 10^9$).\n\n"
            "2. استراتيجيات الأتمتة الهندسية:\n"
            "   - **حساب `versionCode` آلياً**: تجنب تعديله يدوياً في الملفات! يمكن حسابه في Gradle عبر عدد الـ Commits في الفرع الرئيسي: `git rev-list --count HEAD`، أو عبر الـ CI Build Number (`GITHUB_RUN_NUMBER`).\n   - **Conventional Commits**: إجبار الفريق على كتابة رسائل الـ Commits بصيغة قياسية: `feat:`, `fix:`, `chore:`, `perf:`, `BREAKING CHANGE:`.\n   - **أتمتة الـ Changelog والـ Tags**: استخدام أدوات مثل `semantic-release` أو `git-cliff` لتحليل الـ commits تلقائياً عند الدمج في `main`، وتحديد ما إذا كان الإصدار القادم Major أم Minor أم Patch، ثم إنشاء Git Tag وإضافة ملف الـ Release Notes وتحديث ملف `CHANGELOG.md`."
        ),
        "practical_walkthrough": (
            "حساب `versionCode` و `versionName` آلياً داخل `build.gradle.kts` باستخدام Git:\n"
            "```kotlin\n"
            "// app/build.gradle.kts\n"
            "import java.io.ByteArrayOutputStream\n"
            "\n"
            "fun getGitCommitCount(): Int {\n"
            "    val stdout = ByteArrayOutputStream()\n"
            "    exec {\n"
            "        commandLine(\"git\", \"rev-list\", \"--count\", \"HEAD\")\n"
            "        standardOutput = stdout\n"
            "    }\n"
            "    return stdout.toString().trim().toIntOrNull() ?: 1\n"
            "}\n"
            "\n"
            "fun getGitLatestTag(): String {\n"
            "    val stdout = ByteArrayOutputStream()\n"
            "    exec {\n"
            "        commandLine(\"git\", \"describe\", \"--tags\", \"--abbrev=0\")\n"
            "        standardOutput = stdout\n"
            "    }\n"
            "    return stdout.toString().trim().ifEmpty { \"1.0.0\" }\n"
            "}\n"
            "\n"
            "android {\n"
            "    defaultConfig {\n"
            "        // يتم حساب versionCode تلقائياً من عدد الكوميتات لضمان التزايد الدائم:\n"
            "        versionCode = getGitCommitCount()\n"
            "        // يتم استخراج versionName من أحدث Git Tag:\n"
            "        versionName = getGitLatestTag()\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Automate versioning using Conventional Commits and Semantic Versioning. Calculate versionCode dynamically from git commit count or CI build numbers to guarantee monotonic increments, derive versionName from git tags, and automate changelog generation and tagging using tools like semantic-release or git-cliff on release branches.",
        "best_answer": (
            "Automating Android release versioning removes manual human error and ensures store compliance:\n\n"
            "1. **Android Dual Versioning Paradigm**:\n"
            "   - **`versionCode` (Integer)**: A strictly increasing positive integer required by Google Play to identify upgrade paths. Generating it from `git rev-list --count HEAD` or CI pipeline run numbers ensures monotonicity without manual editing.\n"
            "   - **`versionName` (String)**: The consumer-facing release string (e.g. `\"3.2.0\"`) adhering to Semantic Versioning (`MAJOR.MINOR.PATCH`).\n\n"
            "2. **Conventional Commits & Automated Bumping**:\n"
            "   - Enforce commit conventions (`feat:`, `fix:`, `refactor:`, `perf:`, `BREAKING CHANGE`). CI tooling parses commit history since the last git tag to determine the next SemVer version increment automatically.\n\n"
            "3. **Changelog & Tag Generation**:\n"
            "   - Utilities like `git-cliff` or GitHub Actions release workflows automatically compile grouped changelogs, create an annotated Git tag (`v3.2.0`), generate release notes for Google Play's `whatsnew-en-US.txt`, and publish a GitHub Release."
        ),
        "deep_answer": (
            "At enterprise scale with multiple CPU architectures or flavors, versioning requires mathematical planning:\n\n"
            "1. **ABI/Flavor Version Code Offsets**: If distributing APKs rather than AABs, Google Play requires distinct versionCodes for different ABIs (e.g. arm64-v8a must have a higher versionCode than armeabi-v7a so devices pick the 64-bit package). A classic formula is `versionCode = (baseVersionCode * 10) + abiCode`.\n\n"
            "2. **CI Tagging Race Conditions**: Never push a Git tag *before* the release build succeeds. If the build or release fails half-way through, the tag points to a failed state. The pipeline must build and deploy the artifact first; only upon confirmed distribution does it commit the release tag and changelog to the repository.\n\n"
            "3. **Single Source of Truth**: Avoid storing version numbers in multiple places (e.g. `gradle.properties`, `AndroidManifest.xml`, and Git tags). Make the Git repository tag the single source of truth from which build scripts dynamically extract the version string."
        ),
        "follow_ups": [
            {
                "question": "What is the consequence if a new release has a lower or equal versionCode than the currently active release on Google Play?",
                "answer": "Google Play will reject the upload with an error stating that the versionCode must be strictly greater than active releases."
            },
            {
                "question": "Why is using `git rev-list --count HEAD` for versionCode reliable on the main branch?",
                "answer": "Because commits on a shared mainline only increase, guaranteeing a strictly increasing integer sequence across builds."
            }
        ]
    },
    {
        "id": "CIC-12",
        "arabic_explanation": (
            "كيف تقوم بتقليل وقت التجميع الأولي البارد (Cold-Build) وتسريع تنفيذ خط أنابيب الـ CI في أندرويد؟\n\n"
            "1. أسباب بطء بناء الـ CI (Bottlenecks):\n"
            "   - سيرفرات الـ CI (مثل GitHub Actions runners) غالباً ما تكون بيئات عابرة (Ephemeral VMs) تبدأ من الصفر بدون أي كاش للمكتبات أو الـ Gradle Daemon.\n   - إعادة تجميع كل الـ Modules والمكتبات مع كل PR تستهلك من 15 إلى 40 دقيقة.\n\n"
            "2. استراتيجيات التسريع الجوهرية (Optimization Tactics):\n"
            "   - **1. Remote Build Cache (كاش التجميع البعيد)**: أهم خطوة على الإطلاق! إعداد كاش سحابي (عبر Gradle Enterprise / Develocity أو سيرفر HTTP/S3) يسمح لسيرفرات الـ CI بمشاركة مخرجات المهام (Task Outputs). أي مهمة تم بناؤها مسبقاً بنفس المدخلات يتم تنزيل نتيجتها في أجزاء من الثانية (`FROM-CACHE`).\n   - **2. استعادة كاش الـ Gradle والـ Dependencies**: استخدام `gradle/actions/setup-gradle` الذي يقوم بحفظ واستعادة مجلدات `~/.gradle/caches` ومجلد الـ wrapper تلقائياً.\n   - **3. تفعيل خصائص Gradle المتقدمة**: تفعيل `org.gradle.parallel=true` لتجميع الوحدات المستقلة بالتوازي، وتفعيل `org.gradle.configuration-cache=true` لتخطي مرحلة التكوين (Configuration Phase).\n   - **4. فحص الـ Modules المتأثرة فقط (Affected Module Detection)**: تشغيل الاختبارات والفحوصات فقط على الموديولات التي تغيرت في الـ Git Diff وما يعتمد عليها، بدلاً من فحص 100 موديول بالكامل.\n   - **5. ضبط ذاكرة الـ JVM بدقة**: تخصيص ذاكرة كافية لـ Gradle في الـ CI (`-Xmx4g -XX:+UseParallelGC`) لتفادي توقف الـ Garbage Collector المتكرر."
        ),
        "practical_walkthrough": (
            "إعداد ملف `gradle.properties` وتخصيص الـ CI لسرعة قياسية:\n"
            "```properties\n"
            "# gradle.properties مخصص لبيئة الـ CI:\n"
            "org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC -XX:MaxMetaspaceSize=1024m\n"
            "org.gradle.parallel=true\n"
            "org.gradle.caching=true\n"
            "org.gradle.configuration-cache=true\n"
            "kapt.incremental.apt=true\n"
            "kotlin.incremental=false # Incremental compilation غير مجدية في الـ cold builds النظيفة بدون كاش محلي\n"
            "```\n"
            "وفي ملف `settings.gradle.kts` لتفعيل الـ Remote Build Cache:\n"
            "```kotlin\n"
            "buildCache {\n"
            "    local {\n"
            "        isEnabled = true\n"
            "    }\n"
            "    remote<HttpBuildCache> {\n"
            "        url = uri(\"https://gradle-cache.company.internal/cache/\")\n"
            "        credentials {\n"
            "            username = System.getenv(\"CACHE_USER\")\n"
            "            password = System.getenv(\"CACHE_PASSWORD\")\n"
            "        }\n"
            "        isPush = System.getenv(\"IS_CI_MAIN_BRANCH\") == \"true\" // سيرفر الـ main فقط يرفع للكاش\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Slash Android CI build times by configuring Gradle Remote Build Cache (Develocity/HTTP cache) for task reuse, enabling Gradle configuration cache and parallel execution, caching Gradle dependencies via setup-gradle actions, using affected module detection to test only modified modules, and tuning JVM heap memory.",
        "best_answer": (
            "Accelerating cold and warm CI builds requires addressing Gradle's configuration and execution phases systematically:\n\n"
            "1. **Remote Build Cache Infrastructure**:\n"
            "   - Ephemeral CI containers start without local cache. Enabling a remote HTTP build cache (e.g. Gradle Enterprise/Develocity or self-hosted HTTP cache) allows tasks that match input hashes to pull pre-compiled bytecode with `FROM-CACHE`, cutting build times by 50–70%.\n\n"
            "2. **Gradle Execution Flags**:\n"
            "   - Enable `org.gradle.parallel=true` to process independent Gradle subprojects concurrently.\n"
            "   - Enable `org.gradle.configuration-cache=true` to skip the configuration phase on subsequent invocations.\n"
            "   - Enable `org.gradle.caching=true`.\n\n"
            "3. **Affected Module Detection**:\n"
            "   - In large multi-module repositories, use tools like Dropbox's `AffectedModuleDetector` or custom Git diff inspection. Run tests and static analysis exclusively on changed modules and their transitive downstream dependents rather than the entire project.\n\n"
            "4. **JVM & Memory Tuning for CI Runners**:\n"
            "   - Ephemeral runners typically suffer from memory thrashing. Configure `-Xmx4g` to `-Xmx6g` with `-XX:+UseParallelGC` to minimize garbage collection pauses during intensive compilation."
        ),
        "deep_answer": (
            "From an architectural systems engineering angle, cache hygiene and task avoidability drive performance:\n\n"
            "1. **Task Cache Miss Hunting**: If a single task includes absolute file paths or system timestamps in its `@Input`, Gradle invalidates the task's cache key on every runner, turning `FROM-CACHE` into expensive recompilations. Teams run Gradle Build Scans regularly to audit task inputs and enforce path sensitivity (`PathSensitivity.RELATIVE`).\n\n"
            "2. **Push vs. Pull Cache Access Control**: Never allow every unverified PR to push to the remote build cache; a corrupted or poisoned cache entry on a feature branch can infect other builds. The main branch CI should be the only agent configured with `isPush = true` permissions, while PR builds have read-only (`isPush = false`) pull access.\n\n"
            "3. **KSP vs. KAPT Migration**: KAPT relies on Java stub generation which severely hampers build parallelization and cache performance. Migrating annotation processors to Kotlin Symbol Processing (KSP) delivers up to 2x faster compilation speed and native incremental processing."
        ),
        "follow_ups": [
            {
                "question": "Why should feature PR builds have read-only access to the remote Gradle build cache?",
                "answer": "To prevent cache poisoning, ensuring that only trusted, validated builds from the main branch populate cache entries."
            },
            {
                "question": "How does KSP improve build performance over KAPT in CI?",
                "answer": "KSP interacts directly with the Kotlin compiler AST without generating expensive intermediate Java stub files, reducing compilation time by up to 50%."
            }
        ]
    },
    {
        "id": "CIC-13",
        "arabic_explanation": (
            "كيف تتعامل مع الاختبارات المتقلبة (Flaky Tests)، وما هي سياسات إعادة المحاولة (Retries) والعزل (Quarantine) في الـ CI؟\n\n"
            "1. ما هو الـ Flaky Test وما خطورته؟\n"
            "   - هو اختبار يعطي نتائج متضاربة (ينجح أحياناً ويفشل أحياناً) لنفس الكود ونفس البيئة دون أي تغيير.\n   - خطورته: يدمر ثقة المطورين في الـ CI، ويجعل الفريق يتجاهل فشل الاختبارات (\"مجرد فليك، أعد تشغيل الـ Pipeline!\")، مما يؤدي لتمرير كوارث حقيقية للإنتاج.\n\n"
            "2. الأسباب التقنية للـ Flakiness في أندرويد:\n"
            "   - الاعتماد على `Thread.sleep` أو أوقات انتظار غير محددة بدلاً من `IdlingResource` أو `advanceUntilIdle()` في الـ Coroutines.\n   - الرسوم المتحركة (Animations) النشطة في المحاكي أثناء اختبارات الـ UI.\n   - الاعتماد على شبكة إنترنت حقيقية أو خوادم خارجية غير مستقرة بدلاً من MockWebServer.\n   - تسريب البيانات (State Leak) بين الاختبارات في قواعد بيانات Room المشتركة.\n\n"
            "3. استراتيجية العزل وإعادة المحاولة (Quarantine & Retry Policy):\n"
            "   - **إعادة المحاولة المحدودة (Bounded Retries)**: السماح لـ Gradle بإعادة تشغيل الاختبار الفاشل مرة أو مرتين كحد أقصى (`maxRetries = 1`) لمنع تعطيل الـ PRs العاجلة.\n   - **سياسة العزل الفوري (Quarantine)**: أي اختبار يفشل بشكل متقلب يتم تمييزه بـ `@FlakyTest`، ونقله فوراً من مسار فحص الـ PRs إلى مسار ليلي منعزل (Non-blocking Nightly Suite).\n   - **تذكرة عمل ذات أولوية (P1 Bug)**: فتح Issue فوري للفريق المسؤول، مع إعطاء مهلة محددة (SLA: مثلاً أسبوع) لإصلاحه أو حذفه نهائياً من المشروع."
        ),
        "practical_walkthrough": (
            "إعداد Gradle Test Retry وعزل الاختبارات المشكوك فيها عبر JUnit Categories:\n"
            "```kotlin\n"
            "// app/build.gradle.kts\n"
            "plugins {\n"
            "    id(\"org.gradle.test-retry\") version \"1.5.8\"\n"
            "}\n"
            "\n"
            "tasks.withType<Test>().configureEach {\n"
            "    retry {\n"
            "        // إعادة المحاولة فقط في بيئة الـ CI وبحد أقصى محاولة واحدة:\n"
            "        maxRetries.set(if (System.getenv(\"CI\") == \"true\") 1 else 0)\n"
            "        maxFailures.set(5) // إذا كان هناك أكثر من 5 أخطاء، أوقف البناء ولا تعيد المحاولة (فشل حقيقي)\n"
            "        failOnPassedAfterRetry.set(false) // يسمح بالنجاح المؤقت مع تسجيل الاختبار المتقلب\n"
            "    }\n"
            "\n"
            "    // استبعاد الاختبارات المعزولة (@Category(FlakyTest::class)) من فحص الـ PRs:\n"
            "    if (project.hasProperty(\"excludeFlaky\")) {\n"
            "        useJUnit {\n"
            "            excludeCategories(\"com.example.testing.FlakyTestCategory\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage flaky tests by addressing root causes (animations, unconfined coroutines, shared state), applying bounded retries in CI (max 1 retry) to prevent pipeline blockage, and enforcing a strict quarantine policy where flaky tests are moved out of blocking PR checks into non-blocking nightly suites until fixed.",
        "best_answer": (
            "Flaky tests undermine engineering trust and require an operational and technical mitigation policy:\n\n"
            "1. **Root-Cause Remediation**:\n"
            "   - Replace asynchronous delays and `Thread.sleep` with Kotlin Coroutines' `runTest` and `advanceUntilIdle()`.\n"
            "   - Enforce hermetic test environments: disable emulator animations via ADB, mock network layers with OkHttp MockWebServer, and use in-memory Room databases with strict `@Before`/`@After` teardowns.\n\n"
            "2. **Bounded Retries in CI**:\n"
            "   - Implement the Gradle Test Retry plugin configured to retry failed tests at most once (`maxRetries = 1`). Retries act as a temporary velocity buffer to prevent blocking innocent PRs while logging telemetry.\n\n"
            "3. **Automated Quarantine Protocol**:\n"
            "   - If a test passes only on retry, CI logs it as a flake metric. The test is immediately tagged (`@FlakyTest`) and quarantined from the blocking PR gate to a non-blocking scheduled suite.\n\n"
            "4. **SLA-Driven Resolution**:\n"
            "   - A P1 technical debt ticket is automatically generated for the owning squad. If not resolved within a defined SLA (e.g. 5 days), the quarantined test is deleted to keep test suites lean and trustworthy."
        ),
        "deep_answer": (
            "From an engineering telemetry and cultural perspective, flaky test tracking must be automated:\n\n"
            "1. **Flakiness Observability Dashboard**: Measure 'Flake Rate' across CI builds (total retries / total runs). If an organization's flake rate exceeds 1%, engineering leadership must treat test stabilization as a sprint blocker. Without visibility, engineers develop 'retry fatigue' where they blindly restart entire CI pipelines.\n\n"
            "2. **De-flaking via Repeated Local Execution**: When debugging a suspect test, run it 100 times in a loop locally using Gradle `--rerun-tasks`: `./gradlew test --tests 'com.app.SuspectTest' --repeat 100`. This reliably forces race conditions and coroutine leaks to surface.\n\n"
            "3. **The Anti-Pattern of Infinite Retries**: Treating retries as a permanent fix rather than an alert mechanism creates dangerous compounding flakiness. Two flaky tests with 90% pass rates have an 81% combined pass rate; 10 such tests drop overall pipeline reliability below 35%, rendering CI useless."
        ),
        "follow_ups": [
            {
                "question": "Why should tests that pass only after a retry still be flagged as failures in metrics?",
                "answer": "Because masked flakes degrade into persistent failures; recording them in metrics ensures visibility and accountability before they completely break the pipeline."
            },
            {
                "question": "How do you reproduce a race condition in a suspected flaky test locally?",
                "answer": "Run the specific test repeatedly in a loop (e.g. 100 times) using test runner repeat flags to expose timing variations."
            }
        ]
    },
    {
        "id": "CIC-14",
        "arabic_explanation": (
            "كيف تدير عملية الإطلاق التدريجي (Staged Rollout)، وبوابات معدل الأعطال (Crash-Rate Gates)، وخطط التراجع (Rollback Plans) في أندرويد؟\n\n"
            "1. معضلة التراجع (Rollback) في أندرويد:\n"
            "   - على عكس خوادم الويب، **لا يمكنك عمل Rollback فوري لإصدار أندرويد قديم** لأن نظام أندرويد يرفض تثبيت نسخة ذات `versionCode` أقل من المثبتة على جهاز المستخدم.\n   - بمجرد تثبيت التحديث على هواتف المستخدمين، لا يمكنك سحبه إجبارياً إلا بطرح تحديث جديد تماماً برقم أعلى.\n\n"
            "2. استراتيجية الإطلاق التدريجي (Staged Rollout):\n"
            "   - طرح التطبيق بنسب تصاعدية مدروسة: **1% -> 5% -> 20% -> 50% -> 100%** على مدار عدة أيام.\n   - الهدف: حصر نطاق الضرر (Blast Radius) في شريحة ضئيلة من المستخدمين إذا ظهرت كارثة غير متوقعة.\n\n"
            "3. بوابات جودة المراقبة (Crash-Rate Gates):\n"
            "   - مراقبة مؤشرات **Android Vitals** و **Firebase Crashlytics** فور بدء كل مرحلة:\n   - **Crash-free users**: يجب ألا يقل عن 99.9%.\n   - **User-perceived crash rate**: معيار جوجل في Vitals هو أقل من 1.09% (لتفادي معاقبة التطبيق في محركات بحث المتجر).\n   - إذا تجاوز معدل الأعطال النسبة المقبولة، يتم **إيقاف الطرح فوراً (Halt Rollout)**.\n\n"
            "4. خطة الاستجابة للكوارث (Disaster Recovery Plan):\n"
            "   - **الخط الدفاعي الأول (Feature Flags)**: إيقاف الميزة المسببة للكراش سحابياً عبر Firebase Remote Config فوراً، دون الحاجة لتحديث التطبيق.\n   - **الخط الدفاعي الثاني (Emergency Hotfix)**: إذا كان الكراش في كود التهيئة (Application.onCreate) ولا تعمل معه الأعلام، يتم عمل Hotfix فوري وزيادة الـ `versionCode` وطرحه للمتجر بنسبة 100%."
        ),
        "practical_walkthrough": (
            "مخطط منطقي لإدارة الطرح التدريجي ومراقبة الـ Crash Rate:\n"
            "```kotlin\n"
            "// معالجة الأخطاء الحرجة بالاعتماد على Remote Config كخط دفاع أول:\n"
            "class FeatureManager(private val remoteConfig: FirebaseRemoteConfig) {\n"
            "    fun isNewCheckoutFlowEnabled(): Boolean {\n"
            "        // إذا رصدنا كراشات في الإنتاج، نغير القيمة إلى false في الكونسول\n"
            "        // فيتم تعطيل الميزة فوراً لجميع المستخدمين خلال دقائق:\n"
            "        return remoteConfig.getBoolean(\"enable_new_checkout_flow\")\n"
            "    }\n"
            "}\n"
            "```\n"
            "جدول مراحل الطرح التدريجي القياسي:\n"
            "| اليوم | النسبة | الشرط للانتقال للمرحلة التالية |\n"
            "|---|---|---|\n"
            "| اليوم 1 | 1% | استقرار Vitals و Crash-free > 99.9% لمدة 24 ساعة |\n"
            "| اليوم 2 | 5% | لا توجد كراشات OOM أو فواتير متكررة |\n"
            "| اليوم 3 | 20% | فحص استقرار الخوادم الخلفية والـ API latency |\n"
            "| اليوم 4 | 50% | استمرار المؤشرات الخضراء |\n"
            "| اليوم 5 | 100% | إطلاق كامل لجميع المستخدمين |"
        ),
        "quick_answer": "Manage releases via staged rollouts (1% to 100%) to contain blast radius, gating progression behind Android Vitals and Crashlytics metrics (crash-free users > 99.9%). Since Android prohibits downward versionCode rollbacks, mitigate critical incidents by halting rollouts, toggling remote feature flags, or releasing an expedited hotfix with an incremented versionCode.",
        "best_answer": (
            "A disciplined mobile release rollout framework consists of three operational pillars:\n\n"
            "1. **Staged Rollout Cadence**:\n"
            "   - Releases progress through controlled cohorts: 1% -> 5% -> 20% -> 50% -> 100% over a 4 to 5-day cycle. This limits the blast radius of latent device-specific or OS-version bugs to a fraction of the user base.\n\n"
            "2. **Automated Quality Gates & Android Vitals**:\n"
            "   - Progression between stages requires meeting strict thresholds:\n"
            "     - Crash-free user rate $\\ge 99.9%$.\n"
            "     - User-perceived crash rate in Android Vitals below Google's 1.09% bad-behavior threshold.\n"
            "     - ANR rate below 0.47%.\n"
            "   - If any metric breaches thresholds, the staged rollout is immediately halted in Google Play Console.\n\n"
            "3. **Multi-Tiered Rollback Strategy**:\n"
            "   - Android OS strictly rejects installing an APK with a lower `versionCode` than the active installed build, making client-side rollbacks impossible.\n   - **Tier 1 (Instant)**: Kill-switch the faulty code path via server-side Feature Flags (Firebase Remote Config).\n   - **Tier 2 (Hotfix)**: If startup crashes prevent remote config fetches, branch a hotfix from the release tag, revert the culprit commit, increment `versionCode`, and expedite a 100% hotfix release."
        ),
        "deep_answer": (
            "From an organizational resilience and SRE perspective, release gating requires clear runbooks and automated alerting:\n\n"
            "1. **The 'Halting vs. Halved' Rollout Myth**: When you halt a staged rollout in Google Play Console, users who already received the update remain on that buggy version; halting only stops new users from downloading it. Teams must actively support the cohort stuck on the buggy version until the hotfix is published.\n\n"
            "2. **In-App Force Updates (Flexible vs. Immediate)**: When a severe zero-day vulnerability or corrupt local database migration occurs, a standard store update is insufficient because users may not update for weeks. Integrating the Google Play In-App Updates API with an `AppUpdateType.IMMEDIATE` flow forces a blocking full-screen update dialog on app launch for broken client versions.\n\n"
            "3. **Server-Side API Compatibility**: When rolling out a new app version over 5 days, backend APIs must support both old and new payload schemas simultaneously. Never deploy breaking API changes until the client staged rollout reaches 100% and adoption curves stabilize."
        ),
        "follow_ups": [
            {
                "question": "Why can't you simply deploy the previous APK version to Google Play if a release fails?",
                "answer": "Google Play and the Android OS Package Manager enforce strictly monotonic versionCode increments; downgrading versionCode causes an installation failure on user devices."
            },
            {
                "question": "What happens to users who already downloaded a faulty build if you halt a staged rollout?",
                "answer": "They remain on the faulty build; halting only prevents new users from downloading it, which is why feature flags or immediate hotfixes are required."
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
    for item in CIC_08_14:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions CIC-08 to CIC-14. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
