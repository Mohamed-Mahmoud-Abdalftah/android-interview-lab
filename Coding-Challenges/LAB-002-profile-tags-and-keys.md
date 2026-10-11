---
id: LAB-002
lesson_id: KOT-002
status: reviewed
code_verification: tested
---
# LAB-002 — افصل الـ mutable state عن الـ Java boundary

<p dir="rtl" lang="ar"><strong>المهمة:</strong> عندك Java SDK بترجع <code dir="ltr">List&lt;String&gt;</code> قابلة للتعديل، وممكن ترجع <code dir="ltr">null</code> أو عناصر <code dir="ltr">null</code> رغم إن التوقيع مش موضّح فيه ده. ابنِ snapshot نظيفة للـ tags، وافصل نسختين من draft عن بعض، واستخدم key ثابتة للـ cache.</p>

<p dir="rtl" lang="ar"><strong>المطلوب:</strong></p>

1. <span dir="rtl" lang="ar"><code dir="ltr">snapshotLegacyTags(raw: List&lt;String?&gt;?): List&lt;String&gt;</code> ترجع قائمة فاضية لو المصدر null؛ تشيل الـ null والـ blank بعد <code dir="ltr">trim()</code>؛ وتحافظ على ترتيب القيم الباقية. النتيجة لازم تكون منفصلة عن قائمة Java الأصلية، بحيث تعديل المصدر بعد الاستدعاء ما يغيّرش الـ snapshot.</span>
2. <span dir="rtl" lang="ar"><code dir="ltr">safeTagsFromLegacy(id)</code> تحوّل نتيجة <code dir="ltr">LegacyProfileApi.tagsFor(id)</code> إلى نوع nullable صريح عند الـ boundary وتستخدم الدالة السابقة.</span>
3. <span dir="rtl" lang="ar"><code dir="ltr">ProfileDraft.detachedCopy()</code> ترجع draft جديدة بقائمة tags جديدة. جرّب كمان <code dir="ltr">copy()</code> العادية وشوف ليه تعديل قائمة النسخة بيظهر في الأصل.</span>
4. <span dir="rtl" lang="ar">خلي <code dir="ltr">ProfileKey(tenantId, profileId)</code> مفتاح cache ثابت بخصائص <code dir="ltr">val</code>. نسختان بنفس القيم لازم يكونوا متساويين بـ <code dir="ltr">==</code> وليهم نفس <code dir="ltr">hashCode()</code>، حتى لو <code dir="ltr">===</code> نتيجتها false.</span>

<p dir="rtl" lang="ar"><strong>ابدأ من:</strong> <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/java/academy/LegacyProfileApi.java">Java SDK fake</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ProfileSemanticsTest.kt">JUnit tests</a>. جرّب الحل بنفسك قبل فتح <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ProfileSemantics.kt">reference implementation</a>. اللاب Kotlin/JVM على JDK 17؛ مفيهوش Android SDK ولا network service.</p>

<p dir="rtl" lang="ar"><strong>حالات لازم تتوقعها:</strong> <code dir="ltr">tagsFor("missing")</code> بترجع null؛ <code dir="ltr">tagsFor("mona")</code> بترجع قائمة mutable فيها قيم صالحة وnull وblank؛ تعديل قائمة Java بعد ما تاخد snapshot ما يغيّرش الناتج؛ وتعديل tags في نسخة <code dir="ltr">detachedCopy()</code> ما يغيّرش الأصل والعكس. <code dir="ltr">val</code> بتمنع إعادة ربط المرجع، لكنها ما بتجمّدش الـ mutable list. <code dir="ltr">var</code> ممكن تربط متغير محلي بكائن تاني من غير ما تغيّر الكائن الأول.</p>

<p dir="rtl" lang="ar"><strong>فخ الـ cache:</strong> ما تستخدمش draft فيها قيم بتتغير كمفتاح <code dir="ltr">Map</code>. لو المفتاح اتغير بطريقة بتأثر على <code dir="ltr">equals()</code> وهو جوه الـ map، سلوك الـ map غير محدد في <a dir="ltr" href="https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html">عقد Java Map</a>. اختبر نجاح lookup بمفتاح <code dir="ltr">ProfileKey</code> ثابت بدل افتراض إن lookup بالمفتاح المتغيّر لازم يفشل بطريقة معينة. وكمان <code dir="ltr">List</code> في Kotlin واجهة قراءة فقط، مش ضمان لعدم التغيير العميق أو لمنع Java من التعديل لو عندها reference لنفس القائمة.</p>

<p dir="rtl" lang="ar"><strong>التعقيد:</strong> عمل snapshot أو نسخ قائمة tags بطول <code dir="ltr">n</code> بياخد <code dir="ltr">O(n)</code> عناصر إضافية؛ الـ trim نفسه بيقرأ أحرف كل tag، فزمن التنظيف الكلي <code dir="ltr">O(n + total tag characters)</code>. النسخة هنا بتفصل القائمة فقط؛ العناصر Strings غير قابلة للتعديل. لو عناصرها كائنات mutable، هتحتاج تحدد سياسة نسخ أعمق حسب الـ domain.</p>

<p dir="rtl" lang="ar"><strong>التحقق:</strong> من <code dir="ltr">projects/kotlin-jvm-labs/</code> شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> وافحص تقرير JUnit XML في <code dir="ltr">build/test-results/test/</code>. تقييم ذاتي اختياري: 3 نقاط لتنظيف مدخل Java، 2 لفصل الـ alias، 2 لمفتاح cache ثابت، 2 لاختبارات edge cases، و1 لشرح الفرق بين <code dir="ltr">==</code> و<code dir="ltr">===</code>. مفيش امتحان إجباري أو وقت محدد في Learning Mode.</p>
