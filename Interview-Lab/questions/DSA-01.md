---
id: "DSA-01"
question: "What is time complexity versus space complexity?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "A"
phase: 5
priority: "P2"
order: 440
editorial_status: "reviewed"
---

# DSA-01

## Original interview question

What is time complexity versus space complexity?

## What the interviewer evaluates

- Growth of running work versus extra memory as input grows.
- Distinguishing auxiliary space from input/output storage.

## Explanation in Arabic

Time complexity تقيس نمو عدد العمليات لما input size `n` يكبر، وspace complexity تقيس memory إضافية تستخدمها الخوارزمية. ممكن algorithm أسرع لكن محتاجة `HashSet` بحجم `n`، وممكن أقل memory لكنها تعمل nested scan بوقت `n²`. لازم نحدد هل بنحسب auxiliary space فقط ولا output نفسه، وإيه معنى `n` في المشكلة.

### Practical walkthrough in Egyptian Arabic

لو عندك list فيها آلاف المنتجات، اسأل هل bottleneck حسابي ولا رسم UI. `O(n)` loop ممكن يكون مقبول لو مرة واحدة خارج Main، و`O(n²)` على كل scroll كارثة. Space complexity تحسب الـextra memory، مثل `HashSet` لتجنب scan متكرر. اذكر حجم الإدخال الفعلي، التخصيصات، وتأثير GC؛ Big O يصف النمو لا زمنًا مطلقًا.

## Why it matters and how it works

Asymptotic notation abstracts hardware constants and measures scaling under a defined case. Space includes live allocations, recursion stack and data structures; input and required output may be excluded by convention only if stated. On Android, allocations also create GC pressure and jank.

## Worked example

Finding duplicates in a product list by a HashSet takes expected O(n) time and O(n) additional space; comparing every pair takes O(n²) time and O(1) auxiliary space. For 20 items either is fine; for 100k items the difference matters.

## Trade-offs and decision criteria

Memory is scarce on low-end devices, but CPU on main thread also matters. Streaming or paging can bound memory at the cost of extra I/O. Measure actual performance after asymptotic analysis.

## Failure modes

Claiming O(1) space for a recursive DFS ignores call stack. Claiming O(n) time while repeatedly concatenating immutable strings can hide quadratic copying. Define cost model and profile.

## Production perspective

For a Compose list transformation, estimate CPU and allocations per update, then move heavy work out of composition and benchmark on low-end devices. Avoid optimizing a cold path without evidence.

## Interview answer — short

“Time complexity describes work growth; space complexity describes additional memory growth. I state the input size and whether the bound is worst or average case, then check real device costs.”

## Interview answer — structured

“A HashSet duplicate check trades O(n) extra memory for expected O(n) time, while nested comparison uses constant auxiliary memory but O(n²) time. Big O is a scaling model, not a stopwatch. For Android I also care about allocations and GC on the main thread, so I combine analysis with profiling on representative devices. Measure actual performance after asymptotic analysis.”

## Interview answer — deep senior

“I separate how work grows from how much additional memory it retains. Time complexity counts operations as the input grows; space complexity counts extra storage, excluding or including the input only after stating the convention. For example, scanning product IDs with a nested search can take quadratic comparisons but little extra memory. Building a `HashSet` gives expected linear time with linear extra space. That does not mean the set is always preferable: for twenty items on a rarely used settings screen, allocation and simplicity may dominate. For thousands of rows refreshed on every keystroke, quadratic work on Main can cause dropped frames. I state the input size and frequency, derive the complexity, then measure representative devices and release builds. I also distinguish total work from a single UI frame: an `O(n)` transform done once in a repository can be harmless, while the same transform repeated for every visible item is not. The production decision balances latency, memory pressure, correctness and maintainability.”

## How to answer in the interview

- **Why:** estimate scaling before a large input ships.
- **How:** state input size, operations and extra allocations.
- **Trade-off:** faster lookup versus more memory.
- **Failure case:** small benchmark hides quadratic growth.
- **Production solution:** profile representative device/data.

## Deep-dive talking points

Prompt for input definition, auxiliary versus output space, HashSet trade-off and device measurements.

## Follow-up questions

- [DSA-02](../dsa-02/): What does O(n log n) mean? **Answer:** work grows roughly proportionally to n times log n.
- [DSA-08](../dsa-08/): Why use a set? **Answer:** expected linear duplicate detection with linear memory.

## Self-check rubric

State input size, count time operations and auxiliary memory separately for a concrete list algorithm; explain how an Android allocation or latency limit changes the practical choice.

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection representations.
- [Android performance guidance](https://developer.android.com/topic/performance) — device costs.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
