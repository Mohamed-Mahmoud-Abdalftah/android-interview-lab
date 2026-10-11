---
id: ARC-001
title: SOLID and useful patterns
module: 04-Architecture-DI
tier: Core
estimated_minutes: 55
prerequisite_ids: [KOT-003]
learning_outcomes:
  - Explain responsibility boundaries through an Android data-flow example
  - Apply a narrow write port and substitute a fake without changing product logic
  - Identify when abstraction, inheritance or patterns add cost without a real requirement
  - Trace validation, delegation and failure behavior in a pure JVM use case
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/topic/architecture/recommendations
  - https://developer.android.com/topic/architecture/data-layer
  - https://developer.android.com/topic/architecture/domain-layer
  - https://kotlinlang.org/docs/fun-interfaces.html
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/SaveNote.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/SaveNoteTest.kt
question_ids: [ARC-Q001, ARC-Q002, ARC-Q003, ARC-Q004, ARC-Q005]
---

# ARC-001 — SOLID and useful patterns

**Starting point:** [KOT-003](../01-Kotlin-JVM-ART/kot-003-classes-constructors-initialization-order.md) covered class construction, visibility and invariants. Here the question is where behavior belongs and how dependencies flow. This is one architecture unit, not a claim that Hilt, full MVVM, offline-first storage or all SOLID principles have been exercised on Android.

**Two-hour route:** 55 minutes reading/trace, 20 minutes [five questions with answers](../Interview-Question-Bank/BY-TOPIC.md), 25 minutes [LAB-006](../Coding-Challenges/LAB-006-save-note-port.md), 10 minutes [revision](../Flashcards-Revision/ARC-001.md), optional 10 minutes [English](../Speaking-Shadowing/DAY-19.md). Learning Mode keeps answers visible.

## Mental model

<p dir="rtl" lang="ar">بدل ما screen تنادي database مباشرة وتعمل validation وتقرر شكل UI في function واحدة، افصل مسؤولية عرض الحالة عن قاعدة المنتج وعن التخزين. مبادئ SOLID أدوات لتحديد حدود التغيير، مش قانون يقول لازم interface لكل class. اسأل: أي سبب يخلي الجزء ده يتغير؟ مين يملك contract؟ هل abstraction بتسمح باستبدال حقيقي واختبار واضح؟ توجيه Android الرسمي يوصي بـ UI/data layers، repository كواجهة للبيانات، وdomain layer عند تعقيد أو إعادة استخدام منطق الأعمال؛ ده توصية قابلة للتكييف حسب التطبيق. <a dir="ltr" href="https://developer.android.com/topic/architecture/recommendations">Android architecture recommendations</a>، اتراجعت 2026-10-10.</p>

<ul dir="rtl" lang="ar">
<li><strong>Single Responsibility:</strong> <code dir="ltr">SaveNote</code> يطبق قاعدة إدخال note ويطلب تخزينها؛ تفاصيل Room/HTTP ليست فيه.</li>
<li><strong>Open/Closed:</strong> تقدر تبدّل adapter التخزين من غير تعديل قاعدة المنتج، لو contract ثابتة ومناسبة فعلًا.</li>
<li><strong>Liskov substitution:</strong> أي implementation لـ <code dir="ltr">NoteWriter</code> لازم تحترم معنى <code dir="ltr">upsert</code> أو توثق فشلها؛ مجرد تنفيذ interface لا يضمن السلوك.</li>
<li><strong>Interface Segregation:</strong> use case الكتابة تحتاج <code dir="ltr">upsert</code> فقط، مش interface ضخمة فيها read, delete, sync بلا حاجة.</li>
<li><strong>Dependency Inversion:</strong> الـ use case تعتمد على contract صغيرة مملوكة لاحتياجها؛ adapter قاعدة البيانات تنفذها. ده غير مجرد استخدام DI framework.</li>
</ul>

## Mechanism and execution trace

<p dir="rtl" lang="ar">المثال قابل للتشغيل في JVM: <code dir="ltr">NoteWriter</code> port صغيرة؛ <code dir="ltr">SaveNote</code> تستقبلها في constructor. عند invocation تنظف ID والعنوان بـ <code dir="ltr">trim</code>، ترفض الفراغ، ثم تبني <code dir="ltr">Note</code> واحدة وتنادي <code dir="ltr">upsert</code> مرة. <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/SaveNote.kt">التنفيذ</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/SaveNoteTest.kt">JUnit tests</a> يثبتوا contract المحددة فقط. <a dir="ltr" href="https://kotlinlang.org/docs/fun-interfaces.html">Kotlin functional interfaces</a>.</p>

