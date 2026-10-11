---
id: MOCK-006
status: reviewed
---
# MOCK-006 — DSA live coding

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **SYS-Q001:** In a one-pass two-sum search, why should the map lookup happen before inserting the current value? Trace [3] and [3,3] with target 6.
2. **SYS-Q002:** Why can Int.MAX_VALUE plus 1 create a false two-sum match with target Int.MIN_VALUE? Show the arithmetic boundary in the algorithm.
3. **SYS-Q003:** For a nondecreasing array and target T, explain why moving left when sum<T, or right when sum>T, cannot discard a valid pair.
4. **SYS-Q004:** Compare expected map-search time/space with a sorted two-pointer search. State the hash assumption and the cost if you must sort first.
5. **SYS-Q005:** Why use stable Int keys in the pair-search map and avoid sorting the caller’s array in place? Relate this to mobile feature boundaries.
6. **DSA-Q001:** State the core invariant of Dijkstra's algorithm and the input condition that makes it valid.
7. **DSA-Q002:** When should you choose BFS instead of Dijkstra for shortest path?
8. **DSA-Q003:** Why can a node appear multiple times in the priority queue, and how do you handle that correctly?
9. **DSA-Q004:** How can integer overflow corrupt shortest-path results, and how would you prevent it?
10. **DSA-Q005:** How would you structure a senior-level live-coding answer for weighted shortest path?
11. **SYS-Q006:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain BFS and DFS choice, choose a correction, and name evidence that would prove or falsify it.
12. **SYS-Q007:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain Heap invariant, choose a correction, and name evidence that would prove or falsify it.

## Answer key

1. **SYS-Q001:** Before index i the map contains only earlier elements. Lookup before insertion prevents reusing the current element. A single 3 has no pair; in [3,3], the second 3 finds index zero and returns two distinct indices. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q001.md)
2. **SYS-Q002:** Int addition wraps on the JVM, so an impossible mathematical sum can equal an Int target after overflow. I compute both target minus value and candidate sums in Long and range-check a complement before converting back to Int. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q002.md)
3. **SYS-Q003:** If the current sum is below target, pairing the current left value with any index no farther right gives a value no larger, so left cannot be in a solution. The symmetric argument removes right when the sum is too large. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q003.md)
4. **SYS-Q004:** The map scan performs O(n) lookups/inserts and uses O(n) space, with expected linear time under suitable hash distribution. On already sorted input, validation and two pointers take O(n) time and O(1) extra space. Sorting first adds O(n log n) time and may change original positions. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q004.md)
5. **SYS-Q005:** Stable keys preserve lookup semantics, and leaving the input unchanged avoids surprising a caller that reuses it. Mutable map keys can violate the map contract when equality changes. An in-place sort also destroys original index meaning unless positions are carried separately. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q005.md)
6. **DSA-Q001:** The map stores the best discovered distance and the heap yields the smallest current candidate. Non-negative edges ensure a settled minimum cannot later be improved through a more expensive prefix. [Complete answer](../Interview-Question-Bank/Model-Answers/DSA-Q001.md)
7. **DSA-Q002:** BFS is the simpler linear-time choice when every edge has equal cost. Dijkstra is needed when non-negative edge costs differ and the objective is minimum total cost. [Complete answer](../Interview-Question-Bank/Model-Answers/DSA-Q002.md)
8. **DSA-Q003:** Each improvement inserts a new candidate because the queue has no convenient decrease-key. On poll, I skip an entry whose distance no longer equals the current distance map. [Complete answer](../Interview-Question-Bank/Model-Answers/DSA-Q003.md)
9. **DSA-Q004:** A wrapped sum can become negative and incorrectly win relaxation. I guard addition and enforce meaningful domain bounds and units before the algorithm runs. [Complete answer](../Interview-Question-Bank/Model-Answers/DSA-Q004.md)
10. **DSA-Q005:** I clarify the graph contract, state the invariant, trace a counterexample to BFS, implement relaxation and parent reconstruction, then test edge cases and give complexity with lazy heap entries. [Complete answer](../Interview-Question-Bank/Model-Answers/DSA-Q005.md)
11. **SYS-Q006:** BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q006.md)
12. **SYS-Q007:** The root is the priority optimum; arbitrary iteration is not globally sorted. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q007.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
