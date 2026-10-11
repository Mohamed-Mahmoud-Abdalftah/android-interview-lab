---
id: "SEC-22"
question: "How do you design biometric-gated access to a Keystore operation?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 319
editorial_status: "reviewed"
---

# SEC-22

## Original interview question

How do you design biometric-gated access to a Keystore operation?

## What the interviewer evaluates

- Authentication prompt, Keystore key authorization and Cipher binding.
- Biometric enrollment/credential fallback and key invalidation limits.

## Explanation in Arabic

Biometric prompt لوحده UI gate؛ لو المطلوب حماية crypto operation لازم key في Android Keystore متقيّدة بـuser authentication، ونربط `Cipher`/`CryptoObject` بـ`BiometricPrompt`. نجاح dialog من غير key policy مش دليل إن secret اتحمى. نوع authenticator، fallback ومدة صلاحية المصادقة لازم تتحدد حسب risk، مع recovery لو key اتبطلت.

## Why it matters and how it works

A KeyGenParameterSpec may require user authentication for key use. For an auth-per-use key, initialize a Cipher and pass it as a CryptoObject to BiometricPrompt; only after a successful result perform the operation. API and authenticator combinations vary across versions, so verify supported combinations for the app’s minimum API and AndroidX Biometric version.

## Worked example

A high-value local signing step creates a Keystore signing key requiring per-use strong authentication. The app signs a server challenge after BiometricPrompt succeeds. The server verifies the signature and still checks the current session and transfer details. The signature is evidence of key use, not user intent by itself.

## Trade-offs and decision criteria

Per-use authentication raises friction but better binds operation to a fresh gesture. Time-window authentication improves convenience but widens the period of permitted use. Device credential fallback and enrollment changes affect recovery and must be tested.

## Failure modes

Calling BiometricPrompt then reading a plaintext token from preferences leaves the token independent of the prompt. An auth-bound key can become invalid, so provide a safe sign-in/re-enrollment path rather than silently bypassing the gate.

## Production perspective

For a fintech flow, threat-model which exact operation needs a gesture; use a server challenge tied to operation ID and amount, a Keystore key with appropriate user-auth policy, and audit without biometric data. Test enrollment change, cancel, lockout and process death.

## Interview answer — short

“I bind a Keystore key operation to BiometricPrompt via CryptoObject when I need cryptographic gating. A dialog alone is only UI control; the backend still authorizes the transaction.”

## Interview answer — structured

“I configure the Keystore key to require user authentication, initialize a Cipher or Signature, and pass it through BiometricPrompt as a CryptoObject where the API combination supports it. After success, the app performs the operation. I choose per-use versus timed authorization based on risk, and plan for enrollment changes, lockout and key invalidation. For a transfer, the server verifies a challenge-bound result and independently checks session and transaction policy. The mechanics matter. A KeyGenParameterSpec may require user authentication for key use. For an auth-per-use key, initialize a Cipher and pass it as a CryptoObject to BiometricPrompt; only after a successful result perform the operation. API and authenticator combinations vary across versions, so verify supported combinations for the app’s minimum API and AndroidX Biometric version.”

## Interview answer — deep senior

“A biometric gate must protect a concrete capability, not merely a screen. I decide whether I need local decryption or a challenge signature, configure KeyGenParameterSpec accordingly, and verify the AndroidX/platform authenticator rules for supported API levels. I bind a fresh server challenge and immutable transfer parameters to the signature so a replay or UI modification cannot approve a different amount. I handle cancellation, lockout, device credential fallback and invalidated keys with explicit re-enrollment. I do not claim that a biometric prompt makes a rooted client trusted; the backend remains authoritative. Consider a concrete case. A high-value local signing step creates a Keystore signing key requiring per-use strong authentication. The app signs a server challenge after BiometricPrompt succeeds. The server verifies the signature and still checks the current session and transfer details. The signature is evidence of key use, not user intent by itself. A failure case illustrates the risk. Calling BiometricPrompt then reading a plaintext token from preferences leaves the token independent of the prompt. An auth-bound key can become invalid, so provide a safe sign-in/re-enrollment path rather than silently bypassing the gate. In production, the response is concrete. For a fintech flow, threat-model which exact operation needs a gesture; use a server challenge tied to operation ID and amount, a Keystore key with appropriate user-auth policy, and audit without biometric data. Test enrollment change, cancel, lockout and process death.”

## Deep-dive talking points

Prompt for auth-bound key, CryptoObject, per-use versus time-window policy, enrollment invalidation and server challenge binding.

## Follow-up questions

- [SEC-13](../sec-13/): What if enrollment invalidates a key? **Answer:** re-authenticate and enroll a new key.
- [SEC-27](../sec-27/): Can a patched UI approve a transfer? **Answer:** backend verifies challenge and transaction state.

## Self-check rubric

Can I distinguish UI gating from cryptographic gating and describe operation-bound verification?

## References and reviewed-on date

- [BiometricPrompt guide](https://developer.android.com/identity/sign-in/biometric-auth) — cryptographic authentication flow.
- [KeyGenParameterSpec](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec) — user-auth key constraints.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
