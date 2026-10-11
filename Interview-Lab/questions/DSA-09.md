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

“I express the total as a sum and simplify its dominant term. For `sum(i=1..n) i`, the result is n(n+1)/2. For a halving inner process, it is n log n if repeated independently per outer iteration. For a sliding window, I charge each pointer advance to an element; each element is visited a bounded number of times, so O(n). This matters in Compose/RecyclerView transforms, where a hidden linear lookup per row may turn every refresh quadratic. I confirm with scaling measurements before redesign. Inspect total pointer movement.”

## Deep-dive talking points

Prompt for summation, geometric progression, amortized pointer argument and hidden contains.

## Follow-up questions

- [DSA-12](../dsa-12/): What common hidden O(n)? **Answer:** List.find/contains inside per-row mapping.
- [DSA-03](../dsa-03/): Why discard 1/2 coefficient? **Answer:** asymptotic dominant growth.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin collection operations](https://kotlinlang.org/docs/collection-operations.html) — API behavior context.
- [Android performance](https://developer.android.com/topic/performance) — scaling measurements.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
