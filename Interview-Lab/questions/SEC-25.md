---
id: "SEC-25"
question: "What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 322
editorial_status: "reviewed"
---

# SEC-25

## Original interview question

What are OWASP MASVS/MASTG, and how do they guide mobile security reviews?

## What the interviewer evaluates

- MASVS as controls and MASTG as test procedures.
- Risk-based scope, evidence and the difference between a checklist and proof.

## Explanation in Arabic

ما هي معايير OWASP MASVS و MASTG، وكيف ترشد المهندسين في مراجعات الأمان واختبار الاختراق لتطبيقات أندرويد؟

1. ما هو OWASP MASVS (Mobile Application Security Verification Standard)؟
   - هو المعيار الصناعي العالمي الموحد لمتطلبات أمان تطبيقات الموبايل.
   - يقسم متطلبات الأمان إلى 8 مجالات رئيسية:
     * **MASVS-STORAGE**: أمان تخزين البيانات، تشفير قواعد البيانات، منع التسريب في الـ Logs والـ Backups.
     * **MASVS-CRYPTO**: استخدام خوارزميات التشفير القياسية (AES-GCM)، توليد المفاتيح في Keystore، حظر الخوارزميات الضعيفة (MD5, SHA1, DES, ECB).
     * **MASVS-AUTH**: إدارة الجلسات، التوكنز، وحماية المصادقة البيومترية.
     * **MASVS-NETWORK**: تشفير الاتصالات عبر TLS 1.3، تثبيت الشهادات (Pinning)، وتأمين WebViews.
     * **MASVS-PLATFORM**: أمان مكونات النظام (Exported components, App Links, PendingIntents).
     * **MASVS-CODE**: جودة الكود، إعدادات المترجم، وتحديث المكتبات.
     * **MASVS-RESILIENCE**: مقاومة الهندسة العكسية، فحص الـ Root، وحماية الـ Binary.

2. مستويات التقييم (Verification Levels):
   - **MASVS-L1 (Standard Security)**: المتطلبات الأساسية لجميع التطبيقات (حماية البيانات، HTTPS، منع الـ Logs غير الآمنة).
   - **MASVS-L2 (Defense-in-Depth)**: مخصص للتطبيقات الحساسة (Fintech, Banking, Healthcare) ويتطلب تشفيراً عتادياً و Play Integrity.
   - **MASVS-R (Resilience)**: متطلبات إضافية لمقاومة الهندسة العكسية والـ Tampering.

3. ما هو OWASP MASTG (Mobile Application Security Testing Guide)؟
   - هو الدليل العملي لاختبار كل بند في الـ MASVS، ويحتوي على أوامر الاختبار العملية وأكواد Frida وأدوات الفحص (MobSF, apktool, jadx) للتأكد من استيفاء المتطلبات.

## Practical walkthrough

تطبيق قائمة فحص (Checklist) برمجية مستوحاة من OWASP MASVS-L2 أثناء الـ Code Review:
```kotlin
// فحص برمجي مستوحى من MASVS-STORAGE و MASVS-CRYPTO:
object SecurityReviewChecklist {
    // 1. MASVS-STORAGE: التأكد من عدم استخدام Plaintext SharedPreferences للأسرار
    fun auditStorage(sharedPrefsName: String, context: Context): Boolean {
        val prefsFile = File(context.filesDir.parent, "shared_prefs/$sharedPrefsName.xml")
        // فحص الملف للتأكد من خلوه من أي كلمات مرور أو مفاتيح صريحة
        val content = prefsFile.readText()
        val hasExposedTokens = content.contains("token") || content.contains("password")
        return !hasExposedTokens
    }

    // 2. MASVS-CRYPTO: التحقق من رفض خوارزميات التشفير الممنوعة أمنياً
    fun validateCipherTransformation(transformation: String) {
        val forbidden = listOf("DES", "ECB", "MD5", "RC4")
        if (forbidden.any { transformation.contains(it, ignoreCase = true) }) {
            throw SecurityException("MASVS-CRYPTO Violation: Insecure cipher $transformation is strictly forbidden!")
        }
    }
}
```

## Why it matters and how it works

MASVS defines verification areas and MASTG gives test methods; MASWE catalogs weaknesses. A review maps app assets and threats to relevant controls, executes tests on the actual release build and records evidence, severity and remediation. Passing a tool scan is not equivalent to passing all controls.

## Worked example

For a POS app, map a token-store design to MASVS-STORAGE and MASVS-CRYPTO, then test backup extraction, local file contents, key loss and logging. Map API traffic to MASVS-NETWORK and capture release traffic to verify TLS behavior. Record device/API and app version with findings.

