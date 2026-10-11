---
id: KOT-Q011-ANSWER
question_id: KOT-Q011
status: reviewed
---
# KOT-Q011 — Model answer

**Spoken answer:** “Kotlin interleaves property initializers and init blocks in their source order. In this example normalization records property:Ada, validation records init, and the later label initializer records label:ADA. If require fails, construction throws before the later initializer runs.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> ما تجمعش كل الـ properties في مرحلة منفصلة عن <code dir="ltr">init</code>. هنا أول initializer تعمل <code dir="ltr">trim</code> وتسجل <code dir="ltr">property:Ada</code>، بعدين كتلة <code dir="ltr">init</code> تسجل نفسها وتفحص القيمة، وبعدها <code dir="ltr">label</code> تتعمل. لو الاسم مسافات، <code dir="ltr">require</code> ترمي exception، فـ <code dir="ltr">label</code> مش بتتنفذ.</p>

**Mechanics:** The order follows declarations in the class body; this is documented by [Kotlin classes](https://kotlinlang.org/docs/classes.html), checked 2026-10-10. The local [JUnit trace](../../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt) checks both the valid order and early termination. The event list is a test probe, not an endorsed mutable constructor dependency in production.

**Common wrong answer:** “All properties initialize first, then all init blocks.” That changes the predicted trace and can hide reads before validation. **Trade-off:** Keep initialization short and side-effect-light; a factory is easier when parsing external input can fail normally.

**Follow-up 1:** What if a second init block appears after label? **It runs after label, if earlier validation succeeded.** Kotlin interleaves it at its written position instead of moving all init blocks together.

**Follow-up 2:** What can an observer see after require throws? **No successfully constructed instance is returned.** Side effects already performed before the exception, such as appended diagnostic events, still happened; avoid external side effects in partial construction.

**Fair rubric (10):** 4 exact order, 2 blank path, 2 contract/evidence distinction, 2 side-effect caveat. No Android runtime claim.
