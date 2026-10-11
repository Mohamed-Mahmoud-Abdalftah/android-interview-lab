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

“I choose the primitive by security goal. A plain hash detects accidental change only when the expected digest is itself trusted; it does not authenticate an attacker-controlled message. HMAC authenticates among parties sharing a key. A digital signature can be verified with a public key without exposing the signer’s private key. Encryption is reversible with a key, and authenticated encryption is preferable when stored secrets need both confidentiality and integrity. Password storage needs a slow, salted scheme, not a general-purpose hash.”

## Interview answer — deep senior

“In a mobile payment design, I first assign key ownership. A server private signing key must not be inside the APK; the app may carry a public verification key. Shared HMAC keys are unsuitable if every untrusted app instance would receive the same forging secret. For local data, an AEAD mode like AES-GCM protects ciphertext integrity, but nonce uniqueness and key-loss recovery are part of the design. A hash is useful for stable identifiers or integrity comparisons only when the expected value is trusted. Password verification belongs server-side with a specialized KDF, unique salts and an upgrade policy.”

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

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
