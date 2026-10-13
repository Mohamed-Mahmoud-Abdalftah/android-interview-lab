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

## Explanation in Arabic

Android Keystore بيولّد أو يستورد cryptographic keys تحت alias، والـapp يطلب عملية تشفير أو توقيع بدل ما يحتفظ بالـraw key في ملف. بعض الأجهزة تنفذ العملية داخل TEE أو StrongBox، لكن ده مش مضمون لكل key أو device. الـplaintext بيفضل يظهر للـapp وقت الاستخدام؛ Keystore ما بتحولش الجهاز المخترق إلى trusted client.

## Practical walkthrough

لو app خزن ciphertext ومعاه alias لمفتاح في Keystore، المفتاح ما يطلعش كـraw bytes للـapp. بس وقت فك التشفير الـplaintext يدخل memory، وroot/hooking ممكن يراقبه. افحص `KeyInfo` لو hardware backing مطلوب؛ ما تفترضش StrongBox موجود في كل جهاز. لو المفتاح اتفقد بعد restore، عندك مسار re-login أو استعادة موثوقة بدل crash متكرر.

## Why it matters and how it works

KeyGenParameterSpec limits purposes, algorithms, user-auth requirements and, where supported, hardware properties. AndroidKeyStore mediates operations without exporting key material. Inspect KeyInfo/security level when a hardware guarantee is part of the threat model; do not infer hardware backing merely from the provider name.

## Worked example

Android/Kotlin example for a previously generated `AndroidKeyStore` AES key on API 23+ with `compileSdk` 31+. It checks whether this **specific** key is hardware backed; the API 31 branch reports TEE or StrongBox, while earlier devices use the older boolean. The app must still define what to do when hardware backing is unavailable.

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

“Android Keystore lets an app use keys without exporting their key material. Hardware backing may strengthen that protection, but I check actual capabilities and still design ciphertext format, backup, rotation, and recovery.”

## Interview answer — structured

“Android Keystore lets an app perform cryptographic operations with a key that it cannot export as raw material. Some keys are protected in TEE or StrongBox, but I verify the actual key properties on supported devices. For stored ciphertext I still need an IV, authenticated format, version, backup and recovery plan. The app sees plaintext when it uses the key, so Keystore reduces extraction risk without making a compromised runtime trustworthy.”

## Interview answer — deep senior

“I use Keystore to keep cryptographic key material nonexportable and to restrict operations, then verify whether a particular generated key is hardware backed rather than assuming every device has StrongBox. The app still sees plaintext when it uses the key, so runtime compromise remains in scope. I would version the ciphertext envelope, use a fresh IV for each AES-GCM encryption, and test restore and key invalidation. A restored token with no usable key should lead to reauthentication. Keystore protects one part of the data flow; the backend still decides whether a transfer is authorized. For a payment token store, I would inspect the generated key's security level on the supported device matrix and decide whether a software-backed key is acceptable for that specific risk. If the product requires hardware assurance, unsupported devices need a documented fallback or eligibility rule. I would never use key nonexportability to claim that a hooked process cannot ask Keystore to decrypt data or sign on its behalf.”

## How to answer in the interview

- **Why:** key extraction and key use are different threats.
- **How:** generate a nonexportable key, inspect actual security level, and version ciphertext.
- **Trade-off:** hardware backing varies by device and key policy.
- **Failure case:** restored ciphertext has no matching Keystore key.
- **Production solution:** test key-loss recovery and keep authorization server-side.

## Deep-dive talking points

Explain where Keystore key material is generated and used, when hardware protection is available, and what a compromised client can still observe.

## Follow-up questions

- [SEC-11](../sec-11/): What must be stored beside AES-GCM ciphertext? **Answer:** a version, unique IV and authenticated output, with recovery policy.
- [SEC-13](../sec-13/): What if a key disappears? **Answer:** classify the protected value and invoke a designed reissue or recovery path.

## Self-check rubric

Can I distinguish key material from ciphertext, state hardware limits, describe AES-GCM IV handling, and explain restore and server-trust boundaries?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key protection and operations.
- [KeyGenParameterSpec](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec) — key constraints.
- [KeyInfo API](https://developer.android.com/reference/android/security/keystore/KeyInfo) — hardware security level and legacy query.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
