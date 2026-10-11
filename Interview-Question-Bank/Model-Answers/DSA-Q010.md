---
id: DSA-Q010-ANSWER
question_id: DSA-Q010
status: reviewed
---
# DSA-Q010 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Compress dimensions only after proving each state reads values that the overwrite order preserves.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل dp state لها معنى وdependencies معروفة؛ ضغط الأبعاد صحيح فقط لو overwrite order لا تمسح قيمة لسه مطلوبة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Explain when a two-dimensional DP table can be compressed to one row, then show the overwrite-order risk.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في DP optimization:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـDP optimization: اكتب recurrence وbase cases والevaluation order أولًا، نفذ table واضحة، ثم اضغط memory بعد رسم dependencies واتجاه iteration.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Any two-dimensional DP can be reduced to one array by overwriting from left to right.”

<p dir="rtl" lang="ar">في <strong>DP optimization</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل dp state لها معنى وdependencies معروفة؛ ضغط الأبعاد صحيح فقط لو overwrite order لا تمسح قيمة لسه مطلوبة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في DP optimization: احتفظ بالجدول الكامل لو reconstruction أووضوح reasoning أهم من memory؛ rolling array ليست تحسينًا مجانيًا.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار DP optimization: قارن بالrecursive memo oracle على inputs صغيرة، واختبر zero/one boundaries وحالة تكشف overwrite في الاتجاه الغلط.</p>

## Live-coding version

**Problem:** Explain when a two-dimensional DP table can be compressed to one row, then show the overwrite-order risk.

```kotlin
fun minPathSum(grid: Array<IntArray>): Long {
    require(grid.isNotEmpty() && grid[0].isNotEmpty())
    val dp = LongArray(grid[0].size) { Long.MAX_VALUE }
    dp[0] = 0
    for (row in grid) {
        for (column in row.indices) {
            val fromUp = dp[column]
            val fromLeft = if (column > 0) dp[column - 1] else Long.MAX_VALUE
            dp[column] = row[column] + minOf(fromUp, fromLeft)
        }
    }
    return dp.last()
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> وقت تحديث dp[column]، قيمتها القديمة هي from-up والجديدة في dp[column-1] هي from-left. اتجاه الكتابة جزء من correctness، مش تفصيلة optimization.</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في DP optimization، الـshortcut هي: <bdi dir="ltr">Any two-dimensional DP can be reduced to one array by overwriting from left to right.</bdi> ودي تكسر: كل dp state لها معنى وdependencies معروفة؛ ضغط الأبعاد صحيح فقط لو overwrite order لا تمسح قيمة لسه مطلوبة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار DP optimization: قارن بالrecursive memo oracle على inputs صغيرة، واختبر zero/one boundaries وحالة تكشف overwrite في الاتجاه الغلط.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في DP optimization: احتفظ بالجدول الكامل لو reconstruction أووضوح reasoning أهم من memory؛ rolling array ليست تحسينًا مجانيًا.</span>

## English model answer

“Compress dimensions only after proving each state reads values that the overwrite order preserves. I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity. I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.”
