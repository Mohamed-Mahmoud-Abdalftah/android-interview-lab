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

## Why it matters and how it works

HashSet uses hash/equality; equality semantics determine duplicates. For a stream larger than memory, use bounded external sort or database uniqueness/index and pagination. Approximate filters can reduce I/O but cannot prove absence without confirmation.

## Worked example

Illustrative Kotlin: `val seen = HashSet<String>(); val firstDuplicate = ids.firstOrNull { !seen.add(it) }`. Assumes IDs are normalized and memory fits. In Room, a unique index can enforce no duplicate persisted IDs across concurrent writers.

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

“For a large list I estimate cardinality and key size before allocating a set. If it fits, a one-pass HashSet is simple; if it does not, I consider streaming chunks with external sort or delegate uniqueness to indexed storage. Approximate membership structures can filter candidates but need exact confirmation to avoid false positives. In a payment import, the client-side set is just a precheck: the backend/database enforces unique operation IDs atomically. I test case/Unicode normalization and duplicate values crossing batch boundaries.”

## Deep-dive talking points

Prompt for equality definition, HashSet memory, sort trade-off, streaming and durable constraint.

## Follow-up questions

- [DSA-06](../dsa-06/): Is set lookup guaranteed constant? **Answer:** expected under hashing assumptions.
- [DSA-15](../dsa-15/): What prevents concurrent duplicate requests? **Answer:** atomic server-side key state, not only a local set.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a data or memory trade-off, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin set operations](https://kotlinlang.org/docs/set-operations.html) — set semantics.
- [Room indices](https://developer.android.com/training/data-storage/room/defining-data) — unique indexed storage.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
