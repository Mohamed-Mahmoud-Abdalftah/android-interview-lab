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

- Define the input size and compare growth in work and extra memory.
- State whether space means auxiliary storage or includes input and output.
- Explain an Android decision without converting Big O into a timing, frame, GC, or OOM guarantee.

## Concept and technical explanation

Time complexity describes how the number of operations grows with input size under a stated case and cost model. Space complexity describes how memory use grows. If an interview asks for auxiliary space, exclude the given input and required output but include temporary structures and recursion stack. Big O is an upper-bound style description often used for worst-case growth; a hash-based example should say when its stated time is expected rather than guaranteed.

On Android, an algorithm's measured latency also depends on constants, data shape, runtime, and device. Work on the main thread can delay rendering or responsiveness, but one O(n) label cannot prove it fits a frame. Extra collections can raise memory footprint and allocation work; they do not guarantee a GC pause or OOM. Estimate growth first, then profile the actual path on representative devices.

## Practical walkthrough (English)

For a list of prices, a nested comparison checks every distinct pair in O(n²) time and O(1) auxiliary space. A hash set remembers earlier prices and can find a complement in expected O(n) time with O(n) auxiliary space, assuming ordinary hash behavior. If the input is already sorted, two pointers can use O(n) time and O(1) auxiliary space; sorting an unsorted input adds its own time, memory, and mutation contract. Each version must handle arithmetic overflow and avoid using the same element twice.

## Explanation in Arabic

`Time Complexity` بتوصف عدد الخطوات بيكبر إزاي لما حجم الـ Input يكبر؛ و`Space Complexity` بتوصف الذاكرة بتكبر إزاي. لازم أحدد يعني إيه `n` وبحسب Worst Case ولا Expected Case. ولو قلت `Auxiliary Space` فأنا غالبًا باستثني الـ Input والـ Output المطلوب، لكن أحسب الـ HashSet أو Recursion Stack اللي أضفتهم.

في Android، `O(n)` مش وعد إن الشغل هيخلص في Frame واحدة؛ الـ Constants والجهاز وشكل البيانات مهمين. و`O(n)` Space ما تعنيش تلقائيًا GC Pause أو OOM. لو حساب ثقيل شغال على Main Thread ممكن يؤخر الرسم، ولو بعمل Collections كبيرة ممكن أضغط على الذاكرة. أقدّر الـ Growth الأول، وبعدها أقيس الـ Path الحقيقي على جهاز يمثل المستخدمين.

## Practical walkthrough

لو بدور على سعرين مجموعهم Target، مقارنة كل زوج وقتها `O(n²)` وAuxiliary Space `O(1)`. `HashSet` تحفظ الأسعار اللي شوفتها وتخلي البحث Expected `O(n)` وقت و`O(n)` Space. لو القائمة Sorted أصلًا، Two Pointers تمشي `O(n)` وقت و`O(1)` Extra Space؛ لكن فرز قائمة غير مرتبة له تكلفة إضافية وقد يغير البيانات. في المثال أحوّل الجمع لـ `Long` عشان `Int` ما تعملش Overflow، وما أستخدمش نفس العنصر مرتين.

## Why it matters and how it works

Asymptotic analysis helps choose a strategy as data grows, not forecast exact milliseconds. The hash set trades extra live memory for fewer expected comparisons. Worst-case hashing, boxing, cache locality, input ordering, and allocation costs still matter on a device. Main-thread latency and total memory must be measured separately.

## Worked example

The snippet is a self-contained Kotlin/JVM comparison. It bounds the target to the sum of two `Int` values before subtraction, performs arithmetic in `Long`, and tests a duplicate-value pair as two separate positions.

```kotlin
fun pairQuadratic(values: IntArray, target: Long): Boolean {
    for (i in values.indices) {
        for (j in i + 1 until values.size) {
            if (values[i].toLong() + values[j].toLong() == target) return true
        }
    }
    return false
}

fun pairWithSet(values: IntArray, target: Long): Boolean {
    if (target !in 2L * Int.MIN_VALUE..2L * Int.MAX_VALUE) return false
    val seen = HashSet<Int>()
    for (value in values) {
        val complement = target - value.toLong()
        if (complement in Int.MIN_VALUE.toLong()..Int.MAX_VALUE.toLong() &&
            complement.toInt() in seen
        ) return true
        seen.add(value)
    }
    return false
}

fun main() {
    val values = intArrayOf(Int.MAX_VALUE, 1, 7, 7)
    check(pairQuadratic(values, Int.MAX_VALUE.toLong() + 1))
    check(pairWithSet(values, Int.MAX_VALUE.toLong() + 1))
    check(pairWithSet(values, 14))
    check(!pairWithSet(intArrayOf(7), 14))
    check(!pairWithSet(values, Long.MAX_VALUE))
}
```

## Trade-offs and decision criteria

