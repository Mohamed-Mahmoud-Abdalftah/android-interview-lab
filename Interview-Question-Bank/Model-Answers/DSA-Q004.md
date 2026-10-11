---
id: DSA-Q004-ANSWER
question_id: DSA-Q004
status: reviewed
---
# DSA-Q004 — Complete model answer

<p dir="rtl" lang="ar">لو distance كبيرة واتجمع عليها weight، <code dir="ltr">Long</code> ممكن تلف لقيمة سالبة فتظهر كأنها route أرخص. قبل الجمع افحص إن <code dir="ltr">distance &lt;= Long.MAX_VALUE - weight</code>. والأفضل كمان domain bounds ووحدات واضحة عند ingestion، لأن رقم ضخم غالبًا data error.</p>

**Spoken answer:** “A wrapped sum can become negative and incorrectly win relaxation. I guard addition and enforce meaningful domain bounds and units before the algorithm runs.”

**Common wrong answer:** Assuming `Long` is large enough and therefore cannot overflow in adversarial or synthetic input.

**Follow-up 1:** Should overflow silently clamp to `Long.MAX_VALUE`? Only if the API contract defines saturation; otherwise reject or skip with observable diagnostics.

**Follow-up 2:** Would `BigInteger` always be better? It prevents overflow but adds cost and does not fix invalid units or a broken graph contract.

**Rubric:** Describe corruption, pre-add guard, domain validation, observable policy, and trade-offs.
