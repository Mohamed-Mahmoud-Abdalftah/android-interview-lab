---
id: PRO-001
title: Room, migrations, WAL and DataStore
module: 06-Production-Engineering
tier: Core
estimated_minutes: 120
prerequisite_ids: [ARC-003]
learning_outcomes:
  - Design a release-safe Room migration chain without destructive fallback
  - Explain transactions, WAL concurrency and checkpoint limits without promising impossible guarantees
  - Choose Room or DataStore from data shape, invariants and query needs
  - Separate a JVM migration-coverage audit from Android database migration evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/training/data-storage/room/migrating-db-versions
  - https://developer.android.com/training/data-storage/room/testing-db
  - https://developer.android.com/topic/libraries/architecture/datastore
  - https://developer.android.com/reference/androidx/room/migration/Migration
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/MigrationCoveragePlanner.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/MigrationCoveragePlannerTest.kt
question_ids: [PRO-Q006, PRO-Q007, PRO-Q008, PRO-Q009, PRO-Q010]
---

# PRO-001 — Room, migrations, WAL and DataStore

**مسار الساعتين:** 55 دقيقة شرح وتتبع، 20 دقيقة [أسئلة وإجابات كاملة](../Interview-Question-Bank/BY-TOPIC.md)، 25 دقيقة [LAB-015](../Coding-Challenges/LAB-015-migration-coverage-planner.md)، 10 دقائق [مراجعة](../Flashcards-Revision/PRO-001.md)، و10 دقائق شرح بصوتك من [Day 31](../Speaking-Shadowing/DAY-31.md).

## Mental model — البيانات على الجهاز عقد إصدار

<p dir="rtl" lang="ar">قاعدة البيانات على موبايل المستخدم مش ملف داخلي تقدر تمسحه وقت ما تحب. هي عقد طويل العمر بين نسخة التطبيق القديمة والنسخة الجديدة. المستخدم ممكن يقفز من schema version 1 لـ4 من غير ما يشغّل 2 أو3، وممكن Android يقتل الـprocess أثناء فتح القاعدة. هدف الـmigration إن كل نسخة مدعومة توصل للـtarget schema مع الحفاظ على البيانات والـinvariants، أو تفشل بوضوح قبل ما التطبيق يعرض حالة كاذبة.</p>

<p dir="rtl" lang="ar">افصل أربع مسئوليات: <strong>Room schema</strong> للبيانات المنظمة والعلاقات والاستعلامات؛ <strong>migration graph</strong> لتحويل الإصدارات؛ <strong>transaction</strong> لوحدة التغيير المنطقية؛ و<strong>DataStore</strong> لإعدادات صغيرة أو typed preferences من غير joins. اختيار storage من شكل البيانات وعقدها، مش من إن API أسهل.</p>

<table dir="rtl" lang="ar"><thead><tr><th>السؤال</th><th>Room</th><th>DataStore</th></tr></thead><tbody>
<tr><td>فيه entities وعلاقات وفلترة وترتيب وفهارس؟</td><td>مناسب</td><td>غير مناسب</td></tr>
<tr><td>قيمة صغيرة زي theme أو onboarding flag؟</td><td>ممكن لكن زيادة تعقيد</td><td>مناسب</td></tr>
<tr><td>محتاج atomic update على صفوف متعددة؟</td><td>استخدم transaction</td><td>التحديث atomic للملف، لكن من غير relational query</td></tr>
<tr><td>محتاج partial update أو query حسب column؟</td><td>مناسب مع schema/index</td><td>اقرأ واكتب object كامل؛ مش database</td></tr>
</tbody></table>

## Mechanism and execution trace — من version 1 إلى 4

<p dir="rtl" lang="ar">افترض إن version 1 فيها جدول note، وversion 2 أضافت drafts، وversion 3 أضافت server version، وversion 4 أضافت mutation ID. وقت فتح القاعدة Room تقرأ schema version المخزنة، تبحث عن migration path مسجلة، تنفذ خطواتها بالترتيب، وبعدها تتحقق من schema النهائية. لو مستخدم عنده version 1 ونشرنا 4، وجود migration من 3 إلى4 فقط لا يكفي؛ لازم graph فيها path كاملة من 1 إلى4 لكل نسخة ما زلنا ندعمها.</p>

