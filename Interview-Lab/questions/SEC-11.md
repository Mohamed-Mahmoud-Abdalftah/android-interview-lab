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

## Why it matters and how it works

Generate a non-exportable key with encrypt/decrypt purposes, then initialize a Cipher for each encryption so it gets a fresh IV. Store a versioned envelope and use the same IV for decryption, never reuse an IV under the key. Authentication failures are data-integrity or key-loss events, not empty-string defaults.

## Worked example

Illustrative Kotlin call site, assuming a previously generated Keystore AES key and an app-private envelope format: `val cipher = Cipher.getInstance("AES/GCM/NoPadding"); cipher.init(Cipher.ENCRYPT_MODE, key); val sealed = cipher.doFinal(tokenBytes); val iv = cipher.iv`. Persist `iv` and `sealed` atomically with a format version; this is not a complete library implementation.

## Trade-offs and decision criteria

App-level encryption adds implementation and recovery complexity. Avoid storing a secret at all when possible. A replaceable token can be discarded after key loss; irreplaceable user data needs a separate recovery design outside device-bound Keystore.

## Failure modes

Using a fixed GCM IV or writing ciphertext without its tag breaks security or recovery. Backing up encrypted bytes but not the key creates undecipherable data. Test interrupted writes, tampering, logout, reinstall and backup restore.

## Production perspective

A production token store writes a versioned envelope atomically, excludes unrecoverable ciphertext from backup, redacts errors, and clears invalid tokens before re-authentication. The backend owns token revocation and session status.

## Interview answer — short

“I use a Keystore AES key with AES-GCM, a fresh IV per encryption, and a versioned ciphertext envelope. I plan for key loss and never treat local encryption as server authorization.”

## Interview answer — structured

“Keystore protects the key material, while the app still needs a correct encryption format. For a small replaceable secret I generate an AES key with restricted purposes, encrypt with AES-GCM and a unique IV, and persist the IV, ciphertext, tag and version together. I handle authentication failure or missing key by clearing the token and asking the user to sign in. Backup rules must not restore ciphertext without its key. I avoid designing custom crypto if a reviewed library or platform option meets the same requirements.”

## Interview answer — deep senior

“The trust model matters more than the API call. I minimize local secret retention, then define a versioned AEAD envelope and atomic storage semantics. Keystore may be hardware backed but I check actual properties; plaintext remains visible to the app while used. I test nonce uniqueness, corrupted ciphertext, partial writes, rotation from old aliases, process death and restore to a new device. A refresh token is replaceable through a controlled login flow, so I fail closed on invalidation. The service still checks session validity and can revoke tokens; a compromised client can observe a token during use, so encryption is defense in depth.”

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

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
