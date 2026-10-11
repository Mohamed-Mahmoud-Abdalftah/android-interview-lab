---
id: ARC-Q014-ANSWER
question_id: ARC-Q014
status: reviewed
---
# ARC-Q014 — Complete model answer

<p dir="rtl" lang="ar">أبدأ بمعنى البيانات وتكلفة الفقد. server version تكشف conflict. Last-write-wins تصلح لبيانات قليلة الخطورة لو الوقت موثوق، field merge لو الحقول مستقلة، manual merge لو المحتوى مهم، وoperations مالية لها authority مختلفة ولا تُدمج كنص. أحافظ على النسختين لحد القرار.</p>

**Spoken answer:** “Conflict policy is a product rule. I detect conflicts with server versions, preserve both pieces of evidence, and choose overwrite, field merge, manual resolution, or rejection based on data semantics.”

**Common wrong answer:** Applying device-timestamp last-write-wins universally, despite clock skew and silent data loss.

**Follow-up 1:** When is field-level merge unsafe? It is unsafe when fields share invariants or the combined result was never valid as one user intent.

**Follow-up 2:** What should telemetry record? Record privacy-safe conflict type, versions, age, and resolution outcome, not sensitive field contents.

**Rubric:** Cover detection, preserved evidence, domain semantics, options, clock risk, and observability.
