---
id: "TST-23"
question: "How would you create a risk-based test plan for a security-sensitive release?"
topic: "Testing, Quality & Reliability"
code: "TST"
group: "C"
phase: 4
priority: "P1"
order: 418
editorial_status: "reviewed"
---

# TST-23

## Original interview question

How would you create a risk-based test plan for a security-sensitive release?

## What the interviewer evaluates

- Threat-driven release test scope and evidence.
- Highest-risk trust boundaries, regression and rollout monitoring.

## Explanation in Arabic

كيف تضع خطة اختبار مبنية على المخاطر (Risk-Based Test Plan) لإصدار أمني حساس (Security-Sensitive Release) لتطبيق بنكي؟

1. مفهوم الـ Risk-Based Testing في أندرويد:
   - التركيز على الميزات الأكثر خطورة (High-Impact / High-Probability Areas) بدلاً من إضاعة الوقت في اختبار شاشات ثابتة.
   - في التطبيقات المالية، المجالات الأكثر خطورة هي: **المصادقة وتخزين التوكنز، التشفير العتادي، تحويل الأموال، وحماية الذاكرة**.

2. محاور خطة الاختبار الأمني الحساسة (The 4 Security Testing Pillars):
   - **1. اختبارات الـ Cryptographic Integrity**: التحقق من أن مفاتيح Keystore AES-GCM مقفلة عتادياً بالبصمة ولا تفتح برمجياً عند محاكاة نجاح البصمة بدون `CryptoObject`.
   - **2. اختبارات هجمات التلاعب (Tampering & Hooking via Frida)**: تشغيل اختبارات أمنية على محاكي معمول له Root وتطبيق سكربتات Frida للتحقق من أن التطبيق يرفض العمليات السيرفرية عند غياب شهادة Play Integrity.
   - **3. اختبارات تسريب البيانات (Data Leakage Verification)**: فحص ملفات Logcat، والـ Screenshots في الـ App Switcher، وتقارير الأعطال للتأكد من خلوها تماماً من أي Bearer tokens أو أرقام بطاقات (PAN).
   - **4. اختبارات التوافق العكسي وتشفير التخزين**: اختبار فتح قاعدة بيانات SQLCipher المشفرة والتأكد من عدم تخزين المفتاح كنص صريح في الـ SharedPreferences.

## Practical walkthrough

مصفوفة اختبار أمني مبنية على المخاطر لتوثيق وتغطية المسارات الحساسة:
```text
مصفوفة الاختبار الأمني المبني على المخاطر (Risk-Based Test Matrix):
┌────────────────────────────┬─────────────────────────────┬──────────────────────────────────────────┐
│ المسار الحساس (Asset)      │ مستوى الخطر (Risk Level)     │ الاختبارات الإلزامية (Verification)       │
├────────────────────────────┼─────────────────────────────┼──────────────────────────────────────────┤
│ Biometric Keystore Unlock  │ Critical (High Impact)      │ اختبار أوتوماتيكي مع CryptoObject حقيقي   │
│ Payment Double-Charge      │ Critical (Financial Loss)   │ اختبار شبكي لـ Idempotency Key مع Timeout │
│ Sensitive Screen Capture   │ High (Compliance Violation) │ فحص تفعيل FLAG_SECURE في Recent Apps     │
│ Logcat Token Leakage       │ High (PII Leak)             │ فحص آلي بـ Semgrep / Custom Lint في CI   │
│ Root / Frida Detection     │ Medium (Client Friction)    │ فحص السلوك المتدرج مع السيرفر            │
└────────────────────────────┴─────────────────────────────┴──────────────────────────────────────────┘
```

## Why it matters and how it works

A risk-based plan ranks likelihood and impact, then assigns verification at the boundary that can actually prove a control. Static scanning catches configuration errors; dynamic tests catch runtime behavior; backend tests verify financial authority. Staged rollout watches residual risks.

## Worked example

For a banking update that changes token storage, test migration from old encrypted data, key invalidation, backup restore, logout, refresh races and log redaction. Add a tampered-client request test to prove server rejects changed amounts. Run minified APK smoke on supported API levels.

## Trade-offs and decision criteria

