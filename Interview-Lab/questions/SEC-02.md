---
id: "SEC-02"
question: "What is Android Keystore, and what is hardware-backed key storage?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 299
editorial_status: "reviewed"
---

# SEC-02

## Original interview question

What is Android Keystore, and what is hardware-backed key storage?

## What the interviewer evaluates

- Difference between non-exportable key material and encrypted application data.
- Hardware-backed capability checks and their device-dependent limits.

## Concept and technical explanation

Android Keystore lets an app generate and use cryptographic keys without exporting raw key material into its process. That property does not prove that a particular key is hardware backed: depending on device, algorithm, and policy, the key can be software protected, TEE backed, or StrongBox backed. Inspect KeyInfo for the actual generated key when hardware level matters. Hardware protection makes extraction harder, but a compromised app can still request key operations and see data before or after cryptography. Server authorization remains essential for sensitive actions.

## Practical walkthrough (English)

A token-encryption feature generates an AES key under an AndroidKeyStore alias and encrypts each token with AES-GCM using a fresh IV. It checks the generated key’s KeyInfo when TEE or StrongBox backing is policy-critical. If the requested level is unavailable, the product policy decides whether to accept a lower level, require re-authentication, or disable the feature. A backup restore may bring back ciphertext without the non-transferable app key, so the app needs a key-loss recovery path. This is a design walkthrough; the hardware path requires device testing.

## Explanation in Arabic

`Android Keystore` بيدي التطبيق Alias ومفتاح للاستخدام في Crypto Operations من غير ما يسلّمه Raw Key Material. دي حماية من الاستخراج عبر API التطبيق، لكنها لوحدها مش دليل إن المفتاح جوه عتاد آمن. مستوى الحماية ممكن يكون Software أو `TEE` أو `StrongBox` حسب الجهاز ونوع المفتاح والإعدادات؛ لو الـ Threat Model محتاج Hardware، افحص `KeyInfo.securityLevel` للمفتاح الفعلي.

`TEE` بيشتغل في بيئة معزولة على نفس الـ SoC، و`StrongBox` في Secure Hardware منفصل لو الجهاز بيدعمه. دعم StrongBox مش مضمون، وبعض Algorithms أو Key Sizes أو Auth Policies ممكن ما تتنفذش عليه. الـ Keystore بيقلل فرصة استخراج المفتاح، لكن App متخترق ممكن تطلب منه استخدام المفتاح أو تقرأ Plaintext الناتج. لذلك لا تجعل وجود Keystore بديل عن Backend Authorization أو Device/Request Verification.

ممكن تربط استخدام المفتاح بـ User Authentication، لكن إبطال المفتاح عند تغيير Biometrics يعتمد على إعدادات زي `setInvalidatedByBiometricEnrollment` ونوع الـ Auth. ومفاتيح التطبيق عادة لا تنتقل مع Backup؛ البيانات المشفرة بمفتاحها تحتاج Recovery Plan.

## Practical walkthrough

تطبيق بيحفظ Token محليًا: يطلب من `AndroidKeyStore` توليد AES Key باسم Alias محدد، ويشفر الـ Token بـ AES-GCM مع IV جديد لكل تشفير. بعد التوليد يفحص `KeyInfo` لو سياسة المنتج تتطلب TEE أو StrongBox. لو الجهاز ما يحققش السياسة، القرار يبقى واضح: امنع Feature معينة أو اطلب Re-authentication بدل ما تدّعي Hardware Protection. لو المفتاح ضاع بعد Reinstall أو Restore، تجاهل Ciphertext القديم وارجع لمسار تسجيل الدخول؛ متفترضش إن Backup نقل الـ Key.

## Why it matters and how it works

KeyGenParameterSpec limits purposes, algorithms, user-auth requirements and, where supported, hardware properties. AndroidKeyStore mediates operations without exporting key material. Inspect KeyInfo/security level when a hardware guarantee is part of the threat model; do not infer hardware backing merely from the provider name.

## Worked example

Illustrative Android/Kotlin example (not executed in the JVM lab) for a previously generated `AndroidKeyStore` AES key on API 23+ with `compileSdk` 31+. It checks whether this **specific** key is hardware backed; the API 31 branch reports TEE or StrongBox, while earlier devices use the older boolean. The app must still define what to do when hardware backing is unavailable.

```kotlin
import android.os.Build
import android.security.keystore.KeyInfo
import android.security.keystore.KeyProperties
import javax.crypto.SecretKey
import javax.crypto.SecretKeyFactory

fun isHardwareBacked(key: SecretKey): Boolean {
    val factory = SecretKeyFactory.getInstance(key.algorithm, "AndroidKeyStore")
    val info = factory.getKeySpec(key, KeyInfo::class.java) as KeyInfo
    return if (Build.VERSION.SDK_INT >= 31) {
        info.securityLevel == KeyProperties.SECURITY_LEVEL_TRUSTED_ENVIRONMENT ||
            info.securityLevel == KeyProperties.SECURITY_LEVEL_STRONGBOX
    } else {
        @Suppress("DEPRECATION")
        val backed = info.isInsideSecureHardware
        backed
    }
}
```

