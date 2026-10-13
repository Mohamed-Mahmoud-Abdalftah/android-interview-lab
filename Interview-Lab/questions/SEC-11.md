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

- Key creation versus full authenticated-ciphertext protocol.
- Nonce uniqueness, backup, key loss and server authority.

## Explanation in Arabic

لتشفير small secret مثل refresh token، الـapp تنشئ AES key في Android Keystore وتستخدم AES-GCM مع IV جديد لكل عملية. لازم تخزن version وIV وciphertext+tag مع بعض؛ وقت القراءة الـtag يفشل لو البيانات اتغيرت. الـKeystore مش مكان نحط فيه arbitrary plaintext. لو key ضاع بعد reinstall أو restore، token يتشال ويطلب sign-in بدل افتراض إن decrypt هينجح.

## Practical walkthrough

لو محتاج تخزّن refresh token صغير، ولّد AES key في Keystore واستعمل AES-GCM مع IV فريد لكل encryption. خزّن envelope فيها version وIV وciphertext+tag، واكتبها atomically. وقت القراءة، tag failure ممكن يعني تلف بيانات أو مفتاح مختلف، فلا تعيد استخدام IV أو ترجع plaintext جزئي. لو token بديل، اطلب login بدل محاولة إصلاح صامتة.

## Why it matters and how it works

Generate a non-exportable key with encrypt/decrypt purposes, then initialize a Cipher for each encryption so it gets a fresh IV. Store a versioned envelope and use the same IV for decryption, never reuse an IV under the key. Authentication failures are data-integrity or key-loss events, not empty-string defaults.

## Worked example

Android/Kotlin example for a small replaceable token. `key` is an existing AES key generated in `AndroidKeyStore` for GCM encryption; this function produces a versioned envelope but the caller must persist it atomically in app-private storage. A production reader must validate version and IV length before AES-GCM decryption.

```kotlin
import javax.crypto.Cipher
import javax.crypto.SecretKey

fun sealToken(token: ByteArray, key: SecretKey): ByteArray {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, key) // provider generates a fresh IV
    val ciphertextAndTag = cipher.doFinal(token)
    val iv = cipher.iv
    require(iv.size in 12..16)
    return byteArrayOf(1, iv.size.toByte()) + iv + ciphertextAndTag
}
```

The same key and IV pair must never encrypt twice. On decryption, GCM authentication failure is a hard failure; do not return partial plaintext.

## Trade-offs and decision criteria

App-level encryption adds implementation and recovery complexity. Avoid storing a secret at all when possible. A replaceable token can be discarded after key loss; irreplaceable user data needs a separate recovery design outside device-bound Keystore.

## Failure modes

Using a fixed GCM IV or writing ciphertext without its tag breaks security or recovery. Backing up encrypted bytes but not the key creates undecipherable data. Test interrupted writes, tampering, logout, reinstall and backup restore.

## Production perspective

A production token store writes a versioned envelope atomically, excludes unrecoverable ciphertext from backup, redacts errors, and clears invalid tokens before re-authentication. The backend owns token revocation and session status.

## Interview answer — short

“I use a Keystore AES key with AES-GCM, a fresh IV per encryption, and a versioned ciphertext envelope. I plan for key loss and never treat local encryption as server authorization.”

## Interview answer — structured

“For a small replaceable token I would generate an AES key in Android Keystore, encrypt with AES-GCM using a fresh IV, and write a versioned envelope containing IV and authenticated ciphertext atomically. Decryption must either verify the tag or fail; it cannot return a default plaintext. I test tampering, interrupted writes, backup restore and key loss. If the token cannot be decrypted, the app clears it and requests sign-in while the backend keeps control of the session.”

## Interview answer — deep senior

“For a replaceable local secret, I would generate a restricted AES key in Android Keystore, encrypt with AES-GCM using a fresh IV, and store version, IV, and ciphertext plus tag as one atomic envelope. Decryption either authenticates the entire value or fails; I never return partial plaintext. I would test IV uniqueness, tampering, crash during write, key invalidation, and restore without the original key. If the token cannot be recovered, the app asks for sign-in instead of silently weakening storage. Hardware backing is device dependent, and plaintext is still exposed to the app during use, so server revocation and authorization remain essential. I would avoid a hand-rolled serialized format without test vectors: define exact byte order, IV length, tag length and supported versions, and reject malformed envelopes before decrypting. A write should be atomic so a crash cannot leave half an IV or tag. I would also inspect whether backup rules include the ciphertext; if the key will not survive restore, excluding it or forcing reauthentication is a product decision, not an implementation accident.”

## How to answer in the interview

- **Why:** local encryption is only as sound as key and format handling.
- **How:** generate Keystore AES-GCM key and persist a versioned IV/ciphertext envelope.
- **Trade-off:** encrypted storage complicates migration and recovery.
- **Failure case:** IV reuse or restored ciphertext without its key.
- **Production solution:** atomic writes, test tampering, and reauthenticate on unrecoverable key loss.

## Deep-dive talking points

Specify the ciphertext envelope, authenticated-encryption mode, IV uniqueness, key alias/version, backup exclusions and unreadable-key recovery path.

## Follow-up questions

- [SEC-13](../sec-13/): What happens on restore? **Answer:** device-bound key may be unavailable; re-authenticate or use designed recovery.
- [SEC-14](../sec-14/): Does encrypting a refresh token revoke it? **Answer:** no, server revocation is separate.

## Self-check rubric

Can I describe key purpose, unique IV, envelope/tag, atomic persistence, invalidation and token recovery?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key properties and use.
- [Android cryptography guidance](https://developer.android.com/privacy-and-security/cryptography) — cryptographic practices.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
