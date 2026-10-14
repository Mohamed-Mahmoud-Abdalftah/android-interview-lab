---
id: "SEC-13"
question: "How do you handle key invalidation, key rotation, backups, and reinstall?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 310
editorial_status: "reviewed"
---

# SEC-13

## Original interview question

How do you handle key invalidation, key rotation, backups, and reinstall?

## What the interviewer evaluates

- Key invalidation and rotation as explicit data-lifecycle events.
- Backup/reinstall behavior and replaceable versus irreplaceable data.

## Explanation in Arabic

كيف تتعامل مع إبطال المفاتيح (Key Invalidation)، تدوير المفاتيح (Key Rotation)، النسخ الاحتياطي (Auto Backup)، وإعادة التثبيت (Reinstall)؟

1. إبطال المفاتيح (Key Invalidation) عبر البصمة:
   - عند إنشاء مفتاح في Keystore مع خاصية `setInvalidatedByBiometricEnrollment(true)`، فإن إضافة أو حذف أي بصمة جديدة على مستوى الهاتف يقوم **بإبطال المفتاح عتادياً وبشكل نهائي**!
   - أي محاولة استخدام لاحقة للمفتاح سترمي `KeyPermanentlyInvalidatedException`. هذا يحمي التطبيق البنكي إذا قام شخص يعرف رمز قفل الشاشة بتسجيل بصمة إصبعه على هاتف الضحية.

2. تدوير المفاتيح (Key Rotation):
   - يجب أن تدعم المعمارية إصدارات متعددة للمفاتيح (`secret_key_v1`, `secret_key_v2`).
   - عند تدوير المفتاح، يتم إنشاء المفتاح الجديد، وقراءة البيانات القديمة وفك تشفيرها بالمفتاح القديم، ثم إعادة تشفيرها بالمفتاح الجديد، وحذف المفتاح القديم.

3. خطر النسخ الاحتياطي التلقائي (Auto Backup Hazard):
   - ميزة Android Auto Backup (`allowBackup="true"`) تقوم برفع ملفات التطبيق الداخلية إلى Google Drive.
   - **الكارثة**: ملفات البيانات المشفرة يتم رفعها، ولكن **مفاتيح Android Keystore لا تغادر الشريحة العتادية للهاتف أبداً**!
   - عندما يشتري المستخدم هاتفاً جديداً ويسترجع النسخة الاحتياطية، توجد الملفات المشفرة ولكن المفتاح العتادي غير موجود، فتفشل عملية فك التشفير برمي `KeyNotFoundException` أو انهيار التطبيق!
   - **الحل**: استثناء الملفات المشفرة عبر `backup_rules.xml` أو تعطيل النسخ الاحتياطي كلياً للتطبيقات الحساسة (`android:allowBackup="false"`).

## Practical walkthrough

معالجة إبطال المفاتيح برمجياً واستثناء الملفات المشفرة من الـ Auto Backup:
```kotlin
// 1. التعامل مع استثناء إبطال المفتاح العتادي KeyPermanentlyInvalidatedException:
class BiometricCryptoRepository(
    private val keyStore: KeyStore,
    private val sessionManager: SessionManager
) {
    fun getEncryptCipher(keyAlias: String): Cipher? {
        return try {
            val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
            Cipher.getInstance("AES/GCM/NoPadding").apply {
                init(Cipher.ENCRYPT_MODE, secretKey)
            }
        } catch (e: KeyPermanentlyInvalidatedException) {
            // تم تسجيل بصمة جديدة على الجهاز! المفتاح أُبطل عتادياً لحماية الحساب
            keyStore.deleteEntry(keyAlias)
            sessionManager.forceLogoutDueToBiometricChange()
            null
        }
    }
}
```

```xml
<!-- 2. منع رفع الملفات المشفرة في Android Auto Backup داخل res/xml/backup_rules.xml -->
<data-extraction-rules>
    <cloud-backup>
        <!-- استثناء مجلد الداتابيز وقيم التوكنز المشفرة لأن المفاتيح العتادية لن تنتقل للجهاز الجديد -->
        <exclude path="datastore/secure_tokens.preferences_pb" />
        <exclude domain="database" path="encrypted_app_db" />
    </cloud-backup>
</data-extraction-rules>
```

## Why it matters and how it works

Persist a ciphertext format version and key identifier. While the old key works, decrypt and write the new envelope atomically before deleting old data. If the old key no longer works, no local algorithm can reconstruct plaintext. Android backup policy must align with Keystore non-transferability.

## Worked example

When upgrading a token store, read old token, encrypt under alias `session-v2`, verify decryption, then switch the persisted active version. If process death occurs before switch, keep the old record readable. If neither key works, delete only the unusable token and require authenticated renewal.

