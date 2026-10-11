---
id: PRO-Q029-ANSWER
question_id: PRO-Q029
status: reviewed
---
# PRO-Q029 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Test every supported installed schema to the target and destructive fallback policy explicitly.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل schema version مدعومة لها path للtarget يحافظ على rows والconstraints؛ فتح database جديدة لا يثبت upgrade للمستخدمين الحاليين.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Your Room database supports versions 4 through 9. Which migration paths must CI execute, what data assertions belong after opening version 9, and why is a clean install irrelevant?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Migration coverage:</strong> Room schema version على أجهزة المستخدمين قديمة بسنين. نجاح clean install يختبر target schema فقط؛ MigrationTestHelper لازم تفتح database fixture من كل starting version، تطبق path للtarget، وبعدها تفحص rows وindices وforeign keys.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـMigration coverage: احتفظ schema exports وfixtures لكل starting version، شغّل MigrationTestHelper للtarget، واعمل data assertions للindices وFKs وdefaults.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The newest schema opens on a clean install, so migration coverage is complete.”

<p dir="rtl" lang="ar">في <strong>Migration coverage</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل schema version مدعومة لها path للtarget يحافظ على rows والconstraints؛ فتح database جديدة لا يثبت upgrade للمستخدمين الحاليين. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Migration coverage: destructive migration مسموحة فقط لcache قابلة لإعادة البناء وبقرار product صريح؛ مش للبيانات التي أنشأها المستخدم.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Migration coverage: افتح fixture حقيقية لكل version، هاجرها خطوة بخطوة ومباشرًا حسب graph، ثم تحقق من user-authored data والconstraints وعدم destructive fallback.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Migration coverage، الـshortcut هي: <bdi dir="ltr">The newest schema opens on a clean install, so migration coverage is complete.</bdi> ودي تكسر: كل schema version مدعومة لها path للtarget يحافظ على rows والconstraints؛ فتح database جديدة لا يثبت upgrade للمستخدمين الحاليين.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Migration coverage: افتح fixture حقيقية لكل version، هاجرها خطوة بخطوة ومباشرًا حسب graph، ثم تحقق من user-authored data والconstraints وعدم destructive fallback.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Migration coverage: destructive migration مسموحة فقط لcache قابلة لإعادة البناء وبقرار product صريح؛ مش للبيانات التي أنشأها المستخدم.</span>

## English model answer

“Test every supported installed schema to the target and destructive fallback policy explicitly. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
