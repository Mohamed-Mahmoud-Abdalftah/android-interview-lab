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

لتشفير سر حساس وصغير على الجهاز (زي refresh token أو biometric session key)، بنستخدم Android Keystore عشان المفتاح نفسه يتولد ويتخزن داخل بيئة معزولة عتاديًا (TEE أو StrongBox) ولا يخرج أبدًا للـRAM كـplaintext raw bytes. التشفير بيتم بـ `AES/GCM/NoPadding` بمفتاح 256-bit. الـprovider بيولد IV عشوائي فريد بطول 12 bytes لكل عملية تشفير منفصلة؛ إياك تعيد استخدام نفس الـIV مع نفس المفتاح نهائيًا، لأن ده بيكسر سرية وسلامة GCM تمامًا. البيانات المشفرة لازم تتخزن في envelope منظم فيه رقم إصدار (version byte)، طول الـIV، الـIV نفسه، والـciphertext مدمج معاه الـ128-bit authentication tag.

## Practical walkthrough

أثناء القراءة، بنمرر نفس الـIV في `GCMParameterSpec(128, iv)` ونعمل `cipher.init(Cipher.DECRYPT_MODE, key)`. لو حصل أي تلاعب في حرف واحد من البيانات أو الـIV، التشفير هيرمي `AEADBadTagException` فورًا ويرفض فك التشفير. كمان لو المستخدم ضاف بصمة جديدة وكان المفتاح متظبط بـ `setInvalidatedByBiometricEnrollment(true)`، المفتاح هيرمي `KeyPermanentlyInvalidatedException`. الملف المتشفر لازم يتكتب على القرص بـ `AtomicFile` عشان لو النظام طفى في نص الكتابة ما يحصلش ملف مقطوع. لو فك التشفير فشل لأي سبب، القرار الهندسي الصح مش إنك تحاول تخمن أو ترجع قيمة فاضية، بل تمسح السجل المعطوب وتطلب من المستخدم re-authentication نظيف، بينما الـbackend يفضل صاحب السلطة في إلغاء الـsession.

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

“I generate a 256-bit AES key inside Android Keystore configured for AES-GCM without export rights. For encryption, I let the Keystore generate a fresh 12-byte IV per invocation and store an envelope containing version, IV, ciphertext, and 128-bit authentication tag atomically. During decryption, GCM checks data integrity, throwing `AEADBadTagException` if tampered. If the key is invalidated or lost, I purge the local record and prompt the user for clean re-authentication.”

## Interview answer — structured

“When implementing Keystore-backed encryption for small secrets like refresh tokens:
1. **Key Generation:** I use `KeyGenerator` with provider `AndroidKeyStore`, generating an AES key with `PURPOSE_ENCRYPT or PURPOSE_DECRYPT`, `BLOCK_MODE_GCM`, and `ENCRYPTION_PADDING_NONE`. The key material remains permanently in hardware (TEE or StrongBox).
2. **Encryption Protocol:** I use `AES/GCM/NoPadding`. Calling `cipher.init(Cipher.ENCRYPT_MODE, key)` automatically generates a cryptographically random 12-byte IV. I construct a versioned envelope containing `[version, iv_length, iv, ciphertext_length, ciphertext_and_tag]`.
3. **Decryption & Validation:** I extract the IV, configure `GCMParameterSpec(128, iv)`, and invoke `cipher.doFinal()`. If any byte was altered, GCM tag verification fails with `AEADBadTagException`. I map this to a security error rather than falling back silently.
4. **Resilience & Storage:** I write the envelope to `noBackupFilesDir` using `AtomicFile` to prevent torn writes and unwanted cloud backups.
5. **Session Architecture:** If the key is lost after an OS upgrade or invalidated by biometric re-enrollment, the app handles it as a predictable lifecycle event, clearing the token and initiating user login.”

## Interview answer — deep senior

“A senior engineer looks at Keystore encryption not just as calling crypto APIs, but as a complete system lifecycle: threat model, key storage, wire format, and failure recovery.

I generate an AES-256 key restricted to GCM mode directly inside `AndroidKeyStore`. I set `setRandomizedEncryptionRequired(true)` so the platform enforces fresh nonce generation, mitigating the catastrophic risk of GCM IV collision. If biometric binding is required, I set `setUserAuthenticationRequired(true)` and `setInvalidatedByBiometricEnrollment(true)`. In that design, the `Cipher` is wrapped in `BiometricPrompt.CryptoObject`, and `cipher.doFinal()` only succeeds after hardware-authenticated biometric confirmation.

For persistence, I design an explicit versioned envelope: version byte, IV length, 12-byte IV, and ciphertext with embedded 128-bit authentication tag. I save this file using `AtomicFile` inside `noBackupFilesDir`. This eliminates two major production bugs: corrupted partial writes during unexpected process kills, and orphaned ciphertext restored via Android Auto-Backup onto a new device that lacks the hardware private key.

On the decryption side, any failure—whether `AEADBadTagException` from file tampering, or `KeyPermanentlyInvalidatedException` from biometric changes—is handled as an explicit invalidation trigger: the client purges the corrupted token and navigates to the login screen.

Crucially, I never confuse device-level encryption with server-level security. A rooted device with runtime instrumentation can hook `cipher.doFinal()` when the secret is briefly held in memory. Therefore, the on-device secret must only be a replaceable refresh token with short validity, while the backend maintains strict token binding, rotation, and revocation authority.”

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

- [SEC-13](../sec-13/): What happens to Keystore keys when the user backs up and restores to a new phone? **Answer:** Hardware-backed Keystore keys cannot be exported, so ciphertext restored to a new phone cannot be decrypted; design a clean re-authentication path.
- [SEC-14](../sec-14/): Does encrypting a refresh token with Keystore prevent token theft in RAM? **Answer:** No, once decrypted in process memory, a rooted device with memory inspection can read it; defense-in-depth requires short token TTL and backend rotation.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
