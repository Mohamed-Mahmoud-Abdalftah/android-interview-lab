---
id: SYS-Q004-ANSWER
question_id: SYS-Q004
status: reviewed
---
# SYS-Q004 — Complete model answer

**Spoken answer:** “The map scan performs O(n) lookups/inserts and uses O(n) space, with expected linear time under suitable hash distribution. On already sorted input, validation and two pointers take O(n) time and O(1) extra space. Sorting first adds O(n log n) time and may change original positions.”

<p dir="rtl" lang="ar">ما تقولش HashMap O(1) دائمًا؛ Java docs تربطها بتوزيع hash مناسب. sorted two-pointer خطية ومساحتها ثابتة بعد فحص الترتيب. لو لازم تفرز أولًا، احسب تكلفة الفرز والـ indices.</p>

**Mechanics:** Java HashMap documents constant-time basic operations conditional on dispersion. The two-pointer loop moves a boundary each iteration, at most n-1 moves after one linear sortedness check. [Kotlin arrays](https://kotlinlang.org/docs/arrays.html), [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) were checked 2026-10-10.

**Common wrong answer:** “Map is always O(n) worst-case and two pointers always wins.” Both claims ignore hash conditions, sorting cost and output semantics.

**Follow-up 1:** What if the values are already sorted but original indices still matter? A map preserves the original positions directly; an indexed sorted representation is another option with sorting/space costs.

**Follow-up 2:** Would a benchmark replace the proof? No. The proof describes growth and contract, while a benchmark can measure real constants and allocation behavior for a workload.

**Rubric for self-review:** State the exact output and input contract, trace a loop invariant, cover duplicates/overflow/no solution, and give complexity with its assumptions. This is visible practice, not a scored assessment.
