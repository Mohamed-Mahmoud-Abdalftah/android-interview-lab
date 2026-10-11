---
id: KOT-Q030-ANSWER
question_id: KOT-Q030
status: reviewed
---
# KOT-Q030 — Complete model answer

<p dir="rtl" lang="ar">الـgeneric set قد تحتاج boxed Integer objects أو references وتعمل allocations وhash-table overhead. كمان initial capacity، resizing، cache locality وGC ممكن يأثروا. لكن ده مش تصريح نستبدلها بهيكل معقد فورًا. أجمع allocation profile، CPU samples، GC pauses، input sizes وend-to-end latency من relevant devices وrelease-like variant. لو الـset هي hotspot مؤثرة، أقارن primitive collection أو domain-specific bitmap لما range تسمح، مع correctness وmemory benchmarks.</p>

**Spoken answer:** “The algorithm scales better, but a generic `HashSet<Int>` can still add boxing, allocation, table capacity and locality costs. I would profile allocations, GC and CPU in the real path on representative devices. I only introduce a primitive collection or bitmap when the measurements show this set is material and the value range and dependency cost support the alternative.”

**Common wrong answer:** Big-O is linear, so allocations and runtime behavior no longer matter.

**Follow-up 1:** When can a bitmap work? When values map to a known, acceptably small range and the memory calculation is explicit; sparse or unbounded IDs can make it wasteful or unsafe.

**Follow-up 2:** What must remain in the benchmark? The same input distribution, duplicate position, build type, warmup policy and observable result so the optimizer cannot remove the work.

**Rubric:** Mention boxing/table costs, representative profiling, a justified primitive alternative and preservation of semantics.
