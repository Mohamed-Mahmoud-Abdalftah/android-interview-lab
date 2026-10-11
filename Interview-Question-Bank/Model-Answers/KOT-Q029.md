---
id: KOT-Q029-ANSWER
question_id: KOT-Q029
status: reviewed
---
# KOT-Q029 — Complete model answer

<p dir="rtl" lang="ar">أثبت contract الأول: “first repeated in input order” معناها أول position تقابل قيمة شوفتها قبل كده. nested loops تحافظ على العقد، أسوأ زمنها <code dir="ltr">O(n²)</code> ومساحتها <code dir="ltr">O(1)</code>. HashSet تمشي مرة واحدة، زمنها المتوقع <code dir="ltr">O(n)</code> ومساحتها <code dir="ltr">O(n)</code>، وتحافظ على معنى أول repeated position. Sorting تكلف <code dir="ltr">O(n log n)</code> وقد تغير input؛ والأهم إن adjacent duplicate بعد sort لا تعطي تلقائيًا أول repeated position في الترتيب الأصلي من غير metadata إضافية.</p>

**Spoken answer:** “I define the semantic requirement before choosing the data structure. Nested comparison preserves input order but has quadratic worst-case time. A hash set returns the first value encountered twice in expected linear time with linear extra space. Sorting can reduce comparison complexity but either mutates or copies the input and can lose the original-order meaning unless I keep indices.”

**Common wrong answer:** Sort and return the first adjacent duplicate; it is always equivalent to the first repeated value in original order.

**Follow-up 1:** Why qualify hash-set time as expected? It relies on expected constant-time hashing and a reasonable distribution; adversarial collisions and implementation details affect guarantees.

**Follow-up 2:** When might nested loops be the better engineering choice? With a small enforced bound, severe memory constraints, simple value equality and tests documenting that bound.

**Rubric:** Define first repeated position, give all three trade-offs, mention mutation/order, and qualify hash behavior.
