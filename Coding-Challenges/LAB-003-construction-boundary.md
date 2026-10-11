---
id: LAB-003
lesson_id: KOT-003
status: reviewed
code_verification: tested
---
# LAB-003 — Constructor order and validated config

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ <code dir="ltr">ConstructionTimeline</code> تسجل ترتيب property initializers و<code dir="ltr">init</code> وsecondary body، ثم <code dir="ltr">EndpointConfig.parse</code> تقبل host غير فاضي وport من <code dir="ltr">1..65535</code> بعد <code dir="ltr">trim</code>. جرّب الحل قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/Construction.kt">reference implementation</a>.</p>

**Starter contract:** In the existing Kotlin/JVM project, create a class with constructor inputs raw: String and events: MutableList<String>. Record normalization before an init block, validate a nonblank normalized name, then set an uppercase label. Add a secondary constructor with a prefix and record its body last. For config, use a class with host, port and authority(), plus a parse(rawHost, port) factory returning null on invalid input. [JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/ConstructionTest.kt) are the executable acceptance cases. No Android SDK or network is needed.

<p dir="rtl" lang="ar"><strong>حالات الحافة:</strong> input فيه مسافات حول اسم صالح، اسم كله مسافات، host null أو blank، port صفر أو أكبر من 65535. الـ trace لازم تثبت إن <code dir="ltr">require</code> الفاشلة تمنع تهيئة label وجسم secondary. ما تستدعيش <code dir="ltr">open</code> method أثناء base construction؛ راجع <a dir="ltr" href="../Real-World-Scenarios/SCN-003-open-constructor-dispatch.md">سيناريو SCN-003</a>.</p>

**Approaches and complexity:** Direct source-order initializers make the trace easy to review. A factory keeps expected parsing failure outside the constructor while init remains a last defense. Trimming a string of length m is O(m) time and can allocate O(m) output; record appends are O(1) amortized for this small in-memory list. No performance benchmark was run.

**Verification:** From projects/kotlin-jvm-labs run ./gradlew clean test check run --no-daemon. Inspect JUnit XML and [BUILD-VERIFICATION](../BUILD-VERIFICATION.md) for the observed count; do not infer pass from source alone. The incorrect open-dispatch sketch is conceptual and is not a reference solution.

**Optional rubric (10):** 3 exact event order, 2 early failure, 2 factory rejection cases, 2 valid normalization, 1 explanation of constructor visibility. Learning Mode keeps the solution visible and has no required timer or score.
