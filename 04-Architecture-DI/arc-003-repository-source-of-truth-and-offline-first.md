---
id: ARC-003
title: Repository, source of truth and offline-first
module: 04-Architecture-DI
tier: Core
estimated_minutes: 60
prerequisite_ids: [ARC-002]
learning_outcomes:
  - Define repository ownership and a single readable source of truth
  - Trace a local-first write through an outbox-style pending mutation and sync
  - Distinguish transport failure from version conflict without losing the local draft
  - Bound an in-memory JVM model against Room, WorkManager and process-death requirements
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://developer.android.com/topic/architecture/data-layer
  - https://developer.android.com/topic/architecture/data-layer/offline-first
  - https://developer.android.com/topic/architecture/recommendations
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/OfflineNotesRepository.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/OfflineNotesRepositoryTest.kt
question_ids: [ARC-Q011, ARC-Q012, ARC-Q013, ARC-Q014, ARC-Q015]
---

# ARC-003 — Repository, source of truth and offline-first

ابدأ من [ARC-002](arc-002-mvvm-udf-state-and-events.md): الـ ViewModel تملك screen state، لكن محتاجة data contract واحدة بدل ما تتعامل مع database وnetwork مباشرة. **مسار الساعتين:** 60 دقيقة هنا، 20 دقيقة [أسئلة وإجابات](../Interview-Question-Bank/BY-TOPIC.md)، 25 دقيقة [LAB-014](../Coding-Challenges/LAB-014-offline-note-repository.md)، 10 دقائق [revision](../Flashcards-Revision/ARC-003.md)، و5 دقائق [speaking](../Speaking-Shadowing/DAY-21.md).

## Mental model — مصدر قراءة واحد وسياسة مزامنة واضحة

<p dir="rtl" lang="ar">Repository مش مجرد class تغير اسم Retrofit أو DAO. دورها تعرض data لباقي التطبيق، تجمع مصادرها، وتحدد مين source of truth وإزاي التعارض يتحل. في offline-first غالبًا الـ local database هي المصدر الذي تقرأ منه UI دائمًا. الـ network تجيب تحديثات أو تستقبل writes، والrepository تكتب نتيجتها محليًا؛ الشاشة ما تجمعش local list وnetwork list بنفسها.</p>

<p dir="rtl" lang="ar">“Single source of truth” لا تعني إن فيه نسخة واحدة في الكون؛ تعني إن لكل نوع data فيه authority واضحة للقراءة داخل boundary. ممكن server تكون authority النهائية للتعارض، بينما local database هي canonical stream التي يقرأها التطبيق. الفرق مهم: UI ترى local فورًا، وsync تعدل local بعد قبول server. Android data-layer guide تضع repositories كبوابة للبيانات وتكلفها بحل conflicts، وoffline-first guide توصي إن local source تكون مصدر القراءة للتطبيق. راجع <a dir="ltr" href="https://developer.android.com/topic/architecture/data-layer">data layer</a> و<a dir="ltr" href="https://developer.android.com/topic/architecture/data-layer/offline-first">offline-first guide</a>، اتراجعوا 2026-10-10.</p>

<table dir="rtl" lang="ar"><thead><tr><th>مسؤولية</th><th>مين يملكها</th><th>ليه</th></tr></thead><tbody>
<tr><td>عرض notes للشاشة</td><td>Local source عبر repository</td><td>نفس السلوك online/offline وتحديث observable واحد.</td></tr>
<tr><td>Network DTO/HTTP</td><td>Remote data source</td><td>تفاصيل transport لا تتسرب للـ UI.</td></tr>
<tr><td>Queue ومتى نعمل sync</td><td>Repository + persistent worker</td><td>سياسة data متعددة المصادر.</td></tr>
<tr><td>قرار conflict النهائي</td><td>Product/server contract</td><td>last-write-wins ليست صحيحة لكل domain.</td></tr>
<tr><td>Screen loading/error</td><td>ViewModel/UI state</td><td>presentation فوق data state.</td></tr>
</tbody></table>

## Mechanism and execution trace

