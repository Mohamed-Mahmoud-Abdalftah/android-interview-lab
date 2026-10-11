---
id: ARC-Q013-ANSWER
question_id: ARC-Q013
status: reviewed
---
# ARC-Q013 — Complete model answer

<p dir="rtl" lang="ar">لو حفظت entity ثم التطبيق مات قبل outbox، المستخدم يشوف تعديل لن يصل للserver. لو حفظت outbox وحدها، worker تبعت عملية لا تطابق local state. transaction واحدة تجعل data والintent يظهروا معًا أو لا يظهروا، وبعد restart worker تكمل بأمان.</p>

**Spoken answer:** “The entity and outbox represent one user intent. A single transaction prevents crash windows where visible data has no sync work or queued work has no matching local state.”

**Common wrong answer:** Writing the entity and then enqueueing in memory, assuming the process remains alive between both steps.

**Follow-up 1:** Does a database transaction make the remote write atomic too? No. Remote delivery is another transaction boundary and needs idempotency and reconciliation.

**Follow-up 2:** Why use a stable mutation identity? Retries and worker restarts can then return the same remote result instead of applying the effect twice.

**Rubric:** Explain both crash windows, local atomicity, remote boundary, stable identity, and restart behavior.
