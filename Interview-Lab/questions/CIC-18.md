---
id: "CIC-18"
question: "A malicious pull request tries to access signing secrets. How do you prevent leakage?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "C"
phase: 4
priority: "P2"
order: 437
editorial_status: "reviewed"
---

# CIC-18

## Original interview question

A malicious pull request tries to access signing secrets. How do you prevent leakage?

## What the interviewer evaluates

- Malicious PR code in build scripts/tests and privileged workflow contexts.
- Separation of untrusted validation from signing/release.

## Explanation in Arabic

فتح شخص غريب أو مساهم خارجي Pull Request خبيث يحاول الوصول لمفاتيح التوقيع والأسرار. كيف تحمي الـ CI/CD من التسريب؟

1. سيناريو الهجوم (Supply Chain / CI Attack Vector):
   - يقوم المهاجم بعمل Fork للمستودع، ويعدل ملفات مثل `build.gradle.kts` أو ملفات الاختبار أو workflows الـ CI ليكتب كوداً يقرأ متغيرات البيئة:
     `println(System.getenv("KEYSTORE_PASSWORD"))` أو يقوم بإرسالها لسيرفر خارجي عبر `curl`.
   - ثم يفتح Pull Request للمستودع الأصلي، على أمل أن يشغل سيرفر الـ CI الكود ويطبع أو يسرب الأسرار.

2. إجراءات الحماية الدفاعية المتكاملة:
   - **1. عزل أسرار الـ Forks افتراضياً**: في منصات مثل GitHub Actions، تكون أسرار المستودع **محجوبة تماماً وغير متاحة** في الـ workflows التي يتم تشغيلها بواسطة حدث `pull_request` القادم من Forks.
   - **2. تجنب الثغرة القاتلة `pull_request_target`**: حدث `pull_request_target` يملك صلاحيات وصول للأسرار ولكنه يعمل في سياق الفرع المستهدف. **يُحظر تماماً** عمل checkout لكود الـ PR مع استخدام `pull_request_target` لأنه يمنح كود المهاجم وصولاً فورياً للأسرار (Pwn Request).
   - **3. اشتراط الموافقة البشرية (Approval Required)**: ضبط إعدادات الـ CI لتطلب موافقة يدوية من أحد مسؤولي المشروع لتشغيل الـ CI لأي مساهم لأول مرة (First-time contributors).
   - **4. حماية البيئات (Environment Protection Rules)**: حصر أسرار الإنتاج في بيئة محمية (مثل `production-release`) تتطلب موافقة كتابية قبل بدء أي وظيفة تستخدمها.

## Practical walkthrough

إعدادات أمان صارمة في ملفات الـ CI والـ GitHub Actions:
```yaml
# 1. فحص الـ PRs القادمة من الـ Forks بدون أي وصول للأسرار الحساسة:
name: PR Untrusted Check
on: pull_request # هذا الحدث آمن افتراضياً: لا يملك وصولاً لأسرار المستودع

jobs:
  build_and_test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      # تشغيل مهام التجميع والاختبار للنسخة الـ Debug فقط (لا تحتاج لمفاتيح الإنتاج):
      - run: ./gradlew testDebugUnitTest assembleDebug

# 2. في وظيفة النشر الحقيقية: نربطها ببيئة إنتاجية محمية تتطلب مراجعين معتمدين:
  publish_release:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production-protected # يتطلب موافقة يدوية في GitHub Settings
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew bundleRelease
        env:
          KEYSTORE_PASSWORD: ${{ secrets.PROD_KEYSTORE_PASSWORD }}
```

## Why it matters and how it works

CI executes repository code, including build scripts and plugins, so PR jobs are code execution by an untrusted author. `pull_request_target`-style privileged contexts are dangerous if they check out untrusted commits. Artifact promotion must validate provenance rather than trusting attacker-produced files.

## Worked example

An attacker changes `build.gradle.kts` to POST `$PLAY_TOKEN`. In safe CI, PR job has no token and outbound restrictions where feasible. After merge/review, a separate release job retrieves scoped credentials and signs a known commit’s artifact.

## Trade-offs and decision criteria

