---
id: "SEC-26"
question: "Design secure session storage for a fintech app on a potentially compromised device."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 323
editorial_status: "reviewed"
---

# SEC-26

## Original interview question

Design secure session storage for a fintech app on a potentially compromised device.

## What the interviewer evaluates

- Session storage on a hostile endpoint with explicit residual risk.
- Token scope, refresh races, revocation and high-risk action step-up.

## Explanation in Arabic

على جهاز ممكن يكون compromised، مفيش local storage يخلي bearer token غير قابل للسرقة وقت الاستخدام. نقلل الضرر: access token قصير ومحدود، refresh token يُخزّن فقط لو session persistence مطلوبة، Keystore-backed protection وbackup exclusions، server rotation/revocation، وstep-up للعمليات الحساسة. أي payment decision لازم server-side.

## Why it matters and how it works

Keystore raises extraction cost for a local wrapping key, but hooks can observe tokens when decrypted or sent. The server owns grant validity and can bind risk signals to a session, enforce limits and revoke it. Refresh must be single-flight in one process and tolerate unknown network outcomes without resurrecting old sessions.

## Worked example

A transfer app stores a replaceable refresh token in app-private, encrypted storage and keeps access tokens in memory. On launch it refreshes under a session-generation lock; if the key is unavailable it asks for login. For a large transfer it gets fresh server challenge/step-up, not a local “biometric passed” Boolean.

## Trade-offs and decision criteria

Durable sessions improve usability but extend exposure. Hardware-backed protection, if available, may help against offline extraction, not runtime compromise. Stronger step-up adds friction; use risk tiers and accessible recovery.

## Failure modes

An attacker hooks token-read code and captures a bearer token despite encryption. An old refresh response arrives after logout and restores the session. Enforce server revocation and compare session generation before committing any refresh result.

## Production perspective

Monitor session anomalies, provide per-device revocation, minimize scopes, and test rooted/hooked devices, backup restore and process death. Never log token values. Payment state is independently reconciled by the backend.

## Interview answer — short

“On a possibly compromised device, I minimize token lifetime and scope, protect only necessary durable credentials, and rely on server revocation and step-up. Keystore helps against extraction but cannot stop runtime hooks.”

## Interview answer — structured

“I design assuming client storage may be inspected. Access tokens are short-lived and preferably memory-only; a refresh token persists only when needed, with app-private storage, Keystore-backed encryption, backup policy and key-loss sign-in. The server rotates and revokes grants, while local refresh is serialized and guarded against logout races. Sensitive payments require a server-validated challenge and normal authorization. Integrity signals can adjust risk but never establish absolute trust.”

## Interview answer — deep senior

“I would split threats: offline file extraction, runtime hooking, stolen bearer credentials and forged transaction requests. Keystore and encrypted storage target the first; short token lifetime, server rotation/revocation and anomaly detection limit the second and third. The backend independently checks account ownership, amount, transaction state and idempotency for the fourth. A refresh response is committed only if the session generation still matches, preventing resurrection after logout. Process death and key invalidation lead to explicit re-authentication, and offline logout blocks local use while remote revocation remains pending. I document that a fully compromised endpoint can observe plaintext at use time.”

## Deep-dive talking points

Prompt for four threat classes, session-generation race, key-loss recovery, server revocation and step-up limits.

## Follow-up questions

- [SEC-14](../sec-14/): How is refresh coordinated? **Answer:** single-flight locally plus server rotation policy.
- [SEC-29](../sec-29/): Can rooted-device checks guarantee safety? **Answer:** no; use risk signals and server policy.

## Self-check rubric

Can I describe storage, runtime residual risk, refresh/logout races and server authorization?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — local key limits.
- [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) — risk signals.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
