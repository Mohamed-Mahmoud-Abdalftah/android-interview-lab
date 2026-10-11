---
id: PRO-Q017-ANSWER
question_id: PRO-Q017
status: reviewed
---
# PRO-Q017 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Verify Gradle, AGP, Kotlin, JDK, and Compose compiler compatibility from current official tables.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل build stage لها artifact ودليل منفصل، والrelease variant لا تحتوي debug dependency أو secret، والshrinking contract أضيق من keep-all.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">The app builds after upgrading AGP but fails only on API 23 release devices. Build a compatibility investigation across JDK, Gradle, AGP, Kotlin, desugaring, minSdk, and device runtime.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Compatibility matrix:</strong> Kotlin compiler تنتج class files، desugaring تعالج language/library features، D8 يحول لـDEX، وR8 يحلل reachability ويعمل shrink/optimize/obfuscate. بعد packaging وsigning، الجهاز يثبت artifact وART تحمل DEX؛ debug وrelease ممكن يختلفوا جذريًا.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCompatibility matrix: ثبّت tool versions من compatibility tables، ابن واختبر minified release في CI، افحص dependency/APK output، واحفظ mapping وsigning material بصلاحيات محدودة.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “If debug works, release is equivalent; disable shrinking when something disappears.”

<p dir="rtl" lang="ar">في <strong>Compatibility matrix</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل build stage لها artifact ودليل منفصل، والrelease variant لا تحتوي debug dependency أو secret، والshrinking contract أضيق من keep-all. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Compatibility matrix: generated adapters أوexplicit registration تقلل reflection keep rules؛ disabling R8 يخفي contract ويكبر artifact.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Compatibility matrix: شغّل release smoke path، retrace crash بالmapping المطابقة، افحص DEX/resources/dependencies، وافشل CI لو debug endpoint أو forbidden class ظهرت.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Compatibility matrix، الـshortcut هي: <bdi dir="ltr">If debug works, release is equivalent; disable shrinking when something disappears.</bdi> ودي تكسر: كل build stage لها artifact ودليل منفصل، والrelease variant لا تحتوي debug dependency أو secret، والshrinking contract أضيق من keep-all.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Compatibility matrix: شغّل release smoke path، retrace crash بالmapping المطابقة، افحص DEX/resources/dependencies، وافشل CI لو debug endpoint أو forbidden class ظهرت.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Compatibility matrix: generated adapters أوexplicit registration تقلل reflection keep rules؛ disabling R8 يخفي contract ويكبر artifact.</span>

## English model answer

“Verify Gradle, AGP, Kotlin, JDK, and Compose compiler compatibility from current official tables. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
