---
id: "SEC-20"
question: "How do you implement certificate pinning with a rotation/recovery strategy?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 317
editorial_status: "reviewed"
---

# SEC-20

## Original interview question

How do you implement certificate pinning with a rotation/recovery strategy?

## What the interviewer evaluates

- Coordinated server/client pin rotation with rollback and old-client support.
- Difference between public-key pin and certificate lifetime.

## Explanation in Arabic

Pinning لو اتعمل بpin واحد ممكن شهادة جديدة تقطع كل مستخدمين النسخ القديمة. الخطة: أجهّز backup public key مستقلة، أشحنها في app قبل أي server switch، أختبر overlap، وبعد انتشار النسخ أبدّل certificate/keys تدريجيًا. متابعة errors وrollback مدروس. ما نعملش trust-all fallback؛ ده يهدم الهدف.

## Practical walkthrough

خطة pinning تبدأ قبل انتهاء certificate بشهور: شحن current SPKI ومعاه backup key مختلفة في التطبيق، ثم اختبار أقدم نسخة مدعومة مع server chain الجديدة. `expiration` في Network Security Config بيوقف pinning بعد التاريخ، فده fallback availability له ثمن أمني؛ قراره لازم واعي. لو فشل rollout، ما تفتحش trust-all، بل استخدم backup/تحديث signed مضبوط ومراقبة أخطاء.

## Why it matters and how it works

A pin set accepts selected public keys/certificates in addition to normal TLS validation. Old binaries cannot learn an emergency new pin after their network path is broken. Therefore prepublished backup pins, key custody and update cadence must be decided before enabling enforcement.

## Worked example

Timeline: release v1 with current and backup SPKI pins; verify uptake and old-version traffic; activate server certificate using the backup key on a staging endpoint; run old-client tests; roll production gradually; later ship a new backup before retiring the prior one. This is an operational example.

## Trade-offs and decision criteria

Pinning narrows CA trust but creates availability dependency on release adoption. Pin expiry can prevent permanent bricking in some platform configurations, but it weakens enforcement after expiry and must not be the sole recovery plan.

## Failure modes

New server cert uses an unknown key: TLS chain is valid, pin check fails, checkout dies. Fix is a planned key overlap or controlled app update, not disabling hostname verification or accepting all certificates.

## Production perspective

Assign owners to pin inventory, certificate expiry, signing/release process and telemetry. Exercise rotation in staging with oldest supported APK and monitor pin failure by app version without logging personal data.

## Interview answer — short

“I deploy current and backup pins before changing server keys, test old clients and monitor the rollout. A trust-all fallback is unacceptable; pinning needs an availability and recovery plan from day one.”

## Interview answer — structured

“Pinning constrains which server keys an app accepts beyond ordinary TLS validation. I choose public-key pins, maintain a separately controlled backup, ship both before server rotation, and verify old supported releases against the new chain. Then I stage server activation and monitor failures. Because an old app cannot fetch a new pin after pin failure, I plan overlap, update adoption and rollback beforehand. The backend still validates every financial request. ”

## Interview answer — deep senior

“I treat pins as distributed configuration with a lead time longer than certificate renewal. I maintain a matrix of app versions, accepted SPKI hashes, backend certs and sunset dates. I test staging and production canaries through real TLS stacks, including old devices and alternate endpoints, and ensure backup key custody is independent. If the main key is compromised, I can move to the prepublished backup; if both are unusable, recovery may require an app update through another channel, not a silent trust-all path. I decide whether this outage risk is justified before adopting pinning. This is an operational example.  The recovery strategy should be written before rollout: who holds the backup key, how old binaries are tested, what telemetry triggers a pause, and which app versions still need support. I would simulate the primary key being unavailable and verify that the backup chain works through the real TLS stack. Pin expiration is an availability fallback that turns off pinning after its date; it should be a conscious risk decision, never a hidden substitute for rotation.”

## How to answer in the interview

- **Why:** pinning couples mobile release cadence to server certificates.
- **How:** ship current and backup SPKI pins before rotation and test old binaries.
- **Trade-off:** pin expiry preserves availability by disabling pinning later.
- **Failure case:** emergency key change with no deployed backup.
- **Production solution:** rotation matrix, canary rollout, and monitored recovery.

## Deep-dive talking points

Prompt for prepublished backup key, oldest-client test, cert/key distinction, emergency recovery and pin-failure telemetry.

## Follow-up questions

- [SEC-08](../sec-08/): What does pinning add? **Answer:** accepted-key restriction after normal TLS validation.
- [SEC-28](../sec-28/): How do you avoid bricking old clients? **Answer:** overlap current and backup pins before rotation.

## Self-check rubric

Can I draw the deployment order and describe failure/recovery without weakening TLS?

## References and reviewed-on date

- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — pin sets and expiration.
- [OWASP MASVS network](https://mas.owasp.org/MASVS/controls/MASVS-NETWORK-2/) — endpoint identity.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