```text
installed v1
  -> MIGRATION_1_2: create drafts
  -> MIGRATION_2_3: add server_version with a safe default/backfill
  -> MIGRATION_3_4: add mutation_id + index
  -> schema v4 opens, DAO queries start
```

<p dir="rtl" lang="ar">الـJVM lab عندنا يعمل release audit على الـgraph قبل Android integration test. <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/MigrationCoveragePlanner.kt">MigrationCoveragePlanner.kt</a> يستخدم breadth-first search عشان يلاقي أقصر path معلنة، ويرجع النسخ القديمة اللي ملهاش طريق للـtarget. هو لا ينفذ SQL ولا يقلد اختيار Room الداخلي؛ قيمته إنه يمنعك تنسى upgrade path في release matrix.</p>

```kotlin
val steps = listOf(
    SchemaStep(1, 2, "create drafts"),
    SchemaStep(2, 3, "add server version"),
    SchemaStep(3, 4, "add mutation id"),
)

check(missingMigrationStarts(4, setOf(1, 2, 3, 4), steps).isEmpty())
```

<p dir="rtl" lang="ar">تتبع التنفيذ: الـqueue تبدأ بـ1 ومسار فاضي. planner تزور 1→2، بعدها 2→3، بعدها 3→4 وترجع الثلاث خطوات. لو شلت 2→3، الزيارة تقف عند2 وترجع <code dir="ltr">null</code>. لو فيه 1→4 direct path مختبرة، BFS تختارها لأنها أقل خطوات. ده قرار الـaudit model فقط؛ Android test لازم يفتح قاعدة حقيقية من كل schema قديمة ويثبت النتيجة.</p>

## Wrong and corrected migration implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> تزود version، تستخدم destructive migration عشان crash يختفي، أو تكتب <code dir="ltr">ALTER TABLE</code> من غير ما تفكر في rows القديمة. النتيجة ممكن تكون فقد بيانات صامت، default له معنى غلط، query بطيئة، أو startup failure يظهر فقط للمستخدم اللي قفز من إصدار قديم.</p>

