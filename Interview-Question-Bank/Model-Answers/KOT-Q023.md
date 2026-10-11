---
id: KOT-Q023-ANSWER
question_id: KOT-Q023
status: reviewed
---
# KOT-Q023 — Complete model answer

<p dir="rtl" lang="ar"><code dir="ltr">List&lt;*&gt;</code> تقول إن فيه element type محددة لكنها مجهولة للـcaller، لذلك القراءة الآمنة <code dir="ltr">Any?</code>. <code dir="ltr">List&lt;Any?&gt;</code> عقدها إن element type نفسها Any?، مش مجرد مجهولة. الفرق أوضح مع mutable types: star projection تمنعك تضيف قيمة arbitrary لأن الـobject الحقيقي ممكن تكون MutableList&lt;String&gt;. لو محتاج تعرف النوع، اعمل parsing أو token صريح.</p>

**Spoken answer:** “A star projection preserves that some concrete type exists while hiding what it is. I can read values as `Any?`, but I cannot assume a specific element type or write arbitrary values. `List<Any?>` explicitly declares `Any?` as the element type.”

**Common wrong answer:** A star projection converts every element to `Any?` and removes all original type constraints.

**Follow-up 1:** When is a star projection useful? For inspection, logging, counting, or routing that does not require the concrete element type.

**Follow-up 2:** Can you cast List<*> to List<String>? The cast is unchecked under erasure, so validate every element or use a typed serializer.

**Rubric:** Explain unknown concrete type, safe reads, restricted writes, and the difference from explicit Any?.
