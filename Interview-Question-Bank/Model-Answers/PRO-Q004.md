---
id: PRO-Q004-ANSWER
question_id: PRO-Q004
status: reviewed
---
# PRO-Q004 — Complete model answer

<p dir="rtl" lang="ar">App Link verification تثبت association بين domain والتطبيق وقت التوجيه، مش إن كل parameter حقيقة ولا إن المستخدم يملك order. المستخدم يقدر يكتب URL بنفسه. التطبيق يبعت identifier للbackend تحت session الحالية؛ backend تتحقق من ownership وحالة provider والversion، وتتعامل مع التكرار idempotently، ثم ترجع state للعرض.</p>

**Spoken answer:** “Domain verification protects link routing, not payment authority. The backend checks the authenticated user's ownership and the provider-backed order state, then returns the source-of-truth result.”

**Common wrong answer:** Treating a signed application or verified domain as permission to trust all client-supplied business data.

**Follow-up 1:** What if the provider callback is delayed? Show pending and refresh from the backend; define timeout and reconciliation without inventing local success.

**Follow-up 2:** How do you handle replay safely? Use a stable idempotency key and state transition rules that make repeated confirmations produce one business effect.

**Rubric:** Separate association, authentication, ownership, provider state, source of truth, and replay policy.
