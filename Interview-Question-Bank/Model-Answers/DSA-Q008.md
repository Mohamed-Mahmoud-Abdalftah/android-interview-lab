---
id: DSA-Q008-ANSWER
question_id: DSA-Q008
status: reviewed
---
# DSA-Q008 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A size-k min-heap costs O(n log k) and avoids sorting all n when k is small.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> بعد معالجة i عناصر، الـmin-heap تحتوي أكبر min(k, i) عناصر شوفتهم، والـroot أصغر عنصر داخل الـTop K الحالية.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Return the largest k values from a stream while using O(k) extra memory; state how duplicates are handled.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Top K selection:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـTop K selection: احتفظ بـmin-heap حجمها k: أضف لحد k، وبعدها استبدل الـroot فقط لما العنصر الجديد أكبر؛ عرّف سياسة duplicates وترتيب الناتج صراحة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Put every value in a HashSet; that automatically returns the Top K values in order.”

<p dir="rtl" lang="ar">في <strong>Top K selection</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: بعد معالجة i عناصر، الـmin-heap تحتوي أكبر min(k, i) عناصر شوفتهم، والـroot أصغر عنصر داخل الـTop K الحالية. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Top K selection: لو k قريب من n أو محتاج output مرتبة بالكامل، sorting قد تكون أبسط؛ Quickselect مناسب لو average O(n) مقبول والترتيب النهائي غير مطلوب.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Top K selection: قارن بالـfull sort على random small inputs، واختبر k=0 وk&gt;n وduplicates وnegative values وk قريب من n.</p>

## Live-coding version

**Problem:** Return the largest `k` values from a stream while using O(k) extra memory; state how duplicates are handled.

```kotlin
fun topK(values: IntArray, k: Int): List<Int> {
    if (k <= 0) return emptyList()
    val heap = java.util.PriorityQueue<Int>()
    for (value in values) {
        if (heap.size < k) heap += value
        else if (value > heap.peek()) {
            heap.poll()
            heap += value
        }
    }
    return heap.toList().sortedDescending()
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> بعد i عناصر، الـmin-heap فيها أكبر min(k,i) قيم. كل update تكلف O(log k)، فالإجمالي O(n log k) والذاكرة O(k).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Top K selection، الـshortcut هي: <bdi dir="ltr">Put every value in a HashSet; that automatically returns the Top K values in order.</bdi> ودي تكسر: بعد معالجة i عناصر، الـmin-heap تحتوي أكبر min(k, i) عناصر شوفتهم، والـroot أصغر عنصر داخل الـTop K الحالية.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Top K selection: قارن بالـfull sort على random small inputs، واختبر k=0 وk&gt;n وduplicates وnegative values وk قريب من n.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Top K selection: لو k قريب من n أو محتاج output مرتبة بالكامل، sorting قد تكون أبسط؛ Quickselect مناسب لو average O(n) مقبول والترتيب النهائي غير مطلوب.</span>

## English model answer

“A size-k min-heap costs O(n log k) and avoids sorting all n when k is small. I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity. I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.”