```kotlin
fun interface NoteWriter {
    fun upsert(note: Note)
}
class SaveNote(private val writer: NoteWriter) {
    operator fun invoke(rawId: String, rawTitle: String): Note {
        val id = rawId.trim()
        val title = rawTitle.trim()
        require(id.isNotEmpty())
        require(title.isNotEmpty())
        return Note(id, title).also(writer::upsert)
    }
}
```

<table dir="rtl" lang="ar">
<thead><tr><th>Input</th><th>قرار use case</th><th>أثر على writer</th></tr></thead>
<tbody>
<tr><td dir="ltr"><code dir="ltr">(" n-1 ", " Prep ")</code></td><td>تنتج <code dir="ltr">Note("n-1", "Prep")</code>.</td><td>استدعاء <code dir="ltr">upsert</code> مرة ثم رجوع القيمة.</td></tr>
<tr><td dir="ltr"><code dir="ltr">(" ", "Prep")</code></td><td>ترمي <code dir="ltr">IllegalArgumentException</code> قبل التخزين.</td><td>صفر استدعاءات.</td></tr>
<tr><td dir="ltr">writer تفشل</td><td>الخطأ يمر للـ caller؛ لا تدعي نجاحًا وهميًا.</td><td>محاولة واحدة؛ مصير التخزين الفعلي حسب adapter.</td></tr>
</tbody>
</table>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> ViewModel أو Activity تتحقق من title، تنادي SQL مباشرة، وتعمل retry لكل فشل تحت <code dir="ltr">catch (Exception)</code> ثم تعرض success. كده قواعد المنتج مربوطة بالواجهة والتخزين، والفشل اتخبّى. وغلط آخر إننا ننشئ interfaces لكل سطر من غير سبب تغيير أو استبدال متوقع.</p>

```kotlin
// Conceptual anti-pattern; no Android SDK/database is present in this lab.
fun onSave(title: String) {
    try { database.execSQL("...") } catch (_: Exception) { showSuccess() }
}
```

<p dir="rtl" lang="ar"><strong>التصحيح القابل للاختبار:</strong> screen ترسل intent/حدث، والـ use case تطبق validation وتفوض لـ port؛ adapter تخزين حقيقية تتعامل مع transaction/error policy. لا تجعل <code dir="ltr">NoteWriter</code> مجرد اسم جديد لنفس قاعدة البيانات إن ما فيش boundary مفيدة. في مشروع صغير، توجيه Android يسمح بدمج repository/data source حين لا تضيف طبقة منفصلة قيمة؛ الدليل هنا يشرح port عند وجود قاعدة يمكن اختبارها بمعزل عن التخزين. <a dir="ltr" href="https://developer.android.com/topic/architecture/data-layer">Android data layer</a>.</p>

## Alternatives and trade-offs

<p dir="rtl" lang="ar">لو المنطق بسيط وبيُستخدم في مكان واحد، ممكن ViewModel تنادي repository مباشرة من غير use case class. لو قاعدة validation مشتركة أو workflow معقدة، domain use case أوضح. <code dir="ltr">NoteWriter</code> بتعبر عن عملية كتابة واحدة؛ لو التطبيق يحتاج قراءة stream منفصل، واجهة قراءة مستقلة قد تكون أنسب. لكن كثرة الواجهات تزود ملفات ومسارات تنقل، فبررها بسلوك فعلي أو احتمال تغيير معقول. <a dir="ltr" href="https://developer.android.com/topic/architecture/domain-layer">Android domain layer</a>.</p>

<p dir="rtl" lang="ar">ما تبنيش inheritance hierarchy لمجرد إعادة استخدام سطرين. composition هنا يوضح dependency، وKotlin <code dir="ltr">fun interface</code> تسمح fake أو adapter صغير. تعريف interface لا يضمن LSP: adapter ترمي خطأ بعد ما تكون خزّنت نصف البيانات مثلًا تخالف توقع atomic upsert حتى لو compiler راضي. عشان كده اختبارات contract عبر implementations مهمة لما تضيف قاعدة بيانات حقيقية.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">أربع اختبارات JUnit تغطي normalization واستدعاء واحد، ID فارغ، title فارغ، وفشل writer. الاختبارات تستخدم fake في الذاكرة، فتثبت أن use case لا تحتاج Android أو Room لبناء القرار، لكنها لا تثبت transaction، persist بعد process death، thread safety، أو repository source-of-truth. شغّل <code dir="ltr">./gradlew clean test check run --no-daemon</code> من مشروع JVM وراجع <a dir="ltr" href="../BUILD-VERIFICATION.md">دليل البناء</a>.</p>

