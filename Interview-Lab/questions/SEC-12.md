---
id: "SEC-12"
question: "What should you know about the deprecated EncryptedSharedPreferences API?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 309
editorial_status: "reviewed"
---

# SEC-12

## Original interview question

What should you know about the deprecated EncryptedSharedPreferences API?

## What the interviewer evaluates

- Awareness that the AndroidX `EncryptedSharedPreferences` class is deprecated in the current API reference.
- Separation of app storage format, Keystore key protection, and server-side authority.
- Migration and recovery thinking: existing ciphertext, invalidated keys, backups, and logout.

## Explanation in Arabic

ما هي حقيقة مكتبة `EncryptedSharedPreferences` ومكتبة `security-crypto`، ولماذا تم إيقافها (Deprecated) وما هي البدائل الحديثة؟

1. ما كانت فكرة `EncryptedSharedPreferences`؟
   - كانت جزءاً من مكتبة `androidx.security:security-crypto` وتعتمد على مكتبة Google Tink لتشفير مفاتيح وقيم الـ SharedPreferences تلقائياً، بحيث يتم تشفير المفاتيح باستخدام خوارزمية SIV-AES ويتم تشفير القيم باستخدام AES-GCM، مع حفظ مفتاح رئيسي (MasterKey) في الـ Android Keystore.

2. لماذا أصبحت كابوساً برمجياً وتم اعتبارها Deprecated؟
   - **معدل انهيارات كارثي في الإنتاج (High Crash Rates)**: مكتبة Tink كانت تعتمد على حفظ Keyset مشفر داخل ملف xml. على العديد من أجهزة سامسونج وشاومي وعند حدوث تحديثات للنظام (OTA) أو استعادة نسخ احتياطي، كان الـ Keystore يفقد المفتاح أو يتلف ملف الـ Keyset، مما يسبب انهيارات غير قابلة للإصلاح مثل `SecurityException`, `DeadObjectException`, `CleartextKeysetException`, و`GeneralSecurityException`.
   - **أداء ضعيف وتجميد للـ UI**: كانت تقرأ وتفك تشفير الـ Keyset بالكامل وتستدعي الـ Keystore عبر IPC عند تهيئة التطبيق، مما يسبب Jank أو ANR إذا تمت تهيئتها على الـ Main Thread.
   - **توقف التطوير الرسمي (Maintenance Mode)**: جوجل توقفت عن صيانة وتحديث المكتبة لفترة طويلة وأعلنت إيقافها لاحقاً لعدم استقرارها الهندسي.

3. ما هي البدائل المعتمدة في بيئات الإنتاج الحديثة؟
   - **Android Jetpack DataStore (مع تشفير مخصص)**: استخدام DataStore مع مُشفّر مخصص (Custom Serializer) يعتمد مباشرة على Android Keystore الخام.
   - **SQLCipher مع Room Database**: لتخزين البيانات المنظمة الحساسة بقاعدة بيانات مشفرة بالكامل.
   - **التشفير المباشر عبر Keystore AES-GCM**: تشفير التوكنز فقط يدوياً قبل حفظها في DataStore أو تخزينها.

## Practical walkthrough

بديل حديث ومستقر: استخدام Jetpack Preferences DataStore مع تشفير القيم عبر Keystore الخام بدون الاعتماد على المكتبة التالفة:
```kotlin
// ❌ النمط القديم المليء بالمشاكل والانهيارات:
// val sharedPrefs = EncryptedSharedPreferences.create(context, "secrets", masterKey, ...)
// يسبب أعطالاً مفاجئة في أجهزة الإنتاج: KeyPermanentlyInvalidatedException أو Keystore crashes!

// ✅ المعمارية الحديثة: DataStore مع تشفير التوكنز عبر Android Keystore مباشرة وبشكل آمن:
class SecureTokenStorage(
    private val dataStore: DataStore<Preferences>,
    private val cryptoManager: KeystoreSecretStorage // كلاس Keystore AES-GCM موثوق ومفحوص
) {
    private val TOKEN_KEY = stringPreferencesKey("encrypted_auth_token")

    suspend fun saveAuthToken(token: String) {
        val encryptedBytes = cryptoManager.encrypt(token.toByteArray(Charsets.UTF_8))
        val base64Ciphertext = Base64.encodeToString(encryptedBytes, Base64.NO_WRAP)
        
        dataStore.edit { preferences ->
            preferences[TOKEN_KEY] = base64Ciphertext
        }
    }

    fun getAuthToken(): Flow<String?> = dataStore.data.map { preferences ->
        val base64Ciphertext = preferences[TOKEN_KEY] ?: return@map null
        try {
            val encryptedBytes = Base64.decode(base64Ciphertext, Base64.NO_WRAP)
            val decryptedBytes = cryptoManager.decrypt(encryptedBytes)
            String(decryptedBytes, Charsets.UTF_8)
        } catch (e: Exception) {
            // إذا تلف المفتاح أو تم مسحه، التعامل بمرونة وحذف التوكن التالف بدون انهيار التطبيق
            null
        }
    }
}
```

## Why it matters and how it works

The library encrypted preference keys and values using a master key, commonly backed by Android Keystore. Its deprecation is an API status, not proof that existing stored values have stopped working. Keystore controls key generation and allowed operations; the app still owns ciphertext format, IV handling, backup policy, rotation, and error recovery. Client storage cannot serve as the trust boundary for authorization or payment decisions. Backup restoration may bring ciphertext without the original Keystore key, so recovery must be designed.

## Worked example

