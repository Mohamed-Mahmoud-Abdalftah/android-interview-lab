---
id: KOT-Q005-ANSWER
question_id: KOT-Q005
status: reviewed
---
# KOT-Q005 — Model answer

**Spoken answer:** “A generated data-class `copy` can expose a way to construct a changed value, undermining a private validation factory. For this small type I use an ordinary class with a private constructor and a `parse` function that checks every input. If value semantics are needed, I add them deliberately without exposing an unchecked constructor path.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> <code dir="ltr">data class</code> بتولّد <code dir="ltr">copy()</code>، وفي نسخة Kotlin المستخدمة ظهر تحذير إن <code dir="ltr">copy</code> ممكن تكشف constructor الخاصة. لو عملت factory تتحقق من الاسم ثم سمحت بنسخة جديدة من غير تحقق، الـ invariant اتكسر. class عادية مع private constructor و<code dir="ltr">parse</code> أو تحقق داخل الـ constructor حلّين مختلفين حسب طريقة الفشل المطلوبة.</p>

**Mechanics:** The local Kotlin 2.4.20 compiler warned that a non-public primary constructor is exposed via generated `copy()` and that copy visibility is changing in a future release. The [lab class](../../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt) avoids generated `copy`. This is a verified compiler observation for the pinned version, not a claim that every Kotlin version behaves identically. [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) and [Kotlin Gradle compatibility](https://kotlinlang.org/docs/gradle-configure-project.html), checked 2026-10-10.

**Common wrong answer:** “Private constructor alone proves every instance valid.” Generated members and deserializers need separate review. **When not to use a custom class:** If the value needs no invariant, an ordinary data class may be simpler.

**Follow-up 1:** Could you add `require(value.isNotBlank())` in the constructor? **Yes.** That validates even generated copy calls, though callers then get an exception rather than a parse result; decide deliberately.

**Follow-up 2:** Does `private constructor` protect against reflection/deserialization? **No absolute guarantee.** Treat serialization and reflection as separate trust boundaries and validate decoded input.

**Fair rubric (10):** 3 copy issue, 3 invariant-preserving alternative, 2 validation failure semantics, 2 trust-boundary caveat. Version caveat: generated `copy` visibility warning observed with Kotlin 2.4.20 on 2026-10-10.
