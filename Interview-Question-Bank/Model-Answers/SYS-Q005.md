---
id: SYS-Q005-ANSWER
question_id: SYS-Q005
status: reviewed
---
# SYS-Q005 — Complete model answer

**Spoken answer:** “Stable keys preserve lookup semantics, and leaving the input unchanged avoids surprising a caller that reuses it. Mutable map keys can violate the map contract when equality changes. An in-place sort also destroys original index meaning unless positions are carried separately.”

<p dir="rtl" lang="ar">الـ Int key ثابتة، فـ hash/equality لا تتغير أثناء وجودها في map. ترتيب array الأصلية in-place يغير بيانات caller ومعنى indices. دي side effects لازم تكون مكتوبة في contract.</p>

**Mechanics:** The Java Map contract leaves behavior unspecified if a key changes in a way that affects equality. The tested implementation reads IntArray and returns indices without mutating it. [Kotlin arrays](https://kotlinlang.org/docs/arrays.html), [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) and [Java Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html) were checked 2026-10-10.

**Common wrong answer:** “The helper is internal, so mutation does not matter.” Callers can still reuse or share the input and rely on its order.

**Follow-up 1:** Could a mutable object be used as a key safely? Only if the equality-relevant state remains stable while it is in the map; an immutable key type is safer.

**Follow-up 2:** What would you test for the input contract? Copy the original array before invocation and assert the values and order are unchanged afterward.

**Rubric for self-review:** State the exact output and input contract, trace a loop invariant, cover duplicates/overflow/no solution, and give complexity with its assumptions. This is visible practice, not a scored assessment.
