---
id: "DSA-08"
question: "How would you detect duplicates efficiently in a large list?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 447
editorial_status: "reviewed"
---

# DSA-08

## Original interview question

How would you detect duplicates efficiently in a large list?

## What the interviewer evaluates

- Expected-linear set scan versus sorting or brute force.
- Large-input memory, streaming and key-equivalence decisions.

## Explanation in Arabic

للكشف عن duplicate في list كبيرة، نمشي مرة ونحط كل key في `HashSet`؛ لو `add` رجعت false لقينا تكرار. الوقت expected O(n)، والذاكرة O(n). لو memory ضيقة ومسموح نغير الترتيب، sort O(n log n) وبعدها مقارنة المتجاورين. لازم نحدد معنى “نفس العنصر”: ID ثابت ولا object equality؟

### Practical walkthrough in Egyptian Arabic

لإيجاد أول duplicate في ترتيب الإدخال، `HashSet.add` يرجع false عند التكرار؛ المتوقع `O(n)` وقت و`O(n)` ذاكرة. sorting يستهلك وقت أكثر وقد يغير order، وnested loops `O(n²)`. مع stream لا نهائي، set تكبر بلا حد؛ عرّف window أو durable index. لو IDs مالية، local set لا تمنع duplicate business effect على server.

## Why it matters and how it works

HashSet uses hash/equality; equality semantics determine duplicates. For a stream larger than memory, use bounded external sort or database uniqueness/index and pagination. Approximate filters can reduce I/O but cannot prove absence without confirmation.

## Worked example

Illustrative Kotlin: `val seen = HashSet<String>(); val firstDuplicate = ids.firstOrNull { !seen.add(it) }`. Assumes IDs are normalized and memory fits. In Room, a unique index can enforce no duplicate persisted IDs across concurrent writers.

For an unsorted stream, keep only seen values and stop at the first repeated value in input order. The map/set memory cost is the trade-off; for unbounded data use a bounded window or a durable external index with an explicit definition of “duplicate.”

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private fun firstRepeated(ids: Iterable<String>): String? {
    val seen = HashSet<String>()
    for (id in ids) if (!seen.add(id)) return id
    return null
}

class DuplicateDetectionExampleTest {
    @Test fun inputOrderAndNoDuplicate() {
        assertEquals("a", firstRepeated(listOf("a", "b", "a", "b")))
        assertEquals(null, firstRepeated(listOf("a", "b")))
    }
}
```

## Trade-offs and decision criteria

Set gives fast expected detection but retains keys. Sorting can use less extra memory if in-place sorting is allowed, but changes order and costs more CPU. DB uniqueness moves enforcement to durable boundary.

## Failure modes

Using mutable data class as set key then mutating it breaks hash lookup. Normalization mismatch (`abc` versus `ABC`) may hide logical duplicates. In concurrent updates, a client-side set is not an atomic uniqueness guarantee.

## Production perspective

For an Android import, normalize IDs, check memory budget, use a DB unique constraint for durable writes and report duplicate count safely without logging personal data.

## Interview answer — short

“A HashSet scan detects duplicates in expected O(n) time and O(n) space; sorting then scanning costs O(n log n) but can use less extra memory. I define equality and durable uniqueness separately.”

## Interview answer — structured

“I choose a key and equality rule, then insert keys into a HashSet until an insert fails. This is expected linear time but may hold all keys. If memory is limited and I may reorder, I sort and compare neighbors; for persisted concurrent data, a Room/SQLite unique index is the real enforcement boundary. I avoid mutable keys and test normalization edge cases.”

## Interview answer — deep senior

“I first clarify what ‘duplicate’ means: any repeated value, the first value repeated in input order, or all duplicates. For the first repeated ID in an unsorted list, I scan once and insert each ID into a `HashSet`; the first failed `add` is the answer. That is expected O(n) time and O(n) extra space, with stable input order and no mutation of the caller’s list. A nested scan uses O(1) extra space but O(n²) comparisons, which can freeze a large list. Sorting costs O(n log n) and may change the original ordering unless I copy or retain indices. For an unbounded stream, the set itself becomes a memory problem, so I define a bounded time window, eviction policy or durable external index. A local set can suppress accidental duplicate UI events, but it cannot guarantee one payment effect across devices or process death; that requires a server-enforced identity. I test no duplicates, repeated first/last values and memory limits.”

## How to answer in the interview

- **Why:** duplicate scans can become quadratic.
- **How:** use seen set and define first repeated semantics.
- **Trade-off:** linear memory versus sorting or nested scans.
- **Failure case:** unbounded set leaks memory.
- **Production solution:** bounded window or server uniqueness contract.

## Deep-dive talking points

Prompt for equality definition, HashSet memory, sort trade-off, streaming and durable constraint.

## Follow-up questions

- [DSA-06](../dsa-06/): Is set lookup guaranteed constant? **Answer:** expected under hashing assumptions.
- [DSA-15](../dsa-15/): What prevents concurrent duplicate requests? **Answer:** atomic server-side key state, not only a local set.

## Self-check rubric

Compare a hash-set scan with sorting for duplicate detection; state expected time and extra memory, preserve first-duplicate semantics if required, and test empty and large inputs.

## References and reviewed-on date

- [Kotlin set operations](https://kotlinlang.org/docs/set-operations.html) — set semantics.
- [Room indices](https://developer.android.com/training/data-storage/room/defining-data) — unique indexed storage.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
