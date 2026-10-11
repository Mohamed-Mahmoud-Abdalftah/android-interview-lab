---
id: EUI-Q008-ANSWER
question_id: EUI-Q008
status: reviewed
---
# EUI-Q008 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Preserve logical focus across adaptive layout changes and avoid trapping keyboard or accessibility navigation.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الfocus تتبع logical item identity قابلة للاستمرار، مش index أوView instance قد تتغير بعد navigation أوadaptive layout أوdata update.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A TV or keyboard-driven screen navigates away and back after the list changes. Design stable focus identity and restoration without pointing to a removed item.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Focus restoration:</strong> الfocus تتبع logical item identity قابلة للاستمرار، مش index أوView instance قد تتغير بعد navigation أوadaptive layout أوdata update. احفظ stable item ID، وبعد عودة البيانات اطلب focus فقط لو العنصر ما زال موجودًا وقابلًا للfocus؛ وإلا اختار fallback منطقي قريب من ترتيب القراءة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـFocus restoration: احفظ stable item ID، وبعد عودة البيانات اطلب focus فقط لو العنصر ما زال موجودًا وقابلًا للfocus؛ وإلا اختار fallback منطقي قريب من ترتيب القراءة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Save the adapter index and request focus on the same index after every recreation.”

<p dir="rtl" lang="ar">في <strong>Focus restoration</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الfocus تتبع logical item identity قابلة للاستمرار، مش index أوView instance قد تتغير بعد navigation أوadaptive layout أوdata update. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Focus restoration: في touch-only flow قد يكفي أول عنصر منطقي؛ TV وkeyboard accessibility تحتاج restoration صريحة ومختبرة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Focus restoration: ركز item، غادر الشاشة، احذف أوحرّك العنصر، ارجع تحت keyboard وTalkBack وlayout مختلف؛ تحقق من target صحيح وعدم focus trap.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Focus restoration، الـshortcut هي: <bdi dir="ltr">Save the adapter index and request focus on the same index after every recreation.</bdi> ودي تكسر: الfocus تتبع logical item identity قابلة للاستمرار، مش index أوView instance قد تتغير بعد navigation أوadaptive layout أوdata update.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Focus restoration: ركز item، غادر الشاشة، احذف أوحرّك العنصر، ارجع تحت keyboard وTalkBack وlayout مختلف؛ تحقق من target صحيح وعدم focus trap.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Focus restoration: في touch-only flow قد يكفي أول عنصر منطقي؛ TV وkeyboard accessibility تحتاج restoration صريحة ومختبرة.</span>

## English model answer

“Preserve logical focus across adaptive layout changes and avoid trapping keyboard or accessibility navigation. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”
