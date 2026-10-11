---
id: KOT-Q025-ANSWER
question_id: KOT-Q025
status: reviewed
---
# KOT-Q025 — Complete model answer

<p dir="rtl" lang="ar">reified مع inline تخلي compiler يحط runtime type المباشرة عند call site، فتقدر تستخدم <code dir="ltr">T::class</code> أو <code dir="ltr">value is T</code> وتبني typed factory من غير caller يمرر class يدويًا. لكنها لا تثبت عناصر nested generic تلقائيًا؛ مثل List&lt;String&gt; تحتاج فحص elements أو type descriptor/serializer. كمان inline توسع الكود، والدالة reified لا تتعامل كـgeneric runtime function مستقلة بنفس الشكل.</p>

**Spoken answer:** “A reified inline parameter makes the direct call-site type available for checks and type-token factories. It does not reconstruct a complete nested generic graph after JVM erasure. For values such as lists or serialized models, I still need element validation or a serializer with full type metadata.”

**Common wrong answer:** Reified parameters preserve every generic argument recursively and eliminate all unchecked casts.

**Follow-up 1:** When would you pass KClass explicitly instead? When the function cannot be inline, the token is selected dynamically, or the API must store and reuse it.

**Follow-up 2:** When is a serializer better than KClass? When validation or decoding depends on fields, nullability, nested generics, or polymorphic schema.

**Rubric:** Include inline call-site specialization, direct type access, nested limits, explicit tokens, and serializer use.
