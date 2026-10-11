---
id: PRO-Q030-ANSWER
question_id: PRO-Q030
status: reviewed
---
# PRO-Q030 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Maintain a search interval that still contains every possible answer and compute midpoint without overflow.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Given sorted [1, 4, 7, 9, 13] and target 9, return index 3; return -1 when absent.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Binary-search invariant:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـBinary-search invariant: اكتب input/output وedge cases، سمّي معنى stack/map/window/search interval، ثم trace مثال adversarial قبل كتابة Kotlin واشتق complexity من عدد الحركات الفعلية.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.”

<p dir="rtl" lang="ar">في <strong>Binary-search invariant</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Binary-search invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Binary-search invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</p>

## Live-coding version

**Problem:** Given sorted `[1, 4, 7, 9, 13]` and target `9`, return index `3`; return `-1` when absent.

```kotlin
fun binarySearch(values: IntArray, target: Int): Int {
    var low = 0
    var high = values.lastIndex
    while (low <= high) {
        val mid = low + (high - low) / 2
        when {
            values[mid] < target -> low = mid + 1
            values[mid] > target -> high = mid - 1
            else -> return mid
        }
    }
    return -1
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> في بداية كل iteration، لو target موجود فهي جوه [low, high]. كل مقارنة تشيل نصف مستحيل، فالوقت O(log n) والذاكرة O(1).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Binary-search invariant، الـshortcut هي: <bdi dir="ltr">Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.</bdi> ودي تكسر: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Binary-search invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Binary-search invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</span>

## English model answer

“Maintain a search interval that still contains every possible answer and compute midpoint without overflow. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
