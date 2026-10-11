---
id: LAB-020
lesson_id: COR-004
status: reviewed
code_verification: tested
---
# LAB-020 — Choose the stream from its contract

<p dir="rtl" lang="ar"><strong>Contract:</strong> اكتب decision function: لو محتاج current value فالاختيار State؛ لو كل subscribers الحاليين لازم يشوفوا future emissions فالاختيار Event؛ غير كده Query باردة. اشرح إن النموذج يساعد السؤال لكنه لا يختار replay أو persistence بدل requirements.</p>

**Code:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt)

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt)

Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Interview extension:** State the invariant, complexity or delivery guarantee before changing the implementation. Add one failure test that rejects a plausible wrong solution.
