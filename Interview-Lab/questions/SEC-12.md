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

## Practical walkthrough

لو فريق عنده ملف `EncryptedSharedPreferences` قديم، ما ينفعش يحذفه أول release فيفقد refresh tokens عند المستخدمين. اعمل migration: اقرأ بالقارئ القديم طول ما key موجودة، اكتب format الجديد، اقرأها للتأكد، وبعدها امسح القديمة. لو restore جاب ciphertext بلا Keystore key، تعامل معها كجلسة انتهت واطلب sign-in. لا تفترض إن deprecation معناها إن البيانات القديمة قابلة للقراءة تلقائيًا.

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

“`EncryptedSharedPreferences` is deprecated, so I would check the current AndroidX guidance before using it in a new design. Existing files still need a migration plan: inventory values, read with the old key while possible, write and verify a new format, then retire the old entry. Restored ciphertext can be unusable because Keystore keys may be absent, so replaceable tokens should lead to reauthentication. Deprecation alone does not justify silent data loss.”

## Interview answer — deep senior

“I would first classify the data and threat model instead of choosing an encrypted preferences helper by habit. AndroidX Security Crypto's EncryptedSharedPreferences API is deprecated, so an existing app needs an explicit migration rather than a blanket recommendation for new work. Keystore can protect key material subject to device capabilities, while the app still owns authenticated encryption format, IV uniqueness, backup exclusions, versioning, and key-loss recovery. A refresh token can often be revoked and reissued after unrecoverable key invalidation; irreplaceable local data needs a different recovery plan. I would migrate with a read-old/write-new/verify sequence, test restore to a different device and biometric changes, and keep server authorization independent of any device-side ciphertext. For migration I would test old ciphertext on every supported app upgrade path, not just the latest release. I would make the new write idempotent, verify it before deleting the old entry, and leave a recovery path for process death between steps. Deprecation does not imply the old encrypted file is immediately vulnerable, and it does not justify silently changing storage without a data-loss plan. Device restore without the old key should produce an explicit sign-in state.”

## How to answer in the interview

- **Why:** deprecated storage still exists on user devices.
- **How:** inventory values and migrate with a verified, crash-safe switch.
- **Trade-off:** retaining legacy readers temporarily increases code complexity.
- **Failure case:** restore brings ciphertext without its key.
- **Production solution:** stage migration and support reauthentication for replaceable tokens.

## Deep-dive talking points

Discuss authenticated encryption, IV uniqueness, Android backup/restore behavior, hardware-backed key properties, invalidation after authentication changes, token revocation, and migration rollback.

## Follow-up questions

- [SEC-11](../sec-11/): How would you design small-secret storage? **Answer:** define the data threat model, protect key material with Keystore where appropriate, and version an authenticated ciphertext format with backup rules.
- [SEC-13](../sec-13/): What if the key is invalidated? **Answer:** treat ciphertext as unreadable; reauthenticate and rotate revocable tokens, while separately planning recovery for irreplaceable data.
- [SEC-14](../sec-14/): How do you revoke a refresh token? **Answer:** invalidate the server-side session or token family and clear local copies; local deletion alone is not revocation.

## Self-check rubric

Score 0–5, one point each: identify current deprecation; explain what Keystore does; describe an existing-data migration; handle backup/key loss; separate local storage from server trust. No credit for claiming guaranteed security.

## References and reviewed-on date

- [AndroidX Security Crypto API reference](https://developer.android.com/reference/androidx/security/crypto/package-summary) — current deprecation status.
- [EncryptedSharedPreferences API reference](https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences) — deprecation and backup warning.
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key material and operation constraints.

Technically reviewed against the linked primary documentation on 2026-10-13. The snippet covers key creation only; the complete encryption format was intentionally omitted because it requires an application-specific threat model and recovery design.
