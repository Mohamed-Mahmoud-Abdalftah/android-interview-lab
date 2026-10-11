---
id: KOT-Q021-ANSWER
question_id: KOT-Q021
status: reviewed
---
# KOT-Q021 — Complete model answer

<p dir="rtl" lang="ar">لو التحويل مسموح، reference من نوع MutableList&lt;Animal&gt; تقدر تضيف Dog إلى object أصلها موعود إنها تحتوي Cat فقط. ساعتها القراءة من الـoriginal reference تكسر عقد النوع. عشان الـmutable list بتنتج وتستهلك T، Kotlin تخليها invariant. لو العملية قراءة فقط استخدم producer covariant أو projection مناسبة؛ ولو كتابة فقط استخدم consumer contravariant.</p>

**Spoken answer:** “A mutable list both produces and consumes its element type. If a cat list widened to an animal list, the wider reference could insert a dog and violate the original promise. That is why mutable generic containers are invariant unless an operation explicitly restricts direction.”

**Common wrong answer:** Because Cat does not inherit from Animal once it is placed inside a generic type.

**Follow-up 1:** Why can read-only List be covariant? Its public contract produces elements without accepting arbitrary elements for mutation.

**Follow-up 2:** Can a cast safely force the assignment? No, it hides the type violation and lets an incompatible write fail later.

**Rubric:** Explain both read and write positions, the incompatible insertion, and safe directional alternatives.