<p dir="rtl" lang="ar">المعمل يبني نموذج صغير في الذاكرة. <code dir="ltr">saveLocal</code> تنظف input وتكتب <code dir="ltr">LocalNote</code> بحالة Pending وmutation ID جديدة، فتظهر فورًا من <code dir="ltr">get/all</code>. لما <code dir="ltr">sync</code> تشتغل، تبعت نفس mutation ID والعنوان وbase server version. لو النقل فشل، الاستثناء يظهر والrecord تفضل Pending بنفس الهوية. retry تستخدم نفس الهوية، وده أساس idempotency end-to-end.</p>

```text
Server v3: "Old"
        |
seed local CLEAN v3
        |
saveLocal "My edit" + mutation m4
        v
local PENDING(title="My edit", baseVersion=3, mutation=m4)
        |
remote says current server is v4 "Remote edit"
        v
local CONFLICT(local draft preserved, remote evidence attached)
```

<p dir="rtl" lang="ar">لو server تقبل، ترجع canonical record/version؛ repository تستبدل local record بنسخة Clean وتمسح pending ID. لو ترجع Conflict، ما تمسحش draft المحلية وما تدّعيش نجاح؛ تخزن remote snapshot بجانبها عشان policy أو المستخدم يقرر merge. لو network ترمي exception، ما تحولهاش conflict؛ transport failure لا تقول إن server رفضت.</p>

<p dir="rtl" lang="ar">التعديل المحلي الثاني قبل sync يحصل على mutation ID جديدة لكنه يحتفظ بـbase server version نفسها. ده معناه إن payload الجديدة supersede القديمة محليًا في النموذج. production queue لازم تعمل ده atomically: note/outbox تتحدثا في transaction واحدة، وإلا crash بينهم يعمل note ظاهرة من غير operation أو operation بpayload قديمة. اقرأ <a dir="ltr" href="../projects/kotlin-jvm-labs/src/main/kotlin/academy/OfflineNotesRepository.kt">التنفيذ</a> و<a dir="ltr" href="../projects/kotlin-jvm-labs/src/test/kotlin/academy/OfflineNotesRepositoryTest.kt">الاختبارات</a>.</p>

## Wrong and corrected implementation

<p dir="rtl" lang="ar"><strong>غلط:</strong> ViewModel تعمل network request، تعرض response مباشرة، وبعدها تحاول تحدث database. offline الشاشة فاضية، والـ network والdatabase ممكن يختلفوا. وغلط تاني إن sync تعمل catch لكل exception وتمسح pending عشان “ما تكررش”، فتفقد تعديل المستخدم.</p>

```kotlin
suspend fun save(title: String) {
    val remote = api.save(title)
    uiState.value = remote       // second source rendered directly
    dao.insert(remote)            // crash here leaves UI/data disagreement
}
```

<p dir="rtl" lang="ar"><strong>التصحيح:</strong> UI تراقب local stream فقط. write strategy تتحدد حسب المنتج: online-only للعملية التي لا يجوز قبولها محليًا، queued/lazy write للتعديل الضروري offline، أو write-through عند الحاجة. في lazy write، اكتب entity وoutbox atomically، وجدول unique persistent work، وابعت idempotency key. بعد network response اكتب canonical result محليًا في transaction، فيتحرك stream طبيعيًا.</p>

## Read, write and conflict strategies

<p dir="rtl" lang="ar"><strong>Reads:</strong> اعرض local فورًا، وrefresh تحدث local. خطأ refresh لا يمسح بيانات صالحة؛ خلي stale/error metadata واضحة حسب UX. network status وحده مش دليل إن request هتنجح، فابدأ العمل وتعامل مع النتيجة. <strong>Writes:</strong> مش كل عملية ينفع offline. تغيير nickname يمكن queue؛ دفع أو حجز inventory غالبًا يحتاج online authority أو حالة pending صريحة.</p>

<p dir="rtl" lang="ar"><strong>Conflicts:</strong> last-write-wins بسيط لكنه ممكن يمسح شغل صحيح، وdevice clocks غير موثوقة. server version أو ETag أفضل لاكتشاف التعديل المتزامن. merge field-by-field يصلح لو fields مستقلة؛ CRDT له تكلفة وتعقيد ومش حل تلقائي. للnotes، ممكن تعرض نسختين للمستخدم. للpayment، merge نصوص لا معنى لها والserver authority تحكم.</p>

