---
id: "SEC-07"
question: "Compare encryption, hashing, HMAC, and digital signatures."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 304
editorial_status: "reviewed"
---

# SEC-07

## Original interview question

Compare encryption, hashing, HMAC, and digital signatures.

## What the interviewer evaluates

- Reversible confidentiality versus one-way digest versus keyed integrity versus asymmetric authenticity.
- Correct primitive choice for passwords, API messages and signatures.

## Explanation in Arabic

مقارنة رياضية ومعمارية بين 4 مفاهيم أساسية في أمن المعلومات:
التشفير (Encryption)، والتجزئة (Hashing)، و HMAC، والتوقيع الرقمي (Digital Signatures):

1. التشفير (Encryption - السرية القابلة للعكس):
   - **الهدف**: تحقيق السرية والخصوصية (Confidentiality). تحويل النص الصريح إلى نص غير مفهوم، مع **إمكانية فك التشفير واستعادة النص الأصلي** باستخدام مفتاح سري.
   - **الأنواع**: متماثل (Symmetric مثل AES-256) بمفتاح واحد، أو غير متماثل (Asymmetric مثل RSA/ECC) بمفتاح عام وخاص.
   - **أفضل استخدام**: تشفير قاعدة البيانات المحلية، وتشفير رسائل المحادثة.

2. التجزئة (Hashing - البصمة الرقمية أحادية الاتجاه):
   - **الهدف**: التحقق من سلامة البيانات (Integrity). تحويل نص بأي طول إلى بصمة ثابتة الطول (Digest) مثل SHA-256.
   - **خاصية حتمية**: **أحادية الاتجاه رياضياً (One-Way)**؛ من المستحيل رياضياً استعادة النص الأصلي من الـ Hash.
   - **أفضل استخدام**: التحقق من سلامة تنزيل ملف APK (Checksum)، وحفظ كلمات المرور على السيرفر مع Salt (عبر bcrypt/Argon2).

3. HMAC (Hash-based Message Authentication Code - التجزئة بالمفتاح السري):
   - **الهدف**: التحقق من سلامة البيانات ومصدرها الموثوق (Integrity + Authenticity) باستخدام مفتاح سري مشترك متماثل.
   - **كيف يعمل**: دمج النص مع مفتاح سري مشترك قبل التجزئة: `HMAC = Hash(Key + Message)`.
   - **أفضل استخدام**: توقيع طلبات الـ Webhooks والـ API لمنع التلاعب بالبيانات أثناء النقل بين طرفين يعرفان نفس المفتاح.

4. التوقيع الرقمي (Digital Signatures - إثبات المصدر وعدم الإنكار):
   - **الهدف**: التحقق من المصدر، وسلامة المحتوى، **وعدم القدرة على الإنكار (Non-Repudiation)**.
   - **كيف يعمل**: تشفير الـ Hash الخاص بالرسالة باستخدام **المفتاح الخاص (Private Key)** للراسل. يستطيع أي شخص في العالم التحقق من التوقيع باستخدام **المفتاح العام (Public Key)**.
   - **أفضل استخدام**: توقيع ملفات الـ APK (APK Signature Scheme v2/v3)، وتوقيع المعاملات المالية في البنوك عبر مفاتيح Keystore الخاصة.

## Practical walkthrough

المقارنة البرمجية بين التشفير التوثيقي (AES-GCM)، والتجزئة، والتوقيع الرقمي في Kotlin:
```kotlin
// 1. Hashing: بصمة أحادية الاتجاه للتحقق من سلامة ملف:
fun calculateSha256(data: ByteArray): String {
    val digest = MessageDigest.getInstance("SHA-256").digest(data)
    return digest.joinToString("") { "%02x".format(it) }
}

// 2. HMAC: توقيع رسالة بمفتاح سري مشترك للتحقق من عدم التلاعب:
fun generateHmac(key: ByteArray, message: ByteArray): ByteArray {
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(SecretKeySpec(key, "HmacSHA256"))
    return mac.doFinal(message)
}

// 3. التوقيع الرقمي (Digital Signature): توقيع بمفتاح خاص داخل Keystore لا يمكن إنكاره:
fun signTransaction(privateKey: PrivateKey, transactionBytes: ByteArray): ByteArray {
    val signature = Signature.getInstance("SHA256withECDSA")
    signature.initSign(privateKey)
    signature.update(transactionBytes)
    return signature.sign() // يرسل للسيرفر مع المعاملة ليتحقق منه بالمفتاح العام
}
```

## Why it matters and how it works

Authenticated encryption such as AES-GCM combines confidentiality and integrity, provided nonce use is correct. A cryptographic hash alone proves neither who produced data nor that an attacker did not replace both data and hash. HMAC authenticates to shared-key holders; a digital signature allows public verification without sharing the signing key.

## Worked example

