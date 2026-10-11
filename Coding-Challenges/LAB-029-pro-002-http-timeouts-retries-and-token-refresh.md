---
id: LAB-029
lesson_id: PRO-002
status: reviewed
code_verification: tested
---
# LAB-029 — HTTP, timeouts, retries and token refresh boundary model

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> حوّل أهم قرار في الدرس لـpure Kotlin contract، وابدأ بtest للحل الغلط. استخدم <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt">CompletionModels.kt</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt">CompletionModelsTest.kt</a>. اشرح بوضوح إن النموذج لا يشغل Android framework أو backend.</p>

**Cases:** valid, malformed, duplicate, stale identity, boundary values, no mutation, and one permanent failure. Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon`.

**Interview extension:** State the invariant and complexity or delivery guarantee, then propose the Android/integration test that closes the remaining evidence gap.
