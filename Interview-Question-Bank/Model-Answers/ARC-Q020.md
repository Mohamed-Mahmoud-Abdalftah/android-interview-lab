---
id: ARC-Q020-ANSWER
question_id: ARC-Q020
status: reviewed
---
# ARC-Q020 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A global locator hides dependencies and lifetime, making order-dependent tests and stale state easier to create.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل object لازم تستلم dependencies المطلوبة بشكل ظاهر، والـlifetime والreplacement يفضلوا تحت سيطرة composition root بدل global mutable registry.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A legacy app obtains dependencies from a global object in every screen. You cannot rewrite the app at once. How would you migrate toward constructor injection while keeping releases safe, and where is a small service locator still defensible?</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Service locator trade-off:</strong> كل object لازم تستلم dependencies المطلوبة بشكل ظاهر، والـlifetime والreplacement يفضلوا تحت سيطرة composition root بدل global mutable registry. لف الـlegacy locator خلف adapters صغيرة، وابدأ constructor injection من الـnew code والleaves للداخل. خلي composition root واحدة، وامنع أي registration أو lookup جديد خارج migration seam.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـService locator trade-off: لف الـlegacy locator خلف adapters صغيرة، وابدأ constructor injection من الـnew code والleaves للداخل. خلي composition root واحدة، وامنع أي registration أو lookup جديد خارج migration seam.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A global service locator is equivalent to constructor injection because both eventually return the same object.”

<p dir="rtl" lang="ar">في <strong>Service locator trade-off</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل object لازم تستلم dependencies المطلوبة بشكل ظاهر، والـlifetime والreplacement يفضلوا تحت سيطرة composition root بدل global mutable registry. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Service locator trade-off: locator محلية immutable داخل plugin boundary أو framework callback قد تكون مقبولة لو lookup surface صغيرة والlifetime صريحة؛ global mutable locator ليست نفس الحالة.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Service locator trade-off: شغّل testين بترتيب عكسي وتأكد إن مفيش global registration متسربة، وابنِ object graph بfake واحدة من غير reset سحري أو Android process جديد.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Service locator trade-off، الـshortcut هي: <bdi dir="ltr">A global service locator is equivalent to constructor injection because both eventually return the same object.</bdi> ودي تكسر: كل object لازم تستلم dependencies المطلوبة بشكل ظاهر، والـlifetime والreplacement يفضلوا تحت سيطرة composition root بدل global mutable registry.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Service locator trade-off: شغّل testين بترتيب عكسي وتأكد إن مفيش global registration متسربة، وابنِ object graph بfake واحدة من غير reset سحري أو Android process جديد.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Service locator trade-off: locator محلية immutable داخل plugin boundary أو framework callback قد تكون مقبولة لو lookup surface صغيرة والlifetime صريحة؛ global mutable locator ليست نفس الحالة.</span>

## English model answer

“A global locator hides dependencies and lifetime, making order-dependent tests and stale state easier to create. I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis. I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.”
