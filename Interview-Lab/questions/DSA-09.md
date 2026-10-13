---
id: "DSA-09"
question: "How do you calculate complexity for nested loops with dependent bounds?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 448
editorial_status: "reviewed"
---

# DSA-09

## Original interview question

How do you calculate complexity for nested loops with dependent bounds?

## What the interviewer evaluates

- Summation of dependent loop bounds, not automatic multiplication.
- Triangular, halving and geometric examples.

## Explanation in Arabic

Nested loops مش دائمًا O(n²): لو الداخلي من 0 لحد i، عدد التكرارات `1+2+…+n = n(n+1)/2` وبالتالي O(n²). لو j بيتضاعف كل مرة داخل outer n، الداخلي O(log n) فالمجموع O(n log n). ولو outer والداخل بيمشوا pointer واحد للأمام، ممكن O(n) إجمالي. نعد العمليات الفعلية أو نكتب summation.

### Practical walkthrough in Egyptian Arabic

Nested loops مش دائمًا `O(n²)`: لو inner يبدأ من i، مجموع 1+2+...+n ما زال quadratic؛ لو pointer يتحرك للأمام مرة واحدة عبر كل outer iterations قد يكون linear. اكتب عدد تكرارات inner كـsum بدل ضرب آلي. مثال `for each row { items.find(...) }` في Compose list يصنع scan لكل row؛ اعمل index مرة خارج render.

## Why it matters and how it works

Dependent bounds make simple “multiply loop lengths” insufficient. Sum inner work over outer iterations. A geometric progression can be O(n) even with syntactically nested loops; amortized analysis may be needed when a pointer never retreats.

## Worked example

For each `i` from 0 to n-1, scanning prior entries costs i, so total n(n−1)/2. In a paged Android list, repeatedly checking all earlier items per row can cause jank as the list grows. Build a set/index if repeated lookup is the intent.

## Trade-offs and decision criteria

Summation gives a correct upper bound but may be more detail than a tiny bounded input needs. An index improves scaling at memory cost. Verify hidden collection calls as well as loop syntax.

## Failure modes

Calling `contains` on a List inside one loop looks like one loop but costs O(n²). Conversely, two pointers advancing monotonically can be O(n) despite nested `while` blocks. Inspect total pointer movement.

## Production perspective

Use realistic n in benchmarks and move heavy list transforms off the main thread. Add a scaling benchmark to catch accidental quadratic regressions.

## Interview answer — short

“For dependent loops I sum inner work across outer iterations. A triangular loop is O(n²), doubling inner index gives O(n log n), and monotonic two-pointer work can be O(n).”

## Interview answer — structured

“I do not multiply loop counts blindly. If the inner loop runs i times for outer i, the total is a triangular sum, O(n²). If it halves or doubles a range each time, I get a logarithmic factor. If two pointers only advance through the input once overall, the total can be linear. I also inspect library calls hidden in a loop, such as List.contains. Sum inner work over outer iterations.”

## Interview answer — deep senior

“I count iterations, not just loop keywords. If the outer index goes from zero to n and the inner loop runs from that index to n, the total is a triangular sum, roughly n²/2, so it is still quadratic. If the inner pointer only advances forward across the whole algorithm and never resets, the combined work may be linear by amortized analysis. I write the sum or an invariant for each pointer and include the cost of work inside the body; a map lookup or sort there changes the result. This matters in Android list binding: `items.forEach { product -> allPrices.find { it.id == product.id } }` can scan n prices for each of n products, producing quadratic work during rendering. I would build a price-by-ID map once, accepting O(n) memory for expected O(n) total transformation. Then I measure frame time, because a theoretically linear replacement could still allocate too much. The interviewer should hear the derivation and the practical decision.”

## How to answer in the interview

- **Why:** dependent bounds need a counted sum.
- **How:** derive total iterations or amortized pointer moves.
- **Trade-off:** precomputed index costs memory.
- **Failure case:** multiplying loops without checking shared progress.
- **Production solution:** measure repeated work in UI paths.

## Deep-dive talking points

Prompt for summation, geometric progression, amortized pointer argument and hidden contains.

## Follow-up questions

- [DSA-12](../dsa-12/): What common hidden O(n)? **Answer:** List.find/contains inside per-row mapping.
- [DSA-03](../dsa-03/): Why discard 1/2 coefficient? **Answer:** asymptotic dominant growth.

## Self-check rubric

Derive the sum for a dependent inner loop rather than multiplying loop bounds blindly; give a linear triangular or logarithmic example and state its memory complexity.

## References and reviewed-on date

- [Kotlin collection operations](https://kotlinlang.org/docs/collection-operations.html) — API behavior context.
- [Android performance](https://developer.android.com/topic/performance) — scaling measurements.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
