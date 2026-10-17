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

## Concept and technical explanation

OWASP MASVS (Mobile Application Security Verification Standard) defines the definitive baseline security requirements for mobile applications, organized across eight core domains: Storage, Crypto, Auth, Network, Platform, Code, and Resilience. Applications are evaluated against defined risk profiles: MASVS-L1 establishes standard security baseline hygiene applicable to all mobile apps; MASVS-L2 introduces defense-in-depth controls required for sensitive financial, healthcare, and enterprise apps; and MASVS-R specifies technical resilience controls against client-side reverse engineering, dynamic instrumentation, and binary tampering. OWASP MASTG (Mobile Application Security Testing Guide) serves as the companion technical testing manual. It provides concrete static analysis (SAST) and dynamic analysis (DAST) procedures, test cases, and tool workflows (utilizing Frida, objection, radare2, and Ghidra) to rigorously verify whether an application complies with each corresponding MASVS requirement.

## Practical walkthrough (English)

Automated MASVS compliance checks in CI/CD and production code verification:
```kotlin
// 1. Implementing MASVS-STORAGE: Hardware-backed encrypted preferences
class SecureStorageManager(private val context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .setRequestStrongBoxProvider(true)
        .build()

    val encryptedPrefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_vault_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
}

// 2. Enforcing MASVS-NETWORK: Disabling cleartext traffic and configuring TLS 1.3
// Verified in res/xml/network_security_config.xml and tested dynamically via MASTG test suites
```

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

OWASP MASVS provides the standard security requirements for mobile applications across storage, crypto, network, and platform domains, divided into baseline L1, defense-in-depth L2, and anti-tamper resilience R levels. MASTG is the comprehensive testing manual that details how to verify each requirement through static analysis and dynamic reverse-engineering tools like Frida. Together, they transform subjective security reviews into verifiable, reproducible engineering standards.

## Interview answer — structured

Mobile security reviews require an objective benchmark rather than ad-hoc opinions, and OWASP MASVS establishes that baseline.
The standard divides mobile security into eight specific domains covering data storage, cryptography, authentication, network communication, platform interactions, code quality, and reverse engineering resilience.
Organizations select an applicable verification profile based on their operational threat model.
MASVS-L1 sets essential baseline security for any mobile application, focusing on good hygiene such as blocking cleartext traffic and avoiding credential leakage in system logs.
MASVS-L2 represents defense-in-depth for sensitive financial and medical applications, mandating hardware-backed key storage, certificate pinning, and strict session isolation.
MASVS-R adds explicit anti-tamper and anti-reversing controls for apps operating in hostile client environments.
To verify these requirements, engineers and auditors use the OWASP MASTG.
The MASTG delivers explicit static analysis instructions and dynamic penetration testing recipes using tools like objection and Frida, providing concrete evidence of compliance rather than passive checklist ticking.

## Interview answer — deep senior

In enterprise engineering, OWASP MASVS and MASTG serve as the bridge connecting product engineering, cybersecurity auditors, and regulatory compliance frameworks like PCI-DSS.
Rather than treating security as an afterthought prior to release, we integrate MASVS controls directly into our architectural definitions and continuous integration pipelines.
For a tier-one fintech application, our target profile is MASVS-L2 combined with MASVS-R.
Under MASVS-STORAGE, we mandate that no customer data touches disk unencrypted, routing all persistence through EncryptedSharedPreferences backed by StrongBox and explicitly excluding sensitive databases from automated cloud backups.
Under MASVS-NETWORK, we configure network security configurations to forbid cleartext HTTP and enforce public key pinning with planned rotation schedules.
Under MASVS-PLATFORM, we audit every exported component, verify incoming deep link digital assets, and lock all PendingIntents with immutability flags.
The true power of MASTG lies in dynamic validation during automated staging tests.
We utilize MASTG test cases within automated security smoke tests, injecting Frida scripts to verify whether sensitive cryptographic keys can be extracted from memory dumps and confirming that repackaged binaries fail signature verification.
This shifts security left from an annual compliance audit to an automated engineering discipline with measurable security SLOs. We also configure automated SAST linters in our Gradle verification tasks to enforce crypto algorithm standards and verify that all manifest components declare explicit exported flags.

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
