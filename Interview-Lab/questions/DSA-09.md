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

## Concept and technical explanation

Calculating time complexity when loop iterations depend dynamically on an outer index requires evaluating arithmetic summations rather than multiplying upper bounds:
- Independent vs Dependent Loops:
  - Independent Loops: `for (i in 0 until n) for (j in 0 until m)` executes strictly $n 	imes m$ times, yielding $O(n 	imes m)$ or $O(n^2)$ when $m = n$.
  - Dependent Loops: `for (i in 0 until n) for (j in i + 1 until n)` executes a varying number of steps: when $i = 0$, inner runs $n - 1$ times; when $i = 1$, $n - 2$ times; down to $0$ when $i = n - 1$.
- Arithmetic Series Derivation:
  - Total operations $S = (n - 1) + (n - 2) + \dots + 2 + 1 + 0$.
  - Using Gauss's summation formula: $S = rac{n(n - 1)}{2} = rac{n^2 - n}{2} = rac{1}{2}n^2 - rac{1}{2}n$.
  - In asymptotic Big O notation, constants like $rac{1}{2}$ and lower-order terms like $-rac{1}{2}n$ are dropped.
  - Final Complexity: $O(n^2)$ Quadratic Time.
  - Mathematical Invariant: Even though the loop executes half the iterations of a full $n 	imes n$ matrix, its growth rate remains strictly quadratic.
- Geometric and Doubling Loops:
  - If the inner loop doubles (`var j = 1; while (j < i) j *= 2`), inner executes $\log_2 i$ times: $\sum_{i=1}^n \log i = \log(n!) = O(n \log n)$ via Stirling's approximation.
  - If the outer loop doubles (`var i = 1; while (i <= n) i *= 2`) and inner runs $i$ times: $\sum_{k=0}^{\log n} 2^k = 2^{\log_2 n + 1} - 1 = 2n - 1 = O(n)$ Linear Time!

## Practical walkthrough (English)

Kotlin examples analyzing nested loops with dependent arithmetic and doubling bounds:
```kotlin
// Example 1: Triangular Dependent Loop -> O(n^2)
// Total iterations: (n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2 -> O(n^2)
fun compareAllPairs(items: List<String>) {
    val n = items.size
    for (i in 0 until n) {
        for (j in i + 1 until n) {
            // Evaluates every unique pair exactly once
            val pairComparison = items[i] == items[j]
        }
    }
}

// Example 2: Outer loop doubles, inner loop runs up to i -> O(n) Linear Time!
// Iterations: 1 + 2 + 4 + 8 + ... + n = 2n - 1 -> O(n)
fun doublingOuterLoop(n: Int) {
    var count = 0
    var i = 1
    while (i <= n) {
        for (j in 0 until i) {
            count++
        }
        i *= 2 // Geometric expansion
    }
}
```

## Explanation in Arabic

كيف تحسب التعقيد الزمني بدقة للحلقات التكرارية المتداخلة ذات الحدود المعتمدة على بعضها (Dependent Bounds)؟

1. خطأ الضرب السطحي الشائع (The Naive Multiplication Error):
   - كثير من المطورين ينظرون لحلقتين متداخلتين ويفترضون تلقائياً أن التعقيد هو $O(n \times m)$ دائماً بمجرد ضرب الحدود!
   - إذا كانت الحلقة الداخلية تعتمد على متغير الحلقة الخارجية ($j$ يعتمد على $i$)، يجب **حساب مجموع المتسلسلة الرياضية (Summation)** بدقة بدلاً من الضرب السطحي.

2. الحالة الكلاسيكية: المتسلسلة الحسابية (Arithmetic Series):
   - حلقة خارجية `for (i in 0 until n)`، وحلقة داخلية `for (j in i until n)`:
     * عندما $i = 0$: تنفذ الحلقة الداخلية $n$ مرة.
     * عندما $i = 1$: تنفذ الحلقة الداخلية $n - 1$ مرة.
     * عندما $i = n - 1$: تنفذ الحلقة الداخلية $1$ مرة.
   - إجمالي الخطوات:
     $$S = n + (n - 1) + (n - 2) + \dots + 1 = \sum_{k=1}^n k = \frac{n(n + 1)}{2} = \frac{n^2}{2} + \frac{n}{2}$$
   - بإهمال الثوابت والحدود الدنيا، يصبح التعقيد **$O(n^2)$**.

3. المفاجأة الرياضية: المتسلسلة الهندسية (Geometric Series):
   - تخيل حلقة يتضاعف فيها $i$ (`i *= 2`) بينما تنفذ الحلقة الداخلية $i$ مرة:
     * إجمالي الخطوات: $1 + 2 + 4 + 8 + \dots + n = 2n - 1$.
   - التعقيد هنا هو **$O(n)$ خطي وليس $O(n^2)$ ولا $O(n \log n)$** على الإطلاق! لذلك الحساب الرياضي الدقيق إلزامي.

## Practical walkthrough