```kotlin
// Wrong for user-owned data: the app appears to recover by deleting it.
Room.databaseBuilder(context, AppDb::class.java, "app.db")
    .fallbackToDestructiveMigration()
    .build()
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> اكتب transformation واضحة، صدّر schemas في version control، واعمل migration test لكل starting version مدعومة. لو column الجديدة لازم تبقى non-null، حدد default مؤقت آمن أو اعمل create-copy-validate-swap لما التحويل معقد. بعد التحويل اختبر البيانات، مش شكل الجدول بس.</p>

```kotlin
// Android example; package/signature depends on the Room major version in the app.
val migration3To4 = object : Migration(3, 4) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE notes ADD COLUMN mutation_id TEXT")
        db.execSQL("CREATE UNIQUE INDEX index_notes_mutation_id ON notes(mutation_id)")
    }
}
```

<p dir="rtl" lang="ar">المثال فوق تعليمي ومش متجمع في JVM project. في مشروع Android حقيقي استخدم API المناسبة لنسخة Room الفعلية، وسجّل migration في builder، وشغّل <code dir="ltr">MigrationTestHelper</code> على exported schemas. راجع دليل <a dir="ltr" href="https://developer.android.com/training/data-storage/room/migrating-db-versions">Room migrations</a> ودليل <a dir="ltr" href="https://developer.android.com/training/data-storage/room/testing-db">migration testing</a>؛ تم فحصهم 2026-10-10.</p>

## Transactions, WAL and concurrency

<p dir="rtl" lang="ar">الـtransaction تقول إن مجموعة تغييرات database تنجح كوحدة واحدة أو تتراجع كوحدة واحدة. مثال offline-first: تعديل entity وإضافة outbox row لازم يحصلوا في transaction واحدة. لو كتبت entity وبعدها الـprocess مات قبل outbox، الـUI هتعرض تعديل ملوش sync intent. ولو كتبت outbox الأول وماتت قبل entity، worker ممكن يبعت حاجة مش ظاهرة محليًا.</p>

```kotlin
@Transaction
suspend fun saveDraft(entity: NoteEntity, mutation: OutboxEntity) {
    noteDao.upsert(entity)
    outboxDao.insert(mutation)
}
```

<p dir="rtl" lang="ar"><code dir="ltr">WAL</code> أو write-ahead logging يخلي SQLite تسجل التغييرات في log قبل دمجها في الملف الرئيسي، ويسمح غالبًا إن readers تكمل مع writer واحد. ده يحسن concurrency، لكنه مش معناه writers بلا حدود، ومش بديل transaction، ومش ضمان إن كل البيانات اتزامنت مع server. checkpoint ينقل صفحات من WAL للملف الرئيسي؛ reader طويل أو transaction ضخمة ممكن تأخر checkpoint وتكبر الملف. لذلك راقب زمن transaction وحجم writes، وما تعملش network call جوه database transaction.</p>

<p dir="rtl" lang="ar">خلي transaction قصيرة وحتمية: اقرأ/اكتب البيانات المحلية اللازمة واقفلها. الـHTTP يحصل خارجها، وبعد الرد افتح transaction جديدة تطبق النتيجة بشرط إن mutation/version ما زالت الحالية. كده ما بتحجزش database lock أثناء network latency، وبتمنع response قديمة من مسح intent أحدث.</p>

## DataStore decision and failure boundaries

<p dir="rtl" lang="ar">Preferences DataStore مناسب لمفاتيح بسيطة من غير schema typed قوية؛ Proto DataStore مناسب لما عايز object typed وله schema وتطور معروف. الاثنين يعرضوا data كـFlow والتحديث serialized/atomic على مستوى DataStore. بس لو عندك قائمة notes، search، foreign keys، partial rows أو joins، حطها في Room. تخزين JSON ضخم في preference واحدة يحول كل تعديل صغير إلى قراءة وكتابة object كامل ويخفي قواعد البيانات جوه blob.</p>

<p dir="rtl" lang="ar">تعامل مع القراءة والفشل صراحة. <code dir="ltr">IOException</code> أثناء القراءة ممكن تتحول لقيمة default حسب policy مع telemetry، لكن corruption أو programmer error ما ينفعش يتبلعوا كأن المستخدم أول مرة يفتح التطبيق. عند النقل من SharedPreferences استخدم migration الرسمية مرة واحدة واختبر إن القيمة لا تتكرر ولا تضيع. ما تعملش أكثر من DataStore instance لنفس الملف داخل process، وخلي الملكية واضحة في DI.</p>

```kotlin
// Android sketch: keep one injected owner for this file.
val Context.settingsDataStore by preferencesDataStore(name = "settings")

