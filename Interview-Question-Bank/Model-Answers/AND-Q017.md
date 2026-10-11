---
id: AND-Q017-ANSWER
question_id: AND-Q017
status: reviewed
---
# AND-Q017 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A synchronous Binder call blocks the caller. From main, queueing, remote contention, or nested locks can exceed the response budget even when average service time is low.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الـsynchronous Binder call توقف caller لحد reply؛ main thread budget تشمل queueing والremote work والlock contention.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Why can a fast service still cause an ANR through Binder?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Synchronous Binder call:</strong> الـBinder proxy يكتب transaction في kernel driver، والـserver thread يقرأها وينفذها. لو call synchronous فالـcaller تفضل blocked لحد reply؛ زمنها يشمل queueing والremote work وأي lock contention، مش زمن method body بس.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSynchronous Binder call: انقل call من main لو contract تسمح، قلل payload والعمل داخل transaction، ومتحتفظش local lock أثناء IPC.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Binder runs in another process, so a synchronous call cannot block the UI thread.”

<p dir="rtl" lang="ar">في <strong>Synchronous Binder call</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الـsynchronous Binder call توقف caller لحد reply؛ main thread budget تشمل queueing والremote work والlock contention. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Synchronous Binder call: oneway مناسب فقط لcommand لا تحتاج reply أو ordering أقوى؛ مش تحويل آلي لكل Binder call.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Synchronous Binder call: بطّئ remote service واحبس lock متحكم فيه، ثم راقب binder transaction والmain-thread blocked slice في Perfetto/ANR trace.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Synchronous Binder call، الـshortcut هي: <bdi dir="ltr">Binder runs in another process, so a synchronous call cannot block the UI thread.</bdi> ودي تكسر: الـsynchronous Binder call توقف caller لحد reply؛ main thread budget تشمل queueing والremote work والlock contention.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Synchronous Binder call: بطّئ remote service واحبس lock متحكم فيه، ثم راقب binder transaction والmain-thread blocked slice في Perfetto/ANR trace.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Synchronous Binder call: oneway مناسب فقط لcommand لا تحتاج reply أو ordering أقوى؛ مش تحويل آلي لكل Binder call.</span>

## English model answer

“A synchronous Binder call blocks the caller. From main, queueing, remote contention, or nested locks can exceed the response budget even when average service time is low. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
