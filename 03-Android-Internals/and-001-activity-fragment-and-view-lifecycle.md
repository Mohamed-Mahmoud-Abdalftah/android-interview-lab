---
id: AND-001
title: Activity, Fragment and view lifecycle
module: 03-Android-Internals
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-002]
learning_outcomes:
  - Trace Activity visible and foreground states through common callbacks without inventing a universal sequence
  - Distinguish Fragment lifetime from its view lifetime and choose the matching owner
  - Explain why onDestroy is not a persistence guarantee after process death
  - Identify what a pure JVM view-owner model proves and what requires an Android test
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/guide/components/activities/activity-lifecycle
  - https://developer.android.com/guide/fragments/lifecycle
  - https://developer.android.com/guide/components/activities/process-lifecycle
  - https://developer.android.com/topic/libraries/architecture/saving-states
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/ViewSession.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/ViewSessionTest.kt
question_ids: [AND-Q001, AND-Q002, AND-Q003, AND-Q004, AND-Q005]
---

# AND-001 — Activity, Fragment and view lifecycle

**Starting point:** [KOT-002](../01-Kotlin-JVM-ART/kot-002-val-var-types-equality-and-identity.md) introduced references and mutable ownership. A Fragment object can remain while its view is destroyed; retaining a reference to that view is an ownership error. Day 2 is the conceptual prerequisite, even though this is scheduled on Day 13.

