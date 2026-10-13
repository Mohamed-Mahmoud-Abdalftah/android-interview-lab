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

Encryption بتخفي الرسالة ويمكن فكّها بمفتاح؛ hash digest من غير مفتاح ومش بديل لتشفير سر؛ HMAC بتثبت integrity/authenticity بين أطراف شايلة نفس المفتاح؛ digital signature بمفتاح private وتتحقق بـpublic key. Passwords تحتاج password hashing متخصص ومملّح، مش SHA-256 خام. وفي كل الحالات لازم تعرف مين ماسك المفتاح وإيه حدود الثقة.

## Practical walkthrough

لو backend يبعت إعدادات دفع لازم app تتحقق من مصدرها، يوقّعها private key على السيرفر وapp تتحقق بـpublic key. Plain SHA-256 للرسالة مش كفاية لو المهاجم يقدر يبدّل الرسالة والـhash سوا. HMAC يتطلب secret مشترك، فلا تحطّ مفتاح server HMAC في APK. تشفير AES-GCM يحمي السرية وintegrity، لكن مش إثبات قرار دفع من backend.

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

“Encryption protects confidentiality, hashes summarize data, HMAC authenticates with a shared secret, and signatures authenticate with a private/public key pair. Passwords need a dedicated salted password-hashing scheme.”

## Interview answer — structured

“I choose a primitive by the property I need. Encryption protects confidentiality; a plain hash is a digest, not proof of who wrote a message. HMAC authenticates between parties sharing a secret, while a digital signature lets the app verify a server message with a public key without carrying the private key. Passwords need dedicated salted password hashing on the server. For local secrets I use authenticated encryption and vetted platform APIs, not a custom combination of primitives.”

## Interview answer — deep senior

“I first name the property I need. Encryption gives confidentiality, while authenticated encryption such as AES-GCM also detects modification. A plain hash is a digest, not proof of origin when an attacker can replace both data and hash. HMAC authenticates between parties that share a secret; putting the same HMAC key in every APK defeats that trust model. A server can sign a configuration with a private key and let the app verify with a public key. Passwords need a salted password-hashing scheme on the server, not a fast general-purpose hash. I would use vetted APIs and keep all private payment authority off device. A useful design exercise is to ask whether the app must read the message, verify its origin, or both. A public signature can verify server-issued configuration without giving every mobile installation the signing secret. By contrast, encrypting a payload under an app-wide symmetric key shipped in the APK would not establish a private boundary. I would include algorithm, key ownership, and replay handling in the protocol review.”

## How to answer in the interview

- **Why:** each primitive solves a different security property.
- **How:** choose encryption for confidentiality, hash for digest, HMAC for shared-key authenticity, signature for public verification.
- **Trade-off:** shared secrets in clients are extractable.
- **Failure case:** treating a plain hash as authentication.
- **Production solution:** keep signing keys server-side and use purpose-specific libraries.

## Deep-dive talking points

Compare confidentiality, one-way digest, keyed integrity and asymmetric authenticity using one concrete Android-to-server message for each primitive.

## Follow-up questions

- [SEC-11](../sec-11/): Why AES-GCM rather than encryption alone? **Answer:** the authentication tag rejects modified ciphertext.
- [SEC-05](../sec-05/): Can an app hold a shared HMAC signing secret securely? **Answer:** not if it must be extracted from a distributed client.

## Self-check rubric

Can I pick a primitive for confidentiality, shared-key authentication, public verification and password storage, including nonce/key limitations?

## References and reviewed-on date

- [Android cryptography guidance](https://developer.android.com/privacy-and-security/cryptography) — platform cryptographic practices.
- [OWASP MASVS cryptography](https://mas.owasp.org/MASVS/controls/MASVS-CRYPTO-1/) — algorithm and key controls.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