<p dir="rtl" lang="ar"><strong>Sync:</strong> pull عند فتح feature بسيط لفترات offline قصيرة. push notification تقول إن data stale ثم التطبيق يسحب التغيير. hybrid شائع. WorkManager مفيدة لشغل persistent مؤجل بقيود network، لكن “schedule نجح” لا يعني sync نجحت. worker لازم idempotent، والqueue نفسها persistent، والتقدم/الفشل يرجعوا للlocal source.</p>

## Tests and failure cases

<p dir="rtl" lang="ar">ستة اختبارات JVM بدأت بفشل compile ثم نجحت: local write تظهر Pending، accepted response تجعل canonical Clean، network failure تحفظ mutation وتعيد بنفس ID، conflict تحفظ draft والنسخة البعيدة، تعديل ثانٍ يحصل على mutation جديدة مع نفس base version، وblank input لا يغير local state. ده دليل على model in-memory فقط.</p>

<p dir="rtl" lang="ar">الناقص مهم: لا Room transaction، لا Flow، لا WorkManager، لا process death، لا concurrency، لا real HTTP، ولا multi-device sync. integration tests لازم تقفل process بعد local+outbox transaction، تعيد worker مرتين، تقلب ترتيب responses، تعمل migration، وتتحقق إن UI لا تقرأ network مباشرة. اختبر conflict policy بأمثلة domain حقيقية، مش بس technical timestamps.</p>

## Interview explanation

<p dir="rtl" lang="ar"><strong>بالمصري:</strong> بخلي local database source of truth للقراءة، فالـ UI تشوف نفس stream online وoffline. write محلية تتخزن atomically مع outbox وmutation ID. worker تبعتها للserver idempotently. accepted response تحدث local canonical record؛ network failure تسيبها pending؛ version conflict تحافظ على draft وتدخل policy واضحة بدل overwrite صامت.</p>

**English, 20 seconds:** “The UI reads one local source of truth. Offline writes update local data and a durable outbox atomically, then an idempotent worker synchronizes and writes the canonical result back locally.”

**English, 60–90 seconds:** “The repository owns coordination between local and remote sources. Higher layers observe the local database only. For a lazy write, I store the edited entity and a mutation record in one transaction, so the change is immediately visible and survives process death. A worker sends a stable mutation identity. Transport failure leaves it pending; acceptance replaces the local record with the server's canonical version; a version conflict preserves both pieces of evidence for an explicit policy. Unit tests cover transition rules, while Room, WorkManager, process restart, and API idempotency require integration tests.”

## Senior follow-ups

<ol dir="rtl" lang="ar"><li><strong>هل local دائمًا authority النهائية؟</strong> لأ؛ هي source of truth التي يقرأها التطبيق، والserver قد تحسم conflict وتغذيها.</li><li><strong>ليه transaction بين entity وoutbox؟</strong> تمنع crash window التي تحفظ واحدة من غير الثانية.</li><li><strong>هل connectivity callback تشغل sync فقط لما online؟</strong> استخدمها signal وجدولة، لكن request نفسها هي دليل النجاح؛ الشبكة قد تفشل رغم الاتصال.</li><li><strong>إمتى online-only أفضل؟</strong> عند operation تحتاج authority فورية أو لا يمكن تمثيل ambiguity بأمان.</li><li><strong>إزاي تمنع worker مزدوج؟</strong> unique work يساعد، وidempotency في repository/server تظل ضرورية.</li></ol>

## Misconceptions and revision

<ul dir="rtl" lang="ar"><li>“Repository wrapper للAPI.” ناقص؛ تملك data policy وتنسيق المصادر.</li><li>“Offline-first يعني كل write تشتغل offline.” غلط؛ الحد الأدنى critical reads، والwrites حسب المنتج.</li><li>“Last write wins آمنة دائمًا.” غلط؛ قد تفقد data وتعتمد على clocks.</li><li>“WorkManager تمنع duplicate.” غلط؛ job execution at-least-once محتمل، فصمّم idempotency.</li><li>“Network error تمسح pending.” غلط؛ حافظ على intent واعرض الحالة.</li></ul>

**Evidence limit:** Six JVM tests verify an in-memory model. No Room, Flow, WorkManager, process restart, network API, durable transaction, multi-device conflict, or Android component is executed.
