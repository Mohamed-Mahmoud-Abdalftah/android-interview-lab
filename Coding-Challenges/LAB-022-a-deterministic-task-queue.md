---
id: LAB-022
lesson_id: COR-006
status: reviewed
code_verification: tested
---
# LAB-022 — A deterministic task queue

<p dir="rtl" lang="ar"><strong>Contract:</strong> نفّذ queue تشغّل snapshot من المهام الجاهزة؛ task تضيف task جديدة لا تتنفذ في نفس runCurrent. اختبر الترتيب والـnested scheduling. النموذج يشرح scheduler semantics ولا يدّعي إنه بديل لـkotlinx-coroutines-test.</p>

**Code:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt)

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt)

Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Interview extension:** State the invariant, complexity or delivery guarantee before changing the implementation. Add one failure test that rejects a plausible wrong solution.
