---
id: "SEC-03"
question: "Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 300
editorial_status: "reviewed"
---

# SEC-03

## Original interview question

Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords.

## What the interviewer evaluates

- Purpose, lifetime, exposure and rotation of five credential types.
- Why a bearer token is not a cryptographic key and an APK API key is not a secret.

## Explanation in Arabic

Cryptographic key بتستخدم في encrypt/sign؛ password سرّ المستخدم للتحقق ومينفعش يتخزن plaintext؛ access token غالبًا bearer قصير العمر للـAPI؛ refresh token أطول عمرًا ويجيب tokens جديدة؛ API key بتعرّف تطبيق أو مشروع حسب سياسة الـprovider، ومش لازم تثبت هوية مستخدم. خلطهم يخلّي team يخزن token في logs أو يفترض إن API key داخل APK سرّ مستحيل يتسرب.

## Why it matters and how it works

Each credential has a distinct issuer, verifier, scope and revocation path. Passwords are verified server-side with an appropriate salted password-hashing scheme. Access/refresh tokens are issued and checked by the identity backend. Cryptographic keys may be generated in Android Keystore. A public mobile API key can identify a project but needs server restrictions and quotas.

## Worked example

In a checkout app, the backend authenticates the user and issues scoped access/refresh credentials. The app stores only what it needs; the refresh token is replaceable through sign-in and never enters logs. The payment-provider private key remains on the server. A bundled map-service identifier is restricted by provider controls, not treated as confidential.

## Trade-offs and decision criteria

Short access-token lifetimes limit exposure but increase refresh traffic. Refresh-token rotation improves revocation visibility but requires race handling. Keystore protects a local encryption key; it does not turn a bearer token into proof of device integrity.

## Failure modes

Putting a provider secret in BuildConfig ships it in the APK. Recording Authorization headers leaks bearer tokens. Reusing one symmetric key for unrelated purposes complicates rotation. Keep private provider operations behind a backend and use per-credential lifecycle rules.

## Production perspective

Document a credential inventory: owner, storage location, scope, lifetime, rotation, incident response. Build a redaction policy and server revocation endpoint. Test expired tokens, refresh races and logout across devices.

## Interview answer — short

“Keys perform cryptographic operations; passwords authenticate users; access and refresh tokens represent delegated sessions; API keys identify a client or project under a provider contract. I give each a separate storage, scope and rotation policy.”

## Interview answer — structured

“The key distinction is who verifies and revokes the credential. A password is a user secret checked server-side, an access token is typically a short-lived bearer authorization artifact, and a refresh token obtains new access tokens and needs stronger lifecycle controls. A cryptographic key performs encryption or signing, often using Keystore locally. An API key in a mobile binary can be extracted, so private provider credentials belong on the backend. I never log any of these values.”

## Interview answer — deep senior

“For a fintech app I start with a threat inventory rather than call everything a secret. I separate identity proof, session delegation and cryptographic operations. Access tokens get narrow scopes and expiry; refresh tokens get server-side revocation, rotation and race-safe handling; Keystore keys can protect necessary local data but cannot make client decisions authoritative. Passwords stay out of app persistence after login and are hashed with a suitable server scheme. Public API identifiers may be shipped with restrictions, while private payment credentials stay server-side. Incident response differs: revoke a token, rotate an API key, or re-enroll a device-bound key.”

## Deep-dive talking points

Classify each credential by issuer, holder, scope, revocation and lifetime; explain why an APK API key is not equivalent to a backend private key.

## Follow-up questions

- [SEC-05](../sec-05/): Can an embedded API key be confidential? **Answer:** no; assume extraction and restrict or proxy it.
- [SEC-14](../sec-14/): How is a refresh token revoked? **Answer:** invalidate its server-side session/grant and clear local copies.

## Self-check rubric

Can I name issuer, verifier, lifetime, storage, and revocation for each of the five credential types?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key operations.
- [OWASP MASVS authentication](https://mas.owasp.org/MASVS/controls/MASVS-AUTH-1/) — authentication controls.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
