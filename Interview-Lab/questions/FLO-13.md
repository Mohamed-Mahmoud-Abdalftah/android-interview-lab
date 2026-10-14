---
id: "FLO-13"
question: "Compare combine and zip."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 126
editorial_status: "reviewed"
---

# FLO-13

## Original interview question

Compare combine and zip.

## What the interviewer evaluates

Compare latest-pair combination with positional pairing.

## Explanation in Arabic

المقارنة بين `combine` و `zip` بتحدد كيفية دمج تدفقين من البيانات (Merging two Flows):

1. المشغل `combine` (الدمج عند أي تحديث جديد):
   - يدمج التدفقين، و **يصدر قيمة جديدة في كل مرة يصدر فيها أي من التدفقين قيمة جديدة** (بشرط أن يكون كلا التدفقين قد أصدرا قيمة أولى على الأقل).
   - يأخذ أحدث قيمة من التدفق الأول مع أحدث قيمة من التدفق الثاني (Latest values combined).
   - **الاستخدام المثالي في Android:** تجميع مدخلات شاشة متعددة (مثل: نص البحث + خيار الفلتر المختار + حالة الاتصال بالإنترنت) لتوليد حالة الـ UI.

2. المشغل `zip` (الربط الزوجي المتسلسل 1:1):
   - يربط العناصر **زوجاً بزوج حسب الترتيب (Strict 1-to-1 Pairing)**.
   - العنصر الأول من التدفق A يُربط فقط مع العنصر الأول من التدفق B. والعنصر الثاني مع الثاني، وهكذا.
   - لو التدفق A أصدر 10 عناصر بينما التدفق B أصدر عنصراً واحداً فقط، الـ `zip` سينتظر ويتعلق حتى يصدر B عنصره الثاني قبل إنتاج الزوج الثاني!
   - ينتهي البث بمجرد انتهاء أقصر تدفق بينهما.

## Practical walkthrough

مقارنة عملية في الكود:
```kotlin
val flowA = flowOf("A1", "A2", "A3")
val flowB = flowOf("B1", "B2")

// مع zip:
flowA.zip(flowB) { a, b -> "$a-$b" }.collect { println(it) }
// النتيجة: "A1-B1", "A2-B2" فقط! (A3 تم تجاهله لأن B انتهى)

// مع combine في الـ ViewModel الحقيقي:
combine(
    searchQueryFlow,
    selectedCategoryFlow,
    sortByFlow
) { query, category, sort ->
    // كلما غير المستخدم الفلتر أو الحرف المكتوب، يتم إنتاج حالة جديدة فوراً بأحدث القيم:
    FilterState(query, category, sort)
}.collect { updateUi(it) }
```

## Why it matters and how it works

`combine` can emit many outputs for a burst from one side using latest counterpart; it is not an atomic database snapshot across independent sources. `zip` queues/pairs emissions and completes when pairs cannot continue. Choose based on temporal semantics, not just syntax.

## Worked example

JVM example uses coroutines-core; both streams are typed and the combined result is current UI data.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.zip

fun visible(items: Flow<List<String>>, query: Flow<String>): Flow<List<String>> =
    items.combine(query) { all, q -> all.filter { it.contains(q, true) } }
fun paired(a: Flow<Int>, b: Flow<Int>): Flow<Pair<Int, Int>> =
    a.zip(b) { x, y -> x to y }
```

## Trade-offs and decision criteria

Combine reacts to independent state changes but may recompute frequently; debounce or distinct state upstream if appropriate. Zip preserves positional pairing but can stall if one side pauses and silently truncate when one completes early.

## Failure modes

Zipping a rapidly changing search query with Room items gives mismatched positional pairs and stale UI. Combining two server responses without version or transaction validation can still create a logically inconsistent composite.

## Production perspective

A catalog screen combines current cached items with text filter state, showing a new list on either change. A backend quote requiring correlated prices uses a server-generated version or transaction ID rather than assuming combine makes independent data atomic.

## Interview answer — short

combine emits a new paired value whenever EITHER flow emits, using the latest values from both streams; zip pairs elements strictly 1-to-1 by order index (item 1 with item 1, item 2 with item 2) and halts when the shorter flow completes.

## Interview answer — structured

The difference between `combine` and `zip` comes down to temporal pairing versus index-based pairing.

**`combine`** is the standard workhorse for Android UI state generation. Once each upstream flow emits at least once, `combine` produces a new value whenever *either* flow emits, pairing the newly emitted item with the most recent cached item from the other stream. I use it constantly in ViewModels to merge search text, category filters, and user authentication status into a single unified `UiState`.

**`zip`** enforces strict index-based 1-to-1 pairing. Element 0 from Flow A is paired only with Element 0 from Flow B. If Flow A emits 5 items while Flow B emits 1, `zip` suspends after the first pair, waiting until Flow B produces its second item. Furthermore, `zip` terminates as soon as the shorter flow completes.


## Interview answer — deep senior

Under the hood, `combine` is implemented using internal channels and fair selector loops (`select` expression). It maintains internal state slots for each upstream stream. When any upstream sends a new value, the slot is updated, and the transform lambda is evaluated with the latest snapshot of all slots.

In contrast, `zip` buffers upstream emissions sequentially in paired queues. If one flow is fast and the other is slow, `zip` buffers the fast flow's items in memory waiting for corresponding pairs, which can create heap memory pressure if the flows emit at vastly different cadences.

In modern Android development, `combine` supports merging up to 5 flows directly with type-safe overloads, or an arbitrary `Array<Flow<T>>` for dynamic widget configurations.


## How to answer in the interview

- **Why:** live UI needs latest combination, finite pairs need matching positions.
- **How:** trace unequal-rate sources.
- **Trade-off:** combine can update often; zip waits.
- **Failure case:** zip leaves dashboard stale.
- **Production solution:** test first emission and completion behavior.

## Deep-dive talking points

Trace emission timelines for both operators and identify where version consistency must be enforced.

## Follow-up questions

- **Interviewer:** "Why won't `combine` emit anything if one of the flows never emits an initial item?"
  **Answer:** "Because `combine` requires a full set of values to evaluate its transform lambda. If Flow A emits 10 values but Flow B has not emitted anything yet, `combine` buffers the latest from Flow A and remains silent until Flow B emits its first element."

- **Interviewer:** "Can you combine more than 5 flows in Kotlin?"
  **Answer:** "Yes. There is an overload `combine(vararg flows: Flow<T>) { array -> ... }` that takes an array or collection of flows, returning an array of latest values."

- **Interviewer:** "When would you actually use `zip` in a real Android app?"
  **Answer:** "When you have two ordered sequential streams that correspond 1-to-1, such as pairing a stream of recorded audio frames with a synchronized stream of video frame timestamps."

## Self-check rubric

Can I draw both timelines, predict completion and state one cross-source consistency limit?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — combine and zip.

Technically reviewed against primary documentation on 2026-10-13.
