---
id: AND-Q029-ANSWER
question_id: AND-Q029
status: reviewed
---
# AND-Q029 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “After consuming a prefix, the stack contains unmatched opening brackets in encounter order. A closing bracket must match the top; the final stack must be empty.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Implement balanced brackets and state the stack invariant.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Stack live-coding invariant:</strong> في live coding، الـinvariant هي معنى الـdata structure بعد كل خطوة. بنحددها قبل code، نعمل trace على edge case تكسر الحل الساذج، وبعدها نشتق complexity من عدد الزيارات والعمليات بدل حفظ اسم pattern.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـStack live-coding invariant: اكتب input/output وedge cases، سمّي معنى stack/map/window/search interval، ثم trace مثال adversarial قبل كتابة Kotlin واشتق complexity من عدد الحركات الفعلية.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.”

<p dir="rtl" lang="ar">في <strong>Stack live-coding invariant</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Stack live-coding invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Stack live-coding invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</p>

## Live-coding version

**Problem:** Given `()[]{}` return `true`; given `([)]` return `false`.

```kotlin
fun isBalanced(text: String): Boolean {
    val stack = ArrayDeque<Char>()
    val opening = mapOf(')' to '(', ']' to '[', '}' to '{')
    for (char in text) {
        when (char) {
            '(', '[', '{' -> stack.addLast(char)
            ')', ']', '}' -> if (stack.removeLastOrNull() != opening[char]) return false
        }
    }
    return stack.isEmpty()
}
```

<p dir="rtl" lang="ar"><strong>Trace وcomplexity:</strong> بعد كل character، الـstack فيها الـopening brackets اللي لسه متقفلتش بنفس ترتيب ظهورها. كل character تدخل وتخرج مرة، فالوقت O(n) والذاكرة O(n) في أسوأ حالة.</p>


## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Stack live-coding invariant، الـshortcut هي: <bdi dir="ltr">Recognizing the common pattern is enough; edge cases, the loop invariant, and overflow do not change correctness.</bdi> ودي تكسر: الـloop invariant تصف بالضبط معنى الـdata structure بعد معالجة كل prefix؛ كل iteration تحافظ عليها وتقلل مساحة البحث أو تحرك الحدود مرة واحدة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Stack live-coding invariant: اختبر empty وsingle وduplicates وno-solution وoverflow، وقارن random small inputs بحل brute-force واضح.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Stack live-coding invariant: الحل الأبسط المقبول أفضل لو constraints صغيرة؛ optimization مطلوبة فقط لما تقدر تثبت invariant وmemory trade-off.</span>

## English model answer

“After consuming a prefix, the stack contains unmatched opening brackets in encounter order. A closing bracket must match the top; the final stack must be empty. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
