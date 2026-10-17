---
id: "SEC-21"
question: "What is Play Integrity API? What trust decisions must happen on the server?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 318
editorial_status: "reviewed"
---

# SEC-21

## Original interview question

What is Play Integrity API? What trust decisions must happen on the server?

## What the interviewer evaluates

- Play Integrity verdict as server-consumed risk signal, not client Boolean.
- Request binding, freshness, policy tiers and false positives.

## Concept and technical explanation

The Google Play Integrity API is a security attestation service that helps developers protect their applications and backend services from tampering, fraud, unauthorized access, and malicious execution environments. The architecture bridges the mobile client, Google Play servers, and the enterprise application backend. During a high-stakes transaction (login, checkout, payment authorization), the client requests a cryptographic integrity token, binding it to a server-generated cryptographic nonce to defeat replay attacks. Google Play services inspect the runtime environment—checking bootloader status, system image integrity, hardware-backed Keystore attestation, and Google Play app licensing. Critically, the mobile client must never decrypt, parse, or evaluate this integrity verdict locally, as dynamic instrumentation tools like Frida can easily hook client Boolean checks. Instead, the raw encrypted token is sent to the enterprise backend server, where it is decrypted and validated directly against Google's Play Integrity servers before authorizing business logic.

## Practical walkthrough (English)

Requesting and binding a Play Integrity token with server-side nonce:
```kotlin
class IntegrityAttestationManager(
    private val context: Context,
    private val backendApi: FintechApiService
) {
    private val integrityManager = PlayIntegrity.getIntegrityManager(context)

    suspend fun verifyAndExecutePayment(orderId: String, amount: Long) {
        // 1. Fetch one-time cryptographic nonce from enterprise backend
        val serverNonce = backendApi.generatePaymentNonce(orderId)

        // 2. Request attestation token bound to the server nonce
        val tokenResponse = integrityManager.requestIntegrityToken(
            IntegrityTokenRequest.builder()
                .setNonce(serverNonce) // Cryptographically binds token to this specific action
                .build()
        ).await()

        val integrityToken = tokenResponse.token()

        // 3. Transmit encrypted token to backend server - NEVER evaluate locally!
        val verificationResult = backendApi.authorizePaymentWithIntegrity(
            orderId = orderId,
            amount = amount,
            integrityToken = integrityToken
        )
        
        if (!verificationResult.isSuccess) {
            throw SecurityException("Backend rejected transaction: device integrity failure")
        }
    }
}
```

## Explanation in Arabic

ما هي Play Integrity API؟ وما هي القرارات الأمنية التي يجب أن تُتخذ حصرياً على السيرفر (Server-Side Decisions)؟

1. ما هي Play Integrity API وماذا تفحص؟
   - هي البديل الرسمي والحديث لـ SafetyNet Attestation من Google.
   - تقوم بفحص حالة البيئة التي يعمل فيها التطبيق وإصدار شهادة موقعة مشفرة (Cryptographically Signed Token) تحتوي على ثلاثة مؤشرات رئيسية:
     * **App Licensing Verdict**: هل التطبيق مرخص ومثبت من متجر Google Play الرسمي؟
     * **App Recognition Verdict**: هل توقيع الـ APK والـ Package Name مطابقان للإصدار الأصلي المسجل في Play Console؟
     * **Device Recognition Verdict**: مستوى سلامة الجهاز والعتاد (MEETS_BASIC_INTEGRITY, MEETS_DEVICE_INTEGRITY, MEETS_STRONG_INTEGRITY).

