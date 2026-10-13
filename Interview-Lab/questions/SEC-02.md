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

ما هو Android Keystore وما هو التخزين المدعوم عتادياً (Hardware-Backed Key Storage - TEE / StrongBox)؟

1. ما هو Android Keystore ولماذا يختلف عن التخزين العادي؟
   - في التشفير العادي، إذا أنشأت مفتاح تشفير في كود Kotlin، فإن مصفوفة البايتات (`ByteArray`) الخاصة بالمفتاح تكون موجودة في ذاكرة الـ RAM الخاصة بالتطبيق. إذا كان الجهاز Rooted، يمكن للمهاجم استخراج المفتاح من الـ RAM بسهولة!
   - **Android Keystore System** صُمم لحل هذه المشكلة جذرياً: **المفتاح لا يدخل ذاكرة التطبيق إطلاقاً (Non-Exportable Key Material)**.
   - يتم إنشاء المفتاح وحفظه داخل مخزن مشفر خاص بالنظام. التطبيق لا يملك المفتاح؛ بل يملك فقط مرجعاً له (Alias/Handle). عندما يريد التطبيق تشفير أو فك تشفير نص، يرسل النص إلى الـ Keystore، فيقوم الـ Keystore بإجراء التشفير داخلياً وإعادة النص المشفر للتطبيق دون أن يرى التطبيق بايتات المفتاح الحقيقية أبداً!

2. مستويات الأمان العتادي (Hardware-Backed TEE vs. StrongBox):
   - **Software Fallback (برمجي)**: في الهواتف القديمة أو المحاكيات، يُخزن المفتاح برمجياً (أقل أماناً).
   - **TEE (Trusted Execution Environment)**: بيئة تنفيذ معزولة عتادياً تعمل على معالج مستقل (مثل ARM TrustZone) داخل نفس شريحة الـ SoC. نظام Android الرئيسي (Linux) لا يملك وصولاً لذاكرة الـ TEE.
   - **StrongBox Keymaster (أعلى درجات الأمان)**: شريحة عتادية مادية منفصلة تماماً ومقاومة للتلاعب الفيزيائي (Dedicated Secure Hardware / HSM مثل شريحة Titan M في هواتف Pixel). تمتلك معالجها الخاص وذاكرتها الخاصة وساعتها الخاصة.

## Practical walkthrough

توليد مفتاح AES-256 مشفر مدعوم عتادياً داخل Android Keystore مع دعم StrongBox:
```kotlin
class KeystoreManager {
    private val KEY_ALIAS = "user_auth_secret_key"
    private val ANDROID_KEYSTORE = "AndroidKeyStore"

    fun getOrCreateSecretKey(context: Context): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        
        // 1. التحقق مما إذا كان المفتاح موجوداً مسبقاً:
        if (keyStore.containsAlias(KEY_ALIAS)) {
            val entry = keyStore.getEntry(KEY_ALIAS, null) as KeyStore.SecretKeyEntry
            return entry.secretKey
        }

        // 2. توليد مفتاح AES-256 جديد غير قابل للاستخراج داخل العتاد:
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        val keyGenSpec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM) // الوضع الآمن Authenticated Encryption
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            // طلب تخزين المفتاح في StrongBox المادي إذا كان عتاد الجهاز يدعمه (Android 9+):
            .setIsStrongBoxBacked(context.packageManager.hasSystemFeature(PackageManager.FEATURE_STRONGBOX_KEYSTORE))
            .build()

        keyGenerator.init(keyGenSpec)
        return keyGenerator.generateKey() // المفتاح تم إنشاؤه داخل العتاد ولا يمكن تصديره أبداً!
    }
}
```

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

Android Keystore generates and stores cryptographic keys in isolated environments so key material is never exposed in the app's RAM. Hardware-backed storage leverages a TEE (ARM TrustZone) or a dedicated StrongBox chip (hardware HSM), preventing key extraction even if the device's Android OS or Linux kernel is fully rooted.

## Interview answer — structured

The Android Keystore system fundamentally changes key management by making cryptographic key material **non-exportable**:

1. **Non-Exportable Key Material**: In software cryptography, AES keys exist in JVM heap memory as raw byte arrays, easily dumpable via Frida or memory dump tools on rooted devices. With Android Keystore, the private/secret key never enters the application process. The app receives an opaque handle (`Key`), delegating encryption/decryption operations to system security daemons.

2. **Hardware-Backed Isolation Tiers**:
   - **TEE (Trusted Execution Environment)**: Runs on the primary SoC using hardware virtualization (e.g., ARM TrustZone). Cryptographic operations run under a microkernel isolated from the Android Linux kernel.
   - **StrongBox Keymaster (API 28+)**: A physically separate, tamper-resistant hardware security module (HSM, such as Google Titan M or Samsung Knox Vault). StrongBox has its own dedicated CPU, secure storage, and true random number generator, resisting physical hardware side-channel attacks.

3. **Security Boundary Distinction**: Hardware-backed Keystore protects **keys from extraction**, but it does not protect the plaintext data *after* decryption in application RAM.

## Interview answer — deep senior

How does Keymaster/KeyMint verify hardware backing programmatically?

Senior engineers inspect key properties using the `KeyFactory` / `SecretKeyFactory` info spec:

```kotlin
val factory = SecretKeyFactory.getInstance(key.algorithm, "AndroidKeyStore")
val keyInfo = factory.getKeySpec(key, KeyInfo::class.java) as KeyInfo
val isInsideSecureHardware = keyInfo.isInsideSecureHardware
val securityLevel = keyInfo.securityLevel // SECURITY_LEVEL_TRUSTED_ENVIRONMENT or STRONGBOX
```

If `isInsideSecureHardware` returns false, the key is stored in software (legacy software Keymaster emulation), which is vulnerable to kernel-level exploitation on rooted devices. In high-assurance fintech and banking apps, policies can mandate that high-value operations proceed only when `keyInfo.isInsideSecureHardware == true`.

## How to answer in the interview

- **Why:** key extraction and key use are different threats.
- **How:** generate a nonexportable key, inspect actual security level, and version ciphertext.
- **Trade-off:** hardware backing varies by device and key policy.
- **Failure case:** restored ciphertext has no matching Keystore key.
- **Production solution:** test key-loss recovery and keep authorization server-side.

## Deep-dive talking points

Explain where Keystore key material is generated and used, when hardware protection is available, and what a compromised client can still observe.

## Follow-up questions

- **Interviewer:** "Can you backup and restore Android Keystore keys to Google Drive?"
  **Answer:** "No. Hardware-backed Keystore keys are tied physically to the specific device's secure hardware and can never be exported or restored onto another device."

- **Interviewer:** "What happens if a user removes their device lockscreen PIN?"
  **Answer:** "Keys generated with `.setUserAuthenticationRequired(true)` are permanently invalidated and deleted by the Keystore system."

## Self-check rubric

Can I distinguish key material from ciphertext, state hardware limits, describe AES-GCM IV handling, and explain restore and server-trust boundaries?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key protection and operations.
- [KeyGenParameterSpec](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec) — key constraints.
- [KeyInfo API](https://developer.android.com/reference/android/security/keystore/KeyInfo) — hardware security level and legacy query.

Technically reviewed against primary documentation on 2026-10-13.
