---
id: ARC-Q009-ANSWER
question_id: ARC-Q009
status: reviewed
---
# ARC-Q009 — Complete model answer

<p dir="rtl" lang="ar"><strong>الإجابة بالمصري:</strong> ViewModel على مستوى الشاشة تملك state اللازمة للرسم وتنسّق use cases للـ screen. ما تحطش فيها View أو Context مرتبط بـ Activity، وما تخليهاش repository ثانية مليانة SQL وHTTP. لو جزء UI مركب وله state مستقلة وإعادة استخدام، state holder عادية ممكن تمسكه. لو قاعدة منتج معقدة أو مشتركة بين شاشات، استخرج domain use case.</p>

<p dir="rtl" lang="ar">الاستخراج مش هدف عددي. قِس سبب التغيير، lifetime، وإمكانية الاختبار. فلترة بسيطة خاصة بالشاشة ممكن تبقى في ViewModel. workflow دفع أو merge policy للبيانات لازم contract أوضح بعيدًا عن presentation. والـ repository تظل مسؤولة عن تنسيق مصادر البيانات ومصدر الحقيقة.</p>

**Spoken answer:** “A screen ViewModel owns renderable screen state and coordinates product operations. I extract reusable or complex product rules into use cases, and component-specific UI logic into plain state holders with the right lifetime.”

**Common wrong answer:** “Every screen must have one ViewModel and one use case per method.” That adds files without establishing useful behavioral boundaries.

**Follow-up 1:** Can a ViewModel receive an application Context? Sometimes a carefully scoped dependency may require it, but prefer a narrow abstraction and never retain an Activity or View reference.

**Follow-up 2:** How do you detect a ViewModel acting as a repository? Look for transport, SQL, caching, source selection, and transaction decisions mixed with formatting and screen state.

**Rubric:** Explain responsibility, lifetime, extraction triggers, Android reference risks, and repository ownership.