## Trade-offs and decision criteria

Keeping old keys supports gradual migration but extends exposure and complicates cleanup. Eager rotation simplifies final state but can lengthen startup and fail mid-migration. Reissuable tokens are easier than locally created data without a server copy.

## Failure modes

Silently replacing a failed decrypt with an empty token hides corruption and may loop on refresh. Blindly restoring encrypted preferences to a new install can strand data. Surface a safe re-authentication state and record redacted diagnostics.

## Production perspective

For a finance app, test fresh install, reinstall, cloud restore, device transfer, biometric enrollment changes where auth-bound keys are used, and interrupted migration. Backend sessions can be revoked and reissued; payment history is recovered from server records.

## Interview answer — short

Biometric Keystore keys are permanently invalidated via KeyPermanentlyInvalidatedException when new biometrics are enrolled. In backup scenarios, hardware Keystore keys never migrate between devices; therefore, encrypted files must be excluded via backup_rules.xml to avoid decryption crashes upon reinstall. Key rotation requires versioned aliases and background re-encryption.

## Interview answer — structured

Managing the cryptographic key lifecycle across OS events requires planning for three distinct operational hazards.

First, with Biometric Key Invalidation, when keys are generated with `setInvalidatedByBiometricEnrollment(true)`, the hardware invalidates the key if the device user adds, removes, or modifies biometric enrollments. Future cryptographic operations throw `KeyPermanentlyInvalidatedException`. Production code must catch this specific exception, purge local biometric credentials, and route the user to re-authenticate with primary credentials (password/OTP). Next, with The Auto Backup / Reinstall Pitfall, Android Cloud Auto Backup transfers private app files to Google Drive, but Keystore hardware keys are physically locked to the device's TEE/SE and are never exported. When restored on a new device, encrypted files exist without the decryption key, causing permanent decryption failure. Apps must exclude encrypted databases and DataStore files in `backup_rules.xml` or disable `android:allowBackup="false"`.
Finally, production key rotation uses versioned aliases (e.g., `key_alias_v2`). The app reads data encrypted with `v1`, decrypts it, generates `v2` in Keystore, re-encrypts the payload, updates an encrypted metadata pointer, and securely destroys `v1`.


## Interview answer — deep senior

From an enterprise security posture, handling key invalidation and restore states is a critical architectural requirement.

First, with Device Reinstall Lifecycle, when an app is uninstalled and reinstalled on the same physical device, Keystore keys are permanently wiped by the Android OS package manager. Any residual orphaned data (e.g., stored on external scoped storage or synced back from cloud backups) cannot be decrypted. The app must detect a fresh install lifecycle, re-initialize its cryptographic Keystore keysets, and request a fresh session token from the backend. Next, with Zero-Downtime Key Rotation Strategy, for server-synced local data, client key rotation should be triggered via backend-driven feature flags or rotation metadata headers. When the server signals a key rollover, a background WorkManager job performs atomic read-decrypt-reencrypt operations on local stores in chunks, preventing blocking operations during critical user flows.
Finally, with Defensive Exception Handling, never treat `KeyStoreException` as a generic runtime failure. Differentiate between `UserNotAuthenticatedException` (biometric prompt required), `KeyPermanentlyInvalidatedException` (credential enrollment changed), and hardware communication errors (`KeyStoreConnectException`), taking deterministic recovery actions for each.


## How to answer in the interview

- **Why:** key lifecycle outlives a single encryption call.
- **How:** version aliases and ciphertext, migrate atomically, then retire old keys.
- **Trade-off:** keeping old readers supports rollback but extends key exposure.
- **Failure case:** partial migration or backup without Keystore key.
- **Production solution:** exercise reinstall, restore, invalidation, and crash recovery tests.

## Deep-dive talking points

Build a decision table for key invalidation, biometric enrollment changes, backup restore and reinstall; separate revocable tokens from irreplaceable user data.

## Follow-up questions

- **Interviewer:** "What happens if a user disables their screen lock (PIN/Password) on a device with biometric keys?"
  **Answer:** "All Keystore keys requiring device credentials or user authentication are instantly destroyed and wiped by the Android Keymaster daemon."

- **Interviewer:** "Why does setting android:allowBackup="false" help fintech applications?"
  **Answer:** "It blocks adb backup extraction (`adb backup`) and Google Drive cloud backups, preventing local database extraction on developer-enabled devices."

## Self-check rubric

Can I explain rotation ordering, crash recovery, invalidation, backup/reinstall and data-class-specific recovery?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key behavior.
- [Android Auto Backup](https://developer.android.com/identity/data/autobackup) — restore and exclusion rules.

Technically reviewed against primary documentation on 2026-10-13.
