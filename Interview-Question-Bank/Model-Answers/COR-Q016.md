---
id: COR-Q016-ANSWER
question_id: COR-Q016
status: reviewed
---
# COR-Q016 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A cold Flow executes its upstream separately for every collector. I either keep one collector, move the request behind a cache, or share it with stateIn or shareIn in a scope whose lifetime and start policy match the feature.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> كل collector للـcold Flow يشغّل upstream مستقلة؛ مشاركة النتيجة تحتاج scope وstart policy وreplay contract مقصودين.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">Two collectors collect the same cold Flow and duplicate a network request. Explain the behavior and valid fixes.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Cold flow collection:</strong> الـcold Flow وصف للتنفيذ؛ كل collect تستدعي builder وupstream من البداية. stateIn أوshareIn يشغلوا upstream واحدة داخل scope محددة ويعرضوا hot stream، لذلك start policy وreplay وscope lifetime جزء من correctness.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـCold flow collection: لو الطلب واحد للfeature شاركه بـstateIn/shareIn داخل scope مناسب أو انقل fetch خلف cache/source of truth؛ متجمعش نفس cold upstream في أكتر من layer بلا قصد.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “A Flow is shared automatically, so multiple collectors cannot duplicate upstream work.”

<p dir="rtl" lang="ar">في <strong>Cold flow collection</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: كل collector للـcold Flow يشغّل upstream مستقلة؛ مشاركة النتيجة تحتاج scope وstart policy وreplay contract مقصودين. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Cold flow collection: سيب الـFlow cold لو كل collector فعلًا محتاج execution مستقلة؛ sharing تغير lifetime والذاكرة والفشل.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Cold flow collection: شغّل collectorين بعداد fake upstream، اثبت callين في التصميم القديم وcall واحدة مع sharing، ثم اختبر stop timeout وإعادة الاشتراك.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Cold flow collection، الـshortcut هي: <bdi dir="ltr">A Flow is shared automatically, so multiple collectors cannot duplicate upstream work.</bdi> ودي تكسر: كل collector للـcold Flow يشغّل upstream مستقلة؛ مشاركة النتيجة تحتاج scope وstart policy وreplay contract مقصودين.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Cold flow collection: شغّل collectorين بعداد fake upstream، اثبت callين في التصميم القديم وcall واحدة مع sharing، ثم اختبر stop timeout وإعادة الاشتراك.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Cold flow collection: سيب الـFlow cold لو كل collector فعلًا محتاج execution مستقلة؛ sharing تغير lifetime والذاكرة والفشل.</span>

## English model answer

“A cold Flow executes its upstream separately for every collector. I either keep one collector, move the request behind a cache, or share it with stateIn or shareIn in a scope whose lifetime and start policy match the feature. I would make scope ownership, cancellation, failure propagation, and the final state mutation explicit, then verify the race with deterministic coroutine tests. I would reproduce the interleaving with virtual time and controlled fakes, including cancellation and stale completion.”
