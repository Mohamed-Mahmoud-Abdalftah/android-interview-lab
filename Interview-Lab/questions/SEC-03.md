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

## Practical walkthrough

في checkout، password يثبت هوية المستخدم وقت login، access token يحمل صلاحية محدودة للـAPI، refresh token يبدله، وAPI key عامة ممكن تعرّف تطبيق خرائط. مفتاح التشفير يحمي بيانات أو يوقّع challenge. كل واحد له دورة حياة مختلفة: logout يبطل refresh token من السيرفر، لكن تدوير encryption key محتاج migration للبيانات المشفّرة.

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

“I separate secrets by purpose and authority. A password authenticates the user and should never be stored plaintext. Access tokens are scoped, short-lived session credentials; refresh tokens need tighter storage and server revocation. API keys may be public mobile identifiers or privileged provider credentials, depending on the provider contract. Cryptographic keys encrypt or sign and have a different rotation problem. In a fintech app I keep high-authority provider keys on the backend and document expiry, storage and recovery for each credential.”

## Interview answer — deep senior

“I classify credentials by who issues them, what authority they carry, and how they are revoked. A password proves user knowledge at login and is never stored as plaintext. A short-lived access token carries delegated API access; a refresh token extends the session and needs server rotation and revocation. An API key may only identify a mobile project, or it may be a privileged provider secret that must stay on the backend. Cryptographic keys encrypt or sign data and need their own rotation plan. For a payment app I would document these lifecycles separately, because rotating a session token is very different from migrating ciphertext under a new key. An interview answer should also cover incident response. If a refresh token leaks, revoke its session and rotate tokens; if an embedded provider secret leaks, rotate it at the provider and inspect abuse; if an encryption key is lost, migrate or recover ciphertext rather than merely issuing a new token. A credential inventory with owner, privileges, expiry and recovery path makes these actions executable instead of theoretical.”

## How to answer in the interview

- **Why:** calling everything a secret hides its authority.
- **How:** classify each by issuer, storage, scope, expiry, rotation, and revocation.
- **Trade-off:** shorter sessions improve exposure limits but add refresh traffic.
- **Failure case:** shipping a privileged provider key in an APK.
- **Production solution:** server-own private keys and rotate/revoke sessions explicitly.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