A backend signs a payment configuration with a private key and the app verifies it using a pinned public verification key. That does not authorize a charge: the backend still checks transaction identity. For local encrypted tokens, use authenticated encryption, not an unauthenticated cipher plus plain SHA-256.

## Trade-offs and decision criteria

HMAC is efficient but every verifier with the shared key can forge messages. Signatures support broader verification but require key-distribution and rotation design. Password hashing deliberately costs more computation than ordinary hashes to resist guessing.

## Failure modes

Storing `SHA256(password)` as the password verifier enables fast offline guessing if the database leaks. Encrypting without authentication allows undetected modification. Reusing a GCM nonce under one key can catastrophically weaken security.

## Production perspective

For each security requirement, document the property needed: secrecy, tamper detection, origin proof or password verification. Review algorithms, key ownership, rotation and failure behavior with a security specialist, and use platform libraries rather than custom cryptography.

## Interview answer — short

Encryption provides reversible confidentiality using keys (AES/RSA). Hashing produces an irreversible one-way digest to verify data integrity (SHA-256). HMAC adds a shared secret key to hashing to verify both integrity and authenticity. Digital signatures use asymmetric cryptography (Private/Public key) to provide integrity, authenticity, and non-repudiation.

## Interview answer — structured

Selecting the correct cryptographic primitive depends on whether the security goal is confidentiality, integrity, authenticity, or non-repudiation:

1. **Encryption (Confidentiality - Reversible)**: Transforms plaintext into ciphertext. Requires a key to decrypt back to plaintext. Symmetric encryption (AES-256 GCM) is fast for local data storage and payload encryption. Asymmetric encryption (RSA/ECC) encrypts data with a public key that only the matching private key can decrypt.

2. **Hashing (Integrity - Irreversible)**: A deterministic, one-way mathematical function mapping arbitrary-length inputs to a fixed-length digest (e.g. SHA-256). Changing a single bit completely changes the hash. Used for APK checksum verification and password hashing (with salt and slow KDFs like Argon2).

3. **HMAC (Keyed Integrity & Authenticity - Symmetric)**: Computes a hash combined with a shared secret key (`HmacSHA256`). Confirms that the message was not modified in transit AND that it was created by an entity possessing the shared secret.

4. **Digital Signatures (Authenticity & Non-Repudiation - Asymmetric)**: Signs a message hash with a private key; verifiable by anyone using the corresponding public key (e.g. ECDSA, RSA). Guarantees **non-repudiation**: the signer cannot claim they didn't author the message, making it mandatory for financial payment authorizations and APK code signing.

## Interview answer — deep senior

Cryptographic Failure Modes in Android Applications:

1. **Using Unauthenticated Encryption (AES-CBC without HMAC)**: Susceptible to **Padding Oracle Attacks** and bit-flipping attacks. Always use **Authenticated Encryption with Associated Data (AEAD)**, specifically **AES-GCM (Galois/Counter Mode)**, which generates a cryptographic authentication tag validating both ciphertext integrity and payload confidentiality.

2. **Hashing Passwords with Fast Hashes**: Using SHA-256 or MD5 for passwords is an immediate security vulnerability because modern GPUs compute billions of SHA-256 hashes per second via rainbow tables. Password hashing must use slow, memory-hard Key Derivation Functions (PBKDF2 with 100,000+ iterations, bcrypt, or Argon2id).

## How to answer in the interview

- **Why:** each primitive solves a different security property.
- **How:** choose encryption for confidentiality, hash for digest, HMAC for shared-key authenticity, signature for public verification.
- **Trade-off:** shared secrets in clients are extractable.
- **Failure case:** treating a plain hash as authentication.
- **Production solution:** keep signing keys server-side and use purpose-specific libraries.

## Deep-dive talking points

Compare confidentiality, one-way digest, keyed integrity and asymmetric authenticity using one concrete Android-to-server message for each primitive.

## Follow-up questions

- **Interviewer:** "What is Non-Repudiation in digital signatures?"
  **Answer:** "The inability of the sender to deny having sent the message, because only their hardware-held private key could have generated the valid signature."

- **Interviewer:** "Why does AES-GCM require a unique IV (Initialization Vector) for every encryption?"
  **Answer:** "Reusing an IV with the same AES key completely destroys GCM security, allowing an attacker to recover both plaintext and the authentication subkey."

## Self-check rubric

Can I pick a primitive for confidentiality, shared-key authentication, public verification and password storage, including nonce/key limitations?

## References and reviewed-on date

- [Android cryptography guidance](https://developer.android.com/privacy-and-security/cryptography) — platform cryptographic practices.
- [OWASP MASVS cryptography](https://mas.owasp.org/MASVS/controls/MASVS-CRYPTO-1/) — algorithm and key controls.

Technically reviewed against primary documentation on 2026-10-13.
