---
id: LAB-005
lesson_id: COR-001
status: reviewed
code_verification: tested
---
# LAB-005 — Profile card in a structured scope

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ <code dir="ltr">suspend fun loadProfileCard</code> تستقبل function معلقة للاسم، وأخرى لعدد badges، و<code dir="ltr">CoroutineDispatcher</code> متحقن. ارجع <code dir="ltr">ProfileCard</code> بعد اكتمال الاثنين. شغّل المصدرين كأطفال تحت caller، وخلي الخطأ يظهر، وإلغاء parent يوصل للأطفال. جرّب قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileCard.kt">reference implementation</a>.</p>

**Contract:** Profile and badges are independent. Do not return a partial card. Do not use GlobalScope. The dispatcher is supplied by the caller so the test can control scheduling. Use a parent-bound scope and await both results. The [JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileCardTest.kt) are executable acceptance cases; the project pins coroutines core/test 1.11.0.

<p dir="rtl" lang="ar"><strong>حالات الحافة:</strong> profile يخلص قبل badges؛ badges تخلص قبل profile؛ أحد المصدرين يرمي خطأ؛ parent تتلغى والاثنان لسه مستنيين. استخدم <code dir="ltr">CompletableDeferred</code> وtest scheduler بدل <code dir="ltr">Thread.sleep</code>. راجع <a dir="ltr" href="../Real-World-Scenarios/SCN-005-orphan-refresh.md">السيناريو</a> لمعنى ownership في شاشة حقيقية.</p>

**Trade-offs and complexity:** Two children add scheduling and error policy. For independent work, elapsed wall time can approach the slower branch, but this lab does not benchmark speed. Total work remains the sum of the two sources; memory includes their Deferred state and results. If the second source depends on the first, sequential code is clearer.

**Verification:** Run `./gradlew clean test check run --no-daemon` from `projects/kotlin-jvm-labs`, inspect JUnit XML and [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). This JVM test does not verify Android lifecycle, actual IO dispatcher saturation or network cancellation.

**Optional rubric (10):** 2 parent ownership, 2 both results, 2 failure propagation, 2 cancellation, 1 injected dispatcher, 1 precise distinction between suspend and background work. No timer or score is required.
