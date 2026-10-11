---
id: LAB-019
lesson_id: COR-003
status: reviewed
code_verification: tested
---
# LAB-019 — Bounded cooperative batches

<p dir="rtl" lang="ar"><strong>Contract:</strong> قسّم العناصر batches، وارجع فقط الـbatches المكتملة قبل cancellation boundary. ارفض batch size غير موجب، ولا تعدّل input. النموذج pure يثبت boundary الحسابية؛ توصيل ensureActive الحقيقي موضح في الدرس ويحتاج coroutine integration test.</p>

**Code:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt)

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt)

Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Interview extension:** State the invariant, complexity or delivery guarantee before changing the implementation. Add one failure test that rejects a plausible wrong solution.
