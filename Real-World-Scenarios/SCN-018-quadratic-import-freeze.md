---
id: SCN-018
lesson_id: KOT-006
status: reviewed
code_verification: not_run
---
# SCN-018 — A quadratic import scan freezes large customer files

**Hypothetical incident.** A CSV import validates duplicate IDs with nested loops on the main thread. Internal fixtures contain fewer than 100 rows, but one customer imports 12,000 unique rows. Release users report an ANR-like freeze, and the first theory blames ART optimization.

## Investigation

<p dir="rtl" lang="ar">ثبت الـinput size والـthread والـvariant والوقت اللي الـtrace واقفة فيه. راجع loop counters أو sampling profile بدل اسم runtime عام. في unique input، nested implementation تعمل تقريبًا <code dir="ltr">n(n-1)/2</code> مقارنة؛ عند 12,000 عنصر ده حوالي 72 مليون مقارنة قبل تكاليف parsing والرسم. قارن debug/release بنفس الملف، لكن ما تعتبرش فرق الزمن سببًا لو stack والـoperation count بيقولوا إن algorithm نفسها بتكبر تربيعيًا.</p>

1. Reproduce with sanitized files at 100, 1,000, 5,000 and 12,000 rows.
2. Record the executing thread, CPU samples, elapsed stage times and comparison count.
3. Separate parsing, duplicate detection, persistence and UI rendering.
4. Confirm the contract: report the first repeated ID in import order and never mutate the parsed rows.

## Repair

<p dir="rtl" lang="ar">استخدم set للـIDs اللي اتشافت وارجع أول ID يتكرر. اعمل validation خارج main thread لو الملف كبير، بس تغيير dispatcher لوحده ما يصلحش quadratic work؛ هو بس يمنع تجميد الرسم. أضف size limits أو progress/cancellation لو UX محتاج، واختبر memory لأن الحل الجديد مساحته <code dir="ltr">O(n)</code>. لو IDs حساسة، telemetry تسجل counts وdurations مش القيم نفسها.</p>

## Verification and rollout

- Unit tests preserve first-repeated semantics, integer boundaries and input order.
- Deterministic probe counts prove linear scan attempts for unique fixtures.
- A release-like device benchmark compares representative sizes and memory pressure.
- Roll out gradually and watch import duration, cancellation, memory and failure categories.

## Senior follow-ups

1. **Would moving the old loop to Dispatchers.Default fix it?** It protects the main thread, but the CPU work still grows quadratically and can waste battery or delay completion.
2. **Why not sort in place?** It changes caller data and can lose “first repeated in original order”; a copy also adds memory and still costs `O(n log n)`.
3. **What evidence can the JVM lab provide?** Functional equivalence and operation-count growth for the model, not Android scheduling, ART optimization, ANR thresholds or device latency.

[LAB-017](../Coding-Challenges/LAB-017-duplicate-scan-complexity.md) contains the executable model.
