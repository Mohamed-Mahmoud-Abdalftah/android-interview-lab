---
id: AND-Q024-ANSWER
question_id: AND-Q024
status: reviewed
---
# AND-Q024 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Background scheduling is inexact and Doze batches work. Clarify the real user outcome, use push or approved exact mechanisms only when policy permits, and design stale-data UX.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> اختيار Android work API يتحدد من durability وdeadline وuser visibility وقيود البدء؛ retry لا تحصل لفشل permanent ولا تنشئ duplicate effect.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A product asks for a sync exactly every 15 minutes overnight. How do you respond?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Doze and exact timing:</strong> WorkManager تحفظ WorkSpec في database وتعيد جدولة الشغل تحت قيود النظام؛ Foreground Service عملية ظاهرة للمستخدم بإشعار والتزامات بدء ونوع service؛ coroutine داخل screen owner تنتهي بانتهاء الـowner. الاختيار هنا lifetime contract، مش تفضيل API.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـDoze and exact timing: استخدم WorkManager للشغل durable deferrable، Foreground Service للشغل الجاري الظاهر والمسموح، وowner scope للشغل القصير؛ عرّف unique work وretry classification صراحة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Use a Foreground Service for every long task and retry every failure until it succeeds.”

<p dir="rtl" lang="ar">في <strong>Doze and exact timing</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: اختيار Android work API يتحدد من durability وdeadline وuser visibility وقيود البدء؛ retry لا تحصل لفشل permanent ولا تنشئ duplicate effect. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Doze and exact timing: Push قد تكون wake-up hint للتوقيت الخادمي؛ exact alarm لا تستخدم إلا لuser-facing exact requirement مسموحة بالسياسة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Doze and exact timing: اختبر process kill وDoze وduplicate enqueue وpermanent auth failure وstop action على device، وتأكد إن business operation identity لا تتكرر.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Doze and exact timing، الـshortcut هي: <bdi dir="ltr">Use a Foreground Service for every long task and retry every failure until it succeeds.</bdi> ودي تكسر: اختيار Android work API يتحدد من durability وdeadline وuser visibility وقيود البدء؛ retry لا تحصل لفشل permanent ولا تنشئ duplicate effect.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Doze and exact timing: اختبر process kill وDoze وduplicate enqueue وpermanent auth failure وstop action على device، وتأكد إن business operation identity لا تتكرر.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Doze and exact timing: Push قد تكون wake-up hint للتوقيت الخادمي؛ exact alarm لا تستخدم إلا لuser-facing exact requirement مسموحة بالسياسة.</span>

## English model answer

“Background scheduling is inexact and Doze batches work. Clarify the real user outcome, use push or approved exact mechanisms only when policy permits, and design stale-data UX. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
