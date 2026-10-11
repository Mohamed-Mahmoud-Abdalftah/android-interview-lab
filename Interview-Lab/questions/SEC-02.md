---
id: "SEC-02"
question: "What is Android Keystore, and what is hardware-backed key storage?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 299
editorial_status: "reviewed"
---

# SEC-02

## Original interview question

What is Android Keystore, and what is hardware-backed key storage?

## What the interviewer evaluates

- Difference between non-exportable key material and encrypted application data.
- Hardware-backed capability checks and their device-dependent limits.

## Explanation in Arabic

Android Keystore بيولّد أو يستورد cryptographic keys تحت alias، والـapp يطلب عملية تشفير أو توقيع بدل ما يحتفظ بالـraw key في ملف. بعض الأجهزة تنفذ العملية داخل TEE أو StrongBox، لكن ده مش مضمون لكل key أو device. الـplaintext بيفضل يظهر للـapp وقت الاستخدام؛ Keystore ما بتحولش الجهاز المخترق إلى trusted client.

## Why it matters and how it works

KeyGenParameterSpec limits purposes, algorithms, user-auth requirements and, where supported, hardware properties. AndroidKeyStore mediates operations without exporting key material. Inspect KeyInfo/security level when a hardware guarantee is part of the threat model; do not infer hardware backing merely from the provider name.

## Worked example

Example design: create an AES-GCM key under a versioned alias, generate a fresh random IV per encryption, store IV plus ciphertext and tag in an app-private file, and exclude unrecoverable ciphertext from backup. On decryption failure, classify the data: reissue a token or recover irreplaceable data through a separate verified process. This is an architectural sketch.

## Trade-offs and decision criteria

Hardware-backed keys can raise the cost of extraction, but availability, authentication behavior and StrongBox support vary. Server-held secrets avoid shipping a secret at all; local encryption is useful only for data that must reside locally.

## Failure modes

Assuming a Keystore key survives reinstall or backup restore breaks decryption: app keys are ordinarily removed with the app and not transferred. Another error is using AES-GCM with a repeated IV under the same key. Test key loss and rotate with versioned ciphertext.

## Production perspective

A banking app uses Keystore for a local token-encryption key, verifies device capability only if policy requires it, excludes incompatible encrypted blobs from backup, and falls back to re-authentication after key loss. Backend token revocation and authorization remain decisive.

## Interview answer — short

“Android Keystore lets an app use keys without exporting their key material. Hardware backing may strengthen that protection, but I check actual capabilities and still design ciphertext format, backup, rotation, and recovery.”

## Interview answer — structured

“I use AndroidKeyStore to generate a key with restricted purposes and, if needed, authentication constraints. The app passes data to cryptographic operations; some devices protect key material in a TEE or StrongBox. I verify the key properties rather than assume hardware backing. For AES-GCM I store a unique IV with authenticated ciphertext and plan for key loss on restore or reinstall. Keystore protects keys, not a compromised runtime or server decisions. The practical design still needs an authenticated ciphertext format: store a fresh IV with each AES-GCM result, version the envelope and decide what happens when the key is unavailable. I would verify hardware properties only when policy depends on them. A restored token file without its original key should lead to sign-in, not a silent empty value.”
## Interview answer — deep senior

“I separate three concerns: where key material lives, how application ciphertext is formatted, and who authorizes the business action. Keystore addresses the first and can restrict use, but plaintext enters the app during an operation and device implementations differ. I would validate algorithm and security level for the threat model, bind ciphertext to a version and unique nonce, test migration and invalidation, and never back up ciphertext expecting the original device key to reappear. For replaceable tokens, re-authentication is usually safer than fragile recovery. A server must still validate every privileged request. I would separate key protection from application data protection and business authorization. AndroidKeyStore can restrict a key’s purpose and may execute operations in TEE or StrongBox, depending on device capability; I would inspect actual key information instead of assuming it. The app still handles plaintext during a cryptographic call and must choose a unique IV, authenticated mode, versioned storage and atomic write. Backup or reinstall can leave ciphertext without a usable key, so a replaceable session token triggers reauthentication and server revocation as needed. For irreplaceable local data, recovery must be designed before encryption. I would test tampering, interrupted writes, rotation and restore on supported devices, while keeping all payment decisions on the backend.”
## Deep-dive talking points

Explain where Keystore key material is generated and used, when hardware protection is available, and what a compromised client can still observe.

## Follow-up questions

- [SEC-11](../sec-11/): What must be stored beside AES-GCM ciphertext? **Answer:** a version, unique IV and authenticated output, with recovery policy.
- [SEC-13](../sec-13/): What if a key disappears? **Answer:** classify the protected value and invoke a designed reissue or recovery path.

## Self-check rubric

Can I distinguish key material from ciphertext, state hardware limits, describe AES-GCM IV handling, and explain restore and server-trust boundaries?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key protection and operations.
- [KeyGenParameterSpec](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec) — key constraints.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
