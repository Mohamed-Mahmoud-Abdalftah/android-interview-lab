---
id: SCN-012
lesson_id: PRO-003
status: reviewed
code_verification: not_run
---
# SCN-012 — A crafted return link marks an order paid

**Hypothetical security investigation.** Support reports a receipt screen showing “Paid” while the backend order remains pending. No real incident logs or device reproduction are available.

<p dir="rtl" lang="ar">ابدأ بالحفاظ على evidence: app version، مصدر فتح الرابط، sanitized route، order version، وbackend state. ما تسجلش token أو URL كاملة. اختبر فرضيات منفصلة: host comparison بـ <code dir="ltr">contains</code>، Activity exported بلا authorization، status مأخوذة من query، duplicate parameter، أو race بين callback وrefresh.</p>

## Investigation

1. Reproduce with a lookalike host and direct explicit intent in a safe test build.
2. Trace whether UI text came from the link or a backend refresh.
3. Verify App Link association and manifest exposure on a device.
4. Check backend ownership and idempotency with a different account and replayed request.

<p dir="rtl" lang="ar">الإصلاح يبدأ بإزالة authority من الرابط: parser ضيقة ثم lookup على backend تحت session الحالية. اعرض pending لحد ما المصدر الموثوق يرد. اقفل component لو مش محتاجة export، واختبر links المرفوضة. rollout تدريجي مع telemetry لأن تغيير routing ممكن يمنع روابط شرعية قديمة.</p>

The [JVM lab](../Coding-Challenges/LAB-011-trusted-payment-return-link.md) verifies parsing only. A real Android manifest, domain, backend, and payment provider are required before a security fix can be claimed in production.

## Senior follow-ups

1. **Would cancelling the screen request undo a payment?** No; payment authority and idempotency live downstream.
2. **What is the rollback?** Restore the prior route only if it does not reintroduce unauthorized state changes; otherwise use a server-controlled compatibility path.
