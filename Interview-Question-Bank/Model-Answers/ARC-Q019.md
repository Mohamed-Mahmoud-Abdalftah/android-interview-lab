---
id: ARC-Q019-ANSWER
question_id: ARC-Q019
status: reviewed
---
# ARC-Q019 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “A test replaces the narrow boundary and verifies graph wiring plus behavior; constructor tests alone do not prove Hilt installation.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">You need an integration test that replaces the real payments gateway while keeping the production database graph. Show the Hilt test replacement you would use, the scope it must preserve, and what the test still cannot prove.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في DI replacement tests:</strong> Hilt component تحتفظ بالـscoped instance داخل عمر الـcomponent نفسها. SingletonComponent تعيش عمر process، ActivityRetainedComponent تعدي configuration change، وActivityComponent تتبدل مع Activity. لو account state اتحطت Singleton فهي لا تتصفر تلقائيًا عند logout.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـDI replacement tests: ارسم component graph، انقل account state لـaccount/session owner قابلة للإبطال، استخدم semantic qualifiers، واختبر Hilt replacement والlogout.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Make the dependency a Singleton so every screen sees the same object forever.”

<p dir="rtl" lang="ar">في <strong>DI replacement tests</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في DI replacement tests: constructor injection كافية داخل object graph الصغيرة؛ Hilt تضيف قيمة عند Android lifetimes وتجميع graph، مش لمجرد اتباع pattern.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار DI replacement tests: ابدأ account A ثم logout وaccount B، أعد إنشاء component، واثبت عدم تسريب cache أو endpoint؛ شغّل graph test يثبت binding الفعلية.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في DI replacement tests، الـshortcut هي: <bdi dir="ltr">Make the dependency a Singleton so every screen sees the same object forever.</bdi> ودي تكسر: dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار DI replacement tests: ابدأ account A ثم logout وaccount B، أعد إنشاء component، واثبت عدم تسريب cache أو endpoint؛ شغّل graph test يثبت binding الفعلية.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في DI replacement tests: constructor injection كافية داخل object graph الصغيرة؛ Hilt تضيف قيمة عند Android lifetimes وتجميع graph، مش لمجرد اتباع pattern.</span>

## English model answer

“A test replaces the narrow boundary and verifies graph wiring plus behavior; constructor tests alone do not prove Hilt installation. I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis. I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.”