**Two-hour route:** 55 minutes lifecycle trace, 20 minutes [questions with complete answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes [LAB-007](../Coding-Challenges/LAB-007-view-session-owner.md), 10 minutes [revision](../Flashcards-Revision/AND-001.md), optional 10 minutes [English](../Speaking-Shadowing/DAY-13.md). No timed assessment is required.

## Mental model

<p dir="rtl" lang="ar">الـ Activity والـ Fragment والـ Fragment view مش نفس العمر. Activity عندها callbacks زي <code dir="ltr">onCreate/onStart/onResume/onPause/onStop/onDestroy</code>، لكن لازم تربط كل resource باللحظة اللي محتاجه فيها. Fragment ممكن تفضل موجودة بينما view بتاعتها اتدمرت، فـ observer أو binding خاصة بالـ view لازم تتبع <code dir="ltr">viewLifecycleOwner</code> وتتخلص من مراجع view عند <code dir="ltr">onDestroyView</code>. ما تتعاملش مع <code dir="ltr">onDestroy</code> كأنه callback مضمون عند قتل process. <a dir="ltr" href="https://developer.android.com/guide/components/activities/activity-lifecycle">Activity lifecycle</a>، <a dir="ltr" href="https://developer.android.com/guide/fragments/lifecycle">Fragment lifecycle</a>، اتراجعوا 2026-10-10.</p>

<ul dir="rtl" lang="ar">
<li><code dir="ltr">onStart</code> يرتبط عادةً بظهور Activity، و<code dir="ltr">onResume</code> بتفاعلها في المقدمة؛ multi-window والحالات الخاصة تمنع اختزال كل حدث في تسلسل واحد.</li>
<li><code dir="ltr">onStop</code> عند عدم ظهور Activity؛ التنظيف أو حفظ مناسب قد يبدأ هنا بحسب نوع resource، لكن durable data تحتاج مسار تخزين مستقل.</li>
<li><code dir="ltr">onDestroyView</code> نهاية عمر View الخاصة بـ Fragment، وقد تأتي قبل نهاية Fragment نفسها.</li>
<li><code dir="ltr">ViewModel</code> قد تستمر عبر configuration change، لكنها ليست بديل تخزين دائم بعد process death. Saved state صغيرة كنسخة احتياطية، والبيانات الدائمة في data layer.</li>
</ul>

## Mechanism and execution trace

<p dir="rtl" lang="ar">السيناريو: Fragment تعرض profile. نربط render callback بالـ view بعد إنشائها، ونجمع UI state بمالك view، ثم نفصل binding/observer عند تدمير view. لو view جديدة اتعملت لنفس Fragment instance، نربط renderer جديدة. الـ JVM <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/ViewSession.kt">ViewSession</a> تمثل قرار attach/detach بشكل مبسط؛ لا تدعي إنها <code dir="ltr">LifecycleOwner</code> أو إنها تشغّل callbacks Android. <a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/ViewSessionTest.kt">اختباراتها</a> تثبت فقط إن المرجع يتوقف عن استقبال قيم بعد detach وإن view جديدة تقدر تستقبله.</p>

```kotlin
val session = ViewSession()
session.attach { value -> renderInCurrentView(value) }
session.show("A")       // delivered to current renderer
session.detach()        // analogous to clearing view references
session.show("late")    // false: no renderer receives it
```

<table dir="rtl" lang="ar">
<thead><tr><th>حدث</th><th>مالك الـ view</th><th>قرار الـ render</th></tr></thead>
<tbody>
<tr><td>إنشاء view الأولى</td><td><code dir="ltr">viewLifecycleOwner</code> الأولى.</td><td>اربط observer/binding الخاصة بها.</td></tr>
<tr><td>تدمير view</td><td>الـ owner الأولى تصل DESTROYED.</td><td>أوقف جمع UI وأزل مراجع view في <code dir="ltr">onDestroyView</code>.</td></tr>
<tr><td>وصول result متأخر</td><td>لا توجد view أولى صالحة.</td><td>لا تعرض عليها؛ state مملوكة لصاحب أطول إذا كانت ما زالت مفيدة.</td></tr>
<tr><td>إنشاء view ثانية</td><td><code dir="ltr">viewLifecycleOwner</code> جديدة.</td><td>اربط renderer جديدة وأعد عرض state المناسبة.</td></tr>
</tbody>
</table>

<p dir="rtl" lang="ar">Android Fragment docs توضح إن view lifecycle تتحول إلى DESTROYED قبل نداء <code dir="ltr">onDestroyView</code>، وبعده لازم تزيل مراجع view. الـ Fragment lifecycle نفسها مختلفة. ده سبب استخدام <code dir="ltr">viewLifecycleOwner</code> لمراقبة بيانات بتحدث view بدل <code dir="ltr">this</code> لو Fragment ممكن تحتفظ بعمر أطول. لا تفترض إن configuration change وprocess death نفس مسار الاستعادة؛ راجع <a dir="ltr" href="https://developer.android.com/topic/libraries/architecture/saving-states">saved UI state guidance</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> تسجل observer مربوط بعمر Fragment ويحتفظ بـ binding الخاصة بـ view. عند إزالة view، callback متأخرة تحاول الوصول إلى binding قديمة أو تمنع جمعها. وغلط تاني إنك تحفظ data مهمة فقط في <code dir="ltr">onDestroy</code> اعتمادًا على إن النظام سيناديها عند قتل process.</p>

```kotlin
// Conceptual Android sketch, not compiled by the JVM lab:
liveData.observe(this) { binding.title.text = it } // wrong owner for a view callback
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> عند وجود view استخدم <code dir="ltr">viewLifecycleOwner</code> لملاحظة ما يخصها، وأزل binding في <code dir="ltr">onDestroyView</code>. لـ Flow UI استخدم collection lifecycle-aware في نطاق view بدل إطلاق job غير مقيدة؛ تفاصيل <code dir="ltr">repeatOnLifecycle</code> ومتى يبدأ/يتوقف في وحدة لاحقة. احتفظ بـ UI state في owner مناسب واستعد البيانات بعد التكوين أو process death من saved state/data layer حسب نوعها. <a dir="ltr" href="https://developer.android.com/guide/fragments/lifecycle">Fragment docs</a>.</p>

## Boundaries and alternatives

<p dir="rtl" lang="ar">مش كل observer لها نفس owner. عمل متعلق بـ Fragment نفسها قد يتبع عمر Fragment، أما عمل يلمس view فيتبع view owner. Activity resource مثل camera أو location قد يبدأ/يتوقف عند STARTED أو RESUMED حسب حاجة المنتج ودعم multi-window؛ لا تحفظ قاعدة عامة من غير فحص API. <code dir="ltr">onPause</code> قصير، و<code dir="ltr">onStop</code> يعبر عن عدم الظهور؛ اختيار مكان cleanup له trade-offs موثقة في <a dir="ltr" href="https://developer.android.com/guide/components/activities/activity-lifecycle">Activity lifecycle guide</a>.</p>

<p dir="rtl" lang="ar">عند configuration change يمكن إنشاء Activity جديدة، وقد تحتفظ ViewModel بـ UI data في الذاكرة، لكن عند system process death قد لا تستقبل <code dir="ltr">onDestroy</code> أصلًا. استخدم saved state للقدر الصغير اللازم لإعادة بناء الشاشة وpersistent storage للبيانات الحقيقية. <a dir="ltr" href="https://developer.android.com/guide/components/activities/process-lifecycle">Process lifecycle guidance</a>. لا تعتبر JVM model بديل اختبار تدوير الشاشة أو back stack.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">أربعة اختبارات JVM تحقق: لا render قبل attach؛ render للـ view الحالية؛ لا render بعد detach؛ view جديدة تستقبل بعد فصل القديمة. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> داخل المعمل وراجع <a dir="ltr" href="../BUILD-VERIFICATION.md">دليل البناء</a>. هذه اختبارات ownership محلية، وليست Android instrumentation أو FragmentScenario أو تسريب ذاكرة مُقاس.</p>

<p dir="rtl" lang="ar">قبل release حقيقي: اختبر تبديل الوجهة في back stack، rotation، دخول multi-window، background/foreground، process recreation، late async result، وbinding cleanup. سجل callbacks فعلية وراجع stack trace، بدل توقع sequence من الذاكرة. Android SDK وemulator غير متوفرين في هذا workspace حتى الآن، فهذه الحالات غير منفذة.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> بفصل عمر Fragment عن عمر view بتاعتها. أي observer بتعدل view أربطها بـ <code dir="ltr">viewLifecycleOwner</code> وأنضف binding في <code dir="ltr">onDestroyView</code>. Activity callbacks تساعدني أوقف resources حسب الظهور والتفاعل، لكن مش كل event له نفس الترتيب في كل ظرف. process death ممكن يحصل من غير <code dir="ltr">onDestroy</code>، فبحفظ state الصغيرة المناسبة وبجيب بيانات التطبيق من مصدر دائم.</p>

**English, about 20 seconds:** “A Fragment can outlive its view. I bind view updates to the view lifecycle owner and clear view references when the view is destroyed. I never rely on onDestroy as a process-death persistence hook.”

**English, about 60–90 seconds:** “Activity callbacks describe visibility and interaction transitions, but I choose resource ownership based on the actual requirement rather than memorizing one universal callback sequence. A Fragment has its own lifecycle and a separate view lifecycle. A view observer tied to the Fragment can outlive a destroyed view, so I use the viewLifecycleOwner and clear bindings at onDestroyView. For configuration changes, a ViewModel can retain in-memory state; for system process death, saved state and durable data sources are different recovery tools. Our JVM lab verifies that a renderer is detached and a new one can attach. It does not execute Android callbacks, so I would still use an Android lifecycle test and device trace before claiming integration safety.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل <code dir="ltr">onDestroy</code> مضمونة عند قتل process؟</strong> لأ، فلا تعتمد عليها لحفظ data أساسية. <a dir="ltr" href="https://developer.android.com/guide/components/activities/process-lifecycle">المصدر</a>.</li>
<li><strong>هل Fragment نفسها انتهت عند <code dir="ltr">onDestroyView</code>؟</strong> مش بالضرورة؛ view انتهت ويمكن Fragment تفضل موجودة وتعمل view جديدة.</li>
<li><strong>هل ViewModel بديل database؟</strong> لأ؛ تحتفظ بحالة خلال بعض تغييرات التكوين، لكن persistent app data تحتاج تخزين مناسب.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“Fragment وview نفس العمر.” غلط؛ view lifecycle مستقلة.</li>
<li>“Observer بتعدل view ينفع دائمًا تربطها بـ Fragment.” غلط لو Fragment تعيش بعد view.</li>
<li>“<code dir="ltr">onDestroy</code> آخر فرصة مضمونة لحفظ البيانات.” غلط عند process kill.</li>
<li>“Pure JVM detach test يثبت Android lifecycle.” غلط؛ يثبت قرار ملكية مبسط فقط.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات سريعة:</strong> بعد detach <code dir="ltr">show()</code> ترجع false. View جديدة تحتاج owner جديدة. Process kill قد لا ينادي <code dir="ltr">onDestroy</code>. راجع <a dir="ltr" href="../Flashcards-Revision/AND-001.md">البطاقات</a> و<a dir="ltr" href="../Real-World-Scenarios/SCN-007-fragment-view-leak.md">السيناريو</a>.</p>

**Evidence limit:** Platform behavior is sourced to official Android documentation checked 2026-10-10. Only a pure JVM renderer-ownership model was compiled/tested; no Android SDK, emulator, FragmentScenario, lifecycle trace or leak analysis was executed.
