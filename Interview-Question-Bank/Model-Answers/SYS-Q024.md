---
id: SYS-Q024-ANSWER
question_id: SYS-Q024
status: reviewed
---
# SYS-Q024 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Expose timestamp and accuracy, adapt rate to user value, and stop collection with owner lifetime.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل location لها timestamp وaccuracy وprovider context؛ القيمة الأحدث وصولًا ليست بالضرورة الأحدث قياسًا أوالأدق، والpermission/background policy جزء من العقد.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A courier app shows location. Define freshness, accuracy, permission, battery, background, and out-of-order update rules before choosing the API and interval.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Location freshness:</strong> كل location لها timestamp وaccuracy وprovider context؛ القيمة الأحدث وصولًا ليست بالضرورة الأحدث قياسًا أوالأدق، والpermission/background policy جزء من العقد. حدد max age وrequired accuracy للjourney، ارفض out-of-order measurements بالelapsed realtime، ووازن interval وpriority مع battery والforeground/background rules.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـLocation freshness: حدد max age وrequired accuracy للjourney، ارفض out-of-order measurements بالelapsed realtime، ووازن interval وpriority مع battery والforeground/background rules.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The last callback received is always the freshest and most accurate location.”

<p dir="rtl" lang="ar">في <strong>Location freshness</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل location لها timestamp وaccuracy وprovider context؛ القيمة الأحدث وصولًا ليست بالضرورة الأحدث قياسًا أوالأدق، والpermission/background policy جزء من العقد. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Location freshness: last-known location مناسبة كبداية معلّمة stale؛ active high-accuracy updates تستخدم فقط لما user journey تبرر battery والpermission cost.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Location freshness: أرسل fixes قديمة تصل متأخر، accuracy ضعيفة، permission downgrade، provider off، background transition، وclock change؛ تحقق من stale UI وfallback الواضح.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Location freshness، الـshortcut هي: <bdi dir="ltr">The last callback received is always the freshest and most accurate location.</bdi> ودي تكسر: كل location لها timestamp وaccuracy وprovider context؛ القيمة الأحدث وصولًا ليست بالضرورة الأحدث قياسًا أوالأدق، والpermission/background policy جزء من العقد.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Location freshness: أرسل fixes قديمة تصل متأخر، accuracy ضعيفة، permission downgrade، provider off، background transition، وclock change؛ تحقق من stale UI وfallback الواضح.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Location freshness: last-known location مناسبة كبداية معلّمة stale؛ active high-accuracy updates تستخدم فقط لما user journey تبرر battery والpermission cost.</span>

## English model answer

“Expose timestamp and accuracy, adapt rate to user value, and stop collection with owner lifetime. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
