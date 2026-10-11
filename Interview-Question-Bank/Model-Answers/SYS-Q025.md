---
id: SYS-Q025-ANSWER
question_id: SYS-Q025
status: reviewed
---
# SYS-Q025 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Minimize retention and precision, obtain permission, and separate health metadata from sensitive content.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الtelemetry تثبت stage والduration والresult من غير raw coordinates أوPAN أوtoken أوuser content، وكل identifier لازم تكون scoped وretained لأقصر مدة لازمة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">You need to debug failed location sync without logging coordinates or user identity. Design useful redacted telemetry and its retention and access controls.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Privacy and observability:</strong> الtelemetry تثبت stage والduration والresult من غير raw coordinates أوPAN أوtoken أوuser content، وكل identifier لازم تكون scoped وretained لأقصر مدة لازمة. سجل operation ID عشوائية، coarse error category، age/accuracy buckets، duration وapp/device version؛ طبق redaction قبل النقل وRBAC وretention limit في backend.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـPrivacy and observability: سجل operation ID عشوائية، coarse error category، age/accuracy buckets، duration وapp/device version؛ طبق redaction قبل النقل وRBAC وretention limit في backend.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Sensitive values are safe to log if the dashboard is accessible only to engineers.”

<p dir="rtl" lang="ar">في <strong>Privacy and observability</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الtelemetry تثبت stage والduration والresult من غير raw coordinates أوPAN أوtoken أوuser content، وكل identifier لازم تكون scoped وretained لأقصر مدة لازمة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Privacy and observability: on-device debug bundle بموافقة المستخدم قد تحتوي تفاصيل أكثر لفترة قصيرة؛ production analytics الافتراضية تفضل aggregated وredacted.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Privacy and observability: مرر payload فيها coordinates وtokens وPII عبر كل log/crash/analytics path، وافشل الاختبار لو ظهر raw value؛ راجع إن correlation ما زالت تكفي لإعادة timeline.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Privacy and observability، الـshortcut هي: <bdi dir="ltr">Sensitive values are safe to log if the dashboard is accessible only to engineers.</bdi> ودي تكسر: الtelemetry تثبت stage والduration والresult من غير raw coordinates أوPAN أوtoken أوuser content، وكل identifier لازم تكون scoped وretained لأقصر مدة لازمة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Privacy and observability: مرر payload فيها coordinates وtokens وPII عبر كل log/crash/analytics path، وافشل الاختبار لو ظهر raw value؛ راجع إن correlation ما زالت تكفي لإعادة timeline.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Privacy and observability: on-device debug bundle بموافقة المستخدم قد تحتوي تفاصيل أكثر لفترة قصيرة؛ production analytics الافتراضية تفضل aggregated وredacted.</span>

## English model answer

“Minimize retention and precision, obtain permission, and separate health metadata from sensitive content. I would define identities and state transitions across client and server, design for duplicate and out-of-order delivery, and prove recovery with observable end-to-end evidence. I would test duplicate, delayed, missing, and out-of-order events and observe recovery across both client and server.”