## Trade-offs and decision criteria

A standard makes coverage repeatable, but each app has different assets and risk. A strict checklist can miss a payment-state logic bug; supplement it with architecture and business-flow threat modeling.

## Failure modes

A reviewer marks “encrypted” because a database library is present without testing backups or plaintext logs. Require evidence from runtime/file inspection and a recovery drill. Treat false positives and untested controls explicitly.

## Production perspective

Keep a control-to-test matrix in security review, run MASTG procedures against representative devices and minified builds, and track exceptions with owners and expiry. Retest after SDK, OS or backend changes.

## Interview answer — short

OWASP MASVS defines the security standard across storage, crypto, network, platform, and resilience tiers, evaluated at L1 (baseline), L2 (defense-in-depth for fintech), and R (tamper resistance). MASTG provides practical testing guides, test cases, and penetration testing tools to verify each requirement.

## Interview answer — structured

OWASP MASVS and MASTG serve as the authoritative security verification framework for modern mobile engineering.

First, a MASVS (Specification) defines actionable requirements organized across core security domains. Next, with MASVS-STORAGE, sensitive data at rest, cache clearing, backup exclusion, keyboard cache suppression.
Additionally, with MASVS-CRYPTO, hardware-backed keys, AES-GCM, cryptographically secure PRNGs, eliminating broken primitives. With MASVS-NETWORK, modern TLS configuration, certificate pinning, WebView network boundary hardening.
With MASVS-PLATFORM, restricting exported components, validating deep links, and securing IPC. With MASVS-RESILIENCE, anti-tampering, integrity verification, and root/instrumentation mitigations.
**Security Levels**. With MASVS-L1, baseline hygiene required for any commercial application.
With MASVS-L2, deep defense-in-depth mandatory for fintech, banking, and healthcare applications. With MASVS-R, optional resilience layer providing client hardening against dynamic reverse engineering.
Finally, a MASTG (Testing Guide) provides concrete white-box source code audits, dynamic runtime analysis scripts (Frida), and static tooling (MobSF, JADX) to verify compliance against every MASVS control.


## Interview answer — deep senior

From an architectural governance perspective, senior engineers operationalize MASVS/MASTG throughout the software development lifecycle.

First, with Threat Modeling & Architecture Phase, map every new feature against MASVS controls during design. If a feature introduces biometric authentication, align directly with `MASVS-AUTH` and `MASVS-CRYPTO` by mandating hardware-bound `CryptoObject` patterns. Next, with Automated CI/CD Verification, embed automated compliance gates into CI pipelines using tools like MobSF CLI, Android Lint with custom security rules, and Semgrep scanning for cryptographic misconfigurations (e.g. Hardcoded IVs, `allowBackup=true`, or `FLAG_MUTABLE` PendingIntents).
Finally, with Vendor & Penetration Testing Alignment, use MASTG test identifiers (e.g. `MASTG-TEST-0001`) as the contract benchmark for third-party penetration testing audits, ensuring repeatable, evidence-based security verification rather than subjective vendor opinions.


## How to answer in the interview

- **Why:** security reviews need testable requirements and evidence.
- **How:** map app assets to MASVS controls and MASTG procedures.
- **Trade-off:** broad coverage costs time, so prioritize high-risk paths.
- **Failure case:** checkbox completion without release-build evidence.
- **Production solution:** record scope, device matrix, findings, owners, and residual risk.

## Deep-dive talking points

Prompt for asset/threat inventory, control-to-test evidence, release APK, tool limits and business-logic coverage.

## Follow-up questions

- **Interviewer:** "What is the difference between MASVS-L1 and MASVS-L2?"
  **Answer:** "L1 focuses on standard mobile data hygiene and best practices; L2 enforces advanced threat defense, including hardware-backed cryptographic attestation, strict zeroization, and multi-factor authorization."

- **Interviewer:** "Does achieving MASVS-R guarantee an app cannot be hacked?"
  **Answer:** "No; MASVS-R raises the economic and time cost for reverse engineers, but client execution on a hostile device can never be mathematically guaranteed secure."

## Self-check rubric

Can I map a control to a concrete test and explain limits of scans/checklists?

## References and reviewed-on date

- [OWASP MASVS](https://mas.owasp.org/MASVS/) — mobile verification areas.
- [OWASP MASTG](https://mas.owasp.org/MASTG/) — testing guide.

Technically reviewed against primary documentation on 2026-10-13.
