---
id: SYS-Q003-ANSWER
question_id: SYS-Q003
status: reviewed
---
# SYS-Q003 — Complete model answer

**Spoken answer:** “If the current sum is below target, pairing the current left value with any index no farther right gives a value no larger, so left cannot be in a solution. The symmetric argument removes right when the sum is too large.”

<p dir="rtl" lang="ar">في array مرتبة، لو left+right أصغر من target، كل شريك آخر مع left داخل الحدود أصغر أو يساوي right، فلا حل مع left. ولو المجموع أكبر، كل شريك مع right داخل الحدود أكبر أو يساوي left.</p>

**Mechanics:** The invariant is that any remaining solution lies between left and right. Each move excludes one boundary using monotonic order. The method validates sortedness first and compares Long sums. [Kotlin arrays](https://kotlinlang.org/docs/arrays.html), [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) were checked 2026-10-10.

**Common wrong answer:** “Move either pointer arbitrarily until a match.” That lacks a preservation argument.

**Follow-up 1:** What breaks on unsorted input? The monotonic elimination proof fails; a move can discard a valid pair. Validate or establish sorting first.

**Follow-up 2:** Does sorting preserve original indices? No. Carry original positions with values or use a map if the output contract requires original indices.

**Rubric for self-review:** State the exact output and input contract, trace a loop invariant, cover duplicates/overflow/no solution, and give complexity with its assumptions. This is visible practice, not a scored assessment.