2. القاعدة الذهبية: العميل لا يفك التشفير ولا يتخذ القرار!
   - **خطأ ساذج**: فك تشفير الـ Token على الهاتف وفحص النتيجة في كود Kotlin (`if (verdict == MEETS_DEVICE_INTEGRITY)`). هذا الفحص يمكن تجاوزه بسهولة عبر Frida أو تعديل الـ Smali!
   - **المعمارية الصحيحة**: يقوم السيرفر بإنشاء رقم عشوائي (Cryptographic Nonce) مشفر مرتبط بطلب المستخدم. يطلب التطبيق الـ Token من Google Play مدمجاً بهذا الـ Nonce، ثم يرسل الـ Token الخام إلى السيرفر. السيرفر هو الطرف الوحيد الذي يفك تشفير الـ Token ويفحص التوقيع وصحة الـ Nonce ويتخذ قرار السماح أو الرفض.

## Practical walkthrough

المعمارية الصحيحة لطلب Play Integrity Token وإرساله للسيرفر للتحقق منه:
```kotlin
class PlayIntegrityRepository(
    private val context: Context,
    private val backendApi: BackendSecurityApi
) {
    private val integrityManager = IntegrityManagerFactory.create(context)

    // 1. طلب الـ Token باستخدام Nonce وارد من السيرفر لمنع هجمات Replay Attacks:
    suspend fun verifyTransaction(serverNonce: String, transactionId: String): TransactionResult {
        val request = IntegrityTokenRequest.builder()
            .setCloudProjectNumber(123456789012L) // Cloud Project Number الخاص بالتطبيق
            .setRequestHash(serverNonce) // ربط الـ Token بالـ Nonce السيرفري
            .build()

        val tokenResponse = integrityManager.requestIntegrityToken(request).await()
        val integrityToken = tokenResponse.token()

        // 2. إرسال الـ Token الخام للسيرفر دون فحص محلي:
        // السيرفر يستخدم Google Play Developer API لفك التشفير والتأكد من سلامة التوقيع والجهاز
        return backendApi.authorizeSensitiveTransaction(
            transactionId = transactionId,
            integrityToken = integrityToken
        )
    }
}
```

## Why it matters and how it works

The backend uses Google Play’s decode/verification flow and checks package identity, app recognition, request details and the action binding. Standard requests support requestHash; classic requests use nonce. Do not put sensitive raw data in these fields. Verdict categories and availability vary, so absent or adverse signals need documented handling.

## Worked example

Android/Kotlin request-binding illustration for a Play Integrity **standard** request. `TransferIntent` fields are validated and immutable; app and backend must use the exact same canonical serialization. Pass this digest as `requestHash`, then have the backend verify and decode the integrity token and recompute the hash before it applies transfer authorization.

```kotlin
import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID

data class TransferIntent(
    val operationId: UUID,
    val amountMinor: Long,
    val currency: String,
    val beneficiaryId: UUID,
)

fun requestHash(intent: TransferIntent): String {
    require(intent.amountMinor > 0)
    require(intent.currency.matches(Regex("[A-Z]{3}")))
    val canonical = "${intent.operationId}|${intent.amountMinor}|" +
        "${intent.currency}|${intent.beneficiaryId}"
    val bytes = MessageDigest.getInstance("SHA-256")
        .digest(canonical.toByteArray(StandardCharsets.UTF_8))
    return Base64.encodeToString(bytes, Base64.NO_WRAP)
}
```

A hash binds fields but is not itself an authorization check; the server still validates session, operation state, amount and risk policy.

## Trade-offs and decision criteria

Integrity raises attack cost and supports fraud decisions but adds latency, quotas, platform dependency and exclusion risk. A high-friction deny policy may harm legitimate devices; tiered responses can preserve availability while limiting exposure.

## Failure modes

Checking the verdict only on-device lets an attacker patch the result. Reusing a token for another amount breaks request binding. A cached verdict can be proxied; request it near the protected action and validate server-side.

## Production perspective

Instrument acceptance/denial rates by app version and device cohort without collecting unnecessary identifiers. Review false-positive appeals, provide safe alternate verification, and test tampered request parameters.

## Interview answer — short