Isolated workflows add complexity and may delay external contributions, but protect signing authority. Dependency verification and pinned actions reduce supply-chain exposure; they do not replace PR-secret isolation.

## Failure modes

A workflow uses a privileged token and then checks out `github.event.pull_request.head.sha`; malicious Gradle runs with secrets. Remove secret from that context, restrict permissions and rotate any exposed credential.

## Production perspective

Security review covers workflows, actions, Gradle plugins and artifact handoff. Audit release-trigger permissions and credential use, and alert on unexpected Play uploads.

## Interview answer — short

Prevent secret leakage by relying on CI security boundaries where PRs from forks have zero access to repository secrets by default. Avoid the vulnerable pull_request_target checkout pattern, mandate human maintainer approval for first-time contributors before workflows run, and isolate signing secrets into protected environments with strict branch restrictions.

## Interview answer — structured

Defending Android CI pipelines against malicious pull requests targeting signing secrets requires multi-layered controls:

1. **Default Fork Secret Isolation**:
   - Modern CI platforms (such as GitHub Actions) strictly withhold repository secrets from workflow runs triggered by `pull_request` events originating from forked repositories. The runner operates in a zero-secret sandbox.

2. **Eliminate the `pull_request_target` Pwn Vulnerability**:
   - Never use `pull_request_target` combined with checking out the pull request's untrusted HEAD commit. This dangerous pattern grants untrusted code access to write permissions and repository secrets, allowing attackers to exfiltrate keys via build scripts.

3. **First-Time Contributor Execution Gates**:
   - Configure repository security policies to require maintainer review and manual approval before any workflow runs for first-time contributors, preventing malicious crypto-miners or credential-stealing scripts from executing automatically.

4. **Environment Isolation & Branch Protection**:
   - Bind production signing secrets to a protected 'Production' Environment in GitHub/GitLab. Restrict this environment exclusively to the protected `main` branch with mandatory code reviews, ensuring PRs cannot reference release secrets.

## Interview answer — deep senior

From a supply-chain security and build provenance perspective, defense-in-depth extends into Gradle and dependencies:

1. **Gradle Build Cache & Dependency Poisoning**: A malicious PR could modify dependency resolution repositories in `settings.gradle.kts` to point to an attacker-controlled Maven server serving poisoned binaries, or poison the shared remote build cache. Ensure PR builds have read-only build cache permissions and restrict dependency repositories to verified HTTPS hosts.

2. **Dynamic Log Redaction & Audit**: Even within trusted teams, mistakes happen. CI systems employ automated output scanners that mask detected high-entropy strings and recognized private key formats (`-----BEGIN PRIVATE KEY-----`). Any attempt to print masked variables results in `***` in the public build logs.

3. **Audit CI Network Egress**: In enterprise self-hosted runner infrastructure, configure firewall egress rules to restrict CI outbound network traffic exclusively to authorized endpoints (Maven Central, Google Maven, Google Play API, GitHub), blocking unauthorized outbound sockets to arbitrary external IP addresses.

## How to answer in the interview

- **Why:** source manifests differ from shipped merge.
- **How:** inspect release merged manifest and smoke URI.
- **Trade-off:** static speed versus runtime proof.
- **Failure case:** placeholder resolves to wrong authority.
- **Production solution:** gate exact authority, permissions and export state.

## Deep-dive talking points

Prompt for build script exfiltration, privileged context danger, artifact provenance and credential rotation.

## Follow-up questions

- **Interviewer:** "Why does GitHub Actions withhold secrets from `pull_request` events originating from forks?"
  **Answer:** "To prevent unauthorized external contributors from modifying code or workflows to print or exfiltrate private repository secrets."

- **Interviewer:** "What is the correct way to use `pull_request_target` safely if it is needed?"
  **Answer:** "Use it only for labeling or triage actions without checking out or running the untrusted PR code."

## Self-check rubric

Explain fork-PR secret isolation, workflow permission minimization and avoiding privileged pull_request_target checkout of attacker code. Show a safe path for artifact validation before signing.

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing roles.
- [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html) — supply-chain integrity.

Technically reviewed against primary documentation on 2026-10-13.
