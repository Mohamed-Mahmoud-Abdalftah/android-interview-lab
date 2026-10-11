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

`EncryptedSharedPreferences` كانت convenience API تشفّر keys وvalues، لكنها دلوقتي deprecated في AndroidX Security Crypto؛ ماينفعش أقول إنها الاختيار الحديث الافتراضي من غير مراجعة نسخة المكتبة والـdocs. الـAndroid Keystore بتحمي key material من الاستخراج بقدر ضمانات الجهاز، لكن مش بتخلي البيانات أو الـapp ضد كل هجوم. لو عندك مستخدمين مخزنين بيانات بالطريقة القديمة، migration لازم تراعي إن الـkey ممكن تضيع بعد restore أو تتبطل؛ ساعتها ما نخترعش decrypt ناجح، بل نطلب إعادة authentication أو نسترجع من server آمن حسب نوع البيانات.

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

“`EncryptedSharedPreferences` is deprecated in AndroidX Security Crypto, so I would not recommend it as a universal new default. I would check the current API guidance and the app’s threat model, protect necessary keys with Android Keystore, and plan migration, backup exclusions, key invalidation, and recovery. Client encryption never replaces server authorization.”

## Interview answer — structured

“The AndroidX encrypted preferences API is now deprecated. Existing apps may still have ciphertext written with it, so the decision is not simply to swap a dependency. I inventory stored data, decide which values need local encryption at all, and define a versioned migration that reads old values only while the old key is available, verifies the new write, and safely handles key loss. For secrets such as refresh tokens, I can often clear and require re-authentication on unrecoverable key failure. Keystore protects key material subject to device capabilities; the application must still design IVs, backup rules, rotation, and incident handling. I never treat local encryption as server-side trust or a way to hide a bundled API secret.”

## Deep-dive talking points

Discuss authenticated encryption, IV uniqueness, Android backup/restore behavior, hardware-backed key properties, invalidation after authentication changes, token revocation, and migration rollback.

## Follow-up questions

- [SEC-11](../sec-11/): How would you design small-secret storage? **Hint:** distinguish key management from ciphertext format.
- [SEC-13](../sec-13/): What if the key is invalidated? **Hint:** make recovery explicit for each data class.
- [SEC-14](../sec-14/): How do you revoke a refresh token? **Hint:** server authority and session lifecycle.

## Self-check rubric

Score 0–5, one point each: identify current deprecation; explain what Keystore does; describe an existing-data migration; handle backup/key loss; separate local storage from server trust. No credit for claiming guaranteed security.

## References and reviewed-on date

- [AndroidX Security Crypto API reference](https://developer.android.com/reference/androidx/security/crypto/package-summary) — current deprecation status.
- [EncryptedSharedPreferences API reference](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences) — deprecation and backup warning.
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key material and operation constraints.

Technically reviewed against the linked primary documentation on 2026-10-11. The snippet covers key creation only; the complete encryption format was intentionally omitted because it requires an application-specific threat model and recovery design.
