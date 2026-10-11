---
id: SYS-Q001-ANSWER
question_id: SYS-Q001
status: reviewed
---
# SYS-Q001 — Complete model answer

**Spoken answer:** “Before index i the map contains only earlier elements. Lookup before insertion prevents reusing the current element. A single 3 has no pair; in [3,3], the second 3 finds index zero and returns two distinct indices.”

<p dir="rtl" lang="ar">الـ invariant إن map فيها prefix فقط. لو تدخل الحالية قبل lookup، array فيها 3 واحدة ممكن تطلع pair مع نفسها. عند العنصر الثاني في [3,3] تلاقي index الأولى.</p>

**Mechanics:** The map stores the earliest index for each previous value. Each step tests the complement against that prefix, then records the current value only if absent. The first returned pair is determined by the second index. [Kotlin arrays](https://kotlinlang.org/docs/arrays.html), [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) were checked 2026-10-10.

**Common wrong answer:** “The value exists in the map, so it must be a different item.” That is false if insertion precedes lookup.

**Follow-up 1:** What if a value appears three times? Keeping its earliest index still yields distinct indices and the first pair encountered by the scan’s second index.

**Follow-up 2:** What if the product wants the lexicographically smallest pair? This first-encountered contract may differ; specify and test the required tie-breaking rule.

**Rubric for self-review:** State the exact output and input contract, trace a loop invariant, cover duplicates/overflow/no solution, and give complexity with its assumptions. This is visible practice, not a scored assessment.
