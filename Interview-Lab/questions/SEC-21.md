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

Play Integrity API evaluates app binary authenticity, licensing, and device integrity verdicts. The client must never decrypt or act on the token locally; instead, it requests a token bound to a server-generated nonce and sends it to the backend, which decodes Google's cryptographic verdict to enforce policy.

## Interview answer — structured

Play Integrity API provides attestation of app authenticity and device trustworthiness.

First, **Evaluation Signals**. Next, with App Recognition, validates whether the running APK matches the package name and signing certificate registered in Google Play.
Additionally, with App Licensing, verifies whether the user acquired the app legitimately through Google Play. With Device Recognition, returns graduated verdicts (`MEETS_BASIC_INTEGRITY` for emulators/rooted devices without active tampering, `MEETS_DEVICE_INTEGRITY` for certified CTS-compliant Android devices, `MEETS_STRONG_INTEGRITY` for hardware-backed keystore and bootloader locking).
**Mandatory Server-Side Verification**. Decrypting or validating verdicts on the Android client is an anti-pattern because client memory and conditional branches can be hooked.
The server initiates an action by generating a cryptographically random, short-lived `nonce`. The mobile client requests an integrity token embedding this nonce, and forwards the token to the backend. Finally, the backend validates the verdict payload directly via Google APIs or Google's public keys, verifying the nonce, timestamp, package name, and integrity level.


## Interview answer — deep senior

Senior architects implement Play Integrity using risk-based decision ladders rather than binary kill-switches.

First, with Tiered Risk Responses, failing `MEETS_STRONG_INTEGRITY` should not immediately block app usage. Budget devices, custom vendor builds, or uncertified devices can pass `MEETS_BASIC_INTEGRITY`. High-risk financial operations (wire transfers, password resets) can mandate `MEETS_DEVICE_INTEGRITY`, while read-only browsing can proceed under basic integrity with stepped-up MFA requirements. Next, play Integrity Standard vs. Classic Requests is the standard API offers cached attestation tokens for low latency, while classic requests communicate directly with Google Play servers. For sensitive payments, classic requests bound to dynamic nonces guarantee fresh, un-cached hardware validation.
Finally, with Fallback & Graceful Degradation, google Play Services may be temporarily unavailable or throttled. Backend architectures must establish fallback policies (e.g., rate-limiting requests or requiring SMS OTP) rather than completely blocking legitimate users during Google outages.


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
