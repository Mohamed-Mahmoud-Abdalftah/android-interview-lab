---
id: COR-Q029-ANSWER
question_id: COR-Q029
status: reviewed
---
# COR-Q029 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Before index i, the map contains values from earlier indices and their chosen indices. I ask whether target minus current exists before inserting current, which prevents using the same element twice and returns according to the specified index policy.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">For two-sum on an unsorted array, state the one-pass hash-map invariant before coding.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Hash-map invariant:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـHash-map invariant: اكتب input/output وedge cases، سمّي معنى stack/map/window/search interval، ثم trace مثال adversarial قبل كتابة Kotlin واشتق complexity من عدد الحركات الفعلية.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.”

<p dir="rtl" lang="ar">في <strong>Hash-map invariant</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Hash-map invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Hash-map invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</p>

## Live-coding version

**Problem:** Given `[2, 7, 11, 15]` and target `9`, return indices `[0, 1]` without using the same element twice.

```kotlin
fun twoSum(values: IntArray, target: Int): IntArray? {
    val seen = HashMap<Int, Int>()
    for ((index, value) in values.withIndex()) {
        val needed = target.toLong() - value.toLong()
        if (needed in Int.MIN_VALUE.toLong()..Int.MAX_VALUE.toLong()) {
            seen[needed.toInt()]?.let { return intArrayOf(it, index) }
        }
        seen.putIfAbsent(value, index)
    }
    return null
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> قبل index=i، الـmap فيها القيم من indices الأصغر فقط؛ عشان كده بنفحص complement قبل insert ومش بنستخدم نفس العنصر مرتين. الوقت expected O(n) والذاكرة O(n).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Hash-map invariant، الـshortcut هي: <bdi dir="ltr">Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.</bdi> ودي تكسر: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Hash-map invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Hash-map invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</span>

## English model answer

“Before index i, the map contains values from earlier indices and their chosen indices. I ask whether target minus current exists before inserting current, which prevents using the same element twice and returns according to the specified index policy. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
