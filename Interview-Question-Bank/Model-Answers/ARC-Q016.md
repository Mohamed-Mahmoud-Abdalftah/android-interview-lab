---
id: ARC-Q016-ANSWER
question_id: ARC-Q016
status: reviewed
---
# ARC-Q016 — Complete model answer

## الإجابة المختصرة

**Spoken answer:** “Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state.”

<p dir="rtl" lang="ar"><strong>الخلاصة بالمصري:</strong> dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state.</p>

## افهم السؤال قبل ما تجاوب

<p dir="rtl" lang="ar"><strong>المحاور بيديك الحالة دي:</strong> <bdi dir="ltr">A repository is scoped to SingletonComponent and caches the signed-in user. The user logs out and signs in with another account without the process dying. Explain the bug, choose the correct owner for account state, and describe what Hilt does and does not reset.</bdi></p>

<p dir="rtl" lang="ar"><strong>تحت الغطا في Hilt component lifetimes:</strong> Hilt component تحتفظ بالـscoped instance داخل عمر الـcomponent نفسها. SingletonComponent تعيش عمر process، ActivityRetainedComponent تعدي configuration change، وActivityComponent تتبدل مع Activity. لو account state اتحطت Singleton فهي لا تتصفر تلقائيًا عند logout.</p>

<p dir="rtl" lang="ar"><strong>إيه اللي لازم يظهر في إجابتك؟</strong> حدّد الـowner، امشِ في الـexecution order، سمّي الـfailure اللي السؤال كاشفها، وبعدها اربط القرار بـtrade-off واختبار يثبت السلوك.</p>

## القرار العملي

<p dir="rtl" lang="ar">بالنسبة لـHilt component lifetimes: ارسم component graph، انقل account state لـaccount/session owner قابلة للإبطال، استخدم semantic qualifiers، واختبر Hilt replacement والlogout.</p>

## الـfailure والـwrong answer

**Common wrong answer:** “Make the dependency a Singleton so every screen sees the same object forever.”

<p dir="rtl" lang="ar">في <strong>Hilt component lifetimes</strong> المشكلة في الإجابة دي إنها تكسر الـinvariant الأساسية: dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state. النتيجة ممكن تبان سليمة في الـhappy path، وبعد race أوrecreation أوfailure boundary تظهر المشكلة الحقيقية.</p>

## الـtrade-off

<p dir="rtl" lang="ar">في Hilt component lifetimes: constructor injection كافية داخل object graph الصغيرة؛ Hilt تضيف قيمة عند Android lifetimes وتجميع graph، مش لمجرد اتباع pattern.</p>

## الاختبار اللي يثبت الإجابة

<p dir="rtl" lang="ar">لاختبار Hilt component lifetimes: ابدأ account A ثم logout وaccount B، أعد إنشاء component، واثبت عدم تسريب cache أو endpoint؛ شغّل graph test يثبت binding الفعلية.</p>



## Follow-up answers

**Follow-up 1:** What fails if the common shortcut is used? <span dir="rtl" lang="ar">في Hilt component lifetimes، الـshortcut هي: <bdi dir="ltr">Make the dependency a Singleton so every screen sees the same object forever.</bdi> ودي تكسر: dependency lifetime تطابق data owner، والbinding identity معناها واضح، والtest تستبدل أضيق boundary من غير global stale state.</span>

**Follow-up 2:** How do you prove the fix? <span dir="rtl" lang="ar">لاختبار Hilt component lifetimes: ابدأ account A ثم logout وaccount B، أعد إنشاء component، واثبت عدم تسريب cache أو endpoint؛ شغّل graph test يثبت binding الفعلية.</span>

**Follow-up 3:** What constraint could change your choice? <span dir="rtl" lang="ar">في Hilt component lifetimes: constructor injection كافية داخل object graph الصغيرة؛ Hilt تضيف قيمة عند Android lifetimes وتجميع graph، مش لمجرد اتباع pattern.</span>

## English model answer

“Scope lifetime must match the data owner; a singleton cannot safely retain account-scoped mutable state. I would start from ownership and the source of truth, trace validation and side effects, and introduce only the boundaries that protect a real invariant or change axis. I would test state transitions, dependency call counts, stale completions, and the source-of-truth boundary.”
