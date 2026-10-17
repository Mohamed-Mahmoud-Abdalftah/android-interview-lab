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

## Concept and technical explanation

Modern cryptography provides four fundamental mathematical primitives, each addressing distinct security objectives: confidentiality, integrity, authenticity, and non-repudiation. Encryption transforms plaintext into ciphertext using a key, providing confidentiality; it is reversible when the corresponding decryption key is possessed. Encryption is divided into symmetric ciphers (such as AES-GCM, where the same key is used for both operations, making it extremely fast for bulk data) and asymmetric ciphers (such as RSA or ECC, where a public key encrypts and a private key decrypts). Hashing is a one-way mathematical function (such as SHA-256) that maps arbitrary-length inputs to a fixed-size digest, providing integrity verification; it uses no keys and cannot be reversed. HMAC (Hash-based Message Authentication Code) combines a cryptographic hash with a shared secret key, providing both integrity and authenticity; it verifies that the message has not been tampered with and was produced by an entity holding the shared key. Digital signatures combine asymmetric cryptography with hashing; the sender signs a message digest using their private key, and any verifier holding the corresponding public key can verify authenticity, integrity, and non-repudiation.

## Practical walkthrough (English)

Comparing cryptographic primitives implementation in Kotlin:
```kotlin
// 1. Symmetric Authenticated Encryption (AES-GCM): Confidentiality + Integrity
fun encryptAesGcm(plaintext: ByteArray, secretKey: SecretKey): Pair<ByteArray, ByteArray> {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, secretKey)
    val iv = cipher.iv // 12-byte initialization vector
    val ciphertext = cipher.doFinal(plaintext)
    return Pair(iv, ciphertext)
}

// 2. Cryptographic Hash (SHA-256): One-way Integrity check (No Key)
fun computeSha256(data: ByteArray): ByteArray =
    MessageDigest.getInstance("SHA-256").digest(data)

// 3. HMAC (HMAC-SHA256): Symmetric Authenticity + Integrity (Shared Key)
fun computeHmac(data: ByteArray, sharedKey: SecretKey): ByteArray {
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(sharedKey)
    return mac.doFinal(data)
}

// 4. Digital Signature (ECDSA): Asymmetric Authenticity + Integrity + Non-repudiation
fun signPayloadEcdsa(data: ByteArray, privateKey: PrivateKey): ByteArray {
    val signer = Signature.getInstance("SHA256withECDSA")
    signer.initSign(privateKey)
    signer.update(data)
    return signer.sign()
}
```

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

We distinguish four cryptographic primitives by their mathematical goals: encryption uses keys to hide data reversibly for confidentiality, hashing creates fixed one-way digests without keys to check integrity, HMAC combines hashing with a shared secret key for symmetric authenticity, and digital signatures use asymmetric private keys to guarantee authenticity, integrity, and non-repudiation.

## Interview answer — structured

Selecting the correct cryptographic primitive depends strictly on whether the engineering requirement is confidentiality, integrity, authenticity, or non-repudiation.
Encryption provides confidentiality by rendering data unreadable to anyone lacking the decryption key.
It exists as symmetric encryption like AES-GCM, which uses a single shared key for rapid bulk data processing, and asymmetric encryption like RSA, which uses mathematically paired public and private keys.
Hashing provides integrity verification without using any keys.
A cryptographic hash function like SHA-256 takes input of any length and produces a deterministic, fixed-size digest that cannot be reversed, exhibiting an avalanche effect where changing one bit completely alters the digest.
HMAC provides message integrity and authenticity by combining a cryptographic hash function with a pre-shared secret key, proving that the sender possessed the key and the payload was not altered.
Digital signatures provide the highest level of trust by combining asymmetric cryptography with hashing.
The sender hashes the payload and encrypts the digest with their private key; recipients verify the signature using the sender's public key, proving authenticity, message integrity, and mathematical non-repudiation.

## Interview answer — deep senior

In enterprise system design, choosing the wrong cryptographic primitive or misunderstanding its mathematical guarantees introduces catastrophic vulnerabilities.
A classic anti-pattern is storing passwords using raw cryptographic hashes like SHA-256 or MD5.
Because cryptographic hashes are designed for high throughput, attackers can compute billions of guesses per second using GPUs and rainbow tables; password hashing requires slow, memory-hard key derivation functions like Argon2id or PBKDF2 with unique salts.
Another frequent mistake is confusing encryption with authentication.
Using unauthenticated symmetric encryption like AES-CBC without an integrity tag leaves the ciphertext vulnerable to padding oracle attacks and bit-flipping manipulation.
Modern engineering mandates Authenticated Encryption with Associated Data (AEAD), such as AES-256-GCM, which generates an authentication tag alongside the ciphertext to detect tampering.
When comparing HMAC to Digital Signatures, the distinction centers on key distribution and non-repudiation.
HMAC relies on a symmetric shared secret; because both the sender and receiver hold the identical key, either party could mathematically forge the HMAC, meaning HMAC cannot provide legal non-repudiation.
Digital signatures solve this through asymmetric key pairs.
In mobile banking, we use hardware-backed ECDSA keys generated inside Android Keystore.
The client signs a financial transaction digest using its hardware-isolated private key, and the banking server verifies the signature using the registered public key.
Because the private key can never leave the client's secure hardware, the signature provides indisputable cryptographic non-repudiation.

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
