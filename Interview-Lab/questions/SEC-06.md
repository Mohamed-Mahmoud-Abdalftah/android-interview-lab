---
id: "SEC-06"
question: "What are encryption at rest and encryption in transit?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 303
editorial_status: "reviewed"
---

# SEC-06

## Original interview question

What are encryption at rest and encryption in transit?

## What the interviewer evaluates

- Scope of confidentiality for stored bytes and network transport.
- Key handling, TLS endpoint validation, and plaintext at use time.

## Explanation in Arabic

Encryption at rest بتحمي bytes وهي مخزنة، مثل database أو token file، من بعض سيناريوهات فقدان الجهاز أو نسخ الملفات. Encryption in transit بتحمي الاتصال بين app وserver باستخدام TLS مع التحقق من هوية الطرف. الاتنين مهمين لكن مختلفين: TLS ما بتحميش ملف محفوظ، وتشفير الملف ما يمنعش MITM. والـplaintext لازم يظهر وقت الاستخدام في process أو server.

## Why it matters and how it works

At rest, a key and authenticated encryption format protect stored content; Android file-based encryption already provides device-level protection, while app-level encryption may add protection for a specific threat model. In transit, TLS negotiates keys and validates the server certificate chain and hostname. Neither mode authorizes a payment.

## Worked example

For a banking app, use HTTPS with system certificate validation for API traffic, avoid cleartext exceptions, and store only minimal replaceable credentials locally. If app-level encryption is justified, keep its key in Keystore and define restore/key-loss behavior. Validate the backend response and user authorization separately.

## Trade-offs and decision criteria

App-level encryption adds complexity, key rotation and backup failures. Relying only on OS storage may be sufficient for non-sensitive cached data. Pinning is an optional additional network constraint with availability costs; it does not replace TLS validation.

## Failure modes

Disabling TLS validation for a test environment exposes all users if shipped. Backing up app-encrypted files without their device key makes them unreadable. Treat both as test cases: network interception should fail and restore should recover safely.

## Production perspective

Production reviews trace each sensitive field from collection through storage, transport, logs and deletion. Release builds reject cleartext traffic to sensitive endpoints, and telemetry records policy failures without recording secrets.

## Interview answer — short

“At-rest encryption protects stored data; TLS protects data crossing the network. Both have key and recovery requirements, and neither replaces backend authorization or protects plaintext while it is being processed.”

## Interview answer — structured

“I separate two attack windows. Android storage encryption and, if needed, Keystore-backed app encryption reduce exposure of stored bytes. TLS protects requests in transit when certificate and hostname checks remain enabled. I also minimize what is stored and sent, avoid logging secrets, and design for key loss. Pinning can add a constraint for selected endpoints but complicates certificate rotation. Server authorization is independent of both forms of encryption. For each sensitive field I identify both windows. HTTPS with certificate and hostname validation protects transit; Android storage encryption and, where justified, Keystore-backed app encryption protect stored bytes. I minimize retention, exclude incompatible ciphertext from backup and keep authorization independent of encryption.”
## Interview answer — deep senior

“For a payment app I make a data-flow table: where PAN-adjacent metadata and tokens enter, how long they remain, and which service receives them. I use TLS with normal validation, explicitly test that cleartext and invalid certificates fail, and only add pins when the threat model justifies rotation and recovery cost. At rest I minimize sensitive persistence first; if app encryption is needed, use authenticated encryption with a Keystore-protected key, versioned format and restore strategy. Runtime hooks on a compromised device may still observe plaintext, so the server verifies every transaction. On a payment app I would trace a token from receipt through memory, network, local persistence, backup and deletion. TLS protects the connection to a verified endpoint but does not protect a database after download; local encryption protects bytes at rest but plaintext appears while the app uses it. If we add app-level AES-GCM, we own IV uniqueness, key rotation, format version and recovery after key loss. If we add pinning, we also own certificate rollout and outage planning. I would test invalid certificates, cleartext configuration, backup restore and redacted telemetry on release builds. None of these controls makes a client-supplied approval trustworthy; the service must independently authenticate and authorize the financial operation.”
## Deep-dive talking points

Separate on-disk ciphertext from TLS channel protection, identify who holds each key, and explain why neither replaces authenticated authorization.

## Follow-up questions

- [SEC-08](../sec-08/): What does TLS pinning add? **Answer:** an extra accepted-key constraint beyond ordinary chain validation.
- [SEC-23](../sec-23/): What breaks after backup restore? **Answer:** Keystore-bound ciphertext may be unusable.

## Self-check rubric

Can I distinguish the two encryption windows, name plaintext exposure and backup limits, and keep authorization separate?

## References and reviewed-on date

- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — TLS/cleartext and trust settings.
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key protection.

Technically reviewed against the cited primary documentation on 2026-10-11; this is an automated editorial and technical review, not a human review.
