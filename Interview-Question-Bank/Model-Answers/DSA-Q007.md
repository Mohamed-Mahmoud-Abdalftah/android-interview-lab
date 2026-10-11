---
id: DSA-Q007-ANSWER
question_id: DSA-Q007
status: reviewed
---
# DSA-Q007 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Hash map plus doubly linked order gives expected O(1) get/put when every mutation updates both structures atomically.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـmap والdoubly linked order تصف نفس entries؛ الرأس most recent والذيل least recent، وكل get/put يحدث الاثنين atomically.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Design an LRU cache with expected O(1) get and put. Explain which two structures must stay consistent.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في LRU cache design:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـLRU cache design: استخدم hash map إلى nodes وقائمة sentinel؛ move-to-front عند get/update، وevict tail عند تجاوز capacity مع حذف map entry نفسها.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A HashMap alone can identify the least recently used key in O(1).”

<p dir="rtl" lang="ar">في <strong>LRU cache design</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـmap والdoubly linked order تصف نفس entries؛ الرأس most recent والذيل least recent، وكل get/put يحدث الاثنين atomically. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في LRU cache design: LinkedHashMap access-order أبسط في JVM لو custom eviction/threading غير مطلوبة؛ لا تعيد اختراعها بلا سبب interview واضح.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار LRU cache design: اختبر capacity 0/1، update existing، repeated get، eviction order، وassert list/map consistency بعد كل operation.</p>

## Live-coding version

**Problem:** Design an LRU cache with expected O(1) `get` and `put`. Explain which two structures must stay consistent.

```kotlin
class LruCache<K, V>(private val capacity: Int) {
    private val values = object : LinkedHashMap<K, V>(16, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<K, V>) =
            size > capacity
    }

    fun get(key: K): V? = values[key]
    fun put(key: K, value: V) {
        if (capacity > 0) values[key] = value
    }
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> الـhash lookup يجيب القيمة، وaccess-order list تحدد مين least recently used. أي get ناجحة أوput لازم تحدث الترتيب؛ التنفيذ المتوقع O(1) والذاكرة O(capacity).</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في LRU cache design، الـshortcut هي: <bdi dir="ltr">A HashMap alone can identify the least recently used key in O(1).</bdi> ودي تكسر: الـmap والdoubly linked order تصف نفس entries؛ الرأس most recent والذيل least recent، وكل get/put يحدث الاثنين atomically.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار LRU cache design: اختبر capacity 0/1، update existing، repeated get، eviction order، وassert list/map consistency بعد كل operation.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في LRU cache design: LinkedHashMap access-order أبسط في JVM لو custom eviction/threading غير مطلوبة؛ لا تعيد اختراعها بلا سبب interview واضح.</span>

## English model answer

“Hash map plus doubly linked order gives expected O(1) get/put when every mutation updates both structures atomically. I would define the contract and invariant first, derive the data structure from the required operations, and test adversarial boundaries before claiming complexity. I would trace the invariant and test empty, duplicate, boundary, overflow, and worst-case inputs against a simple oracle.”
