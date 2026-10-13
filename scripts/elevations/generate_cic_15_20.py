#!/usr/bin/env python3
"""Generator for CIC-15 through CIC-20 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "cic.json"

CIC_15_20 = [
    {
        "id": "CIC-15",
        "arabic_explanation": (
            "ما هي تعارضات Git (Conflicts) التي يمكن أن يسببها التراجع عن كوميت قديم (`git revert`)، وكيف يتم حلها؟\n\n"
            "1. طبيعة التعارض عند عمل Revert لكوميت قديم:\n"
            "   - عندما تقوم بعمل `git revert` لكوميت حدث منذ أسابيع (مثلاً قبل 30 كوميت)، فإن Git يحاول تطبيق **عكس التغيير (Inverse Patch)** بدقة على الكود الحالي.\n   - إذا كانت الكوميتات التي تلت ذلك الكوميت قد عدلت نفس الأسطر، أو غيرت أسماء الكلاسات أو الحزم (Refactoring)، أو حذفت الملف الأصلي، فإن Git لن يستطيع تطبيق التراجع آلياً وسيتوقف معلناً عن **Merge Conflict**.\n\n"
            "2. أنواع التعارضات الشائعة:\n"
            "   - **1. تعارضات نصية مباشرة (Content Conflicts)**: الكود المحذوف تم تعديل أسطره لاحقاً بواسطة ميزات أخرى. تظهر علامات التعارض القياسية (`<<<<<<< HEAD`, `=======`, `>>>>>>>`).\n   - **2. تعارضات حذف ونقل الملفات (Tree / Rename Conflicts)**: الكوميت القديم أنشأ ملفاً، وكوميت لاحق نقله إلى مجلد آخر أو حذفه، فيحتار Git في كيفية عكس التغيير.\n   - **3. تعارضات دلالية غير مرئية (Semantic / Compile Conflicts)**: أخطر نوع! قد ينجح الـ Revert دون أي تضارب نصي في Git، ولكن الكود لا يجمع (Compilation Error) أو يسبب كراش وقت التشغيل لأن دوال أخرى في النظام أصبحت تعتمد على وجود الكلاسات أو الـ APIs التي قمت بالتراجع عنها!\n\n"
            "3. خطوات الحل الهندسي:\n"
            "   - حل التعارضات النصية يدوياً في الملفات.\n   - تشغيل `./gradlew compileDebugKotlin` و `./gradlew testDebugUnitTest` فوراً قبل إتمام الـ commit للتأكد من السلامة الدلالية للـ Revert."
        ),
        "practical_walkthrough": (
            "خطوات حل تعارض ناتج عن revert لكوميت قديم بالخطوات والأوامر:\n"
            "```bash\n"
            "# 1. محاولة التراجع عن كوميت قديم:\n"
            "git revert 3c7a10f\n"
            "# المخرجات:\n"
            "# error: could not revert 3c7a10f... feat: add loyalty reward engine\n"
            "# hint: after resolving the conflicts, mark the corrected paths with 'git add <paths>'\n"
            "\n"
            "# 2. فحص الملفات المتعارضة:\n"
            "git status # يوضح: both modified: app/src/main/java/com/app/CheckoutViewModel.kt\n"
            "\n"
            "# 3. فتح الملف وحل علامات التعارض النصية:\n"
            "# إزالة أسطر الـ loyalty engine مع الإبقاء على تعديلات الدفع الجديدة بأمان\n"
            "\n"
            "# 4. التحقق الحاسم من سلامة التجميع والاختبارات:\n"
            "./gradlew compileDebugKotlin testDebugUnitTest\n"
            "\n"
            "# 5. استكمال الـ Revert بعد نجاح التجميع:\n"
            "git add app/src/main/java/com/app/CheckoutViewModel.kt\n"
            "git revert --continue\n"
            "git push origin main\n"
            "```"
        ),
        "quick_answer": "Reverting an older commit causes content conflicts when subsequent commits modified the same lines, tree conflicts if files were moved or deleted, and silent semantic conflicts where dependent code breaks at compile-time. Resolve them by manually reconciling diffs, running full compilation and unit tests, and finalizing with git revert --continue.",
        "best_answer": (
            "When executing `git revert` on an older commit, Git applies an inverse patch against current HEAD. This produces three distinct conflict categories:\n\n"
            "1. **Content Conflicts (Direct Textual Invalidation)**:\n"
            "   - Occurs when intermediate commits modified, refactored, or formatted the exact lines that the inverse patch attempts to delete or restore. Git halts with standard conflict markers (`<<<<<<< HEAD` vs `>>>>>>> parent of...`).\n\n"
            "2. **Tree / Rename Conflicts**:\n"
            "   - Arise when files created or modified by the old commit were subsequently renamed, moved to new packages during architectural modularization, or deleted entirely.\n\n"
            "3. **Silent Semantic / Compilation Conflicts**:\n"
            "   - The most insidious category: the inverse patch applies cleanly with zero textual conflicts, but subsequent commits introduced dependencies on classes, fields, or database schemas defined in the reverted commit. The codebase breaks during Kotlin compilation or triggers runtime exceptions.\n\n"
            "Resolving an old revert mandates manually clearing conflict markers, followed by running `./gradlew compileDebugKotlin` and unit tests to verify semantic integrity before executing `git revert --continue`."
        ),
        "deep_answer": (
            "In large scale engineering teams, managing complex historical reverts requires operational discipline:\n\n"
            "1. **The Revert Blast Radius Assessment**: Never blindly revert a 2-month-old commit in a production repo. Use `git log -S \"SymbolName\"` to identify every commit that touched or referenced the affected symbol since the target commit. If 15 subsequent features depend on it, an inverse patch will cause cascading fractures.\n\n"
            "2. **Surgical Forward-Fix vs. Revert**: If an old commit introduced a bug but has deep architectural entanglement with current production code, executing `git revert` is often more dangerous than writing a targeted forward hotfix that neutralizes the buggy code path while preserving the surrounding public API contracts.\n\n"
            "3. **Reverting a Long Chain**: If a feature comprised multiple commits, use range revert: `git revert OLDER_COMMIT..NEWER_COMMIT`. Git reverts them in reverse chronological order, minimizing intermediate dependency conflicts."
        ),
        "follow_ups": [
            {
                "question": "What is a semantic Git conflict and why is it dangerous in reverts?",
                "answer": "A conflict where code merges cleanly without textual errors, but breaks at compile or runtime because remaining code depended on symbols removed by the revert."
            },
            {
                "question": "In what order does Git revert a range of commits (`git revert A..B`)?",
                "answer": "It reverts in reverse chronological order (from B backward to A) to cleanly unwind dependencies."
            }
        ]
    },
    {
        "id": "CIC-16",
        "arabic_explanation": (
            "كيف تدير البيئات المتعددة (Environments) والنكهات (Product Flavors) في أندرويد بشكل احترافي؟\n\n"
            "1. مفهوم أبعاد النكهات (Flavor Dimensions) وأنواع البناء (Build Types):\n"
            "   - **Build Types**: تحدد خصائص البناء (مثل `debug` للبرمجة مع تمكين التصحيح، و `release` للمستخدمين مع تمكين R8 والتوقيع).\n   - **Product Flavors**: تحدد إصدارات المنتج المختلفة (مثل بيئات السيرفر: `dev`, `staging`, `prod` أو طريقة التوزيع: `playStore`, `fdroid`).\n   - **Build Variant = Flavor + Build Type** (مثلاً: `devDebug`, `prodRelease`).\n\n"
            "2. أفضل الممارسات الهندسية لإدارة البيئات:\n"
            "   - **لاحقة معرف التطبيق (`applicationIdSuffix`)**: إضافة `.dev` و `.staging` لتوليد حزم فريدة، مما يتيح للمطورين وفريق الـ QA **تثبيت نسختي الـ Dev والـ Prod معاً على نفس الهاتف جنباً إلى جنب** دون أن تحذف إحداهما الأخرى.\n   - **عزل الموارد وملفات الإعدادات عبر مجلدات المصادر (Source Sets)**:\n     * وضع `google-services.json` الخاص بـ Firebase Dev في `app/src/dev/`، وملف Prod في `app/src/prod/`.\n   - **حقن الإعدادات في `BuildConfig` أو `resValue`**: تمرير عناوين الـ Base URL ومفاتيح البيئة عبر Gradle دون كتابتها داخل كود التطبيق مباشرة.\n   - **عزل المكتبات حسب البيئة**: استخدام `debugImplementation` لأدوات مثل Chucker و LeakCanary مع `releaseImplementation` لمكتبات الـ no-op المقابلة لمنع تسريب أدوات التصحيح للإنتاج."
        ),
        "practical_walkthrough": (
            "إعداد Gradle احترافي يدعم بيئات Dev و Staging و Prod بالتفصيل:\n"
            "```kotlin\n"
            "// app/build.gradle.kts\n"
            "android {\n"
            "    flavorDimensions += listOf(\"environment\")\n"
            "\n"
            "    productFlavors {\n"
            "        create(\"dev\") {\n"
            "            dimension = \"environment\"\n"
            "            applicationIdSuffix = \".dev\"\n"
            "            versionNameSuffix = \"-dev\"\n"
            "            buildConfigField(\"String\", \"BASE_URL\", \"\\\"https://api-dev.company.com/\\\"\")\n"
            "            resValue(\"string\", \"app_name\", \"App (DEV)\")\n"
            "        }\n"
            "        create(\"staging\") {\n"
            "            dimension = \"environment\"\n"
            "            applicationIdSuffix = \".staging\"\n"
            "            versionNameSuffix = \"-staging\"\n"
            "            buildConfigField(\"String\", \"BASE_URL\", \"\\\"https://api-staging.company.com/\\\"\")\n"
            "            resValue(\"string\", \"app_name\", \"App (STG)\")\n"
            "        }\n"
            "        create(\"prod\") {\n"
            "            dimension = \"environment\"\n"
            "            buildConfigField(\"String\", \"BASE_URL\", \"\\\"https://api.company.com/\\\"\")\n"
            "            resValue(\"string\", \"app_name\", \"App\")\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "dependencies {\n"
            "    // تفعيل فاحص الشبكة Chucker فقط في بيئات التطوير والتصحيح:\n"
            "    debugImplementation(\"com.github.chuckerteam.chucker:library:4.0.0\")\n"
            "    releaseImplementation(\"com.github.chuckerteam.chucker:library-no-op:4.0.0\")\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Manage environments using Gradle flavorDimensions and productFlavors combined with buildTypes. Use applicationIdSuffix to allow side-by-side installations on the same device, isolate environment-specific backend URLs via BuildConfig fields, manage distinct Google Services configs using flavor-specific source sets, and inject debug tooling using variant-aware dependencies.",
        "best_answer": (
            "Managing multiple environments in modern Android applications relies on structured Gradle architecture:\n\n"
            "1. **Flavor Dimensions and Build Variants**:\n"
            "   - Define dimensions (e.g. `environment`: `dev`, `staging`, `prod`). Gradle multiplies flavors by build types (`debug`, `release`) to produce concrete build variants like `devDebug` and `prodRelease`.\n\n"
            "2. **Side-by-Side Coexistence (`applicationIdSuffix`)**:\n"
            "   - Assign `applicationIdSuffix = \".dev\"` and `applicationIdSuffix = \".staging\"`. This allows developers and QA to install production, staging, and development builds concurrently on a single physical device without overwriting app sandboxes.\n\n"
            "3. **Configuration Injection via BuildConfig and ResValue**:\n"
            "   - Expose backend endpoints, feature toggles, and app display names dynamically via `buildConfigField` and `resValue(\"string\", \"app_name\", ...)`, keeping source code agnostic of underlying environment URLs.\n\n"
            "4. **Source Sets & Third-Party Isolation**:\n"
            "   - Use directory-based source sets (`src/dev/`, `src/prod/`) to supply distinct configuration assets (e.g. separate Firebase `google-services.json` files for dev and prod GCP projects), and isolate profiling tools using `debugImplementation` vs `releaseImplementation` no-op stubs."
        ),
        "deep_answer": (
            "From an architectural modularity and build performance perspective, multi-flavor setups require governance:\n\n"
            "1. **Combinatorial Explosion Hazard**: Having 3 flavor dimensions with 3 flavors each creates $3 \\times 3 \\times 2 = 18$ build variants. This drastically degrades Gradle configuration times, IDE indexing, and CI matrix execution. Keep flavor dimensions minimal (ideally a single dimension for environment), and handle sub-variations via runtime feature flags or build properties.\n\n"
            "2. **Multi-Module Flavor Propagation**: In an 80-module app, declaring flavors in every library module creates tight coupling and configuration failures (`missingDimensionStrategy`). Follow modern Android architecture guidelines: keep library modules flavor-agnostic, and declare flavors exclusively in the top-level `:app` application module.\n\n"
            "3. **Secrets Isolation in CI**: The release pipeline for `prodRelease` must never execute with `dev` keys, nor should `dev` builds touch production databases or Stripe credentials. CI pipelines must validate and restrict secret injection based on the specific variant being compiled."
        ),
        "follow_ups": [
            {
                "question": "Why should library modules avoid declaring product flavors in multi-module apps?",
                "answer": "To prevent combinatorial variant explosion and complex variant-matching configuration issues; flavors should be declared primarily in the root application module."
            },
            {
                "question": "How does `applicationIdSuffix` enable side-by-side app installations on Android?",
                "answer": "It modifies the unique Android OS package identifier, allowing the PackageManager to treat dev and prod builds as completely independent apps."
            }
        ]
    },
    {
        "id": "CIC-17",
        "arabic_explanation": (
            "حدث كراش حرج في الإنتاج بينما فرع التطوير الرئيسي (`main`) ابتعد وتضمن ميزات جديدة غير جاهزة للإطلاق. ما هي استراتيجيتك الدقيقة في Git والـ CI؟\n\n"
            "1. توصيف المأزق الهندسي:\n"
            "   - التطبيق الحي في المتجر هو الإصدار `v2.4.0`.\n   - فرع `main` يحتوي على 40 كوميت لميزات جديدة للإصدار `v2.5.0` ما زالت قيد التطوير والاختبار، وبالتالي **يستحيل تجميع أو إطلاق `main` للإنتاج فوراً**.\n\n"
            "2. استراتيجية الإصلاح العاجل (Hotfix Branching Strategy):\n"
            "   - **1. التفريع من تاج الإنتاج (Branch from Tag)**: إنشاء فرع جديد مشتق مباشرة من التاج الدقيق للإصدار الإنتاجي: `git checkout -b hotfix/2.4.1 v2.4.0`.\n   - **2. الإصلاح الجراحي (Surgical Fix)**: كتابة أقل قدر ممكن من الكود لحل العطل الحرج فقط، مع كتابة Unit Test يثبت المشكلة ويتحقق من حلها.\n   - **3. بناء واختبار وتوزيع الـ Hotfix**: رفع الـ Hotfix وتجميع نسخة `v2.4.1` مع زيادة الـ `versionCode`، وتوزيعها لمسار الإنتاج مع Staged Rollout.\n   - **4. وسم الإصدار (Tagging)**: عمل Tag جديد على الكوميت: `git tag v2.4.1`.\n   - **5. إعادة الدمج في الفرع الرئيسي (Backporting)**: دمج أو انتقاء (`cherry-pick`) كوميت الإصلاح إلى فرع `main` فوراً؛ لضمان عدم عودة الكراش للظهور عند إطلاق التحديث الكبير القادم `v2.5.0`."
        ),
        "practical_walkthrough": (
            "تسلسل أوامر Git خطوة بخطوة للتعامل مع الـ Hotfix وإعادة الدمج:\n"
            "```bash\n"
            "# 1. إنشاء فرع الـ hotfix انطلاقاً من Tag النسخة الحالية في الإنتاج:\n"
            "git fetch --tags\n"
            "git checkout -b hotfix/2.4.1 tags/v2.4.0\n"
            "\n"
            "# 2. كتابة كود الإصلاح الجراحي واختبارات الوحدة:\n"
            "# ... تعديل الكود واختباره محلياً ...\n"
            "git commit -am \"fix(checkout): resolve NPE during 3DS biometric challenge (#451)\"\n"
            "\n"
            "# 3. تجميع واختبار الـ release bundle ورفعه للإنتاج عبر CI:\n"
            "git push origin hotfix/2.4.1\n"
            "# بعد اكتمال النشر والتأكد من استقرار الإصدار:\n"
            "git tag -a v2.4.1 -m \"Release hotfix 2.4.1\"\n"
            "git push origin v2.4.1\n"
            "\n"
            "# 4. نقل الإصلاح إلى فرع التطوير الرئيسي (Backporting):\n"
            "git checkout main\n"
            "git pull origin main\n"
            "git cherry-pick tags/v2.4.1^{commit} -x\n"
            "git push origin main\n"
            "# النتيجة: تم حل مشكلة الإنتاج دون سحب أي كود غير جاهز، وتم تأمين الفرع الرئيسي.\n"
            "```"
        ),
        "quick_answer": "Branch immediately from the production release tag (e.g., git checkout -b hotfix/2.4.1 v2.4.0). Apply a surgical fix with a regression test, increment versionCode, build and deploy v2.4.1 to production. Once verified, tag the hotfix and backport the commit to main via git cherry-pick -x or merge to prevent bug regression in future releases.",
        "best_answer": (
            "Executing a production hotfix when the mainline has diverged requires a strict, audited protocol:\n\n"
            "1. **Isolate the Baseline via Release Tag**:\n"
            "   - Check out a dedicated hotfix branch directly from the production release Git tag (`git checkout -b hotfix/2.4.1 tags/v2.4.0`). Never attempt to hotfix directly from `main` or develop, as unverified features will leak into production.\n\n"
            "2. **Surgical Implementation & Regression Testing**:\n"
            "   - Write the minimal atomic fix necessary to resolve the crash. Accompany it with a failing unit test that reproduces the incident to confirm the fix.\n\n"
            "3. **Version Bump & Production Deployment**:\n"
            "   - Increment `versionCode` and update `versionName` to `\"2.4.1\"`. Trigger the CI pipeline to compile, sign, and upload the hotfix AAB to Google Play production via staged rollout.\n\n"
            "4. **Audit Tagging & Backporting to Mainline**:\n"
            "   - Tag the release commit (`git tag -a v2.4.1`).\n   - Backport the hotfix commit into `main` using `git cherry-pick -x` or by merging the hotfix branch into `main`. The `-x` flag records the original commit hash, guaranteeing that the fix survives into subsequent major releases."
        ),
        "deep_answer": (
            "From an operational and incident management perspective, hotfixes carry hidden risks:\n\n"
            "1. **The 'Forgot to Backport' Trap**: The most frequent failure in hotfix workflows is deploying the hotfix, celebrating the fix, and forgetting to merge it back into `main`. Three weeks later, `v2.5.0` ships and re-introduces the identical crash, causing severe reputational damage. Enforce automated CI bots or branch policies that require a PR merging the hotfix branch back into `main` before closing the incident.\n\n"
            "2. **Database Migration Clashes**: If the hotfix touches Room or SQLite database schemas, handle versioning cautiously. If `v2.4.0` was on db version 4, the hotfix `v2.4.1` might introduce db version 5. If `main` already introduced a different migration for db version 5, a merge collision occurs that can corrupt user databases upon future updates. Backport migrations must reconcile schema version numbers carefully.\n\n"
            "3. **Expedited Store Review**: Alert Google Play Developer Support or use expedited review requests in Play Console if the hotfix addresses a catastrophic revenue or data-loss incident."
        ),
        "follow_ups": [
            {
                "question": "Why is branching from the production release tag safer than fixing on `main`?",
                "answer": "Because `main` contains incomplete, unverified feature code; branching from the tag guarantees binary parity with production, containing only the surgical fix."
            },
            {
                "question": "What is the danger of not backporting a hotfix into the mainline development branch?",
                "answer": "The bug will resurface in the next scheduled feature release, causing a regression."
            }
        ]
    },
    {
        "id": "CIC-18",
        "arabic_explanation": (
            "فتح شخص غريب أو مساهم خارجي Pull Request خبيث يحاول الوصول لمفاتيح التوقيع والأسرار. كيف تحمي الـ CI/CD من التسريب؟\n\n"
            "1. سيناريو الهجوم (Supply Chain / CI Attack Vector):\n"
            "   - يقوم المهاجم بعمل Fork للمستودع، ويعدل ملفات مثل `build.gradle.kts` أو ملفات الاختبار أو workflows الـ CI ليكتب كوداً يقرأ متغيرات البيئة:\n     `println(System.getenv(\"KEYSTORE_PASSWORD\"))` أو يقوم بإرسالها لسيرفر خارجي عبر `curl`.\n   - ثم يفتح Pull Request للمستودع الأصلي، على أمل أن يشغل سيرفر الـ CI الكود ويطبع أو يسرب الأسرار.\n\n"
            "2. إجراءات الحماية الدفاعية المتكاملة:\n"
            "   - **1. عزل أسرار الـ Forks افتراضياً**: في منصات مثل GitHub Actions، تكون أسرار المستودع **محجوبة تماماً وغير متاحة** في الـ workflows التي يتم تشغيلها بواسطة حدث `pull_request` القادم من Forks.\n   - **2. تجنب الثغرة القاتلة `pull_request_target`**: حدث `pull_request_target` يملك صلاحيات وصول للأسرار ولكنه يعمل في سياق الفرع المستهدف. **يُحظر تماماً** عمل checkout لكود الـ PR مع استخدام `pull_request_target` لأنه يمنح كود المهاجم وصولاً فورياً للأسرار (Pwn Request).\n   - **3. اشتراط الموافقة البشرية (Approval Required)**: ضبط إعدادات الـ CI لتطلب موافقة يدوية من أحد مسؤولي المشروع لتشغيل الـ CI لأي مساهم لأول مرة (First-time contributors).\n   - **4. حماية البيئات (Environment Protection Rules)**: حصر أسرار الإنتاج في بيئة محمية (مثل `production-release`) تتطلب موافقة كتابية قبل بدء أي وظيفة تستخدمها."
        ),
        "practical_walkthrough": (
            "إعدادات أمان صارمة في ملفات الـ CI والـ GitHub Actions:\n"
            "```yaml\n"
            "# 1. فحص الـ PRs القادمة من الـ Forks بدون أي وصول للأسرار الحساسة:\n"
            "name: PR Untrusted Check\n"
            "on: pull_request # هذا الحدث آمن افتراضياً: لا يملك وصولاً لأسرار المستودع\n"
            "\n"
            "jobs:\n"
            "  build_and_test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-java@v4\n"
            "        with: { distribution: 'temurin', java-version: '17' }\n"
            "      # تشغيل مهام التجميع والاختبار للنسخة الـ Debug فقط (لا تحتاج لمفاتيح الإنتاج):\n"
            "      - run: ./gradlew testDebugUnitTest assembleDebug\n"
            "\n"
            "# 2. في وظيفة النشر الحقيقية: نربطها ببيئة إنتاجية محمية تتطلب مراجعين معتمدين:\n"
            "  publish_release:\n"
            "    if: github.event_name == 'push' && github.ref == 'refs/heads/main'\n"
            "    environment: production-protected # يتطلب موافقة يدوية في GitHub Settings\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: ./gradlew bundleRelease\n"
            "        env:\n"
            "          KEYSTORE_PASSWORD: ${{ secrets.PROD_KEYSTORE_PASSWORD }}\n"
            "```"
        ),
        "quick_answer": "Prevent secret leakage by relying on CI security boundaries where PRs from forks have zero access to repository secrets by default. Avoid the vulnerable pull_request_target checkout pattern, mandate human maintainer approval for first-time contributors before workflows run, and isolate signing secrets into protected environments with strict branch restrictions.",
        "best_answer": (
            "Defending Android CI pipelines against malicious pull requests targeting signing secrets requires multi-layered controls:\n\n"
            "1. **Default Fork Secret Isolation**:\n"
            "   - Modern CI platforms (such as GitHub Actions) strictly withhold repository secrets from workflow runs triggered by `pull_request` events originating from forked repositories. The runner operates in a zero-secret sandbox.\n\n"
            "2. **Eliminate the `pull_request_target` Pwn Vulnerability**:\n"
            "   - Never use `pull_request_target` combined with checking out the pull request's untrusted HEAD commit. This dangerous pattern grants untrusted code access to write permissions and repository secrets, allowing attackers to exfiltrate keys via build scripts.\n\n"
            "3. **First-Time Contributor Execution Gates**:\n"
            "   - Configure repository security policies to require maintainer review and manual approval before any workflow runs for first-time contributors, preventing malicious crypto-miners or credential-stealing scripts from executing automatically.\n\n"
            "4. **Environment Isolation & Branch Protection**:\n"
            "   - Bind production signing secrets to a protected 'Production' Environment in GitHub/GitLab. Restrict this environment exclusively to the protected `main` branch with mandatory code reviews, ensuring PRs cannot reference release secrets."
        ),
        "deep_answer": (
            "From a supply-chain security and build provenance perspective, defense-in-depth extends into Gradle and dependencies:\n\n"
            "1. **Gradle Build Cache & Dependency Poisoning**: A malicious PR could modify dependency resolution repositories in `settings.gradle.kts` to point to an attacker-controlled Maven server serving poisoned binaries, or poison the shared remote build cache. Ensure PR builds have read-only build cache permissions and restrict dependency repositories to verified HTTPS hosts.\n\n"
            "2. **Dynamic Log Redaction & Audit**: Even within trusted teams, mistakes happen. CI systems employ automated output scanners that mask detected high-entropy strings and recognized private key formats (`-----BEGIN PRIVATE KEY-----`). Any attempt to print masked variables results in `***` in the public build logs.\n\n"
            "3. **Audit CI Network Egress**: In enterprise self-hosted runner infrastructure, configure firewall egress rules to restrict CI outbound network traffic exclusively to authorized endpoints (Maven Central, Google Maven, Google Play API, GitHub), blocking unauthorized outbound sockets to arbitrary external IP addresses."
        ),
        "follow_ups": [
            {
                "question": "Why does GitHub Actions withhold secrets from `pull_request` events originating from forks?",
                "answer": "To prevent unauthorized external contributors from modifying code or workflows to print or exfiltrate private repository secrets."
            },
            {
                "question": "What is the correct way to use `pull_request_target` safely if it is needed?",
                "answer": "Use it only for labeling or triage actions without checking out or running the untrusted PR code."
            }
        ]
    },
    {
        "id": "CIC-19",
        "arabic_explanation": (
            "نشر خط أنابيب الـ CI/CD نكهة خاطئة (مثل نشر نسخة الـ Staging أو الـ Dev إلى مسار الإنتاج في المتجر). كيف تمنع تكرار هذه الكارثة نهائياً؟\n\n"
            "1. تحليل السبب الجذري (Root Cause Analysis - RCA):\n"
            "   - **1. غموض في أسماء المهام (Ambiguous Tasks)**: تشغيل أمر عام مثل `./gradlew bundleRelease` في مشروع يحتوي على نكهات، مما يجعل Gradle يبني نكهة عشوائية أو أول نكهة معرفة أبجدياً.\n   - **2. استخدام مسارات عامة (Wildcard Artifacts)**: كتابة مسار مثل `app/build/outputs/bundle/*/*.aab` في أداة الرفع، فتقوم برفع أول ملف تجده في المجلد.\n   - **3. أخطاء في تكوين الـ CI**: عدم مطابقة فرع البناء مع متغيرات البيئة الصحيحة.\n\n"
            "2. آليات المنع والحماية الهندسية الصارمة:\n"
            "   - **1. أسماء مهام صريحة ومحددة بالكامل**: استخدام `./gradlew bundleProdRelease` دائماً بدلاً من المهام العامة.\n   - **2. فحص ما قبل النشر (Pre-Flight Verification Gate)**: كتابة مهمة فحص في الـ CI تقوم بفك حزمة الـ AAB وفحص الـ Manifest للتأكد قطيعاً من أن `package_name` يطابق تطبيق الإنتاج الرسمي وليس `.dev` أو `.staging`.\n   - **3. التحقق من `BuildConfig` وثوابت البيئة**: فحص أن `BuildConfig.BUILD_TYPE == \"release\"` و `BuildConfig.FLAVOR == \"prod\"`.\n   - **4. مسار ملفات حصري بدون Wildcards**: تحديد مسار الـ AAB الدقيق: `app/build/outputs/bundle/prodRelease/app-prod-release.aab` وإفشال البناء فوراً إذا لم يكن الملف في هذا المسار الدقيق."
        ),
        "practical_walkthrough": (
            "إعداد مهمة فحص برمجية في Gradle أو CI للتحقق من هوية الـ AAB قبل رفعه لـ Google Play:\n"
            "```bash\n"
            "# خطوة فحص صارمة في GitHub Actions قبل النشر:\n"
            "- name: Verify Production Artifact Integrity\n"
            "  run: |\n"
            "    AAB_PATH=\"app/build/outputs/bundle/prodRelease/app-prod-release.aab\"\n"
            "    \n"
            "    # 1. التأكد من وجود الملف في المسار الدقيق الخاص بنكهة الإنتاج:\n"
            "    if [ ! -f \"$AAB_PATH\" ]; then\n"
            "      echo \"CRITICAL ERROR: Production AAB not found at expected path!\" && exit 1\n"
            "    fi\n"
            "    \n"
            "    # 2. فحص الـ Package Name داخل الـ Manifest باستخدام bundletool لمنع نكهات dev أو staging:\n"
            "    PACKAGE_NAME=$(bundletool dump manifest --bundle=\"$AAB_PATH\" | grep 'package=' | head -n 1)\n"
            "    echo \"Inspected Package: $PACKAGE_NAME\"\n"
            "    \n"
            "    if [[ \"$PACKAGE_NAME\" == *\".dev\"* ]] || [[ \"$PACKAGE_NAME\" == *\".staging\"* ]]; then\n"
            "      echo \"FATAL: Staging or Dev flavor detected in release artifact! Aborting deployment!\"\n"
            "      exit 1\n"
            "    fi\n"
            "    \n"
            "    echo \"SUCCESS: Verified genuine production artifact. Proceeding to Play Store deployment.\"\n"
            "```"
        ),
        "quick_answer": "Prevent wrong flavor deployments by eliminating wildcard artifact paths, invoking fully qualified Gradle tasks (bundleProdRelease), implementing an automated pre-flight verification step using bundletool to assert the production package ID, and isolating deployment workflows into protected branch-restricted pipelines.",
        "best_answer": (
            "Preventing accidental flavor misdeployment requires eliminating ambiguity across build scripts, artifacts, and CI gates:\n\n"
            "1. **Explicit Fully-Qualified Gradle Invocations**:\n"
            "   - Ban generic tasks like `./gradlew bundle` or `./gradlew assembleRelease` in release workflows. Always invoke explicit variant tasks such as `./gradlew bundleProdRelease`.\n\n"
            "2. **Eliminate Wildcard Artifact Patterns**:\n"
            "   - Remove patterns like `build/outputs/bundle/*/*.aab` in deployment steps. Hardcode the exact deterministic artifact path: `app/build/outputs/bundle/prodRelease/app-prod-release.aab`, failing the build immediately if the expected path is missing.\n\n"
            "3. **Pre-Flight Manifest & Bytecode Inspection**:\n"
            "   - Implement an automated pre-deployment verification step. Use Google's `bundletool` CLI to inspect the generated AAB manifest, asserting that the package name matches `com.company.app` and does not contain `.dev` or `.staging` suffixes, and verifying that the signing certificate matches the production upload fingerprint.\n\n"
            "4. **Branch & Environment Decoupling**:\n"
            "   - Decouple CI pipelines: staging deployment workflows only trigger on the `develop` branch with staging credentials, while production deployment workflows trigger solely on protected release tags with production credentials."
        ),
        "deep_answer": (
            "From an operational reliability and post-mortem perspective, defense against misconfiguration involves structural guarantees:\n\n"
            "1. **Automated Smoke Testing via Internal Track**: Even with manifest verification, mandate that the deployed AAB lands on the Google Play Internal Testing track first. An automated smoke test on Firebase Test Lab or an internal canary group tests that the app connects to production endpoints and returns 200 OK before the release is promoted to general production.\n\n"
            "2. **Compile-Time Safety via Gradle Variant Filters**: If a specific flavor/buildType combination should never exist (e.g. `devRelease` or `prodDebug`), eliminate it entirely using `androidComponents.beforeVariants`: disable invalid variants so running an incorrect task fails instantly with 'Task not found'.\n\n"
            "3. **Audit Trail and Telemetry**: Log the build SHA, release variant name, and signer fingerprint into the CI summary dashboard, guaranteeing transparency and immediate detection if unexpected parameters were supplied."
        ),
        "follow_ups": [
            {
                "question": "How can you disable invalid variant combinations like `prodDebug` in Gradle?",
                "answer": "Using `androidComponents.beforeVariants`, filter variants matching flavor 'prod' and buildType 'debug' and call `enabled = false`."
            },
            {
                "question": "Why is using wildcard paths like `bundle/*/*.aab` dangerous in CI deployment steps?",
                "answer": "If an earlier task built a dev or staging AAB, the wildcard may pick and deploy the wrong file to production."
            }
        ]
    },
    {
        "id": "CIC-20",
        "arabic_explanation": (
            "خط أنابيب الـ CI يستغرق 40 دقيقة كاملة، مما يعطل الفريق ويهدر الوقت. كيف تقوم بعمل فحص دقيق (Profile) وترتيب أولويات التحسين لتقليل هذا الوقت جذرياً؟\n\n"
            "1. خطة الفحص والتشخيص الهندسي (Profiling Strategy):\n"
            "   - لا تبدأ بالتحسين العشوائي! استخدم أدوات القياس أولاً:\n   - **Gradle Build Scan (`--scan`)**: الأداة الذهبية؛ توضح بدقة بالمللي ثانية أين ضاع الوقت: في مرحلة الـ Configuration، أم في تنزيل الـ Dependencies، أم في مهام Kotlin Compilation، أم في R8، أم في الـ Tests.\n   - **Gradle Profiler**: أداة قياس دقيقة لمقارنة أداء المهام محلياً عبر جولات متعددة.\n   - **تقارير الـ CI Runner Timing**: معرفة الوقت المستغرق في إعداد بيئة الـ VM وتشغيل المحاكيات وتنزيل الكاش.\n\n"
            "2. مصفوفة أولويات التحسين (Prioritization Matrix):\n"
            "   - **الأولوية 1 (High Impact, Low Effort)**:\n     * تفعيل كاش الـ Dependencies والـ Gradle Wrapper (`gradle/actions/setup-gradle`).\n     * تفعيل `org.gradle.parallel=true` و `org.gradle.caching=true` في `gradle.properties`.\n     * تخصيص ذاكرة كافية لـ JVM (`-Xmx6g -XX:+UseParallelGC`).\n   - **الأولوية 2 (High Impact, Medium Effort)**:\n     * **تقسيم الـ Pipeline إلى Jobs متوازية**: تشغيل Lint والتحليل الساكن واختبارات الوحدة بالتوازي على Runners مستقلين بدلاً من تشغيلها بتسلسل بطيء.\n     * **تفعيل الـ Remote Build Cache**: مشاركة مخرجات التجميع عبر السيرفر لتخطي المهام التي لم تتغير مدخلاتها (`FROM-CACHE`).\n   - **الأولوية 3 (High Impact, High Effort)**:\n     * **فحص الموديولات المتأثرة فقط (Affected Module Detection)**: تشغيل الاختبارات للموديولات المتغيرة في الـ PR فقط.\n     * **فصل اختبارات الـ UI والأجهزة**: نقل اختبارات المحاكي الثقيلة من فحص الـ PRs العاجلة إلى مسار ليلي مجدول (Nightly Pipeline) أو تشغيلها عبر مزارع سحابية متوازية (Firebase Test Lab)."
        ),
        "practical_walkthrough": (
            "خطة عملية بالأوامر والتكوينات لتقليص وقت الـ CI من 40 دقيقة إلى أقل من 8 دقائق:\n"
            "```properties\n"
            "# 1. في gradle.properties لتفعيل الأداء الأقصى:\n"
            "org.gradle.jvmargs=-Xmx6144m -XX:+UseParallelGC\n"
            "org.gradle.parallel=true\n"
            "org.gradle.caching=true\n"
            "org.gradle.configuration-cache=true\n"
            "```\n"
            "```yaml\n"
            "# 2. تحويل خط الأنابيب من التسلسلي (Sequential) إلى المتوازي (Parallel) في GitHub Actions:\n"
            "jobs:\n"
            "  lint_and_static:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "      - run: ./gradlew detekt spotlessCheck lintDebug\n"
            "\n"
            "  unit_tests:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: gradle/actions/setup-gradle@v3\n"
            "      - run: ./gradlew testDebugUnitTest\n"
            "\n"
            "  # كلتا المهمتين تعملان بالتوازي، فينخفض وقت الانتظار من (15 + 20 = 35 دقيقة) إلى 10 دقائق فقط!\n"
            "```"
        ),
        "quick_answer": "Profile the 40-minute pipeline using Gradle Build Scans (--scan) to pinpoint exact bottlenecks across configuration, compilation, and testing. Prioritize optimizations: first, enable dependency caching, parallel execution, and configuration cache; second, split sequential monolithic jobs into parallel CI runners; third, implement a remote build cache and affected module detection.",
        "best_answer": (
            "Systematically reducing a 40-minute Android CI pipeline to under 10 minutes requires empirical profiling and tiered intervention:\n\n"
            "1. **Empirical Bottleneck Profiling**:\n"
            "   - Generate a Gradle Build Scan (`./gradlew assembleDebug --scan`). Inspect the timeline to isolate where time is wasted: configuration overhead, network dependency downloading, Kotlin compilation, annotation processing, or testing.\n\n"
            "2. **Tier 1: Immediate Execution Wins (Low Effort, High Impact)**:\n"
            "   - Cache `~/.gradle/caches` and wrapper using `gradle/actions/setup-gradle`.\n   - Enable `org.gradle.parallel=true`, `org.gradle.caching=true`, and `org.gradle.configuration-cache=true`.\n   - Allocate proper runner memory: `-Xmx6g -XX:+UseParallelGC` to eliminate GC thrashing.\n\n"
            "3. **Tier 2: Pipeline Parallelization (Medium Effort)**:\n"
            "   - Break monolithic single-job pipelines into parallel matrix jobs: (a) static analysis and formatting, (b) local JVM unit tests, and (c) debug assembly. Running these concurrently on multiple runners cuts wall-clock time dramatically.\n\n"
            "4. **Tier 3: Remote Caching & Affected Module Detection (High Impact)**:\n"
            "   - Deploy a shared Remote Build Cache (Develocity or HTTP cache). Tasks that produce identical bytecode are resolved instantly with `FROM-CACHE`.\n   - Enforce Affected Module Detection to execute tests only for modules impacted by the PR's git diff."
        ),
        "deep_answer": (
            "From an engineering leadership and platform infrastructure perspective, deep optimizations require architectural shifts:\n\n"
            "1. **Decouple Emulators from PR Gates**: Running full Android emulator suites on slow GitHub Actions virtual machines often consumes 25+ minutes of the 40-minute pipeline. Senior teams run only fast local JVM unit tests and Robolectric on PR gates, and offload instrumented UI tests to sharded cloud device farms (Firebase Test Lab / Flank / Marathon) scheduled on merge trains or nightly builds.\n\n"
            "2. **Eliminate Non-Cacheable Task Bottlenecks**: Audit tasks that constantly miss cache due to bad inputs. Common culprits include custom tasks embedding timestamps, git commit hashes, or absolute paths into compiled files, which invalidate the Gradle cache key for all downstream tasks.\n\n"
            "3. **KAPT to KSP Migration**: If the build scan reveals excessive annotation processing duration, migrating Room, Moshi, and Dagger/Hilt to Kotlin Symbol Processing (KSP) cuts code-generation and stub-generation overhead by up to 50% across large modular codebases."
        ),
        "follow_ups": [
            {
                "question": "What tool provides the most granular visibility into Gradle CI task execution durations?",
                "answer": "Gradle Build Scans (`--scan`), which output an interactive timeline detailing task execution, cache hits, and dependencies."
            },
            {
                "question": "Why does decomposing a single CI pipeline into parallel jobs drastically reduce wall-clock time?",
                "answer": "Because independent tasks (like static analysis and unit testing) run concurrently on separate cloud VM cores instead of waiting for each other in series."
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
    for item in CIC_15_20:
        existing_dict[item["id"]] = item

    all_items = list(existing_dict.values())
    all_items.sort(key=lambda x: x["id"])

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Updated {DATA_FILE} with questions CIC-15 to CIC-20. Total questions: {len(all_items)}")


if __name__ == "__main__":
    main()