Broad exhaustive device coverage is costly; choose representative API/ABI/OEM cohorts based on exposure and incident history. Automated scans help prioritize but do not replace manual threat review or provider certification.

## Failure modes

Team runs only unit tests and claims security complete while a new exported Activity accepts forged extras. Inspect merged manifest and execute hostile intents. A passing client test cannot prove backend authorization.

## Production perspective

Record risk owner, test evidence, residual limitation and release gate. Roll out gradually with anomaly dashboards, rollback plan and incident escalation; monitor both security and legitimate-user false positives.

## Interview answer — short

Create a risk-based test plan by ranking features by financial and security impact, prioritizing hardware Keystore cryptography, payment idempotency, and token leakage surfaces. Combine automated linting for PII leaks, on-device instrumentation tests for biometric ciphers, and simulated hooking attacks to verify server-side zero-trust defenses.

## Interview answer — structured

A risk-based security test plan prioritizes engineering verification according to asset criticality and threat modeling.

First, **Threat Modeling & Risk Stratification**. Next, categorize application components into Risk Tiers. Tier 1 (Critical): Authentication tokens, Keystore encryption, biometric authorization, payment checkout. Tier 2 (Moderate): Profile management, deep link routing. Tier 3 (Low): Static marketing content.
**Automated Security Gates in CI**. With Static Analysis, enforce custom Android Lint and Semgrep rules scanning for hardcoded secrets, missing `FLAG_SECURE`, cleartext traffic permissions, and insecure `FLAG_MUTABLE` PendingIntents.
With Dependency Vulnerability Scanning, run automated CVE scans against all third-party Gradle dependencies. **Dynamic On-Device Security Assertions**.
Execute instrumented tests verifying that Keystore keys mandate `setUserAuthenticationRequired(true)`. Assert that invoking biometric callbacks without valid hardware `CryptoObject` releases triggers `UserNotAuthenticatedException`.
**Data Exfiltration Audits**. Finally, audit release build outputs: inspect Logcat outputs, memory heap dumps, and SQLite database files to assert that PAN numbers, CVVs, and auth tokens are strictly absent from unencrypted storage.


## Interview answer — deep senior

From an organizational compliance and release governance perspective, high-assurance releases require multi-party sign-offs.

First, with Independent Penetration Testing (OWASP MASTG), validate the release candidate against OWASP Mobile Application Security Testing Guide (MASTG) benchmarks. Engage external penetration testers to attempt dynamic method hooking (Frida), local storage extraction (`adb backup`), and proxy interception (Burp Suite). Next, with Server-Side Zero Trust Verification, test that backend endpoints reject requests if the client's Play Integrity verdict indicates a tampered APK or unrecognized signing certificate SHA-256.
Finally, with Rollback & Blast-Radius Mitigation, ensure the security release is backed by active remote feature kill switches. If an unanticipated issue occurs post-release, the security feature can be disarmed remotely without deploying an emergency app store update.


## How to answer in the interview

- **Why:** security-sensitive changes need risk-weighted evidence.
- **How:** map token migration, key loss, backup, tampering and logs to test layers.
- **Trade-off:** release cost versus exposure and impact.
- **Failure case:** client SDK verdict is treated as authorization.
- **Production solution:** backend checks, device matrix and exact coverage report.

## Deep-dive talking points

Prompt for threat-to-test matrix, real boundary, release variant, residual risk and rollout gate.

## Follow-up questions

- **Interviewer:** "What is the primary objective of Risk-Based Testing?"
  **Answer:** "To allocate testing effort and time proportionally to the areas of highest business, financial, and security risk."

- **Interviewer:** "Why is static analysis alone insufficient for a security-sensitive release?"
  **Answer:** "Static analysis inspects code syntax, but cannot verify dynamic runtime behavior like Keystore hardware key unlocks, memory dumps, or network race conditions."

## Self-check rubric

Rank token migration, key invalidation, backup restore, tampered requests and log leakage by likelihood and impact. Assign each a test layer and release gate, including a minified build and backend authorization check.

## References and reviewed-on date

- [OWASP MASVS](https://mas.owasp.org/MASVS/) — mobile security controls.
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — test methods.

Technically reviewed against primary documentation on 2026-10-13.
