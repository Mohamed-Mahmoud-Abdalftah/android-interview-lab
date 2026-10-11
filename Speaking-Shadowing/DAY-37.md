# Day 37 optional speaking — pair-search invariants

Read [SYS-001](../08-Mobile-System-Design/sys-001-arrays-maps-two-pointers-and-invariants.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “I clarify the output contract / state a loop invariant / and test duplicates, overflow and no solution.” Stress **contract** and **invariant**.

**About 20 seconds:** “For original indices in unsorted input, I scan with a map of earlier values and check the complement before insertion. For sorted values, I move two pointers based on the sum.”

**About 90 seconds:** “First I clarify whether the output needs original indices or values and whether sorting is allowed. In the map solution, before index i the map holds the earliest index of each value in the prefix. I compute the complement in Long to avoid overflow, look it up before insertion so I never reuse the current element, and return the first pair by second index. Expected time is linear with linear extra space under suitable hashing. On already sorted input, two pointers use monotonic order to exclude a boundary each step, giving linear time and constant extra space after validation. I test duplicates, no pair, extreme values and nonmutation.”

**Useful phrases:** “original index”, “prefix invariant”, “conditional expected complexity”, “overflow-safe intermediate”. Avoid “HashMap is constant time in every case”.

**Self-check:** Trace one duplicate and one overflow case without notes. Retry with [revision cards](../Flashcards-Revision/SYS-001.md). Free written references: [Kotlin arrays](https://kotlinlang.org/docs/arrays.html) and [Java HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html), checked 2026-10-10.
