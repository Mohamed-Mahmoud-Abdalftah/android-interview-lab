---
id: "SEC-11"
question: "How do you implement Keystore-backed encryption for small app secrets?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 308
editorial_status: "reviewed"
---

# SEC-11

## Original interview question

How do you implement Keystore-backed encryption for small app secrets?

## What the interviewer evaluates

- Android Keystore architecture: hardware-backed TEE/StrongBox vs software fallback.
- Correct authenticated encryption: AES-GCM (256-bit key, 12-byte IV, 128-bit authentication tag) without IV reuse.
- Envelope serialization, atomic persistence, and defense against data corruption.
- Key lifecycle handling: key generation, biometric invalidation, backup exclusion, and missing-key reauthentication.
- Threat modeling: local client boundary vs server session authority.

## Explanation in Arabic

كيف تقوم بتنفيذ تشفير مدعوم عتادياً بالـ Keystore لتخزين أسرار التطبيق الصغيرة (App Secrets) بشكل آمن؟

1. ما هي خوارزمية التشفير القياسية الموصى بها؟
   - **AES/GCM/NoPadding (Galois/Counter Mode)**: هي خوارزمية تشفير متماثل توفر **Authenticated Encryption with Associated Data (AEAD)**. هذا يعني أنها لا تكتفي بتشفير البيانات (Confidentiality) فقط، بل تولد أيضاً **Authentication Tag** يحمي من أي تلاعب أو تعديل في النص المشفر (Integrity & Authenticity).
   - في حال حاول المهاجم تعديل حتى بايت واحد في البيانات المشفرة، تفشل عملية فك التشفير برمي استثناء `AEADBadTagException` فوراً.

2. دور الـ Android Keystore:
   - يُولد مفتاح AES-256 داخل الـ Keystore ولا يخرج منه أبداً (`PURPOSE_ENCRYPT or PURPOSE_DECRYPT`).
   - التطبيق يستخدم اسم المفتاح (Alias) فقط لتوجيه أوامر التشفير وفك التشفير للنظام.

3. إدارة متجه البدء (Initialization Vector - IV):
   - تتطلب خوارزمية GCM متجه بدء (IV) فريداً تماماً لكل عملية تشفير (عادة 12 بايت).
   - **قاعدة حرجة**: لا تقم أبداً بإعادة استخدام نفس الـ IV مع نفس المفتاح، لأن ذلك يدمر أمان خوارزمية GCM بالكامل!
   - يُترك لـ `Cipher.init(Cipher.ENCRYPT_MODE, secretKey)` توليد IV عشوائي جديد تلقائياً في كل مرة، ويتم حفظ هذا الـ IV بجانب النص المشفر (مثلاً بدمجهما معاً في نفس المصفوفة) لأن الـ IV ليس سراً.

## Practical walkthrough

تطبيق احترافي لتشفير وفك تشفير البيانات الصغيرة باستخدام Android Keystore و AES-256-GCM:
```kotlin
class KeystoreSecretStorage {
    private val KEY_ALIAS = "app_auth_secret_v1"
    private val ANDROID_KEYSTORE = "AndroidKeyStore"
    private val TRANSFORMATION = "AES/GCM/NoPadding"
    private val GCM_TAG_LENGTH_BITS = 128
    private val IV_SIZE_BYTES = 12

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
        if (keyStore.containsAlias(KEY_ALIAS)) {
            return (keyStore.getEntry(KEY_ALIAS, null) as KeyStore.SecretKeyEntry).secretKey
        }
        val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
        val spec = KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setRandomizedEncryptionRequired(true) // يجبر النظام على رفض IV مكرر
            .build()
        keyGen.init(spec)
        return keyGen.generateKey()
    }

    fun encrypt(plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        val iv = cipher.iv // 12-byte IV تم توليده عشوائياً بواسطة الـ Cipher
        val ciphertextWithTag = cipher.doFinal(plaintext)
        
        // دمج الـ IV مع النص المشفر في مصفوفة واحدة: [12 bytes IV] + [Ciphertext + Tag]
        return ByteBuffer.allocate(iv.size + ciphertextWithTag.size)
            .put(iv)
            .put(ciphertextWithTag)
            .array()
    }

    fun decrypt(encryptedPayload: ByteArray): ByteArray {
        val buffer = ByteBuffer.wrap(encryptedPayload)
        val iv = ByteArray(IV_SIZE_BYTES).also { buffer.get(it) }
        val ciphertextWithTag = ByteArray(buffer.remaining()).also { buffer.get(it) }

        val cipher = Cipher.getInstance(TRANSFORMATION)
        val spec = GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv)
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), spec)
        return cipher.doFinal(ciphertextWithTag)
    }
}
```

