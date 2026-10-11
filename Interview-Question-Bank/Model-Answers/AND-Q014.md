---
id: AND-Q014-ANSWER
question_id: AND-Q014
status: reviewed
---
# AND-Q014 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Inspect who must call it, required permission, intent filters, sensitive operations, input validation, and whether an internal non-exported proxy is possible.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> أي external Intent أو PendingIntent input غير موثوق لحد validation والauthorization داخل الـcomponent، والـidentity والmutability لازم يكونوا مقصودين.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">What do you inspect before marking an Activity, service, or receiver exported?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Exported component review:</strong> الـIntent مجرد رسالة فيها action وdata وextras، والـintent filter يعمل routing فقط. هو لا يثبت هوية المرسل ولا authorization. PendingIntent تضيف تفويضًا من creator لكن identity وrequestCode وmutability يحددوا هل pending intents هتتبدل أوتتعدل.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـExported component review: حوّل الـIntent إلى typed command بعد فحص action وscheme/host/path والsizes، أعد authorization للحساب الحالي، واستخدم explicit immutable PendingIntent إلا لو fill-in field موثقة مطلوبة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Android matched the intent filter, so the input is trusted and already authorized.”

<p dir="rtl" lang="ar">في <strong>Exported component review</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: أي external Intent أو PendingIntent input غير موثوق لحد validation والauthorization داخل الـcomponent، والـidentity والmutability لازم يكونوا مقصودين. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Exported component review: استخدم non-exported proxy أو verified App Link لو callers الخارجيين محدودين؛ ده يقلل surface بدل توسيع intent filter.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Exported component review: أرسل lookalike host وduplicate params وoversized extras وwrong account وreplayed PendingIntent، واثبت إن الرفض يحصل قبل أي data access أو side effect.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Exported component review، الـshortcut هي: <bdi dir="ltr">Android matched the intent filter, so the input is trusted and already authorized.</bdi> ودي تكسر: أي external Intent أو PendingIntent input غير موثوق لحد validation والauthorization داخل الـcomponent، والـidentity والmutability لازم يكونوا مقصودين.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Exported component review: أرسل lookalike host وduplicate params وoversized extras وwrong account وreplayed PendingIntent، واثبت إن الرفض يحصل قبل أي data access أو side effect.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Exported component review: استخدم non-exported proxy أو verified App Link لو callers الخارجيين محدودين؛ ده يقلل surface بدل توسيع intent filter.</span>

## English model answer

“Inspect who must call it, required permission, intent filters, sensitive operations, input validation, and whether an internal non-exported proxy is possible. I would trace the Android component and process lifecycle, preserve only the state that belongs at each boundary, and verify framework behavior on a device or emulator. I would test recreation, process death, duplicate entry, and invalid external input on an emulator or device.”
