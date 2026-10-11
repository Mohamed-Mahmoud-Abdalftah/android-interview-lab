---
id: DSA-Q006-ANSWER
question_id: DSA-Q006
status: reviewed
---
# DSA-Q006 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Sort by start; the output contains disjoint merged intervals and the last is the only candidate for overlap.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> بعد معالجة أول i intervals المرتبة بالstart، الناتج disjoint ويمثل اتحادها، وآخر interval فقط ممكن تتداخل مع التالية.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Merge [[1,3],[2,6],[8,10],[10,12]] using an explicitly stated closed-interval policy.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Interval merge invariant:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـInterval merge invariant: رتب بالstart ثم end، انسخ أول interval، وادمج لو next.start &lt;= last.end حسب closed/open contract؛ وإلا أضف interval جديدة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Compare each interval only with its original neighbor; sorting and the output invariant are optional.”

<p dir="rtl" lang="ar">في <strong>Interval merge invariant</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: بعد معالجة أول i intervals المرتبة بالstart، الناتج disjoint ويمثل اتحادها، وآخر interval فقط ممكن تتداخل مع التالية. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Interval merge invariant: sweep-line يلزم لو محتاج counts/events متعددة؛ sort-and-merge أبسط لإخراج الاتحاد مرة واحدة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Interval merge invariant: اختبر empty وcontained/touching/disjoint وunsorted inputs وinteger boundaries، وقارن الاتحاد مع point-set oracle على ranges صغيرة.</p>

## Live-coding version

**Problem:** Merge `[[1,3],[2,6],[8,10],[10,12]]` using an explicitly stated closed-interval policy.

```kotlin
data class Interval(val start: Int, val end: Int)

fun merge(input: List<Interval>): List<Interval> {
    if (input.isEmpty()) return emptyList()
    val sorted = input.sortedWith(compareBy(Interval::start, Interval::end))
    val result = mutableListOf(sorted.first())
    for (next in sorted.drop(1)) {
        val last = result.last()
        if (next.start <= last.end) {
            result[result.lastIndex] = last.copy(end = maxOf(last.end, next.end))
        } else {
            result += next
        }
    }
    return result
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> بعد معالجة prefix من القائمة المرتبة، result فيها intervals منفصلة وتمثل نفس الاتحاد. الـsorting O(n log n)، والmerge نفسها O(n).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Interval merge invariant، الـshortcut هي: <bdi dir="ltr">Compare each interval only with its original neighbor; sorting and the output invariant are optional.</bdi> ودي تكسر: بعد معالجة أول i intervals المرتبة بالstart، الناتج disjoint ويمثل اتحادها، وآخر interval فقط ممكن تتداخل مع التالية.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Interval merge invariant: اختبر empty وcontained/touching/disjoint وunsorted inputs وinteger boundaries، وقارن الاتحاد مع point-set oracle على ranges صغيرة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Interval merge invariant: sweep-line يلزم لو محتاج counts/events متعددة؛ sort-and-merge أبسط لإخراج الاتحاد مرة واحدة.</span>

## English model answer

“Sort by start; the output contains disjoint merged intervals and the last is the only candidate for overlap. I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity. I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.”
