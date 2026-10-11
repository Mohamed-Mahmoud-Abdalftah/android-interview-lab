---
id: LAB-018
lesson_id: COR-002
status: reviewed
code_verification: tested
---
# LAB-018 — Supervised batch without swallowed cancellation

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> استقبل list من suspending tasks مستقلة. شغّلها كأطفال تحت <code dir="ltr">supervisorScope</code>، وارجع result بنفس ترتيب input. النجاح يحمل value، والـfailure المتوقعة تحمل message. لو الـparent اتلغى لازم الإلغاء يطلع للcaller، مش يتحول لعنصر error.</p>

**Interview constraints:** Do not use `GlobalScope`. Do not detach jobs. Do not catch `Throwable` without preserving cancellation. Explain whether tasks are safe to retry and why output order differs from completion order.

**Red phase that was observed:** The first implementation used `runCatching` and the cancellation test failed because `CancellationException` became `ChildResult(error=...)`.

**Correct implementation:** [CompletionModels.kt](../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt) rethrows cancellation before mapping ordinary failures.

**Tests:** [CompletionModelsTest.kt](../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt) proves sibling isolation and parent cancellation. Run `./gradlew test --tests academy.CompletionModelsTest --no-daemon` inside `projects/kotlin-jvm-labs`.

**Follow-up:** Add a request generation to every task and reject results from an older generation without changing cancellation behavior.
