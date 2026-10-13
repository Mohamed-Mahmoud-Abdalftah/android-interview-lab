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

## Practical walkthrough

في تطبيق بنك، TLS يحمي request وهي ماشية للشبكة، لكن بعد وصول الرد الـtoken ممكن يتكتب في cache أو log. تشفير الملف بمفتاح Keystore يحمي نسخة الـbytes على القرص في بعض التهديدات، لكنه ما يمنعش hook يشوف plaintext وقت الاستخدام. اعمل data-flow يحدد الأماكن اللي السر بيظهر فيها، وقلل التخزين والاحتفاظ قبل اختيار التشفير.

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

“At-rest encryption protects stored bytes; TLS protects traffic between the app and server when certificate and hostname validation remain enabled. I first minimize what is stored, then use Keystore-backed app encryption where the threat model justifies it and define recovery if the key disappears. Neither layer hides plaintext during processing or repairs a log leak. I test the actual release network policy, backup and restore behavior, and keep authorization on the backend.”

## Interview answer — deep senior

“I map the data’s lifetime before picking encryption. TLS with valid certificate and hostname checks protects traffic between app and server, while local encryption can reduce exposure of stored bytes. Neither stops a hook from reading a token when the app uses it, and TLS does not remove plaintext from a log or crash report. For a banking flow I would minimize stored credentials, keep keys in Keystore where justified, define key-loss behavior, and test a restore. I would also verify that release traffic rejects invalid certificates and cleartext paths. Backend authorization remains independent of both encryption layers. I would distinguish Android's device storage encryption from app-managed encryption: the former is platform protection, while the latter introduces key format and migration obligations. A file encrypted under a device-bound key may be unrecoverable after backup restore. For network transport I would test the actual release Network Security Config, redirects and certificate failure behavior, not just inspect an HTTPS base URL in source.”

## How to answer in the interview

- **Why:** network and storage expose different attack windows.
- **How:** use validated TLS for transit and a justified local encryption design for stored data.
- **Trade-off:** local encryption creates key-loss and backup obligations.
- **Failure case:** plaintext leaks through logs or memory after decryption.
- **Production solution:** minimize retained data and test both network and restore paths.

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

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