This reports key storage properties; it does not prove the current app process or user request is trustworthy.

## Trade-offs and decision criteria

Hardware-backed keys can raise the cost of extraction, but availability, authentication behavior and StrongBox support vary. Server-held secrets avoid shipping a secret at all; local encryption is useful only for data that must reside locally.

## Failure modes

Assuming a Keystore key survives reinstall or backup restore breaks decryption: app keys are ordinarily removed with the app and not transferred. Another error is using AES-GCM with a repeated IV under the same key. Test key loss and rotate with versioned ciphertext.

## Production perspective

A banking app uses Keystore for a local token-encryption key, verifies device capability only if policy requires it, excludes incompatible encrypted blobs from backup, and falls back to re-authentication after key loss. Backend token revocation and authorization remain decisive.

## Interview answer — short

Android Keystore lets an app use a key without exporting its raw bytes. Hardware backing is a separate property: a key may be software protected, TEE backed, or StrongBox backed depending on the device and configuration. Verify the generated key with KeyInfo when the level matters. A compromised app may still invoke the key and observe plaintext, so Keystore does not replace server authorization or key-loss recovery.

## Interview answer — structured

Android Keystore reduces key extraction risk by mediating cryptographic operations without returning raw key material to the app. But “AndroidKeyStore” is not proof that the key lives in secure hardware. Depending on device support and requested properties, the generated key may be software protected, TEE backed, or StrongBox backed. I check KeyInfo for the real key if policy requires hardware.

For a locally encrypted token, I use an authenticated mode such as AES-GCM with a fresh IV for each encryption. If StrongBox is unavailable, fallback is an explicit security-policy decision. I also test restore or reinstall, because encrypted data may outlive the key needed to decrypt it.

A compromised app can still ask Keystore to use a non-exportable key and read plaintext or signatures. Therefore the backend must authorize sensitive requests and handle revocation; hardware backing is a defense for key material, not a guarantee that the client request is trustworthy.

## Interview answer — deep senior

The Android Keystore API exposes key handles and constrains purposes and authentication without exporting raw key material into the application process. This is distinct from hardware backing. The actual security level can be software, TEE, or StrongBox, subject to device and algorithm support. Inspect KeyInfo on the generated key. If a remote server needs evidence of hardware properties, validate key attestation server-side rather than trusting a client-supplied flag.

The threat boundary matters: a compromised app process may fail to extract key bytes but may still request a permitted signing or decryption operation, or read plaintext before encryption and after decryption. User-authentication gating can limit key use; biometric-enrollment invalidation depends on the key policy, authentication type, and settings such as setInvalidatedByBiometricEnrollment. It is not correct to claim every authenticated key is invalidated whenever biometrics change.

For locally encrypted data, use a sound mode such as AES-GCM with a unique IV per key operation, version the ciphertext, and plan for key loss after restore or reinstall. StrongBox might be unsupported or lack an algorithm or policy; fallback to TEE or software must follow a documented risk decision. Keystore protects key material, while backend authorization, token revocation, and correct request binding remain the decisive controls for payment or account actions.

## How to answer in the interview

- **Why:** key extraction and key use are different threats.
- **How:** generate a nonexportable key, inspect actual security level, and version ciphertext.
- **Trade-off:** hardware backing varies by device and key policy.
- **Failure case:** restored ciphertext has no matching Keystore key.
- **Production solution:** test key-loss recovery and keep authorization server-side.

## Deep-dive talking points

Explain where Keystore key material is generated and used, when hardware protection is available, and what a compromised client can still observe.

## Follow-up questions

- **Interviewer:** "Does AndroidKeyStore imply hardware backing?"
  **Answer:** "No. Check KeyInfo on the generated key when TEE or StrongBox is required."

- **Interviewer:** "Can a compromised app use a non-exportable key?"
  **Answer:** "Yes, if its permitted operations are available. Non-exportability limits extraction, not all misuse; the backend still authorizes requests."

- **Interviewer:** "Are all biometric-gated keys invalidated on enrollment changes?"
  **Answer:** "No. The behavior depends on the key’s authentication policy and setInvalidatedByBiometricEnrollment; test the exact configuration."

## Self-check rubric

Can I distinguish key material from ciphertext, state hardware limits, describe AES-GCM IV handling, and explain restore and server-trust boundaries?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — extraction prevention and limitations.
- [KeyInfo API](https://developer.android.com/reference/android/security/keystore/KeyInfo) — security levels.
- [KeyGenParameterSpec.Builder](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder) — StrongBox and authentication policy.
- [Key attestation](https://source.android.com/docs/security/features/keystore/attestation) — remote evidence.

Technically reviewed against primary documentation on 2026-10-19.
