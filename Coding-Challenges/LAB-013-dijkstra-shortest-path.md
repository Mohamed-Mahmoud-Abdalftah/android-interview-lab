---
id: LAB-013
lesson_id: EXT-DSA-01
status: reviewed
code_verification: tested
---
# LAB-013 — Dijkstra with path reconstruction

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> اكتب shortest path لـ directed graph بأوزان غير سالبة. استخدم min-heap، distance map، parent map، stale-entry guard، وoverflow guard. رجّع distance وnodes أو <code dir="ltr">null</code>. ارفض أي negative weight. اكتب tests قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ShortestPath.kt">reference</a>.</p>

**Acceptance:** [سبعة اختبارات](../projects/kotlin-jvm-labs/src/test/kotlin/academy/ShortestPathTest.kt) تشمل cheapest weighted path، stale entry، unreachable/missing، self، negative، overflow، وdestination-only node. اشرح invariant وcomplexity بصوتك قبل تشغيل الاختبارات.

<p dir="rtl" lang="ar"><strong>امتداد:</strong> أضف tie-break policy ثابتة، ثم قارن BFS على unweighted graph. لا تغير implementation لقبول negative weights؛ اختَر algorithm مناسبة وtests جديدة.</p>

**Complexity:** O((V+E) log E) conservative with lazy heap entries, O(V+E) graph plus distance/parent/queue space. Run `./gradlew clean test check run --no-daemon`.
