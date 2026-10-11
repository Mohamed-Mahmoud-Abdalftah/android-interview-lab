---
id: POS-Q004-ANSWER
question_id: POS-Q004
status: reviewed
---
# POS-Q004 — Complete model answer

<p dir="rtl" lang="ar">أنشئ business payment intent وهوية attempt واضحة، ومرر idempotency key ثابتة لنفس العملية من التطبيق للbackend/provider. state machine تسمح outcome نهائية واحدة، والbackend تخزن request/result atomically حسب عقدها. retry بنفس payload والkey ترجع نفس النتيجة، بينما محاولة جديدة تحتاج قرار صريح بعد reconciliation.</p>

**Spoken answer:** “I carry one business identity through every layer, make provider submission idempotent, persist the resulting transition atomically, and reconcile unknown attempts before creating a new charge.”

**Common wrong answer:** Deduplicating only by UI button state, which disappears after restart and does not cover backend retries.

**Follow-up 1:** Is an attempt ID the same as an order ID? Usually no; one order can have controlled multiple attempts, while each attempt has one outcome lifecycle.

**Follow-up 2:** What if identical keys arrive with different amounts? Reject the conflict and alert; silently accepting a changed payload breaks idempotency meaning.

**Rubric:** Include business and attempt identity, stable key, atomic persistence, payload consistency, terminal state, and reconciliation.
