---
id: ARC-Q006-ANSWER
question_id: ARC-Q006
status: reviewed
---
# ARC-Q006 — Complete model answer

<p dir="rtl" lang="ar"><strong>الإجابة بالمصري:</strong> الـ UI تقرأ <code dir="ltr">UiState</code> وترسمها، ولما المستخدم يدوس Save تبعت action للـ state holder. الـ ViewModel تتحقق من input أو تفوض قاعدة المنتج للـ domain، تنشر loading state، وتبدأ العملية في scope مملوكة لها. الـ repository تملك الوصول للبيانات، وبعد النتيجة الـ ViewModel تحولها لحالة نجاح أو فشل. الشاشة ما تستنتجش نجاح من نفسها، وما تعرفش تفاصيل database.</p>

<p dir="rtl" lang="ar"><strong>التتبع:</strong> <code dir="ltr">SaveTapped</code> يدخل، الحالة تصبح pending ومعها request ID، owner يبدأ الحفظ بالـ title snapshot، completion ترجع بنفس ID، ثم reducer تقبلها فقط لو ما زالت العملية الحالية. الـ UI تجمع آخر state بطريقة مرتبطة بالـ lifecycle وتعيد الرسم. ده يخلي اتجاه البيانات مفهوم، لكنه لا يثبت إن التخزين نجح إلا لو repository رجعت contract موثوقة.</p>

**Spoken answer:** “The UI renders immutable state and sends a save action. The ViewModel owns screen state and coordinates the operation, while the repository owns data access. The completion returns to the state holder, which emits a new renderable state.”

**Common wrong answer:** “MVVM means the ViewModel contains all business logic and the Activity only forwards callbacks.” That produces a large state holder and still leaves ownership unclear.

**Follow-up 1:** Where should reusable title validation live? Put reusable product validation in a domain use case or repository boundary, while the ViewModel maps its result into screen state.

**Follow-up 2:** Does immutable UI state make the repository thread safe? No. Immutability simplifies screen transitions; repository concurrency, transactions, and dispatcher policy require their own design and tests.

**Rubric:** Name the action, state holder, state transition, data boundary, lifecycle-aware rendering, and the limit of UI evidence.