For a small bounded list, the simpler quadratic scan may be adequate. A hash set is useful for larger unsorted input if its extra memory is acceptable. A sorted input supports two pointers with constant auxiliary space; sorting first is a separate operation. Paging or streaming can bound resident data when the entire collection need not be loaded, but may add I/O and change the algorithm.

## Failure modes

Calling hash lookup a guaranteed O(1) operation or asserting a fixed execution time. Forgetting recursion stack in auxiliary space. Saying the sorted two-pointer method is O(1) space after silently sorting or copying an unsorted list. Summing two `Int` values before widening, which can overflow. Moving a CPU-heavy algorithm off the main thread may protect UI responsiveness but does not reduce its total work.

## Production perspective

Define expected and worst input sizes, calculate both resource-growth dimensions, and profile on representative devices with realistic data. For a Compose or RecyclerView list, avoid heavy recomputation on the main thread and measure frames and allocations after changing the algorithm. Set memory budgets for low-memory devices. Do not claim a universal frame threshold or zero OOM risk from Big O alone.

## Interview answer — short

Time complexity is how work grows with input size; space complexity is how memory grows. I state the case and whether space means only extra storage. For two-sum, comparing every pair is O(n²) time and O(1) extra space; a hash set gives expected O(n) time with O(n) extra space. On Android that helps choose an approach, but I still measure real latency and memory on target devices.

## Interview answer — structured

I start by defining `n` and the cost I count. Time complexity tracks growth in operations; space complexity tracks memory growth. If the question says auxiliary space, I count my temporary structures and call stack but usually leave out the supplied input and required output, stating that convention.

For two prices adding to a target, nested loops compare pairs: O(n²) time, O(1) auxiliary space. A hash set remembers prior values, so lookup is expected constant time and the whole scan expected O(n), while storing up to n values costs O(n) space. If the input is already sorted, two pointers can give O(n) time and O(1) extra space; sorting it first changes the total cost and perhaps the input.

In Android I use this to predict scaling, then check the actual device path. An O(n) algorithm might still be too slow on the main thread for a large n or expensive per-item work. A hash set might create too much memory pressure for a low-end device. I profile frame timing and allocations rather than translating Big O into a promised millisecond number.

## Interview answer — deep senior

Complexity is a model, so I state the input and assumptions before giving symbols. For a list of n prices, the nested-loop pair search does roughly n(n−1)/2 comparisons in the worst case, hence O(n²) time with constant auxiliary storage. The hash-set version holds up to n distinct values and does expected O(n) work under ordinary hash behavior, but that is not a universal worst-case guarantee. If data is sorted beforehand, two pointers need linear scans and constant extra state; the sorting or copying cost must be included if the input was not already sorted.

Space accounting needs equal care. I say whether input and output are counted, include the recursion stack when relevant, and distinguish peak live memory from allocation rate. A Kotlin `HashSet<Int>` also has object and table overhead; O(n) does not tell me the exact bytes. Arithmetic correctness is independent of complexity: adding two `Int` prices can overflow before comparison, so the runnable example widens to `Long` and treats duplicate values at two indices separately.

On Android I use asymptotic growth to reject a design that will scale badly, then profile the real workload. Constants, data distribution, runtime, hardware, and main-thread placement determine whether work disrupts rendering. Moving work to `Dispatchers.Default` may keep the UI responsive but does not make the algorithm faster overall, and too much parallel work can still compete for CPU. For memory pressure I look at peak footprint and allocations on lower-memory target devices. I choose the simplest approach that meets measured latency and memory constraints rather than claiming O(n) guarantees smooth frames or no OOM.

## How to answer in the interview

Name the input size and case, give time and auxiliary space separately for one concrete algorithm, then explain the trade-off and which Android measurement would confirm the choice.

## Deep-dive talking points

Worst versus expected time; auxiliary versus total space; hash assumptions; sorted-input precondition; overflow; peak live memory versus churn; main-thread placement and profiling.

## Follow-up questions

- **Interviewer:** "Is the hash-set solution guaranteed O(n)?" **Answer:** "That is its expected behavior under ordinary hashing; I would not promise that as a worst-case bound."
- **Interviewer:** "Is two pointers O(1) space for any input?" **Answer:** "Only if it is already sorted, or if sorting in place is allowed and its cost is included."
- **Interviewer:** "Does moving O(n²) work to a background dispatcher fix complexity?" **Answer:** "It can avoid blocking the main thread, but it does not reduce the total comparisons."

## Self-check rubric

Can I state n, case, time, auxiliary space, sorting assumptions, and an Android measurement without a made-up timing guarantee?

## References and reviewed-on date

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html) — collection and set behavior.
- [Android rendering performance](https://developer.android.com/topic/performance/issues/render) — frame diagnosis.
- [Android memory overview](https://developer.android.com/topic/performance/memory-overview) — memory pressure.

Technically reviewed against current primary documentation on 2026-10-19; agent editorial review, not human verification.
