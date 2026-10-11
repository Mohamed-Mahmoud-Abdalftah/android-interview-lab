---
id: KOT-Q024-ANSWER
question_id: KOT-Q024
status: reviewed
---
# KOT-Q024 — Complete model answer

<p dir="rtl" lang="ar">JVM غالبًا شايفة runtime class الخارجية List من غير String argument. الـunchecked cast قد تفحص outer object فقط، فيمشي List&lt;Int&gt; تحت promise كاذبة. compiler يضيف cast لما عنصر يتستخدم كـString، وهنا يظهر ClassCastException بعيد عن boundary. الحل validation لكل element أو serializer يحتفظ بالshape، ثم copy typed. احصر أي cast بعد الفحص بدل generic API تخلي caller يخمن النوع.</p>

**Spoken answer:** “Type erasure removes most generic arguments at runtime, so the outer list check cannot prove its elements are strings. The generated element cast may fail only when a value is read. I validate and convert at the boundary or use a serializer carrying the full type description.”

**Common wrong answer:** The JVM validates the generic argument during the cast but delays reporting the error.

**Follow-up 1:** Does `value is List<*>` prove element safety? No, it proves only the outer value is a list with an unknown element type.

**Follow-up 2:** Why copy after validation? The owned typed snapshot prevents a mutable external alias from inserting invalid elements later.

**Rubric:** Mention erased arguments, delayed element casts, boundary validation, richer metadata, and alias control.
