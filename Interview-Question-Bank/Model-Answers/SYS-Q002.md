---
id: SYS-Q002-ANSWER
question_id: SYS-Q002
status: reviewed
---
# SYS-Q002 — Complete model answer

**Spoken answer:** “Int addition wraps on the JVM, so an impossible mathematical sum can equal an Int target after overflow. I compute both target minus value and candidate sums in Long and range-check a complement before converting back to Int.”

<p dir="rtl" lang="ar">لو MAX_VALUE و1 اتجمعوا في Int، النتيجة تلف إلى MIN_VALUE رغم إن المجموع الرياضي أكبر. Long في حساب complement والمقارنة تمنع pair وهمية.</p>

**Mechanics:** For each Int input, target.toLong() - value.toLong() is safely representable in Long. Only a complement in Int range can match an input element. Two-pointer sums likewise use Long. [Kotlin arrays](https://kotlinlang.org/docs/arrays.html), [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) were checked 2026-10-10.

**Common wrong answer:** “The target is Int, so Int arithmetic must be safe.” Operand addition/subtraction can overflow before comparison.

**Follow-up 1:** Can the Long subtraction overflow for two Int operands? No. The difference range is within about 4.3 billion in magnitude, far below Long limits.

**Follow-up 2:** How would you test it? Use [Int.MAX_VALUE,1] with Int.MIN_VALUE expecting no pair, and MIN_VALUE plus MAX_VALUE targeting -1 expecting a valid pair.

**Rubric for self-review:** State the exact output and input contract, trace a loop invariant, cover duplicates/overflow/no solution, and give complexity with its assumptions. This is visible practice, not a scored assessment.
