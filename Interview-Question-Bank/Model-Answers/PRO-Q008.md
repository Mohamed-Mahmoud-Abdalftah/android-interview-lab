---
id: PRO-Q008-ANSWER
question_id: PRO-Q008
status: reviewed
---
# PRO-Q008 — Complete model answer

<p dir="rtl" lang="ar">الكود ماسك transaction خلال network latency، وده يطول lock ويخلط atomicity محلية بفشل remote. كمان entity وoutbox مش مكتوبين كوحدة واحدة، فـcrash بينهم يضيع intent. أصححها بـtransaction قصيرة تكتب entity والحالة Pending وoutbox بنفس mutation ID، وبعدها worker يعمل network خارج transaction. لما الرد يرجع، transaction جديدة تطبق النتيجة فقط لو mutation/version ما زالت الحالية. WAL يساعد القراءة تتداخل مع writer لكنه لا يبرر network داخل transaction.</p>

**Spoken answer:** “I atomically persist the local state and durable outbox, then close the transaction. A worker performs the remote call outside the database lock. A second short transaction conditionally applies the response using mutation or version identity, which also rejects stale completions.”

**Common wrong answer:** Enable WAL so the long transaction no longer blocks or risks inconsistency.

**Follow-up 1:** What if the server succeeds and the response is lost? Retry the same stable idempotency identity and keep the local mutation pending until an authoritative result arrives.

**Follow-up 2:** Why conditionally apply the response? A newer local edit may exist, so an older completion must not overwrite the current user intent.

**Rubric:** Identify long locks, atomic entity/outbox write, network separation, stable identity, and stale-result protection.
