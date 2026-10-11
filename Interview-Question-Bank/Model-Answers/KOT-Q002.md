---
id: KOT-Q002-ANSWER
question_id: KOT-Q002
status: reviewed
---
# KOT-Q002 — Model answer

**Spoken answer:** “An unannotated Java return is a platform type, so Kotlin cannot enforce the same null contract. I assign it to `String?`, validate it once, and expose a safe domain result. I test null and blank responses from a fake SDK.”

<p dir="rtl" lang="ar"><strong>الشرح بالمصري:</strong> Java method من غير nullability annotation بتدخل Kotlin كـ platform type. الـ compiler بيسمح باستدعاء مباشر، لكن ده مش وعد إن القيمة مش null. استقبلها <code dir="ltr">String?</code> وافحصها عند الـ boundary، وبعدها خلّي باقي التطبيق يتعامل مع نتيجة واضحة.</p>

**Mechanics:** `String!` is IDE/compiler notation, not Kotlin source syntax. Platform types relax null checks; a direct call may fail at runtime. `val raw: String? = LegacyProfileApi.nameFor(id)` makes uncertainty explicit. Then `ProfileName.parse(raw)` handles null and blank separately. [Kotlin Java interop](https://kotlinlang.org/docs/java-interop.html), checked 2026-10-10. [Runnable example](../../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileName.kt).

**Common wrong answer:** “Assign it to `String` and the compiler guarantees the SDK.” An assertion may instead fail at runtime. **When not to use a default:** A required legal/payments identity should surface a typed failure, not silently become `Guest`.

**Follow-up 1:** Would trustworthy Java nullability annotations help? **Yes,** Kotlin can map recognized annotations to nullable or non-null types, but annotations must match runtime behavior and compiler settings.

**Follow-up 2:** Could `!!` be justified? **Only** if an independently established invariant says null is impossible and a deliberate immediate failure is desired. It does not make a poorly documented vendor API trustworthy.

**Fair rubric (10):** 3 platform type, 3 explicit boundary conversion, 2 validation/test, 2 product semantics. Version caveat: exact annotation interpretation depends on recognized annotations and compiler configuration; not assumed here.
