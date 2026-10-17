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

## Concept and technical explanation

The EncryptedSharedPreferences API (part of the androidx.security:security-crypto Jetpack library) was originally introduced to provide seamless, drop-in encrypted key-value storage backed by the Google Tink cryptographic library and Android Keystore master keys. In recent library revisions, EncryptedSharedPreferences has been formally deprecated by Google. The deprecation stems from severe underlying architectural deficiencies and edge-case reliability failures across the heterogeneous Android device ecosystem. The implementation relied on XML file parsing wrapped with cryptographic streaming ciphers, causing significant main-thread I/O latency, Application Not Responding (ANR) spikes, and deadlocks in multi-threaded environments. Furthermore, low-tier devices and specific OEM hardware variants (notably older Samsung and Huawei devices) suffered from catastrophic KeyStore corruption, throwing unrecoverable KeyStoreException, NullPointerException, or corrupted master key states that permanently locked users out of their encrypted data. The modern migration path involves adopting Jetpack DataStore (Preferences or Proto DataStore) combined with Google Tink directly, or building isolated Keystore AES-GCM serializers that decouple disk I/O from cryptographic operations.

## Practical walkthrough (English)

Safe migration pattern from deprecated EncryptedSharedPreferences to Jetpack DataStore:
```kotlin
// 1. Handling legacy EncryptedSharedPreferences corruption gracefully
class LegacyMigrationHelper(private val context: Context) {
    fun extractLegacyTokenOrNull(): String? {
        return try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            val legacyPrefs = EncryptedSharedPreferences.create(
                context,
                "secure_prefs",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
            legacyPrefs.getString("auth_token", null)
        } catch (e: Exception) {
            // Catches Keystore corruption, OEM crypto bugs, or broken master keys
            null
        }
    }

    fun wipeCorruptedLegacyPrefs() {
        try {
            context.getSharedPreferences("secure_prefs", Context.MODE_PRIVATE)
                .edit().clear().commit()
        } catch (ignored: Exception) {}
    }
}

// 2. Modern recommendation: Jetpack DataStore with direct Tink / Keystore encryption
// DataStore provides non-blocking coroutine-based async I/O on Dispatchers.IO
```

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

Google deprecated EncryptedSharedPreferences due to serious architectural flaws, including main-thread I/O performance bottlenecks, multi-threading deadlocks, and frequent Keystore corruption crashes on OEM devices. Production applications are migrating to Jetpack DataStore combined with Google Tink or custom Keystore AES-GCM wrappers, executing asynchronous encrypted persistence safely off the main thread.

## Interview answer — structured

While EncryptedSharedPreferences offered an easy API for securing key-value storage, Google formally deprecated it due to widespread production reliability issues.
The library wrapped traditional SharedPreferences XML files with Google Tink encryption keys anchored to an Android Keystore master key.
In production, this design created severe performance problems because SharedPreferences operations are synchronous, causing disk I/O and cryptographic computation to block the main thread and trigger ANR spikes.
More critically, the library suffered from catastrophic hardware-keystore failures on specific OEM hardware, particularly when devices rebooted or updated firmware.
Applications frequently encountered fatal crashes like KeyStoreException or broken master keys where encrypted preferences became permanently unreadable, stranding users in corrupted states.
Modern Android development replaces this deprecated class with Jetpack DataStore.
DataStore uses Kotlin Coroutines and Flow to guarantee asynchronous, thread-safe disk operations on Dispatchers.IO, separating storage mechanics from encryption and allowing teams to layer Google Tink or Keystore AES-GCM cleanly without risking main-thread freezes.

## Interview answer — deep senior

The deprecation of EncryptedSharedPreferences represents a case study in why simply wrapping legacy, synchronous I/O abstractions with heavy cryptographic operations inevitably fails at scale.
SharedPreferences was architected in the earliest days of Android with the assumption that reading small XML files in memory is fast enough for the main thread.
When Jetpack Security layered two-level authenticated encryption over preference keys via AES-256-SIV and preference values via AES-256-GCM, every read and write operation became a cryptographic transaction.
On mid-tier and budget Android devices, hardware cryptographic accelerators in the TEE have limited throughput; invoking Keystore operations synchronously during UI rendering resulted in severe jank and measurable ANR regressions.
Beyond latency, the ecosystem encountered fatal edge-case failures.
OEM implementations of Keymaster frequently failed during concurrent multi-process writes or Direct Boot transitions, corrupting the Keystore keyset or throwing internal Keystore errors with cryptic vendor codes.
Once the master keyset was corrupted, the XML file could neither be read nor recovered, causing endless startup crashes unless the app caught the exception and wiped all local user data.
To resolve this in modern architectures, we migrate away from EncryptedSharedPreferences toward Jetpack DataStore.
DataStore operates entirely off the main thread via Kotlin coroutines, provides transactional data consistency, and allows developers to serialize encrypted protocol buffers or use Google Tink directly on Dispatchers.IO.
When performing migrations, we implement resilient try-catch fallbacks: if reading legacy EncryptedSharedPreferences fails due to Keystore corruption, we wipe the corrupt file, force a clean token re-authentication, and persist the new session safely into DataStore.

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
