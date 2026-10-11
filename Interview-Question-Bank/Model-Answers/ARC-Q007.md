---
id: ARC-Q007-ANSWER
question_id: ARC-Q007
status: reviewed
---
# ARC-Q007 — Complete model answer

<p dir="rtl" lang="ar"><strong>الإجابة بالمصري:</strong> UDF تنظّم الاتجاه: actions تدخل للـ state holder، وهي تنتج state، والـ UI ترسمها. ده يقلل أماكن التعديل العشوائي ويخلي transition قابلة للتتبع والاختبار. لكنها مش lock ولا transaction. طلبين network ممكن يرجعوا بترتيب مختلف، collector قديمة ممكن تفضل شغالة لو lifecycle غلط، وكتابتين database ممكن يتعارضوا.</p>

<p dir="rtl" lang="ar">عشان تمنع stale update محتاج identity أو version لكل طلب وسياسة واضحة: هل تلغي القديم؟ هل latest wins؟ هل تجمع النتائج؟ في معمل editor، reducer تقبل completion لو ID تطابق الطلب الحالي. ده يمنع رسالة UI غلط، لكنه لا يلغي I/O قديمة ولا يرجّع كتابة حصلت فعلًا. مصدر الحقيقة لازم يُقرأ أو يحصل reconciliation بعد التعارض.</p>

**Spoken answer:** “UDF gives me one traceable direction for actions and state. It does not serialize asynchronous work. I still need request identity, cancellation or conflict policy, and lifecycle ownership.”

**Common wrong answer:** “A single StateFlow automatically eliminates races.” A StateFlow serializes state publication, while producers and external operations may still race.

**Follow-up 1:** When is latest-wins the wrong policy? It is wrong when every operation matters, such as payments or queued uploads; use explicit ordering and idempotency instead.

**Follow-up 2:** How would you prove a stale result is ignored? Use a deterministic test that starts two identified operations, completes the first late, and asserts the second state is unchanged.

**Rubric:** Separate direction of data from serialization, name a concrete race, and propose a testable conflict policy.
