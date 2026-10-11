---
id: LAB-009
lesson_id: UI-001
status: reviewed
code_verification: tested
---
# LAB-009 — Stable row identity and detached snapshot

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> عرّف immutable <code dir="ltr">NoteRow(id, title)</code> ودالتين: <code dir="ltr">sameRow</code> للهوية عبر ID، و<code dir="ltr">sameRowContent</code> للمحتوى المعروض. أضف <code dir="ltr">snapshotRows</code> تنسخ outer list حتى لا تتغير snapshot بعد تعديل source list. جرّب قبل <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/NoteRow.kt">reference implementation</a>.</p>

**Acceptance cases:** [Four JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/NoteRowTest.kt) cover same ID/new title, different ID/same title, visible content change and detached outer list. The row fields are immutable strings; if nested mutable data is introduced, extend the snapshot contract and tests.

<p dir="rtl" lang="ar"><strong>حدود التمرين:</strong> هذه دوال JVM عادية، مش <code dir="ltr">DiffUtil.ItemCallback</code> فعلية. اشرح كيف ستوصلها في Android adapter لاحقًا، وكيف تنظف Fragment binding في <code dir="ltr">onDestroyView</code>. راجع <a dir="ltr" href="../Real-World-Scenarios/SCN-010-stale-recyclerview-binding.md">السيناريو</a> لتفصل diff bug عن lifecycle bug.</p>

**Complexity:** Identity/content comparison here O(length of compared strings) in worst case; copying n row references takes O(n) time and O(n) outer-list space. The copy is shallow. No RecyclerView performance measurement was run.

**Verification:** Run `./gradlew clean test check run --no-daemon` in `projects/kotlin-jvm-labs` and inspect [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). Optional rubric (10): 3 identity, 2 content, 2 snapshot, 2 Android integration limits, 1 complexity. No score or timer is required.