suspend fun setDarkMode(enabled: Boolean) {
    settingsDataStore.edit { values -> values[DARK_MODE] = enabled }
}
```

<p dir="rtl" lang="ar">راجع <a dir="ltr" href="https://developer.android.com/topic/libraries/architecture/datastore">DataStore guide</a> لاختيار Preferences أو Proto، وحدود الاستخدام، وطريقة migration. الـlesson لا تدّعي اختبار DataStore أو Room لأن البيئة الحالية JVM من غير Android SDK.</p>

## Production release workflow

<ol dir="rtl" lang="ar">
<li><strong>حدد supported starts:</strong> من telemetry وسياسة minimum supported app version، مش من الذاكرة.</li>
<li><strong>صدّر schemas:</strong> خزن JSON لكل version في repository وراجع diff في code review.</li>
<li><strong>خطط data transform:</strong> nullability، defaults، backfill، indexes، uniqueness، وحجم البيانات.</li>
<li><strong>اختبر كل path:</strong> أنشئ قاعدة من schema قديمة، حط rows لها edge cases، شغّل migrations، وافتح أحدث Room schema.</li>
<li><strong>اختبر interruption:</strong> crash/restart حوالين business transaction، وretry للoutbox، ومساحة تخزين قليلة حسب المخاطر.</li>
<li><strong>اعمل staged rollout:</strong> راقب open failures، migration duration، database size، ANR وcrash signals من غير تسجيل بيانات حساسة.</li>
<li><strong>جهز recovery:</strong> rollback binary لا يرجّع schema تلقائيًا. لازم forward-compatible plan أو hotfix migration مدروسة.</li>
</ol>

## Tests and failure cases

<p dir="rtl" lang="ar">سبعة JUnit tests بدأت بفشل compile قبل التنفيذ، وبعد إضافة planner غطت multi-step path، direct shortcut، missing edge، same version، downgrade unsupported، invalid/duplicate definitions، وكل starting versions. التعقيد <code dir="ltr">O(V + E)</code> للبحث بعد بناء adjacency، ومساحة <code dir="ltr">O(V + E)</code>. الاختبارات تثبت منطق الـrelease audit فقط.</p>

<p dir="rtl" lang="ar">الدليل الكامل في Android لازم يضيف instrumentation migration tests من schemas حقيقية، assertions على rows وindexes وconstraints، database reopen، وكل قفزة إصدار مدعومة. أضف test للـDAO transaction، concurrent reads المطلوبة، وDataStore migration/corruption policy. لا تعتبر in-memory Room كفاية لمشكلة file migration؛ افتح database file فعلية في test environment.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> بتعامل مع local storage كعقد إصدار. أحدد كل النسخ القديمة المدعومة، أوفر path للtarget، وأختبر schema والبيانات من كل start. Room للبيانات المنظمة والمعاملات، وDataStore لإعدادات صغيرة. WAL يساعد read/write concurrency لكنه ما يلغي writer serialization ولا يعوض transaction. في offline write أخزن entity وoutbox مع بعض، والnetwork خارج transaction.</p>

**English interview answer:** “I treat the on-device schema as a versioned compatibility contract. Every supported installed version needs a tested path to the release schema, with assertions on data and constraints rather than schema shape alone. I use Room for relational state and transactions, DataStore for small settings, and keep network work outside database transactions. WAL can improve reader and writer overlap, but it does not remove write contention or provide remote consistency.”

## Senior follow-ups

1. **Why is a 1→2 and 3→4 test insufficient for a v4 release?** Because users can arrive from every supported installed version; the 2→3 edge or a verified direct path may be missing.
2. **When is destructive migration acceptable?** Only for explicitly disposable/rebuildable data with a product-approved recovery path, never as a silent fix for user-owned state.
3. **Can rollback APK solve a failed migration?** Not automatically; the newer schema may be unreadable by the older binary, so release design needs forward compatibility or a new corrective migration.
4. **Why not call the API inside a Room transaction?** Network latency holds local resources unpredictably and couples remote failure to database locking; persist intent, call remotely, then conditionally apply the result.
5. **Does WAL make writes parallel?** SQLite still serializes writes; WAL mainly allows readers and a writer to overlap under appropriate conditions.

## Misconceptions and revision

<ul dir="rtl" lang="ar">
<li><strong>“Room بتعمل migration تلقائي لكل تغيير”:</strong> auto migration لها حدود، والتحويلات الدلالية محتاجة spec واختبارات.</li>
<li><strong>“فتح آخر schema يكفي”:</strong> لازم تفتح من كل version مدعومة وتفحص data.</li>
<li><strong>“WAL معناها مفيش lock”:</strong> غلط؛ write contention وlong transactions ما زالوا مهمين.</li>
<li><strong>“DataStore بديل عام لـRoom”:</strong> هي مناسبة لبيانات صغيرة، من غير relational queries.</li>
<li><strong>“الـJVM planner يثبت SQL”:</strong> هو يثبت اكتمال graph اللي أعلنتها فقط؛ SQL وRoom محتاجين Android integration evidence.</li>
</ul>

**حدود الدليل:** اتنفذ planner واختباراته على JVM. ما اتنفذش Room، SQLite file، WAL checkpoint، DataStore، Android process death، emulator/device أو migration على بيانات إنتاج.