## Why it matters and how it works

The Android Keystore provider protects cryptographic keys from extraction by hosting key material in a hardware-isolated environment (Trusted Execution Environment or StrongBox Keymaster/KeyMint). Rather than granting the application direct access to raw key bytes, the Keystore returns an opaque `SecretKey` handle. Cryptographic operations (`Cipher`, `Mac`, `Signature`) are performed inside the secure hardware boundary.

Authenticated encryption via `AES/GCM/NoPadding` provides both confidentiality and message integrity. An encryption envelope consists of:
1. Version byte (for backward-compatible crypto protocol migration).
2. Initialization Vector (IV): exactly 12 bytes generated randomly by the platform provider per encryption call.
3. Authenticated ciphertext + GCM Tag: 128-bit MAC computed across the payload.

If an attacker modifies the ciphertext or tampering occurs on disk, decryption fails deterministically at tag verification time (`AEADBadTagException`), preventing chosen-ciphertext attacks.

## Worked example

Here is a production-grade, hardened Kotlin implementation that manages Keystore key creation, authenticated encryption, safe decryption, and envelope parsing:

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyPermanentlyInvalidatedException
import android.security.keystore.KeyProperties
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.DataInputStream
import java.io.DataOutputStream
import java.security.KeyStore
import javax.crypto.AEADBadTagException
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class KeystoreTokenCryptor(
    private val keyAlias: String = "auth_token_key_v1"
) {
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    private companion object {
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
        private const val GCM_TAG_LENGTH_BITS = 128
        private const val CURRENT_VERSION: Byte = 1
        private const val EXPECTED_IV_LENGTH = 12
    }

    @Synchronized
    fun getOrCreateKey(): SecretKey {
        val existingKey = keyStore.getKey(keyAlias, null) as? SecretKey
        if (existingKey != null) return existingKey

        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )
        val spec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setRandomizedEncryptionRequired(true) // Forces new IV on each encrypt init
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }

    fun encrypt(plaintext: ByteArray): ByteArray {
        val key = getOrCreateKey()
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, key) // Provider auto-generates 12-byte secure IV
        val iv = cipher.iv ?: error("Cipher IV must not be null in GCM mode")
        require(iv.size == EXPECTED_IV_LENGTH) { "Invalid IV length: ${iv.size}" }

        val ciphertextWithTag = cipher.doFinal(plaintext)

        val output = ByteArrayOutputStream()
        DataOutputStream(output).use { stream ->
            stream.writeByte(CURRENT_VERSION.toInt())
            stream.writeByte(iv.size)
            stream.write(iv)
            stream.writeInt(ciphertextWithTag.size)
            stream.write(ciphertextWithTag)
        }
        return output.toByteArray()
    }

    fun decrypt(envelopeBytes: ByteArray): ByteArray {
        val input = ByteArrayInputStream(envelopeBytes)
        val (version, iv, ciphertextWithTag) = DataInputStream(input).use { stream ->
            val version = stream.readByte()
            require(version == CURRENT_VERSION) { "Unsupported envelope version: $version" }
            val ivLength = stream.readByte().toInt()
            require(ivLength == EXPECTED_IV_LENGTH) { "Invalid IV length in envelope: $ivLength" }
            val iv = ByteArray(ivLength).also { stream.readFully(it) }
            val cipherLength = stream.readInt()
            val cipherData = ByteArray(cipherLength).also { stream.readFully(it) }
            Triple(version, iv, cipherData)
        }

        val key = keyStore.getKey(keyAlias, null) as? SecretKey
            ?: throw IllegalStateException("Key $keyAlias not found in AndroidKeyStore")

        val cipher = Cipher.getInstance(TRANSFORMATION)
        val spec = GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv)

        return try {
            cipher.init(Cipher.DECRYPT_MODE, key, spec)
            cipher.doFinal(ciphertextWithTag)
        } catch (tampered: AEADBadTagException) {
            throw SecurityException("Data integrity check failed: payload was modified or corrupted", tampered)
        } catch (invalidated: KeyPermanentlyInvalidatedException) {
            throw IllegalStateException("Keystore key permanently invalidated by OS biometric update", invalidated)
        }
    }
}
```

```kotlin
// Example verification test demonstrating tampering detection
class KeystoreTokenCryptorTest {
    fun verifyTamperingDetection(cryptor: KeystoreTokenCryptor) {
        val secret = "super_secret_refresh_token_value".encodeToByteArray()
        val envelope = cryptor.encrypt(secret)

        // Corrupt single byte in the ciphertext payload
        val corruptedEnvelope = envelope.copyOf()
        corruptedEnvelope[corruptedEnvelope.lastIndex] = (corruptedEnvelope.last().toInt() xor 0xFF).toByte()

        try {
            cryptor.decrypt(corruptedEnvelope)
            error("Decryption should have thrown SecurityException due to bad GCM tag!")
        } catch (expected: SecurityException) {
            // Success: GCM authentication tag caught corruption before returning plaintext
        }
    }
}
```

## Trade-offs and decision criteria

1. **Keystore AES-GCM vs EncryptedSharedPreferences (Jetpack Security):**
   - Jetpack `EncryptedSharedPreferences` provides high-level key-value storage backed by Keystore master keys and Tink. However, it suffers from known corruption bugs on legacy Android versions and lacks granular control over biometric gating.
   - A custom `KeystoreTokenCryptor` gives explicit serialization, exact atomic file control, clear version migration, and deterministic lifecycle handling for critical fintech tokens.

2. **Hardware Backing Availability:**
   - On budget devices, Android Keystore may fall back to software emulation if StrongBox or TEE Keymaster is absent. Check `KeyInfo.isInsideSecureHardware()` when financial compliance mandates hardware-enforced resistance.

3. **User Data vs Disposable Tokens:**
   - Keystore keys are bound to the specific device install. If an app is uninstalled or restored on a new device, Keystore keys are not restored with auto-backup. Therefore, use this pattern for replaceable session tokens where key loss gracefully leads to re-authentication, never for non-recoverable user data without external backup keys.

## Failure modes

- **Nonce/IV Reuse in GCM:** Reusing the same IV with the same AES key completely compromises the authentication tag and can allow plaintext recovery across multiple messages. Never hardcode or manually reuse IVs; let `Cipher.init(ENCRYPT_MODE, key)` draw from hardware RNG.
- **Silent Fallback on Decryption Failure:** Catching `Exception` and returning an empty byte array or default string allows corrupted states or active tampering to go unnoticed. Always surface a typed failure that clears the local cache and triggers clean login.
- **Torn File Writes:** A power loss during file write leaves a partial envelope on disk. Always use Android's `AtomicFile` to perform writes via a staging file.
- **Auto-Backup Restoring Ciphertext Without Key:** If ciphertext is included in Google Drive Auto-Backup, restoring to a new device will bring orphaned ciphertext whose Keystore key does not exist on the target hardware. Exclude credential files in `res/xml/backup_rules.xml`.

## Production perspective

In a production banking or payment app:
- Store the encrypted payload using `AtomicFile` inside `context.noBackupFilesDir` to guarantee exclusion from cloud backups.
- If biometric authorization is required, configure `.setUserAuthenticationRequired(true)` with `.setInvalidatedByBiometricEnrollment(true)`. Instantiate `BiometricPrompt.CryptoObject(cipher)` with the initialized cipher so hardware validates the biometric challenge prior to `cipher.doFinal()`.
- Log cryptographic failure rates to telemetry (redacting sensitive data) to detect device-specific keystore regressions or active client tampering.
- Treat on-device encryption as defense-in-depth: the backend remains the ultimate authority, validating signed JWT claims and enforcing immediate server-side revocation upon token refresh or security alert.

## Interview answer — short

To encrypt small secrets, generate an AES-256 key inside Android Keystore configured for AES/GCM/NoPadding. Let the Cipher generate a fresh 12-byte IV on each encryption, store the IV prepended to the ciphertext, and decrypt using a GCMParameterSpec with 128-bit authentication tag. GCM ensures both confidentiality and tamper detection.

## Interview answer — structured

Encrypting small secrets securely on Android requires Keystore-managed hardware isolation and authenticated encryption:

1. **Key Generation in Keystore**: Generate a 256-bit AES key inside `AndroidKeyStore` using `KeyGenParameterSpec` configured with `PURPOSE_ENCRYPT or PURPOSE_DECRYPT`, `BLOCK_MODE_GCM`, `ENCRYPTION_PADDING_NONE`, and `setRandomizedEncryptionRequired(true)`. The key material never leaves hardware.

2. **Authenticated Encryption (AES-GCM)**: GCM is an AEAD (Authenticated Encryption with Associated Data) mode. In addition to encrypting data, it appends a 128-bit authentication tag. If an attacker modifies even a single byte of ciphertext in storage, `cipher.doFinal()` throws `AEADBadTagException`, preventing bit-flipping attacks.

3. **IV Management**: GCM requires a unique Initialization Vector (IV)—typically 12 bytes—for every encryption under the same key. Reusing an IV with GCM destroys cryptographic security. Always let `cipher.init(Cipher.ENCRYPT_MODE, key)` generate the random IV via the system's secure RNG, and prepend the IV to the stored ciphertext.

4. **Decryption**: Extract the first 12 bytes as IV, initialize `Cipher.DECRYPT_MODE` with `GCMParameterSpec(128, iv)`, and decrypt the remaining bytes.

## Interview answer — deep senior

From an architectural standpoint, implementing Keystore-backed encryption requires considering concurrency, performance, and key resilience:

1. **Keystore IPC Bottlenecks**: Android Keystore operations involve IPC to the `keystored` daemon and hardware TEE/StrongBox calls. These calls are CPU-intensive and blocking. Encryption and decryption routines must never execute on the Main Thread; dispatch them to a dedicated background Coroutine dispatcher (`Dispatchers.IO` or `Dispatchers.Default`).

2. **Handling Corrupted Entries**: In production across diverse OEM implementations, Keystore operations occasionally throw `KeyStoreException` or `UnrecoverableKeyException` due to hardware glitches or OS upgrades. Resilient architectures catch these exceptions, clear the corrupted alias, purge stale encrypted tokens from storage, and gracefully prompt the user to re-authenticate.

3. **Size Constraints**: Keystore AES-GCM is designed for small payloads (tokens, encryption keys, PII strings). For large files or databases, use an **Envelope Encryption** pattern: generate a random data key in memory, encrypt the file using standard AES-CTR/CBC, and use Keystore only to encrypt that data key.

## How to answer in the interview

- **Why:** On-device plaintext storage is vulnerable to root extraction, app backups, and file system inspection.
- **How:** Generate a non-exportable AES key in `AndroidKeyStore`, encrypt with `AES/GCM/NoPadding` using a fresh 12-byte IV, serialize into a versioned envelope, and persist with `AtomicFile`.
- **Trade-off:** Keystore keys do not migrate across devices, and StrongBox hardware support varies across Android OEMs.
- **Failure case:** GCM IV reuse destroys encryption integrity; backup restore produces undecipherable tokens.
- **Production solution:** Exclude from backup via `noBackupFilesDir`, detect tampering with GCM tags, and trigger clean re-authentication on key loss.

## Deep-dive talking points

- **TEE vs StrongBox:** TEE shares main CPU hardware memory isolation, while StrongBox uses a dedicated security chip with isolated CPU and secure storage.
- **AEAD (Authenticated Encryption with Associated Data):** Why GCM replaces older AES-CBC + HMAC designs by computing authentication tags natively.
- **Key Invalidation:** How adding a new fingerprint invalidates user-auth keys when `setInvalidatedByBiometricEnrollment(true)` is set.
- **Atomic Persistence:** Using `AtomicFile` rename semantics to eliminate partially written files during OS shutdowns.

## Follow-up questions

- **Interviewer:** "Why should you never use AES/ECB/PKCS5Padding?"
  **Answer:** "ECB mode encrypts identical plaintext blocks into identical ciphertext blocks, revealing patterns and structure, and lacks an authentication tag against tampering."

- **Interviewer:** "What happens if you supply your own hardcoded IV to AES/GCM?"
  **Answer:** "If `setRandomizedEncryptionRequired(true)` is set, Keystore throws an exception; if bypassed, reusing the same IV completely breaks GCM security and exposes key details."

## Self-check rubric

- Can I explain why `AndroidKeyStore` prevents key export from secure hardware?
- Can I write the complete `KeyGenParameterSpec` configuration for AES-GCM?
- Can I describe why 12-byte IV uniqueness is mandatory in AES-GCM?
- Can I handle `AEADBadTagException` and `KeyPermanentlyInvalidatedException` without silent fallback?
- Can I articulate why encrypted secrets should be saved in `noBackupFilesDir` using `AtomicFile`?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — hardware-backed cryptographic keys.
- [Android cryptography guidance](https://developer.android.com/privacy-and-security/cryptography) — best practices for cipher suites and GCM.
- [OWASP Mobile Application Security (MASVS-STORAGE)](https://mas.owasp.org/MASVS/04-MASVS-STORAGE/) — secure storage verification requirements.

Technically reviewed against primary documentation on 2026-10-13.
