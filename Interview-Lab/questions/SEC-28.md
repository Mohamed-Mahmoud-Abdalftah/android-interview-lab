---
id: "SEC-28"
question: "An embedded TLS certificate expires. How do you rotate pins without bricking the app?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "C"
phase: 3
priority: "P1"
order: 325
editorial_status: "reviewed"
---

# SEC-28

## Original interview question

An embedded TLS certificate expires. How do you rotate pins without bricking the app?

## What the interviewer evaluates

- Certificate expiry versus pin set, release uptake and emergency plan.
- No insecure fallback during a pin mismatch.

## Explanation in Arabic

لو certificate embedded كpin وانتهت أو اتبدلت key، النسخ القديمة ممكن تفقد الاتصال حتى لو الشهادة الجديدة valid. نستخدم public-key pins بمفتاح backup مختلف، ننشره قبل switch، نختبر أقدم app مدعوم، ونراقب الأخطاء. صلاحية pin في config مش magic fix؛ لو انتهت هتقل الحماية. ما نفتحش trust-all عشان نرجع الخدمة.

## Practical walkthrough

لو شهادة TLS انتهت، ده غير إن SPKI اتغيّرت. لو pin على public key والrenewal احتفظ بنفس key، pin قد تفضل صالحة؛ لو key اتبدلت، النسخ القديمة تحتاج backup pin مشحونة مسبقًا. اعمل جدول فيه app versions والـpins اللي كل نسخة تعرفها ومواعيد انتهاء الشهادات. ما تستخدمش trust-all كـemergency fix؛ ده يحوّل outage لثغرة.

## Why it matters and how it works

Pinning requires both normal TLS validation and membership in an accepted pin set. A renewed certificate under the same public key may keep an SPKI pin valid, whereas key rotation needs prepublished new key material. Old installed clients cannot be patched through the failed TLS channel.

## Worked example

Before an October certificate renewal, ship an app version carrying current and backup SPKI hashes, wait for measured adoption, test against staging with the backup key and the oldest supported APK, then rotate the server gradually. Keep a separately controlled recovery key.

## Trade-offs and decision criteria

Certificate pins are simple to reason about but change more often; public-key pins can ease certificate renewal but require secure key lifecycle. Pinning adds outage risk, so assess whether it is justified over standard TLS.

## Failure modes

A cert expires Friday and the app only pins its exact DER certificate. Monday checkout fails. The corrective path is a prepared overlap or app update, not disabling trust validation remotely.

## Production perspective

Keep a version-to-pin inventory, expiry alerts, rollout gates and old-client traffic metrics. Test offline/install-old-app recovery and communicate supported-version policy before relying on pins for critical payments.

## Interview answer — short

“I avoid a single expiring certificate pin. I prepublish a backup public-key pin, test old clients before server rotation, and keep a controlled update path; I never recover by accepting arbitrary certificates.”

## Interview answer — structured

“A pin mismatch can make a valid new certificate unusable to old apps. I distinguish a certificate renewal from public-key rotation, ship backup pins ahead of the change and test the oldest supported release against the new chain. Then I stage the server switch while monitoring failures by app version. Expiry and rollback policies are designed in advance. Normal TLS validation stays enabled throughout. ”

## Interview answer — deep senior

“This is an operational dependency across release and infrastructure teams. I track which binaries trust which keys, maintain backup key custody outside the primary certificate path, and rehearse rotation before expiry. If an incident requires emergency key change, the prepublished backup enables continuity; otherwise I may need a store-delivered app update and a service incident, not a trust-all override. I also verify the chosen Android/library pinning semantics, including pin-set expiration, on the production network stack. The backend still treats every request as untrusted. Keep a separately controlled recovery key. Monday checkout fails.  I would rehearse the renewal with a matrix of app versions, pins and certificate chains, including a client whose update is delayed. If the public key is unchanged, renewal may not require a new SPKI pin; if key material changes, the backup must already be in those old binaries. An emergency app release cannot instantly reach every user, so operational overlap is essential. I would reject a trust-all bypass even under outage pressure.”

## How to answer in the interview

- **Why:** old binaries may reject a valid rotated chain.
- **How:** distinguish certificate renewal from key rotation, predeploy backup SPKI, and test oldest supported builds.
- **Trade-off:** operational overlap needs long planning.
- **Failure case:** single embedded certificate pin expires.
- **Production solution:** versioned trust matrix, staged rollout, and tested update path.

## Deep-dive talking points

Prompt for SPKI versus exact-cert pin, overlap order, old-client matrix, emergency backup and secure failure.

## Follow-up questions

- [SEC-20](../sec-20/): What is the safe rotation order? **Answer:** client backup first, server switch later.
- [SEC-08](../sec-08/): Why not always pin? **Answer:** outage risk may outweigh incremental CA-risk reduction.

## Self-check rubric

Can I explain why expiry bricks clients and give a safe ordered recovery plan?

## References and reviewed-on date

- [Android Network Security Configuration](https://developer.android.com/privacy-and-security/security-config) — pin sets and expiration.
- [OWASP MASVS network](https://mas.owasp.org/MASVS/controls/MASVS-NETWORK-2/) — endpoint identity.

Technically reviewed against the cited primary documentation on 2026-10-13; this is an automated editorial and technical review, not a human review.