For an app upgrading from the deprecated preference file, first inventory exactly what is stored. A refresh token is better treated as replaceable: read and migrate only while the old key works, write the new format, verify a round trip, then remove the old entry; on key loss, clear the unusable token and require sign-in. The following Android snippet shows **only** creation of an AES key in Android Keystore. It is not a complete encryption or migration implementation; a real design must specify AES-GCM IV uniqueness, ciphertext format, authentication tags, backup exclusions, and key-rotation tests.

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import javax.crypto.KeyGenerator

fun createStorageKey(alias: String) {
    val generator = KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore"
    )
    generator.init(
        KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .build()
    )
    generator.generateKey()
}
```

## Trade-offs and decision criteria

Use Keystore-backed encryption only where the threat model warrants local confidentiality and operational recovery is designed. Plain preferences or DataStore can be appropriate for non-secret settings; neither is a safe place for embedded API secrets. Minimize sensitive data retained on-device. Hardware-backed protection availability varies by device; check actual key properties if that matters to the threat model. A token that can be revoked and reissued differs from irreplaceable user data.

## Failure modes

**Wrong:** migrate by copying the encrypted XML through Android Auto Backup and assume it will decrypt on a fresh installation. The Keystore key may not be restored. **Right:** exclude incompatible ciphertext from backup or implement deliberate recovery, then test restore and key invalidation. Also wrong: treating `local.properties`, R8 obfuscation, or an APK-bundled secret as protected runtime storage.

## Production perspective

A banking app upgrades local token storage. It does not silently discard live sessions, nor does it claim to decrypt after key loss. The migration is staged, telemetry excludes token values, failures lead to safe re-authentication, and server revocation remains authoritative. A payment approval is verified server-side; encrypted local preferences do not make a client decision trustworthy.

## Interview answer — short

EncryptedSharedPreferences was deprecated due to high production crash rates caused by Keystore state corruption, DeadObjectExceptions across OEM updates, and Tink keyset deserialization failures. Modern production systems replace it with Jetpack DataStore combined with raw Android Keystore AES-GCM encryption, or SQLCipher for structured datasets.

## Interview answer — structured

`EncryptedSharedPreferences` (part of Jetpack `androidx.security:security-crypto`) provided out-of-the-box key and value encryption wrapping Google Tink and Android Keystore. However, it proved unreliable in production.

First, **Root Causes of Deprecation**. Next, with Keyset Corruption & Crashes, tink stored an encrypted keyset in private XML files. Across OEM Android updates, backup restores, or Keystore daemon crashes, the hardware master key would become unrecoverable, throwing unrecoverable `SecurityException`, `DeadObjectException`, or `CleartextKeysetException` during app startup.
Additionally, with Main-Thread Blocking, initializing `EncryptedSharedPreferences` performed blocking Keystore IPC and keyset decryption, triggering frame drops and ANRs. With Unmaintained Status, google ceased active development, leaving reported bugs unresolved.
**Modern Production Alternatives**. With Jetpack DataStore + Custom Keystore Encryption, persist encrypted byte buffers or Base64 payloads into Jetpack DataStore asynchronously using Coroutines, backed by a clean, self-contained raw Keystore AES-GCM implementation.
Finally, with SQLCipher / Room, for structured relational data requiring at-rest encryption.


## Interview answer — deep senior

Senior engineers evaluating Android storage security avoid black-box abstraction libraries that hide Keystore lifecycle hazards.

First, with State Inconsistency Post-Reboot/Restore, when a user restores from Google Auto Backup or when OEM Keystore daemons desynchronize after a major OS update, the keyset file remains on disk while the hardware Keystore alias has vanished. `EncryptedSharedPreferences` crashes permanently because it cannot decrypt the keyset and lacks an automatic reset fallback. Next, with Resilient Replacement Architecture, in our production stack, we decouple persistence from encryption.
We maintain a dedicated `CryptoEngine` executing on `Dispatchers.Default` using raw `AndroidKeyStore`. When decryption fails due to key invalidation or hardware faults, we catch the cryptographic error, proactively wipe the corrupted storage entry, and fire a re-authentication event to navigate the user to login.
Finally, this graceful degradation guarantees that security failures never cascade into unrecoverable app startup crashes.


## How to answer in the interview

- **Why:** deprecated storage still exists on user devices.
- **How:** inventory values and migrate with a verified, crash-safe switch.
- **Trade-off:** retaining legacy readers temporarily increases code complexity.
- **Failure case:** restore brings ciphertext without its key.
- **Production solution:** stage migration and support reauthentication for replaceable tokens.

## Deep-dive talking points

Discuss authenticated encryption, IV uniqueness, Android backup/restore behavior, hardware-backed key properties, invalidation after authentication changes, token revocation, and migration rollback.

## Follow-up questions

- **Interviewer:** "What is the difference between SIV and GCM in Tink's implementation?"
  **Answer:** "SIV (Synthetic IV) is deterministic authenticated encryption used for SharedPreferences keys so identical lookup keys produce identical ciphertexts for querying, while GCM is randomized for values."

- **Interviewer:** "Why is Jetpack DataStore structurally safer than SharedPreferences for encrypted payloads?"
  **Answer:** "DataStore is fully asynchronous, runs on Coroutine dispatchers off the UI thread, supports transactional data migration, and handles error recovery through explicit Catch operators."

## Self-check rubric

Score 0–5, one point each: identify current deprecation; explain what Keystore does; describe an existing-data migration; handle backup/key loss; separate local storage from server trust. No credit for claiming guaranteed security.

## References and reviewed-on date

- [AndroidX Security Crypto API reference](https://developer.android.com/reference/androidx/security/crypto/package-summary) — current deprecation status.
- [EncryptedSharedPreferences API reference](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences) — deprecation and backup warning.
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key material and operation constraints.

Technically reviewed against primary documentation on 2026-10-13.
