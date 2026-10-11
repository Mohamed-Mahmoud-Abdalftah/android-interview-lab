---
id: PRO-Q020-ANSWER
question_id: PRO-Q020
status: reviewed
---
# PRO-Q020 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Protect upload/signing keys, rotate through supported mechanisms, and never treat client signatures as server authorization.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> هوية التطبيق تعتمد على signing lineage؛ upload key ترسل artifact إلى Play بينما app-signing key توقع النسخة التي تصل للمستخدم، ولا واحدة منهما توضع داخل repository أوAPK.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Walk through Android app signing from CI to Play delivery. Which keys exist, where should each live, and what breaks if the upload key or app signing key is compromised?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Signing boundary:</strong> هوية التطبيق تعتمد على signing lineage؛ upload key ترسل artifact إلى Play بينما app-signing key توقع النسخة التي تصل للمستخدم، ولا واحدة منهما توضع داخل repository أوAPK. استخدم Play App Signing، خزّن upload credential في CI secret store بصلاحية محدودة، فعّل rotation والاسترجاع، واربط كل release بالartifact digest وsigning certificate المتوقع.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـSigning boundary: استخدم Play App Signing، خزّن upload credential في CI secret store بصلاحية محدودة، فعّل rotation والاسترجاع، واربط كل release بالartifact digest وsigning certificate المتوقع.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “The signing password inside gradle.properties is sufficient protection for a production signing key.”

<p dir="rtl" lang="ar">في <strong>Signing boundary</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: هوية التطبيق تعتمد على signing lineage؛ upload key ترسل artifact إلى Play بينما app-signing key توقع النسخة التي تصل للمستخدم، ولا واحدة منهما توضع داخل repository أوAPK. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Signing boundary: لو التوزيع خارج Play، HSM أوmanaged signing service تمسك production key؛ local keystore مناسبة فقط لبيئات التطوير المقيدة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Signing boundary: تحقق في CI من certificate digest للartifact، ارفض unsigned أوwrong-key bundle، وجرّب update path على نسخة موقعة من release lineage الصحيحة.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Signing boundary، الـshortcut هي: <bdi dir="ltr">The signing password inside gradle.properties is sufficient protection for a production signing key.</bdi> ودي تكسر: هوية التطبيق تعتمد على signing lineage؛ upload key ترسل artifact إلى Play بينما app-signing key توقع النسخة التي تصل للمستخدم، ولا واحدة منهما توضع داخل repository أوAPK.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Signing boundary: تحقق في CI من certificate digest للartifact، ارفض unsigned أوwrong-key bundle، وجرّب update path على نسخة موقعة من release lineage الصحيحة.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Signing boundary: لو التوزيع خارج Play، HSM أوmanaged signing service تمسك production key؛ local keystore مناسبة فقط لبيئات التطوير المقيدة.</span>

## English model answer

“Protect upload/signing keys, rotate through supported mechanisms, and never treat client signatures as server authorization. I would classify the failure, correlate it with the exact release and cohort, protect irreversible side effects, and define rollout and rollback evidence before changing production behavior. I would use a release-like build, comparable cohorts and percentiles, failure injection, and a predefined rollback threshold.”
