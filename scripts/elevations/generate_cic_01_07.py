#!/usr/bin/env python3
"""Generator for CIC-01 through CIC-07 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cic.json"

CIC_01_07 = [
    {
        "id": "CIC-01",
        "arabic_explanation": (
            "ما هو الفرق بين التكامل المستمر (CI)، والتسليم المستمر (Continuous Delivery)، والنشر المستمر (Continuous Deployment) في سياق تطبيقات الأندرويد؟\n\n"
            "1. التكامل المستمر (Continuous Integration - CI):\n"
            "   - المفهوم: دمج كود المطورين بانتظام في الفرع الرئيسي (Main/Trunk) عدة مرات في اليوم.\n"
            "   - الأتمتة: بمجرد فتح Pull Request، يُطلق السيرفر خط أنابيب آلي (Pipeline) يقوم بفحص: تجميع الكود (Build)، التحليل الساكن (Lint, Detekt, ktlint)، واختبارات الوحدة (Unit Tests).\n"
            "   - الهدف: اكتشاف الأخطاء مبكراً جداً (Fail Fast) ومنع تعطل الفرع الرئيسي.\n\n"
            "2. التسليم المستمر (Continuous Delivery - CD):\n"
            "   - المفهوم: الكود الموجود على الفرع الرئيسي جاهز دائماً للنشر للإنتاج في أي لحظة وبشكل آلي، ولكن **عملية الطرح الفعلي للجمهور (Release) تتطلب موافقة بشرية بنقرة زر (Manual Gate)**.\n"
            "   - في أندرويد: الأتمتة تبني حزمة الـ AAB الموقعة، وترفعها لمسار الاختبار الداخلي (Internal Testing) على Google Play Console، وتنتظر قرار فريق المنتج أو الـ QA لإطلاقها للمستخدمين.\n\n"
            "3. النشر المستمر (Continuous Deployment - CD):\n"
            "   - المفهوم: أي تغيير يمر بنجاح عبر الـ Pipeline يُنشر تلقائياً وبشكل كامل للإنتاج (Production) دون أي تدخل بشري.\n"
            "   - خصوصية الأندرويد: النشر المستمر الكامل المباشر لـ 100% من مستخدمي الإنتاج نادر وغير محبذ في تطبيقات الموبايل الحساسة؛ بسبب مراجعات Google Play غير الفورية (App Review latency)، واستحالة عمل Rollback فوري على أجهزة المستخدمين إذا حدث كراش كارثي، لذلك يُستعاض عنه بالتسليم المستمر مع الـ Staged Rollouts."
        ),
        "practical_walkthrough": (
            "مخطط GitHub Actions يوضح الفرق بين CI و Continuous Delivery في خط أنابيب أندرويد:\n"
            "```yaml\n"
            "# .github/workflows/android_ci_cd.yml\n"
            "name: Android CI/CD Pipeline\n"
            "\n"
            "on:\n"
            "  pull_request:\n"
            "    branches: [ main ] # المرحلة الأولى: Continuous Integration (CI)\n"
            "  push:\n"
            "    branches: [ main ] # المرحلة الثانية: Continuous Delivery (CD)\n"
            "\n"
            "jobs:\n"
            "  # 1. CI Stage: Runs on every PR to prevent regressions\n"
            "  ci_verification:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      - run: ./gradlew lintDebug testDebugUnitTest\n"
            "\n"
            "  # 2. CD Stage: Runs only on Main push, builds signed AAB & deploys to Internal Test track\n"
            "  cd_delivery:\n"
            "    needs: ci_verification\n"
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: ./gradlew bundleRelease\n"
            "      - name: Deploy to Google Play Internal Track (Ready for release approval)\n"
            "        uses: r0adkll/upload-google-play@v1\n"
            "        with:\n"
            "          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_JSON_KEY }}\n"
            "          packageName: com.company.app\n"
            "          releaseFiles: app/build/outputs/bundle/release/*.aab\n"
            "          track: internal # Continuous Delivery: Deployed to test ring, human gates production release\n"
            "```"
        ),
        "quick_answer": "Continuous Integration automates compiling, linting, and testing on every pull request to catch bugs early. Continuous Delivery ensures every commit on main automatically generates a signed release artifact published to an internal test track ready for one-click production release. Continuous Deployment eliminates that manual gate, automatically pushing directly to production.",
        "best_answer": (
            "The distinction between CI and the two forms of CD hinges on automation boundaries and release confidence:\n\n"
            "1. **Continuous Integration (CI)**:\n"
            "   - Developers integrate code into the shared main branch frequently. Every pull request triggers an automated pipeline running static analysis, ktlint, detekt, Android Lint, and local JVM unit tests, failing fast if regressions occur.\n\n"
            "2. **Continuous Delivery (CD)**:\n"
            "   - Automates the packaging, obfuscation (R8), signing, and deployment of release artifacts (AAB) to staging environments or Google Play internal test tracks. The application is perpetually release-ready, but triggering the production rollout involves a deliberate human decision.\n\n"
            "3. **Continuous Deployment (CD)**:\n"
            "   - Fully automated progression where every green commit on main is deployed directly to end users without manual gates.\n\n"
            "In mobile engineering, teams practice Continuous Delivery rather than pure Continuous Deployment because client-side updates cannot be instantaneously rolled back if critical zero-day crashes occur, and store review latency makes human release gating and staged rollouts essential."
        ),
        "deep_answer": (
            "From an engineering governance and mobile release engineering perspective, mobile CI/CD differs fundamentally from backend microservices:\n\n"
            "1. **The Asymmetry of Mobile Rollbacks**: In web backends, Continuous Deployment allows deploying 20 times a day because a faulty container can be rolled back in 30 seconds via Kubernetes blue/green routing. In mobile, once a faulty APK/AAB is installed on 500,000 devices, rolling it back requires compiling a hotfix, passing Google Play review (which can take hours or days), and waiting for users to update over Wi-Fi. Therefore, production releases must be treated with defense-in-depth.\n\n"
            "2. **Continuous Delivery with Staged Gates**: Senior teams implement Continuous Delivery up to Play Store Internal/Closed testing rings. From there, production release is managed via staged rollouts (e.g., 1% -> 5% -> 20% -> 100%) paired with automated crash-rate metrics (Vitals / Crashlytics threshold alarms).\n\n"
            "3. **Decoupling Deployment from Feature Exposure**: True agility in mobile is achieved by combining Continuous Delivery of the binary with server-driven Feature Flags (e.g. Firebase Remote Config or LaunchDarkly). The code is shipped continuously, but dark-launched and selectively toggled per user cohort without waiting for app store cycles."
        ),
        "follow_ups": [
            {
                "question": "Why is pure Continuous Deployment to 100% of production users risky on Android?",
                "answer": "Because client binary updates cannot be revoked instantly; once installed on user hardware, fixing an emergency crash requires a store review cycle and user app download."
            },
            {
                "question": "How do feature flags complement Continuous Delivery in mobile apps?",
                "answer": "They decouple binary deployment from feature release, allowing instant server-side kill-switching without waiting for store update approvals."
            }
        ]
    },
    {
        "id": "CIC-02",
        "arabic_explanation": (
            "ما هي المراحل النموذجية (Stages) في خط أنابيب أندرويد (Android CI Pipeline) المتكامل؟\n\n"
            "1. المراحل الأساسية لـ Android CI Pipeline:\n"
            "   - **1. Checkout & Cache Hydration**: تنزيل الكود واستعادة الكاش السحابي للـ Gradle wrapper والـ dependencies والـ build-cache لتقليل وقت التجميع.\n"
            "   - **2. Static Analysis & Linting**: فحص الكود الساكن عبر أسرع أدوات: ktlint/Spotless لفحص التنسيق، Detekt لقواعد الكود، وAndroid Lint لاكتشاف أخطاء الـ SDK ومشاكل الأداء والموارد المفقودة.\n"
            "   - **3. Unit Tests (JVM)**: تشغيل `testDebugUnitTest` لاختبارات الـ ViewModels والـ UseCases والـ Repositories. هذه المرحلة يجب أن تنتهي في أقل من دقيقتين.\n"
            "   - **4. Compilation & Assemble**: بناء الـ APK أو الـ AAB التجريبي للتأكد من خلو المشروع من أخطاء التجميع.\n"
            "   - **5. Instrumented & UI Tests**: تشغيل الاختبارات على أجهزة أو محاكيات حقيقية (غالباً عبر Matrix أو خدمات سحابية مثل Firebase Test Lab) لتغطية الـ critical user journeys.\n"
            "   - **6. Security & Size Checks**: فحص الثغرات الأمنية في الـ Dependencies (Dependency-Check)، وفحص حجم الـ APK بواسطة أدوات مثل Diffuse أو bundletool لمنع تسرب ملفات ضخمة.\n"
            "   - **7. Artifact Archival & Notification**: رفع ملفات الـ Test Reports و mapping.txt، وإرسال تنبيه على Slack/Teams بحالة البناء."
        ),
        "practical_walkthrough": (
            "مخطط تفصيلي لمراحل الـ CI Pipeline في ملف عمل GitHub Actions متوازي وعالي الأداء:\n"
            "```yaml\n"
            "# .github/workflows/pr_validation.yml\n"
            "name: PR Quality Gate\n"
            "on: [pull_request]\n"
            "\n"
            "jobs:\n"
            "  # المرحلة السريعة (Fail Fast): التنسيق والتحليل الساكن\n"
            "  static_analysis:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "      - name: Run Linters & Detekt\n"
            "        run: ./gradlew spotlessCheck detekt\n"
            "\n"
            "  # مرحلة اختبارات الوحدة السريعة\n"
            "  unit_tests:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "      - name: Run JVM Unit Tests\n"
            "        run: ./gradlew testDebugUnitTest\n"
            "\n"
            "  # مرحلة الفحص الأمني وحجم الحزمة (تعتمد على نجاح الفحوصات السابقة)\n"
            "  bundle_and_size:\n"
            "    needs: [static_analysis, unit_tests]\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "      - name: Build Debug APK & Analyze Size\n"
            "        run: ./gradlew assembleDebug\n"
            "```"
        ),
        "quick_answer": "A production Android CI pipeline consists of: Checkout and cache restoration, static analysis (formatting, Detekt, Android Lint), JVM unit testing (testDebugUnitTest), build assembly, instrumentation/UI testing on device clouds, APK/AAB size analysis, and artifact publishing or reporting.",
        "best_answer": (
            "A well-architected Android CI pipeline is structured into tiered, parallel stages designed to fail fast:\n\n"
            "1. **Environment Setup & Cache Hydration**:\n"
            "   - Checks out repository code, sets up the target JDK, and restores the remote Gradle build cache and dependency cache to avoid redundant network and compilation overhead.\n\n"
            "2. **Static Analysis & Linting**:\n"
            "   - Runs Spotless/ktlint for formatting, Detekt for code smell detection, and Android Lint with `--baseline` for framework deprecation and resource issues.\n\n"
            "3. **Local Unit Tests**:\n"
            "   - Executes `testDebugUnitTest` across all modules in parallel on the host JVM. This validates domain rules, ViewModels, and state machines within minutes.\n\n"
            "4. **Compilation & Assembly Verification**:\n"
            "   - Compiles debug and release variants (`assembleDebug`, `bundleRelease`) to detect missing dependencies or R8 configuration failures early.\n\n"
            "5. **Instrumentation & Performance Gates**:\n"
            "   - Executes end-to-end UI tests on emulators or cloud farms (Firebase Test Lab), accompanied by size regression diffing using tools like Diffuse to prevent bundle bloating."
        ),
        "deep_answer": (
            "Optimizing CI stages for team velocity requires strict pipeline choreography and tiering:\n\n"
            "1. **Fail-Fast Parallelization**: Do not run stages sequentially. Run static code checks and local unit tests in parallel. If ktlint or a unit test fails at minute 1, terminate remaining jobs immediately to conserve cloud runner credits and provide instant developer feedback.\n\n"
            "2. **Decoupling PR CI from Merge CI**: Running instrumented UI tests on every single commit inside an open PR creates bottlenecks and wastes resources. Mature teams run static analysis and unit tests on PR commits, while delegating heavy instrumented test suites and release bundle generation to nightly builds or the post-merge staging pipeline.\n\n"
            "3. **Artifact Retention & Reproducibility**: The pipeline must produce and store build outputs: test result XMLs for CI dashboards, R8 mapping files for crash de-obfuscation in production monitoring, and Baseline Profile outputs. Without automated mapping artifact archiving, tracing field crashes becomes impossible."
        ),
        "follow_ups": [
            {
                "question": "Why should static analysis and unit tests run before assemble tasks?",
                "answer": "To fail fast within seconds if formatting or tests break, avoiding the expensive 5-minute overhead of full APK compilation."
            },
            {
                "question": "How do you handle long-running instrumentation tests in PR pipelines?",
                "answer": "Run a smoke test subset on PRs, and schedule the exhaustive instrumentation test suite on nightly pipelines or merge trains."
            }
        ]
    },
    {
        "id": "CIC-03",
        "arabic_explanation": (
            "ما هي مخرجات البناء (Build Artifacts) ومسارات الإطلاق (Release Tracks) في تطوير تطبيقات أندرويد؟\n\n"
            "1. مخرجات البناء (Build Artifacts):\n"
            "   - **Android App Bundle (AAB)**: حزمة النشر الرسمية لـ Google Play. لا تُثبت مباشرة على الأجهزة، بل يقوم متجر جوجل بتقسيمها عبر Dynamic Delivery لتوليد Split APKs خاصة بكل جهاز بناءً على شاشته ومعالجه ولغته، مما يوفر 20–30% من الحجم.\n"
            "   - **APK (Universal / Split)**: حزمة التطبيق القابلة للتثبيت المباشر (`.apk`). تُستخدم للاختبارات الداخلية وسيرفرات الـ QA و Firebase App Distribution.\n"
            "   - **ملف الخرائط (mapping.txt)**: ينتجه R8/ProGuard أثناء عمل Shrinking & Obfuscation. ضروري جداً لفك تشفير الـ Stacktraces المبهمة (De-obfuscation) في Firebase Crashlytics.\n"
            "   - **ملفات الـ Baseline Profiles (`baseline.prof`)**: مخرجات يتم تضمينها داخل التطبيق لتوجيه نظام ART لترجمة الكود الهام إلى لغة الآلة مسبقاً (AOT) لتسريع وقت التشغيل بنسبة تصل لـ 30%.\n\n"
            "2. مسارات الإطلاق (Release Tracks) على Google Play Console:\n"
            "   - **Internal Testing**: حتى 100 مختبر داخلي. الإطلاق فوري (بدون مراجعة متجر تقريباً، بضع دقائق).\n"
            "   - **Closed Testing (Alpha/Beta)**: قوائم بريد محددة أو مجموعات Google Groups لاختبار ميزات محددة قبل الطرح العام.\n"
            "   - **Open Testing (Public Beta)**: يمكن لأي مستخدم على المتجر الانضمام للبيتا دون موافقة مسبقة.\n"
            "   - **Production (مع Staged Rollout)**: النسخة العامة المتاحة للملايين، ويتم طرحها تدريجياً بنسب تصاعدية (مثلاً: 1% -> 5% -> 20% -> 50% -> 100%)."
        ),
        "practical_walkthrough": (
            "إعداد Gradle لتوليد مخرجات البناء ونسخ الـ mapping.txt آلياً للأرشفة:\n"
            "```kotlin\n"
            "// app/build.gradle.kts\n"
            "android {\n"
            "    buildTypes {\n"
            "        release {\n"
            "            isMinifyEnabled = true\n"
            "            isShrinkResources = true\n"
            "            proguardFiles(\n"
            "                getDefaultProguardFile(\"proguard-android-optimize.txt\"),\n"
            "                \"proguard-rules.pro\"\n"
            "            )\n"
            "            signingConfig = signingConfigs.getByName(\"release\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// مهمة أتمتة لأرشفة ملف الـ mapping.txt الناتج مع رقم النسخة:\n"
            "tasks.register<Copy>(\"archiveMappingFile\") {\n"
            "    dependsOn(\"minifyReleaseWithR8\")\n"
            "    from(layout.buildDirectory.dir(\"outputs/mapping/release\"))\n"
            "    into(layout.projectDirectory.dir(\"release-artifacts/mappings\"))\n"
            "    include(\"mapping.txt\")\n"
            "    rename { \"mapping-v${android.defaultConfig.versionName}.txt\" }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Build artifacts are the compiled deliverables of a build: AAB for Play Store distribution, APKs for direct testing, mapping.txt for R8 crash de-obfuscation, and baseline profiles for startup speed. Release tracks in Google Play Console are tiered delivery rings: Internal (fast team testing), Closed (controlled cohorts), Open (public beta), and Production (staged rollout to general users).",
        "best_answer": (
            "Build artifacts and release tracks form the operational pipeline connecting local compilation to production delivery:\n\n"
            "1. **Core Android Build Artifacts**:\n"
            "   - **Android App Bundle (.aab)**: The mandatory distribution format for Google Play. Enables Dynamic Delivery where Google Play generates device-optimized Split APKs tailored to screen density, language, and CPU architecture (ABI).\n"
            "   - **APK (.apk)**: Standalone installable packages primarily built for local development, QA testing, and distribution via Firebase App Distribution.\n"
            "   - **ProGuard / R8 Mapping File (`mapping.txt`)**: Crucial metadata that maps obfuscated class and method names back to original Kotlin source lines. Without uploading this to Crashlytics or Play Console, stack traces remain unreadable.\n"
            "   - **Baseline Profile (`baseline.prof`)**: Compiled profile rules that guide ART ahead-of-time compilation for instant app startup.\n\n"
            "2. **Google Play Release Tracks**:\n"
            "   - **Internal Testing Track**: Fast-tracked to up to 100 authorized testers, bypassing deep review gates in minutes.\n"
            "   - **Closed (Alpha/Beta) Track**: Targeted tester pools for feature validation.\n"
            "   - **Open Track**: Broad public opt-in beta testing.\n"
            "   - **Production Track**: The general consumer release channel, configured with staged percentage rollouts (1% to 100%) to mitigate blast radius."
        ),
        "deep_answer": (
            "From an architectural release management standpoint, artifact immutability and track promotion are fundamental:\n\n"
            "1. **Artifact Immutability**: A fundamental CI/CD anti-pattern is compiling one artifact for QA testing and recompiling another binary for production. High-performing teams compile a single signed release AAB once, promote it through Internal -> Beta -> Production tracks without rebuilding. Recompiling introduces timestamp drift, dependency version discrepancies, and untracked code changes.\n\n"
            "2. **Dynamic Delivery & App Slicing**: Distributing raw Universal APKs inflates download sizes by bundling multiple densities (hdpi to xxxhdpi) and CPU ABIs (armeabi-v7a, arm64-v8a, x86_64). Google Play uses the AAB to serve minimal split APKs, reducing data usage and uninstallation rates.\n\n"
            "3. **Automated Crashlytics Symbol Uploading**: CI workflows must integrate the Firebase Crashlytics Gradle plugin (`uploadCrashlyticsSymbolFileRelease`) or Play Developer API to guarantee that every release artifact is strictly paired with its corresponding obfuscation mapping in observability tools."
        ),
        "follow_ups": [
            {
                "question": "What happens if you release an app without uploading mapping.txt to Crashlytics?",
                "answer": "Crash reports show obfuscated symbols like `a.b.c(SourceFile:1)` making it impossible to identify the culprit line or method in production."
            },
            {
                "question": "Why shouldn't you recompile the app when moving from Beta to Production track?",
                "answer": "Recompiling violates artifact immutability and risks shipping untested bytecode differences; the exact binary validated by QA must be promoted."
            }
        ]
    },
    {
        "id": "CIC-04",
        "arabic_explanation": (
            "قارن بين أوامر Git الأساسية: `merge`، و `rebase`، و `squash`، و `revert`، و `reset` من حيث السلوك وتعديل التاريخ وحالات الاستخدام؟\n\n"
            "1. المقارنة الهندسية الشاملة:\n"
            "   - **`git merge`**: يدمج فرعين عبر إنشاء commit جديد يُسمى Merge Commit (يمتلك 2 parents). يحافظ على التاريخ كاملاً بكل تفاصيله وتسلسله الزمني، ولكنه ينتج تاريخاً متشابكاً (Non-linear history).\n"
            "   - **`git rebase`**: يعيد تشغيل (Replay) التغييرات الخاصة بالفرع الحالي فوق قمة الفرع المستهدف (HEAD). يُنشئ تاريخاً خطياً نظيفاً جداً (Linear history)، ولكنه **يعيد كتابة التاريخ (Rewrites commit hashes)**، لذا يُحظر استخدامه على الفروع العامة المشتركة.\n"
            "   - **`git squash`**: يدمج عدة commits صغيرة أو تجريبية من فرع الميزة في commit واحد نظيف وذري (Atomic Commit). ممتاز لإخفاء رسائل الـ commits الفوضوية (مثل: \"fix typo\", \"wip\") قبل الدمج في Main.\n"
            "   - **`git revert`**: يلغي تأثير commit قديم عبر **إنشاء commit جديد معاكس (Forward-looking inverse commit)**. آمن 100% على الفروع المشتركة لأنه لا يعبث بالتاريخ إطلاقاً.\n"
            "   - **`git reset`**: يرجع مؤشر الفرع إلى نقطة زمنية سابقة في التاريخ. يمسح الـ commits من التاريخ، وإذا رُفعت للـ remote تتطلب `git push --force`، مما يجعله خطيراً على الفروع المشتركة."
        ),
        "practical_walkthrough": (
            "أمثلة عملية توضح الفوارق بين هذه الأوامر في بيئة العمل اليومية:\n"
            "```bash\n"
            "# 1. Rebase فرعك المحلي على أحدث تغييرات main قبل فتح الـ PR (تاريخ خطي نظيف):\n"
            "git checkout feature/user-profile\n"
            "git fetch origin\n"
            "git rebase origin/main\n"
            "\n"
            "# 2. Squash دمج عدة commits أثناء الـ rebase التفاعلي:\n"
            "git rebase -i HEAD~3\n"
            "# في المحرر: غير 'pick' إلى 'squash' أو 's' للكوميتات الثانية والثالثة\n"
            "\n"
            "# 3. Revert آمن لكوميت سبب كراش على main المشترك (ينشئ كوميت جديد يعكس التغيير):\n"
            "git checkout main\n"
            "git revert 4f8a91b\n"
            "git push origin main # مسموح بدون force push لأن التاريخ لم يعد كتابته!\n"
            "\n"
            "# 4. Reset محلي لإلغاء آخر كوميت مع الحفاظ على التغييرات في الكود للتعديل:\n"
            "git reset --soft HEAD~1\n"
            "```"
        ),
        "quick_answer": "Merge joins branches preserving full history with a merge commit. Rebase replays commits linearly on top of upstream, rewriting hashes. Squash collapses multiple commits into a single atomic commit. Revert creates a new inverse commit to safely undo changes on shared branches, and Reset moves the branch pointer backward, rewriting history.",
        "best_answer": (
            "These five Git operations govern how branch histories are combined, rewritten, or corrected:\n\n"
            "1. **`git merge`**:\n"
            "   - Integrates diverged branches by creating a 3-way merge commit with two parents. It guarantees complete historical accuracy and context, but creates a non-linear graph with merge commit noise.\n\n"
            "2. **`git rebase`**:\n"
            "   - Re-applies local commits one by one on top of the target base branch. Yields a clean, perfectly linear commit history. Because it assigns new commit SHA hashes, it must never be run on public shared branches.\n\n"
            "3. **`git squash`**:\n"
            "   - Compresses a series of incremental commits into a single commit. Frequently used in PR merges (Squash and Merge) to condense exploratory development into a single logical, bisect-friendly commit on main.\n\n"
            "4. **`git revert`**:\n"
            "   - Safely rolls back changes by creating a new forward commit containing the inverse diff. It preserves history and causes no merge conflicts for teammates on shared branches.\n\n"
            "5. **`git reset`**:\n"
            "   - Adjusts the current branch HEAD backward in time. Rewrites branch history and requires forced pushes if already remote, making it suitable only for local unshared work."
        ),
        "deep_answer": (
            "In team Git architecture and CI governance, choosing between merge, rebase, and squash impacts debugging and bisecting:\n\n"
            "1. **Git Bisect Optimization**: A linear history generated by `git rebase` or `squash and merge` makes `git bisect` fast and reliable. When messy merge commit graphs exist, automated bisect scripts frequently stumble into broken intermediary states where commits were merged half-baked.\n\n"
            "2. **The Squash vs. Rebase Debate in PRs**: Squash-and-merge is preferred in many Android teams because it reduces PR clutter to a single cohesive feature commit linked to a Jira/Issue ID. However, if a 2,000-line PR contains 10 logical architectural refactors, squashing them destroys the context of each distinct change. A clean interactive rebase (`git rebase -i`) preserving 3 atomic commits is superior in complex refactorings.\n\n"
            "3. **Golden Rule of Git Rebase**: Never rebase a branch that has been published and shared with other engineers. Rebase changes commit SHAs; when peers pull the rebased branch, Git interprets their identical local commits as divergent, creating duplicate commits and painful merge conflicts."
        ),
        "follow_ups": [
            {
                "question": "What is the primary risk of using rebase on a shared team branch?",
                "answer": "It rewrites commit hashes, causing teammates' local branches to diverge and creating duplicate commits and messy conflict resolutions."
            },
            {
                "question": "How does squash-merge benefit git bisect?",
                "answer": "It ensures every commit on main is a complete, working, compilable state rather than a half-broken 'work in progress' commit."
            }
        ]
    },
    {
        "id": "CIC-05",
        "arabic_explanation": (
            "قارن بين `git reset --soft` و `git reset --hard` (بالإضافة إلى `--mixed`) وماذا يحدث للـ HEAD والـ Index وبيئة العمل؟\n\n"
            "1. شجرة Git الثلاثية (The Three Trees):\n"
            "   - **HEAD**: مؤشر آخر commit تم تسجيله.\n"
            "   - **Index (Staging Area)**: الملفات المجهزة للـ commit القادم (`git add`).\n"
            "   - **Working Tree (Working Directory)**: الملفات الموجودة حالياً على قرصك الصلب داخل مجلد المشروع.\n\n"
            "2. المقارنة التفصيلية بين أنواع الـ Reset:\n"
            "   - **`git reset --soft <commit>`**:\n"
            "     * يحرك مؤشر HEAD فقط إلى الكوميت المحدد.\n"
            "     * **يترك الـ Index والـ Working Tree كما هما تماماً**.\n"
            "     * النتيجة: كل التغييرات التي حدثت بعد هذا الكوميت تظل في حالة **Staged** (مجهزة للكوميت)، ممتازة جداً إذا أردت تعديل رسالة الكوميت أو دمج آخر 3 كوميتات محلياً.\n"
            "   - **`git reset --mixed <commit>` (الوضع الافتراضي)**:\n"
            "     * يحرك HEAD ويعيد تعيين الـ Index ليطابق الكوميت.\n"
            "     * **يترك الـ Working Tree سليمة**.\n"
            "     * النتيجة: التغييرات تظل موجودة في ملفاتك ولكنها تصبح **Unstaged** (غير مجهزة).\n"
            "   - **`git reset --hard <commit>`**:\n"
            "     * يحرك HEAD ويعيد تعيين الـ Index ويعيد تعيين الـ Working Tree!\n"
            "     * **يمسح كل التغييرات غير المسجلة تماماً من على القرص**.\n"
            "     * أمر تدميري (Destructive): لا يُستخدم إلا إذا كنت متأكداً بنسبة 100% أنك تريد التخلص من كل ما قمت به والعودة لتلك النقطة في الزمن."
        ),
        "practical_walkthrough": (
            "سيناريوهات عملية توضح متى تستخدم كل نوع من الـ Reset:\n"
            "```bash\n"
            "# سيناريو 1: قمت بعمل commit لرسالة خاطئة وتريد إعادة تجهيز الكود مع تعديل بسيط:\n"
            "git commit -m \"wip featur\"\n"
            "git reset --soft HEAD~1\n"
            "# الآن كل الملفات ما زالت في الـ Staging Area:\n"
            "git status # shows: Changes to be committed\n"
            "git commit -m \"feat(auth): implement biometric login challenge\"\n"
            "\n"
            "# سيناريو 2: قمت بعمل commit وأدركت أنك تريد فصل الملفات إلى كوميتين منفصلين:\n"
            "git reset --mixed HEAD~1 # أو ببساطة git reset HEAD~1\n"
            "git status # shows: Changes not staged for commit\n"
            "git add UserAuth.kt && git commit -m \"feat: add auth service\"\n"
            "git add UserAuthTest.kt && git commit -m \"test: add auth unit tests\"\n"
            "\n"
            "# سيناريو 3: تجربة فاشلة تماماً وتريد مسح كل ما كتبته والعودة لفرع main النظيف:\n"
            "git reset --hard origin/main\n"
            "# تم مسح كل التعديلات غير المسجلة والمسجلة بعد origin/main!\n"
            "```"
        ),
        "quick_answer": "Git reset --soft moves HEAD back to a specified commit leaving both the Index and Working Directory intact, keeping changes staged. Git reset --mixed (the default) moves HEAD and resets the Index, leaving changes unstaged in the Working Tree. Git reset --hard resets HEAD, Index, and Working Tree, permanently discarding all changes.",
        "best_answer": (
            "The difference between Git reset modes lies in how they interact with Git's three trees (HEAD, the Index, and the Working Tree):\n\n"
            "1. **`git reset --soft <commit>`**:\n"
            "   - Updates the HEAD ref pointer to the target commit.\n"
            "   - Does NOT touch the Index (Staging area) or the Working Tree.\n"
            "   - All changes from the undone commits remain staged, ready to be immediately re-committed. Ideal for re-organizing commits or squashing local work.\n\n"
            "2. **`git reset --mixed <commit>` (Default)**:\n"
            "   - Updates HEAD and resets the Index to match the target commit.\n"
            "   - Leaves the Working Tree unmodified on disk.\n"
            "   - All changes remain intact in your files but appear as unstaged modifications. Useful for selectively re-staging files into atomic commits.\n\n"
            "3. **`git reset --hard <commit>`**:\n"
            "   - Updates HEAD, resets the Index, and forces the Working Tree to match the target commit.\n"
            "   - Completely obliterates all tracked modifications in the working directory.\n"
            "   - It is a destructive operation; uncommitted local work cannot be recovered."
        ),
        "deep_answer": (
            "From an operational safety and disaster recovery perspective, understanding reset boundaries is critical:\n\n"
            "1. **Disaster Recovery via `git reflog`**: If a developer executes an accidental `git reset --hard HEAD~5` and loses committed work, the commits are not instantly wiped from Git's object database. As long as those commits were previously committed, their SHA identifiers exist in the local reference log. Running `git reflog`, identifying the previous commit hash, and running `git reset --hard <previous-sha>` fully restores the lost state.\n\n"
            "2. **The Danger with Untracked Files**: `git reset --hard` only affects files tracked by Git. Untracked files (new files never staged via `git add`) are left untouched on disk. To wipe both tracked and untracked artifacts, teams run `git clean -fd` alongside `git reset --hard`.\n\n"
            "3. **CI Cleaning Best Practices**: On self-hosted CI runners that reuse workspaces across pipeline runs, running `git reset --hard HEAD && git clean -ffdx` ensures a 100% clean, pristine workspace without residual build artifacts from previous builds."
        ),
        "follow_ups": [
            {
                "question": "Can you recover commits lost after an accidental `git reset --hard`?",
                "answer": "Yes, using `git reflog` to locate the commit hash before the reset and running `git reset --hard <sha>`."
            },
            {
                "question": "What is the primary use case for `git reset --soft HEAD~1`?",
                "answer": "Undoing the last commit while keeping all changes staged to rewrite the commit message or add missing files."
            }
        ]
    },
    {
        "id": "CIC-06",
        "arabic_explanation": (
            "لماذا يعتبر أمر `git revert` أكثر أماناً من `git reset` على الفروع المشتركة (Shared Branches)؟\n\n"
            "1. جوهر المشكلة في الفروع المشتركة:\n"
            "   - الفروع المشتركة (مثل `main`, `develop`, `release/*`) يقوم بسحبها (Pull) والعمل عليها عشرات المهندسين وسيرفرات الـ CI/CD.\n"
            "   - إذا استخدمت `git reset` لمسح كوميت سبب مشكلة، فأنت **تغير تاريخ الفرع إلى الوراء**.\n"
            "   - لرفع هذا التغيير للـ Remote، ستضطر لاستخدام `git push --force`، وهو ما يكسر تزامن كل المهندسين الآخرين.\n\n"
            "2. كوارث الـ `git reset` على الفروع المشتركة:\n"
            "   - **تكرار الكوميتات وتضاربها**: عندما يقوم زملاؤك بعمل `git pull`، سيرى Git أن فرعهم المحلي يملك الكوميت الذي حذفته، فيقوم بدمجه مرة أخرى (Re-merge)، ويعود الخطأ الذي حذفته إلى الحياة!\n   - **فقدان التدقيق (Audit Trail)**: مسح الكوميت يحذف الدليل على من كتب الكود ومتى ظهرت المشكلة.\n\n"
            "3. لماذا `git revert` هو الخيار الاحترافي؟:\n"
            "   - **تاريخ تطلعي للأمام (Forward-only)**: ينشئ كوميت جديد تماماً يقوم بعكس التغييرات (Inverse Diff).\n   - **دفع عادي دون Force**: يرفع للـ Remote باستخدام `git push` الطبيعي دون الحاجة لـ `--force`.\n   - **تزامن سلس**: عندما يقوم الزملاء بعمل `git pull`، يتحدث كودهم بسلاسة دون تعارضات أو كسر لفروعهم."
        ),
        "practical_walkthrough": (
            "مقارنة عملية توضح الفرق في سيناريو إصلاح خطأ إنتاجي على الفرع المشترك:\n"
            "```bash\n"
            "# ❌ السيناريو الخاطئ والخطير (Reset على فرع مشترك):\n"
            "git checkout main\n"
            "git reset --hard HEAD~1\n"
            "git push origin main --force # ⚠️ خطر كارثي: يمسح كوميتات الزملاء ويعطل الـ CI!\n"
            "\n"
            "# ✅ السيناريو الهندسي الآمن والصحيح (Revert على فرع مشترك):\n"
            "git checkout main\n"
            "git pull origin main\n"
            "\n"
            "# 1. فحص الـ log لتحديد الـ hash للكوميت المعيب:\n"
            "# e.g., commit 9a8b7c6 \"feat: add experimental payment sdk\"\n"
            "\n"
            "# 2. إنشاء كوميت عكسي يلغي التغييرات مع رسالة واضحة:\n"
            "git revert 9a8b7c6 -m 1 # (إذا كان merge commit نحدد الـ parent برقم 1)\n"
            "\n"
            "# 3. دفع التغيير للأمام بسلاسة وبدون أي force:\n"
            "git push origin main\n"
            "# النتيجة: تم التراجع عن الخطأ، مع الحفاظ على سجل التدقيق وتزامن الزملاء.\n"
            "```"
        ),
        "quick_answer": "Git revert is safer on shared branches because it creates a new forward-moving commit that inverts the target changes without rewriting history. Git reset rewrites history and requires force-pushing, which corrupts teammates' branches, causes ghost commit re-merges, and destroys audit logs.",
        "best_answer": (
            "On shared branches like `main` or release stabilization branches, `git revert` is the only safe undo mechanism for three core reasons:\n\n"
            "1. **Forward-Only History (No Force-Push Required)**:\n"
            "   - `git revert <sha>` records a new commit containing the exact inverse diff of the flawed commit. Because the branch tip advances forward linearly, it can be pushed with a standard `git push` without requiring destructive force pushes (`git push --force`).\n\n"
            "2. **Teammate Synchronization & Ghost Merges**:\n"
            "   - If you use `git reset` and force-push to a shared branch, any collaborator whose local clone still has the erased commit will unknowingly re-introduce it the next time they pull or merge, causing ghost bug resuscitations and severe merge conflicts.\n\n"
            "3. **Compliance and Auditability**:\n"
            "   - Enterprise compliance frameworks (such as SOC2 or ISO 27001) mandate an immutable audit trail. `git revert` transparently documents that a feature was committed, caused an issue, and was subsequently rolled back, preserving full attribution."
        ),
        "deep_answer": (
            "Handling reverts on complex merge commits presents an architectural challenge that senior engineers must navigate:\n\n"
            "1. **Reverting Merge Commits (`git revert -m 1`)**: When reverting a merge commit, Git does not know which of the two parents represents the mainline. Passing `-m 1` specifies that the first parent (the target branch, like `main`) is the baseline. This reverts the changes introduced by the feature branch.\n\n"
            "2. **The Re-Merge Dilemma**: A critical nuance occurs when re-introducing the feature later. If you simply re-merge the original feature branch after reverting it, Git sees that the commits are already in history and **will not re-apply the reverted code**! To re-introduce the feature, you must execute `git revert <revert-commit-sha>` (reverting the revert) before merging new fixes.\n\n"
            "3. **Branch Protection Enforcements**: Mature teams configure branch protection rules in GitHub or GitLab that strictly disallow `git push --force` or `--force-with-lease` on `main`, enforcing `git revert` by operational policy."
        ),
        "follow_ups": [
            {
                "question": "What happens if you try to merge a feature branch that was previously reverted on main?",
                "answer": "Git will not re-apply the feature diff because it considers those commits already in history; you must revert the revert commit first."
            },
            {
                "question": "Why is the `-m` flag required when reverting a merge commit?",
                "answer": "Because a merge commit has multiple parents, so `-m 1` explicitly designates the mainline parent to calculate the reverse diff against."
            }
        ]
    },
    {
        "id": "CIC-07",
        "arabic_explanation": (
            "ما هي أدوات Git المتقدمة: `git stash`، و `git cherry-pick`، ومفهوم الـ Fork، ومتى يُستخدم كل منها؟\n\n"
            "1. تخزين العمل المؤقت (`git stash`):\n"
            "   - يقوم بحفظ التغييرات غير المسجلة مؤقتاً في Stash Stack وتفريغ الـ Working Tree لتعود نظيفة.\n"
            "   - متى يُستخدم؟ عندما تكون في منتصف ميزة وتطلب منك القيادة فجأة إصلاح خطأ طارئ (Hotfix) على فرع آخر، أو عندما تريد عمل `git pull` ولكن تغييراتك المحلية تمنع ذلك.\n"
            "   - ملاحظة هامة: `git stash` الافتراضي يخزن الملفات المعدلة المسجلة فقط؛ لتخزين الملفات الجديدة غير المسجلة (Untracked) يجب استخدام `git stash -u`.\n\n"
            "2. انتقاء الكوميتات (`git cherry-pick`):\n"
            "   - يتيح لك أخذ commit محدد بالـ hash بتاعه من فرع معين، وإعادة تطبيقه فقط دون بقية الفرع على فرعك الحالي.\n"
            "   - متى يُستخدم؟ في سيناريو الـ Backporting: إصلاح Bug على فرع التطوير `main` وتريد تطبيق نفس الإصلاح على فرع الإنتاج القديم `release/2.4` دون سحب ميزات `main` غير الجاهزة.\n\n"
            "3. التفريع المستقل (Fork):\n"
            "   - استنساخ كامل للمستودع على مستوى السيرفر (GitHub/GitLab) تحت حسابك الشخصي أو منظمة منفصلة.\n"
            "   - متى يُستخدم؟ في مشاريع الـ Open Source والمكتبات الخارجية (Libraries)، أو عندما لا يملك المطور صلاحيات الكتابة (Push) على المستودع الأصلي، فيقوم بعمل Fork ورفع التغييرات إليه ثم فتح Pull Request للمستودع الأصلي (Upstream)."
        ),
        "practical_walkthrough": (
            "أمثلة لأوامر `stash` و `cherry-pick` الشائعة في بيئة العمل اليومية:\n"
            "```bash\n"
            "# 1. استخدام git stash مع الملفات غير المتابعة (untracked files):\n"
            "git stash push -u -m \"WIP: payment card validation logic\"\n"
            "git checkout hotfix/crash-fix\n"
            "# ... إصلاح العطل ورفعه ...\n"
            "git checkout feature/payment\n"
            "git stash pop # استعادة التغييرات ومسحها من الـ stash stack\n"
            "\n"
            "# 2. استخدام cherry-pick لنقل إصلاح أمني من main إلى فرع الإصدار release-v1.4:\n"
            "git checkout release/v1.4\n"
            "git log origin/main --oneline -n 3 # العثور على الكوميت المطلوب، e.g., c8d9e0f\n"
            "git cherry-pick c8d9e0f\n"
            "git push origin release/v1.4\n"
            "\n"
            "# 3. مزامنة الـ Fork المحلي مع المستودع الأصلي (Upstream):\n"
            "git remote add upstream https://github.com/original-org/android-core.git\n"
            "git fetch upstream\n"
            "git checkout main\n"
            "git merge upstream/main\n"
            "```"
        ),
        "quick_answer": "Git stash shelves uncommitted changes to allow switching branches cleanly. Git cherry-pick applies a specific commit by hash from another branch onto the current branch without merging the whole branch. A Fork is a server-side repository copy allowing developers to contribute via pull requests without write permissions to the upstream repository.",
        "best_answer": (
            "These three Git mechanisms solve distinct workflow and isolation problems:\n\n"
            "1. **`git stash`**:\n"
            "   - Temporarily shelves uncommitted changes (both staged and unstaged) onto an internal stack (`stash@{0}`), returning the working directory to a pristine HEAD state.\n"
            "   - Crucial for rapid context-switching, such as investigating an urgent production bug while mid-refactor. Using `-u` (include untracked) ensures newly created files are also stashed.\n\n"
            "2. **`git cherry-pick <commit-sha>`**:\n"
            "   - Extracts the exact diff introduced by a single commit from any branch and applies it as a brand-new commit on the currently checked-out branch.\n"
            "   - Ideal for backporting critical bug fixes from `main` to existing maintenance or release branches without pulling unreleased features.\n\n"
            "3. **Fork**:\n"
            "   - A remote server-side clone of a repository hosted under an independent user or organization account.\n"
            "   - Establishes a decoupled contribution boundary standard in open-source projects or enterprise contractor models, where external contributors lack direct push permissions and submit pull requests across forks."
        ),
        "deep_answer": (
            "From an engineering governance standpoint, there are subtle pitfalls with cherry-pick and stash:\n\n"
            "1. **The Cherry-Pick Duplicate Commit Hazard**: When you cherry-pick commit `A` into branch `B`, Git creates a new commit `A'` with a different hash. If branch `B` is later merged back into the original branch, Git must reconcile two commits that share identical diffs. In complex histories, this can trigger redundant conflict resolution or misleading blame graphs. Always record origin metadata using `git cherry-pick -x` to append the source commit hash to the commit message.\n\n"
            "2. **Stash Volatility in Team Environments**: Git stashes are local to your workstation and not backed up to the remote repository. Leaving large, multi-day refactors in `git stash` risks unrecoverable data loss during machine failures or accidental directory cleanups (`git stash drop` or hard cleans). Incomplete work should instead be committed to a personal remote draft branch (`draft/feature-wip`).\n\n"
            "3. **Upstream Fork Synchronization**: In forked workflows, keeping the local fork synchronized with `upstream` via automated rebase workflows prevents massive drift and painful merge conflicts when PRs are opened against the canonical repo."
        ),
        "follow_ups": [
            {
                "question": "Why should you use the `-x` flag when cherry-picking commits?",
                "answer": "It automatically records the original commit SHA in the commit message, preserving provenance and simplifying future auditability."
            },
            {
                "question": "What is the difference between `git stash pop` and `git stash apply`?",
                "answer": "`git stash pop` applies the top stash and immediately drops it from the stash stack, whereas `git stash apply` leaves it in the stack."
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
    for item in CIC_01_07:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions CIC-01 to CIC-07. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
