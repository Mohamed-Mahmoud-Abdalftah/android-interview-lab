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

## Concept and technical explanation

Managing cryptographic keys in production Android applications requires designing for four critical lifecycle events: key invalidation, key rotation, device backup/restore, and application reinstallation. Key invalidation occurs primarily when Keystore keys bound to user authentication (via setUserAuthenticationRequired) are permanently invalidated by the platform (KeyPermanentlyInvalidatedException) when the user removes their lockscreen PIN/password or enrolls a new biometric fingerprint. Key rotation is the operational discipline of transitioning encrypted data from an older cryptographic key to a newer key version without data loss, accomplished using versioned ciphertext envelopes. Device backups present a major security hazard: by default, Android Auto Backup may copy encrypted files or preferences to Google Drive; however, because Keystore keys are tied to physical hardware and are never included in backups, restored files on a new device or after reinstallation become permanently undecryptable. Applications must explicitly disable auto-backup for encrypted storage via android:allowBackup="false" or data extraction rules.

## Practical walkthrough (English)

Handling key invalidation and configuring backup exclusion rules:
```xml
<!-- 1. Exclude encrypted storage from Android Auto Backup in data_extraction_rules.xml -->
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <!-- Exclude encrypted SharedPreferences / Keystore-dependent files -->
        <exclude path="shared_prefs/secure_session.xml" />
        <exclude path="databases/encrypted_vault.db" />
    </cloud-backup>
    <device-transfer>
        <exclude path="shared_prefs/secure_session.xml" />
        <exclude path="databases/encrypted_vault.db" />
    </device-transfer>
</data-extraction-rules>
```
Graceful handling of KeyPermanentlyInvalidatedException in Kotlin:
```kotlin
// 2. Catching key invalidation when biometrics change
fun executeBiometricDecryption(cipher: Cipher, encryptedData: ByteArray): Result<ByteArray> {
    return try {
        Result.success(cipher.doFinal(encryptedData))
    } catch (e: KeyPermanentlyInvalidatedException) {
        // Biometrics were altered: lockscreen changed or new fingerprint added!
        // 1. Wipe orphaned local ciphertext
        clearOrphanedCredentials()
        // 2. Request user to re-authenticate with primary credentials / password
        Result.failure(SecurityException("Cryptographic key invalidated due to security changes", e))
    }
}
```

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

We handle key invalidation by catching KeyPermanentlyInvalidatedException when lockscreen or biometric enrollments change, clearing unusable ciphertext, and prompting re-authentication. For backups and reinstalls, because Keystore keys never transfer across devices, we explicitly exclude encrypted files from Android Auto Backup to prevent unrecoverable decryption failures.

## Interview answer — structured

A resilient mobile security architecture plans for inevitable key lifecycle events rather than assuming cryptographic keys live indefinitely.
Key invalidation occurs when biometric-bound Keystore keys detect that lockscreen security has changed, such as when a user adds a new fingerprint or disables their device PIN.
The platform throws a KeyPermanentlyInvalidatedException, preventing an unauthorized person who enrolled a fingerprint on a borrowed phone from unlocking the original user's sensitive data.
Applications must catch this exception, wipe the now-unusable local ciphertext, and prompt the user to re-authenticate using their master password.
Key rotation involves persisting a version header alongside encrypted data; when a key rotates, the application decrypts using the old key and re-encrypts using the new key version within an atomic transaction.
Finally, handling backups and reinstalls requires strict isolation.
Android Keystore keys are bound to device hardware and do not survive app reinstallation or cloud backup restore.
We configure XML data extraction rules to exclude encrypted preferences and databases from cloud backups, ensuring that restored apps start with a clean state rather than crashing on orphaned ciphertext.

## Interview answer — deep senior

Production cryptographic engineering distinguishes itself by anticipating failure modes in identity and device transitions.
When keys are configured with setUserAuthenticationRequired, the Android Keymaster daemon binds key usability to the hardware biometric enrollment database.
If an attacker or unauthorized user adds their own fingerprint in system settings, the system invalidates all existing keys to maintain non-repudiation and prevent account takeover.
When KeyPermanentlyInvalidatedException is thrown, handling it gracefully is paramount: crashing the app or silently looping produces a fatal user experience.
The app must intercept the exception, purge the orphaned ciphertext, inform the user with transparent security rationale, and require a full backend challenge with password or multi-factor authentication to establish a new key pair.
The interaction between Android Keystore and Android Auto Backup is another notorious trap.
When users migrate to a new phone, Google's backup system automatically transfers files unless explicitly restricted.
However, because hardware Keystore keys cannot be backed up, the restored application inherits encrypted files on the new phone with no valid key in its new Keystore to decrypt them.
This produces silent decryption failures or startup crashes.
We eliminate this vulnerability by configuring android:dataExtractionRules in Android 12 and later, explicitly excluding all sensitive databases, credentials, and token files from cloud backups and device-to-device transfers.
If user data must be restored on a new device, we design a server-assisted key escrow or client re-sync architecture rather than relying on OS-level file transfers.

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
