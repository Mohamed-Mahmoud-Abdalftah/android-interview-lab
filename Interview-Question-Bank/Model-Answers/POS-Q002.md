---
id: POS-Q002-ANSWER
question_id: POS-Q002
status: reviewed
---
# POS-Q002 — Complete model answer

<p dir="rtl" lang="ar">الtimeout تقول إن الرد ما وصلش، لكنها ما تقولش إن الطلب ما وصلش. ممكن provider وافقت والnetwork انقطعت في الرجوع. عرض Declined كذب، وإعادة الطلب بهوية جديدة ممكن تعمل duplicate charge. احتفظ بنفس attempt/idempotency key واعمل reconciliation قبل قرار جديد.</p>

**Spoken answer:** “A timeout is an observation failure, not a business decline. I mark the attempt unknown and reconcile it with the provider using the original idempotency identity.”

**Common wrong answer:** Applying a generic exponential retry policy to financial authorization calls without idempotency semantics.

**Follow-up 1:** When can retry be safe? When the provider contract guarantees idempotency for the same key and the payload is exactly the same.

**Follow-up 2:** What should the cashier see? A clear pending or checking state that blocks duplicate action and offers a defined recovery path.

**Rubric:** Explain ambiguity, duplicate risk, idempotency, reconciliation, and honest user state.
