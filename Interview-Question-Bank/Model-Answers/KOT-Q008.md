---
id: KOT-Q008-ANSWER
question_id: KOT-Q008
status: reviewed
---
# KOT-Q008 — Model answer

**Spoken answer:** “`first == second` is true because the data class generates equality from its primary-constructor `id`. `first === second` is false because these are two constructed instances. `first === alias` is true because `alias` points to `first`. I use `==` for value semantics and reserve `===` for a real identity question.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> <code dir="ltr">==</code> في Kotlin بيفحص الـ <code dir="ltr">equals()</code> بشكل آمن مع <code dir="ltr">null</code>؛ والـ <code dir="ltr">data class</code> هنا بتولّد مقارنة على <code dir="ltr">id</code> اللي في الـ primary constructor. عشان كده <code dir="ltr">first == second</code> صح، لكن <code dir="ltr">===</code> بيسأل هل المرجعين لنفس النسخة؛ <code dir="ltr">first</code> و<code dir="ltr">second</code> نسختين مختلفتين، و<code dir="ltr">alias</code> هي نفس <code dir="ltr">first</code>.</p>

**Mechanics:** Kotlin translates `a == b` into a null-safe equality check based on `equals(Any?)`. A data class normally generates `equals()` and `hashCode()` from properties in its primary constructor. `===` tests whether references identify the same object. The prompt constructs distinct `Candidate` instances, avoiding string-pooling or boxed-primitive identity assumptions. [Kotlin equality](https://kotlinlang.org/docs/equality.html) and [data classes](https://kotlinlang.org/docs/data-classes.html), checked 2026-10-10.

**Common wrong answer:** “`==` compares memory addresses in Kotlin.” That describes the default `equals` behavior of a class with no value equality override, not the operator's general contract. **When to use `===`:** When the question really is whether two references point to one object, such as checking an exact sentinel instance.

**Follow-up 1:** What if `first: Candidate?` is null and `second` is not? **`first == second` is false without throwing.** If both are null, it is true. `==` handles the nullable left operand rather than calling a method on null.

**Follow-up 2:** Can `==` compare arrays element by element? **Ordinary array equality is not the element comparison most interviewers intend.** Use `contentEquals` for elements in the same order; use `contentDeepEquals` for nested arrays when its semantics fit the data.

**Fair rubric (10):** 3 three trace outcomes, 3 operator semantics, 2 null safety, 1 array caveat, 1 appropriate identity use. Kotlin/JVM object-instance example; no Android claim.
