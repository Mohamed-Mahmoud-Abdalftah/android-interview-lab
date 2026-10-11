---
id: LAB-021
lesson_id: COR-005
status: reviewed
code_verification: tested
---
# LAB-021 — Reject a stale versioned result

<p dir="rtl" lang="ar"><strong>Contract:</strong> استقبل current request ID وcandidate فيها requestId وvalue. رجع value فقط لو IDs متساوية. اختبر القديم والجديد وحدود Long. اشرح إن gate تحمي state لكنها لا توقف الشغل الخارجي.</p>

**Code:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt)

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt)

Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` from `projects/kotlin-jvm-labs`.

**Interview extension:** State the invariant, complexity or delivery guarantee before changing the implementation. Add one failure test that rejects a plausible wrong solution.
