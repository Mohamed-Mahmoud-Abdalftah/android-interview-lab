---
id: KOT-Q013-ANSWER
question_id: KOT-Q013
status: reviewed
---
# KOT-Q013 — Model answer

**Spoken answer:** “The secondary constructor must delegate to the primary constructor, directly or indirectly. Primary property initializers and init blocks finish before the secondary body. If validation throws, that body does not run. I use a factory when external parsing is expected to fail without an exception.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> الـ secondary مش باب خلفي يتجاوز <code dir="ltr">init</code>. تفويضه للـ primary يخلّي التهيئة والتحقق يحصلوا الأول. في معملنا، <code dir="ltr">secondary:member</code> تظهر بعد <code dir="ltr">label:ADA</code>، لكن مع اسم فاضي مش تظهر خالص لأن <code dir="ltr">require</code> أوقفت construction.</p>

**Mechanics:** [Kotlin constructors](https://kotlinlang.org/docs/classes.html) documents delegation and order; the [JUnit case](../../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt) observes both branches on Kotlin 2.4.20/JDK 17. A default parameter can express a simple optional value with less API surface; a named factory can validate or return a typed failure instead of forcing overloads.

**Common wrong answer:** “Secondary constructor code runs, then this(...) is called.” Its delegation syntax makes the opposite order explicit. **Trade-off:** Use multiple constructors when Java interop or genuinely different construction APIs require them, not merely to avoid a simple default argument.

**Follow-up 1:** Could one secondary constructor delegate through another? **Yes.** The chain ultimately reaches the primary constructor, so its initialization runs before either secondary body finishes.

**Follow-up 2:** Would a thrown init exception be caught inside the secondary body? **No, that body never starts.** Catch at the call site or use a parsing factory that returns an explicit failure value.

**Fair rubric (10):** 4 delegation order, 2 failure branch, 2 alternative choice, 2 indirect delegation.
