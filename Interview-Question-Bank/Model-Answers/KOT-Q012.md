---
id: KOT-Q012-ANSWER
question_id: KOT-Q012
status: reviewed
---
# KOT-Q012 — Model answer

**Spoken answer:** “A primary-constructor parameter without val or var is an input to construction, not automatically a stored property. Adding val stores a read-only property that members and callers can access according to visibility. I often normalize raw input and store only the validated value.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> <code dir="ltr">class User(name: String)</code> عنده input اسمه <code dir="ltr">name</code> وقت التهيئة، لكن مش property يقدر caller يقرأها بعدين. <code dir="ltr">class User(val name: String)</code> بتعرّف property. لو جاي input من Java أو network، ممكن تستقبل raw parameter وتخزن نسخة normalized بعد validation بدل الاحتفاظ بالـ raw value، عشان ما تخلّيش حالتين متعارضتين داخل الكائن.</p>

**Mechanics:** Kotlin [class documentation](https://kotlinlang.org/docs/classes.html) distinguishes constructor parameters from properties and shows explicit assignment when a parameter must be retained. [Visibility modifiers](https://kotlinlang.org/docs/visibility-modifiers.html) determine who can access the stored property. Both pages checked 2026-10-10. This does not prove the source was trustworthy; validation remains a separate decision.

**Common wrong answer:** “Every constructor argument becomes a field.” That assumes storage Kotlin did not declare. **Trade-off:** Retain raw input only when audit or error reporting truly needs it, with privacy and ownership considered; otherwise keep one canonical representation.

**Follow-up 1:** Does val make a stored object deeply immutable? **No.** It limits reassignment of the property; an object such as a mutable list can still change through its own methods or another alias.

**Follow-up 2:** Can a plain constructor parameter be used in an init block? **Yes, during construction.** If a later member function must use it, assign it to a property or derive a stored value explicitly.

**Fair rubric (10):** 4 parameter/property distinction, 2 normalization, 2 visibility, 2 mutability caveat.
