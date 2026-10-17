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

## Concept and technical explanation

Mitigating secret exfiltration and remote code execution attacks from untrusted pull requests requires strict runner sandboxing, trigger hygiene, and least-privilege infrastructure:
- Attack Vectors in Mobile CI Pipelines:
  - An attacker submits a pull request containing modified Gradle tasks, dependencies, or GitHub Action steps designed to dump environment variables, print base64 keystores, or transmit credentials to an external endpoint.
- The Danger of `pull_request_target`:
  - The standard `pull_request` event executes workflows in the context of the fork, strictly withholding repository secrets and write permissions.
  - Using `pull_request_target` grants workflows access to secrets and write tokens while running against the base repository. If the workflow checks out the untrusted head commit (`ref: github.event.pull_request.head.sha`), it allows arbitrary untrusted code to execute with full access to production signing credentials.
- Multi-Layered Defense Architecture:
  1. Complete Fork Secret Isolation:
     - Workflows triggered by external pull requests must never be exposed to signing keystores, service account JSON files, or deployment credentials.
  2. GitHub Environments & Manual Approvals:
     - Production secrets must be bound to a protected GitHub Environment.
     - Deployments and signing jobs require manual gate approval from designated code owners, preventing automated execution on arbitrary branches.
  3. Ephemeral Secrets & Workload Identity Federation (OIDC):
     - Replace long-lived static service account keys with OpenID Connect (OIDC) tokens federated with Google Cloud IAM. Credentials expire within an hour and cannot be reused outside the specific workflow scope.
  4. Secret Masking and Runner Log Hygiene:
     - CI platforms automatically mask registered secret values, printing `***` in build logs.
     - Ephemeral runner directories are scrubbed immediately in post-execution hooks (`if: always()`).
  5. Scoped Access Permissions:
     - Enforce minimum permissions on CI bot tokens (`permissions: contents: read`). Restrict write and secret-access permissions exclusively to protected mainline deployment jobs.

## Practical walkthrough (English)

Hardened GitHub Actions workflow mitigating malicious PR credential exfiltration:
```yaml
# .github/workflows/pr_verification.yml
name: PR Untrusted Verification

# Safe event: Does not expose production secrets to forks
on:
  pull_request:
    branches: [ main ]

# Minimal default permissions for the GITHUB_TOKEN
permissions:
  contents: read
  pull-requests: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v3

      # Executes checks strictly WITHOUT any production secrets or signing materials
      - name: Run Build and Unit Tests
        run: ./gradlew testDebugUnitTest lintDebug

# Note: Release signing is isolated in a separate workflow:
# Triggered ONLY on push to protected mainline, NEVER on pull_request!
```

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

Prevent signing secret leakage by running PR checks under the standard pull_request event which strictly isolates secrets from forks. Never use pull_request_target with untrusted checkouts. Protect production secrets inside GitHub Environments requiring manual approvals, isolate release signing exclusively to protected mainline pushes, and adopt OIDC short-lived tokens.

## Interview answer — structured

Preventing credential leakage from malicious pull requests requires strict isolation between untrusted code execution and repository secrets.
The primary attack vector occurs when a malicious pull request injects code into build scripts to print or exfiltrate environment variables. To neutralize this, we use the standard pull_request workflow trigger, which inherently restricts runner permissions and withholds all production secrets from untrusted forks. We strictly avoid using pull_request_target with untrusted head commits, as doing so permits remote code execution within a privileged environment.
Furthermore, we restrict signing materials and Google Play service account keys to protected GitHub Environments. These environments enforce mandatory manual approval gates by senior release engineers before jobs can acquire secret access.
By isolating release signing pipelines exclusively to merges onto protected mainline branches and migrating toward short-lived OIDC tokens, we ensure that untrusted contributors have zero access to production cryptographic materials.

## Interview answer — deep senior

From an application security engineering and platform governance standpoint, CI/CD pipelines are prime targets for software supply chain compromises. If an adversary can coax a CI runner into executing arbitrary Gradle code with access to production secrets, your application signing keys and distribution channels are compromised.
The most frequent architectural blunder in GitHub Actions is misconfiguring pull_request_target. Teams often adopt it to allow external pull requests to run linters or post status comments, but then naively checkout the pull request's untrusted head SHA. Because pull_request_target runs in the security context of the base branch, it grants the runner full access to repository secrets. A malicious actor can simply add a line to build.gradle.kts that curls the environment variables to a remote command-and-control server. We strictly prohibit pull_request_target in favor of standard pull_request events with read-only token permissions.
To achieve zero-trust CI security, we physically decouple presubmit validation from release signing. Pull request workflows only compile debug variants and execute JVM unit tests without needing any signing material. Production keystores and deployment service accounts are sequestered inside protected deployment environments. These environments enforce required reviewers, meaning an authorized release engineer must manually approve execution before secrets are decrypted.
Finally, we replace static, long-lived service account JSON keys with OpenID Connect federated authentication against Google Cloud IAM. CI runners request short-lived, single-use identity tokens that automatically expire within minutes and are strictly scoped to upload AABs to specific Play Store tracks, neutralizing credential exfiltration risks completely.

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