Play Integrity API checks app authenticity, licensing, and device integrity against Google Play servers. The client requests an encrypted token bound to a server-side nonce during sensitive actions. The enterprise backend server must decrypt and evaluate the verdict, deciding whether to allow the action based on device trust levels rather than trusting client-side Boolean checks.

## Interview answer — structured

Google Play Integrity API provides cryptographic proof that requests originate from your genuine, unmodified application binary running on a trusted, certified Android device.
When a sensitive operation like a financial transaction or authentication begins, the mobile app obtains a one-time cryptographic nonce from the backend server.
The app passes this nonce to the Play Integrity SDK, which queries Google Play services to assess runtime security.
Google analyzes the operating system bootloader status, system image signatures, package certificate, and user licensing.
The SDK returns an encrypted, signed integrity token to the application.
Crucially, all trust decisions must occur on the backend server.
Evaluating integrity verdicts on the client by checking simple Boolean conditions is futile because an attacker using Frida or debuggers can hook the method and force a positive verdict.
The mobile app forwards the encrypted token to the enterprise backend, which decrypts it using Google API endpoints, validates the nonce freshness, and enforces business policies according to device integrity tiers.

## Interview answer — deep senior

In modern zero-trust mobile architecture, Play Integrity API serves as the cryptographic bridge that verifies client trustworthiness without relying on vulnerable client-side self-assertions.
Traditional root-detection libraries rely on checking file paths like /system/bin/su or inspecting build tags.
In an adversarial environment, tools like Magisk with Zygisk hide these artifacts effortlessly, and runtime hookers like Frida neutralize return values in memory.
Play Integrity overcomes this by leveraging hardware-backed Keystore attestation and Google Play infrastructure to generate an asymmetric cryptographic verdict that cannot be forged by a local client process.
The threat model dictates that the mobile client is strictly a messenger.
If the client attempted to parse the token or decide access based on if (verdict.isTrusted()), an adversary modifies a single assembly branch or hooks the method to bypass security entirely.
Therefore, the backend server must be the sole consumer of the attestation verdict.
The workflow enforces cryptographic action binding: the backend generates a cryptographically secure random nonce tied to the specific user session and transaction parameters.
When the backend receives the integrity token, it calls Google's server-to-server decryption API.
The backend inspects three verdict categories: appLicensing, appRecognitionVerdict (verifying the genuine package and release signing certificate), and deviceRecognitionVerdict (evaluating MEETS_BASIC_INTEGRITY, MEETS_DEVICE_INTEGRITY, and MEETS_STRONG_INTEGRITY).
The server applies nuanced risk policies: allowing read-only browsing on basic devices while strictly demanding MEETS_STRONG_INTEGRITY for high-value fund transfers.

## How to answer in the interview

- **Why:** attestation adds signals, not user authorization.
- **How:** bind token to request details and verify verdict plus session server-side.
- **Trade-off:** strict enforcement can exclude legitimate devices.
- **Failure case:** trusting a client-decoded verdict or replayed token.
- **Production solution:** server risk tiers, nonce/hash binding, and outcome monitoring.

## Deep-dive talking points

Prompt for standard requestHash versus classic nonce, server decode, request binding, tiered policy and false-positive handling.

## Follow-up questions

- **Interviewer:** "What happens on devices without Google Play Services (e.g., Huawei or custom AOSP)?"
  **Answer:** "Play Integrity API fails immediately with an integrity service unavailable error; alternative attestations or server-side risk scoring must be used."

- **Interviewer:** "Why is the nonce parameter critical for Play Integrity requests?"
  **Answer:** "The nonce binds the integrity verdict to a specific transaction and timestamp, preventing attackers from capturing a valid token and replaying it against future requests."

## Self-check rubric

Can I place token verification on the server and explain binding, normal authorization and adverse-verdict handling?

## References and reviewed-on date

- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — signal and policy model.
- [Standard API request](https://developer.android.com/google/play/integrity/standard) — requestHash binding.

Technically reviewed against primary documentation on 2026-10-13.