<p dir="rtl" lang="ar">قرار <code dir="ltr">require</code> يعني input invalid خطأ programming/contract في المعمل. لو المستخدم يكتب عنوان فاضي كحالة عادية، production UI يجب أن تحولها إلى validation result مفهوم بدل crash. ولأن <code dir="ltr">upsert</code> هنا sync port، أي I/O حقيقي يحتاج تصميم main-safety وsuspend boundary مستقل، مستفيد من <a dir="ltr" href="../02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md">COR-001</a>.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> ببدأ بسبب التغيير: الشاشة تعرض وتستقبل حدث، use case تطبق قاعدة حفظ note، والـ adapter تعرف طريقة التخزين. حقنت <code dir="ltr">NoteWriter</code> صغيرة بدل database class، فاختبرت إن ID/title بيتنضفوا وإن input الغلط ما يوصلش للتخزين. ده يوضح SRP وDIP وISP بشكل عملي، بس مش دليل إن كل مشروع يحتاج نفس عدد الطبقات.</p>

**English, about 20 seconds:** “I separate the product rule from storage mechanics. SaveNote validates and normalizes a note, then calls a narrow NoteWriter port. A fake lets me test the rule without a database, while the real adapter owns persistence.”

**English, about 60–90 seconds:** “I use SOLID as a way to reason about change boundaries, not as a class-count target. In the JVM example, the save use case owns normalization and input validity, while a narrow writer contract hides storage details. An invalid ID or title fails before the writer is called, and a writer failure reaches the caller. That supports isolated tests and substitution, but it does not prove that a Room adapter is transactional or that the UI handles expected validation errors gracefully. For a small feature I may call a repository directly from the ViewModel; I add a domain use case when logic is reused or complex. I would verify the contract against a real persistence adapter before claiming offline durability.”

## Senior follow-ups

<ol dir="rtl" lang="ar">
<li><strong>هل حقن interface يعني تصميم جيد تلقائيًا؟</strong> لأ. لازم contract ضيقة وواضحة، وعندك سبب تغيير أو اختبار. abstraction غير مستخدمة تكلفة.</li>
<li><strong>لو writer تخزن ثم ترمي exception، هل use case تقدر تقول العملية فشلت بالكامل؟</strong> لأ؛ دي semantics adapter وtransaction. لازم contract وتكامل يحددا النتيجة.</li>
<li><strong>ليه ما بنستخدمش Hilt هنا؟</strong> constructor injection كافية للمعمل؛ Hilt wiring له قيمة عند graph Android أكبر، لكنه لا يصلح حدود مسؤولية سيئة.</li>
</ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li>“SOLID يعني interface لكل class.” غلط؛ ابدأ بسبب التغيير والcontract.</li>
<li>“Repository لازم تكون طبقة منفصلة عن data source حتى لو مصدر واحد.” توجيه Android يجيز الدمج في حالات صغيرة.</li>
<li>“Unit fake يثبت persist بعد process death.” غلط؛ ده اختبار adapter/تكامل.</li>
<li>“تنفيذ interface يضمن LSP.” غلط؛ السلوك والآثار والفشل جزء من العقد.</li>
</ul>

<p dir="rtl" lang="ar"><strong>إجابات سريعة:</strong> عنوان فارغ: writer صفر استدعاءات. writer فشلت: الاستثناء يظهر. هل ننشئ use case لكل getter؟ لأ، بعد تقييم التعقيد وإعادة الاستخدام. راجع <a dir="ltr" href="../Flashcards-Revision/ARC-001.md">البطاقات</a> و<a dir="ltr" href="../Real-World-Scenarios/SCN-006-note-save-success-lie.md">سيناريو النجاح الوهمي</a>.</p>

**Evidence limit:** Kotlin/JVM tests verify the narrow port and validation paths. Android architectural recommendations were read on 2026-10-10; no Android UI, Room, DI graph, database durability or process-death behavior was built or tested.