تحليل عملي للفرق بين المتسلسلة الحسابية والمتسلسلة الهندسية في كود كوتلن:
```kotlin
// 1. المتسلسلة الحسابية O(n^2):
fun printPairs(n: Int) {
    var totalSteps = 0
    for (i in 0 until n) {
        for (j in i until n) { // j يعتمد على i
            totalSteps++
        }
    }
    // totalSteps = n * (n + 1) / 2 -> O(n^2)
}

// 2. المتسلسلة الهندسية O(n) (حلقة متداخلة تبدو مخادعة ولكنها خطية!):
fun geometricDependentLoop(n: Int) {
    var totalSteps = 0
    var i = 1
    while (i <= n) {
        for (j in 0 until i) { // j يعتمد على i المتضاعف
            totalSteps++
        }
        i *= 2 // تضاعف أسي
    }
    // الخطوات: 1 + 2 + 4 + 8 + ... + 2^k = 2 * n - 1 -> O(n)!
}
```

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

Calculate complexity for nested loops with dependent bounds by expressing the total steps as a mathematical summation rather than naively multiplying loop limits. For triangular loops where inner runs n minus i times, the sum equals n multiplied by n minus one over two, which simplifies asymptotically to O(n^2). Geometric doubling patterns require summing powers of two or logarithms.

## Interview answer — structured

Calculating time complexity for nested loops with dependent bounds requires setting up and evaluating mathematical summations rather than multiplying bounds.
When the inner loop bound depends on the outer loop variable, such as iterating from i plus one to n, the inner loop executes a decreasing number of operations on each pass. For a list of size n, the inner loop runs n minus one times, then n minus two times, continuing down to one operation.
This forms an arithmetic series known as Gauss's summation. The sum equals n multiplied by n minus one divided by two. Multiplying this out yields one-half n squared minus one-half n. Because asymptotic analysis omits multiplicative constants and lower-order terms, the complexity simplifies directly to O(n^2).
Even though the loop processes only half of an n by n grid, its fundamental growth rate remains strictly quadratic. For non-linear bounds where variables double geometrically, engineers sum powers of two or logarithms, which can yield surprising linear O(n) or linearithmic O(n log n) results.

## Interview answer — deep senior

From an algorithmic proof and performance modeling perspective, analyzing dependent loops exposes the danger of mechanical Big O heuristics. Many engineers glance at nested loops and assume quadratic time, or mistakenly conclude that running half an iteration makes an algorithm sub-quadratic.
The rigorous methodology constructs a formal summation. In a triangular nested loop comparing all unique pairs, the outer index i increments from zero to n minus one, while the inner index j runs from i plus one to n. The total operation count is represented by the summation of n minus one minus i for i equals zero to n minus one. Expanding this series produces Gauss's formula: n times n minus one divided by two. In asymptotic notation, the coefficient of one-half is dropped, leaving O of n squared. The practical mobile takeaway is that cutting operations in half does not change algorithmic scalability; as catalog sizes scale by a factor of ten, execution time still increases hundredfold.
Furthermore, analyzing non-standard dependent boundaries reveals counter-intuitive complexities. Consider a loop where the outer index doubles on each iteration while the inner loop runs linearly up to i. A naive analysis might predict O of n log n. However, expressing the iterations as the summation of two to the power of k for k equals zero to log n forms a geometric series. The sum evaluates to two n minus one, proving that the algorithm actually runs in strictly linear O of n time.
In Android development, mastering these summation patterns is essential when profiling layout measurement passes, custom Canvas drawing routines, or DiffUtil list comparisons to identify whether nested logic will scale smoothly across growing datasets.

## How to answer in the interview

- **Why:** dependent bounds need a counted sum.
- **How:** derive total iterations or amortized pointer moves.
- **Trade-off:** precomputed index costs memory.
- **Failure case:** multiplying loops without checking shared progress.
- **Production solution:** measure repeated work in UI paths.

## Deep-dive talking points

Prompt for summation, geometric progression, amortized pointer argument and hidden contains.

## Follow-up questions

- **Interviewer:** "Why does a sliding window algorithm with nested while loops have $O(n)$ complexity rather than $O(n^2)$?"
  **Answer:** "Because the inner window pointer advances monotonically forward at most $n$ times across the entire execution, resulting in an amortized $O(n)$ runtime."

- **Interviewer:** "What is the closed form sum of $1 + 2 + 3 + \dots + n$?"
  **Answer:** "$\frac{n(n + 1)}{2}$, which asymptotically scales to $O(n^2)$."

## Self-check rubric

Derive the sum for a dependent inner loop rather than multiplying loop bounds blindly; give a linear triangular or logarithmic example and state its memory complexity.

## References and reviewed-on date

- [Kotlin collection operations](https://kotlinlang.org/docs/collection-operations.html) — API behavior context.
- [Android performance](https://developer.android.com/topic/performance) — scaling measurements.

Technically reviewed against primary documentation on 2026-10-13.
