---
id: LAB-008
lesson_id: SYS-001
status: reviewed
code_verification: tested
---
# LAB-008 — Pair search with explicit invariants

<p dir="rtl" lang="ar"><strong>المطلوب الأول:</strong> نفّذ <code dir="ltr">pairIndicesForTarget(values: IntArray, target: Int)</code> ترجع original indices لعنصرين مختلفين أو null، من غير تعديل input. اختَر أول pair بحسب second index في المسح. استخدم map لأول index لكل قيمة، وامنع overflow بحساب complement في Long.</p>

<p dir="rtl" lang="ar"><strong>المطلوب الثاني:</strong> نفّذ <code dir="ltr">pairValuesInSorted</code> على input مرتبة تصاعديًا أو متساوية، بعد فحص الشرط. ارجع values بدل indices، باستخدام two pointers وLong sum. لو input غير مرتبة ارمِ <code dir="ltr">IllegalArgumentException</code>. اكتب invariant قبل الحل؛ جرّب قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/PairSearch.kt">reference implementation</a>.</p>

**Executable cases:** [Seven JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/PairSearchTest.kt) cover original indices/nonmutation, duplicates, false overflow match, valid extremes, deterministic first match, sorted success and no pair/invalid order. The [scenario](../Real-World-Scenarios/SCN-008-overflow-batch-pair.md) gives a production-style investigation.

**Complexity:** Hash map: O(n) expected time under suitable hash distribution and O(n) extra space. Sorted two pointers including validation: O(n) time and O(1) extra space. Sorting an unsorted input first changes costs and original-index semantics; do not hide that precondition.

**Verification:** Run `./gradlew clean test check run --no-daemon` in `projects/kotlin-jvm-labs` and inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). Optional rubric (10): 2 contract, 2 invariants, 2 duplicates/no solution, 2 overflow, 2 complexity/assumptions. No timer or score is required.
