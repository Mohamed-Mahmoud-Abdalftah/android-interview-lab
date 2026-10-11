---
id: ART-Q006-ANSWER
question_id: ART-Q006
status: reviewed
---
# ART-Q006 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “JNI crosses managed/native memory, threading, exception, and lifetime rules and should stay narrow.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل ABI تحتاج native library ورموز مطابقة، وكل JNIEnv تخص thread، والlocal/global references والpending exceptions لها lifetime وقواعد صريحة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A native call crashes only on one ABI. Walk through symbol packaging, thread attachment, local and global references, exception checking, and the artifacts you inspect.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في JNI boundary:</strong> كل ABI تحتاج native library ورموز مطابقة، وكل JNIEnv تخص thread، والlocal/global references والpending exceptions لها lifetime وقواعد صريحة. تحقق من ABI packaging وsymbol lookup، attach thread native عند الحاجة، حرر global refs، افحص exceptions بعد JNI calls، ومرر buffers بعقد ownership واضح.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـJNI boundary: تحقق من ABI packaging وsymbol lookup، attach thread native عند الحاجة، حرر global refs، افحص exceptions بعد JNI calls، ومرر buffers بعقد ownership واضح.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A JNI function that works on one ABI and thread is safe on every device and caller thread.”

<p dir="rtl" lang="ar">في <strong>JNI boundary</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل ABI تحتاج native library ورموز مطابقة، وكل JNIEnv تخص thread، والlocal/global references والpending exceptions لها lifetime وقواعد صريحة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في JNI boundary: استخدم pure Kotlin أوstable platform API لو native boundary لا تبرر cost؛ generated bindings تقلل hand-written JNI mistakes.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار JNI boundary: شغّل affected ABI على device، اختبر thread attach/detach وGC أثناء native hold وJava exception وmissing symbol، واربط tombstone بالunstripped symbols لنفس build.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في JNI boundary، الـshortcut هي: <bdi dir="ltr">A JNI function that works on one ABI and thread is safe on every device and caller thread.</bdi> ودي تكسر: كل ABI تحتاج native library ورموز مطابقة، وكل JNIEnv تخص thread، والlocal/global references والpending exceptions لها lifetime وقواعد صريحة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار JNI boundary: شغّل affected ABI على device، اختبر thread attach/detach وGC أثناء native hold وJava exception وmissing symbol، واربط tombstone بالunstripped symbols لنفس build.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في JNI boundary: استخدم pure Kotlin أوstable platform API لو native boundary لا تبرر cost؛ generated bindings تقلل hand-written JNI mistakes.</span>

## English model answer

“JNI crosses managed/native memory, threading, exception, and lifetime rules and should stay narrow. I would name the exact build or runtime stage, inspect its input and output artifact, and avoid transferring guarantees between Kotlin, JVM bytecode, DEX tooling, and ART. I would inspect the release artifact, mapping, DEX or runtime trace from the exact affected build and device version.”
