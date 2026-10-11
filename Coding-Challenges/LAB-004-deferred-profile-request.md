---
id: LAB-004
lesson_id: KOT-004
status: reviewed
code_verification: tested
---
# LAB-004 — Deferred profile request

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ factory اسمها <code dir="ltr">createDeferredProfileRequest</code> تستقبل <code dir="ltr">currentId: () -&gt; String?</code> و<code dir="ltr">request: (String) -&gt; Unit</code> وترجع <code dir="ltr">() -&gt; Boolean</code>. ما تقراش provider وقت إنشاء callback. عند كل invocation اقرأها مرة، اعمل <code dir="ltr">trim</code>، وارجع false من غير إرسال لو ID null أو blank. لو صالحة ابعتها وارجع true. خلّي خطأ request يظهر للـ caller.</p>

**Start here:** Write the function in the Kotlin/JVM project. Keep the [reference implementation](../projects/kotlin-jvm-labs/src/main/kotlin/academy/DeferredRequest.kt) closed until you have a candidate. The [JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/DeferredRequestTest.kt) are executable acceptance cases.

**Edge cases:** A changes to B before invocation; provider returns null; provider returns whitespace; surrounding spaces require normalization; repeated invocations see changing state; request throws. The result Boolean means the request callback was invoked, not that an asynchronous operation succeeded.

<p dir="rtl" lang="ar"><strong>حل محتمل غلط:</strong> <code dir="ltr">val snapshot = currentId()</code> داخل factory. ده يثبّت ID قديمة. حل تاني غلط: تنادي provider مرتين في invocation واحدة؛ لو state اتغيرت بين القراءتين، validation والتنفيذ يختلفوا. اشرح سبب قراءة واحدة، وامتى snapshot تكون مقصودة لعقد مختلف.</p>

**Complexity:** One provider call and at most one request call per invocation. Trimming a string of length n takes O(n) time and may allocate O(n) space; external request cost is outside this bound. No benchmark was run.

**Verification:** Run `./gradlew clean test check run --no-daemon` under `projects/kotlin-jvm-labs`, then inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). The [scenario](../Real-World-Scenarios/SCN-004-stale-profile-callback.md) adds the product-level investigation. This lab is synchronous and cannot validate Android lifecycle, concurrency or network ordering.

**Optional rubric (10):** 3 late read, 2 exactly one provider read, 2 invalid IDs, 1 normalization, 1 exception propagation, 1 clear Boolean contract. Learning Mode has no required timer or score.
