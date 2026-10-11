---
id: LAB-024
lesson_id: AND-003
status: reviewed
code_verification: tested
---
# LAB-024 — Task and back-stack semantics

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> حوّل قرار الدرس لـpure contract صغيرة، واكتب boundary cases قبل implementation. النموذج موجود في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt">CompletionModels.kt</a> والاختبارات في <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>.</p>

**Interview rule:** Explain what this pure model proves and what still needs Android integration. Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Extension:** Add a malformed input, a stale identity, and a duplicate delivery case. State the invariant before code.
