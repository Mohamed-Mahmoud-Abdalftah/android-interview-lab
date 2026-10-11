---
id: EUI-Q002-ANSWER
question_id: EUI-Q002
status: reviewed
---
# EUI-Q002 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Compose snapshots coordinate state reads and writes; mutable non-observable data can bypass invalidation.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> Compose snapshot تجمع reads وwrites في نسخة متسقة وتطبق mutation policy؛ writes متنافسة تحتاج owner أوmerge واضح بدل افتراض last callback wins.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Two coroutines update Compose snapshot state from different contexts. Explain snapshot consistency, mutation policy, and how conflicting writes become visible.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Snapshot state:</strong> Compose snapshot تجمع reads وwrites في نسخة متسقة وتطبق mutation policy؛ writes متنافسة تحتاج owner أوmerge واضح بدل افتراض last callback wins. اجمع state related في model immutable، نفّذ update من owner واحدة أوsnapshot transaction مناسبة، وانشر value جديدة بدل mutation داخل object غير observable.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSnapshot state: اجمع state related في model immutable، نفّذ update من owner واحدة أوsnapshot transaction مناسبة، وانشر value جديدة بدل mutation داخل object غير observable.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Any mutation made from a coroutine is automatically serialized and visible to Compose.”

<p dir="rtl" lang="ar">في <strong>Snapshot state</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: Compose snapshot تجمع reads وwrites في نسخة متسقة وتطبق mutation policy؛ writes متنافسة تحتاج owner أوmerge واضح بدل افتراض last callback wins. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Snapshot state: StateFlow في ViewModel مناسبة للbusiness state؛ snapshot state محلية ممتازة لUI state المرتبطة بالcomposition.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Snapshot state: اجبر updateين متداخلين على fields مترابطة، اقرأ أثناء composition، واثبت عدم lost update أوstate نصف محدثة وأن invalidation تحصل مرة بالقيمة الصحيحة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Snapshot state، الـshortcut هي: <bdi dir="ltr">Any mutation made from a coroutine is automatically serialized and visible to Compose.</bdi> ودي تكسر: Compose snapshot تجمع reads وwrites في نسخة متسقة وتطبق mutation policy؛ writes متنافسة تحتاج owner أوmerge واضح بدل افتراض last callback wins.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Snapshot state: اجبر updateين متداخلين على fields مترابطة، اقرأ أثناء composition، واثبت عدم lost update أوstate نصف محدثة وأن invalidation تحصل مرة بالقيمة الصحيحة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Snapshot state: StateFlow في ViewModel مناسبة للbusiness state؛ snapshot state محلية ممتازة لUI state المرتبطة بالcomposition.</span>

## English model answer

“Compose snapshots coordinate state reads and writes; mutable non-observable data can bypass invalidation. I would locate the issue in state, composition, layout, draw, input, or semantics, then measure that stage and recheck accessibility after the optimization. I would measure the relevant frame stage on a release-like build and recheck semantics and focus after the change.”
