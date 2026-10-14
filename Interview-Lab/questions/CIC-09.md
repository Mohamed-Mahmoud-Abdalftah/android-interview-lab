---
id: "CIC-09"
question: "How do you protect signing material and CI secrets?"
topic: "CI/CD, Git & Team Delivery"
code: "CIC"
group: "B"
phase: 4
priority: "P2"
order: 428
editorial_status: "reviewed"
---

# CIC-09

## Original interview question

How do you protect signing material and CI secrets?

## What the interviewer evaluates

- Signing key custody and PR secret isolation.
- Short-lived credentials, audit and artifact provenance.

## Explanation in Arabic

كيف تقوم بحماية مفاتيح التوقيع (Signing Keystore) وأسرار الـ CI/CD من التسريب أو الاختراق؟

1. المخاطر الأمنية الرئيسية:
   - **تسريب الـ Keystore**: إذا تسرب مفتاح توقيع التطبيق وكلمة السر، يمكن لأي مخترق نشر تحديثات خبيثة للمستخدمين.
   - **اختراق عبر Pull Requests**: تشغيل سيرفرات الـ CI تلقائياً على فروع الـ Forks المفتوحة قد يسمح لمهاجم بطباعة الـ Secrets في الـ Logs (`echo $KEYSTORE`).
   - **كشف الأسرار في الـ Version Control**: رفع ملفات `.jks` أو كلمات المرور صراحة في `build.gradle.kts`.

2. أفضل الممارسات الهندسية لحماية الأسرار:
   - **Google Play App Signing**: الاعتماد على جوجل لحفظ مفتاح التوقيع الرئيسي (App Signing Key). السيرفر يحتاج فقط لمفتاح الرفع (Upload Key)؛ وإذا ضاع أو تسرب مفتاح الرفع، يمكن إعادة ضبطه بسهولة عبر Google Support دون فقدان التطبيق.
   - **تخزين الـ Keystore كـ Secret سحابي**: تحويل ملف الـ JKS إلى نص مشفر (Base64) وتخزينه داخل GitHub Secrets أو HashiCorp Vault أو GCP Secret Manager.
   - **استدعاء الأسرار بشكل عابر (Ephemeral Extraction)**: فك تشفير الـ Keystore في ملف مؤقت داخل مجلد الـ Runner أثناء البناء فقط، ثم حذفه فور انتهاء المهمة.
   - **عزل أسرار الـ PRs**: منع فروع الـ PRs القادمة من الـ Forks من الوصول لأسرار التوقيع والـ Play Store نهائياً.

## Practical walkthrough

