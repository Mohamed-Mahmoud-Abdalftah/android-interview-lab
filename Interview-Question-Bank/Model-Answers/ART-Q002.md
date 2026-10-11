---
id: ART-Q002-ANSWER
question_id: ART-Q002
status: reviewed
---
# ART-Q002 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “D8 desugars and converts bytecode to DEX; R8 can shrink, optimize, and obfuscate according to the build pipeline.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A teammate says D8 and R8 are interchangeable names for the same optimizer. Correct the model and explain what artifact and failure each tool helps you investigate.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في D8 versus R8:</strong> Kotlin compiler تنتج class files، desugaring تعالج language/library features، D8 يحول لـDEX، وR8 يحلل reachability ويعمل shrink/optimize/obfuscate. بعد packaging وsigning، الجهاز يثبت artifact وART تحمل DEX؛ debug وrelease ممكن يختلفوا جذريًا.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـD8 versus R8: حدد أول artifact غلط، افحص release DEX/mapping والloader أو native boundary المعنية، وأضف keep/registration ضيقة بدل تعطيل optimization.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Android executes JVM bytecode directly, so a debug JVM test proves the release ART behavior.”

<p dir="rtl" lang="ar">في <strong>D8 versus R8</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في D8 versus R8: generated adapter أوexplicit registry أبسط من reflection؛ pure Kotlin/JVM test تثبت logic لكنها لا تثبت packaging أو ART behavior.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار D8 versus R8: ابن minified release، افحص DEX وmapping، شغّل affected path على device/version ممثلة، واختبر native cleanup وexception/thread attachment لو JNI داخلة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في D8 versus R8، الـshortcut هي: <bdi dir="ltr">Android executes JVM bytecode directly, so a debug JVM test proves the release ART behavior.</bdi> ودي تكسر: الادعاء مربوط بمرحلة وartifact محددين: source ثم class files ثم DEX/APK ثم ART؛ loader/JNI/reflection تضيف identity وlifetime contracts منفصلة.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار D8 versus R8: ابن minified release، افحص DEX وmapping، شغّل affected path على device/version ممثلة، واختبر native cleanup وexception/thread attachment لو JNI داخلة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في D8 versus R8: generated adapter أوexplicit registry أبسط من reflection؛ pure Kotlin/JVM test تثبت logic لكنها لا تثبت packaging أو ART behavior.</span>

## English model answer

“D8 desugars and converts bytecode to DEX; R8 can shrink, optimize, and obfuscate according to the build pipeline. I would name the exact build or runtime stage, inspect its input and output artifact, and avoid transferring guarantees between Kotlin, JVM bytecode, DEX tooling, and ART. I would inspect the release artifact, mapping, DEX or runtime trace from the exact affected build and device version.”
