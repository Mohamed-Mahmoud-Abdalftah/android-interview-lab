---
id: KOT-Q015-ANSWER
question_id: KOT-Q015
status: reviewed
---
# KOT-Q015 — Model answer

**Spoken answer:** “An init block can throw when an invariant is violated, which is useful for programmer errors. For expected bad external input, I prefer a parsing factory that normalizes and returns a nullable or typed failure. A private constructor controls ordinary callers, but I still test generated copy, reflection and serialization paths that may construct values.”

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> لو caller الداخلي مرّر port غلط، <code dir="ltr">require(port in 1..65535)</code> يطلع الخطأ فورًا. لكن config جاية من خارج التطبيق ممكن تبقى غلط بشكل متوقع؛ <code dir="ltr">parse</code> تنظف الـ host وتتحقق من port وترجع null أو سبب فشل محدد. الـ constructor private يقلل مسارات الإنشاء العادية، و<code dir="ltr">init</code> تحمي invariant لو اتضاف مسار جديد.</p>

**Mechanics:** [Kotlin classes](https://kotlinlang.org/docs/classes.html) documents init validation; [visibility](https://kotlinlang.org/docs/visibility-modifiers.html) documents private constructors. The runnable [EndpointConfig](../../projects/kotlin-jvm-labs/src/main/kotlin/academy/Construction.kt) and [tests](../../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt) check blank/null host, invalid ports and trimmed valid input. All checked 2026-10-10. The example does not perform DNS, TLS or Android network validation.

**Common wrong answer:** “A private constructor proves that any deserialized object is valid.” External mappers and reflection need their own contract tests. **Trade-off:** Nullable parse is compact but loses error detail; a sealed outcome costs more code and supports precise UI messages or telemetry.

**Follow-up 1:** Could a data-class copy bypass a factory? **Depending on the Kotlin version and constructor design, a generated copy can create altered values.** Validate in the constructor or avoid that generated path for a guarded domain type; inspect the pinned compiler behavior.

**Follow-up 2:** Should host validation call the network during init? **No.** Object construction should validate local shape; connectivity is a separate fallible side effect with timeouts, cancellation and ownership outside this value type.

**Fair rubric (10):** 3 invariant path, 3 expected-failure path, 2 alternate creation paths, 2 network-boundary trade-off.
