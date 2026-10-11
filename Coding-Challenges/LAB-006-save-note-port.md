---
id: LAB-006
lesson_id: ARC-001
status: reviewed
code_verification: tested
---
# LAB-006 — Save a note through a narrow port

<p dir="rtl" lang="ar"><strong>المطلوب:</strong> نفّذ <code dir="ltr">Note(id, title)</code> و<code dir="ltr">NoteWriter.upsert</code> و<code dir="ltr">SaveNote</code>. الـ use case تنظف input، ترفض ID أو title فارغين قبل أي write، ثم تنادي writer مرة وتعيد note. خطأ writer لازم يظهر للـ caller. حاول الحل قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/SaveNote.kt">reference implementation</a>.</p>

**Acceptance cases:** [JUnit tests](../projects/kotlin-jvm-labs/src/test/kotlin/academy/SaveNoteTest.kt) verify normalized valid input and one delegation, two invalid-input branches with zero calls, and propagated writer failure. Use a recording fake and a failing fake. No Android SDK, Room or network is required.

<p dir="rtl" lang="ar"><strong>قرار التصميم:</strong> ليه use case تحتاج write-only port بدل Database class؟ إيه معنى success؟ هل failure بعد partial write ممكن تتعالج هنا؟ ناقش حدود العقد قبل توسيع interface. راجع <a dir="ltr" href="../Real-World-Scenarios/SCN-006-note-save-success-lie.md">سيناريو النجاح الوهمي</a>.</p>

**Complexity and limits:** Trimming ID and title of lengths n and m is O(n+m) time and may allocate O(n+m) output. One writer call follows; its I/O cost and atomicity are outside this pure use case bound. A fake proves delegation, not disk durability.

**Verification:** Run `./gradlew clean test check run --no-daemon` in `projects/kotlin-jvm-labs`, inspect JUnit XML and [BUILD-VERIFICATION](../BUILD-VERIFICATION.md). The optional rubric is 3 validation, 2 normalization, 2 one-call delegation, 2 error propagation, 1 contract explanation. No timer or score is required.
