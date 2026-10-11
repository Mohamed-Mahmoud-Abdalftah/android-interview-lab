---
id: LAB-015
lesson_id: PRO-001
status: reviewed
code_verification: tested
---
# LAB-015 — Migration coverage planner

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> مثّل كل migration كـ<code dir="ltr">SchemaStep(from, to, label)</code>. اكتب <code dir="ltr">planMigration</code> ترجع أقصر upgrade path معلنة، و<code dir="ltr">missingMigrationStarts</code> ترجع كل installed versions المدعومة اللي مش هتوصل للtarget. ارفض version غير موجبة، backward/no-op edges، label فاضية، وتعريفين لنفس pair.</p>

**Acceptance:** [سبعة اختبارات](../projects/kotlin-jvm-labs/src/test/kotlin/academy/MigrationCoveragePlannerTest.kt) تغطي multi-step، direct path، missing edge، same version، downgrade، definitions فاسدة، وrelease matrix كاملة. ابدأ من tests قبل [reference implementation](../projects/kotlin-jvm-labs/src/main/kotlin/academy/MigrationCoveragePlanner.kt).

<p dir="rtl" lang="ar"><strong>تتبع مطلوب:</strong> ارسم queue والvisited لمسار 1→2→3→4، وبعدها احذف 2→3 واشرح ليه version 1 و2 يفشلوا حسب باقي graph. وضح إن BFS هنا اختيار للـaudit tool، مش وصف لخوارزمية Room.</p>

**Complexity:** Building and searching the graph is O(V + E) time and O(V + E) space. This JVM lab does not execute SQL, Room, SQLite, DataStore or process death. Extend it with Android `MigrationTestHelper` tests before a release claim.
