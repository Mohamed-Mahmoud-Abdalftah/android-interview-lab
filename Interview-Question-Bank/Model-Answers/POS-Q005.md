---
id: POS-Q005-ANSWER
question_id: POS-Q005
status: reviewed
---
# POS-Q005 — Complete model answer

<p dir="rtl" lang="ar">تحتاج instrumented lifecycle tests، hardware-in-loop ومصفوفة أجهزة، provider sandbox لapprove/decline/timeout/duplicate، backend idempotency وreconciliation tests، security review للبيانات والمفاتيح، واختبارات واعتمادات scheme/vendor المطلوبة. rollout تدريجي يراقب Unknown وduplicate prevention ووقت الحسم.</p>

**Spoken answer:** “The reducer is one layer. Release evidence also includes Android lifecycle tests, certified hardware and provider scenarios, backend idempotency and reconciliation, security controls, and required scheme or vendor certification.”

**Common wrong answer:** Calling a feature production ready after mocked callbacks produce approved and declined states.

**Follow-up 1:** Which failure injection is most valuable? Drop connectivity before submission, during provider processing, and after provider success but before the client receives it.

**Follow-up 2:** What should logs contain? Use privacy-safe attempt correlation and state transitions, never raw card data, keys, or sensitive protocol payloads.

**Rubric:** Name Android, hardware, provider, backend, security, certification, observability, and staged rollout evidence.
