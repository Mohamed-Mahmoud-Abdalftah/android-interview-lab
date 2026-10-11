---
id: ART-Q010-ANSWER
question_id: ART-Q010
status: reviewed
---
# ART-Q010 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Use release artifacts, dexdump/profile traces, mapping, and device versions; do not infer device behavior from JVM tests.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Compare what a JVM unit test, APK inspection, instrumented test, Perfetto trace, and on-device crash can prove about Android runtime behavior.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Runtime evidence:</strong> كل مرحلة لها artifact مختلف: Kotlin/JVM class، DEX، packaged release، ثم runtime state على ART. class identity تشمل defining ClassLoader؛ JNI تضيف native lifetime/thread rules؛ reflection تخفي reachability عن R8. الدليل لازم يطابق المرحلة.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـRuntime evidence: حدد أول artifact غلط، افحص release DEX/mapping والloader أو native boundary المعنية، وأضف keep/registration ضيقة بدل تعطيل optimization.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Android executes JVM bytecode directly, so a debug JVM test proves the release ART behavior.”

<p dir="rtl" lang="ar">في <strong>Runtime evidence</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Runtime evidence: generated adapter أوexplicit registry أبسط من reflection؛ pure Kotlin/JVM test تثبت logic لكنها لا تثبت packaging أو ART behavior.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Runtime evidence: ابن minified release، افحص DEX وmapping، شغّل affected path على device/version ممثلة، واختبر native cleanup وexception/thread attachment لو JNI داخلة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Runtime evidence، الـshortcut هي: <bdi dir="ltr">Android executes JVM bytecode directly, so a debug JVM test proves the release ART behavior.</bdi> ودي تكسر: الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Runtime evidence: ابن minified release، افحص DEX وmapping، شغّل affected path على device/version ممثلة، واختبر native cleanup وexception/thread attachment لو JNI داخلة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Runtime evidence: generated adapter أوexplicit registry أبسط من reflection؛ pure Kotlin/JVM test تثبت logic لكنها لا تثبت packaging أو ART behavior.</span>

## English model answer

“Use release artifacts, dexdump/profile traces, mapping, and device versions; do not infer device behavior from JVM tests. I would name the exact build or runtime stage, inspect its input and output artifact, and avoid transferring guarantees between Kotlin, JVM bytecode, DEX tooling, and ART. I would inspect the release artifact, mapping, DEX or runtime trace from the exact affected build and device version.”