إعداد توقيع الـ Release في Gradle بشكل آمن باستخدام متغيرات البيئة المشفرة:
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // قراءة المسار والأسرار من متغيرات البيئة فقط، وتجنب وضعها في الكود نهائياً:
            storeFile = System.getenv("KEYSTORE_FILE_PATH")?.let { file(it) }
            storePassword = System.getenv("KEYSTORE_STORE_PASSWORD")
            keyAlias = System.getenv("KEYSTORE_KEY_ALIAS")
            keyPassword = System.getenv("KEYSTORE_KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```
وفي ملف GitHub Actions:
```yaml
- name: Decode and Setup Keystore
  env:
    KEYSTORE_BASE64: ${{ secrets.ANDROID_UPLOAD_KEYSTORE_BASE64 }}
  run: |
    echo "$KEYSTORE_BASE64" | base64 --decode > /tmp/release_upload.jks
- name: Build Release Bundle
  env:
    KEYSTORE_FILE_PATH: /tmp/release_upload.jks
    KEYSTORE_STORE_PASSWORD: ${{ secrets.KEYSTORE_STORE_PASSWORD }}
    KEYSTORE_KEY_ALIAS: ${{ secrets.KEYSTORE_KEY_ALIAS }}
    KEYSTORE_KEY_PASSWORD: ${{ secrets.KEYSTORE_KEY_PASSWORD }}
  run: ./gradlew bundleRelease
- name: Clean Up Keystore
  if: always()
  run: rm -f /tmp/release_upload.jks
```

## Why it matters and how it works

Play App Signing separates app signing key management from upload key workflows. CI credentials are granted only to trusted release jobs after required checks, with scoped access and rotation. A masked CI variable is not safe if attacker-controlled code can read it and exfiltrate it.

## Worked example

A fork PR runs compile/tests with read-only token. Only after merge to protected branch does a separate release workflow fetch upload credentials, sign AAB and upload to internal track. The job records artifact hash but never exposes keystore bytes or passwords in logs.

## Trade-offs and decision criteria

Cloud-managed signing reduces direct key handling but adds provider dependency. Manual signing limits automation but can create human error. Choose a custody model with recovery and upload-key rotation procedures.

## Failure modes

Using `pull_request_target` to check out untrusted PR code and run Gradle with repository secrets leaks credentials. Split contexts and never execute untrusted build scripts in privileged job.

## Production perspective

Periodic audit reviews who can trigger release, secret access logs, credential expiry and artifact signatures. Incident runbook covers upload-key compromise and revoked Play service credentials.

## Interview answer — short

Protect signing material by using Google Play App Signing (so CI only holds an Upload Key), storing the keystore as a base64-encoded secret in CI secret vaults, injecting credentials dynamically via environment variables, decoding the file ephemerally into a temporary path deleted on cleanup, and strictly isolating release secrets from untrusted PR builds.

## Interview answer — structured

A hardened mobile secret management architecture relies on four defensive layers.

First, **Google Play App Signing Architecture**. Next, delegate root app signing authority to Google Cloud Key Management. The CI pipeline only holds an **Upload Key**. If an upload key is compromised, administrators can revoke and rotate it via Play Console without stranding existing installed users.
**Encrypted Secret Storage & Ephemeral Lifecycle**. The upload keystore binary is encoded as base64 and stored in enterprise secret vaults (GitHub Secrets, AWS Secrets Manager, or HashiCorp Vault). The CI runner decodes the file into an ephemeral temporary path (`/tmp/upload.jks`) immediately before compilation and securely wipes it in a `finally` or `if: always()` post-build step.
**Zero Secrets in Source Control**. Keystore passwords, aliases, and Play Console JSON API keys are strictly injected via environment variables at runtime, never committed to `build.gradle.kts` or `keystore.properties`.
**PR Execution Security Boundary**. Finally, pull requests originating from public forks or unverified contributors are executed in unprivileged sandbox runners where production release secrets are strictly masked and unavailable.


## Interview answer — deep senior

From a DevSecOps and supply-chain defense perspective, advanced secret protection involves preventing indirect exfiltration.

First, with Malicious Dependency and PR Injection, attackers can submit PRs modifying third-party dependencies or Gradle build scripts to print `System.getenv()` into build logs or send secrets via curl. GitHub Actions enforces that `pull_request` triggers do not have access to repository secrets by default. Never use `pull_request_target` with an automatic checkout of PR head code, as this exposes secrets to attacker-controlled scripts. Next, with Log Masking and Redaction, ensure CI secret values are registered with secret masking utilities (e.g., `::add-mask::` in GitHub Actions). Gradle log levels must never be set to `--debug` or `--info` on production signing tasks, as Gradle may log command-line arguments and environment parameters.
Finally, with OIDC (OpenID Connect) for Cloud Access, replace long-lived API service account JSON keys for Google Cloud and Google Play with short-lived OIDC federated tokens. The GitHub Actions runner authenticates directly with GCP Workload Identity Federation using temporary cryptographic credentials, eliminating static stored credentials.


## How to answer in the interview

- **Why:** release credentials can publish hostile builds.
- **How:** isolate trusted release job and least-privilege secrets.
- **Trade-off:** convenience versus blast radius.
- **Failure case:** fork PR build script exfiltrates secret.
- **Production solution:** protected environments, short-lived credentials, rotation.

## Deep-dive talking points

Prompt for malicious Gradle script, PR versus release isolation, Play upload key, audit and rotation.

## Follow-up questions

- **Interviewer:** "What is the critical security benefit of Google Play App Signing over managing the app signing key manually?"
  **Answer:** "If your upload key is compromised or lost, Google Play can rotate it upon request without abandoning the app or stranding existing users."

- **Interviewer:** "Why is using `pull_request_target` dangerous when handling secrets in GitHub Actions?"
  **Answer:** "Because it runs in the context of the base branch with secret access, allowing untrusted PR code to exfiltrate secrets if checked out directly."

## Self-check rubric

Keep signing credentials out of untrusted PR jobs, scope and rotate secrets, protect workflow permissions and review fork behavior. Explain what a malicious PR could read if the boundary is wrong.

## References and reviewed-on date

- [Play App Signing](https://developer.android.com/studio/publish/app-signing) — signing and upload key roles.
- [Android publishing](https://developer.android.com/studio/publish) — release workflow.

Technically reviewed against primary documentation on 2026-10-13.
